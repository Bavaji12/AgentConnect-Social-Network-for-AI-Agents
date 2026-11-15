from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class RoutingLogResponse(BaseModel):
    id: str
    post_id: str
    target_agent_id: str
    target_company: Optional[str] = None
    target_agent_name: Optional[str] = None
    semantic_score: float
    keyword_score: float
    industry_score: float
    final_score: float
    routing_decision: str
    relevance_explanation: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class RoutingRunResponse(BaseModel):
    post_id: str
    candidates_count: int
    eligible_count: int
    notified_count: int
    results: List[RoutingLogResponse]

class RoutingAnalyticsResponse(BaseModel):
    total_routed: int
    notified_count: int
    filtered_count: int
    average_relevance_score: float
    threshold_pass_rate: float
