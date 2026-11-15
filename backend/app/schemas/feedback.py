from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AgentFeedbackCreate(BaseModel):
    agent_id: str
    post_id: str
    feedback_type: str = Field(..., pattern="^(ENGAGED|IGNORED|IRRELEVANT|HELPFUL)$")
    relevance_rating: float = Field(default=1.0, ge=0.0, le=5.0)

class AgentFeedbackResponse(BaseModel):
    id: str
    agent_id: str
    post_id: str
    feedback_type: str
    relevance_rating: float
    created_at: datetime

    class Config:
        from_attributes = True

class FeedbackAnalyticsResponse(BaseModel):
    total_feedback: int
    engaged_count: int
    ignored_count: int
    irrelevant_count: int
    helpful_count: int
    engagement_rate: float
    average_rating: float
