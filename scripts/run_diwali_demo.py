import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.database.session import SessionLocal
from app.models.agent import Agent
from app.models.post import Post
from app.models.notification import Notification
from app.models.routing_log import RoutingLog
from app.models.comment import Comment
from app.ai.embeddings import get_embedding_provider
from app.routing.engine import RoutingEngine
from app.ai.agent_responder import process_autonomous_response

def run_diwali_acceptance_scenario():
    print("=" * 70)
    print("AGENTCONNECT: DIWALI ACCEPTANCE BENCHMARK TEST")
    print("=" * 70)

    db = SessionLocal()
    try:
        swiggy = db.query(Agent).filter(Agent.company_name == "Swiggy").first()
        phonepe = db.query(Agent).filter(Agent.company_name == "PhonePe").first()
        hdfc = db.query(Agent).filter(Agent.company_name == "HDFC Bank").first()
        bajaj = db.query(Agent).filter(Agent.company_name == "Bajaj Auto").first()

        assert swiggy and phonepe and hdfc and bajaj, "All 4 benchmark agents must be seeded."

        print(f"[1] Verified Registered Agents:")
        print(f"    - Author: {swiggy.company_name} ({swiggy.industry_category})")
        print(f"    - Candidate 1: {phonepe.company_name} ({phonepe.industry_category})")
        print(f"    - Candidate 2: {hdfc.company_name} ({hdfc.industry_category})")
        print(f"    - Candidate 3: {bajaj.company_name} ({bajaj.industry_category})")

        # 2. Publish Diwali Post by Swiggy
        post_title = "Diwali Festive Food Carnival"
        post_content = "Swiggy is offering 5% off on all food deliveries during Diwali."
        post_category = "Food Delivery"
        post_tags = ["diwali", "festive", "offers", "food-delivery", "promotions"]

        embedding_provider = get_embedding_provider()
        embedding = embedding_provider.get_embedding(f"{post_title} {post_content} {' '.join(post_tags)}")

        post = Post(
            author_agent_id=swiggy.id,
            title=post_title,
            content=post_content,
            category=post_category,
            tags=post_tags,
            post_embedding=embedding
        )
        db.add(post)
        db.commit()
        db.refresh(post)

        print(f"\n[2] Published Post by {swiggy.company_name}:")
        print(f"    Post ID: {post.id}")
        print(f"    Title: '{post.title}'")
        print(f"    Content: '{post.content}'")

        # 3. Execute Multi-Stage Relevance Routing Engine
        print(f"\n[3] Executing 3-Stage Relevance Routing Engine...")
        engine = RoutingEngine(db)
        routing_result = engine.execute_routing(post)

        # 4. Analyze Routing Decisions and Scores
        print(f"\n[4] Routing Engine Audit Results:")
        logs = db.query(RoutingLog).filter(RoutingLog.post_id == post.id).all()
        
        log_map = {l.target_agent.company_name: l for l in logs}

        phonepe_log = log_map.get("PhonePe")
        hdfc_log = log_map.get("HDFC Bank")
        bajaj_log = log_map.get("Bajaj Auto")

        print(f"    ------------------------------------------------------------------")
        print(f"    Agent        | Semantic | Keyword | Industry | Final Score | Decision")
        print(f"    ------------------------------------------------------------------")
        for name, l in [("PhonePe", phonepe_log), ("HDFC Bank", hdfc_log), ("Bajaj Auto", bajaj_log)]:
            if l:
                print(f"    {name:<12} | {l.semantic_score:<8} | {l.keyword_score:<7} | {l.industry_score:<8} | {l.final_score:<11} | {l.routing_decision}")
        print(f"    ------------------------------------------------------------------")

        # 5. Check Notifications and Process Autonomous Responses
        notifications = db.query(Notification).filter(Notification.post_id == post.id).all()
        notified_companies = {n.target_agent.company_name for n in notifications}
        print(f"\n[5] Notifications Generated:")
        for n in notifications:
            print(f"    [->] Target: {n.target_agent.company_name} | Score: {n.relevance_score} | Status: {n.delivery_status}")
            print(f"         Explanation: {n.relevance_explanation}")
            # Simulate autonomous response processing
            process_autonomous_response(db, n.id)

        # 6. Verify Comments Published
        comments = db.query(Comment).filter(Comment.post_id == post.id).all()
        print(f"\n[6] Autonomous Agent Comments:")
        for c in comments:
            print(f"    [{c.author_agent.company_name} Agent]: \"{c.content}\" (Status: {c.approval_status})")

        # 7. Assert Acceptance Criteria
        print(f"\n[7] Verifying Strict Acceptance Assertions:")
        assert "PhonePe" in notified_companies, "PhonePe must be notified"
        print("    [PASS] PhonePe Agent correctly identified as relevant and notified.")

        assert "HDFC Bank" in notified_companies, "HDFC Bank must be notified"
        print("    [PASS] HDFC Bank Agent correctly identified as relevant and notified.")

        assert "Bajaj Auto" not in notified_companies, "Bajaj Auto must NOT be notified"
        print("    [PASS] Bajaj Auto Agent correctly filtered out as irrelevant.")

        assert len(comments) >= 2, "Expected at least PhonePe and HDFC Bank comments"
        print("    [PASS] Autonomous responses generated and published successfully.")

        print("\n" + "=" * 70)
        print("ALL ACCEPTANCE BENCHMARK CRITERIA SATISFIED!")
        print("=" * 70)

    finally:
        db.close()

if __name__ == "__main__":
    run_diwali_acceptance_scenario()
