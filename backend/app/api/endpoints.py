"""
FastAPI Route Controllers for HandoffLedger API
Implements the 10 core API contracts from the specification with full SQLAlchemy DB persistence,
deterministic verification, Top-10 exit interview management, and backward-compatible aliases.
"""

from typing import List, Optional, Dict, Any
import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Header, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from backend.app.core.database import get_db, SessionLocal
from backend.app.models.db_models import (
    ChunkModel,
    ClaimModel,
    GraphNodeModel,
    InterviewAnswerModel,
)
from backend.app.models.schemas import (
    AccessLabel,
    IngestedChunk,
    ClaimEntry,
    Citation,
    EvidenceState,
    EntityType,
    SourceType,
    GraphResponse,
    InterviewQuestion,
    IngestSummary,
    ExtractRequest,
    VerificationReport,
    InterviewAnswer,
    ReviewDecision,
    SuccessorRunwayView,
    EvalRequest,
    EvalResult,
)
from backend.app.services.synthetic_data import get_v1_demo_fixtures
from backend.app.services.chunker import (
    chunk_git_commit,
    chunk_chat_message,
    chunk_task_entry,
    chunk_markdown_document,
)
from backend.app.services.extractor import batch_extract_claims
from backend.app.services.verifier import verify_citation_spans, compute_effective_label
from backend.app.services.temporal import resolve_temporal_supersession
from backend.app.services.contradiction import apply_bounded_contradiction_check
from backend.app.services.clearance import (
    filter_chunks_by_clearance,
    filter_claims_by_clearance,
    detect_canary_leakage,
)
from backend.app.services.graph_service import KnowledgeGraphEngine
from backend.app.services.interview import (
    generate_interview_queue,
    process_interview_answer,
)
from backend.app.services.successor import build_successor_runway_view
from backend.app.services.evaluation import evaluate_handover_benchmark
from backend.app.config import settings

router = APIRouter(prefix="/api/v1")

# Global runtime cache synchronized with SQLite
_chunks_cache: List[IngestedChunk] = []
_claims_cache: List[ClaimEntry] = []
_graph_engine: Optional[KnowledgeGraphEngine] = None


def sync_db_from_fixtures(db: Session, chunks: List[IngestedChunk], claims: List[ClaimEntry]):
    """Populates SQLite database tables from active in-memory fixtures."""
    try:
        # Clear existing
        db.query(ClaimModel).delete()
        db.query(ChunkModel).delete()

        # Insert chunks
        for ch in chunks:
            db_chunk = ChunkModel(
                chunk_id=ch.chunk_id,
                source_id=ch.source_id,
                source_type=ch.source_type.value if hasattr(ch.source_type, "value") else str(ch.source_type),
                author=ch.author,
                timestamp=ch.timestamp,
                access_label=ch.access_label.value,
                content=ch.content,
                char_start=ch.char_start,
                char_end=ch.char_end,
                has_canary=ch.has_canary,
                metadata_json=json.dumps(ch.metadata),
            )
            db.add(db_chunk)

        # Insert claims
        for cl in claims:
            cit_dicts = [cit.model_dump() for cit in cl.citations]
            db_claim = ClaimModel(
                claim_id=cl.claim_id,
                entity_id=cl.entity_id,
                attribute_key=cl.attribute_key,
                claim_text=cl.claim_text,
                state=cl.state.value,
                effective_label=cl.effective_label.value,
                citations_json=json.dumps(cit_dicts),
                created_at=cl.created_at,
                source_timestamp=cl.source_timestamp,
                created_by=cl.created_by,
                reviewer_approved=cl.reviewer_approved,
                reviewer_notes=cl.reviewer_notes,
                confidence_score=cl.confidence_score,
                version_history_json=json.dumps(cl.version_history),
            )
            db.add(db_claim)

        db.commit()
    except Exception as e:
        db.rollback()


def get_cached_state():
    """Initializes and returns cached state, persisting to SQLite if empty."""
    global _chunks_cache, _claims_cache, _graph_engine
    if not _chunks_cache or not _claims_cache or _graph_engine is None:
        chunks, claims, engine = get_v1_demo_fixtures()
        _chunks_cache = chunks
        _claims_cache = claims
        _graph_engine = engine

        # Synchronize to DB
        try:
            with SessionLocal() as db:
                sync_db_from_fixtures(db, chunks, claims)
        except Exception:
            pass

    return _chunks_cache, _claims_cache, _graph_engine


