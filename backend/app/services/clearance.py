"""
Pre-Generation Access Clearance Filter & Canary Leakage Detection
Enforces strict security lattice boundaries and validates zero canary leakage.
"""

from typing import List, Sequence, Union
from backend.app.models.schemas import IngestedChunk, ClaimEntry, AccessLabel
from backend.app.config import settings


def filter_chunks_by_clearance(
    chunks: Sequence[IngestedChunk],
    viewer_clearance: AccessLabel,
) -> List[IngestedChunk]:
    """
    Enforces pre-generation clearance:
    Only chunks where viewer_clearance >= chunk.access_label enter the context.
    """
    return [chunk for chunk in chunks if viewer_clearance.can_access(chunk.access_label)]


def filter_claims_by_clearance(
    claims: Sequence[ClaimEntry],
    viewer_clearance: AccessLabel,
) -> List[ClaimEntry]:
    """
    Filters derived claims by effective label:
    A claim is only visible if the viewer clearance is >= claim.effective_label.
    If inaccessible, it can be replaced with a redacted placeholder if preserving structure.
    """
    return [claim for claim in claims if viewer_clearance.can_access(claim.effective_label)]


def project_successor_claims(
    claims: Sequence[ClaimEntry],
    viewer_clearance: AccessLabel,
) -> List[ClaimEntry]:
    """
    Projects claims for successor view:
    Permitted claims appear in full; inaccessible claims render as structural redacted placeholders.
    """
    projected: List[ClaimEntry] = []
    for claim in claims:
        if viewer_clearance.can_access(claim.effective_label):
            projected.append(claim)
        else:
            # Produce structural redacted placeholder
            redacted_claim = claim.model_copy(
                update={
                    "claim_text": f"[RESTRICTED CLAIM: Access Clearance '{claim.effective_label.value}' Required. Contact Lead.]",
                    "citations": [],
                }
            )
            projected.append(redacted_claim)
    return projected


def detect_canary_leakage(text_payload: str, canary_seed: str = settings.CANARY_TOKEN_SEED) -> bool:
    """
    Returns True if canary secret token is detected in the payload string.
    Zero leakage invariant requires this to ALWAYS return False for unprivileged sinks.
    """
    if not text_payload or not canary_seed:
        return False
    return canary_seed in text_payload
