# backend/tests/test_chat.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ── Welcome endpoint ──────────────────────────────────────────
def test_chat_welcome(client):
    res  = client.get("/chat/welcome")
    data = res.get_json()

    assert res.status_code == 200
    assert data["success"] is True
    assert len(data["message"]) > 10


# ── Valid chat message ────────────────────────────────────────
def test_chat_valid(client):
    payload = {
        "message": "What crops grow well in tropical regions?",
        "history": []
    }
    res  = client.post("/chat",
                       json=payload,
                       content_type="application/json")
    data = res.get_json()

    assert res.status_code == 200
    assert data["success"] is True
    assert "response" in data
    assert len(data["response"]) > 10
    assert "updated_history" in data
    assert len(data["updated_history"]) == 2   # user + assistant


# ── Multi-turn conversation ───────────────────────────────────
def test_chat_multi_turn(client):
    # First message
    res1  = client.post("/chat",
                        json={"message": "Tell me about rice farming.",
                              "history": []},
                        content_type="application/json")
    data1 = res1.get_json()
    assert data1["success"] is True

    # Second message with history
    res2  = client.post("/chat",
                        json={"message": "What fertilizer does it need?",
                              "history": data1["updated_history"]},
                        content_type="application/json")
    data2 = res2.get_json()

    assert data2["success"] is True
    assert len(data2["updated_history"]) == 4   # 2 turns × 2 messages


# ── Empty message ─────────────────────────────────────────────
def test_chat_empty_message(client):
    payload = {"message": "", "history": []}
    res  = client.post("/chat",
                       json=payload,
                       content_type="application/json")
    data = res.get_json()

    assert res.status_code == 400
    assert data["success"] is False


# ── Missing message field ─────────────────────────────────────
def test_chat_missing_field(client):
    payload = {"history": []}
    res  = client.post("/chat",
                       json=payload,
                       content_type="application/json")
    data = res.get_json()

    assert res.status_code == 400
    assert data["success"] is False


# ── Tokens used is numeric ────────────────────────────────────
def test_chat_tokens_returned(client):
    payload = {"message": "What is NPK fertilizer?", "history": []}
    res  = client.post("/chat",
                       json=payload,
                       content_type="application/json")
    data = res.get_json()

    assert isinstance(data["tokens_used"], int)
    assert data["tokens_used"] > 0