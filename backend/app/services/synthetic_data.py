"""
Synthetic Dataset Generator (v1_demo)
Generates structured test datasets mimicking a student technical club repository
with planted canary tokens, unrecorded decision gaps, and temporal updates.
"""

from typing import List, Tuple
from datetime import datetime, timezone, timedelta
from backend.app.models.schemas import (
    IngestedChunk,
    ClaimEntry,
    Citation,
    EvidenceState,
    SourceType,
    AccessLabel,
    EntityType,
)
from backend.app.config import settings
from backend.app.services.graph_service import KnowledgeGraphEngine


def get_v1_demo_fixtures(
    ref_time: datetime = datetime(2026, 11, 10, 12, 0, 0, tzinfo=timezone.utc),
) -> Tuple[List[IngestedChunk], List[ClaimEntry], KnowledgeGraphEngine]:
    """Generates the static v1_demo benchmark data."""
    leaver = settings.DEFAULT_LEAVER_NAME
    canary = settings.CANARY_TOKEN_SEED

    # Timestamps
    ts_now = ref_time.isoformat()
    ts_10d_ago = (ref_time - timedelta(days=10)).isoformat()
    ts_30d_ago = (ref_time - timedelta(days=30)).isoformat()
    ts_80d_ago = (ref_time - timedelta(days=80)).isoformat()
    ts_120d_ago = (ref_time - timedelta(days=120)).isoformat()

    chunks: List[IngestedChunk] = [
        # Chunk 1: Git commit on Postgres migration by Alice
        IngestedChunk(
            chunk_id="chunk-git-001",
            source_id="git_log.json",
            source_type=SourceType.GIT_COMMIT,
            author=leaver,
            timestamp=ts_30d_ago,
            access_label=AccessLabel.PUBLIC,
            content="feat(db): migrated database engine from sqlite to postgresql on port 5432 to handle concurrency.",
        ),
        # Chunk 2: Older Git commit by Bob selecting SQLite
        IngestedChunk(
            chunk_id="chunk-git-002",
            source_id="git_log.json",
            source_type=SourceType.GIT_COMMIT,
            author="Bob Developer",
            timestamp=ts_120d_ago,
            access_label=AccessLabel.PUBLIC,
            content="chore: initialized sqlite3 database backend for local club demo.",
        ),
        # Chunk 3: Discord chat regarding auth workaround by Alice
        IngestedChunk(
            chunk_id="chunk-chat-003",
            source_id="discord_export.json",
            source_type=SourceType.CHAT_MESSAGE,
            author=leaver,
            timestamp=ts_10d_ago,
            access_label=AccessLabel.INTERNAL,
            content="Heads up team: for the token refresh bug, we use an in-memory fallback cache when Redis is warming up.",
        ),
        # Chunk 4: Task card untouched for 80 days
        IngestedChunk(
            chunk_id="chunk-task-004",
            source_id="tasks_export.json",
            source_type=SourceType.TASK_CARD,
            author=leaver,
            timestamp=ts_80d_ago,
            access_label=AccessLabel.INTERNAL,
            content="Task-402: Setup automated backup cron on the production server. Status: blocked on credentials.",
        ),
        # Chunk 5: Restricted admin credentials containing CANARY token
        IngestedChunk(
            chunk_id="chunk-restricted-005",
            source_id="admin_vault.json",
            source_type=SourceType.MEETING_NOTE,
            author="Lead Admin",
            timestamp=ts_30d_ago,
            access_label=AccessLabel.RESTRICTED,
            content=f"RESTRICTED: Root production deployment key is {canary}. Do not share with incoming junior members.",
            has_canary=True,
        ),
        # Chunk 6: Meeting notes on Redis cache
        IngestedChunk(
            chunk_id="chunk-doc-006",
            source_id="meeting_notes.md",
            source_type=SourceType.MEETING_NOTE,
            author="Charlie Ops",
            timestamp=ts_10d_ago,
            access_label=AccessLabel.PUBLIC,
            content="Redis cluster deployed on port 6379 with TTL set to 3600 seconds.",
        ),
    ]

    chunks_dict = {c.chunk_id: c for c in chunks}

    claims: List[ClaimEntry] = [
        # Claim 1: Postgres migration (newer)
        ClaimEntry(
            claim_id="claim-001",
            entity_id="database_engine",
            attribute_key="db_type",
            claim_text="Database was migrated to postgresql on port 5432.",
            state=EvidenceState.VERIFIED,
            effective_label=AccessLabel.PUBLIC,
            citations=[Citation(chunk_id="chunk-git-001", quote_span="migrated database engine from sqlite to postgresql on port 5432")],
            source_timestamp=ts_30d_ago,
            created_by=leaver,
        ),
        # Claim 2: SQLite selection (older - should be superseded)
        ClaimEntry(
            claim_id="claim-002",
            entity_id="database_engine",
            attribute_key="db_type",
            claim_text="Database backend is sqlite3.",
            state=EvidenceState.INFERRED,
            effective_label=AccessLabel.PUBLIC,
            citations=[Citation(chunk_id="chunk-git-002", quote_span="initialized sqlite3 database backend")],
            source_timestamp=ts_120d_ago,
            created_by="Bob Developer",
        ),
        # Claim 3: Auth workaround
        ClaimEntry(
            claim_id="claim-003",
            entity_id="auth_service",
            attribute_key="workaround",
            claim_text="Token refresh uses in-memory fallback cache when Redis is warming up.",
            state=EvidenceState.INFERRED,
            effective_label=AccessLabel.INTERNAL,
            citations=[Citation(chunk_id="chunk-chat-003", quote_span="we use an in-memory fallback cache when Redis is warming up")],
            source_timestamp=ts_10d_ago,
            created_by=leaver,
        ),
        # Claim 4: Stale backup cron
        ClaimEntry(
            claim_id="claim-004",
            entity_id="backup_cron",
            attribute_key="status",
            claim_text="Automated backup cron is blocked on credentials.",
            state=EvidenceState.INFERRED,
            effective_label=AccessLabel.INTERNAL,
            citations=[Citation(chunk_id="chunk-task-004", quote_span="Setup automated backup cron on the production server. Status: blocked on credentials.")],
            source_timestamp=ts_80d_ago,
            created_by=leaver,
        ),
        # Claim 5: Restricted root key (carries canary and restricted label)
        ClaimEntry(
            claim_id="claim-005",
            entity_id="deploy_pipeline",
            attribute_key="root_secret",
            claim_text=f"Production deployment root secret contains canary: {canary}",
            state=EvidenceState.VERIFIED,
            effective_label=AccessLabel.RESTRICTED,
            citations=[Citation(chunk_id="chunk-restricted-005", quote_span=f"Root production deployment key is {canary}")],
            source_timestamp=ts_30d_ago,
            created_by="Lead Admin",
        ),
        # Claim 6: Redis cluster
        ClaimEntry(
            claim_id="claim-006",
            entity_id="cache_layer",
            attribute_key="redis_port",
            claim_text="Redis cluster is on port 6379 with TTL 3600 seconds.",
            state=EvidenceState.VERIFIED,
            effective_label=AccessLabel.PUBLIC,
            citations=[Citation(chunk_id="chunk-doc-006", quote_span="Redis cluster deployed on port 6379 with TTL set to 3600 seconds.")],
            source_timestamp=ts_10d_ago,
            created_by="Charlie Ops",
        ),
    ]

    # Build Knowledge Graph Engine
    engine = KnowledgeGraphEngine(leaver_name=leaver)
    engine.add_entity("database_engine", "Database Engine (PostgreSQL)", EntityType.COMPONENT)
    engine.add_entity("auth_service", "Auth Service", EntityType.COMPONENT)
    engine.add_entity("cache_layer", "Redis Cache", EntityType.COMPONENT)
    engine.add_entity("backup_cron", "Production Backup Task", EntityType.TASK)
    engine.add_entity("deploy_pipeline", "Deployment Pipeline", EntityType.COMPONENT)

    # Add dependencies
    engine.add_dependency("auth_service", "database_engine")
    engine.add_dependency("auth_service", "cache_layer")
    engine.add_dependency("backup_cron", "database_engine")
    engine.add_dependency("deploy_pipeline", "auth_service")

    # Attach chunks and claims
    for ch in chunks:
        if "db" in ch.chunk_id or "sqlite" in ch.content or "postgres" in ch.content:
            engine.attach_chunk("database_engine", ch)
        elif "chat" in ch.chunk_id or "token" in ch.content:
            engine.attach_chunk("auth_service", ch)
        elif "task" in ch.chunk_id or "backup" in ch.content:
            engine.attach_chunk("backup_cron", ch)
        elif "restricted" in ch.chunk_id or "deploy" in ch.content:
            engine.attach_chunk("deploy_pipeline", ch)
        elif "doc" in ch.chunk_id or "redis" in ch.content:
            engine.attach_chunk("cache_layer", ch)

    for cl in claims:
        engine.attach_claim(cl.entity_id, cl)

    return chunks, claims, engine
