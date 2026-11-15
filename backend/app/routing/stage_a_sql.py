import logging
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import not_
from app.models.agent import Agent
from app.models.post import Post
from app.models.notification import Notification

logger = logging.getLogger("agentconnect.routing.stage_a")

def run_stage_a_sql_filtering(db: Session, post: Post) -> List[Agent]:
    """
    STAGE A: SQL Filtering
    Filters candidate agents based on hard criteria:
    - Exclude author agent of the post.
    - Exclude inactive agents (is_active = False).
    - Exclude low-trust / blocked agents (trust_score < 0.2).
    - Exclude agents that have already been notified for this post (deduplication).
    """
    # 1. Find all agent IDs that already received or are scheduled for a notification on this post
    already_notified_agent_ids = db.query(Notification.target_agent_id).filter(
        Notification.post_id == post.id
    ).all()
    already_notified_ids = {row[0] for row in already_notified_agent_ids}

    # 2. Query active, trusted candidate agents excluding author and already notified
    query = db.query(Agent).filter(
        Agent.id != post.author_agent_id,
        Agent.is_active == True,
        Agent.trust_score >= 0.2
    )

    if already_notified_ids:
        query = query.filter(not_(Agent.id.in_(already_notified_ids)))

    candidates = query.all()
    logger.info(
        f"Stage A [Post {post.id}]: Excluded author ({post.author_agent_id}) and {len(already_notified_ids)} "
        f"previously notified agents. Qualified {len(candidates)} candidate agents."
    )
    return candidates
