import pytest

def test_feedback_submission_and_analytics(client):
    # 1. Register agent & post
    reg_resp = client.post("/api/v1/agents/register", json={
        "company_name": "FeedbackCorp",
        "agent_name": "FeedbackAgent",
        "industry_category": "Fintech",
        "description": "Fintech",
        "interest_manifesto": "Fintech offers and payment schemes",
        "webhook_url": "http://agentconnect.internal/webhook/fb",
        "response_mode": "auto"
    })
    agent = reg_resp.json()

    post_resp = client.post("/api/v1/posts", json={
        "title": "Fintech Partnership",
        "content": "Looking for digital wallet co-promotions.",
        "category": "Fintech"
    }, headers={"X-Author-Agent-Id": agent["id"]})
    post = post_resp.json()

    # 2. Submit positive feedback
    fb1 = client.post("/api/v1/feedback", json={
        "agent_id": agent["id"],
        "post_id": post["id"],
        "feedback_type": "ENGAGED",
        "relevance_rating": 4.5
    })
    assert fb1.status_code == 201

    # 3. Check analytics
    analytics_resp = client.get("/api/v1/feedback/analytics")
    assert analytics_resp.status_code == 200
    data = analytics_resp.json()
    assert data["total_feedback"] >= 1
    assert data["engaged_count"] >= 1
    assert data["engagement_rate"] > 0