# =========================================================================
# 1. Ingestion & Pre-Generation Clearance
# =========================================================================

@router.post("/ingest", response_model=IngestSummary)
async def ingest_files(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None),
    source_type: str = Form("markdown"),
    db: Session = Depends(get_db),
):
    """
    Uploads project archives (commits, discord chats, tasks, markdown),
    applies regex sanitization, generates chunks, and stores them in SQLite.
    """
    global _chunks_cache, _claims_cache, _graph_engine
    chunks, claims, engine = get_cached_state()
    new_chunks: List[IngestedChunk] = []

    if file:
        content_bytes = await file.read()
        content_str = content_bytes.decode("utf-8", errors="ignore")
        filename = file.filename or "upload.txt"
        if filename.endswith(".md"):
            new_chunks = chunk_markdown_document(content_str, source_id=filename)
        elif filename.endswith(".json"):
            try:
                data = json.loads(content_str)
                if isinstance(data, list):
                    for item in data:
                        if "commit_hash" in item:
                            new_chunks.append(chunk_git_commit(item, source_id=filename))
                        elif "channel" in item:
                            new_chunks.append(chunk_chat_message(item, source_id=filename))
                        elif "task_id" in item:
                            new_chunks.append(chunk_task_entry(item, source_id=filename))
            except Exception:
                pass
    elif raw_text:
        new_chunks = chunk_markdown_document(raw_text, source_id="raw_input.md")

    if new_chunks:
        _chunks_cache.extend(new_chunks)
        for ch in new_chunks:
            engine.attach_chunk("general_component", ch)
        sync_db_from_fixtures(db, _chunks_cache, _claims_cache)

    canary_count = sum(1 for ch in _chunks_cache if ch.has_canary)
    return IngestSummary(
        status="success",
        message=f"Ingested {len(new_chunks)} new chunks into database.",
        chunks_ingested=len(_chunks_cache),
        sources_parsed=list({ch.source_id for ch in _chunks_cache}),
        canary_tokens_indexed=canary_count,
    )


@router.post("/ingest/synthetic")
def load_synthetic_demo(db: Session = Depends(get_db)):
    """Initializes or resets the v1_demo synthetic dataset."""
    global _chunks_cache, _claims_cache, _graph_engine
    chunks, claims, engine = get_v1_demo_fixtures()
    _chunks_cache = chunks
    _claims_cache = claims
    _graph_engine = engine

    sync_db_from_fixtures(db, chunks, claims)

    return {
        "status": "success",
        "message": "Loaded v1_demo dataset with synthetic git commits, chat logs, and canary tokens.",
        "chunks_count": len(chunks),
        "claims_count": len(claims),
    }


@router.get("/chunks", response_model=List[IngestedChunk])
def get_chunks(x_clearance: str = Header("PUBLIC")):
    """Returns ingested chunks filtered by pre-generation clearance."""
    try:
        clearance = AccessLabel(x_clearance.upper())
    except ValueError:
        clearance = AccessLabel.PUBLIC

    chunks, _, _ = get_cached_state()
    return filter_chunks_by_clearance(chunks, clearance)


# =========================================================================
# 2. Extraction & Hybrid Verification
# =========================================================================

@router.post("/extract", response_model=List[ClaimEntry])
def extract_claims(req: Optional[ExtractRequest] = None, db: Session = Depends(get_db)):
    """
    Extracts atomic claims from ingested chunks using schema extraction,
    filtered by clearance.
    """
    global _claims_cache, _graph_engine
    chunks, claims, engine = get_cached_state()
    clearance = req.clearance if req else AccessLabel.PUBLIC
    visible_chunks = filter_chunks_by_clearance(chunks, clearance)

    extracted = batch_extract_claims(visible_chunks)
    if extracted:
        _claims_cache = extracted
        for cl in extracted:
            engine.attach_claim(cl.entity_id, cl)
        sync_db_from_fixtures(db, chunks, _claims_cache)

    return _claims_cache


@router.get("/claims", response_model=List[ClaimEntry])
def get_claims(x_clearance: str = Header("PUBLIC")):
    """Returns claims filtered by effective access label."""
    try:
        clearance = AccessLabel(x_clearance.upper())
    except ValueError:
        clearance = AccessLabel.PUBLIC

    _, claims, _ = get_cached_state()
    return filter_claims_by_clearance(claims, clearance)


