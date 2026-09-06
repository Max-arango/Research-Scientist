```yaml
id: FINDING-004
task_id: TASK-001
source: orchestrator
type: FUNCTIONAL
severity: MEDIUM
confidence: CONFIRMED
status: RESOLVED
signature: "srmae/hitl.py:gate:id-namespace-collision"
affected_component: hitl + metrics + provenance
description: >
  HITL.gate() minted checkpoint objects with the VER (verdict) id prefix. Checkpoints
  therefore polluted the verdict namespace: the traceability metric (verdicts whose
  provenance reaches a SOURCE and EXPERIMENT) counted 5 un-traceable checkpoints as
  verdicts, collapsing traceability from 1.0 to 0.166.
impact: "Silent corruption of a core integrity metric; checkpoints indistinguishable from verdicts."
evidence: |
  demo first run: traceability = 0.16666666666666666 (1 real verdict / 6 VER objects)
  after fix:      traceability = 1.0
reproduction: "run examples/demo_research.py before fix -> AssertionError 'verdict must be fully traceable'"
recommended_fix: "Add CHK id prefix; mint checkpoints as CHK-*; metrics.human_approval_count reads CHK."
verification_method: "tests/test_hitl.py::test_checkpoints_use_chk_prefix_not_ver + demo traceability==1.0"
```

## Historial (append-only)
```
[iter 1] OPEN     — detected by the end-to-end demo self-assertion (traceability != 1.0).
[iter 1] FIXED    — FIX-004: added CHK prefix (ids.py), gate() mints CHK-* (hitl.py),
                    human_approval_count reads CHK (metrics.py).
[iter 1] RESOLVED — verified: demo traceability==1.0, regression test asserts CHK prefix + empty VER; 51 tests OK.
```
