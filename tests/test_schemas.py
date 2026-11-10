"""
Unit tests for HandoffLedger data models and security lattice.
"""

import pytest
from datetime import datetime, timezone
from backend.app.models.schemas import (
    AccessLabel,
    EvidenceState,
    IngestedChunk,
    ClaimEntry,
    Citation,
    SourceType,
    EntityType,
)


def test_access_label_lattice_ranking():
    assert AccessLabel.rank(AccessLabel.PUBLIC) == 0
    assert AccessLabel.rank(AccessLabel.INTERNAL) == 1
    assert AccessLabel.rank(AccessLabel.LEAD_ONLY) == 2
    assert AccessLabel.rank(AccessLabel.RESTRICTED) == 3


def test_access_label_can_access():
    admin = AccessLabel.RESTRICTED
    lead = AccessLabel.LEAD_ONLY
    member = AccessLabel.INTERNAL
    anon = AccessLabel.PUBLIC

    # Admin accesses everything
    assert admin.can_access(AccessLabel.RESTRICTED)
    assert admin.can_access(AccessLabel.LEAD_ONLY)
    assert admin.can_access(AccessLabel.INTERNAL)
    assert admin.can_access(AccessLabel.PUBLIC)

    # Lead can access internal and public, but not restricted
    assert lead.can_access(AccessLabel.LEAD_ONLY)
    assert lead.can_access(AccessLabel.INTERNAL)
    assert lead.can_access(AccessLabel.PUBLIC)
    assert not lead.can_access(AccessLabel.RESTRICTED)

    # Member cannot access lead_only or restricted
    assert member.can_access(AccessLabel.INTERNAL)
    assert not member.can_access(AccessLabel.LEAD_ONLY)
    assert not member.can_access(AccessLabel.RESTRICTED)

    # Anon accesses only public
    assert anon.can_access(AccessLabel.PUBLIC)
    assert not anon.can_access(AccessLabel.INTERNAL)


def test_lattice_join_operation():
    # Least upper bound (max rank)
    labels = [AccessLabel.PUBLIC, AccessLabel.INTERNAL]
    assert AccessLabel.join(labels) == AccessLabel.INTERNAL

    labels_with_lead = [AccessLabel.PUBLIC, AccessLabel.LEAD_ONLY, AccessLabel.INTERNAL]
    assert AccessLabel.join(labels_with_lead) == AccessLabel.LEAD_ONLY

    labels_with_restricted = [AccessLabel.PUBLIC, AccessLabel.RESTRICTED, AccessLabel.INTERNAL]
    assert AccessLabel.join(labels_with_restricted) == AccessLabel.RESTRICTED

    assert AccessLabel.join([]) == AccessLabel.PUBLIC


def test_ingested_chunk_model():
    now_iso = datetime.now(timezone.utc).isoformat()
    chunk = IngestedChunk(
        chunk_id="chunk-abc-123",
        source_id="git_log.json",
        source_type=SourceType.GIT_COMMIT,
        author="alice",
        timestamp=now_iso,
        access_label=AccessLabel.INTERNAL,
        content="Migrated SQLite to PostgreSQL for concurrency.",
        has_canary=False,
    )
    assert chunk.chunk_id == "chunk-abc-123"
    assert chunk.access_label == AccessLabel.INTERNAL
    assert chunk.source_type == SourceType.GIT_COMMIT


def test_claim_entry_model():
    now_iso = datetime.now(timezone.utc).isoformat()
    claim = ClaimEntry(
        claim_id="claim-001",
        entity_id="database_engine",
        attribute_key="db_type",
        claim_text="Database was migrated to PostgreSQL.",
        state=EvidenceState.VERIFIED,
        effective_label=AccessLabel.INTERNAL,
        citations=[Citation(chunk_id="chunk-abc-123", quote_span="Migrated SQLite to PostgreSQL")],
        source_timestamp=now_iso,
    )
    assert claim.state == EvidenceState.VERIFIED
    assert len(claim.citations) == 1
    assert claim.citations[0].chunk_id == "chunk-abc-123"
