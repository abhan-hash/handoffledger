"""
HandoffLedger Temporal Progression Resolver
Groups claims by (entity_id, attribute_key) and orders them chronologically.
If a newer claim supersedes an older claim, updates the older state to SUPERSEDED.
"""

from typing import List, Dict, Tuple
from datetime import datetime
from backend.app.models.schemas import ClaimEntry, EvidenceState


def resolve_temporal_supersession(claims: List[ClaimEntry]) -> List[ClaimEntry]:
    """
    Groups claims by (entity_id, attribute_key).
    For any attribute with multiple claims, sorts by source_timestamp ascending.
    The latest claim retains its evidence status; previous valid claims are updated to SUPERSEDED.
    """
    grouped: Dict[Tuple[str, str], List[ClaimEntry]] = {}
    ungrouped: List[ClaimEntry] = []

    for c in claims:
        if c.attribute_key:
            key = (c.entity_id, c.attribute_key)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(c)
        else:
            ungrouped.append(c)

    resolved: List[ClaimEntry] = list(ungrouped)

    for (entity_id, attr_key), attr_claims in grouped.items():
        if len(attr_claims) <= 1:
            resolved.extend(attr_claims)
            continue

        # Sort chronologically by source_timestamp
        def parse_ts(c: ClaimEntry):
            try:
                return datetime.fromisoformat(c.source_timestamp.replace("Z", "+00:00"))
            except Exception:
                return datetime.min

        sorted_claims = sorted(attr_claims, key=parse_ts)

        # The newest claim stays active
        newest = sorted_claims[-1]

        # Prior claims that are verified or inferred become superseded
        for old_claim in sorted_claims[:-1]:
            if old_claim.state in (EvidenceState.VERIFIED, EvidenceState.INFERRED):
                history_entry = {
                    "transition": "superseded_by_newer_claim",
                    "superseded_by_id": newest.claim_id,
                    "superseded_by_timestamp": newest.source_timestamp,
                    "previous_state": old_claim.state.value,
                }
                new_history = list(old_claim.version_history) + [history_entry]
                updated_claim = old_claim.model_copy(
                    update={
                        "state": EvidenceState.SUPERSEDED,
                        "version_history": new_history,
                        "reviewer_notes": f"Superseded by {newest.claim_id} ({newest.claim_text})",
                    }
                )
                resolved.append(updated_claim)
            else:
                resolved.append(old_claim)

        resolved.append(newest)

    return resolved
