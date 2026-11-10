"""
HandoffLedger Ingestion & Chunking Service
Transforms heterogeneous project artifacts (git commits, chats, tasks, docs)
into immutable, verifiable IngestedChunk models with SHA-256 content hashes.
"""

import hashlib
import json
from typing import List, Dict, Any, Optional
from backend.app.models.schemas import (
    IngestedChunk,
    SourceType,
    AccessLabel,
)
from backend.app.services.redactor import sanitize_credentials
from backend.app.config import settings


def generate_chunk_id(source_id: str, content: str, timestamp: str) -> str:
    """Computes a deterministic SHA-256 identifier for an atomic chunk."""
    raw = f"{source_id}:{timestamp}:{content}"
    return f"chunk-{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]}"


def chunk_git_commit(commit: Dict[str, Any], source_id: str = "git_log.json") -> IngestedChunk:
    """Chunks a single git commit message."""
    raw_content = commit.get("message", "")
    sanitized = sanitize_credentials(raw_content)
    timestamp = commit.get("date", "")
    author = commit.get("author", "Unknown Author")
    access_label_str = commit.get("access_label", "PUBLIC")

    try:
        label = AccessLabel(access_label_str.upper())
    except ValueError:
        label = AccessLabel.PUBLIC

    has_canary = settings.CANARY_TOKEN_SEED in raw_content or settings.CANARY_TOKEN_SEED in sanitized
    chunk_id = generate_chunk_id(source_id, sanitized, timestamp)

    return IngestedChunk(
        chunk_id=chunk_id,
        source_id=source_id,
        source_type=SourceType.GIT_COMMIT,
        author=author,
        timestamp=timestamp,
        access_label=label,
        content=sanitized,
        char_start=0,
        char_end=len(sanitized),
        has_canary=has_canary,
        metadata={"commit_hash": commit.get("commit_hash", "")},
    )


def chunk_chat_message(msg: Dict[str, Any], source_id: str = "discord_export.json") -> IngestedChunk:
    """Chunks a single chat export message."""
    raw_content = msg.get("content", "")
    sanitized = sanitize_credentials(raw_content)
    timestamp = msg.get("timestamp", "")
    author = msg.get("author", "Unknown Member")
    access_label_str = msg.get("access_label", "INTERNAL")

    try:
        label = AccessLabel(access_label_str.upper())
    except ValueError:
        label = AccessLabel.INTERNAL

    has_canary = settings.CANARY_TOKEN_SEED in raw_content or settings.CANARY_TOKEN_SEED in sanitized
    chunk_id = generate_chunk_id(source_id, sanitized, timestamp)

    return IngestedChunk(
        chunk_id=chunk_id,
        source_id=source_id,
        source_type=SourceType.CHAT_MESSAGE,
        author=author,
        timestamp=timestamp,
        access_label=label,
        content=sanitized,
        char_start=0,
        char_end=len(sanitized),
        has_canary=has_canary,
        metadata={"channel": msg.get("channel", "")},
    )


def chunk_task_entry(task: Dict[str, Any], source_id: str = "tasks_export.json") -> IngestedChunk:
    """Chunks a project management task item."""
    title = task.get("title", "")
    desc = task.get("description", "")
    raw_content = f"{title}: {desc}" if title else desc
    sanitized = sanitize_credentials(raw_content)
    timestamp = task.get("updated_at", "")
    author = task.get("assignee", "Unknown Assignee")
    access_label_str = task.get("access_label", "INTERNAL")

    try:
        label = AccessLabel(access_label_str.upper())
    except ValueError:
        label = AccessLabel.INTERNAL

    has_canary = settings.CANARY_TOKEN_SEED in raw_content or settings.CANARY_TOKEN_SEED in sanitized
    chunk_id = generate_chunk_id(source_id, sanitized, timestamp)

    return IngestedChunk(
        chunk_id=chunk_id,
        source_id=source_id,
        source_type=SourceType.TASK_CARD,
        author=author,
        timestamp=timestamp,
        access_label=label,
        content=sanitized,
        char_start=0,
        char_end=len(sanitized),
        has_canary=has_canary,
        metadata={"task_id": task.get("task_id", "")},
    )


def chunk_markdown_document(
    doc_content: str,
    source_id: str = "meeting_notes.md",
    author: str = "Lead Admin",
    timestamp: str = "2026-11-01T12:00:00Z",
) -> List[IngestedChunk]:
    """Chunks markdown by sections or bullet blocks, extracting embedded access labels."""
    chunks: List[IngestedChunk] = []
    lines = doc_content.splitlines()
    current_section = []
    current_label = AccessLabel.PUBLIC

    for line in lines:
        if line.startswith("#"):
            if current_section:
                sec_text = "\n".join(current_section).strip()
                if sec_text:
                    sanitized = sanitize_credentials(sec_text)
                    has_canary = settings.CANARY_TOKEN_SEED in sanitized
                    chunk_id = generate_chunk_id(source_id, sanitized, timestamp)
                    chunks.append(
                        IngestedChunk(
                            chunk_id=chunk_id,
                            source_id=source_id,
                            source_type=SourceType.MEETING_NOTE,
                            author=author,
                            timestamp=timestamp,
                            access_label=current_label,
                            content=sanitized,
                            char_start=0,
                            char_end=len(sanitized),
                            has_canary=has_canary,
                        )
                    )
                current_section = []

            # Check header label
            line_upper = line.upper()
            if "RESTRICTED" in line_upper:
                current_label = AccessLabel.RESTRICTED
            elif "INTERNAL" in line_upper:
                current_label = AccessLabel.INTERNAL
            else:
                current_label = AccessLabel.PUBLIC
            current_section.append(line)
        else:
            current_section.append(line)

    if current_section:
        sec_text = "\n".join(current_section).strip()
        if sec_text:
            sanitized = sanitize_credentials(sec_text)
            has_canary = settings.CANARY_TOKEN_SEED in sanitized
            chunk_id = generate_chunk_id(source_id, sanitized, timestamp)
            chunks.append(
                IngestedChunk(
                    chunk_id=chunk_id,
                    source_id=source_id,
                    source_type=SourceType.MEETING_NOTE,
                    author=author,
                    timestamp=timestamp,
                    access_label=current_label,
                    content=sanitized,
                    char_start=0,
                    char_end=len(sanitized),
                    has_canary=has_canary,
                )
            )

    return chunks
