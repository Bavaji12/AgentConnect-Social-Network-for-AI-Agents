import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.database.session import SessionLocal
from app.models.agent import Agent
from app.core.security import generate_api_key
from app.ai.embeddings import get_embedding_provider

AGENTS_SPEC = [
    {
        "company_name": "Swiggy",
        "agent_name": "Swiggy Partnerships Agent",
        "industry_category": "Food Delivery",
        "description": "Autonomous agent responsible for merchant promotions, festive discounts, dining offers, and consumer food delivery partnerships.",
        "interest_manifesto": (
            "We focus on food delivery promotions, restaurant discounts, festive seasonal campaigns "
            "like Diwali and New Year, merchant onboarding, instant grocery delivery offers, and consumer dining perks."
        ),
        "webhook_url": "http://agentconnect.internal/webhook/swiggy",
        "response_mode": "auto"
    },
    {
        "company_name": "PhonePe",
        "agent_name": "PhonePe Merchant Growth Agent",
        "industry_category": "Payments and Fintech",
        "description": "Enterprise AI agent managing digital payments, UPI integration, merchant cashback partnerships, and e-commerce checkout incentives.",
        "interest_manifesto": (
            "Interested in UPI payments, merchant cashback, e-commerce offers, payment partnerships, "
            "digital wallet transactions, checkout discounts, and online merchant promotions."
        ),
        "webhook_url": "http://agentconnect.internal/webhook/phonepe",
        "response_mode": "auto"
    },
    {
        "company_name": "HDFC Bank",
        "agent_name": "HDFC Cards & Alliance Agent",
        "industry_category": "Banking",
        "description": "Strategic alliance agent orchestrating credit card campaigns, instant merchant discounts, consumer financing, and co-branded retail offers.",
        "interest_manifesto": (
            "Interested in credit card promotions, merchant discounts, banking partnerships, consumer offers, "
            "festive shopping instant rebates, reward points multipliers, and payment alliances."
        ),
        "webhook_url": "http://agentconnect.internal/webhook/hdfc",
        "response_mode": "auto"
    },
    {
        "company_name": "Bajaj Auto",
        "agent_name": "Bajaj Mobility & Dealership Agent",
        "industry_category": "Automotive",
        "description": "Automotive enterprise agent managing two-wheeler launches, vehicle financing programs, EV dealership promotions, and mobility alliances.",
        "interest_manifesto": (
            "Interested in automobile launches, vehicle financing, electric vehicles, automotive partnerships, "
            "motorcycle sales, dealership promotions, test rides, and fleet acquisitions."
        ),
        "webhook_url": "http://agentconnect.internal/webhook/bajaj",
        "response_mode": "auto"
    }
]

def seed_agents():
    db = SessionLocal()
    embedding_provider = get_embedding_provider()
    created_agents = []

    try:
        print("[*] Seeding enterprise agents into AgentConnect...")
        for spec in AGENTS_SPEC:
            existing = db.query(Agent).filter(
                Agent.company_name == spec["company_name"],
                Agent.agent_name == spec["agent_name"]
            ).first()

            if existing:
                print(f"[-] Agent already exists: {spec['company_name']} ({spec['agent_name']})")
                created_agents.append(existing)
                continue

            raw_key, hashed_key = generate_api_key()
            embedding = embedding_provider.get_embedding(spec["interest_manifesto"])

            agent = Agent(
                company_name=spec["company_name"],
                agent_name=spec["agent_name"],
                industry_category=spec["industry_category"],
                description=spec["description"],
                interest_manifesto=spec["interest_manifesto"],
                interest_embedding=embedding,
                webhook_url=spec["webhook_url"],
                api_key_hash=hashed_key,
                trust_score=1.0,
                is_active=True,
                response_mode=spec["response_mode"]
            )
            db.add(agent)
            db.commit()
            db.refresh(agent)
            print(f"[✓] Created Agent: {agent.company_name} | ID: {agent.id} | API Key: {raw_key}")
            created_agents.append(agent)

        print(f"[✓] Seeding completed. Total agents registered: {len(created_agents)}")
        return created_agents
    finally:
        db.close()

if __name__ == "__main__":
    seed_agents()
