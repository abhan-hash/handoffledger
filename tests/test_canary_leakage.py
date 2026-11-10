"""
Automated Canary Leakage Assertion Tests
Verifies zero canary leakage across prompt context, API payloads, successor views, and logs.
"""

import pytest
from backend.app.models.schemas import (
    AccessLabel,
    IngestedChunk,
    ClaimEntry,
    Citation,
    EvidenceState,
    SourceType,
)
from backend.app.services.clearance import (
    filter_chunks_by_clearance,
    filter_claims_by_clearance,
    project_successor_claims,
    detect_canary_leakage,
)
from backend.app.services.synthetic_data import get_v1_demo_fixtures
from backend.app.config import settings


def test_canary_not_leaked_to_public_context():
    chunks, claims, _ = get_v1_demo_fixtures()
    canary = settings.CANARY_TOKEN_SEED

    # 1. Verify canary is indeed in the raw restricted chunk
    assert any(canary in c.content for c in chunks)

    # 2. Filter for PUBLIC viewer
    public_chunks = filter_chunks_by_clearance(chunks, AccessLabel.PUBLIC)
    public_payload = " ".join(c.content for c in public_chunks)
    assert not detect_canary_leakage(public_payload)
    assert canary not in public_payload

    # 3. Filter for INTERNAL viewer (still should not see RESTRICTED canary)
    internal_chunks = filter_chunks_by_clearance(chunks, AccessLabel.INTERNAL)
    internal_payload = " ".join(c.content for c in internal_chunks)
    assert not detect_canary_leakage(internal_payload)
    assert canary not in internal_payload


def test_canary_not_leaked_in_successor_projected_view():
    _, claims, _ = get_v1_demo_fixtures()
    canary = settings.CANARY_TOKEN_SEED

    # Successor with INTERNAL clearance views claims
    projected = project_successor_claims(claims, AccessLabel.INTERNAL)

    # Rendered string representation
    projected_text = " ".join(c.claim_text for c in projected)

    # Invariant: Canary MUST NOT leak into successor view
    assert not detect_canary_leakage(projected_text)
    assert canary not in projected_text

    # Restricted claim must appear as redacted placeholder
    restricted_cards = [c for c in projected if "RESTRICTED CLAIM" in c.claim_text]
    assert len(restricted_cards) > 0
    assert "Contact Lead" in restricted_cards[0].claim_text


def test_canary_accessible_only_with_restricted_clearance():
    _, claims, _ = get_v1_demo_fixtures()
    canary = settings.CANARY_TOKEN_SEED

    # Only an ADMIN / RESTRICTED clearance viewer sees the unredacted claim
    admin_claims = project_successor_claims(claims, AccessLabel.RESTRICTED)
    admin_text = " ".join(c.claim_text for c in admin_claims)
    assert detect_canary_leakage(admin_text)
