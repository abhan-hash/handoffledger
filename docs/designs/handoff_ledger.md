# HandoffLedger: Knowledge Handover Pipeline

*   **Author:** Abhan
*   **Status:** Draft
*   **Date:** 2026-11-10

--------------------------------------------------------------------------------

## Overview

HandoffLedger is a verifiable knowledge handover platform engineered for student technical clubs, small software teams, and open-source project groups. It replaces unverified narrative documentation with an evidence-linked claim ledger, a graph-based single-point-of-knowledge (SPOK) risk engine, a permission-enforcing security lattice, and an objective held-out evaluation harness. 

The system reconstructs project state from disparate activity traces (commits, task trackers, chat discussions, meeting notes), flags epistemic uncertainty across four distinct evidence states (`verified`, `inferred`, `conflicting`, `missing evidence`), interviews departing members on top-ranked knowledge vulnerabilities, enforces pre-generation clearance filtering with automated canary assertions, and equips successors with an actionable 4-pane runway view.

--------------------------------------------------------------------------------

## Problem Statement

When a contributor leaves a technical project, the knowledge they take with them is rarely preserved in the code or existing documentation:
1. **Unrecorded Decision Rationale**: Wikis document what was built, but rarely why a specific architecture, library, or workaround was selected.
2. **Epistemic Masking in Generative Prose**: Narrative handover summaries mask uncertainty with fluent text, presenting unverified guesses and factual conclusions with identical confidence.
3. **Data Leakage in Handover Sharing**: Broad documentation dumps expose confidential credentials, internal server configurations, or private communication to successors who lack clearance.
4. **Questionnaire Fatigue**: Departing members short on time abandon long, open-ended handover questionnaires, leaving critical bottlenecks undocumented.
5. **Lack of Measurable Completeness**: Teams have no objective metric to quantify handover quality, leaving leadership blind to dangerous operational knowledge gaps until a critical system breaks.

--------------------------------------------------------------------------------

## Goals & Non-Goals

### Goals
*   **Evidence-Linked Claim Ledger**: Decompose project knowledge into atomic claims bound to verbatim source citations and tagged with four explicit evidence states (`verified`, `inferred`, `conflicting`, `missing evidence`).
*   **Deterministic SPOK Risk Scoring**: Compute single-point-of-knowledge vulnerability scores per graph entity using:
    $$\text{SPOK}(n) = 0.5 \times \text{Concentration}(n) + 0.25 \times \text{StaleDecay}(n) + 0.25 \times \text{EvidenceWeakness}(n)$$
*   **Adaptive Top-10 Exit Interview**: Execute a focused 10-question sprint targeting high-risk, weak-evidence gaps using a draft-and-verify recognition model that minimizes departing member cognitive load.
*   **Pre-Generation Security Lattice**: Enforce strict chunk-level clearance filtering prior to LLM extraction, propagate labels via lattice join ($\mathcal{L}(c) = \bigsqcup \mathcal{L}(k)$), preserve structural redacted placeholders, and assert zero leakage via automated canary test suites.
*   **Quantitative Handover Evaluation**: Evaluate handover completeness against 20 gold-standard ground-truth questions on fixed dataset `v1_demo`, measuring accuracy gain and token efficiency delta against an unorganized raw source baseline.
*   **Operational Successor Runway**: Deliver a role-appropriate 4-pane successor dashboard (Active Landmines, Account Ownership, Decision Rationale, Immediate Backlog) enabling day-1 continuation.

### Non-Goals
*   **Live Third-Party Webhooks & Connectors**: No live GitHub OAuth or Discord bot integrations for Round 2; ingestion operates on static structured JSON and Markdown archives.
*   **Autonomous Semantic Conflict Resolution**: The system detects contradictions and surfaces them side-by-side; resolution authority remains strictly with human reviewers and departing members.
*   **Export Formatting Engines**: Automated PDF/A generation and external presentation publishing are excluded from Round 2 scope.
*   **Unconstrained Pairwise LLM Comparisons**: No $O(N^2)$ cross-claim LLM comparisons; semantic checks are strictly bounded to candidate claim pairs grouped by entity attribute and overlapping timestamps.
*   **Tamper-Evident Hash Chains**: Cryptographic audit log chaining is deferred to Round 3 hardening.

