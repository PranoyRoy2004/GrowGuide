# backend/tests/test_parse.py

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


# ── Valid natural language input ──────────────────────────────
def test_parse_valid(client):
    payload = {
        "text"     : "I live in a tropical region with heavy rainfall and loamy soil.",
        "recommend": False
    }
    res  = client.post("/parse-input",
                       json=payload,
                       content_type="application/json")
    data = res.get_json()

    assert res.status_code == 200
    assert data["success"] is True
    assert "extracted_features" in data
    assert "extraction_method" in data

    features = data["extracted_features"]
    required = ["N","P","K","temperature","humidity","ph","rainfall"]
    for key in required:
        assert key in features
        assert features[key] is not None


# ── With recommendation flag ──────────────────────────────────
def test_parse_with_recommendation(client):
    payload = {
        "text"     : "Hot humid tropical climate with loamy soil and heavy rain.",
        "recommend": True
    }
    res  = client.post("/parse-input",
                       json=payload,
                       content_type="application/json")
    data = res.get_json()

    assert res.status_code == 200
    assert data["success"] is True
    assert "recommendation" in data
    assert "top_crop" in data["recommendation"]


# ── Too short input ───────────────────────────────────────────
def test_parse_too_short(client):
    payload = {"text": "hot"}
    res  = client.post("/parse-input",
                       json=payload,
                       content_type="application/json")
    data = res.get_json()

    assert res.status_code == 400
    assert data["success"] is False


# ── Missing text field ────────────────────────────────────────
def test_parse_missing_text(client):
    payload = {"recommend": True}
    res  = client.post("/parse-input",
                       json=payload,
                       content_type="application/json")
    data = res.get_json()

    assert res.status_code == 400
    assert data["success"] is False


# ── Extraction method is valid ────────────────────────────────
def test_parse_extraction_method(client):
    payload = {"text": "Tropical region with heavy rainfall and loamy soil."}
    res  = client.post("/parse-input",
                       json=payload,
                       content_type="application/json")
    data = res.get_json()

    valid_methods = ["rule_based", "hybrid", "llm_fallback"]
    assert data["extraction_method"] in valid_methods