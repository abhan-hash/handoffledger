"""
API Endpoint Integration Tests using FastAPI TestClient
"""

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.config import settings

client = TestClient(app)


def test_health_check_endpoint():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_claims_endpoint_clearance_filtering():
    # Public request
    res_pub = client.get("/api/v1/claims", headers={"X-Clearance": "PUBLIC"})
    assert res_pub.status_code == 200
    claims_pub = res_pub.json()
    assert all(c["effective_label"] == "PUBLIC" for c in claims_pub)

    # Restricted request
    res_rest = client.get("/api/v1/claims", headers={"X-Clearance": "RESTRICTED"})
    assert res_rest.status_code == 200
    claims_rest = res_rest.json()
    assert len(claims_rest) >= len(claims_pub)


def test_verify_endpoint_runs_pipeline():
    res = client.post("/api/v1/verify")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "summary" in data
    assert data["summary"]["total"] >= 5


def test_interview_queue_and_answer_submission():
    res_q = client.get("/api/v1/interview/queue?limit=5")
    assert res_q.status_code == 200
    questions = res_q.json()
    assert len(questions) > 0
    q1 = questions[0]

    # Submit answer via design contract payload
    payload = {
        "question_id": q1["question_id"],
        "action": "confirm",
        "response_text": None,
    }
    res_ans = client.post("/api/v1/interview/answer", json=payload)
    assert res_ans.status_code == 200
    assert res_ans.json()["state"] == "verified"


def test_successor_runway_view_no_canary_leak():
    res = client.get("/api/v1/handover/view", headers={"X-Clearance": "INTERNAL"})
    assert res.status_code == 200
    data = res.json()
    assert data["canary_leak_detected"] is False
    assert "panes" in data
    assert "landmines" in data["panes"]
    assert "accounts" in data["panes"]
    assert "decisions" in data["panes"]
    assert "backlog" in data["panes"]
    assert len(data["panes"]["landmines"]) >= 3
    assert len(data["panes"]["accounts"]) >= 3
    assert len(data["panes"]["decisions"]) >= 3
    assert len(data["panes"]["backlog"]) >= 3
    assert settings.CANARY_TOKEN_SEED not in str(data)


def test_evaluation_benchmark_endpoint():
    res = client.post("/api/v1/evaluate", json={"dataset_name": "v1_demo", "viewer_clearance": "INTERNAL"})
    assert res.status_code == 200
    eval_res = res.json()
    assert eval_res["held_out_questions_count"] == 20
    assert eval_res["accuracy_delta"] > 0
    assert eval_res["passed_canary_negative_controls"] is True