--------------------------------------------------------------------------------

## Open Questions

*   **Question 1**: How should the successor view represent claims whose status transitioned to `superseded` when an incoming member audits historical decisions?
*   **Question 2**: In sudden exit scenarios where no interview occurs, what specific heuristic weights should govern the automated "who to ask" routing table?

--------------------------------------------------------------------------------

## Critical User Journeys (CUJs)

### CUJ 1: Scheduled Departure with Adaptive Gap Interview
*   **Given**: A lead backend maintainer plans to step down in 5 days; repository commits, task boards, and chat logs have been ingested and verified.
*   **When**: The maintainer opens HandoffLedger and initiates the exit interview.
*   **Then**: The system presents 10 pre-drafted candidate hypotheses targeting high-SPOK entities; the maintainer confirms, edits, or refutes them in under 15 minutes; answered claims immediately upgrade to `verified` and update downstream graph scores.

### CUJ 2: Reviewer Triage & Batch Approval
*   **Given**: A club president reviews a drafted handover containing 35 extracted claims.
*   **When**: The president opens the Reviewer Staging Dashboard.
*   **Then**: Claims with multiple independent commit citations and `verified` status appear pre-grouped for one-click batch approval; the reviewer focuses review time solely on `conflicting` and `inferred` claims before publishing the handover.

### CUJ 3: Successor Day-1 Onboarding with Role-Restricted Context
*   **Given**: An incoming member with `INTERNAL` clearance takes ownership of the backend service.
*   **When**: The successor logs into the dashboard.
*   **Then**: The 4-pane runway displays active workarounds, unrecorded decision rationales, and next actions; restricted deployment keys appear as structural redacted placeholders (`[RESTRICTED CLAIM: Access Clearance 'RESTRICTED' Required. Contact Lead.]`) without leaking credentials or canary tokens.

--------------------------------------------------------------------------------

## Proposed Architecture

### 1. High-Level Architecture & End-to-End Pipeline

The HandoffLedger execution architecture divides responsibilities strictly between a generative language model and a deterministic Python runtime:

```mermaid
flowchart TD
    subgraph S1["1. Ingestion & Pre-Generation Clearance"]
        SRC["Raw Synthetic Data (v1_demo)\n(Git log, Discord JSON, Tasks, Notes)"] --> REDACT["Regex Credential Sanitizer\n(Tokens, Keys, PII)"]
        REDACT --> CHUNK["Chunker & Lattice Labeling\n(Public / Internal / Restricted)"]
        CHUNK --> DB_CHUNKS[("SQLite Database\n(chunks table)")]
    end

    subgraph S2["2. Extraction & Hybrid Verification"]
        DB_CHUNKS -->|Clearance Filter: L(k) <= Clearance(User)| CTX["Clearance-Filtered Context"]
        CTX --> LLM_EXT["LLM Claim Extractor\n(Strict JSON Schema)"]
        LLM_EXT --> PY_VERIF["Deterministic Python Verifier\n(Substring Matching & Lattice Join)"]
        PY_VERIF --> TEMP_RES["Temporal Attribute Resolver\n(t_new > t_old Supersession)"]
        TEMP_RES --> BOUND_LLM["Bounded LLM Semantic Check\n(Candidate Non-Temporal Pairs Only)"]
        BOUND_LLM --> DB_CLAIMS[("SQLite Database\n(claims & citations tables)")]
    end

    subgraph S3["3. Graph Risk & Exit Interview"]
        DB_CLAIMS --> GRAPH_ENG["NetworkX Graph Engine"]
        GRAPH_ENG --> SPOK_CALC["SPOK Scoring Algorithm\n(Concentration + Decay + Weakness)"]
        SPOK_CALC --> NOISE_FILT["Centrality Filter\n(in_degree >= 2 for Heatmap)"]
        NOISE_FILT --> TOP10_QUEUE["Adaptive Top-10 Exit Interview\n(Draft-and-Verify Micro-Forms)"]
        TOP10_QUEUE -->|Departing Member Resolutions| PY_VERIF
    end

    subgraph S4["4. Review, Delivery & Benchmark Evaluation"]
        NOISE_FILT --> HEATMAP_UI["Interactive Risk Heatmap UI"]
        DB_CLAIMS --> REVIEW_DASH["Reviewer Staging Dashboard\n(Batch Verified / Manual Conflicting)"]
        REVIEW_DASH --> SUCC_VIEW["Successor 4-Pane Runway View\n(Structural Redacted Placeholders)"]
        SUCC_VIEW --> CANARY_TEST["Automated Canary Leak Assertions"]
        SUCC_VIEW --> EVAL_HARNESS["Held-Out 20-Question Evaluation\n(Accuracy & Token Delta on v1_demo)"]
    end
```

