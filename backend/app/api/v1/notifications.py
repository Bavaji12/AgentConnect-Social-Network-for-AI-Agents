from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse, NotificationStatusUpdate
from app.workers.runner import enqueue_notification_delivery

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("", response_model=List[NotificationResponse])
def list_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    post_id: Optional[str] = None,
    target_agent_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Notification)
    if status_filter:
        query = query.filter(Notification.delivery_status == status_filter)
    if post_id:
        query = query.filter(Notification.post_id == post_id)
    if target_agent_id:
        query = query.filter(Notification.target_agent_id == target_agent_id)

    notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    results = []
    for n in notifications:
        item = NotificationResponse.model_validate(n)
        item.source_company = n.source_agent.company_name if n.source_agent else "Unknown"
        item.target_company = n.target_agent.company_name if n.target_agent else "Unknown"
        item.post_title = n.post.title if n.post else ""
        item.post_content = n.post.content if n.post else ""
        results.append(item)
    return results

@router.post("/{notification_id}/retry", response_model=NotificationResponse)
def retry_notification(notification_id: str, db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")

    notification.delivery_status = "PENDING"
    notification.retry_count = 0
    db.commit()
    db.refresh(notification)

    # Enqueue retry
    enqueue_notification_delivery(notification.id)

    item = NotificationResponse.model_validate(notification)
    item.source_company = notification.source_agent.company_name if notification.source_agent else "Unknown"
    item.target_company = notification.target_agent.company_name if notification.target_agent else "Unknown"
    item.post_title = notification.post.title if notification.post else ""
    item.post_content = notification.post.content if notification.post else ""
    return item

@router.patch("/{notification_id}/status", response_model=NotificationResponse)
def update_notification_status(
    notification_id: str,
    update: NotificationStatusUpdate,
    db: Session = Depends(get_db)
):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")

    notification.delivery_status = update.delivery_status
    db.commit()
    db.refresh(notification)

    item = NotificationResponse.model_validate(notification)
    item.source_company = notification.source_agent.company_name if notification.source_agent else "Unknown"
    item.target_company = notification.target_agent.company_name if notification.target_agent else "Unknown"
    item.post_title = notification.post.title if notification.post else ""
    item.post_content = notification.post.content if notification.post else ""
    return item
