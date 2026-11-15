import re
import math
import logging
from typing import List, Tuple
import numpy as np
from app.models.agent import Agent
from app.models.post import Post
from app.core.config import settings

logger = logging.getLogger("agentconnect.routing.stage_b")

def calculate_cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Computes normalized cosine similarity in range [0, 1]."""
    if not vec_a or not vec_b:
        return 0.0
    a = np.array(vec_a, dtype=np.float32)
    b = np.array(vec_b, dtype=np.float32)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    dot = np.dot(a, b) / (norm_a * norm_b)
    # Cosine dot product can be [-1, 1]; normalize into [0, 1]
    return float(max(0.0, min(1.0, (dot + 1.0) / 2.0)))

def extract_keywords(text: str) -> set[str]:
    """Extracts normalized significant business tokens from text."""
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    stop_words = {
        "and", "the", "for", "with", "this", "that", "all", "our", "are",
        "has", "have", "will", "from", "into", "during", "been", "were"
    }
    return {w for w in words if w not in stop_words}

def calculate_keyword_score(post_keywords: set[str], agent_text: str) -> float:
    """Calculates keyword overlap ratio against agent profile."""
    if not post_keywords:
        return 0.0
    agent_keywords = extract_keywords(agent_text)
    overlap = post_keywords.intersection(agent_keywords)
    if not overlap:
        return 0.0
    # Overlap score with saturation
    score = len(overlap) / max(1, min(len(post_keywords), 5))
    return float(min(1.0, score))

def run_stage_b_semantic_search(
    post: Post,
    candidates: List[Agent],
    top_k: int = None
) -> List[Tuple[Agent, float, float]]:
    """
    STAGE B: Semantic Search & Keyword Matching
    Computes vector similarity using pgvector / embedding cosine similarity,
    combines with keyword search, and retrieves top K candidates.
    Returns: List of (agent, semantic_similarity, keyword_score)
    """
    if top_k is None:
        top_k = settings.TOP_K_CANDIDATES

    post_embedding = post.post_embedding or []
    post_text = f"{post.title} {post.content} {' '.join(post.tags or [])}"
    post_keywords = extract_keywords(post_text)

    scored_candidates = []
    for agent in candidates:
        agent_embedding = agent.interest_embedding or []
        sem_sim = calculate_cosine_similarity(post_embedding, agent_embedding)
        
        agent_profile = f"{agent.agent_name} {agent.company_name} {agent.industry_category} {agent.interest_manifesto}"
        kw_score = calculate_keyword_score(post_keywords, agent_profile)
        
        # Candidate stage score for Top-K selection
        preliminary_score = (0.7 * sem_sim) + (0.3 * kw_score)
        scored_candidates.append((agent, sem_sim, kw_score, preliminary_score))

    # Sort descending by preliminary score
    scored_candidates.sort(key=lambda x: x[3], reverse=True)
    top_candidates = scored_candidates[:top_k]

    logger.info(
        f"Stage B [Post {post.id}]: Filtered {len(candidates)} candidates down to "
        f"{len(top_candidates)} top-k candidates."
    )
    return [(agent, sem_sim, kw_score) for agent, sem_sim, kw_score, _ in top_candidates]
