# Architecture — scientific-research-mae

A Scientific Research Operating System: agents operate over **structured scientific objects**
and a **global research state**, not free conversation. This document is the map; the SKILL.md
is the operating protocol and `agents/*.md` are the per-agent constitutions.

## 1. Two layers, on purpose

| Layer | What it is | Why |
|---|---|---|
| **Cognitive** (markdown) | Agent contracts + protocols read by Claude subagents | Orchestration is genuinely done by an LLM reading a contract — modeling it as markdown is honest, not a fake engine. |
| **Machine** (`srmae` Python, stdlib-only) | Storage, IDs, epistemic state machine, evidence engine, provenance graph, snapshots, HITL, safety, failures, disputes, metrics, events | Reproducibility and auditability must be machine-checkable, not vibes. Every value is typed and traceable. |

The cognitive layer proposes; the machine layer records, constrains, and refuses illegal
epistemic moves. An agent cannot mark a claim ROBUST in code without ≥2 independent
replications on file, no matter what its prose says.

## 2. The object spine

```
SOURCE ──SUPPORTS/CONTRADICTS/DERIVES──▶ CLAIM ──PRODUCES──▶ HYPOTHESIS ──IMPLEMENTED_BY──▶ PROTOCOL
                                          │                                                    │
                                          └──TESTED_BY──▶ EXPERIMENT ◀──TESTED_BY──────────────┘
                                                            │ PRODUCES        │ REPRODUCES
                                                            ▼                 ▼
                                                          RESULT ──ANALYZED_BY──▶ ANALYSIS
                                                            │
                                                            └──CHALLENGED_BY──▶ CRITIQUE ──▶ VERDICT
```
Each object: typed ID, version, created_at, created_by (agent), provenance links. Objects are
**append-only** — an update writes a new version; nothing is overwritten or deleted (failed
experiments included).

### Value provenance (anti-hallucination)
Every scientifically loaded value is a `Value{kind, content, support[], note}`. A `RESULT` or
`FACT` with empty `support` is *invalid by construction*. LLM assertions enter as `INFERENCE`
or `OPINION`, never `FACT`. Absent→`UNKNOWN`, doubtful→`UNCERTAIN`, conflicting→`CONTRADICTED`.

## 3. Core modules (`srmae`)

- **ids** — typed sequential IDs, counters persisted (restart-safe).
- **storage** — append-only JSON object store + `events.jsonl`; versioned history.
- **objects** — `Value`, object factory, validity guard.
- **epistemic** — the state machine; `transition()` rejects illegal moves and strengthening
  moves that lack evidence.
- **evidence** — multi-dimensional `EvidenceState` + `suggested_state`/`confidence`; refuses
  simplistic scoring and zero-evidence assessment.
- **provenance** — the graph; `why(id)` reconstructs the full ancestry (sources, experiments,
  seeds, env, audits, critiques, human approvals).
- **snapshots** — `take`/`restore` per loop; full research reconstructable.
- **loops** — `LoopEngine.decide()` (CONTINUE/REWIND/BRANCH/ESCALATE/TERMINATE) + `stalled()`.
- **hitl** — levels + checkpoints; gates block until a human approval is recorded.
- **safety** — classifies actions; can halt the workflow before EXPERIMENT.
- **failures** — 11-type taxonomy, append-only.
- **disputes** — agent disagreement; strong dispute → HITL.
- **metrics** — 14 system-health metrics, each `{value, how, meaning}`.
- **events** — event constants + `emit()` for observability and metrics.

## 4. The loop

```
BOOTSTRAP → for loop in phases:
    orchestrator selects which agent acts (not all every time)
    delegate → agent returns handoff (structured) → persist objects + events
    evidence engine recomputes state → epistemic transition (evidence-gated)
    safety review before any EXPERIMENT
    HITL gate at the 5 checkpoints
    snapshot
    orchestrator.decide(signals) → CONTINUE | REWIND | BRANCH | ESCALATE | TERMINATE
    stall check → escalate if no progress
emit VERDICT (proposed) → HITL FINAL_CONCLUSION → human-reviewed verdict
```

## 5. Data on disk

```
.claude/scientific-research/
├── state/            # current-question, run_status, agent board, run-log
├── storage/          # objects/<ID>.v<n>.json, events.jsonl, counters.json, links
├── snapshots/        # SNP-*.json (also inside storage as objects)
└── reports/          # communicator loop summaries, verdicts, metrics
```

## 6. Metrics model

`unsupported_claim_rate` — fraction of CLAIM/RESULT values with empty support while kind ∈
{RESULT,FACT}. Healthy = 0. `traceability` — fraction of verdicts whose `why()` reaches ≥1
SOURCE and ≥1 EXPERIMENT. `falsification_coverage` — fraction of verdicts with ≥1 CRITIQUE.
`reproducibility_score` — fraction of experiments recording seed+env+params. Each metric ships
with `how` (computation) and `meaning` (interpretation) so no number is a black box.

## 7. Reproducibility guarantees

- Library functions take `ts`/`seed` as parameters — no hidden `now()`/`random()` — so a run
  is a pure function of its inputs.
- IDs and counters persist; the same inputs produce the same IDs.
- `provenance.why()` answers "why did the system conclude this" for any object.
- Snapshots reconstruct the whole investigation state.

## 8. Known limitations

- Live literature retrieval (Researcher) depends on network tools at runtime; the core is
  offline and deterministic, the demo uses declared synthetic sources.
- The safety reviewer is a keyword/flag classifier — a floor, not a substitute for an IRB or a
  domain safety officer.
- The evidence engine encodes heuristics; it structures judgment, it does not replace a
  statistician. All numbers are paired with reasons for human scrutiny.
