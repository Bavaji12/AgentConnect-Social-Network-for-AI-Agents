import asyncio
import logging
from datetime import datetime, timezone
from app.workers.queue import event_queue
from app.database.session import SessionLocal
from app.models.notification import Notification
from app.services.webhook_service import WebhookService
from app.ai.agent_responder import process_autonomous_response
from app.core.config import settings

logger = logging.getLogger("agentconnect.workers.runner")

_worker_task = None
_is_running = False

async def handle_notification_delivery(notification_id: str):
    """
    Executes webhook delivery with retries and triggers autonomous agent response.
    """
    db = SessionLocal()
    try:
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            logger.error(f"Worker cannot find notification {notification_id}")
            return

        post = notification.post
        target_agent = notification.target_agent

        if not target_agent or not post:
            logger.error(f"Incomplete data on notification {notification_id}")
            return

        payload = WebhookService.construct_payload(
            event_id=notification.id,
            post_id=post.id,
            source_agent_id=notification.source_agent_id,
            title=post.title,
            content=post.content,
            relevance_score=notification.relevance_score,
            relevance_explanation=notification.relevance_explanation
        )

        success, status_code, message = await WebhookService.deliver_webhook(
            webhook_url=target_agent.webhook_url,
            payload_data=payload
        )

        if success:
            notification.delivery_status = "DELIVERED"
            notification.delivered_at = datetime.now(timezone.utc)
            db.commit()
            logger.info(f"Notification {notification_id} successfully delivered to {target_agent.company_name}.")

            # Trigger Step 5: Autonomous response
            process_autonomous_response(db, notification.id)
        else:
            notification.retry_count += 1
            if notification.retry_count >= settings.MAX_WEBHOOK_RETRIES:
                notification.delivery_status = "FAILED"
                db.commit()
                logger.warning(
                    f"Notification {notification_id} permanently FAILED after {notification.retry_count} retries: {message}"
                )
            else:
                notification.delivery_status = "PENDING"
                db.commit()
                # Exponential backoff delay: 2 ** retry_count seconds
                backoff_delay = 2 ** notification.retry_count
                logger.info(f"Retrying notification {notification_id} in {backoff_delay} seconds...")
                await asyncio.sleep(backoff_delay)
                await event_queue.enqueue("deliver_notification", {"notification_id": notification_id})

    except Exception as e:
        logger.error(f"Exception during notification worker execution: {e}", exc_info=True)
    finally:
        db.close()

async def worker_loop():
    global _is_running
    logger.info("AgentConnect background worker started.")
    while _is_running:
        try:
            job = await event_queue.dequeue(timeout=1.0)
            if not job:
                await asyncio.sleep(0.1)
                continue

            task_name = job.get("task")
            payload = job.get("payload", {})

            if task_name == "deliver_notification":
                notification_id = payload.get("notification_id")
                if notification_id:
                    await handle_notification_delivery(notification_id)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in worker loop: {e}", exc_info=True)
            await asyncio.sleep(1.0)
    logger.info("AgentConnect background worker stopped.")

def start_worker():
    global _worker_task, _is_running
    if not _is_running:
        _is_running = True
        loop = asyncio.get_event_loop()
        loop.create_task(event_queue.connect())
        _worker_task = loop.create_task(worker_loop())

def stop_worker():
    global _worker_task, _is_running
    _is_running = False
    if _worker_task:
        _worker_task.cancel()

def enqueue_notification_delivery(notification_id: str):
    """
    Schedules a notification for background delivery.
    """
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(event_queue.enqueue("deliver_notification", {"notification_id": notification_id}))
    except RuntimeError:
        # If outside active event loop (e.g. sync script or thread), run synchronously or queue directly
        asyncio.run(event_queue.enqueue("deliver_notification", {"notification_id": notification_id}))
