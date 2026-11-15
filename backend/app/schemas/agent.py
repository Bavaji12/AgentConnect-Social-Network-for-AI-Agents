from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime

class AgentBase(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=255)
    agent_name: str = Field(..., min_length=2, max_length=255)
    industry_category: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=5)
    interest_manifesto: str = Field(..., min_length=10)
    webhook_url: str = Field(..., min_length=5, max_length=500)
    response_mode: str = Field(default="auto", pattern="^(auto|human_approval|ignore)$")

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    company_name: Optional[str] = None
    agent_name: Optional[str] = None
    industry_category: Optional[str] = None
    description: Optional[str] = None
    interest_manifesto: Optional[str] = None
    webhook_url: Optional[str] = None
    response_mode: Optional[str] = Field(None, pattern="^(auto|human_approval|ignore)$")
    is_active: Optional[bool] = None

class AgentResponse(AgentBase):
    id: str
    trust_score: float
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AgentRegisterResponse(AgentResponse):
    api_key: str = Field(default="", description="Raw API key shown only once upon registration")

class AgentLoginRequest(BaseModel):
    agent_id: str
    api_key: str

class AgentLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    agent: AgentResponse
