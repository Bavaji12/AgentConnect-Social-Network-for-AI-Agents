from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

class PostCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    content: str = Field(..., min_length=5)
    category: str = Field(..., min_length=2, max_length=100)
    tags: List[str] = Field(default_factory=list)
    expires_at: Optional[datetime] = None

class PostResponse(BaseModel):
    id: str
    author_agent_id: str
    author_company: Optional[str] = None
    author_name: Optional[str] = None
    title: str
    content: str
    category: str
    tags: List[str] = []
    created_at: datetime
    expires_at: Optional[datetime] = None
    comments_count: int = 0
    notifications_count: int = 0

    class Config:
        from_attributes = True

class PostDetailResponse(PostResponse):
    comments: List[Any] = []
    routing_logs: List[Any] = []
    notifications: List[Any] = []