### 2. Subsystem Specifications

#### 2.1 Ingestion & Pre-Generation Security Engine
*   **Credential Sanitizer (`redactor.py`)**: Runs before chunk storage. Applies pre-compiled regex passes targeting standard high-entropy credentials, replacing matches with pattern-specific tags (`[REDACTED_OPENAI_KEY]`, `[REDACTED_GITHUB_TOKEN]`, `[REDACTED_AWS_KEY]`, `[REDACTED_JWT_TOKEN]`).
*   **Chunker (`chunker.py`)**: Breaks raw sources into atomic, immutable chunks with deterministic SHA-256 identifiers, tracking file paths, character offsets (`char_start`, `char_end`), author identity, access label, and ISO-8601 timestamps.
*   **Security Lattice & Clearance Filter (`clearance.py`)**: Labels obey the strict 4-tier partial order:
    $$\mathcal{L} = \{ \text{PUBLIC} (0) \prec \text{INTERNAL} (1) \prec \text{LEAD_ONLY} (2) \prec \text{RESTRICTED} (3) \}$$
    - *Phase 1 (Canonical Ingestion & Extraction)*: The pipeline ingests sources and extracts atomic claims with canonical system clearance, tagging each chunk and claim with its least-upper-bound lattice join label $\mathcal{L}(c) = \bigsqcup \mathcal{L}(k)$.
    - *Phase 2 (Query Context & Successor Projection)*: When generating prompts for LLM querying or rendering successor views for a viewer with clearance $R$, unprivileged chunks ($\mathcal{L}(k) \not\preceq R$) are strictly excluded from prompt context, and inaccessible claims are projected into structural redacted placeholders.

#### 2.2 Extraction & Hybrid Verification Pipeline
*   **Structured Extractor (`extractor.py`)**: Parses chunks into structured factual statements bound to Pydantic schemas. Claims cite exact chunk identifiers and verbatim quote spans.
*   **Deterministic Python Verifier (`verifier.py`)**:
    1.  *Substring Match Assertion*: Verifies that `citation.quote_span in chunk.content`. Any claim failing substring validation or referencing nonexistent chunks is immediately flagged as `missing evidence`.
    2.  *Lattice Label Inheritance*: Asserts that `claim.effective_label == max(chunks[c].access_label for c in claim.citations)`.
*   **Temporal Progression Resolver (`temporal.py`)**:
    Claims targeting the same entity and attribute key (e.g., `(backend_service, database_driver)`) are sorted chronologically by source timestamp. If a newer claim ($t_{\text{new}} > t_{\text{old}}$) establishes an updated state, the older claim is automatically updated to `state = ClaimState.SUPERSEDED` with an audit record in `version_history`, eliminating false-positive contradiction alerts.
*   **Bounded Semantic Contradiction Pass (`contradiction.py`)**:
    Evaluates candidate claim pairs targeting the same entity attribute within a 24-hour operational window using deterministic attribute and state rules, bounding candidate pairs to $O(K)$ where $K \ll N^2$.

#### 2.3 Graph Engine & Mathematical SPOK Risk Formulation
*   **Graph Model (`graph_service.py`)**: Models project entities as nodes (`PERSON`, `COMPONENT`, `ACCOUNT`, `DECISION`, `TASK`) and dependencies between entities as directed edges. Claims map to entities and cite chunks:
    $$\text{Chunks}(n) = \{ k \in \text{Chunks} \mid \exists c \in \text{Claims}(n) \text{ s.t. } k \in c.\text{citations} \}$$
