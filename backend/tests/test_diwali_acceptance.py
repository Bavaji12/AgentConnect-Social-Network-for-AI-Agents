import pytest
from app.models.agent import Agent
from app.models.post import Post
from app.models.notification import Notification
from app.models.routing_log import RoutingLog
from app.models.comment import Comment
from app.ai.embeddings import get_embedding_provider
from app.routing.engine import RoutingEngine
from app.ai.agent_responder import process_autonomous_response

def test_diwali_multi_stage_acceptance_scenario(db_session):
    """
    CRITICAL ACCEPTANCE TEST (Specification Section 11)
    Register:
    - Swiggy: Food delivery & festive promotions
    - PhonePe: UPI payments, merchant cashback, e-commerce offers
    - HDFC Bank: Credit cards, merchant offers, payment partnerships
    - Bajaj Auto: Automobiles & vehicle financing

    Publish:
    "Swiggy offers 5% off all food deliveries during Diwali."

    Expected:
    - PhonePe should be identified as relevant (notified).
    - HDFC Bank should be identified as relevant (notified).
    - Bajaj Auto should NOT receive a notification (filtered out).
    - Autonomous agent responses generated.
    """
    p = get_embedding_provider()

    # 1. Register Agents
    swiggy_manifesto = (
        "We focus on food delivery promotions, restaurant discounts, festive seasonal campaigns "
        "like Diwali and New Year, merchant onboarding, instant grocery delivery offers, and consumer dining perks."
    )
    swiggy = Agent(
        company_name="Swiggy",
        agent_name="Swiggy Partnerships Agent",
        industry_category="Food Delivery",
        description="Food delivery promotions and dining perks",
        interest_manifesto=swiggy_manifesto,
        interest_embedding=p.get_embedding(swiggy_manifesto),
        webhook_url="http://agentconnect.internal/webhook/swiggy",
        api_key_hash="hash_swiggy",
        trust_score=1.0,
        is_active=True,
        response_mode="auto"
    )

    phonepe_manifesto = (
        "Interested in UPI payments, merchant cashback, e-commerce offers, payment partnerships, "
        "digital wallet transactions, checkout discounts, and online merchant promotions."
    )
    phonepe = Agent(
        company_name="PhonePe",
        agent_name="PhonePe Growth Agent",
        industry_category="Payments and Fintech",
        description="UPI payments and merchant cashback partnerships",
        interest_manifesto=phonepe_manifesto,
        interest_embedding=p.get_embedding(phonepe_manifesto),
        webhook_url="http://agentconnect.internal/webhook/phonepe",
        api_key_hash="hash_phonepe",
        trust_score=1.0,
        is_active=True,
        response_mode="auto"
    )

    hdfc_manifesto = (
        "Interested in credit card promotions, merchant discounts, banking partnerships, consumer offers, "
        "festive shopping instant rebates, reward points multipliers, and payment alliances."
    )
    hdfc = Agent(
        company_name="HDFC Bank",
        agent_name="HDFC Cards Agent",
        industry_category="Banking",
        description="Credit card promotions and merchant discounts",
        interest_manifesto=hdfc_manifesto,
        interest_embedding=p.get_embedding(hdfc_manifesto),
        webhook_url="http://agentconnect.internal/webhook/hdfc",
        api_key_hash="hash_hdfc",
        trust_score=1.0,
        is_active=True,
        response_mode="auto"
    )

    bajaj_manifesto = (
        "Interested in automobile launches, vehicle financing, electric vehicles, automotive partnerships, "
        "motorcycle sales, dealership promotions, test rides, and fleet acquisitions."
    )
    bajaj = Agent(
        company_name="Bajaj Auto",
        agent_name="Bajaj Dealership Agent",
        industry_category="Automotive",
        description="Automotive vehicle sales and financing",
        interest_manifesto=bajaj_manifesto,
        interest_embedding=p.get_embedding(bajaj_manifesto),
        webhook_url="http://agentconnect.internal/webhook/bajaj",
        api_key_hash="hash_bajaj",
        trust_score=1.0,
        is_active=True,
        response_mode="auto"
    )

    db_session.add_all([swiggy, phonepe, hdfc, bajaj])
    db_session.commit()

    # 2. Publish Swiggy Post
    post_title = "Diwali Festive Offer"
    post_content = "Swiggy offers 5% off all food deliveries during Diwali."
    post_category = "Food Delivery"
    post_tags = ["diwali", "festive", "offers", "food-delivery"]

    post_embedding = p.get_embedding(f"{post_title} {post_content} {' '.join(post_tags)}")
    post = Post(
        author_agent_id=swiggy.id,
        title=post_title,
        content=post_content,
        category=post_category,
        tags=post_tags,
        post_embedding=post_embedding
    )
    db_session.add(post)
    db_session.commit()

    # 3. Run Routing
    engine = RoutingEngine(db_session)
    result = engine.execute_routing(post, threshold=0.75)

    # 4. Assert routing outcomes
    notifications = db_session.query(Notification).filter(Notification.post_id == post.id).all()
    notified_agent_ids = {n.target_agent_id for n in notifications}

    assert phonepe.id in notified_agent_ids, "PhonePe must be notified"
    assert hdfc.id in notified_agent_ids, "HDFC Bank must be notified"
    assert bajaj.id not in notified_agent_ids, "Bajaj Auto must NOT be notified"

    # Verify score separation
    phonepe_notif = next(n for n in notifications if n.target_agent_id == phonepe.id)
    hdfc_notif = next(n for n in notifications if n.target_agent_id == hdfc.id)
    assert phonepe_notif.relevance_score >= 0.75
    assert hdfc_notif.relevance_score >= 0.75

    bajaj_log = db_session.query(RoutingLog).filter(
        RoutingLog.post_id == post.id,
        RoutingLog.target_agent_id == bajaj.id
    ).first()
    assert bajaj_log is not None
    assert bajaj_log.final_score < 0.75
    assert bajaj_log.routing_decision == "THRESHOLD_NOT_MET"

    # 5. Process autonomous responses
    for n in notifications:
        process_autonomous_response(db_session, n.id)

    comments = db_session.query(Comment).filter(Comment.post_id == post.id).all()
    comment_authors = {c.author_agent_id for c in comments}
    assert phonepe.id in comment_authors, "PhonePe should have generated a comment"
    assert hdfc.id in comment_authors, "HDFC Bank should have generated a comment"
    assert bajaj.id not in comment_authors, "Bajaj Auto should NOT comment"
