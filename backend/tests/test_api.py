"""
HealthSense AI — Backend API Test Suite
=======================================
Prompt 16: pytest + FastAPI TestClient

Covers:
  - GET /health                     (200, shape)
  - POST /predict  valid payload    (200, shape, value ranges)
  - POST /predict  age > 120        (422, validation_errors key)
  - POST /predict  height < 50 cm   (422, validation_errors key)
  - POST /predict  weight < 10 kg   (422, validation_errors key)
  - POST /predict  missing fields   (422)

Run from the project root:
    pytest backend/tests/test_api.py -q
"""

import pytest
from fastapi.testclient import TestClient

import os
import sys

# Add project root to sys.path so 'backend.main' can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.main import app


client = TestClient(app)

# ---------------------------------------------------------------------------
# Shared fixture: a valid, realistic assessment payload
# ---------------------------------------------------------------------------
VALID_PAYLOAD = {
    "personalInfo": {
        "fullName": "Test User",
        "age": "35",
        "gender": "Female",
        "height": "165",
        "weight": "65",
    },
    "lifestyle": {
        "smoking": "Never",
        "alcohol": "Occasionally",
        "exercise": "3-4 times/week",
        "sleep": "7-8",
        "water": "2-3L",
    },
    "symptoms": {
        "selectedSymptoms": [],
    },
}


# ===========================================================================
# 1. Health endpoint
# ===========================================================================


def test_health_returns_200():
    """GET /health must return HTTP 200."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_response_shape():
    """GET /health must include required top-level fields."""
    response = client.get("/health")
    body = response.json()
    assert "status" in body
    assert "ml_model_loaded" in body


def test_health_status_value():
    """GET /health status field must equal 'healthy'."""
    response = client.get("/health")
    body = response.json()
    assert body["status"] == "healthy"


# ===========================================================================
# 2. Valid prediction
# ===========================================================================


def test_predict_valid_returns_200():
    """POST /predict with a valid payload must return HTTP 200."""
    response = client.post("/predict", json=VALID_PAYLOAD)
    assert response.status_code == 200, response.text


def test_predict_valid_score_range():
    """score must be an integer between 0 and 100."""
    response = client.post("/predict", json=VALID_PAYLOAD)
    body = response.json()
    assert "score" in body
    assert isinstance(body["score"], int)
    assert 0 <= body["score"] <= 100


def test_predict_valid_risk_level_present():
    """riskLevel must be present in the response."""
    response = client.post("/predict", json=VALID_PAYLOAD)
    body = response.json()
    assert "riskLevel" in body
    assert body["riskLevel"] in ("Low Risk", "Moderate Risk", "High Risk")


def test_predict_valid_summary_present():
    """summary must be a non-empty string."""
    response = client.post("/predict", json=VALID_PAYLOAD)
    body = response.json()
    assert "summary" in body
    assert isinstance(body["summary"], str)
    assert len(body["summary"]) > 0


def test_predict_valid_recommendations_list():
    """recommendations must be a list."""
    response = client.post("/predict", json=VALID_PAYLOAD)
    body = response.json()
    assert "recommendations" in body
    assert isinstance(body["recommendations"], list)


def test_predict_valid_not_placeholder():
    """isPlaceholder must be False for a real ML prediction."""
    response = client.post("/predict", json=VALID_PAYLOAD)
    body = response.json()
    assert body.get("isPlaceholder") is False


def test_predict_valid_explainability_fields():
    """factorsConsidered, riskFactors, and protectiveFactors must be present lists."""
    response = client.post("/predict", json=VALID_PAYLOAD)
    body = response.json()
    for field in ("factorsConsidered", "riskFactors", "protectiveFactors"):
        assert field in body, f"Missing explainability field: {field}"
        assert isinstance(body[field], list), f"{field} must be a list"


# ===========================================================================
# 3. Invalid input validation — range checks
# ===========================================================================


def _payload_with(**overrides):
    """Return a copy of VALID_PAYLOAD with personalInfo fields overridden."""
    import copy
    payload = copy.deepcopy(VALID_PAYLOAD)
    payload["personalInfo"].update(overrides)
    return payload


def test_predict_age_above_120_returns_422():
    """age > 120 must return HTTP 422."""
    payload = _payload_with(age="150")
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_predict_age_above_120_validation_errors_key():
    """422 response for age > 120 must contain validation_errors."""
    payload = _payload_with(age="150")
    response = client.post("/predict", json=payload)
    body = response.json()
    assert "detail" in body
    detail = body["detail"]
    assert isinstance(detail, dict), "detail should be a dict with validation_errors"
    assert "validation_errors" in detail
    assert isinstance(detail["validation_errors"], list)
    assert len(detail["validation_errors"]) > 0


def test_predict_height_below_minimum_returns_422():
    """height < 50 cm must return HTTP 422."""
    payload = _payload_with(height="30")
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_predict_height_below_minimum_validation_errors_key():
    """422 response for height < 50 must contain validation_errors."""
    payload = _payload_with(height="30")
    response = client.post("/predict", json=payload)
    body = response.json()
    detail = body.get("detail", {})
    assert isinstance(detail, dict)
    assert "validation_errors" in detail


def test_predict_weight_below_minimum_returns_422():
    """weight < 10 kg must return HTTP 422."""
    payload = _payload_with(weight="5")
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_predict_weight_below_minimum_validation_errors_key():
    """422 response for weight < 10 must contain validation_errors."""
    payload = _payload_with(weight="5")
    response = client.post("/predict", json=payload)
    body = response.json()
    detail = body.get("detail", {})
    assert isinstance(detail, dict)
    assert "validation_errors" in detail


# ===========================================================================
# 4. Malformed / missing required data
# ===========================================================================


def test_predict_missing_personal_info_returns_422():
    """Payload missing personalInfo entirely must be rejected with HTTP 422."""
    malformed = {
        "lifestyle": VALID_PAYLOAD["lifestyle"],
        "symptoms": VALID_PAYLOAD["symptoms"],
    }
    response = client.post("/predict", json=malformed)
    assert response.status_code == 422


def test_predict_empty_body_returns_422():
    """An empty JSON body must be rejected with HTTP 422."""
    response = client.post("/predict", json={})
    assert response.status_code == 422