*   **Single-Point-of-Knowledge Equation (`spok.py`)**:
    $$\text{SPOK}(n) = 0.5 \times \text{Concentration}(n) + 0.25 \times \text{StaleDecay}(n) + 0.25 \times \text{EvidenceWeakness}(n)$$
    
    1.  **Concentration ($C_n \in [0, 1]$)**:
        $$C_n = \frac{\sum_{k \in \text{Chunks}(n)} \mathbb{I}(\text{author}(k) = \text{leaver}) \cdot w(\text{type}(k))}{\sum_{k \in \text{Chunks}(n)} w(\text{type}(k))}$$
        Where $\mathbb{I}(\cdot)$ is the binary indicator function. Source authority weights: $w(\text{git}) = 1.0$, $w(\text{pr}) = 0.9$, $w(\text{task}) = 0.7$, $w(\text{doc}) = 0.6$, $w(\text{chat}) = 0.5$. Boundary: $C_n = 0.0$ if $\text{Chunks}(n) = \emptyset$.
    2.  **Stale Decay ($D_n \in [0, 1]$)**:
        $$D_n = 1.0 - \exp\left(-\frac{\ln(2)}{t_{1/2}} \cdot \Delta t_n\right), \quad t_{1/2} = 60 \text{ days}$$
        Where $\Delta t_n = (t_{\text{now}} - \max_{k \in \text{Chunks}(n)} t_k) / 86400 \text{ seconds}$.
    3.  **Evidence Weakness ($W_n \in [0, 1]$)**:
        $$W_n = \frac{1}{|\mathcal{C}_n|} \sum_{c \in \mathcal{C}_n} \text{Penalty}(\text{state}(c))$$
        Discrete state penalties: $\text{verified} = 0.0$, $\text{superseded} = 0.2$, $\text{inferred} = 0.4$, $\text{conflicting} = 0.8$, $\text{missing evidence} = 1.0$. Boundary: $W_n = 1.0$ if $|\mathcal{C}_n| = 0$.
*   **Centrality Filter & Interview Ranking**:
    -   *Noise Filtering*: Nodes with $(\text{deg}_{\text{in}}(n) < 2) \land (\text{chunk\_count} \le 1)$ are flagged with `is_filtered_from_heatmap = True` to suppress peripheral noise from the visual heatmap.
    -   *Priority Queue*:
        $$\text{Priority}(n) = \text{SPOK}(n) \times (1.0 + \log(1 + \text{deg}_{\text{in}}(n)))$$
        High-SPOK nodes ($\text{SPOK}(n) \ge 0.5$) are retained in the exit interview candidate pool regardless of in-degree to ensure single-maintainer bottlenecks are never suppressed. The top 10 ranked nodes populate the exit interview.

#### 2.4 Adaptive Exit Interview Engine (`interview.py`)
*   **Draft-and-Verify Recognition**: The system pre-synthesizes candidate recognition hypotheses from commit messages and chat fragments.
*   **Action Handlers**: The departing contributor selects `Confirm`, `Edit`, or `Refute`. Confirmations immediately upgrade claims to `verified` with the leaver as source; resolving a node dynamically re-computes downstream SPOK scores in real time.

#### 2.5 Successor 4-Pane Presentation & Canary Testing
*   **Four Cognitive Panes (`successor.py`)**:
    1.  *Active Landmines & Workarounds*: Claims with `attribute_key in ['workaround', 'known_issue', 'gotcha']` or `state == CONFLICTING`.
    2.  *Account & Key Ownership*: Entities of type `ACCOUNT` or claims targeting access credentials.
    3.  *Decision Rationale*: Entities of type `DECISION` or claims explaining architectural trade-offs.
    4.  *Next Actions Backlog*: Entities of type `TASK` and unverified/inferred items requiring immediate continuation.
