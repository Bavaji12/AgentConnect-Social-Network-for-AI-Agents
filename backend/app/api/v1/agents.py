from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.agent import Agent
from app.models.notification import Notification
from app.schemas.agent import (
    AgentCreate, AgentUpdate, AgentResponse, AgentRegisterResponse,
    AgentLoginRequest, AgentLoginResponse
)
from app.schemas.notification import NotificationResponse
from app.core.security import generate_api_key, hash_api_key, create_access_token
from app.ai.embeddings import get_embedding_provider
from app.security.ssrf import validate_webhook_url

router = APIRouter(prefix="/agents", tags=["Agents"])

@router.post("/register", response_model=AgentRegisterResponse, status_code=status.HTTP_201_CREATED)
def register_agent(agent_in: AgentCreate, db: Session = Depends(get_db)):
    # SSRF verification on webhook URL
    is_safe, error_msg = validate_webhook_url(agent_in.webhook_url)
    if not is_safe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid webhook URL: {error_msg}"
        )

    # Check for existing agent under company and agent name
    existing = db.query(Agent).filter(
        Agent.company_name == agent_in.company_name,
        Agent.agent_name == agent_in.agent_name
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent '{agent_in.agent_name}' for company '{agent_in.company_name}' already exists."
        )

    # Generate embedding from agent's interest manifesto
    embedding_provider = get_embedding_provider()
    manifesto_embedding = embedding_provider.get_embedding(agent_in.interest_manifesto)

    # Generate secure API key
    raw_api_key, hashed_api_key = generate_api_key()

    agent = Agent(
        company_name=agent_in.company_name,
        agent_name=agent_in.agent_name,
        industry_category=agent_in.industry_category,
        description=agent_in.description,
        interest_manifesto=agent_in.interest_manifesto,
        interest_embedding=manifesto_embedding,
        webhook_url=agent_in.webhook_url,
        api_key_hash=hashed_api_key,
        trust_score=1.0,
        is_active=True,
        response_mode=agent_in.response_mode
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    agent_data = AgentResponse.model_validate(agent).model_dump()
    return AgentRegisterResponse(**agent_data, api_key=raw_api_key)

@router.post("/login", response_model=AgentLoginResponse)
def login_agent(data: AgentLoginRequest, db: Session = Depends(get_db)):
    hashed_key = hash_api_key(data.api_key)
    agent = db.query(Agent).filter(
        Agent.id == data.agent_id,
        Agent.api_key_hash == hashed_key
    ).first()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Agent ID or API Key."
        )

    if not agent.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agent account has been deactivated."
        )

    token = create_access_token(subject=agent.id, role="agent")
    return AgentLoginResponse(
        access_token=token,
        token_type="bearer",
        agent=AgentResponse.model_validate(agent)
    )

@router.get("", response_model=List[AgentResponse])
def list_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    is_active: Optional[bool] = None,
    industry: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Agent)
    if is_active is not None:
        query = query.filter(Agent.is_active == is_active)
    if industry:
        query = query.filter(Agent.industry_category.ilike(f"%{industry}%"))
    if search:
        query = query.filter(
            (Agent.company_name.ilike(f"%{search}%")) |
            (Agent.agent_name.ilike(f"%{search}%")) |
            (Agent.interest_manifesto.ilike(f"%{search}%"))
        )

    agents = query.order_by(Agent.created_at.desc()).offset(skip).limit(limit).all()
    return [AgentResponse.model_validate(a) for a in agents]

@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found.")
    return AgentResponse.model_validate(agent)

@router.patch("/{agent_id}", response_model=AgentResponse)
def update_agent(agent_id: str, updates: AgentUpdate, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found.")

    update_data = updates.model_dump(exclude_unset=True)

    if "webhook_url" in update_data and update_data["webhook_url"]:
        is_safe, error_msg = validate_webhook_url(update_data["webhook_url"])
        if not is_safe:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid webhook URL: {error_msg}")

    # Re-compute embedding if manifesto updated
    if "interest_manifesto" in update_data and update_data["interest_manifesto"]:
        embedding_provider = get_embedding_provider()
        update_data["interest_embedding"] = embedding_provider.get_embedding(update_data["interest_manifesto"])

    for field, val in update_data.items():
        setattr(agent, field, val)

    db.commit()
    db.refresh(agent)
    return AgentResponse.model_validate(agent)

@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found.")
    db.delete(agent)
    db.commit()
    return None

@router.get("/{agent_id}/notifications", response_model=List[NotificationResponse])
def get_agent_notifications(
    agent_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found.")

    notifications = db.query(Notification).filter(
        Notification.target_agent_id == agent_id
    ).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

    results = []
    for n in notifications:
        item = NotificationResponse.model_validate(n)
        item.source_company = n.source_agent.company_name if n.source_agent else "Unknown"
        item.target_company = n.target_agent.company_name if n.target_agent else "Unknown"
        item.post_title = n.post.title if n.post else ""
        item.post_content = n.post.content if n.post else ""
        results.append(item)
    return results
