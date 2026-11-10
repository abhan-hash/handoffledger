# Design: Realistic Fintech Knowledge Base & Professional Nemotron UX

* **Date:** 2026-11-11
* **Author:** abhan
* **Status:** Proposed

---

## 1. Intent & Why
HandoffLedger replaces narrative, unverified handover documents with an evidence-linked claim ledger and risk engine. Currently, the sample dataset contains only 6 sparse items, leaving key UI views like "Pending Tasks" completely empty and using toy terminology ("local club demo"). Furthermore, while the system is powered by the NVIDIA Nemotron Ultra 550B model, there is no visible, interactive surface for a judge to test or experience the model directly.

This design upgrades the sample dataset into a realistic high-scale payment engineering service (`Core Payment & Ledger API`), populates all four Successor Runway panes with 16–20 genuine technical items, adds tactile onboarding interactions (acknowledging gotchas, copying runbook commands), and embeds a clean, professional NVIDIA Nemotron architecture briefing and Q&A interface with zero emoji clutter.

---

## 2. Goals & Non-Goals

### Goals
- **Dense, Professional Engineering Data**: Flood the 4 cognitive panes with 16–20 realistic technical claims (Stripe webhook race conditions, Redis idempotency locks, PostgreSQL connection pool exhaustion, AWS KMS keys, Kafka event queues, PagerDuty on-call escalation).
- **Fix Empty Category Issue**: Fix regex classification in `successor.py` so "Pending Tasks & Next Steps" displays actionable sprint items.
- **Visible, Elegant NVIDIA Nemotron Integration**: Add a professional "Technical Architecture Briefing" card in the Successor view with real-time synthesis and an interactive "Query Architecture Ledger" box.
- **Interactive Onboarding Utility**: Add clean tactile actions ("Acknowledge Hazard", "Copy Command", and quick filter pills) so the user experiences onboarding friction disappearing.
- **Strict Aesthetic Restraint**: Use clean typography, subtle Lucide icons (`Terminal`, `Copy`, `Check`, `Shield`), and no excessive AI emojis or marketing fluff.
- **100% Backward Compatibility**: All 34 automated pytest unit/integration tests must continue to pass with zero regressions.

### Non-Goals
- Rebranding HandoffLedger or altering its core identity.
- Changing existing navigation tabs, visual layouts, or CSS color palette.
- Defeating or bypassing lattice security access controls or canary token assertions.

---

## 3. Approaches Considered

1. **Approach 1: Dense Dataset + Interactive Runway + Professional Nemotron Terminal (Selected)**
   - Expands backend synthetic fixtures to 16–20 production fintech items.
   - Refines `successor.py` pane mapping to evenly distribute items into all 4 panes.
   - Adds a clean, professional Nemotron briefing generator and prompt chips in `SuccessorView.tsx`.
   - Adds "Acknowledge" and "Copy Command" buttons.
   - *Why Selected*: Directly resolves the empty/slop feeling, provides tangible proof of the 550B model, and preserves all existing visual polish.

2. **Approach 2: Backend Data-Only Expansion (Rejected)**
   - Expands the database fixtures without adding frontend interaction or query capabilities.
   - *Why Rejected*: The site remains passive reading material; judges still cannot see or verify the NVIDIA Nemotron key doing anything active.

3. **Approach 3: Complete Onboarding Wizard Redesign (Rejected)**
   - Restructures the UI into a multi-step setup wizard.
   - *Why Rejected*: Breaks user directive to preserve the existing page layout and visual design.

---

## 4. Technical Specifications

### A. Data Fixtures (`backend/app/services/synthetic_data.py`)
- Project name: `Core Payment & Ledger API (v2.4-prod)`
- Leaver: `Alice Chen (Principal Platform Engineer)`
- 16–20 Ingested Chunks & Claim Entries covering:
  - **Gotchas**: In-memory token fallback on Redis warmup; Stripe webhook signature timestamp drift; pgbouncer connection pool exhaustion; billing invoice lock window.
  - **Accounts & Access**: Production root deploy key (`CANARY_SECRET_UUIDv4_9823f4b1` under `RESTRICTED`); AWS KMS key for card PAN tokenization; PagerDuty payment alert policy; Bank SFTP clearing endpoint.
  - **Decisions**: PostgreSQL 16 migration on port 5432; Redis cluster with 3600s TTL and Sentinel failover; Kafka 12-partition topic routing; SHA-256 payload idempotency locks.
  - **Pending Tasks**: Unblocking automated backup cron credentials; v2 HMAC-SHA256 webhook migration; CAMT.053 settlement batch parser; pgbouncer max-connections increase.

### B. Successor Runway Categorization (`backend/app/services/successor.py`)
- Refactor categorization rules so tasks marked with `task` or `todo` or `blocked` are assigned to `backlog` unless they are explicitly secret/credential stores.

### C. NVIDIA Nemotron Endpoint & Service (`endpoints.py` & `nemotron_client.py`)
- Add `POST /api/v1/llm/query` accepting `{ "query": str }` and returning an architecture answer grounded in verified claims with citation IDs.
- Ensure `POST /api/v1/llm/synthesize` formats a clean, markdown executive summary.

### D. Frontend Interface (`frontend/src/components/SuccessorView.tsx`)
- Render a discreet, high-polish "Technical Briefing" header with:
  - "Generate Executive Briefing" button calling `/api/v1/llm/synthesize`.
  - An interactive architecture query input with 3 professional query chips.
- Add "Acknowledge" state toggle to gotcha cards.
- Add "Copy Command / Snippet" button to task and decision cards.
- Clean up labels to eliminate toy phrasing.

---

## 5. Verification & Testing
- Run `PYTHONPATH=. pytest tests/ -v` to ensure all 34 existing tests pass.
- Verify zero canary leaks in public/internal views.
- Test frontend build (`npm run build`) and verify in browser.
