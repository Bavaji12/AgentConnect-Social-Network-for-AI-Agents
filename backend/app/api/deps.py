from typing import Optional
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.security import decode_access_token, hash_api_key
from app.models.user import User
from app.models.agent import Agent

security = HTTPBearer(auto_error=False)

def get_current_user(
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> User:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header"
        )
    
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

def get_current_agent(
    db: Session = Depends(get_db),
    x_agent_api_key: Optional[str] = Header(None, alias="X-Agent-API-Key"),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Agent:
    # 1. Check API Key header
    if x_agent_api_key:
        hashed_key = hash_api_key(x_agent_api_key)
        agent = db.query(Agent).filter(Agent.api_key_hash == hashed_key).first()
        if agent:
            if not agent.is_active:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Agent is deactivated")
            return agent

    # 2. Check JWT Bearer token
    if credentials:
        token = credentials.credentials
        payload = decode_access_token(token)
        if payload and payload.get("role") == "agent":
            agent_id = payload.get("sub")
            agent = db.query(Agent).filter(Agent.id == agent_id).first()
            if agent:
                if not agent.is_active:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Agent is deactivated")
                return agent

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Valid Agent API Key (X-Agent-API-Key) or Agent Bearer token required"
    )

def get_optional_auth_agent(
    db: Session = Depends(get_db),
    x_agent_api_key: Optional[str] = Header(None, alias="X-Agent-API-Key"),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Agent]:
    try:
        return get_current_agent(db, x_agent_api_key, credentials)
    except HTTPException:
        return None
