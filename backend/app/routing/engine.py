import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.post import Post
from app.models.notification import Notification
from app.models.routing_log import RoutingLog
from app.routing.stage_a_sql import run_stage_a_sql_filtering
from app.routing.stage_b_semantic import run_stage_b_semantic_search
from app.routing.stage_c_rerank import run_stage_c_reranking
from app.core.config import settings

logger = logging.getLogger("agentconnect.routing.engine")

class RoutingEngine:
    """
    Multi-Stage Enterprise Relevance Routing Engine:
    Stage A -> SQL Filtering
    Stage B -> Semantic Search + Keyword Top-K Matching
    Stage C -> Multi-Factor Reranking with LLM Justification
    """
    def __init__(self, db: Session):
        self.db = db

    def execute_routing(self, post: Post, threshold: float = None) -> Dict[str, Any]:
        if threshold is None:
            threshold = settings.RELEVANCE_THRESHOLD

        logger.info(f"Initiating multi-stage routing for Post {post.id} (Threshold: {threshold})")

        # 1. STAGE A: SQL Filtering
        candidates_stage_a = run_stage_a_sql_filtering(self.db, post)
        if not candidates_stage_a:
            logger.info(f"Stage A returned 0 candidates for Post {post.id}")
            return {
                "post_id": post.id,
                "candidates_count": 0,
                "eligible_count": 0,
                "notified_count": 0,
                "results": []
            }

        # 2. STAGE B: Semantic Search & Keyword Top-K
        candidates_stage_b = run_stage_b_semantic_search(post, candidates_stage_a)

        # 3. STAGE C: Multi-Factor Reranking
        reranked_results = run_stage_c_reranking(self.db, post, candidates_stage_b, threshold=threshold)

        created_logs = []
        notifications_created = []

        for item in reranked_results:
            agent = item["agent"]
            # Record routing decision log
            log_entry = RoutingLog(
                post_id=post.id,
                target_agent_id=agent.id,
                semantic_score=item["semantic_score"],
                keyword_score=item["keyword_score"],
                industry_score=item["industry_score"],
                final_score=item["final_score"],
                routing_decision=item["routing_decision"],
                relevance_explanation=item["relevance_explanation"]
            )
            self.db.add(log_entry)
            created_logs.append(log_entry)

            # If threshold is met, create pending notification record
            if item["passes_threshold"]:
                notification = Notification(
                    post_id=post.id,
                    source_agent_id=post.author_agent_id,
                    target_agent_id=agent.id,
                    relevance_score=item["final_score"],
                    relevance_explanation=item["relevance_explanation"],
                    delivery_status="PENDING",
                    retry_count=0
                )
                self.db.add(notification)
                notifications_created.append(notification)

        self.db.commit()

        # Enqueue background tasks for created notifications
        from app.workers.runner import enqueue_notification_delivery
        for notif in notifications_created:
            try:
                enqueue_notification_delivery(notif.id)
            except Exception as e:
                logger.error(f"Failed to enqueue notification {notif.id}: {e}")

        logger.info(
            f"Routing completed for Post {post.id}: {len(candidates_stage_a)} screened, "
            f"{len(notifications_created)} notifications dispatched."
        )

        return {
            "post_id": post.id,
            "candidates_count": len(candidates_stage_a),
            "eligible_count": len(candidates_stage_b),
            "notified_count": len(notifications_created),
            "results": reranked_results
        }
