# Realistic Fintech Knowledge Base & Professional Nemotron UX Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform HandoffLedger's synthetic data from sparse toy placeholders into a dense, production-grade high-scale payment service (`Core Payment & Ledger API`), populate all four Successor Runway panes with 16–20 actionable items, add tactile Day-1 onboarding interactions (acknowledging gotchas, copying runbook snippets), and embed a clean, professional NVIDIA Nemotron Ultra 550B architecture briefing and Q&A surface.

**Architecture:** Expand backend fixtures in `synthetic_data.py` with 16–20 realistic fintech chunks and claims while preserving existing test entities. Refine categorization logic in `successor.py` to balance all four panes (Gotchas, Accounts, Decisions, Backlog). Add `POST /api/v1/llm/query` in `endpoints.py` calling `nemotron_client.py` for grounded Q&A with offline fallback. Enhance `SuccessorView.tsx` with an executive briefing panel, quick prompt chips, card acknowledgment toggles, and command-copy utilities adhering to the Elegostra obsidian theme.

**Tech Stack:** Python 3.10+, FastAPI, SQLAlchemy, NetworkX, Pytest, React 18, TypeScript, Tailwind CSS, Lucide icons, Framer Motion, Vite.

**Spec:** [`docs/superpowers/specs/2026-11-11-realistic-fintech-data-and-nemotron-ux-design.md`](file:///home/abhan/hackwpune/docs/superpowers/specs/2026-11-11-realistic-fintech-data-and-nemotron-ux-design.md)

## Global Constraints
- Product identity remains **HandoffLedger** (no product renaming or layout disruption).
- All 34 existing automated unit/integration tests must pass with zero regressions.
- Lattice security clearance (`PUBLIC < INTERNAL < LEAD_ONLY < RESTRICTED`) and canary token non-disclosure (`CANARY_SECRET_UUIDv4_9823f4b1`) must be strictly maintained.
- Visual aesthetic: Elegostra obsidian dark glass theme (`#080912`), restrained Lucide icons (`Terminal`, `Copy`, `Check`, `Shield`), no excessive AI emojis or marketing fluff.

## Review Focus
1. **Canary Non-Disclosure**: Canary token must never appear in `PUBLIC` or `INTERNAL` views, prompt completions, or UI card text.
2. **Backlog Population**: The "Pending Tasks & Next Steps" pane must not be empty; it must contain 4+ actionable tasks.
3. **Nemotron Offline Fallback**: If `NVIDIA_API_KEY` is empty, `/api/v1/llm/query` and `/api/v1/llm/synthesize` must return grounded fallback data with zero HTTP 500 errors.
4. **Interactive State Persistence**: Acknowledging gotchas or copying commands must trigger tactile toast feedback without reloading or breaking state.
5. **Exact Substring Citations**: All new claims must cite exact verbatim substrings in their corresponding chunks.

---

### Task 1: Realistic Fintech Dataset & Extractor Expansion

**Files:**
- Modify: `backend/app/services/synthetic_data.py`
- Modify: `backend/app/services/extractor.py`
- Test: `tests/test_chunker_and_extractor.py`
- Test: `tests/test_evaluation_harness.py`

- [ ] **Step 1: Write tests for expanded fintech claims and citations**
  Add unit assertions in `tests/test_chunker_and_extractor.py` asserting that new fintech chunks (webhook idempotency, pgbouncer pool, AWS KMS key, Kafka topic) extract valid claims with exact quote spans.
- [ ] **Step 2: Run test to confirm failure before implementation**
  `PYTHONPATH=. pytest tests/test_chunker_and_extractor.py -k "fintech" -v`
- [ ] **Step 3: Expand `synthetic_data.py` with 16–20 realistic fintech chunks and claims**
  In `get_v1_demo_fixtures()`, expand chunks and claims to include:
  - Gotchas: In-memory token fallback on Redis warmup (`auth_service`), Stripe webhook clock drift replay bug (`webhook_receiver`), pgbouncer connection pool exhaustion (`database_engine`), billing invoice table lock (`billing_worker`).
  - Accounts: Production root deployment key (`deploy_pipeline` - RESTRICTED canary), AWS KMS tokenization key (`aws_kms`), PagerDuty escalation policy (`datadog_monitoring`), Bank SFTP clearing endpoint (`bank_sftp`).
  - Decisions: PostgreSQL 16 migration on port 5432 (`database_engine`), Redis cluster with 3600s TTL and Sentinel failover (`cache_layer`), Kafka 12-partition topic routing (`event_stream`), SHA-256 payload idempotency locks (`idempotency_store`).
  - Pending Tasks: Backup cron unblocking (`backup_cron`), v2 HMAC-SHA256 webhook migration (`webhook_v2`), CAMT.053 settlement batch parser (`settlement_reconciliation`), pgbouncer max-connections increase (`pgbouncer_tuning`).
  Ensure the original 6 claims (`claim-001` through `claim-006`) are preserved with exact IDs for backward compatibility.
- [ ] **Step 4: Update `extractor.py` deterministic rules**
  Add matching extraction patterns for the new fintech items so rule-based extraction works seamlessly alongside Nemotron.
- [ ] **Step 5: Run tests and verify all pass**
  `PYTHONPATH=. pytest tests/test_chunker_and_extractor.py tests/test_evaluation_harness.py -v`
- [ ] **Step 6: Commit changes**
  `git commit -am "feat(data): expand synthetic dataset with realistic fintech payment infrastructure claims"`

---

### Task 2: Successor Runway Categorization & Backlog Fix

**Files:**
- Modify: `backend/app/services/successor.py`
- Test: `tests/test_api_endpoints.py`

- [ ] **Step 1: Write test asserting balanced 4-pane distribution**
  In `tests/test_api_endpoints.py`, assert that `/api/v1/successor/view` returns at least 3 items in `panes.landmines`, 3 items in `panes.accounts`, 3 items in `panes.decisions`, and 3 items in `panes.backlog`.
- [ ] **Step 2: Run test to confirm failure**
  `PYTHONPATH=. pytest tests/test_api_endpoints.py -k "test_successor_runway_view" -v`
- [ ] **Step 3: Fix categorization logic in `successor.py`**
  Adjust the categorization order in `build_successor_runway_view`:
  - Check for `task`, `todo`, `cron`, `blocked`, `migration`, `backlog` to route to `backlog` first before general credential checks.
  - Route credentials/keys/deploy secrets to `accounts`.
  - Route workarounds/fallbacks/bugs to `landmines`.
  - Route architecture/database/decisions/superseded items to `decisions`.
- [ ] **Step 4: Run tests and verify all pass**
  `PYTHONPATH=. pytest tests/test_api_endpoints.py -v`
- [ ] **Step 5: Commit changes**
  `git commit -am "fix(successor): balance 4-pane categorization and populate pending tasks backlog"`

---

### Task 3: NVIDIA Nemotron Architecture Q&A & Synthesis Backend Endpoints

**Files:**
- Modify: `backend/app/services/nemotron_client.py`
- Modify: `backend/app/api/endpoints.py`
- Test: `tests/test_nemotron_integration.py`

- [ ] **Step 1: Write test for `POST /api/v1/llm/query`**
  In `tests/test_nemotron_integration.py`, add a test testing `/api/v1/llm/query` with a query like *"What breaks if Redis restarts?"*, asserting response status 200, non-empty answer, grounded citations, and zero canary disclosure under `INTERNAL` clearance.
- [ ] **Step 2: Run test to confirm failure**
  `PYTHONPATH=. pytest tests/test_nemotron_integration.py -k "test_nemotron_llm_query" -v`
- [ ] **Step 3: Implement `query_nemotron_architecture` in `nemotron_client.py`**
  Create function `query_nemotron_architecture(query: str, claims: List[ClaimEntry], clearance: AccessLabel)`:
  - Filters claims by clearance (preventing canary token inclusion in unprivileged prompts).
  - Prompts NVIDIA Nemotron Ultra 550B with strict citation-grounding instructions.
  - Provides deterministic offline fallback when `NVIDIA_API_KEY` is not present or API call fails.
- [ ] **Step 4: Register `POST /api/v1/llm/query` endpoint in `endpoints.py`**
  Expose the query endpoint with Pydantic request model (`query`, optional `clearance`).
- [ ] **Step 5: Run tests and verify all pass**
  `PYTHONPATH=. pytest tests/test_nemotron_integration.py -v`
- [ ] **Step 6: Commit changes**
  `git commit -am "feat(api): add NVIDIA Nemotron grounded architecture query endpoint"`

---

### Task 4: Interactive Successor Runway UI with Nemotron Copilot & Tactile Actions

**Files:**
- Modify: `frontend/src/components/SuccessorView.tsx`
- Modify: `frontend/src/components/AppLayout.tsx`

- [ ] **Step 1: Enhance `SuccessorView.tsx` with Technical Briefing Panel**
  Add a discreet, obsidian glass card at the top of the Successor View:
  - Header: `Technical Architecture Briefing` with badge `NVIDIA Nemotron Ultra 550B`.
  - "Generate Executive Briefing" button calling `/api/v1/llm/synthesize` with loading spinner.
  - Formatted markdown briefing display with verified citation links.
  - "Query Architecture Ledger" input with 3 clean quick-chips:
    - *"What breaks if Redis restarts?"*
    - *"How do I unblock the backup cron?"*
    - *"Who owns the Stripe webhook secrets?"*
  - Answering area with citation tags linking directly to claims.
- [ ] **Step 2: Add tactile card actions**
  - Gotcha cards: "Acknowledge Hazard" button that toggles to a green checkmark with timestamp.
  - Task & Decision cards: "Copy Command / Snippet" button using navigator.clipboard with toast notification.
  - Add quick category filter pills at the top of the panes (`All Items`, `Gotchas`, `Accounts`, `Decisions`, `Backlog`).
- [ ] **Step 3: Update `AppLayout.tsx` project label and author**
  Update default project label to `Core Payment & Ledger API (Production)` and author to `Alice Chen (Principal Platform Engineer)`. Remove any toy demo phrasing.
- [ ] **Step 4: Build frontend and verify no TypeScript or Vite errors**
  `cd frontend && npm run build`
- [ ] **Step 5: Commit changes**
  `git commit -am "feat(ui): add professional Nemotron architecture copilot and tactile runway actions"`

---

### Task 5: End-to-End Verification & Remote Push

**Files:**
- All modified files
- `frontend/dist/*`

- [ ] **Step 1: Run full pytest test suite**
  `PYTHONPATH=. pytest tests/ -v` (Assert all 34+ tests pass).
- [ ] **Step 2: Verify live local endpoints**
  Verify `/api/v1/successor/view`, `/api/v1/llm/status`, `/api/v1/llm/query`, `/api/v1/llm/synthesize`, and `/` root HTML response.
- [ ] **Step 3: Push changes to GitHub repository**
  `git push origin master`
- [ ] **Step 4: Confirm Render auto-deploy or manual trigger readiness**
