from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.post import Post
from app.models.routing_log import RoutingLog
from app.schemas.routing import RoutingRunResponse, RoutingLogResponse, RoutingAnalyticsResponse
from app.routing.engine import RoutingEngine

router = APIRouter(prefix="/routing", tags=["Routing"])

@router.post("/{post_id}/run", response_model=RoutingRunResponse)
def run_routing_for_post(
    post_id: str,
    threshold: Optional[float] = Query(None, ge=0.0, le=1.0),
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")

    engine = RoutingEngine(db)
    result = engine.execute_routing(post, threshold=threshold)

    # Format result response
    logs = db.query(RoutingLog).filter(RoutingLog.post_id == post_id).order_by(RoutingLog.final_score.desc()).all()
    formatted_logs = []
    for l in logs:
        item = RoutingLogResponse.model_validate(l)
        item.target_company = l.target_agent.company_name if l.target_agent else "Unknown"
        item.target_agent_name = l.target_agent.agent_name if l.target_agent else "Unknown"
        formatted_logs.append(item)

    return RoutingRunResponse(
        post_id=post.id,
        candidates_count=result["candidates_count"],
        eligible_count=result["eligible_count"],
        notified_count=result["notified_count"],
        results=formatted_logs
    )

@router.get("/{post_id}/results", response_model=List[RoutingLogResponse])
def get_routing_results(post_id: str, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")

    logs = db.query(RoutingLog).filter(RoutingLog.post_id == post_id).order_by(RoutingLog.final_score.desc()).all()
    formatted_logs = []
    for l in logs:
        item = RoutingLogResponse.model_validate(l)
        item.target_company = l.target_agent.company_name if l.target_agent else "Unknown"
        item.target_agent_name = l.target_agent.agent_name if l.target_agent else "Unknown"
        formatted_logs.append(item)
    return formatted_logs

@router.get("/analytics", response_model=RoutingAnalyticsResponse)
def get_routing_analytics(db: Session = Depends(get_db)):
    total = db.query(RoutingLog).count()
    if total == 0:
        return RoutingAnalyticsResponse(
            total_routed=0,
            notified_count=0,
            filtered_count=0,
            average_relevance_score=0.0,
            threshold_pass_rate=0.0
        )

    notified = db.query(RoutingLog).filter(RoutingLog.routing_decision == "NOTIFIED").count()
    filtered = total - notified

    from sqlalchemy import func
    avg_score = db.query(func.avg(RoutingLog.final_score)).scalar() or 0.0

    return RoutingAnalyticsResponse(
        total_routed=total,
        notified_count=notified,
        filtered_count=filtered,
        average_relevance_score=round(float(avg_score), 4),
        threshold_pass_rate=round(float(notified / total), 4)
    )
