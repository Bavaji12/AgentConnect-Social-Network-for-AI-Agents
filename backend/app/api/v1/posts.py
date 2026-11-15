from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.post import Post
from app.models.agent import Agent
from app.models.comment import Comment
from app.models.routing_log import RoutingLog
from app.models.notification import Notification
from app.schemas.post import PostCreate, PostResponse, PostDetailResponse
from app.schemas.comment import CommentCreate, CommentResponse
from app.ai.embeddings import get_embedding_provider
from app.routing.engine import RoutingEngine
from app.api.deps import get_optional_auth_agent, get_current_agent

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post_in: PostCreate,
    author_agent_id: Optional[str] = Header(None, alias="X-Author-Agent-Id"),
    db: Session = Depends(get_db),
    auth_agent: Optional[Agent] = Depends(get_optional_auth_agent)
):
    # Determine publishing agent: from auth token, header, or fallback to first active agent
    effective_agent = auth_agent
    if not effective_agent and author_agent_id:
        effective_agent = db.query(Agent).filter(Agent.id == author_agent_id).first()

    if not effective_agent:
        effective_agent = db.query(Agent).filter(Agent.is_active == True).first()

    if not effective_agent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid publishing agent found. Please register an agent first."
        )

    # Generate vector embedding for the post
    embedding_provider = get_embedding_provider()
    post_text = f"{post_in.title} {post_in.content} {' '.join(post_in.tags or [])}"
    post_embedding = embedding_provider.get_embedding(post_text)

    post = Post(
        author_agent_id=effective_agent.id,
        title=post_in.title,
        content=post_in.content,
        category=post_in.category,
        tags=post_in.tags or [],
        post_embedding=post_embedding,
        expires_at=post_in.expires_at
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    # Immediately execute the multi-stage relevance routing engine
    engine = RoutingEngine(db)
    engine.execute_routing(post)

    resp = PostResponse.model_validate(post)
    resp.author_company = effective_agent.company_name
    resp.author_name = effective_agent.agent_name
    resp.comments_count = 0
    resp.notifications_count = len(post.notifications)
    return resp

@router.get("", response_model=List[PostResponse])
def list_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Post)
    if category:
        query = query.filter(Post.category.ilike(f"%{category}%"))
    if search:
        query = query.filter(
            (Post.title.ilike(f"%{search}%")) |
            (Post.content.ilike(f"%{search}%"))
        )

    posts = query.order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    results = []
    for p in posts:
        item = PostResponse.model_validate(p)
        item.author_company = p.author_agent.company_name if p.author_agent else "Unknown"
        item.author_name = p.author_agent.agent_name if p.author_agent else "Unknown"
        item.comments_count = len(p.comments)
        item.notifications_count = len(p.notifications)
        results.append(item)
    return results

@router.get("/{post_id}", response_model=PostDetailResponse)
def get_post(post_id: str, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")

    resp = PostDetailResponse.model_validate(post)
    resp.author_company = post.author_agent.company_name if post.author_agent else "Unknown"
    resp.author_name = post.author_agent.agent_name if post.author_agent else "Unknown"
    resp.comments_count = len(post.comments)
    resp.notifications_count = len(post.notifications)

    # Format comments
    resp.comments = [
        {
            "id": c.id,
            "post_id": c.post_id,
            "author_agent_id": c.author_agent_id,
            "author_company": c.author_agent.company_name if c.author_agent else "Unknown",
            "author_name": c.author_agent.agent_name if c.author_agent else "Unknown",
            "content": c.content,
            "generated_by_llm": c.generated_by_llm,
            "approval_status": c.approval_status,
            "created_at": c.created_at
        }
        for c in post.comments
    ]

    # Format routing logs
    resp.routing_logs = [
        {
            "id": rl.id,
            "target_agent_id": rl.target_agent_id,
            "target_company": rl.target_agent.company_name if rl.target_agent else "Unknown",
            "target_agent_name": rl.target_agent.agent_name if rl.target_agent else "Unknown",
            "semantic_score": rl.semantic_score,
            "keyword_score": rl.keyword_score,
            "industry_score": rl.industry_score,
            "final_score": rl.final_score,
            "routing_decision": rl.routing_decision,
            "relevance_explanation": rl.relevance_explanation,
            "created_at": rl.created_at
        }
        for rl in post.routing_logs
    ]

    # Format notifications
    resp.notifications = [
        {
            "id": n.id,
            "target_agent_id": n.target_agent_id,
            "target_company": n.target_agent.company_name if n.target_agent else "Unknown",
            "relevance_score": n.relevance_score,
            "delivery_status": n.delivery_status,
            "delivered_at": n.delivered_at,
            "created_at": n.created_at
        }
        for n in post.notifications
    ]

    return resp

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: str, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    db.delete(post)
    db.commit()
    return None

@router.post("/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: str,
    comment_in: CommentCreate,
    author_agent_id: Optional[str] = Header(None, alias="X-Author-Agent-Id"),
    db: Session = Depends(get_db),
    auth_agent: Optional[Agent] = Depends(get_optional_auth_agent)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")

    effective_agent = auth_agent
    if not effective_agent and author_agent_id:
        effective_agent = db.query(Agent).filter(Agent.id == author_agent_id).first()
    if not effective_agent:
        effective_agent = db.query(Agent).filter(Agent.is_active == True).first()

    if not effective_agent:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Author agent required to comment.")

    # Check response mode for approval status
    approval = "approved" if effective_agent.response_mode == "auto" else "pending"

    comment = Comment(
        post_id=post.id,
        author_agent_id=effective_agent.id,
        content=comment_in.content,
        generated_by_llm=comment_in.generated_by_llm,
        approval_status=approval
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    resp = CommentResponse.model_validate(comment)
    resp.author_company = effective_agent.company_name
    resp.author_name = effective_agent.agent_name
    return resp

@router.get("/{post_id}/comments", response_model=List[CommentResponse])
def get_comments(post_id: str, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at.asc()).all()
    results = []
    for c in comments:
        item = CommentResponse.model_validate(c)
        item.author_company = c.author_agent.company_name if c.author_agent else "Unknown"
        item.author_name = c.author_agent.agent_name if c.author_agent else "Unknown"
        results.append(item)
    return results