*   **Redacted Placeholders**: Inaccessible items render as structural stubs (`[RESTRICTED CLAIM: Access Clearance '<label>' Required. Contact Lead.]`), preserving dependency context without disclosing payload data.
*   **Canary Leakage Assertions (`tests/test_canary_leakage.py`)**:
    Automated pytest test suite asserts zero occurrences of planted high-entropy canary UUIDs across generation prompts, successor API responses, and server logs.

#### 2.6 Held-Out Evaluation Harness (`evaluation.py`)
*   **Benchmark Baseline**: Evaluated against fixed synthetic dataset `v1_demo`.
*   **Gold-Standard Test Suite**: 20 hand-crafted questions evaluating decision recall, operational troubleshooting, and credential rotation, including negative control canary probes.
*   **Metric Delta**:
    $$\Delta_{\text{Handover}} = \text{Accuracy}_{\text{SuccessorView}} - \text{Accuracy}_{\text{RawBaseline}}$$

### 3. Data Models & Entity Schemas (SQLAlchemy 2.0 & Pydantic)

```python
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class AccessLabel(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    RESTRICTED = "RESTRICTED"

class ClaimState(str, Enum):
    VERIFIED = "verified"
    INFERRED = "inferred"
    CONFLICTING = "conflicting"
    MISSING_EVIDENCE = "missing evidence"
    SUPERSEDED = "superseded"

class EntityType(str, Enum):
    PERSON = "person"
    COMPONENT = "component"
    ACCOUNT = "account"
    DECISION = "decision"
    TASK = "task"

class SourceType(str, Enum):
    GIT = "git"
    CHAT = "chat"
    TASK = "task"
    DOC = "doc"

class ChunkSchema(BaseModel):
    chunk_id: str
    source_id: str
    source_type: SourceType
    author: str
    timestamp: str
    access_label: AccessLabel
    content: str
    char_start: int
    char_end: int
    has_canary: bool = False

class CitationSchema(BaseModel):
    chunk_id: str
    quote_span: str

class ClaimSchema(BaseModel):
    claim_id: str
    entity_id: str
    attribute_key: Optional[str] = None
    claim_text: str
    state: ClaimState
    effective_label: AccessLabel
    citations: List[CitationSchema]
    created_at: str
    source_timestamp: str
    created_by: str
    reviewer_approved: bool = False
    reviewer_notes: Optional[str] = None

class GraphNodeSchema(BaseModel):
    node_id: str
    name: str
    entity_type: EntityType
    spok_score: float = Field(ge=0.0, le=1.0)
    concentration: float
    stale_decay: float
    evidence_weakness: float
    in_degree: int
    interview_priority: float
    is_filtered_from_heatmap: bool = False
```

### 4. API Interface Contract (FastAPI)

| Endpoint | Method | Request Payload | Response Model | Description |
| :--- | :--- | :--- | :--- | :--- |
| `/api/v1/ingest` | `POST` | `multipart/form-data` | `IngestSummary` | Uploads project archives, applies regex sanitization, stores chunks. |
| `/api/v1/extract` | `POST` | `ExtractRequest` | `List[ClaimSchema]` | Triggers LLM extraction filtered by user clearance context. |
| `/api/v1/verify` | `POST` | `None` | `VerificationReport` | Runs deterministic substring check, label inheritance, and temporal supersession. |
| `/api/v1/graph/spok` | `GET` | `None` | `GraphResponse` | Returns nodes, edges, SPOK scores, and heatmap centrality filter flags. |
| `/api/v1/interview/queue`| `GET` | `None` | `List[InterviewQuestion]`| Fetches the Top-10 prioritized exit interview questions. |
| `/api/v1/interview/answer`| `POST`| `InterviewAnswer` | `ClaimSchema` | Ingests leaver answers and recalculates downstream SPOK scores in real time. |
| `/api/v1/review/claims` | `GET` | `status_filter` | `List[ClaimSchema]` | Returns staging table with auto-batched verified claims. |
| `/api/v1/review/decide` | `POST` | `ReviewDecision` | `ClaimSchema` | Approves, edits, or rejects claims. |
| `/api/v1/handover/view` | `GET` | `None` | `SuccessorRunwayView` | Returns 4-pane action dashboard with redacted placeholders. |
| `/api/v1/evaluate` | `POST` | `EvalRequest` | `EvalResult` | Runs 20 held-out questions against successor view vs raw baseline on `v1_demo`. |

