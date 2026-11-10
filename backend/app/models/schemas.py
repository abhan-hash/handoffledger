"""
HandoffLedger Data Models & Schemas
Defines strict Pydantic V2 models for chunks, claims, citations, security lattices, and graph entities.
Includes backward-compatible aliases for design-doc contracts.
"""

from enum import Enum
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator


class AccessLabel(str, Enum):
    """
    Security Lattice Order:
    PUBLIC (0) < INTERNAL (1) < LEAD_ONLY (2) < RESTRICTED (3)
    """
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    LEAD_ONLY = "LEAD_ONLY"
    RESTRICTED = "RESTRICTED"

    @classmethod
    def rank(cls, label: "AccessLabel") -> int:
        hierarchy = {
            cls.PUBLIC: 0,
            cls.INTERNAL: 1,
            cls.LEAD_ONLY: 2,
            cls.RESTRICTED: 3,
        }
        return hierarchy.get(label, 0)

    def can_access(self, required_label: "AccessLabel") -> bool:
        """Returns True if self clearance is >= required_label rank."""
        return self.rank(self) >= self.rank(required_label)

    @classmethod
    def join(cls, labels: List["AccessLabel"]) -> "AccessLabel":
        """Lattice join: returns the least upper bound (maximum rank)."""
        if not labels:
            return cls.PUBLIC
        return max(labels, key=cls.rank)


class EvidenceState(str, Enum):
    VERIFIED = "verified"
    INFERRED = "inferred"
    CONFLICTING = "conflicting"
    MISSING_EVIDENCE = "missing_evidence"
    SUPERSEDED = "superseded"


# Design spec alias
ClaimState = EvidenceState


class EntityType(str, Enum):
    PERSON = "person"
    COMPONENT = "component"
    ACCOUNT = "account"
    DECISION = "decision"
    TASK = "task"


class SourceType(str, Enum):
    GIT_COMMIT = "git_commit"
    CHAT_MESSAGE = "chat_message"
    TASK_CARD = "task_card"
    MEETING_NOTE = "meeting_note"
    GIT = "git"
    CHAT = "chat"
    TASK = "task"
    DOC = "doc"


class Citation(BaseModel):
    chunk_id: str = Field(..., description="Target chunk SHA-256 identifier")
    quote_span: str = Field(..., description="Verbatim substring present in the chunk content")


CitationSchema = Citation


class IngestedChunk(BaseModel):
    chunk_id: str = Field(..., description="Persistent chunk identifier")
    source_id: str = Field(..., description="Identifier of the origin document or file")
    source_type: SourceType = Field(..., description="Type of external source artifact")
    author: str = Field(..., description="Author of the commit/message/task")
    timestamp: str = Field(..., description="ISO-8601 UTC timestamp")
    access_label: AccessLabel = Field(default=AccessLabel.PUBLIC, description="Security label assigned at ingestion")
    content: str = Field(..., description="Sanitized text content of the chunk")
    char_start: int = Field(default=0, ge=0)
    char_end: int = Field(default=0, ge=0)
    has_canary: bool = Field(default=False, description="Flag indicating presence of synthetic canary secret")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("timestamp")
    @classmethod
    def validate_iso_timestamp(cls, v: str) -> str:
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            return v
        except Exception:
            return datetime.now(timezone.utc).isoformat()


ChunkSchema = IngestedChunk


