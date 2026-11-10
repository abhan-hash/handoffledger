"""
Integration tests for HandoffLedger Held-Out Benchmark Evaluation Harness
"""

from backend.app.services.synthetic_data import get_v1_demo_fixtures
from backend.app.services.evaluation import (
    evaluate_handover_benchmark,
    load_golden_eval_questions,
)
from backend.app.models.schemas import AccessLabel
from backend.app.config import settings


def test_golden_eval_questions_file_presence_and_count():
    questions = load_golden_eval_questions()
    assert len(questions) == 20, f"Expected 20 golden questions, found {len(questions)}"
    categories = {q["category"] for q in questions}
    assert "security_canary_probe" in categories
    assert "architecture_recall" in categories


def test_handover_evaluation_accuracy_delta():
    _, claims, _ = get_v1_demo_fixtures()
    result = evaluate_handover_benchmark(claims, clearance=AccessLabel.INTERNAL)

    assert result.benchmark_dataset == "v1_demo"
    assert result.held_out_questions_count == 20
    assert result.successor_ledger_accuracy > result.raw_source_baseline_accuracy
    assert result.accuracy_delta >= 0.40  # >= +40% accuracy gain
    assert result.passed_canary_negative_controls is True
    assert result.canary_leakage_rate == 0.0


def test_canary_negative_control_fails_if_canary_exposed():
    _, claims, _ = get_v1_demo_fixtures()
    # If unprivileged context somehow discloses canary
    leaked_claim = claims[0].model_copy(
        update={"claim_text": f"Leaked canary string: {settings.CANARY_TOKEN_SEED}"}
    )
    tampered_claims = [leaked_claim] + claims[1:]

    result = evaluate_handover_benchmark(tampered_claims, clearance=AccessLabel.INTERNAL)
    assert result.passed_canary_negative_controls is False
    assert result.canary_leakage_rate == 1.0
