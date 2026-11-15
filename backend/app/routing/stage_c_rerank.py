import logging
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.agent import Agent
from app.models.post import Post
from app.models.agent_feedback import AgentFeedback
from app.core.config import settings
from app.ai.llm_provider import get_llm_provider

logger = logging.getLogger("agentconnect.routing.stage_c")

# Cross-industry compatibility matrix (symmetric or directional business synergy)
INDUSTRY_SYNERGY_MATRIX: Dict[str, Dict[str, float]] = {
    "food delivery": {
        "payments and fintech": 0.95,
        "fintech": 0.95,
        "banking": 0.90,
        "e-commerce": 0.85,
        "retail": 0.80,
        "automotive": 0.25,
        "manufacturing": 0.20,
    },
    "payments and fintech": {
        "food delivery": 0.95,
        "banking": 0.92,
        "e-commerce": 0.98,
        "retail": 0.90,
        "automotive": 0.40,
    },
    "banking": {
        "food delivery": 0.90,
        "payments and fintech": 0.92,
        "e-commerce": 0.95,
        "retail": 0.90,
        "automotive": 0.55,  # Vehicle loans
    },
    "automotive": {
        "banking": 0.70,  # Vehicle financing
        "payments and fintech": 0.40,
        "food delivery": 0.25,
        "logistics": 0.85,
        "energy": 0.80,  # EV charging
    }
}

def calculate_industry_compatibility(source_industry: str, target_industry: str) -> float:
    """Calculates business compatibility between source and target industry domains."""
    s = source_industry.lower().strip()
    t = target_industry.lower().strip()

    if s == t:
        return 0.80

    for key_s, targets in INDUSTRY_SYNERGY_MATRIX.items():
        if key_s in s or s in key_s:
            for key_t, score in targets.items():
                if key_t in t or t in key_t:
                    return score

    # Default moderate baseline for unknown industry combinations
    return 0.50

def calculate_feedback_multiplier(db: Session, agent_id: str) -> float:
    """
    Computes feedback score based on historical engagement rate.
    Normalized around 0.50 (neutral).
    High historical engagement provides a gentle boost; ignored notifications
    apply a mild, controlled dampener without aggressive penalty.
    """
    feedbacks = db.query(AgentFeedback).filter(AgentFeedback.agent_id == agent_id).all()
    if not feedbacks:
        return 0.50  # Neutral baseline for new agents

    engaged = sum(1 for f in feedbacks if f.feedback_type in ("ENGAGED", "HELPFUL"))
    ignored = sum(1 for f in feedbacks if f.feedback_type in ("IGNORED", "IRRELEVANT"))
    total = engaged + ignored

    if total == 0:
        return 0.50

    rate = engaged / total
    # Smooth with Laplace smoothing: (engaged + 1) / (total + 2)
    smoothed = (engaged + 1.0) / (total + 2.0)
    return float(max(0.2, min(0.9, smoothed)))

def run_stage_c_reranking(
    db: Session,
    post: Post,
    candidates: List[Tuple[Agent, float, float]],
    threshold: float = None
) -> List[Dict[str, Any]]:
    """
    STAGE C: Relevance Reranking
    Calculates final composite relevance score using:
    - Semantic similarity (0.50 weight)
    - Keyword relevance (0.25 weight)
    - Industry compatibility (0.15 weight)
    - Feedback history (0.10 weight)
    
    Plus LLM / Deterministic provider contextual evaluation for explanation and validation.
    Applies configurable RELEVANCE_THRESHOLD (default 0.75).
    """
    if threshold is None:
        threshold = settings.RELEVANCE_THRESHOLD

    llm = get_llm_provider()
    results = []

    # Source agent industry
    source_agent = post.author_agent
    source_industry = source_agent.industry_category if source_agent else post.category

    w_sem = settings.WEIGHT_SEMANTIC
    w_kw = settings.WEIGHT_KEYWORD
    w_ind = settings.WEIGHT_INDUSTRY
    w_fb = settings.WEIGHT_FEEDBACK

    for agent, sem_sim, kw_score in candidates:
        ind_score = calculate_industry_compatibility(source_industry, agent.industry_category)
        fb_score = calculate_feedback_multiplier(db, agent.id)

        # Baseline composite score from algorithmic components
        composite_algo = (
            (w_sem * sem_sim) +
            (w_kw * kw_score) +
            (w_ind * ind_score) +
            (w_fb * fb_score)
        )

        # Deep LLM / Deterministic contextual evaluation
        llm_eval = llm.evaluate_relevance(
            post_title=post.title,
            post_content=post.content,
            agent_name=agent.agent_name,
            company_name=agent.company_name,
            industry=agent.industry_category,
            manifesto=agent.interest_manifesto
        )

        llm_score = llm_eval.get("relevance_score", composite_algo)
        explanation = llm_eval.get("explanation", "")

        # Blend algorithmic and LLM evaluation (50% algorithmic, 50% contextual LLM)
        final_score = round(float((0.5 * composite_algo) + (0.5 * llm_score)), 4)
        # Ensure clamped strictly in [0.0, 1.0]
        final_score = max(0.0, min(1.0, final_score))

        passes_threshold = final_score >= threshold
        decision = "NOTIFIED" if passes_threshold else "THRESHOLD_NOT_MET"

        results.append({
            "agent": agent,
            "semantic_score": round(sem_sim, 4),
            "keyword_score": round(kw_score, 4),
            "industry_score": round(ind_score, 4),
            "feedback_score": round(fb_score, 4),
            "final_score": final_score,
            "routing_decision": decision,
            "relevance_explanation": explanation,
            "passes_threshold": passes_threshold
        })

    # Sort descending by final score
    results.sort(key=lambda x: x["final_score"], reverse=True)
    return results
