# HandoffLedger: Verifiable Knowledge Handover Pipeline

**HandoffLedger** replaces unverified narrative handover summaries with an evidence-linked claim ledger, a graph-based single-point-of-knowledge (SPOK) risk engine, a permission-enforcing security lattice, and an objective held-out evaluation harness.

---

## System Architecture

```mermaid
flowchart TD
    subgraph Ingestion["1. Ingestion & Pre-Generation Clearance"]
        SRC["Raw Synthetic Data (v1_demo)\n(Git, Discord, Tasks, Meeting Notes)"] --> REDACT["Regex Credential Sanitizer"]
        REDACT --> CHUNK["Chunker & Lattice Labeling\n(PUBLIC / INTERNAL / RESTRICTED)"]
        CHUNK --> DB_CHUNKS[("SQLite Database\n(chunks table)")]
    end

    subgraph Verification["2. Extraction & Hybrid Verification"]
        DB_CHUNKS -->|Clearance Filter| CTX["Clearance-Filtered Context"]
        CTX --> EXTRACT["Claim Extractor & Parser"]
        EXTRACT --> VERIF["Deterministic Python Verifier\n(Substring Matching & Lattice Join)"]
        VERIF --> TEMPORAL["Temporal Progression Resolver\n(t_new > t_old Supersession)"]
        TEMPORAL --> DB_CLAIMS[("SQLite Database\n(claims & citations tables)")]
    end

    subgraph GraphSPOK["3. Graph Risk & Exit Interview"]
        DB_CLAIMS --> GRAPH["NetworkX Graph Engine"]
        GRAPH --> SPOK["SPOK Scoring Algorithm\n(Concentration + StaleDecay + EvidenceWeakness)"]
        SPOK --> NOISE["Centrality Filter (in_degree >= 2)"]
        NOISE --> INTERVIEW["Adaptive Top-10 Exit Interview"]
    end

    subgraph Delivery["4. Delivery & Evaluation"]
        DB_CLAIMS --> RUNWAY["Successor 4-Pane Runway View\n(Landmines, Accounts, Decisions, Backlog)"]
        RUNWAY --> CANARY["Automated Canary Leak Assertions"]
        RUNWAY --> EVAL["Held-Out 20-Question Benchmark"]
    end
```

---

## Core Formulas

### Single-Point-of-Knowledge (SPOK) Formula
$$\text{SPOK}(n) = 0.5 \times \text{Concentration}(n) + 0.25 \times \text{StaleDecay}(n) + 0.25 \times \text{EvidenceWeakness}(n)$$

Where:
- $\text{Concentration}(n)$: Ratio of entity knowledge authored by the departing member ($w(\text{git})=1.0, w(\text{pr})=0.9, w(\text{task})=0.7, w(\text{doc})=0.6, w(\text{chat})=0.5$).
- $\text{StaleDecay}(n) = 1.0 - \exp\left(-\frac{\ln(2)}{60} \cdot \Delta t\right)$ with half-life $t_{1/2} = 60\text{ days}$.
- $\text{EvidenceWeakness}(n)$: Penalty average ($\text{verified}=0.0, \text{inferred}=0.4, \text{conflicting}=0.8, \text{missing\_evidence}=1.0$).
- Centrality Filter: In-degree $< 2$ suppresses peripheral single-commit nodes from heatmaps and interview queues.

---

## Quickstart

### 1. Run Automated Test Suite
```bash
PYTHONPATH=. pytest tests/ -v
```

### 2. Start Backend API
```bash
python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
API Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 3. Start Frontend Dashboard
```bash
cd frontend
npm install
npm run dev
```
Dashboard: [http://127.0.0.1:5173/](http://127.0.0.1:5173/)
