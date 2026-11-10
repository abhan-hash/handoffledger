# HandoffLedger: Project Context

**Challenge:** Prevent Critical Knowledge From Leaving With People
**Stage:** Round 1 (The Plan) submitted; Round 2 (The Build) and Round 3 (The Finish) ahead
**Primary focus:** Student tech clubs and small project teams. Extensible to research groups and small workplaces.
**Team:** Abhan (DTU): team lead, backend and data, AI. Stuti Bhatt (CCOEW): frontend and UX, product, evidence.

**One-line pitch:** HandoffLedger turns scattered project activity (commits, chats, notes, tasks) into a handover made of individually checkable claims, finds where critical knowledge depends only on the departing person, interviews them on exactly those gaps, and scores how complete the handover is.

**Core idea in three parts:** a claim ledger, a risk-ranked gap interview, and permission-aware handover views, tied together by a measurable handover score.

---

## 1. Problem Statement

When someone leaves a project, the documents they leave behind are rarely what the next person needs. The real knowledge lives in chat threads, commit history, meeting notes and task boards, and most of it was never written down as a conclusion.

### What gets lost
- Reasoning behind decisions (the "why", not just the "what")
- Unfinished work and its current state
- Hidden dependencies, account ownership and external contacts
- Recurring problems and the workarounds that contain them
- Open questions that were discussed but never resolved

### Why existing documentation fails
- Wikis capture decisions after the fact, if at all, and go stale quickly.
- A generic summary of a repo or chat reads as confident even when the evidence is thin or contradictory.
- Handover notes are written once, at the last minute, by the person with the least time and no idea what the successor needs.
- Broad summaries can expose confidential material to people who should not see it.
- **No handover tells the team how complete it is**, so nobody knows which departures are the most dangerous.

### The exact moment we solve
A team member is leaving a small project team and a named successor must continue their work. The system:
1. Reconstructs project state from authorised sources
2. Marks what is verified and what is not
3. Finds where critical knowledge depends only on the departing person
4. Asks them to fill those gaps first
5. Lets a reviewer approve the result
6. Shares a role-appropriate view with the successor
7. Scores how complete the handover is

### Evidence the problem is real
- Phaladi and Ngulube (2024), South African public enterprises: tacit knowledge loss is largely caused by voluntary and involuntary turnover combined with a lack of retention strategies. *SA Journal of Human Resource Management, 22*, doi:10.4102/sajhrm.v22i0.2229.
- Yapabandara and Divakara (2025), Sri Lankan banking sector: examined how tacit knowledge is lost during staff exits and why formal transfer processes and documentation fall short. *Sri Lanka Journal of Management Studies*, doi:10.4038/sljms.v7i1.169.
- Ismail and Shaikh Ali: describe what a departing person takes as both what they know about their tasks and who they know and work with; handover is hard when knowledge is tacit and data is unstructured.
- These studies come from larger organisations. Student clubs and volunteer teams have faster turnover and fewer formal processes, so the problem is sharper there. Our own structured interviews with club and project leads are planned for Round 2 testing and will be reported in the Round 2 document.

---

## 2. Users Affected

| User | Situation | What they need |
|---|---|---|
| Departing member | Leaving a club, internship, project or team; short on time | A fast way to transfer knowledge, asked only the questions that matter, without writing a long document from scratch |
| Incoming member | Takes over ownership with little context | Ownership, risks, open questions and next actions, with proof behind each claim and a way to ask follow-ups after the person has left |
| Reviewer (project lead or mentor) | Responsible for quality of the transition | A way to correct, reject and approve the handover, plus a score showing how complete it is |
| Data owner / admin | Controls who can see which sources | Assurance, backed by automated tests, that restricted material never reaches people without access |

**Departure scenarios:** graduating student leaving a technical club; member rotating to another project; volunteer stepping down from a community project; sudden exit where no handover was planned.

**Environments:** student tech clubs and project teams (primary); research groups and small workplace teams (extension).

---

## 3. Proposed Solution