@router.post("/verify", response_model=VerificationReport)
def run_verification(db: Session = Depends(get_db)):
    """
    Runs deterministic citation verification, temporal supersession,
    and bounded semantic contradiction checks.
    """
    global _claims_cache
    chunks, claims, engine = get_cached_state()
    chunks_dict = {c.chunk_id: c for c in chunks}

    # 1. Deterministic substring check & label inheritance
    verified_claims: List[ClaimEntry] = []
    for cl in claims:
        is_valid, msg = verify_citation_spans(cl, chunks_dict)
        effective_lbl = compute_effective_label(cl, chunks_dict)
        if not is_valid:
            updated = cl.model_copy(
                update={
                    "state": EvidenceState.MISSING_EVIDENCE,
                    "reviewer_notes": f"Verification failed: {msg}",
                    "effective_label": effective_lbl,
                }
            )
        else:
            updated = cl.model_copy(update={"effective_label": effective_lbl})
        verified_claims.append(updated)

    # 2. Temporal supersession resolution
    temporal_resolved = resolve_temporal_supersession(verified_claims)

    # 3. Bounded semantic contradiction check
    fully_verified = apply_bounded_contradiction_check(temporal_resolved)
    _claims_cache = fully_verified

    # Update graph engine
    for cl in fully_verified:
        engine.attach_claim(cl.entity_id, cl)

    # Persist verified claims to SQLite
    sync_db_from_fixtures(db, chunks, _claims_cache)

    summary = {
        "total": len(fully_verified),
        "verified": sum(1 for c in fully_verified if c.state == EvidenceState.VERIFIED),
        "inferred": sum(1 for c in fully_verified if c.state == EvidenceState.INFERRED),
        "conflicting": sum(1 for c in fully_verified if c.state == EvidenceState.CONFLICTING),
        "missing_evidence": sum(1 for c in fully_verified if c.state == EvidenceState.MISSING_EVIDENCE),
        "superseded": sum(1 for c in fully_verified if c.state == EvidenceState.SUPERSEDED),
    }

    return VerificationReport(status="success", summary=summary, claims=fully_verified)


# =========================================================================
# 3. Graph Risk & Exit Interview
# =========================================================================

@router.get("/graph/spok", response_model=GraphResponse)
def get_graph():
    """Returns the knowledge-risk graph with SPOK scores and centrality flags."""
    _, _, engine = get_cached_state()
    return engine.export_graph_response()


@router.get("/interview/queue", response_model=List[InterviewQuestion])
def get_interview_queue(limit: int = 10):
    """
    Returns the Top-10 prioritized exit interview questions for the departing member.
    Suppresses peripheral low-centrality nodes (in-degree < 2).
    """
    _, claims, engine = get_cached_state()
    return generate_interview_queue(engine, claims, limit=limit)


@router.post("/interview/answer", response_model=ClaimEntry)
def submit_interview_answer(
    payload: InterviewAnswer,
    db: Session = Depends(get_db),
):
    """Ingests departing member answer and immediately updates downstream claims and SPOK scores."""
    global _claims_cache
    chunks, claims, engine = get_cached_state()

    updated_claims, affected_claim = process_interview_answer(
        question_id=payload.question_id,
        action=payload.action,
        response_text=payload.response_text,
        claims=_claims_cache,
        graph_engine=engine,
        leaver_name=settings.DEFAULT_LEAVER_NAME,
    )
    _claims_cache = updated_claims
    sync_db_from_fixtures(db, chunks, _claims_cache)

    # Log in SQLite interview_answers table
    try:
        answer_rec = InterviewAnswerModel(
            question_id=payload.question_id,
            target_node_id=payload.question_id.replace("q-", ""),
            status=payload.action,
            response_text=payload.response_text,
        )
        db.add(answer_rec)
        db.commit()
    except Exception:
        db.rollback()

    if affected_claim:
        return affected_claim
    return _claims_cache[0]


