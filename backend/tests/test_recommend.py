# backend/tests/test_recommend.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app import app


@pytest.fixture
def client():
    """Creates a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ── Health check ──────────────────────────────────────────────
def test_health_check(client):
    res = client.get("/")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "running"


# ── Valid prediction ──────────────────────────────────────────
def test_recommend_valid(client):
    payload = {
        "N": 90, "P": 42, "K": 43,
        "temperature": 20.8,
        "humidity": 82.0,
        "ph": 6.5,
        "rainfall": 202.9
    }
    res  = client.post("/recommend-crop",
                       json=payload,
                       content_type="application/json")
    data = res.get_json()

    assert res.status_code == 200
    assert data["success"] is True
    assert "top_crop" in data
    assert "confidence" in data
    assert len(data["top_3"]) == 3
    assert data["top_crop"] == "rice"


# ── Missing fields ────────────────────────────────────────────
def test_recommend_missing_fields(client):
    payload = {"N": 90, "P": 42}   # missing K, temp, humidity, ph, rainfall
    res  = client.post("/recommend-crop",
                       json=payload,
                       content_type="application/json")
    data = res.get_json()

    assert res.status_code == 400
    assert data["success"] is False
    assert "Missing" in data["error"]


# ── Non-numeric fields ────────────────────────────────────────
def test_recommend_invalid_type(client):
    payload = {
        "N": "high", "P": 42, "K": 43,
        "temperature": 20.8, "humidity": 82.0,
        "ph": 6.5, "rainfall": 202.9
    }
    res  = client.post("/recommend-crop",
                       json=payload,
                       content_type="application/json")
    data = res.get_json()

    assert res.status_code == 400
    assert data["success"] is False


# ── No JSON body ──────────────────────────────────────────────
def test_recommend_no_body(client):
    res  = client.post("/recommend-crop",
                       content_type="application/json")
    data = res.get_json()

    assert res.status_code == 400
    assert data["success"] is False


# ── Confidence is percentage ──────────────────────────────────
def test_confidence_range(client):
    payload = {
        "N": 90, "P": 42, "K": 43,
        "temperature": 20.8, "humidity": 82.0,
        "ph": 6.5, "rainfall": 202.9
    }
    res  = client.post("/recommend-crop",
                       json=payload,
                       content_type="application/json")
    data = res.get_json()

    assert 0 <= data["confidence"] <= 100
    for crop in data["top_3"]:
        assert 0 <= crop["confidence"] <= 100