HandoffLedger turns scattered project activity into a handover made of individually checkable claims, and measures how complete that handover is. It rests on five ideas.

### 3.1 The claim ledger
The handover is not one block of generated prose. Every statement is a **claim** with:
- a **source link** to the commit, message, note or task that supports it
- a **status**: `verified`, `inferred`, `conflicting` or `missing evidence`
- an **owner** who can confirm, correct or reject it
- a **version history**

The system never presents a guess as organisational truth. If two sources disagree, both are shown. If a decision has no recorded reasoning, it is flagged as a gap instead of being invented.

### 3.2 Knowledge-risk graph and risk-ranked gap interview
After reconstruction, the system builds a graph of people, components, accounts, decisions, dependencies and external contacts. Each node gets a **single-point-of-knowledge score**: how much of its evidence exists only through the departing person.

The gap interview is ranked by **risk x weak evidence**, so the departing person is asked the ten questions that matter most, not fifty. Examples:
- "Decision X has no recorded reasoning. Why was it made?"
- "Task Y was last touched three weeks ago. What state is it in?"

Answers become new claims with the departing person recorded as the source. The graph is also shown to the reviewer as a **heat map**.

### 3.3 Permission-aware views with label propagation
- Every ingested item carries an **access label**, and filtering happens **before generation**, so restricted content never enters a model prompt or a view.
- A claim inherits the **most restrictive label** of every source it cites.
- Restricted items appear as **redacted placeholders** that keep structure visible without leaking content.
- The guarantee is tested automatically: **canary strings** planted in restricted sources must never appear in any prompt or view.

### 3.4 Handover quality score
- Hold out a set of questions about the project, answered from the full ledger.
- An agent or a human answers them using **only the successor's view**.
- The share answered correctly is the **handover score**.
- Testing compares "with HandoffLedger" against "raw repository and chat", which turns the impact claim into a number.

### 3.5 Independent verification
A verification step separate from extraction checks that each cited chunk supports its claim and looks for contradicting chunks. Confidence comes from the number and independence of sources and their recency, not from the model's own confidence.

**Outcome:** a reviewed, evidence-linked, role-appropriate continuation plan that the incoming person can acknowledge and start acting on, with a score showing how complete it is.

---

## 4. USPs (What Makes This Different)

1. **Claims, not prose.** Every statement is individually sourced, statused, owned and versioned. Nothing is "just a summary".
2. **Honest uncertainty.** Four evidence states, conflicts shown side by side, gaps flagged instead of invented.
3. **Risk-ranked interview.** Questions ranked by single-point-of-knowledge risk x weak evidence: the top ten, not a long generic form.
4. **Knowledge-risk heat map.** Shows teams where critical knowledge depends on one person, an early warning, not just a handover tool.
5. **Permission-aware by construction.** Filtering before generation, label propagation to derived claims, redacted placeholders, and canary-string tests proving zero leakage.
6. **Measurable handover score.** Held-out questions answered from the successor's view only, compared against the raw repo and chat baseline.
7. **Independent verification.** A separate verifier with its own checks, not the extractor grading itself.
8. **Human in the loop.** Nothing reaches the successor until a reviewer approves; generated content is labelled as such.
9. **Handles the ugly cases.** Sudden exit mode, non-responsive departing person, empty or conflicting sources.

---

## 5. Product Workflow (8 Stages)

1. **Connect.** Admin or departing member uploads or connects authorised sources: repo data, meeting notes, task board export, chat export. Each source is tagged with an access label at ingestion; sensitive patterns (keys, tokens, personal contact details) are redacted. Demo data is synthetic.
2. **Reconstruct.** Extract decisions, owners, responsibilities, dependencies, blockers, recurring problems, open questions and a timeline of key changes.
3. **Verify and graph.** Each extracted item becomes a claim with a source link and evidence status. A separate verifier checks citations and flags contradictions and missing evidence. Claims feed the knowledge-risk graph.
4. **Risk-ranked gap interview.** Departing person answers highest-risk questions first. Answers are stored as new claims. Unanswered questions stay visibly open.
5. **Review.** Reviewer edits, rejects or approves each claim, sees version history and the risk heat map, and approves the handover as a whole.
6. **Handover.** Incoming person gets a role-based view: ownership, risks, dependencies, open questions and a prioritised next-actions plan, each claim linked to its source. They acknowledge receipt, and that is recorded.
7. **Post-exit follow-up (planned for Round 3).** Incoming person sends follow-up questions to the departing person; answers become new claims.
8. **Score.** Handover score computed from held-out questions answered using only the successor's view; shown to reviewer and team lead.

