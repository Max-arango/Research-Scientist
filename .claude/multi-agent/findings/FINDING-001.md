```yaml
id: FINDING-001
task_id: TASK-001
source: orchestrator
type: FUNCTIONAL
severity: MEDIUM
confidence: CONFIRMED
status: RESOLVED
signature: "srmae/hitl.py:CHECKPOINTS:doc-drift"
affected_component: hitl
description: >
  hitl.CHECKPOINTS listed operational gate names, not the 5 canonical scientific
  approval checkpoints defined in SKILL.md / brief §14.
impact: "Contract/code drift; a caller iterating CHECKPOINTS would gate the wrong things."
evidence: "old CHECKPOINTS = [methodology_change, protocol_approval, external_action, ...]"
recommended_fix: "Replace with RESEARCH_QUESTION,HYPOTHESIS,PROTOCOL,MAJOR_EXPERIMENT_BRANCH,FINAL_CONCLUSION"
verification_method: "unittest test_canonical_checkpoints"
```

## Historial (append-only)
```
[iter 1] OPEN     — detected by Orchestrator on API review.
[iter 1] FIXED    — FIX-001: CHECKPOINTS set to canonical 5 in srmae/hitl.py.
[iter 1] RESOLVED — verified: tests/test_hitl.py::test_canonical_checkpoints PASS (51 tests OK).
```
