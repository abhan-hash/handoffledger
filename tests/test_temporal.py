"""
Unit tests for HandoffLedger Temporal Progression Resolver
"""

from datetime import datetime, timezone, timedelta
from backend.app.models.schemas import (
    ClaimEntry,
    Citation,
    EvidenceState,
    AccessLabel,
)
from backend.app.services.temporal import resolve_temporal_supersession


def test_temporal_supersession_marks_older_claim_superseded():
    now = datetime(2026, 11, 10, 12, 0, 0, tzinfo=timezone.utc)
    ts_old = (now - timedelta(days=90)).isoformat()
    ts_new = (now - timedelta(days=10)).isoformat()

    claim_old = ClaimEntry(
        claim_id="claim-db-old",
        entity_id="database_engine",
        attribute_key="db_type",
        claim_text="Database backend is sqlite3.",
        state=EvidenceState.VERIFIED,
        effective_label=AccessLabel.PUBLIC,
        citations=[Citation(chunk_id="chunk-1", quote_span="sqlite3")],
        source_timestamp=ts_old,
        created_by="Bob Developer",
    )

    claim_new = ClaimEntry(
        claim_id="claim-db-new",
        entity_id="database_engine",
        attribute_key="db_type",
        claim_text="Database was migrated to postgresql on port 5432.",
        state=EvidenceState.VERIFIED,
        effective_label=AccessLabel.PUBLIC,
        citations=[Citation(chunk_id="chunk-2", quote_span="postgresql")],
        source_timestamp=ts_new,
        created_by="Alice Maintainer",
    )

    resolved = resolve_temporal_supersession([claim_old, claim_new])
    resolved_dict = {c.claim_id: c for c in resolved}

    assert resolved_dict["claim_db_new" if "claim_db_new" in resolved_dict else "claim-db-new"].state == EvidenceState.VERIFIED
    assert resolved_dict["claim-db-old"].state == EvidenceState.SUPERSEDED
    assert len(resolved_dict["claim-db-old"].version_history) >= 1
    assert resolved_dict["claim-db-old"].version_history[0]["transition"] == "superseded_by_newer_claim"


def test_independent_attributes_not_superseded():
    now = datetime(2026, 11, 10, 12, 0, 0, tzinfo=timezone.utc).isoformat()
    c1 = ClaimEntry(
        claim_id="c1",
        entity_id="database_engine",
        attribute_key="port",
        claim_text="Runs on port 5432",
        state=EvidenceState.VERIFIED,
        effective_label=AccessLabel.PUBLIC,
        source_timestamp=now,
    )
    c2 = ClaimEntry(
        claim_id="c2",
        entity_id="database_engine",
        attribute_key="max_connections",
        claim_text="Max connections set to 100",
        state=EvidenceState.VERIFIED,
        effective_label=AccessLabel.PUBLIC,
        source_timestamp=now,
    )

    resolved = resolve_temporal_supersession([c1, c2])
    resolved_dict = {c.claim_id: c for c in resolved}
    assert resolved_dict["c1"].state == EvidenceState.VERIFIED
    assert resolved_dict["c2"].state == EvidenceState.VERIFIED
