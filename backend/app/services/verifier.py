"""
HandoffLedger Deterministic Citation Verifier & Temporal Resolver
Verifies exact substring fidelity in Python, computes lattice label inheritance,
and resolves chronological state progressions.
"""

from typing import List, Dict, Tuple
from datetime import datetime, timezone
from backend.app.models.schemas import (
    ClaimEntry,
    IngestedChunk,
    EvidenceState,
    AccessLabel,
)


def verify_citation_spans(
    claim: ClaimEntry,
    chunks_dict: Dict[str, IngestedChunk],
) -> Tuple[bool, str]:
    """
    Asserts that every citation cited by the claim exists and that
    the quote_span is a verbatim substring of chunk.content.
    """
    if not claim.citations:
        return False, "Missing citations"

    for cit in claim.citations:
        chunk = chunks_dict.get(cit.chunk_id)
        if not chunk:
            return False, f"Cited chunk '{cit.chunk_id}' not found in database"
        if not cit.quote_span:
            return False, "Empty quote span"
        if cit.quote_span not in chunk.content:
            return False, f"Quote span '{cit.quote_span[:30]}...' not found in chunk content"

    return True, "All citations verified"


def compute_effective_label(
    claim: ClaimEntry,
    chunks_dict: Dict[str, IngestedChunk],
) -> AccessLabel:
    """
    Calculates the lattice join (max rank) of all cited chunks:
    L(claim) = join(L(chunk_1), ..., L(chunk_n))
    """
    cited_labels: List[AccessLabel] = []
    for cit in claim.citations:
        chunk = chunks_dict.get(cit.chunk_id)
        if chunk:
            cited_labels.append(chunk.access_label)

    return AccessLabel.join(cited_labels)


def parse_timestamp_safe(ts: str) -> datetime:
    """Safely converts ISO-8601 string to aware datetime."""
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return datetime.min.replace(tzinfo=timezone.utc)


def resolve_temporal_supersession(claims: List[ClaimEntry]) -> List[ClaimEntry]:
    """
    Resolves historical state updates:
    Claims sharing (entity_id, attribute_key) are ordered by source_timestamp.
    Older claims (t_old < t_new) are updated to EvidenceState.SUPERSEDED
    rather than causing false-positive conflict flags.
    """
    grouped: Dict[Tuple[str, str], List[ClaimEntry]] = {}

    for claim in claims:
        if claim.attribute_key:
            key = (claim.entity_id, claim.attribute_key)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(claim)

    updated_claims = list(claims)

    for (entity_id, attr_key), group in grouped.items():
        if len(group) <= 1:
            continue

        # Sort ascending by source timestamp (oldest first)
        group_sorted = sorted(group, key=lambda c: parse_timestamp_safe(c.source_timestamp))

        # The newest claim is authoritative
        latest_claim = group_sorted[-1]

        # Older claims are marked superseded
        for older in group_sorted[:-1]:
            if older.claim_id != latest_claim.claim_id and older.state != EvidenceState.SUPERSEDED:
                # Find index in updated_claims
                for idx, c in enumerate(updated_claims):
                    if c.claim_id == older.claim_id:
                        updated_claims[idx] = older.model_copy(
                            update={
                                "state": EvidenceState.SUPERSEDED,
                                "reviewer_notes": f"Superseded by newer claim {latest_claim.claim_id}",
                            }
                        )

    return updated_claims


def run_verification_pipeline(
    claims: List[ClaimEntry],
    chunks_dict: Dict[str, IngestedChunk],
) -> List[ClaimEntry]:
    """
    Executes the full deterministic verification pipeline:
    1. Substring fidelity check (demotes to missing_evidence on failure)
    2. Access label lattice join
    3. Temporal progression supersession
    """
    verified_pass: List[ClaimEntry] = []

    for claim in claims:
        is_valid, reason = verify_citation_spans(claim, chunks_dict)
        effective_lbl = compute_effective_label(claim, chunks_dict)

        new_state = claim.state
        notes = claim.reviewer_notes

        if not is_valid and claim.state != EvidenceState.SUPERSEDED:
            new_state = EvidenceState.MISSING_EVIDENCE
            notes = f"Verification failure: {reason}"
        elif is_valid and claim.state == EvidenceState.INFERRED:
            # Upgrade to verified if multiple independent citations or commit citations exist
            has_commit = any(
                chunks_dict.get(c.chunk_id) and chunks_dict[c.chunk_id].source_type.value == "git_commit"
                for c in claim.citations
            )
            if has_commit or len(claim.citations) >= 2:
                new_state = EvidenceState.VERIFIED

        updated_claim = claim.model_copy(
            update={
                "state": new_state,
                "effective_label": effective_lbl,
                "reviewer_notes": notes,
            }
        )
        verified_pass.append(updated_claim)

    # 4. Resolve temporal progressions
    return resolve_temporal_supersession(verified_pass)
