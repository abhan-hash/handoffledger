"""
HandoffLedger Deterministic SPOK Risk Calculator
Implements Single-Point-of-Knowledge (SPOK) calculation, staleness decay, evidence penalty weighting,
centrality filtering, and interview priority ranking.
"""

import math
from datetime import datetime, timezone
from typing import List, Dict, Optional, Sequence, Any
from backend.app.models.schemas import (
    IngestedChunk,
    ClaimEntry,
    GraphNode,
    EvidenceState,
    SourceType,
    EntityType,
)


# Authority weights by source artifact type
SOURCE_AUTHORITY_WEIGHTS: Dict[Any, float] = {
    SourceType.GIT_COMMIT: 1.0,
    SourceType.GIT: 1.0,
    "pull_request": 0.9,
    SourceType.TASK_CARD: 0.7,
    SourceType.TASK: 0.7,
    SourceType.MEETING_NOTE: 0.6,
    SourceType.DOC: 0.6,
    SourceType.CHAT_MESSAGE: 0.5,
    SourceType.CHAT: 0.5,
}

# Evidence state penalties for weakness computation
EVIDENCE_PENALTIES: Dict[EvidenceState, float] = {
    EvidenceState.VERIFIED: 0.0,
    EvidenceState.INFERRED: 0.4,
    EvidenceState.CONFLICTING: 0.8,
    EvidenceState.MISSING_EVIDENCE: 1.0,
    EvidenceState.SUPERSEDED: 0.2,
}

DEFAULT_HALF_LIFE_DAYS: float = 60.0


def calculate_concentration(
    chunks: Sequence[IngestedChunk],
    leaver_name: str,
) -> float:
    """
    Computes author concentration ratio for the departing member:
    C_n = sum(I(author == leaver) * w(type)) / sum(w(type))
    """
    if not chunks or not leaver_name:
        return 0.0

    total_weight = 0.0
    leaver_weight = 0.0
    leaver_clean = leaver_name.strip().lower()

    for chunk in chunks:
        w = SOURCE_AUTHORITY_WEIGHTS.get(chunk.source_type, 0.5)
        total_weight += w
        chunk_author = (chunk.author or "").strip().lower()
        if chunk_author == leaver_clean or leaver_clean in chunk_author:
            leaver_weight += w

    if total_weight <= 0.0:
        return 0.0

    score = leaver_weight / total_weight
    return min(1.0, max(0.0, score))


def calculate_stale_decay(
    last_updated_iso: Optional[str],
    reference_time: Optional[datetime] = None,
    half_life_days: float = DEFAULT_HALF_LIFE_DAYS,
) -> float:
    """
    Computes staleness decay using exponential half-life:
    D_n = 1.0 - exp(-ln(2) / t_1/2 * delta_t)
    """
    if not last_updated_iso:
        return 1.0  # Max staleness if unknown

    if reference_time is None:
        reference_time = datetime.now(timezone.utc)
    elif reference_time.tzinfo is None:
        reference_time = reference_time.replace(tzinfo=timezone.utc)

    try:
        updated_dt = datetime.fromisoformat(last_updated_iso.replace("Z", "+00:00"))
        if updated_dt.tzinfo is None:
            updated_dt = updated_dt.replace(tzinfo=timezone.utc)
        delta_days = (reference_time - updated_dt).total_seconds() / 86400.0
    except Exception:
        return 1.0

    if delta_days <= 0.0:
        return 0.0

    decay_factor = math.log(2.0) / half_life_days
    decay_score = 1.0 - math.exp(-decay_factor * delta_days)
    return min(1.0, max(0.0, decay_score))


def calculate_evidence_weakness(claims: Sequence[ClaimEntry]) -> float:
    """
    Computes average penalty across all linked claims:
    W_n = 1/|C_n| * sum(Penalty(state))
    """
    if not claims:
        return 1.0  # Maximum weakness penalty if no claims exist

    penalties = [EVIDENCE_PENALTIES.get(c.state, 1.0) for c in claims]
    avg_penalty = sum(penalties) / len(penalties)
    return min(1.0, max(0.0, avg_penalty))


def calculate_spok_score(
    concentration: float,
    stale_decay: float,
    evidence_weakness: float,
) -> float:
    """
    Exact SPOK mathematical formula:
    SPOK(n) = 0.5 * Concentration + 0.25 * StaleDecay + 0.25 * EvidenceWeakness
    """
    c = min(1.0, max(0.0, concentration))
    d = min(1.0, max(0.0, stale_decay))
    w = min(1.0, max(0.0, evidence_weakness))
    score = 0.5 * c + 0.25 * d + 0.25 * w
    return round(min(1.0, max(0.0, score)), 4)


def calculate_interview_priority(
    spok_score: float,
    in_degree: int,
) -> float:
    """
    Priority(n) = SPOK(n) * (1.0 + ln(1 + in_degree))
    """
    deg = max(0, in_degree)
    multiplier = 1.0 + math.log(1.0 + deg)
    priority = spok_score * multiplier
    return round(max(0.0, priority), 4)


def evaluate_node_spok(
    node_id: str,
    name: str,
    entity_type: EntityType,
    chunks: Sequence[IngestedChunk],
    claims: Sequence[ClaimEntry],
    leaver_name: str,
    in_degree: int = 0,
    reference_time: Optional[datetime] = None,
    half_life_days: float = DEFAULT_HALF_LIFE_DAYS,
    min_heatmap_in_degree: int = 2,
) -> GraphNode:
    """
    Evaluates all SPOK metrics for a single node entity and constructs a GraphNode model.
    """
    # 1. Compute concentration
    concentration = calculate_concentration(chunks, leaver_name)

    # 2. Find latest activity timestamp across chunks and claims
    timestamps: List[str] = []
    for ch in chunks:
        if ch.timestamp:
            timestamps.append(ch.timestamp)
    for cl in claims:
        if cl.source_timestamp:
            timestamps.append(cl.source_timestamp)
        elif cl.created_at:
            timestamps.append(cl.created_at)

    latest_ts: Optional[str] = max(timestamps) if timestamps else None
    stale_decay = calculate_stale_decay(latest_ts, reference_time, half_life_days)

    # 3. Compute evidence weakness
    evidence_weakness = calculate_evidence_weakness(claims)

    # 4. SPOK score
    spok = calculate_spok_score(concentration, stale_decay, evidence_weakness)

    # 5. Interview priority
    priority = calculate_interview_priority(spok, in_degree)

    # 6. Centrality filter: low in-degree and low chunk count flagged as peripheral noise
    is_filtered = (in_degree < min_heatmap_in_degree) and (len(chunks) <= 1)

    return GraphNode(
        node_id=node_id,
        name=name,
        entity_type=entity_type,
        spok_score=spok,
        concentration=round(concentration, 4),
        stale_decay=round(stale_decay, 4),
        evidence_weakness=round(evidence_weakness, 4),
        in_degree=in_degree,
        interview_priority=priority,
        is_filtered_from_heatmap=is_filtered,
        metadata={
            "chunk_count": len(chunks),
            "claim_count": len(claims),
            "latest_timestamp": latest_ts,
        },
    )