### Failure and edge cases designed for
- **Empty source:** reported as empty, never silently skipped.
- **Conflicting sources:** shown side by side with status `conflicting`.
- **Restricted item for this viewer:** appears as a redacted placeholder, never content.
- **Departing person does not answer:** gaps stay open and lower the handover score.
- **Sudden exit:** no interview, so every claim stays `inferred`; system produces a "who to ask" list from commit and chat history and a prioritised list of what to rediscover first.

---

## 6. Feature List

### Core (committed for the event)
- Source ingestion from file uploads and exports (repo data, notes, task board, chat)
- Extraction of decisions, owners, dependencies, risks, open questions and a timeline
- Claim ledger with citations and four-state evidence status
- Contradiction and missing-evidence flagging
- Reviewer workflow: edit, reject, approve, with version history
- Role-based handover views with access filtering before generation
- Acknowledgement of receipt
- Redaction of sensitive fields (keys, tokens, personal contact details)
- Knowledge-risk graph with single-point-of-knowledge score per node, shown as a heat map, driving gap interview ranking
- Label propagation plus automated canary-string test
- Handover quality score from held-out questions

### Stretch (only if core is stable)
- Live read-only GitHub connection
- Search across the claim ledger
- Export approved handover as PDF
- Hash-chained audit log (tamper-evident record of every view, edit, approval)
- Sudden-exit mode with "who to ask" routing list

### Planned for Round 3
- **Claim decay:** claim flips to "stale, re-verify" when a linked file, task or dependency changes after approval
- **Skeptic pass:** actively searches for contradicting evidence
- **Post-exit question queue and "ask the ledger":** answers only from approved claims, says "not in the ledger" otherwise

---

## 7. Architecture and Data Flow (Context Only)

**Planned stack:** React + Tailwind (frontend); Python + FastAPI (backend); PostgreSQL, SQLite for local dev; graph as entity and edge tables scored in Python; LLM API with structured JSON output for extraction and question generation; a second independent LLM call plus rule checks for verification; chunked sources with keyword and embedding search for retrieval; sign-in with role-based access control and per-chunk labels; canary-string tests and a held-out question harness; managed hosting for a judge-accessible link.

**Data flow:**
1. Sources parsed into small chunks, each stored with source, location and access label; sensitive patterns redacted here.
2. For a given viewer role, only chunks that role may see go to extraction.
3. Model proposes claims in a fixed structure and must cite chunk IDs. Claims without a valid citation are marked `missing evidence`.
4. Verification pass checks each cited chunk supports its claim and compares claims for conflicts. Each claim inherits the most restrictive label of its chunks.
5. Claims and sources populate the knowledge-risk graph, which scores nodes and ranks the gap interview.
6. Approved claims stored with version history and rendered into role-based views.
7. Scoring harness answers held-out questions using only a successor's view and reports the handover score.

### Privacy, security, responsible design
- Access labels applied at ingestion and enforced **before** generation, not hidden afterwards
- Labels propagate to claims, so a derived claim is never less restricted than its sources
- Canary strings planted in restricted sources are checked in every prompt and view by an automated test
- Sensitive patterns redacted at ingestion
- Only synthetic, public, permissioned or anonymised data in demos
- Source access is read-only; nothing is written back
- Every view, edit and approval is logged
- Human review: nothing shared until a reviewer approves; generated content labelled; any claim can be corrected or rejected
- Disclosure: AI model, libraries, templates and any AI-assisted code to be disclosed in Round 2 documentation

