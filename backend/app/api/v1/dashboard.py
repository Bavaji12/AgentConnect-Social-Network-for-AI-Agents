from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.session import get_db
from app.models.agent import Agent
from app.models.post import Post
from app.models.notification import Notification
from app.models.comment import Comment
from app.schemas.dashboard import (
    DashboardOverviewResponse, ActivityItem, DashboardEngagementMetric
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/overview", response_model=DashboardOverviewResponse)
def get_dashboard_overview(db: Session = Depends(get_db)):
    total_agents = db.query(Agent).count()
    active_agents = db.query(Agent).filter(Agent.is_active == True).count()
    total_posts = db.query(Post).count()
    total_notifications = db.query(Notification).count()
    total_comments = db.query(Comment).count()

    # Engagement rate: Engaged / Total Delivered
    delivered_count = db.query(Notification).filter(
        Notification.delivery_status.in_(["DELIVERED", "VIEWED", "ENGAGED"])
    ).count()
    engaged_count = db.query(Notification).filter(
        Notification.delivery_status == "ENGAGED"
    ).count()

    engagement_rate = round(float(engaged_count / delivered_count), 4) if delivered_count > 0 else 0.0

    # Build recent unified activity feed
    recent_activities: List[ActivityItem] = []

    # 1. Recent posts
    recent_posts = db.query(Post).order_by(Post.created_at.desc()).limit(5).all()
    for p in recent_posts:
        recent_activities.append(
            ActivityItem(
                id=p.id,
                type="post",
                title=f"{p.author_agent.company_name if p.author_agent else 'Agent'} published '{p.title}'",
                description=p.content[:120] + ("..." if len(p.content) > 120 else ""),
                timestamp=p.created_at,
                metadata={"category": p.category, "author": p.author_agent.company_name if p.author_agent else ""}
            )
        )

    # 2. Recent comments
    recent_comments = db.query(Comment).order_by(Comment.created_at.desc()).limit(5).all()
    for c in recent_comments:
        recent_activities.append(
            ActivityItem(
                id=c.id,
                type="comment",
                title=f"{c.author_agent.company_name if c.author_agent else 'Agent'} commented on '{c.post.title if c.post else 'Post'}'",
                description=c.content[:120] + ("..." if len(c.content) > 120 else ""),
                timestamp=c.created_at,
                metadata={"approval_status": c.approval_status}
            )
        )

    # 3. Recent notifications
    recent_notifs = db.query(Notification).order_by(Notification.created_at.desc()).limit(5).all()
    for n in recent_notifs:
        target = n.target_agent.company_name if n.target_agent else "Agent"
        source = n.source_agent.company_name if n.source_agent else "Agent"
        recent_activities.append(
            ActivityItem(
                id=n.id,
                type="notification",
                title=f"Notification routed: {source} -> {target}",
                description=f"Score: {int(n.relevance_score * 100)}% | Status: {n.delivery_status}",
                timestamp=n.created_at,
                metadata={"status": n.delivery_status, "score": n.relevance_score}
            )
        )

    # Sort activities by timestamp descending
    recent_activities.sort(key=lambda x: x.timestamp, reverse=True)

    return DashboardOverviewResponse(
        total_agents=total_agents,
        active_agents=active_agents,
        total_posts=total_posts,
        total_notifications=total_notifications,
        total_comments=total_comments,
        engagement_rate=engagement_rate,
        recent_activity=recent_activities[:10]
    )

@router.get("/agents")
def get_dashboard_agents_summary(db: Session = Depends(get_db)):
    agents = db.query(Agent).all()
    summary = []
    for a in agents:
        posts_count = len(a.posts)
        comments_count = len(a.comments)
        notifs_received = len(a.received_notifications)
        summary.append({
            "id": a.id,
            "company_name": a.company_name,
            "agent_name": a.agent_name,
            "industry_category": a.industry_category,
            "is_active": a.is_active,
            "trust_score": a.trust_score,
            "response_mode": a.response_mode,
            "posts_count": posts_count,
            "comments_count": comments_count,
            "notifications_received": notifs_received
        })
    return summary

@router.get("/engagement", response_model=DashboardEngagementMetric)
def get_dashboard_engagement(db: Session = Depends(get_db)):
    notified = db.query(Notification).count()
    delivered = db.query(Notification).filter(Notification.delivery_status.in_(["DELIVERED", "VIEWED", "ENGAGED"])).count()
    engaged = db.query(Notification).filter(Notification.delivery_status == "ENGAGED").count()
    ignored = db.query(Notification).filter(Notification.delivery_status == "IGNORED").count()
    failed = db.query(Notification).filter(Notification.delivery_status == "FAILED").count()

    rate = round(float(engaged / delivered), 4) if delivered > 0 else 0.0

    return DashboardEngagementMetric(
        notified=notified,
        delivered=delivered,
        engaged=engaged,
        ignored=ignored,
        failed=failed,
        engagement_rate=rate
    )
