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

- [x] **Step 1: Write tests for expanded fintech claims and citations**
- [x] **Step 2: Run test to confirm failure before implementation**
- [x] **Step 3: Expand `synthetic_data.py` with 16–20 realistic fintech chunks and claims**
- [x] **Step 4: Update `extractor.py` deterministic rules**
- [x] **Step 5: Run tests and verify all pass**
- [x] **Step 6: Commit changes**

---

### Task 2: Successor Runway Categorization & Backlog Fix

**Files:**
- Modify: `backend/app/services/successor.py`
- Test: `tests/test_api_endpoints.py`

- [x] **Step 1: Write test asserting balanced 4-pane distribution**
- [x] **Step 2: Run test to confirm failure**
- [x] **Step 3: Fix categorization logic in `successor.py`**
- [x] **Step 4: Run tests and verify all pass**
- [x] **Step 5: Commit changes**

---

### Task 3: NVIDIA Nemotron Architecture Q&A & Synthesis Backend Endpoints

**Files:**
- Modify: `backend/app/services/nemotron_client.py`
- Modify: `backend/app/api/endpoints.py`
- Test: `tests/test_nemotron_integration.py`

- [x] **Step 1: Write test for `POST /api/v1/llm/query`**
- [x] **Step 2: Run test to confirm failure**
- [x] **Step 3: Implement `query_nemotron_architecture` in `nemotron_client.py`**
- [x] **Step 4: Register `POST /api/v1/llm/query` endpoint in `endpoints.py`**
- [x] **Step 5: Run tests and verify all pass**
- [x] **Step 6: Commit changes**

---

### Task 4: Interactive Successor Runway UI with Nemotron Copilot & Tactile Actions

**Files:**
- Modify: `frontend/src/components/SuccessorView.tsx`
- Modify: `frontend/src/components/AppLayout.tsx`

- [x] **Step 1: Enhance `SuccessorView.tsx` with Technical Briefing Panel**
- [x] **Step 2: Add tactile card actions**
- [x] **Step 3: Update `AppLayout.tsx` project label and author**
- [x] **Step 4: Build frontend and verify no TypeScript or Vite errors**
- [x] **Step 5: Commit changes**

---

### Task 5: End-to-End Verification & Remote Push

**Files:**
- All modified files
- `frontend/dist/*`

- [x] **Step 1: Run full pytest test suite**
- [x] **Step 2: Verify live local endpoints**
- [x] **Step 3: Push changes to GitHub repository**
- [x] **Step 4: Confirm Render auto-deploy or manual trigger readiness**