---

## 8. Three-Round Plan

| Round | Focus | Deliverables |
|---|---|---|
| Round 1: The Plan | Understand and design | Problem research and evidence; users, scenarios, workflow, architecture and permission model; synthetic sample project data with planted canary strings; this submission |
| Round 2: The Build | Working core workflow | Ingestion, reconstruction, claim ledger with citations, knowledge-risk graph, risk-ranked gap interview, review, role-based handover with label propagation and canary test, first handover score; deployed link and public repo; architecture and data-flow doc; structured feedback from test users; three committed Round 3 improvements |
| Round 3: The Finish | Complete and harden | The three committed improvements; reliability and failure-case handling; accessibility; demo video; testing notes; privacy and responsible-design explanation; limitations and roadmap |

**Committed Round 3 improvements (to be confirmed after Round 2):**
1. Claim decay and stronger evidence checking (skeptic pass, clearer conflict resolution)
2. Post-exit question queue and "ask the ledger"
3. Live source connection and polish (read-only GitHub, hash-chained audit log, accessibility, failure handling)

---

## 9. Expected Impact and How We Measure It

**Impact**
- **Less transition time:** successor starts from ownership, risks and next actions instead of reading every thread.
- **Less lost reasoning:** the risk-ranked interview captures critical knowledge while the person is reachable.
- **More trust:** every claim links to evidence and carries an honest status.
- **Safer sharing:** pre-generation filtering, label inheritance, canary tests, human approval.
- **Fewer repeated mistakes:** recurring problems and workarounds are recorded.
- **Earlier warning:** the risk graph shows where knowledge depends on a single person.

**Metrics**
- **Handover score:** share of held-out questions answered correctly using only the successor's view, vs. raw repo and chat
- **Time to answer:** time for key questions with and without the handover
- **Correction rate:** share of claims reviewers had to correct or reject
- **Leak test:** canary strings reaching any prompt or view (target: zero)

---

## 10. Future Scope
- Read-only connectors for common workplace and community tools
- Continuous knowledge capture, so the handover builds up over time rather than at departure
- Handover health scores warning teams early about single-person dependency
- Organisation-level policies for access labels and retention
- Support for volunteer communities, research groups and companies
- Multilingual handovers and richer export formats

## 11. Known Limitations (Stated in the Submission)
- Output quality depends on the amount and quality of source material
- Tacit knowledge not present in any source depends on the departing person's answers
- AI extraction can be wrong, which is why every claim is reviewable
- The handover score measures coverage of held-out questions, not every possible question

---

## 12. Blunt Notes for Your Own Planning (Not From the Submission)

- **Scope risk is the main danger.** Eleven core features is a lot. The thing that makes this win is the vertical slice: ingest -> claims with citations -> risk-ranked interview -> reviewed, filtered view -> score. Build that end to end before touching polish.
- **The handover score can be gamed or be weak.** If held-out questions are generated from the same ledger the successor view comes from, you are partly testing the system against itself. Write a portion of the questions by hand from the raw synthetic project, ideally including facts only discoverable through the interview.
- **"Independent" verification with a second LLM call is only partly independent.** Same model family, correlated errors. Rule checks (citation exists, quoted span present in the chunk) carry real weight; do not oversell the LLM verifier.
- **Single-point-of-knowledge score needs a concrete formula.** Decide early, e.g. fraction of a node's supporting chunks authored by or only reachable via the departing person, weighted by recency and criticality. Judges will ask.
- **Canary test claim is strong; make sure it is true.** Test prompts, views, logs and error messages, not only final views.
- **The user interviews with club leads were promised for Round 2.** Do them early; they are cheap and give the evidence the literature (all large-org studies) lacks.
- **Synthetic project data is a deliverable of its own.** Design it with planted traps: a decision with no rationale, two conflicting sources, a restricted source with canaries, a stale task, an account owned only by the leaver.
