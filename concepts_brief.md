# HandoffLedger: Knowledge Handover Pipeline

* **Author:** Abhan
* **Date:** 2026-11-10

## Overview

When team members leave student technical clubs, small software teams, or open-source projects, critical tacit knowledge departs with them. Narrative documentation like wikis and last-minute handover notes is rarely what a successor needs: it captures decisions after the fact, obscures epistemic uncertainty behind confident text, risks exposing confidential credentials or private notes, and offers no measurable verification that the successor can continue the work.

HandoffLedger replaces narrative handover summaries with a verifiable claim ledger tied to a knowledge-risk graph and a permission-enforcing propagation engine. The system ingests disparate project traces (git commits, issue trackers, chat exports, meeting notes), sanitizes high-entropy credentials, applies pre-generation access clearance filtering, extracts atomic claims bound to verbatim source citations with four distinct evidence states (`verified`, `inferred`, `conflicting`, `missing evidence`), verifies citation fidelity using deterministic Python logic, calculates a single-point-of-knowledge (SPOK) risk score per graph node, conducts a focused top-10 gap interview with the departing member, enforces role-based access with redacted placeholders verified by automated canary assertions, and evaluates handover completeness against a held-out question harness.

## Analysis

### 1. Hybrid Execution Engine (LLM + Python)
* **LLM Allocation**: The LLM is restricted strictly to unstructured text extraction into schema-bound claims and formulating exit-interview question hypotheses.
* **Deterministic Python Allocation**: All security-critical, mathematical, and algorithmic operations run exclusively in deterministic Python:
  - Pre-generation access label filtering against the security lattice ($\mathcal{L}$).
  - Character-level verbatim quote-span citation checking (`quote_span in chunk.content`).
  - Label inheritance lattice propagation ($\mathcal{L}(c) = \bigsqcup_{k \in \text{Citations}(c)} \mathcal{L}(k)$).
  - SPOK graph scoring and priority ranking.
  - Automated canary string leakage assertions across prompts, API responses, DOM rendering, and logs.

### 2. Contradiction Detection & Temporal Resolution
* **Temporal Progression Resolution**: Historical state changes are not static contradictions. Python groups extracted claims by entity attribute (e.g., `db_type`, `lead_owner`, `service_port`). For claims touching the same attribute, timestamp ordering ($t_{\text{new}} > t_{\text{old}}$) marks the older claim as `superseded` rather than `conflicting`.
* **Bounded Semantic Contradiction Pass**: To prevent $O(N^2)$ LLM cost and latency explosions, the LLM contradiction pass executes *only* on remaining non-temporal claim pairs that share identical entity targets within overlapping temporal windows.

### 3. Graph Centrality Filtering & Anti-Noise Controls
* **Node Explosion Mitigation**: High-turnover repos with hundreds of minor commits produce peripheral clutter. The graph engine enforces a Python centrality filter:
  - Nodes with an in-degree $< 2$ or limited to minor single-file touch points are excluded from the risk heatmap and interview queue.
  - Nodes are preserved in the underlying adjacency list to maintain transitive dependency integrity without degrading visualization signal.

### 4. Benchmark Integrity & Anti-Gaming Harness
* **Evaluation Baseline**: The synthetic project activity dataset is locked to a deterministic release (`v1_demo`).
* **Golden Ground-Truth Test Suite**: Twenty gold-standard evaluation questions are authored manually against `v1_demo` prior to pipeline runs. The suite incorporates negative control probes targeting restricted canaries, where valid behavior requires refusal or reference to a redacted placeholder.
* **Handover Score Metric**: The metric is quantified as a delta against unorganized raw sources:
  $$\Delta_{\text{Handover}} = \text{Score}_{\text{SuccessorView}} - \text{Score}_{\text{RawBaseline}}$$

