# SPEC → IMPLEMENTATION MAP — SR-MAE TASK-001

Evidence = file path / line / behavior. Status per spec section.

| Spec | Requirement | Implemented in | Status |
|---|---|---|---|
| §1 Operating System: Q→…→VERDICT→HITL | pipeline spine | `examples/demo_research.py`, `srmae/loops.py:PHASES` | DONE |
| §2 No LLM-output-as-evidence; kinds FACT/INFERENCE/…/CONTRADICTED | `VALUE_KINDS`, `is_valid_value` reject empty support on FACT/RESULT | `srmae/objects.py:7-35` | DONE |
| §2 Object spine SOURCE→…→VERDICT w/ unique IDs | typed IDs `SRC/CLM/HYP/PRO/EXP/RES/ANL/CRT/VER` + provenance graph | `srmae/ids.py:4-8`, `srmae/provenance.py:7-10` | DONE |
| §3 Hierarchical structure (research question / sub-questions) | supported via `questions[]` (Communicator) and `open_questions` in snapshots | `srmae/snapshots.py:7-10`, `agents/communicator.md` | DONE |
| §4 LLM may reason/search/propose/run but must distinguish kinds | `Value.kind` + `epistemic.LADDER` | `srmae/objects.py`, `srmae/epistemic.py:5-13` | DONE |
| §5-7 Source / Claim / Hypothesis (falsifiable) | schemas enforce `falsification_criteria` minItems=1 | `schemas/source.json`, `schemas/claim.json`, `schemas/hypothesis.json:20` | DONE |
| §8 Protocol w/ inferential justification | schema requires `inferential_justification` | `schemas/protocol.json:6,30` | DONE |
| §9 Experiment: seed/env/params; results: observations[] = Value | `seed/env/deps/params` required | `schemas/experiment.json:7`, `schemas/result.json:17-30` | DONE |
| §10 Analysis w/ observation vs interpretation distinct | `ANL` schema + auditor agent separates | `agents/statistical_auditor.md`, `demo_research.py:204-219` | DONE |
| §11 Critique w/ falsification_status | schema enum: not_attempted/not_falsified/falsified | `schemas/critique.json:21` | DONE |
| §12 Verdict: NOT_FALSIFIED ≠ true; SUPPORTED/NOT_FALSIFIED/…/FALSIFIED | enum + rationale + dissent + human_reviewed | `schemas/verdict.json:18`, `agents/orchestrator.md:38` | DONE |
| §13-14 HITL: 5 mandatory checkpoints, 4 risk levels | `HITL.CHECKPOINTS`, `Level` enum | `srmae/hitl.py:9-23` | DONE |
| §15 Disputes between agents | `Dispute.open/resolve/needs_human` | `srmae/disputes.py` | DONE |
| §16 Snapshots per loop | `snapshots.take/restore` | `srmae/snapshots.py` | DONE |
| §17 Provenance cross-cutting | `Provenance.why()` reconstructs chain incl. seed/env/approvals | `srmae/provenance.py:58-73` | DONE |
| §18 Communication w/ human | `Communicator` agent | `agents/communicator.md` | DONE (cognitive layer) |
| §19 Independence between verification / fundamental / adversary | separate agents + test isolation | `agents/*.md`, `tests/test_*` | DONE |
| §20-21 Verification policy: ≥3 runs + baseline + controls + falsification + reproducibility | verified in demo: 3 independent seeds + negative control + adversary | `examples/demo_research.py:163-199` | DONE |
| §22-24 Anti-hallucination / contradiction tracking / Sci-Hub = access only | source schema separates `accessibility` from `quality_assessment`; Sci-Hub comment in schema | `schemas/source.json:33-42` | DONE |
| §25 Reproducibility: deterministic; ts/seed explicit | `srmae/__init__.py:3` ("no datetime.now/random inside") | DONE |
| §27 NOT_FALSIFIED ≠ true enforced | orchestrator forbidden action, verdict schema rationale required | `agents/orchestrator.md:38`, `schemas/verdict.json:23` | DONE |
| §28 LLM output ≠ evidence | `is_valid_value` enforces empty-support RESULT/FACT invalid | `srmae/objects.py:31-35` | DONE |
| §29-30 Anti-bullshit, anti-overconfidence | confidence capped 0.9, ≤0.5 if uncertainty=high; never ROBUST without ≥2 independent | `srmae/evidence.py:99-126` | DONE |
| §31 14 metrics defined | `metrics.compute` returns 14 with `{value, how, meaning}` | `srmae/metrics.py:117-160` | DONE |
| §32 Internal benchmark | demo is a Simple factual investigation w/ conflicting literature + control verification — covers 1/7 bench cases | `examples/demo_research.py` | PARTIAL (1/7) |
| §33 Logical commits | repo not under git | n/a | N/A (no git repo) |
| §34 PRINCIPAL ARCHITECTURE: ARCHITECTURE/IMPL/.../LIMITATIONS docs | `docs/ARCHITECTURE.md` + README | DONE |

## Gaps

| Gap | Severity | Where |
|---|---|---|
| Internal benchmark covers only 1/7 spec cases (Simple factual investigation). Other 6: contradictory literature (covered), simulation-heavy (covered), hypothesis generation, replication task, adversarial science, failure-heavy — extra test scripts needed. | LOW (the spec asks for tests, not a separate tool) | `tests/` |
| `multi-agent/` (sibling general MAE) is empty skeleton — no agents, no schemas, no state files. | MEDIUM (the orchestrator skill expects content there) | `multi-agent/` |
| `Communication to human` (Communicator agent) is contract-only; no module renders Communicator output to `reports/communicator/`. | LOW (cognitive role) | `reports/communicator/` |
| Adversary `cannot obtain evidence → not_attempted + BLOCKED` path is documented but no test forces it. | LOW | `tests/test_safety.py` could expand |
| No CI / no lint / no mypy — README says stdlib-only, but coverage of `Value.kind` rejection in real production flows depends on schema validation that is not enforced in code; only in agent contracts. | LOW (cognitive layer enforces it; machine layer enforces types) | `srmae/schemas.py` missing |