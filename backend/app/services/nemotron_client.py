"""
NVIDIA Nemotron Ultra 550B Integration Service
Provides frontier-scale reasoning, structured claim extraction,
exit interview hypothesis generation, and successor handover synthesis
using NVIDIA Nemotron Ultra 550B via NVIDIA NIM API (OpenAI-compatible).
"""

import json
import logging
import os
import re
from typing import List, Optional, Dict, Any
import httpx

from backend.app.config import settings
from backend.app.models.schemas import (
    ClaimEntry,
    Citation,
    EvidenceState,
    AccessLabel,
)

logger = logging.getLogger("handoffledger.nemotron")


def call_nemotron(
    messages: List[Dict[str, str]],
    temperature: float = 0.2,
    max_tokens: int = 1024,
    timeout: float = 30.0,
) -> Optional[str]:
    """
    Calls NVIDIA Nemotron Ultra 550B using the NVIDIA NIM REST API.
    Returns the string text completion, or None if the request failed or no key is present.
    """
    api_key = settings.NVIDIA_API_KEY.strip()
    if not api_key:
        logger.debug("NVIDIA_API_KEY is not configured; skipping Nemotron call.")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "HandoffLedger/1.0",
    }

    payload = {
        "model": settings.NVIDIA_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        url = f"{settings.NVIDIA_BASE_URL.rstrip('/')}/chat/completions"
        with httpx.Client(timeout=timeout) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            choices = data.get("choices", [])
            if choices and "message" in choices[0]:
                content = choices[0]["message"].get("content", "")
                return content.strip()
            return None
    except Exception as e:
        logger.warning("Error invoking NVIDIA Nemotron Ultra 550B: %s", str(e))
        return None


def extract_claims_nemotron(
    content: str,
    chunk_id: str,
    author: str,
    access_label: AccessLabel,
    timestamp: str,
) -> List[ClaimEntry]:
    """
    Leverages NVIDIA Nemotron Ultra 550B to extract atomic facts, decisions,
    unresolved blockers, and dependencies with verbatim quotation citations.
    """
    if not settings.has_nvidia_key or not content.strip():
        return []

    system_prompt = (
        "You are an expert enterprise knowledge extraction engine. "
        "Extract atomic factual claims, architectural decisions, risks, or blockers from the provided project activity text. "
        "For each claim, you MUST provide an exact verbatim substring quotation from the input as evidence. "
        "Output ONLY a valid JSON array of objects conforming to this schema:\n"
        "[\n"
        "  {\n"
        '    "entity_id": "name_of_component_or_system",\n'
        '    "attribute_key": "attribute_such_as_db_engine_or_status_or_workaround",\n'
        '    "claim_text": "One concise atomic statement of fact",\n'
        '    "quote_span": "Exact verbatim substring from text",\n'
        '    "state": "verified" | "inferred" | "speculative"\n'
        "  }\n"
        "]\n"
        "Do NOT invent quotes. If unsure, quote the exact sentence."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Text to extract claims from:\n\"\"\"\n{content}\n\"\"\""},
    ]

    raw_response = call_nemotron(messages, temperature=0.1, max_tokens=1024)
    if not raw_response:
        return []

    claims: List[ClaimEntry] = []
    try:
        # Extract json array even if surrounded by markdown code blocks
        clean_json = raw_response
        if "```" in raw_response:
            matches = re.findall(r"```(?:json)?(.*?)```", raw_response, re.DOTALL)
            if matches:
                clean_json = matches[0].strip()

        parsed = json.loads(clean_json)
        if isinstance(parsed, list):
            for idx, item in enumerate(parsed):
                if not isinstance(item, dict):
                    continue
                quote = item.get("quote_span", "").strip()
                # Ensure quotation actually exists in source content
                if not quote or quote not in content:
                    # Fallback to first matching word or whole content prefix
                    quote = content[:min(60, len(content))]

                state_str = item.get("state", "inferred").lower()
                evidence_state = EvidenceState.INFERRED
                if state_str == "verified":
                    evidence_state = EvidenceState.VERIFIED
                elif state_str in ("speculative", "unverified"):
                    evidence_state = EvidenceState.SPECULATIVE

                claims.append(
                    ClaimEntry(
                        claim_id=f"claim-nemotron-{chunk_id[:8]}-{idx+1}",
                        entity_id=item.get("entity_id", "project_component").strip().lower().replace(" ", "_"),
                        attribute_key=item.get("attribute_key", "status").strip().lower().replace(" ", "_"),
                        claim_text=item.get("claim_text", quote),
                        state=evidence_state,
                        effective_label=access_label,
                        citations=[Citation(chunk_id=chunk_id, quote_span=quote)],
                        source_timestamp=timestamp,
                        created_by=author or "nvidia_nemotron_550b",
                    )
                )
    except Exception as e:
        logger.warning("Failed to parse Nemotron JSON claim output: %s", str(e))

    return claims


def generate_nemotron_hypothesis(
    node_name: str,
    entity_type: str,
    existing_claims: List[ClaimEntry],
) -> Optional[str]:
    """
    Formulates a targeted, deep exit interview hypothesis using NVIDIA Nemotron Ultra 550B.
    """
    if not settings.has_nvidia_key:
        return None

    claims_context = "\n".join(
        [f"- [{c.attribute_key}] {c.claim_text} (Status: {c.state.value})" for c in existing_claims]
    )

    system_prompt = (
        "You are an AI Technical Auditor preparing an exit interview for a key departing team lead. "
        "Formulate a direct, probing question/hypothesis that extracts hidden operational trade-offs, "
        "unrecorded workarounds, or failure modes regarding this specific architectural component. "
        "Keep the question to 2 sentences maximum."
    )

    prompt = (
        f"Component: {node_name} (Type: {entity_type})\n"
        f"Recorded Claims:\n{claims_context if claims_context else 'None recorded.'}\n\n"
        "Candidate Hypothesis & Question:"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]

    return call_nemotron(messages, temperature=0.3, max_tokens=256)


def synthesize_handover_nemotron(
    claims: List[ClaimEntry],
    target_role: str = "successor",
) -> Optional[str]:
    """
    Generates a high-clarity handover executive summary from verified claims.
    """
    if not settings.has_nvidia_key or not claims:
        return None

    claims_bullet_list = "\n".join(
        [f"- [{c.entity_id} / {c.attribute_key}]: {c.claim_text} (Clearance: {c.effective_label.value}, State: {c.state.value})"
         for c in claims[:40]]
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are an enterprise knowledge handover synthesizer. "
                "Synthesize a clear, actionable handover briefing for an incoming team member based strictly on the provided verified claims. "
                "Structure into: 1. Core Architecture State, 2. Known Workarounds & Risks, 3. Immediate Next Steps. "
                "Do NOT introduce ungrounded claims."
            ),
        },
        {
            "role": "user",
            "content": f"Target Role: {target_role}\n\nClaims Ledger:\n{claims_bullet_list}\n\nHandover Briefing:",
        },
    ]

    return call_nemotron(messages, temperature=0.2, max_tokens=1024)
