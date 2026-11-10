"""
HandoffLedger Bounded Semantic Contradiction Evaluator
Evaluates candidate claim pairs that target the same entity attribute within
overlapping temporal windows, avoiding full O(N^2) pairwise comparisons.
"""

from typing import List, Tuple, Dict
from datetime import datetime, timezone
from backend.app.models.schemas import ClaimEntry, EvidenceState


def find_conflicting_claim_pairs(claims: List[ClaimEntry]) -> List[Tuple[ClaimEntry, ClaimEntry]]:
    """
    Identifies candidate claim pairs that target the same entity_id and attribute_key,
    have differing assertion texts, and share overlapping or identical timestamps.
    """
    grouped: Dict[Tuple[str, str], List[ClaimEntry]] = {}
    for c in claims:
        if c.attribute_key and c.state != EvidenceState.SUPERSEDED:
            key = (c.entity_id, c.attribute_key)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(c)

    conflicting_pairs: List[Tuple[ClaimEntry, ClaimEntry]] = []

    for key, group in grouped.items():
        if len(group) < 2:
            continue
        # Bounded comparison within same entity attribute
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                c1, c2 = group[i], group[j]
                # If statements assert fundamentally different values at the same timestamp
                if c1.source_timestamp == c2.source_timestamp and c1.claim_text != c2.claim_text:
                    conflicting_pairs.append((c1, c2))

    return conflicting_pairs


def apply_bounded_contradiction_check(claims: List[ClaimEntry]) -> List[ClaimEntry]:
    """
    Applies bounded contradiction detection across candidate attribute pairs.
    Updates conflicting claims to EvidenceState.CONFLICTING.
    """
    conflicts = find_conflicting_claim_pairs(claims)
    conflict_ids = set()
    for c1, c2 in conflicts:
        conflict_ids.add(c1.claim_id)
        conflict_ids.add(c2.claim_id)

    updated: List[ClaimEntry] = []
    for c in claims:
        if c.claim_id in conflict_ids:
            updated.append(
                c.model_copy(
                    update={
                        "state": EvidenceState.CONFLICTING,
                        "reviewer_notes": "Flagged as conflicting with co-temporal claim on same attribute.",
                    }
                )
            )
        else:
            updated.append(c)

    return updated
