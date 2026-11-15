import pytest
from app.models.agent import Agent

def test_agent_registration(client):
    payload = {
        "company_name": "TestCorp",
        "agent_name": "Test Agent",
        "industry_category": "Logistics",
        "description": "Enterprise delivery logistics agent",
        "interest_manifesto": "Autonomous drone dispatch, parcel routing, and supply chain tracking.",
        "webhook_url": "http://agentconnect.internal/webhook/testcorp",
        "response_mode": "auto"
    }
    response = client.post("/api/v1/agents/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["company_name"] == "TestCorp"
    assert "api_key" in data
    assert data["api_key"].startswith("agnt_")
    assert data["trust_score"] == 1.0

def test_duplicate_agent_registration_blocked(client):
    payload = {
        "company_name": "DupCorp",
        "agent_name": "Dup Agent",
        "industry_category": "Fintech",
        "description": "Payment agent",
        "interest_manifesto": "UPI and wallet payments.",
        "webhook_url": "http://agentconnect.internal/webhook/dup",
        "response_mode": "auto"
    }
    r1 = client.post("/api/v1/agents/register", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/api/v1/agents/register", json=payload)
    assert r2.status_code == 400
    assert "already exists" in r2.json()["detail"]

def test_agent_login(client):
    reg_payload = {
        "company_name": "LoginCorp",
        "agent_name": "Login Agent",
        "industry_category": "Retail",
        "description": "Retail discounts agent",
        "interest_manifesto": "Retail flash sales and coupon vouchers.",
        "webhook_url": "http://agentconnect.internal/webhook/login",
        "response_mode": "auto"
    }
    reg_resp = client.post("/api/v1/agents/register", json=reg_payload)
    agent_data = reg_resp.json()
    agent_id = agent_data["id"]
    api_key = agent_data["api_key"]

    login_resp = client.post("/api/v1/agents/login", json={"agent_id": agent_id, "api_key": api_key})
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert token_data["agent"]["id"] == agent_id
