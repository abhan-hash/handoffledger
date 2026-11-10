"""
Unit tests for deterministic citation verifier and temporal progression resolver.
"""

import pytest
from datetime import datetime, timezone, timedelta
from backend.app.models.schemas import (
    IngestedChunk,
    ClaimEntry,
    Citation,
    EvidenceState,
    SourceType,
    AccessLabel,
)
from backend.app.services.verifier import (
    verify_citation_spans,
    compute_effective_label,
    resolve_temporal_supersession,
    run_verification_pipeline,
)


def test_verify_citation_spans_success():
    chunks = {
        "c1": IngestedChunk(
            chunk_id="c1",
            source_id="repo",
            source_type=SourceType.GIT_COMMIT,
            author="alice",
            timestamp="2026-11-01T12:00:00Z",
            content="Migrated SQLite to PostgreSQL on port 5432.",
        )
    }
    claim = ClaimEntry(
        claim_id="cl1",
        entity_id="db",
        claim_text="Database is Postgres",
        state=EvidenceState.INFERRED,
        effective_label=AccessLabel.PUBLIC,
        citations=[Citation(chunk_id="c1", quote_span="Migrated SQLite to PostgreSQL")],
        source_timestamp="2026-11-01T12:00:00Z",
    )
    is_valid, reason = verify_citation_spans(claim, chunks)
    assert is_valid is True
    assert "verified" in reason


def test_verify_citation_spans_failure_missing_chunk():
    claim = ClaimEntry(
        claim_id="cl1",
        entity_id="db",
        claim_text="Database is Postgres",
        state=EvidenceState.INFERRED,
        effective_label=AccessLabel.PUBLIC,
        citations=[Citation(chunk_id="nonexistent-chunk", quote_span="PostgreSQL")],
        source_timestamp="2026-11-01T12:00:00Z",
    )
    is_valid, reason = verify_citation_spans(claim, {})
    assert is_valid is False
    assert "not found" in reason


def test_verify_citation_spans_failure_corrupted_quote():
    chunks = {
        "c1": IngestedChunk(
            chunk_id="c1",
            source_id="repo",
            source_type=SourceType.GIT_COMMIT,
            author="alice",
            timestamp="2026-11-01T12:00:00Z",
            content="We deployed Redis.",
        )
    }
    claim = ClaimEntry(
        claim_id="cl1",
        entity_id="cache",
        claim_text="Memcached is deployed",
        state=EvidenceState.INFERRED,
        effective_label=AccessLabel.PUBLIC,
        citations=[Citation(chunk_id="c1", quote_span="We deployed Memcached")],  # Corrupted quote
        source_timestamp="2026-11-01T12:00:00Z",
    )
    is_valid, reason = verify_citation_spans(claim, chunks)
    assert is_valid is False
    assert "not found in chunk content" in reason


def test_temporal_supersession_logic():
    t_old = "2026-09-01T12:00:00Z"
    t_new = "2026-10-15T12:00:00Z"

    claim_old = ClaimEntry(
        claim_id="cl-old",
        entity_id="db",
        attribute_key="engine",
        claim_text="SQLite3 is the database",
        state=EvidenceState.INFERRED,
        effective_label=AccessLabel.PUBLIC,
        source_timestamp=t_old,
    )
    claim_new = ClaimEntry(
        claim_id="cl-new",
        entity_id="db",
        attribute_key="engine",
        claim_text="PostgreSQL is the database",
        state=EvidenceState.VERIFIED,
        effective_label=AccessLabel.PUBLIC,
        source_timestamp=t_new,
    )

    resolved = resolve_temporal_supersession([claim_old, claim_new])
    by_id = {c.claim_id: c for c in resolved}

    # Old claim should be superseded
    assert by_id["cl-old"].state == EvidenceState.SUPERSEDED
    # New claim remains verified
    assert by_id["cl-new"].state == EvidenceState.VERIFIED
