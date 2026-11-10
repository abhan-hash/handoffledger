"""
HandoffLedger Successor Runway Presentation Service
Renders the role-appropriate 4-pane successor dashboard:
1. Active Landmines & Workarounds
2. Account & Key Ownership
3. Decision Rationale
4. Next Actions Backlog
Inserts structural redacted placeholders for inaccessible claims and verifies canary safety.
"""

from typing import List, Dict, Any
from backend.app.models.schemas import (
    ClaimEntry,
    AccessLabel,
    EvidenceState,
    SuccessorRunwayView,
    SuccessorPanes,
)
from backend.app.services.clearance import (
    project_successor_claims,
    detect_canary_leakage,
)


def build_successor_runway_view(
    claims: List[ClaimEntry],
    clearance: AccessLabel = AccessLabel.INTERNAL,
) -> SuccessorRunwayView:
    """
    Constructs the 4-pane successor runway dashboard, enforcing pre-generation lattice clearance
    and substituting structural stubs for unprivileged viewers.
    """
    projected = project_successor_claims(claims, clearance)

    landmines: List[ClaimEntry] = []
    accounts: List[ClaimEntry] = []
    decisions: List[ClaimEntry] = []
    backlog: List[ClaimEntry] = []

    for c in projected:
        text_lower = c.claim_text.lower()
        entity_lower = c.entity_id.lower()
        attr_lower = c.attribute_key.lower()

        # 1. Backlog / Tasks Priority Check
        if (
            "task" in entity_lower
            or "task-" in text_lower
            or "todo" in text_lower
            or "cron" in entity_lower
            or "upgrade" in entity_lower
            or "migration" in attr_lower
            or "deadline" in attr_lower
            or ("blocked" in text_lower and "backup" in text_lower)
        ):
            backlog.append(c)

        # 2. Gotchas / Landmines Check
        elif (
            "workaround" in text_lower
            or "gotcha" in attr_lower
            or "bug" in text_lower
            or "fallback" in text_lower
            or "flaky" in text_lower
            or "race condition" in text_lower
            or "exhaustion" in text_lower
            or "temporary lock" in text_lower
            or "limit" in attr_lower
        ):
            landmines.append(c)

        # 3. Accounts & Keys Check
        elif (
            "deploy" in entity_lower
            or "secret" in text_lower
            or "key" in text_lower
            or "account" in entity_lower
            or "credential" in text_lower
            or "kms" in entity_lower
            or "sftp" in entity_lower
            or "pagerduty" in text_lower
            or "alert" in attr_lower
            or "whitelist" in text_lower
        ):
            accounts.append(c)

        # 4. Decisions & Rationale
        else:
            decisions.append(c)

    # Assert canary safety on rendered payload
    payload_dump = str([c.model_dump() for c in projected])
    canary_leak_found = detect_canary_leakage(payload_dump)

    return SuccessorRunwayView(
        viewer_clearance=clearance.value,
        canary_leak_detected=canary_leak_found,
        panes=SuccessorPanes(
            landmines=landmines,
            accounts=accounts,
            decisions=decisions,
            backlog=backlog,
        ),
        total_claims_rendered=len(projected),
    )
