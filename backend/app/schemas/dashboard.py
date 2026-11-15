from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class ActivityItem(BaseModel):
    id: str
    type: str  # post, comment, notification, agent
    title: str
    description: str
    timestamp: datetime
    metadata: Optional[dict] = None

class DashboardOverviewResponse(BaseModel):
    total_agents: int
    active_agents: int
    total_posts: int
    total_notifications: int
    total_comments: int
    engagement_rate: float
    recent_activity: List[ActivityItem]

class DashboardEngagementMetric(BaseModel):
    notified: int
    delivered: int
    engaged: int
    ignored: int
    failed: int
    engagement_rate: float
