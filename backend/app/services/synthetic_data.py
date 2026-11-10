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
        # Chunk 7: Idempotency distributed lock
        IngestedChunk(
            chunk_id="chunk-git-007",
            source_id="git_log.json",
            source_type=SourceType.GIT_COMMIT,
            author=leaver,
            timestamp=ts_10d_ago,
            access_label=AccessLabel.INTERNAL,
            content="Distributed Redis lock uses SHA-256 idempotency key with 120s TTL to prevent double charges.",
        ),
        # Chunk 8: Stripe webhook race condition gotcha
        IngestedChunk(
            chunk_id="chunk-chat-008",
            source_id="discord_export.json",
            source_type=SourceType.CHAT_MESSAGE,
            author=leaver,
            timestamp=ts_10d_ago,
            access_label=AccessLabel.INTERNAL,
            content="Incident note: Stripe webhook retries can cause race conditions if the event timestamp is older than 5 minutes.",
        ),
        # Chunk 9: pgbouncer connection pool exhaustion
        IngestedChunk(
            chunk_id="chunk-doc-009",
            source_id="meeting_notes.md",
            source_type=SourceType.MEETING_NOTE,
            author="Charlie Ops",
            timestamp=ts_10d_ago,
            access_label=AccessLabel.INTERNAL,
            content="PostgreSQL pgbouncer connection pool exhaustion during peak transaction bursts (pool size max 100).",
        ),
        # Chunk 10: Billing invoice lock
        IngestedChunk(
            chunk_id="chunk-doc-010",
            source_id="meeting_notes.md",
            source_type=SourceType.MEETING_NOTE,
            author=leaver,
            timestamp=ts_30d_ago,
            access_label=AccessLabel.INTERNAL,
            content="Prorated invoice generation triggers a temporary lock on merchant subscription rows during month-end billing runs.",
        ),
        # Chunk 11: AWS KMS tokenization key
        IngestedChunk(
            chunk_id="chunk-doc-011",
            source_id="admin_vault.json",
            source_type=SourceType.MEETING_NOTE,
            author="Lead Admin",
            timestamp=ts_30d_ago,
            access_label=AccessLabel.INTERNAL,
            content="AWS KMS key arn:aws:kms:us-east-1:1029384756:key/pay-auth-2026 encrypts customer card PAN tokens.",
        ),
        # Chunk 12: PagerDuty escalation
        IngestedChunk(
            chunk_id="chunk-chat-012",
            source_id="discord_export.json",
            source_type=SourceType.CHAT_MESSAGE,
            author="Lead Admin",
            timestamp=ts_10d_ago,
            access_label=AccessLabel.INTERNAL,
            content="PagerDuty escalation policy routes P0 payment failure alerts to #eng-payments-oncall.",
        ),
        # Chunk 13: Bank SFTP clearing
        IngestedChunk(
            chunk_id="chunk-doc-013",
            source_id="meeting_notes.md",
            source_type=SourceType.MEETING_NOTE,
            author="Charlie Ops",
            timestamp=ts_30d_ago,
            access_label=AccessLabel.INTERNAL,
            content="Banking partner SFTP endpoint sftp.partnerbank.com:22 requires IP whitelisting for settlement batch uploads.",
        ),
        # Chunk 14: Kafka stream
        IngestedChunk(
            chunk_id="chunk-git-014",
            source_id="git_log.json",
            source_type=SourceType.GIT_COMMIT,
            author=leaver,
            timestamp=ts_30d_ago,
            access_label=AccessLabel.INTERNAL,
            content="Apache Kafka cluster configured with 12 partitions for payment authorization events on port 9092.",
        ),
        # Chunk 15: Webhook v2 task
        IngestedChunk(
            chunk_id="chunk-task-015",
            source_id="tasks_export.json",
            source_type=SourceType.TASK_CARD,
            author="Bob Developer",
            timestamp=ts_10d_ago,
            access_label=AccessLabel.INTERNAL,
            content="Task-408: Migrate legacy v1 webhook listeners to v2 HMAC-SHA256 signature verification.",
        ),
        # Chunk 16: Settlement worker task
        IngestedChunk(
            chunk_id="chunk-task-016",
            source_id="tasks_export.json",
            source_type=SourceType.TASK_CARD,
            author=leaver,
            timestamp=ts_30d_ago,
            access_label=AccessLabel.INTERNAL,
            content="Task-412: Complete automated settlement reconciliation worker before Friday clearing window.",
        ),
        # Chunk 17: pgbouncer tuning task
        IngestedChunk(
            chunk_id="chunk-task-017",
            source_id="tasks_export.json",
            source_type=SourceType.TASK_CARD,
            author="Charlie Ops",
            timestamp=ts_10d_ago,
            access_label=AccessLabel.INTERNAL,
            content="Task-415: Increase max client connections from 100 to 500 before Black Friday traffic surge.",
        ),
        # Chunk 18: SDK upgrade task
        IngestedChunk(
            chunk_id="chunk-task-018",
            source_id="tasks_export.json",
            source_type=SourceType.TASK_CARD,
            author="Bob Developer",
            timestamp=ts_10d_ago,
            access_label=AccessLabel.INTERNAL,
            content="Task-419: Upgrade stripe-python library to version 8.0.0 to support 3DS2 biometric challenge flows.",
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
        # Claim 7: Idempotency lock
        ClaimEntry(
            claim_id="claim-007",
            entity_id="idempotency_store",
            attribute_key="lock_strategy",
            claim_text="Distributed Redis lock uses SHA-256 idempotency key with 120s TTL to prevent double charges.",
            state=EvidenceState.VERIFIED,
            effective_label=AccessLabel.INTERNAL,
            citations=[Citation(chunk_id="chunk-git-007", quote_span="Distributed Redis lock uses SHA-256 idempotency key with 120s TTL to prevent double charges.")],
            source_timestamp=ts_10d_ago,
            created_by=leaver,
        ),
        # Claim 8: Webhook gotcha
        ClaimEntry(
            claim_id="claim-008",
            entity_id="webhook_receiver",
            attribute_key="race_condition_gotcha",
            claim_text="Stripe webhook retries can cause race conditions if the event timestamp is older than 5 minutes.",
            state=EvidenceState.INFERRED,
            effective_label=AccessLabel.INTERNAL,
            citations=[Citation(chunk_id="chunk-chat-008", quote_span="Stripe webhook retries can cause race conditions if the event timestamp is older than 5 minutes.")],
            source_timestamp=ts_10d_ago,
            created_by=leaver,
        ),
        # Claim 9: Database pool limits
        ClaimEntry(
            claim_id="claim-009",
            entity_id="database_engine",
            attribute_key="pool_limits",
            claim_text="PostgreSQL pgbouncer connection pool exhaustion during peak transaction bursts (pool size max 100).",
            state=EvidenceState.INFERRED,
            effective_label=AccessLabel.INTERNAL,
            citations=[Citation(chunk_id="chunk-doc-009", quote_span="PostgreSQL pgbouncer connection pool exhaustion during peak transaction bursts (pool size max 100).")],
            source_timestamp=ts_10d_ago,
            created_by="Charlie Ops",
        ),
        # Claim 10: Billing table lock gotcha
        ClaimEntry(
            claim_id="claim-010",
            entity_id="billing_worker",
            attribute_key="invoice_table_lock",
            claim_text="Prorated invoice generation triggers a temporary lock on merchant subscription rows during month-end billing runs.",
            state=EvidenceState.INFERRED,
            effective_label=AccessLabel.INTERNAL,
            citations=[Citation(chunk_id="chunk-doc-010", quote_span="Prorated invoice generation triggers a temporary lock on merchant subscription rows during month-end billing runs.")],
            source_timestamp=ts_30d_ago,
            created_by=leaver,
        ),
        # Claim 11: AWS KMS tokenization key
        ClaimEntry(
            claim_id="claim-011",
            entity_id="aws_kms",
            attribute_key="encryption_key",
            claim_text="AWS KMS key arn:aws:kms:us-east-1:1029384756:key/pay-auth-2026 encrypts customer card PAN tokens.",
            state=EvidenceState.VERIFIED,
            effective_label=AccessLabel.INTERNAL,
            citations=[Citation(chunk_id="chunk-doc-011", quote_span="AWS KMS key arn:aws:kms:us-east-1:1029384756:key/pay-auth-2026 encrypts customer card PAN tokens.")],
            source_timestamp=ts_30d_ago,
            created_by="Lead Admin",
        ),
        # Claim 12: PagerDuty escalation
        ClaimEntry(
            claim_id="claim-012",
            entity_id="datadog_monitoring",
            attribute_key="alert_policy",
            claim_text="PagerDuty escalation policy routes P0 payment failure alerts to #eng-payments-oncall.",
            state=EvidenceState.VERIFIED,
            effective_label=AccessLabel.INTERNAL,
            citations=[Citation(chunk_id="chunk-chat-012", quote_span="PagerDuty escalation policy routes P0 payment failure alerts to #eng-payments-oncall.")],
            source_timestamp=ts_10d_ago,
            created_by="Lead Admin",
        ),
        # Claim 13: Bank SFTP clearing
        ClaimEntry(
            claim_id="claim-013",
            entity_id="bank_sftp",
            attribute_key="ip_whitelist",
            claim_text="Banking partner SFTP endpoint sftp.partnerbank.com:22 requires IP whitelisting for settlement batch uploads.",
            state=EvidenceState.VERIFIED,
            effective_label=AccessLabel.INTERNAL,
            citations=[Citation(chunk_id="chunk-doc-013", quote_span="Banking partner SFTP endpoint sftp.partnerbank.com:22 requires IP whitelisting for settlement batch uploads.")],
            source_timestamp=ts_30d_ago,
            created_by="Charlie Ops",
        ),
        # Claim 14: Kafka stream
        ClaimEntry(
            claim_id="claim-014",
            entity_id="event_stream",
            attribute_key="kafka_partitions",
            claim_text="Apache Kafka cluster configured with 12 partitions for payment authorization events on port 9092.",
            state=EvidenceState.VERIFIED,
            effective_label=AccessLabel.INTERNAL,
            citations=[Citation(chunk_id="chunk-git-014", quote_span="Apache Kafka cluster configured with 12 partitions for payment authorization events on port 9092.")],
            source_timestamp=ts_30d_ago,
            created_by=leaver,
        ),
        # Claim 15: Webhook v2 task
        ClaimEntry(
            claim_id="claim-015",
            entity_id="webhook_v2",
            attribute_key="migration_status",
            claim_text="Task-408: Migrate legacy v1 webhook listeners to v2 HMAC-SHA256 signature verification.",
            state=EvidenceState.INFERRED,
            effective_label=AccessLabel.INTERNAL,
            citations=[Citation(chunk_id="chunk-task-015", quote_span="Task-408: Migrate legacy v1 webhook listeners to v2 HMAC-SHA256 signature verification.")],
            source_timestamp=ts_10d_ago,
            created_by="Bob Developer",
        ),
        # Claim 16: Settlement worker task
        ClaimEntry(
            claim_id="claim-016",
            entity_id="settlement_reconciliation",
            attribute_key="parser_deadline",
            claim_text="Task-412: Complete automated settlement reconciliation worker before Friday clearing window.",
            state=EvidenceState.INFERRED,
            effective_label=AccessLabel.INTERNAL,
            citations=[Citation(chunk_id="chunk-task-016", quote_span="Task-412: Complete automated settlement reconciliation worker before Friday clearing window.")],
            source_timestamp=ts_30d_ago,
            created_by=leaver,
        ),
        # Claim 17: pgbouncer tuning task
        ClaimEntry(
            claim_id="claim-017",
            entity_id="pgbouncer_tuning",
            attribute_key="capacity_upgrade",
            claim_text="Task-415: Increase max client connections from 100 to 500 before Black Friday traffic surge.",
            state=EvidenceState.INFERRED,
            effective_label=AccessLabel.INTERNAL,
            citations=[Citation(chunk_id="chunk-task-017", quote_span="Task-415: Increase max client connections from 100 to 500 before Black Friday traffic surge.")],
            source_timestamp=ts_10d_ago,
            created_by="Charlie Ops",
        ),
        # Claim 18: SDK upgrade task
        ClaimEntry(
            claim_id="claim-018",
            entity_id="dependency_upgrade",
            attribute_key="stripe_sdk",
            claim_text="Task-419: Upgrade stripe-python library to version 8.0.0 to support 3DS2 biometric challenge flows.",
            state=EvidenceState.INFERRED,
            effective_label=AccessLabel.INTERNAL,
            citations=[Citation(chunk_id="chunk-task-018", quote_span="Task-419: Upgrade stripe-python library to version 8.0.0 to support 3DS2 biometric challenge flows.")],
            source_timestamp=ts_10d_ago,
            created_by="Bob Developer",
        ),
    ]

    # Build Knowledge Graph Engine
    engine = KnowledgeGraphEngine(leaver_name=leaver)
    engine.add_entity("database_engine", "Database Engine (PostgreSQL)", EntityType.COMPONENT)
    engine.add_entity("auth_service", "Auth Service", EntityType.COMPONENT)
    engine.add_entity("cache_layer", "Redis Cache", EntityType.COMPONENT)
    engine.add_entity("backup_cron", "Production Backup Task", EntityType.TASK)
    engine.add_entity("deploy_pipeline", "Deployment Pipeline", EntityType.COMPONENT)
    engine.add_entity("idempotency_store", "Idempotency Store (Redis)", EntityType.COMPONENT)
    engine.add_entity("webhook_receiver", "Webhook Ingestion Service", EntityType.COMPONENT)
    engine.add_entity("billing_worker", "Billing Invoicing Engine", EntityType.COMPONENT)
    engine.add_entity("aws_kms", "AWS KMS Key Vault", EntityType.COMPONENT)
    engine.add_entity("datadog_monitoring", "Datadog / PagerDuty Alerting", EntityType.COMPONENT)
    engine.add_entity("bank_sftp", "Banking Partner SFTP", EntityType.COMPONENT)
    engine.add_entity("event_stream", "Kafka Event Stream", EntityType.COMPONENT)
    engine.add_entity("webhook_v2", "Webhook Migration Task", EntityType.TASK)
    engine.add_entity("settlement_reconciliation", "Settlement Reconciliation Task", EntityType.TASK)
    engine.add_entity("pgbouncer_tuning", "Connection Pool Tuning Task", EntityType.TASK)
    engine.add_entity("dependency_upgrade", "SDK Upgrade Task", EntityType.TASK)

    # Add dependencies
    engine.add_dependency("auth_service", "database_engine")
    engine.add_dependency("auth_service", "cache_layer")
    engine.add_dependency("backup_cron", "database_engine")
    engine.add_dependency("deploy_pipeline", "auth_service")
    engine.add_dependency("webhook_receiver", "idempotency_store")
    engine.add_dependency("webhook_receiver", "event_stream")
    engine.add_dependency("billing_worker", "database_engine")
    engine.add_dependency("settlement_reconciliation", "bank_sftp")

    # Attach chunks and claims
    for ch in chunks:
        if "db" in ch.chunk_id or "sqlite" in ch.content or "postgres" in ch.content:
            engine.attach_chunk("database_engine", ch)
        elif "chat" in ch.chunk_id and "token" in ch.content:
            engine.attach_chunk("auth_service", ch)
        elif "backup" in ch.content:
            engine.attach_chunk("backup_cron", ch)
        elif "redis" in ch.content:
            engine.attach_chunk("cache_layer", ch)
        elif "restricted" in ch.chunk_id or "deploy" in ch.content:
            engine.attach_chunk("deploy_pipeline", ch)
        else:
            for node_id in engine.graph.nodes:
                if node_id in ch.content.lower() or node_id.replace("_", "") in ch.content.lower().replace(" ", ""):
                    engine.attach_chunk(node_id, ch)
                    break

    for cl in claims:
        engine.attach_claim(cl.entity_id, cl)

    return chunks, claims, engine
