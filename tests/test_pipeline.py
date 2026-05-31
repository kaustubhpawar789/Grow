import pytest
import httpx
from api.guardrails import check_pii, check_advisory_intent

BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Verify the API is running."""
    response = httpx.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_guardrails_pii_unit():
    """Unit test PII regex."""
    assert check_pii("my PAN is ABCDE1234F") is True
    assert check_pii("call me at 9876543210") is True
    assert check_pii("what is the expense ratio") is False

def test_guardrails_advisory_unit():
    """Unit test advisory intent classifier."""
    assert check_advisory_intent("should I invest in HDFC?") is True
    assert check_advisory_intent("which is better, sbi or axis?") is True
    assert check_advisory_intent("what is the AUM of SBI Bluechip?") is False

def test_pii_rejection_api():
    """Verify the API rejects PII queries."""
    response = httpx.post(f"{BASE_URL}/chat", json={"query": "my email is test@test.com"})
    assert response.status_code == 400
    assert "PII" in response.json()["detail"]

def test_advisory_refusal_api():
    """Verify the API gracefully refuses investment advice."""
    response = httpx.post(f"{BASE_URL}/chat", json={"query": "Is it a good time to buy mutual funds?"})
    assert response.status_code == 200
    data = response.json()
    assert data["is_refusal"] is True
    assert "facts-only assistant" in data["response"].lower()

def test_factual_retrieval_api():
    """Verify the API answers factual questions and includes source citation."""
    response = httpx.post(f"{BASE_URL}/chat", json={"query": "What is the exit load for HDFC Mid Cap?"})
    assert response.status_code == 200
    data = response.json()
    assert data["is_refusal"] is False
    
    # Check length
    sentences = data["response"].split(". ")
    assert len(sentences) <= 5 # allowing 3 for content + 2 for source lines
    
    # Check citation
    assert "Source:" in data["response"]
    assert "Last updated" in data["response"]
