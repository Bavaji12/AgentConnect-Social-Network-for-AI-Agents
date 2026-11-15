from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.session import get_db
from app.models.agent_feedback import AgentFeedback
from app.models.agent import Agent
from app.models.post import Post
from app.schemas.feedback import AgentFeedbackCreate, AgentFeedbackResponse, FeedbackAnalyticsResponse

router = APIRouter(prefix="/feedback", tags=["Feedback"])

@router.post("", response_model=AgentFeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(feedback_in: AgentFeedbackCreate, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == feedback_in.agent_id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found.")

    post = db.query(Post).filter(Post.id == feedback_in.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")

    feedback = AgentFeedback(
        agent_id=feedback_in.agent_id,
        post_id=feedback_in.post_id,
        feedback_type=feedback_in.feedback_type,
        relevance_rating=feedback_in.relevance_rating
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return AgentFeedbackResponse.model_validate(feedback)

@router.get("/analytics", response_model=FeedbackAnalyticsResponse)
def get_feedback_analytics(db: Session = Depends(get_db)):
    total = db.query(AgentFeedback).count()
    if total == 0:
        return FeedbackAnalyticsResponse(
            total_feedback=0,
            engaged_count=0,
            ignored_count=0,
            irrelevant_count=0,
            helpful_count=0,
            engagement_rate=0.0,
            average_rating=0.0
        )

    engaged = db.query(AgentFeedback).filter(AgentFeedback.feedback_type == "ENGAGED").count()
    ignored = db.query(AgentFeedback).filter(AgentFeedback.feedback_type == "IGNORED").count()
    irrelevant = db.query(AgentFeedback).filter(AgentFeedback.feedback_type == "IRRELEVANT").count()
    helpful = db.query(AgentFeedback).filter(AgentFeedback.feedback_type == "HELPFUL").count()

    avg_rating = db.query(func.avg(AgentFeedback.relevance_rating)).scalar() or 0.0
    engagement_rate = round(float((engaged + helpful) / total), 4)

    return FeedbackAnalyticsResponse(
        total_feedback=total,
        engaged_count=engaged,
        ignored_count=ignored,
        irrelevant_count=irrelevant,
        helpful_count=helpful,
        engagement_rate=engagement_rate,
        average_rating=round(float(avg_rating), 2)
    )
