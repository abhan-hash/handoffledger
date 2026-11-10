"""
Tests for NVIDIA Nemotron Ultra 550B Integration
Verifies LLM status endpoint, graceful heuristic fallback when unauthenticated,
and claim extraction formatting with exact citations.
"""

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.config import settings
from backend.app.services.nemotron_client import extract_claims_nemotron, generate_nemotron_hypothesis
from backend.app.models.schemas import AccessLabel

client = TestClient(app)


def test_nemotron_llm_status_endpoint():
    """Verify /api/v1/llm/status returns the NVIDIA Nemotron model metadata."""
    response = client.get("/api/v1/llm/status")
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "NVIDIA NIM"
    assert "nemotron" in data["model"].lower()
    assert data["active_tier"] == "NVIDIA Nemotron Ultra 550B"


def test_nemotron_llm_synthesize_endpoint():
    """Verify /api/v1/llm/synthesize returns a structured briefing."""
    response = client.post("/api/v1/llm/synthesize", json={"target_role": "successor"})
    assert response.status_code == 200
    data = response.json()
    assert "briefing" in data
    assert "model" in data
    assert len(data["briefing"]) > 50


def test_nemotron_client_graceful_offline_fallback():
    """When NVIDIA_API_KEY is not set or empty, nemotron extraction gracefully returns empty list."""
    original_key = settings.NVIDIA_API_KEY
    try:
        settings.NVIDIA_API_KEY = ""
        claims = extract_claims_nemotron(
            content="Database migrated to postgresql on port 5432.",
            chunk_id="chk-001",
            author="engineer",
            access_label=AccessLabel.INTERNAL,
            timestamp="2026-11-10T12:00:00Z",
        )
        assert claims == []

        hyp = generate_nemotron_hypothesis("database_engine", "SYSTEM_COMPONENT", [])
        assert hyp is None
    finally:
        settings.NVIDIA_API_KEY = original_key
