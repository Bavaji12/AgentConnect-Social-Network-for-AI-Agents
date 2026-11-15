import pytest

def test_post_creation_and_listing(client):
    # 1. Register agent
    reg_payload = {
        "company_name": "PostPublisherCorp",
        "agent_name": "Publisher Agent",
        "industry_category": "E-Commerce",
        "description": "E-commerce deals agent",
        "interest_manifesto": "E-commerce promotions and seasonal sales.",
        "webhook_url": "http://agentconnect.internal/webhook/publisher",
        "response_mode": "auto"
    }
    reg_resp = client.post("/api/v1/agents/register", json=reg_payload)
    agent = reg_resp.json()

    # 2. Publish post
    post_payload = {
        "title": "Summer Clearance Sale",
        "content": "Enjoy flat 40% off on all fashion apparel this weekend.",
        "category": "E-Commerce",
        "tags": ["summer", "sale", "apparel"]
    }
    post_resp = client.post(
        "/api/v1/posts",
        json=post_payload,
        headers={"X-Author-Agent-Id": agent["id"]}
    )
    assert post_resp.status_code == 201
    post_data = post_resp.json()
    assert post_data["title"] == "Summer Clearance Sale"
    assert post_data["author_company"] == "PostPublisherCorp"

    # 3. List posts
    list_resp = client.get("/api/v1/posts")
    assert list_resp.status_code == 200
    posts = list_resp.json()
    assert len(posts) >= 1
    assert any(p["id"] == post_data["id"] for p in posts)

    # 4. Add comment to post
    comment_payload = {
        "content": "Excited to promote this clearance sale across our reward channels!",
        "generated_by_llm": False
    }
    comment_resp = client.post(
        f"/api/v1/posts/{post_data['id']}/comments",
        json=comment_payload,
        headers={"X-Author-Agent-Id": agent["id"]}
    )
    assert comment_resp.status_code == 201
    comment_data = comment_resp.json()
    assert comment_data["content"] == comment_payload["content"]
