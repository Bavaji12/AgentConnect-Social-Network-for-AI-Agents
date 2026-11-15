from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class NotificationStatusUpdate(BaseModel):
    delivery_status: str = Field(..., pattern="^(PENDING|DELIVERED|FAILED|VIEWED|ENGAGED|IGNORED)$")

class NotificationResponse(BaseModel):
    id: str
    post_id: str
    source_agent_id: str
    source_company: Optional[str] = None
    target_agent_id: str
    target_company: Optional[str] = None
    relevance_score: float
    relevance_explanation: str
    delivery_status: str
    retry_count: int
    delivered_at: Optional[datetime] = None
    created_at: datetime
    post_title: Optional[str] = None
    post_content: Optional[str] = None

    class Config:
        from_attributes = True

class WebhookPayload(BaseModel):
    event_id: str
    post_id: str
    publishing_agent_id: str
    title: str
    content: str
    relevance_score: float
    relevance_explanation: str
    timestamp: str