--------------------------------------------------------------------------------

## Alternatives Considered

### Alternative A: Monolithic Generative Handover Summary
*   **Pros**: Single LLM prompt execution; zero pipeline orchestration; simple text UI output.
*   **Cons**: Epistemic masking hides evidence gaps; hallucinates missing rationales; lacks verbatim citations; impossible to verify provenance.
*   **Reason for Rejection**: Fails the fundamental requirement of epistemic auditability. Narrative summaries mask evidence gaps and incoming members cannot distinguish grounded repository truth from generative hallucination.

### Alternative B: Post-Generation Output Redaction
*   **Pros**: Standard web-application security pattern; easy regex/string scrubbing on final responses.
*   **Cons**: Sensitive source material enters the LLM prompt and context window; exposes internal credentials and restricted conversations to model provider logs; wastes token budget on inaccessible material.
*   **Reason for Rejection**: Violates lattice access guarantees. Clearance must be enforced before generation so restricted chunks never enter LLM prompt context.

### Alternative C: Pure LLM Claim Verifier
*   **Pros**: Accommodates fuzzy semantic alignment and natural language paraphrasing without rigid string matching.
*   **Cons**: Correlated hallucination when the same model family grades its own outputs; non-deterministic evaluation breaks automated CI assertions; adds latency and API cost.
*   **Reason for Rejection**: Verifying quote-span citations and lattice label inheritance must be deterministic and fully reproducible in Python.

### Alternative D: Unconstrained Exhaustive Handover Questionnaire (50+ Questions)
*   **Pros**: Captures every component and peripheral dependency in the project.
*   **Cons**: Severe questionnaire fatigue; departing contributors short on time abandon the questionnaire, resulting in zero captured context.
*   **Reason for Rejection**: An adaptive top-10 priority queue driven by SPOK risk and recognition-based draft-and-verify micro-forms captures maximum critical context within realistic time constraints.

### Alternative E: Unfiltered Graph Heatmap Visualization
*   **Pros**: Exhaustive representation of every touched file, single-line commit, and contributor in repository history.
*   **Cons**: Overwhelms the UI with hundreds of trivial, peripheral single-touch nodes; obscures true single-point-of-failure bottlenecks.
*   **Reason for Rejection**: Enforcing an in-degree and chunk filter suppresses peripheral noise from the visual heatmap while preserving true dependency bottlenecks.

--------------------------------------------------------------------------------

## Risks & Mitigations

| Risk Domain | Potential Failure Mode | Severity | Technical Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **Generative Hallucination** | LLM fabricates architectural rationale or attributes decisions to wrong individuals. | Blocker | Enforce deterministic Python quote-span verification (`quote_span in chunk.content`) and character offsets. Claims lacking verbatim citations are demoted to `missing evidence`. |
| **Data Leakage in Handover** | Sensitive credentials or private discussions disclosed to unprivileged successors. | Blocker | Pre-generation clearance filtering purges restricted chunks before LLM context compilation. Inaccessible claims render as structural placeholders (`[RESTRICTED CLAIM: ...]`). Automated CI canary assertions verify zero leakage. |
| **Departing Contributor Dropout** | Departing person abandons open-ended handover questionnaires due to cognitive fatigue. | Major | Top-10 SPOK priority ranking focuses strictly on highest-risk gaps. Draft-and-verify recognition model reduces effort to one-click Confirm/Edit/Refute actions. |
| **Token Budget & Rate Limits** | Large source repositories exceed LLM context windows or trigger HTTP 429 rate limits. | Major | Chunk batching (100-chunk limits), rule-based extraction fast-paths, and local deterministic verification avoid unnecessary LLM round-trips. |
| **Storage & Concurrency Limits** | SQLite database file contention during parallel ingestion. | Minor | Synchronous SQLite database with SQLAlchemy 2.0 ORM; declarative schemas preserve immediate portability for cloud PostgreSQL migration. |

--------------------------------------------------------------------------------

## Non-Functional Requirements