### 5. Mathematical Risk Scoring: Single-Point-of-Knowledge (SPOK)
For each entity node $n$ in the knowledge graph:
$$\text{SPOK}(n) = 0.5 \times \text{Concentration}(n) + 0.25 \times \text{StaleDecay}(n) + 0.25 \times \text{EvidenceWeakness}(n)$$

Where:
* **Concentration**: Weighted ratio of contributions authored by the departing member across commits (1.0), pull requests (0.9), task cards (0.7), and chat messages (0.5).
* **StaleDecay**: $1.0 - \exp\left(-\frac{\ln(2)}{t_{1/2}} \cdot \Delta t_n\right)$ with half-life $t_{1/2} = 60 \text{ days}$.
* **EvidenceWeakness**: Penalty average across linked claims (`verified`: 0.0, `inferred`: 0.4, `conflicting`: 0.8, `missing evidence`: 1.0).
* **Interview Priority Index**:
  $$\text{Priority}(n) = \text{SPOK}(n) \times (1.0 + \log(1 + \text{deg}_{\text{in}}(n)))$$
  The top 10 ranked nodes populate the Adaptive Exit Interview.

## Goals vs. Non-Goals

### In-Scope Goals
* **Pre-Generation Access Filtering**: Strict chunk-level clearance enforcement before prompting the extraction LLM.
* **Deterministic Verification Engine**: Python-based substring validation, access label lattice propagation, and temporal progression resolution.
* **4-State Claim Ledger**: Support for `verified`, `inferred`, `conflicting`, and `missing evidence` states with explicit citation links.
* **Deterministic SPOK Scoring Engine**: Graph calculation of concentration, stale decay, evidence weakness, and in-degree priority.
* **Automated Canary Assertion Suite**: Unit tests asserting zero canary token leakage across prompt payloads, API responses, DOM rendering, and logs.
* **Held-Out Evaluation Harness**: 20 pre-curated ground-truth questions evaluating successor view accuracy against raw source baselines on `v1_demo`.
* **Core Web UI**: React-based risk heatmap with centrality filtering, reviewer staging dashboard, leaver gap interview interface, and successor runway view.

### Out-of-Scope Non-Goals
* **Live OAuth Integrations**: No direct GitHub or Discord webhook listeners in Round 2; ingestion uses synthetic structured JSON/Markdown exports.
* **Automated PDF Export**: Handover documents are viewed in-app or via structured JSON export; no print formatting engines.
* **Cryptographic Hash Chaining**: Hash-chained tamper-evident logs deferred to Round 3 hardening.
* **Unconstrained N^2 LLM Contradiction Evaluation**: LLM semantic contradiction checks are restricted to attribute-grouped candidates filtered by Python.

## Alternatives Weighed
* **Single Broad LLM Summarization Prompt**: Rejected by author. Producing monolithic handover prose obscures evidentiary gaps, hallucinates missing rationales, and provides no granular citation verification.
* **Post-Generation Output Redaction**: Rejected by author. Filtering secrets or restricted claims after LLM generation risks prompt leakage, violates lattice security, and wastes token quota on inaccessible material.
* **Pure LLM Claim Verifier**: Rejected by author. Using a secondary LLM call to verify extractions introduces correlated model errors and non-deterministic evaluation. Substring checking and label inheritance must be executed deterministically in Python.
* **Unfiltered Graph Visualization**: Rejected by author. Displaying every single-commit file touch point creates visual noise that hides critical single-point-of-failure bottlenecks.

## Key Decisions & Staging for Next Steps
1. **Decision**: Lock Round 2 deliverables to the static ingestion vertical slice using dataset `v1_demo`.
2. **Decision**: Enforce pure Python execution for verification, SPOK calculation, temporal supersession, and canary assertions; restrict LLMs strictly to claim extraction and interview question formulation.
3. **Decision**: Author 20 gold-standard ground-truth benchmark questions on `v1_demo` prior to system testing.
4. **Staging for `/egm-draft`**: Formalize detailed API contracts, Pydantic schemas, and SQLAlchemy data models in `design_draft.md`.