@router.post("/interview/respond")
def submit_interview_response_legacy(
    question_id: str,
    action: str,  # confirm, edit, refute
    response_text: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Backward-compatible alias for frontend calling query parameters."""
    payload = InterviewAnswer(
        question_id=question_id,
        action=action,
        response_text=response_text,
    )
    res = submit_interview_answer(payload, db=db)
    return {"status": "success", "action": action, "target_node_id": question_id.replace("q-", "")}


# =========================================================================
# 4. Reviewer Staging & Triage
# =========================================================================

@router.get("/review/claims", response_model=List[ClaimEntry])
def get_review_claims(
    status_filter: Optional[str] = "all",
    x_clearance: str = Header("LEAD_ONLY"),
):
    """Returns staging claims grouped for reviewer triage."""
    try:
        clearance = AccessLabel(x_clearance.upper())
    except ValueError:
        clearance = AccessLabel.LEAD_ONLY

    _, claims, _ = get_cached_state()
    visible = filter_claims_by_clearance(claims, clearance)

    if status_filter and status_filter != "all":
        visible = [c for c in visible if c.state.value == status_filter]
    return visible


@router.post("/review/decide", response_model=ClaimEntry)
def review_decision(
    decision: ReviewDecision,
    db: Session = Depends(get_db),
):
    """Approves, edits, or rejects a claim in the review staging dashboard."""
    global _claims_cache
    chunks, claims, engine = get_cached_state()

    for idx, c in enumerate(_claims_cache):
        if c.claim_id == decision.claim_id:
            now_iso = datetime.now(timezone.utc).isoformat()
            history = list(c.version_history) + [{
                "action": f"reviewer_{decision.action}",
                "timestamp": now_iso,
                "notes": decision.reviewer_notes,
            }]

            if decision.action == "approve":
                updated = c.model_copy(
                    update={
                        "reviewer_approved": True,
                        "reviewer_notes": decision.reviewer_notes or "Approved by reviewer",
                        "version_history": history,
                    }
                )
            elif decision.action == "reject":
                updated = c.model_copy(
                    update={
                        "state": EvidenceState.MISSING_EVIDENCE,
                        "reviewer_approved": False,
                        "reviewer_notes": decision.reviewer_notes or "Rejected by reviewer",
                        "version_history": history,
                    }
                )
            elif decision.action == "edit" and decision.updated_claim_text:
                updated = c.model_copy(
                    update={
                        "claim_text": decision.updated_claim_text,
                        "reviewer_approved": True,
                        "reviewer_notes": decision.reviewer_notes or "Edited and approved by reviewer",
                        "version_history": history,
                    }
                )
            else:
                updated = c

            _claims_cache[idx] = updated
            sync_db_from_fixtures(db, chunks, _claims_cache)
            return updated

    raise HTTPException(status_code=404, detail=f"Claim '{decision.claim_id}' not found")


# =========================================================================
# 5. Successor Runway View & Canary Safety
# =========================================================================

@router.get("/handover/view", response_model=SuccessorRunwayView)
def get_handover_view(x_clearance: str = Header("INTERNAL")):
    """
    Returns the role-appropriate 4-pane successor runway dashboard:
    1. Active Landmines & Workarounds
    2. Account & Key Ownership
    3. Decision Rationale
    4. Next Actions Backlog
    Inaccessible items render as structural redacted placeholders.
    """
    try:
        clearance = AccessLabel(x_clearance.upper())
    except ValueError:
        clearance = AccessLabel.INTERNAL

    _, claims, _ = get_cached_state()
    return build_successor_runway_view(claims, clearance)


@router.get("/successor/view")
def get_successor_view_legacy(x_clearance: str = Header("INTERNAL")):
    """Backward-compatible alias for frontend calling /api/v1/successor/view."""
    return get_handover_view(x_clearance=x_clearance)


# =========================================================================
# 6. Evaluation Benchmark Harness
# =========================================================================

@router.post("/evaluate", response_model=EvalResult)
def evaluate_pipeline(req: Optional[EvalRequest] = None):
    """
    Executes the 20 gold-standard question benchmark against dataset v1_demo.
    Measures accuracy delta and asserts zero canary token disclosures.
    """
    _, claims, _ = get_cached_state()
    clearance = req.viewer_clearance if req else AccessLabel.INTERNAL
    return evaluate_handover_benchmark(claims, clearance)


@router.get("/evaluation/delta")
def get_evaluation_delta_legacy():
    """Backward-compatible GET endpoint for frontend benchmark metrics."""
    res = evaluate_pipeline()
    return res.model_dump()
