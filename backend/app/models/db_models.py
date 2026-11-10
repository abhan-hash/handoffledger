"""
SQLAlchemy ORM Models for HandoffLedger
"""

import json
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Text,
    Float,
    Integer,
    Boolean,
    DateTime,
)
from backend.app.core.database import Base


class ChunkModel(Base):
    __tablename__ = "chunks"

    chunk_id = Column(String(64), primary_key=True, index=True)
    source_id = Column(String(128), nullable=False, index=True)
    source_type = Column(String(32), nullable=False)
    author = Column(String(64), nullable=False, index=True)
    timestamp = Column(String(64), nullable=False)
    access_label = Column(String(32), nullable=False, default="PUBLIC", index=True)
    content = Column(Text, nullable=False)
    char_start = Column(Integer, default=0)
    char_end = Column(Integer, default=0)
    has_canary = Column(Boolean, default=False)
    metadata_json = Column(Text, default="{}")


class ClaimModel(Base):
    __tablename__ = "claims"

    claim_id = Column(String(64), primary_key=True, index=True)
    entity_id = Column(String(128), nullable=False, index=True)
    attribute_key = Column(String(64), nullable=True, index=True)
    claim_text = Column(Text, nullable=False)
    state = Column(String(32), nullable=False, index=True)  # verified, inferred, conflicting, missing_evidence, superseded
    effective_label = Column(String(32), nullable=False, default="PUBLIC", index=True)
    citations_json = Column(Text, nullable=False, default="[]")  # Serialized list of {chunk_id, quote_span}
    created_at = Column(String(64), nullable=False)
    source_timestamp = Column(String(64), nullable=False)
    created_by = Column(String(64), default="system_extractor")
    reviewer_approved = Column(Boolean, default=False)
    reviewer_notes = Column(Text, nullable=True)
    confidence_score = Column(Float, default=1.0)
    version_history_json = Column(Text, default="[]")


class GraphNodeModel(Base):
    __tablename__ = "graph_nodes"

    node_id = Column(String(128), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    entity_type = Column(String(32), nullable=False)
    spok_score = Column(Float, default=0.0)
    concentration = Column(Float, default=0.0)
    stale_decay = Column(Float, default=0.0)
    evidence_weakness = Column(Float, default=0.0)
    in_degree = Column(Integer, default=0)
    interview_priority = Column(Float, default=0.0)
    is_filtered_from_heatmap = Column(Boolean, default=False)
    metadata_json = Column(Text, default="{}")


class InterviewAnswerModel(Base):
    __tablename__ = "interview_answers"

    question_id = Column(String(64), primary_key=True, index=True)
    target_node_id = Column(String(128), nullable=False, index=True)
    status = Column(String(32), default="unanswered")  # confirmed, edited, refuted
    response_text = Column(Text, nullable=True)
    created_at = Column(String(64), default=lambda: datetime.now(timezone.utc).isoformat())
