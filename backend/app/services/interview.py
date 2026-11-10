"""
HandoffLedger Adaptive Exit Interview Service
Manages Top-10 prioritized interview questions for departing members,
formulates recognition hypotheses, and updates claim ledger status upon answer ingestion.
"""

from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timezone
from backend.app.models.schemas import (
    InterviewQuestion,
    ClaimEntry,
    EvidenceState,
    AccessLabel,
    Citation,
)
from backend.app.services.graph_service import KnowledgeGraphEngine
from backend.app.config import settings
from backend.app.services.nemotron_client import generate_nemotron_hypothesis


def generate_interview_queue(
    graph_engine: KnowledgeGraphEngine,
    claims: List[ClaimEntry],
    limit: int = 10,
    answers_map: Optional[Dict[str, Dict[str, Any]]] = None,
) -> List[InterviewQuestion]:
    """
    Constructs the Top-10 exit interview queue targeting high-SPOK entities.
    Suppresses peripheral noise (in-degree < 2) per specification,
    and reflects recorded answer statuses.
    """
    top_nodes = graph_engine.get_top_interview_nodes(limit=limit, exclude_peripheral=True)
    questions: List[InterviewQuestion] = []

    for idx, node in enumerate(top_nodes, 1):
        node_claims = [c for c in claims if c.entity_id == node.node_id]
        candidate_text: str = ""
        citations = []

        # Attempt to synthesize targeted hypothesis via NVIDIA Nemotron Ultra 550B
        if settings.has_nvidia_key:
            nemotron_hyp = generate_nemotron_hypothesis(node.name, node.entity_type, node_claims)
            if nemotron_hyp:
                candidate_text = nemotron_hyp

        if not candidate_text:
            if node_claims:
                candidate_text = (
                    f"Records indicate '{node_claims[0].claim_text}' "
                    f"Is this rationale accurate and what hidden operational dependencies exist?"
                )
                citations = node_claims[0].citations
            else:
                candidate_text = (
                    f"Component '{node.name}' has no recorded rationale or decisions. "
                    f"What key architectural trade-offs govern its current behavior?"
                )
                citations = []
        elif node_claims:
            citations = node_claims[0].citations

        qid = f"q-{node.node_id}"
        ans = answers_map.get(qid, {}) if answers_map else {}

        questions.append(
            InterviewQuestion(
                question_id=qid,
                target_node_id=node.node_id,
                node_name=node.name,
                entity_type=node.entity_type,
                spok_score=node.spok_score,
                interview_priority=node.interview_priority,
                candidate_hypothesis=candidate_text,
                supporting_citations=citations,
                status=ans.get("status", "unanswered"),
                response_text=ans.get("response_text"),
            )
        )

    return questions


def process_interview_answer(
    question_id: str,
    action: str,
    response_text: Optional[str],
    claims: List[ClaimEntry],
    graph_engine: KnowledgeGraphEngine,
    leaver_name: Optional[str] = None,
) -> Tuple[List[ClaimEntry], Optional[ClaimEntry]]:
    """
    Applies departing member action (confirm, edit, refute) to claims and updates graph.
    """
    author = leaver_name or settings.DEFAULT_LEAVER_NAME
    target_node_id = question_id.replace("q-", "")
    updated_claims = list(claims)
    affected_claim: Optional[ClaimEntry] = None

    if action == "confirm":
        # Upgrade claims for this node to VERIFIED
        for idx, cl in enumerate(updated_claims):
            if cl.entity_id == target_node_id and cl.state != EvidenceState.SUPERSEDED:
                history = list(cl.version_history) + [{
                    "action": "confirmed_in_exit_interview",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "confirmed_by": author,
                }]
                updated = cl.model_copy(
                    update={
                        "state": EvidenceState.VERIFIED,
                        "version_history": history,
                        "reviewer_notes": f"Confirmed by {author} in exit interview.",
                    }
                )
                updated_claims[idx] = updated
                affected_claim = updated
                graph_engine.attach_claim(target_node_id, updated)

    elif action == "edit" and response_text:
        # Create a new verified claim directly authored by leaver
        now_iso = datetime.now(timezone.utc).isoformat()
        new_claim = ClaimEntry(
            claim_id=f"claim-interview-{len(updated_claims)+1}",
            entity_id=target_node_id,
            attribute_key="interview_clarification",
            claim_text=response_text,
            state=EvidenceState.VERIFIED,
            effective_label=AccessLabel.PUBLIC,
            source_timestamp=now_iso,
            created_by=author,
            reviewer_notes=f"Authored during exit interview by {author}",
            version_history=[{
                "action": "authored_in_exit_interview",
                "timestamp": now_iso,
                "author": author,
            }],
        )
        updated_claims.append(new_claim)
        affected_claim = new_claim
        graph_engine.attach_claim(target_node_id, new_claim)

    elif action == "refute":
        # Mark claims as conflicting or refute them
        for idx, cl in enumerate(updated_claims):
            if cl.entity_id == target_node_id and cl.state != EvidenceState.SUPERSEDED:
                updated = cl.model_copy(
                    update={
                        "state": EvidenceState.CONFLICTING,
                        "reviewer_notes": f"Refuted by {author} during exit interview: {response_text or 'Stated inaccurate'}",
                    }
                )
                updated_claims[idx] = updated
                affected_claim = updated

    return updated_claims, affected_claim