### 1. Security & Privacy
*   **Strict Pre-Generation Clearance Isolation**: Chunks tagged `INTERNAL` or `RESTRICTED` must never enter the model prompt context for a viewer lacking appropriate clearance.
*   **Zero Leakage Assertions**: Unit tests assert zero occurrences of high-entropy canary UUIDs in prompt compilations, API responses, client DOM renders, and server logs.
*   **Read-Only Boundary**: Ingestion pipelines access source archives strictly as read-only inputs; no writes or mutations are committed back to source repositories.

### 2. Performance & Latency
*   **Bounded Verification Runtime**: By resolving temporal supersession in Python and restricting LLM semantic checks to candidate attribute-matched pairs, contradiction checking executes in under 5 seconds for a 50-claim ledger.
*   **Graph Query Scaling**: SPOK calculations on NetworkX for graphs up to 5,000 nodes execute in under 150ms in Python.

### 3. Reliability & Dual-Dialect Storage
*   **Reliable Storage Engine**: Synchronous SQLite for zero-configuration hackathon demonstration and local evaluation; SQLAlchemy 2.0 declarative ORM models preserve full schema portability for PostgreSQL cloud deployments.

--------------------------------------------------------------------------------

## Detailed Implementation Plan

### Target Files to Create/Modify

#### 1. Backend Core & Configuration
1.  `backend/pyproject.toml` (Create): Defines backend dependencies (`fastapi`, `uvicorn`, `sqlalchemy>=2.0`, `pydantic>=2.0`, `networkx`, `pytest`, `httpx`, `python-multipart`).
2.  `backend/app/config.py` (Create): Pydantic Settings class loading environment variables (`DATABASE_URL`, `OPENAI_API_KEY`, `CORS_ORIGINS`, `CANARY_SEED`).
3.  `backend/app/core/database.py` (Create): SQLAlchemy 2.0 asynchronous and synchronous engine initializers, session factory, and declarative table schema metadata.
4.  `backend/app/models/db_models.py` (Create): SQLAlchemy ORM table definitions for `chunks`, `claims`, `citations`, `graph_nodes`, and `interview_answers`.
5.  `backend/app/models/schemas.py` (Create): Pydantic V2 schemas for entities, extraction prompt JSON contracts, API request/response payloads, and evaluation models.
6.  `backend/app/main.py` (Create): FastAPI application bootstrap, route mounting, CORS middleware configuration, and global error handling.

#### 2. Ingestion, Security & Extraction Services
7.  `backend/app/services/redactor.py` (Create): Regex-based credential sanitizer stripping OpenAI, GitHub, AWS, and generic JWT credentials prior to chunk storage.
8.  `backend/app/services/chunker.py` (Create): Ingests JSON/Markdown archives, creates atomic chunks, derives persistent SHA-256 IDs, and attaches security labels.
9.  `backend/app/services/clearance.py` (Create): Evaluates security lattice $\mathcal{L}$, filtering chunks before LLM prompt compilation.
10. `backend/app/services/extractor.py` (Create): LLM client executing strictly structured extraction prompts with JSON output constraints.

#### 3. Verification & Graph Services
11. `backend/app/services/verifier.py` (Create): Deterministic citation verification checking exact quote spans, character offsets, and lattice join inheritance.
12. `backend/app/services/temporal.py` (Create): Groups claims by `(entity_id, attribute_key)` and resolves chronological state transitions ($t_{\text{new}} > t_{\text{old}}$ marks older claims as `superseded`).
13. `backend/app/services/contradiction.py` (Create): Bounded LLM semantic contradiction pass evaluating candidate claim pairs targeting the same attribute.
14. `backend/app/services/graph_service.py` (Create): Constructs NetworkX directed graphs from chunks and claims, computing degree metrics and adjacency relationships.
15. `backend/app/services/spok.py` (Create): Computes Concentration, Stale Decay, Evidence Weakness, and In-Degree Priority, applying the in-degree $< 2$ centrality filter.
16. `backend/app/services/interview.py` (Create): Manages Top-10 adaptive exit interview queue, generates recognition hypotheses, and recalculates downstream SPOK scores upon answer ingestion.
17. `backend/app/services/successor.py` (Create): Renders the 4-pane successor runway view and inserts structural redacted placeholders for inaccessible items.
18. `backend/app/services/evaluation.py` (Create): Evaluates the 20 held-out questions on `v1_demo`, computing accuracy deltas against raw source baselines.
19. `backend/app/api/endpoints.py` (Create): FastAPI route handlers exposing the 10 interface endpoints.

