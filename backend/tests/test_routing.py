import pytest
from app.models.agent import Agent
from app.models.post import Post
from app.routing.engine import RoutingEngine
from app.ai.embeddings import get_embedding_provider

def test_routing_excludes_author_and_inactive(db_session):
    p = get_embedding_provider()

    # Create author
    author = Agent(
        company_name="AuthorCorp",
        agent_name="AuthorAgent",
        industry_category="Tech",
        description="Tech",
        interest_manifesto="Tech updates",
        interest_embedding=p.get_embedding("Tech updates"),
        webhook_url="http://agentconnect.internal/webhook/author",
        api_key_hash="hash1",
        is_active=True
    )
    # Create inactive candidate
    inactive = Agent(
        company_name="InactiveCorp",
        agent_name="InactiveAgent",
        industry_category="Tech",
        description="Tech",
        interest_manifesto="Tech updates and software launches",
        interest_embedding=p.get_embedding("Tech updates and software launches"),
        webhook_url="http://agentconnect.internal/webhook/inactive",
        api_key_hash="hash2",
        is_active=False
    )
    # Create active candidate
    active = Agent(
        company_name="ActiveCorp",
        agent_name="ActiveAgent",
        industry_category="Tech",
        description="Tech",
        interest_manifesto="Tech updates and software launches",
        interest_embedding=p.get_embedding("Tech updates and software launches"),
        webhook_url="http://agentconnect.internal/webhook/active",
        api_key_hash="hash3",
        is_active=True
    )
    db_session.add_all([author, inactive, active])
    db_session.commit()

    # Create post by author
    post = Post(
        author_agent_id=author.id,
        title="New Cloud Release",
        content="Deploying serverless agents across multiple regions.",
        category="Tech",
        tags=["cloud", "tech"],
        post_embedding=p.get_embedding("New Cloud Release serverless agents")
    )
    db_session.add(post)
    db_session.commit()

    engine = RoutingEngine(db_session)
    result = engine.execute_routing(post)

    # Candidates should exclude author and inactive
    candidate_names = [item["agent"].company_name for item in result["results"]]
    assert "AuthorCorp" not in candidate_names
    assert "InactiveCorp" not in candidate_names
    assert "ActiveCorp" in candidate_names
