# Agent State Board — TASK-001 it.1 (CLOSED)

| Agent | Status | Notes |
|---|---|---|
| Orchestrator | DONE | main thread; emitted PD-001 |
| Researcher | IDLE | (audit task, not invoked) |
| Hypothesis | IDLE | (audit task) |
| Methodology | IDLE | (audit task) |
| Verification | IDLE | (audit task) |
| Fundamental | IDLE | (audit task) |
| Statistical Auditor | DONE | verified via demo: ANL-00001 in store |
| Adversary | DONE | verified via demo: CRT-00001, DSP-00001 |
| Communicator | IDLE | (audit task) |
| Provenance | DONE | verified via demo: why(VER-00001) reaches SRC+EXP |
| Safety Reviewer | DONE | verified via demo: SAFE_AUTONOMOUS for simulation |

## Final state
- decision: APPROVED (PD-001)
- open findings: 0
- resolved findings: 4 (FINDING-001 MEDIUM, FINDING-002 LOW, FINDING-003 LOW, FINDING-006 INFO)
- accepted findings: 1 (LOW — FINDING-004 Communicator renderer)
- verified findings: 1 (INFO — tests + demo green)

## BUGS FOUND + FIXED during Phase 1-4
- `srmae.provenance.why()` walked only parents; now walks both directions
  (parents + downstream TESTED_BY/PRODUCES/...). Exposed by demo_replication.
- `srmae.metrics.falsification_rate` counted only HYP objects; now counts
  HYP + CLM. Exposed by demo_adversarial.
- `srmae.epistemic.transition()` did not persist; now accepts `store=` and
  auto-persists when given. Backward-compatible (default store=None). Exposed
  by all 3 new demos.