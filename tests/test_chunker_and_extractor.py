"""
Unit tests for Chunker, Extractor, and Bounded Contradiction Pass
"""

from backend.app.services.chunker import (
    chunk_git_commit,
    chunk_chat_message,
    chunk_task_entry,
    chunk_markdown_document,
)
from backend.app.services.extractor import extract_claims_from_chunk
from backend.app.services.contradiction import apply_bounded_contradiction_check
from backend.app.models.schemas import (
    ClaimEntry,
    EvidenceState,
    AccessLabel,
)


def test_chunk_git_commit_and_extract():
    commit_data = {
        "commit_hash": "4f2a91b",
        "author": "Alice Maintainer",
        "date": "2026-10-11T14:22:00Z",
        "message": "feat(db): migrated database engine from sqlite to postgresql on port 5432 to handle concurrency.",
        "access_label": "PUBLIC",
    }
    chunk = chunk_git_commit(commit_data)
    assert chunk.author == "Alice Maintainer"
    assert chunk.access_label == AccessLabel.PUBLIC
    assert "migrated database engine" in chunk.content

    claims = extract_claims_from_chunk(chunk)
    assert len(claims) >= 1
    assert claims[0].entity_id == "database_engine"
    assert claims[0].citations[0].quote_span in chunk.content


def test_chunk_markdown_document_lattice_levels():
    doc = """
# Public Overview [Access: PUBLIC]
Postgres is running on port 5432.

# Restricted Vault [Access: RESTRICTED]
Root production deployment key is CANARY_SECRET_UUIDv4_9823f4b1.
"""
    chunks = chunk_markdown_document(doc)
    assert len(chunks) == 2
    assert chunks[0].access_label == AccessLabel.PUBLIC
    assert chunks[1].access_label == AccessLabel.RESTRICTED
    assert chunks[1].has_canary is True


def test_bounded_contradiction_check_flags_conflicts():
    c1 = ClaimEntry(
        claim_id="c1",
        entity_id="port_setting",
        attribute_key="app_port",
        claim_text="App listens on port 8000.",
        state=EvidenceState.VERIFIED,
        effective_label=AccessLabel.PUBLIC,
        source_timestamp="2026-11-10T12:00:00Z",
    )
    c2 = ClaimEntry(
        claim_id="c2",
        entity_id="port_setting",
        attribute_key="app_port",
        claim_text="App listens on port 9000.",
        state=EvidenceState.VERIFIED,
        effective_label=AccessLabel.PUBLIC,
        source_timestamp="2026-11-10T12:00:00Z",
    )

    resolved = apply_bounded_contradiction_check([c1, c2])
    states = {c.claim_id: c.state for c in resolved}
    assert states["c1"] == EvidenceState.CONFLICTING
    assert states["c2"] == EvidenceState.CONFLICTING


def test_fintech_chunks_and_claims_extraction():
    """Verify high-scale fintech infrastructure chunks extract with exact substring quotes."""
    from backend.app.models.schemas import IngestedChunk, SourceType

    chk = IngestedChunk(
        chunk_id="chunk-fintech-01",
        source_id="chat_ops.json",
        source_type=SourceType.CHAT_MESSAGE,
        author="Alice Chen",
        timestamp="2026-11-09T10:00:00Z",
        access_label=AccessLabel.INTERNAL,
        content="Incident note: Stripe webhook retries can cause race conditions if the event timestamp is older than 5 minutes.",
    )
    claims = extract_claims_from_chunk(chk)
    assert len(claims) >= 1
    assert any("webhook" in c.entity_id or "gateway" in c.entity_id for c in claims)
    for c in claims:
        assert c.citations[0].quote_span in chk.content