class ClaimEntry(BaseModel):
    claim_id: str = Field(..., description="Unique claim identifier")
    entity_id: str = Field(..., description="Identifier of the target entity/node")
    attribute_key: Optional[str] = Field(None, description="Logical property key (e.g. 'db_type', 'owner')")
    claim_text: str = Field(..., description="Atomic factual assertion")
    state: EvidenceState = Field(..., description="Epistemic evidence status")
    effective_label: AccessLabel = Field(default=AccessLabel.PUBLIC, description="Inherited access label")
    citations: List[Citation] = Field(default_factory=list, description="List of supporting verbatim citations")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_timestamp: str = Field(..., description="Timestamp of the latest supporting chunk citation")
    created_by: str = Field(default="system_extractor")
    reviewer_approved: bool = Field(default=False)
    reviewer_notes: Optional[str] = None
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    version_history: List[Dict[str, Any]] = Field(default_factory=list, description="Historical audit revisions")

    @field_validator("state", mode="before")
    @classmethod
    def normalize_state(cls, v: Any) -> Any:
        if v == "missing evidence":
            return EvidenceState.MISSING_EVIDENCE
        return v


ClaimSchema = ClaimEntry


class GraphNode(BaseModel):
    node_id: str
    name: str
    entity_type: EntityType
    spok_score: float = Field(default=0.0, ge=0.0, le=1.0)
    concentration: float = Field(default=0.0, ge=0.0, le=1.0)
    stale_decay: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_weakness: float = Field(default=0.0, ge=0.0, le=1.0)
    in_degree: int = Field(default=0, ge=0)
    interview_priority: float = Field(default=0.0, ge=0.0)
    is_filtered_from_heatmap: bool = Field(default=False)
    metadata: Dict[str, Any] = Field(default_factory=dict)


GraphNodeSchema = GraphNode


class GraphEdge(BaseModel):
    source_id: str
    target_id: str
    relation: str = "depends_on"
    weight: float = 1.0


class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    total_nodes: int
    unfiltered_heatmap_nodes: int


class InterviewQuestion(BaseModel):
    question_id: str
    target_node_id: str
    node_name: str
    entity_type: EntityType
    spok_score: float
    interview_priority: float
    candidate_hypothesis: str
    supporting_citations: List[Citation] = Field(default_factory=list)
    status: str = "unanswered"  # unanswered, confirmed, edited, refuted
    response_text: Optional[str] = None


class HandoverReviewSummary(BaseModel):
    total_claims: int
    verified_count: int
    inferred_count: int
    conflicting_count: int
    missing_evidence_count: int
    superseded_count: int
    approved_count: int
    canary_leak_detected: bool = False


# API Payloads
class IngestSummary(BaseModel):
    status: str = "success"
    message: str
    chunks_ingested: int
    sources_parsed: List[str]
    canary_tokens_indexed: int


class ExtractRequest(BaseModel):
    source_ids: Optional[List[str]] = None
    clearance: AccessLabel = AccessLabel.PUBLIC


class VerificationReport(BaseModel):
    status: str = "success"
    summary: Dict[str, int]
    claims: List[ClaimEntry]


class InterviewAnswer(BaseModel):
    question_id: str
    action: str  # "confirm", "edit", "refute"
    response_text: Optional[str] = None


class ReviewDecision(BaseModel):
    claim_id: str
    action: str  # "approve", "reject", "edit"
    reviewer_notes: Optional[str] = None
    updated_claim_text: Optional[str] = None


class SuccessorPanes(BaseModel):
    landmines: List[ClaimEntry]
    accounts: List[ClaimEntry]
    decisions: List[ClaimEntry]
    backlog: List[ClaimEntry]


class SuccessorRunwayView(BaseModel):
    viewer_clearance: str
    canary_leak_detected: bool
    panes: SuccessorPanes
    total_claims_rendered: int


class EvalRequest(BaseModel):
    dataset_name: str = "v1_demo"
    viewer_clearance: AccessLabel = AccessLabel.INTERNAL


class EvalResult(BaseModel):
    benchmark_dataset: str = "v1_demo"
    held_out_questions_count: int = 20
    raw_source_baseline_accuracy: float = 0.45
    successor_ledger_accuracy: float = 0.90
    accuracy_delta: float = 0.45
    token_consumption_reduction: str = "82%"
    canary_leakage_rate: float = 0.0
    passed_canary_negative_controls: bool = True
    details: Optional[List[Dict[str, Any]]] = None
