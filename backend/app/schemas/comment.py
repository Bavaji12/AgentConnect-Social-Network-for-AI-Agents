from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=2)
    generated_by_llm: bool = True

class CommentApprovalUpdate(BaseModel):
    approval_status: str = Field(..., pattern="^(approved|rejected|pending)$")

class CommentResponse(BaseModel):
    id: str
    post_id: str
    author_agent_id: str
    author_company: Optional[str] = None
    author_name: Optional[str] = None
    content: str
    generated_by_llm: bool
    approval_status: str
    created_at: datetime

    class Config:
        from_attributes = True
