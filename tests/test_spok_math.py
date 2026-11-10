"""
Unit tests for HandoffLedger SPOK mathematical risk calculations and graph engine.
"""

import math
import pytest
from datetime import datetime, timezone, timedelta
from backend.app.models.schemas import (
    IngestedChunk,
    ClaimEntry,
    Citation,
    EvidenceState,
    SourceType,
    EntityType,
    AccessLabel,
)
from backend.app.services.spok import (
    calculate_concentration,
    calculate_stale_decay,
    calculate_evidence_weakness,
    calculate_spok_score,
    calculate_interview_priority,
    evaluate_node_spok,
)
from backend.app.services.graph_service import KnowledgeGraphEngine


def test_concentration_calculation():
    now_iso = datetime.now(timezone.utc).isoformat()

    # 1. Sole author (Alice = 100%)
    chunks_sole = [
        IngestedChunk(
            chunk_id="c1",
            source_id="repo",
            source_type=SourceType.GIT_COMMIT,
            author="alice",
            timestamp=now_iso,
            content="Initial commit",
        ),
        IngestedChunk(
            chunk_id="c2",
            source_id="chat",
            source_type=SourceType.CHAT_MESSAGE,
            author="Alice",
            timestamp=now_iso,
            content="Deploying now",
        ),
    ]
    c_sole = calculate_concentration(chunks_sole, "alice")
    assert pytest.approx(c_sole, 0.001) == 1.0

    # 2. Mixed authors: Alice (git commit = 1.0), Bob (git commit = 1.0)
    chunks_mixed = [
        IngestedChunk(
            chunk_id="c1",
            source_id="repo",
            source_type=SourceType.GIT_COMMIT,
            author="alice",
            timestamp=now_iso,
            content="Alice commit",
        ),
        IngestedChunk(
            chunk_id="c2",
            source_id="repo",
            source_type=SourceType.GIT_COMMIT,
            author="bob",
            timestamp=now_iso,
            content="Bob commit",
        ),
    ]
    c_mixed = calculate_concentration(chunks_mixed, "alice")
    assert pytest.approx(c_mixed, 0.001) == 0.5

    # 3. No contributions by leaver
    c_none = calculate_concentration(chunks_mixed, "charlie")
    assert c_none == 0.0

    # 4. Empty chunks
    assert calculate_concentration([], "alice") == 0.0


def test_stale_decay_half_life():
    ref_time = datetime(2026, 11, 10, 12, 0, 0, tzinfo=timezone.utc)

    # 0 days old -> StaleDecay = 0.0
    ts_now = ref_time.isoformat()
    d_0 = calculate_stale_decay(ts_now, reference_time=ref_time, half_life_days=60.0)
    assert pytest.approx(d_0, 0.001) == 0.0

    # Exactly 60 days old (one half-life) -> StaleDecay = 0.5
    ts_60d = (ref_time - timedelta(days=60)).isoformat()
    d_60 = calculate_stale_decay(ts_60d, reference_time=ref_time, half_life_days=60.0)
    assert pytest.approx(d_60, 0.005) == 0.5

    # 120 days old (two half-lives) -> StaleDecay = 0.75
    ts_120d = (ref_time - timedelta(days=120)).isoformat()
    d_120 = calculate_stale_decay(ts_120d, reference_time=ref_time, half_life_days=60.0)
    assert pytest.approx(d_120, 0.005) == 0.75


def test_evidence_weakness_penalties():
    now_iso = datetime.now(timezone.utc).isoformat()

    def make_claim(state: EvidenceState) -> ClaimEntry:
        return ClaimEntry(
            claim_id=f"c-{state.value}",
            entity_id="node1",
            claim_text="Sample statement",
            state=state,
            effective_label=AccessLabel.PUBLIC,
            source_timestamp=now_iso,
        )

    # All verified -> Weakness = 0.0
    claims_verified = [make_claim(EvidenceState.VERIFIED), make_claim(EvidenceState.VERIFIED)]
    assert calculate_evidence_weakness(claims_verified) == 0.0

    # All missing evidence -> Weakness = 1.0
    claims_missing = [make_claim(EvidenceState.MISSING_EVIDENCE)]
    assert calculate_evidence_weakness(claims_missing) == 1.0

    # Mix: verified (0.0) + inferred (0.4) + conflicting (0.8) + missing (1.0) -> avg = 2.2 / 4 = 0.55
    claims_mix = [
        make_claim(EvidenceState.VERIFIED),
        make_claim(EvidenceState.INFERRED),
        make_claim(EvidenceState.CONFLICTING),
        make_claim(EvidenceState.MISSING_EVIDENCE),
    ]
    w_mix = calculate_evidence_weakness(claims_mix)
    assert pytest.approx(w_mix, 0.001) == 0.55

    # Empty claims list -> max penalty (1.0)
    assert calculate_evidence_weakness([]) == 1.0


def test_spok_score_formula_and_bounds():
    # SPOK = 0.5 * Concentration + 0.25 * StaleDecay + 0.25 * EvidenceWeakness
    # Best case: 0, 0, 0 -> 0.0
    assert calculate_spok_score(0.0, 0.0, 0.0) == 0.0

    # Worst case: 1.0, 1.0, 1.0 -> 1.0
    assert calculate_spok_score(1.0, 1.0, 1.0) == 1.0

    # Known combination: C=1.0, D=0.5, W=0.4
    # Expected: 0.5*1.0 + 0.25*0.5 + 0.25*0.4 = 0.5 + 0.125 + 0.1 = 0.725
    assert pytest.approx(calculate_spok_score(1.0, 0.5, 0.4), 0.0001) == 0.725


def test_interview_priority_and_centrality_filtering():
    engine = KnowledgeGraphEngine(leaver_name="Alice")

    # Add core database service depended on by 3 services (in_degree = 3)
    engine.add_entity("db_core", "Postgres Core", EntityType.COMPONENT)
    engine.add_dependency("api_gateway", "db_core")
    engine.add_dependency("auth_service", "db_core")
    engine.add_dependency("billing_service", "db_core")

    # Add peripheral script touched once (in_degree = 0)
    engine.add_entity("cleanup_cron", "Cleanup Cron", EntityType.TASK)

    now_iso = datetime.now(timezone.utc).isoformat()
    # Attach sole commit by Alice to db_core
    chunk_db = IngestedChunk(
        chunk_id="c_db1",
        source_id="repo",
        source_type=SourceType.GIT_COMMIT,
        author="Alice",
        timestamp=now_iso,
        content="Setup database migrations",
    )
    engine.attach_chunk("db_core", chunk_db)

    # Attach inferred claim to db_core
    claim_db = ClaimEntry(
        claim_id="cl_db1",
        entity_id="db_core",
        claim_text="Database runs on port 5432",
        state=EvidenceState.INFERRED,
        effective_label=AccessLabel.PUBLIC,
        source_timestamp=now_iso,
    )
    engine.attach_claim("db_core", claim_db)

    # Compute graph SPOK
    top_nodes = engine.get_top_interview_nodes(limit=5)
    assert len(top_nodes) > 0
    top_node = top_nodes[0]

    # db_core should be top ranked because of high concentration (1.0) and high in-degree (3)
    assert top_node.node_id == "db_core"
    assert top_node.in_degree == 3
    assert not top_node.is_filtered_from_heatmap

    # cleanup_cron should be filtered from heatmap because in_degree=0 and chunks=0
    all_nodes = {n.node_id: n for n in engine.compute_all_spok()}
    assert all_nodes["cleanup_cron"].is_filtered_from_heatmap is True