#### 4. Synthetic Datasets & Ground Truth Fixtures
20. `data/synthetic/v1_demo/git_log.json` (Create): Synthetic git commit history with unrecorded decisions, maintainer departures, and planted canary tokens.
21. `data/synthetic/v1_demo/discord_export.json` (Create): Synthetic chat logs containing workarounds, contradictory statements, and internal server configurations.
22. `data/synthetic/v1_demo/tasks_export.json` (Create): Synthetic task board entries with incomplete assignments and missing evidence.
23. `data/synthetic/v1_demo/meeting_notes.md` (Create): Synthetic architecture meeting notes with tagged access labels (`PUBLIC`, `INTERNAL`, `RESTRICTED`).
24. `data/synthetic/v1_demo/golden_eval_questions.json` (Create): 20 pre-written ground truth benchmark questions with negative control canary probes.

#### 5. Frontend Client (React + Tailwind CSS)
25. `frontend/package.json` (Create): Vite, React 18, TypeScript, Tailwind CSS, Lucide-React, and D3/SVG dependencies.
26. `frontend/src/App.tsx` (Create): Single-page shell with navigation tabs, role clearance selector (`PUBLIC`, `INTERNAL`, `ADMIN`), and leaver/successor views.
27. `frontend/src/components/RiskHeatmap.tsx` (Create): Interactive risk heatmap rendering nodes color-coded by SPOK score with centrality filtering toggle.
28. `frontend/src/components/ExitInterview.tsx` (Create): Top-10 recognition micro-interview interface featuring candidate hypotheses and Confirm/Edit/Refute actions.
29. `frontend/src/components/ReviewerStaging.tsx` (Create): Reviewer dashboard featuring auto-batched verified claims and focused manual triage for conflicting items.
30. `frontend/src/components/SuccessorRunway.tsx` (Create): 4-pane action dashboard (Landmines, Accounts, Decisions, Backlog) with structural redacted cards.
31. `frontend/src/components/EvaluationDashboard.tsx` (Create): Evaluation dashboard showing 20-question benchmark accuracy delta and token reduction metrics.

#### 6. Test Suite
32. `tests/test_verifier.py` (Create): Unit tests validating exact substring matching, citation offset validity, and lattice join inheritance.
33. `tests/test_temporal.py` (Create): Unit tests validating attribute grouping and temporal supersession logic.
34. `tests/test_spok_math.py` (Create): Unit tests asserting SPOK mathematical bounds, decay curves, and centrality filter behavior.
35. `tests/test_canary_leakage.py` (Create): Automated assertions verifying zero canary leakage across prompt, API, DOM, and log sinks.
36. `tests/test_evaluation_harness.py` (Create): Integration test running the 20-question held-out benchmark on `v1_demo`.
37. `README.md` (Modify): Documents system architecture, quickstart execution, and test execution instructions.

--------------------------------------------------------------------------------

## Verification Plan

### 1. Build & Linting Verification
*   **Backend Lint & Typing**: `ruff check backend/` and `mypy backend/` validating Python type hints and Pydantic V2 models.
*   **Frontend Compilation**: `npm run build` validating TypeScript types and Vite bundling.

### 2. Automated Test Execution
*   **Unit Tests**: `pytest tests/test_verifier.py tests/test_temporal.py tests/test_spok_math.py` ensuring 100% pass rate on algorithmic math and verification rules.
*   **Security Leakage Suite**: `pytest tests/test_canary_leakage.py` validating that canary secrets never appear in prompt context, API outputs, DOM strings, or logs.
*   **Benchmark Evaluation**: `pytest tests/test_evaluation_harness.py` asserting that handover accuracy exceeds raw baseline accuracy ($\Delta_{\text{Handover}} > 0$).

--------------------------------------------------------------------------------

*Drafted with EGM*
