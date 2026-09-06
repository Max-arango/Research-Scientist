```yaml
id: FINDING-003
task_id: TASK-001
source: orchestrator
type: FUNCTIONAL
severity: MEDIUM
confidence: CONFIRMED
status: RESOLVED
signature: "srmae/failures.py:FAILURE_TYPES:spec-mismatch"
affected_component: failures + schemas/failure.json
description: >
  Two parallel builders invented two DIFFERENT failure taxonomies, neither matching
  the canonical 11 types in brief §20. Code had one set, schema had another, test a third.
impact: "log_failure would reject the brief's own type names; schema/code inconsistent."
evidence: |
  code (old): HYPOTHESIS_FALSIFIED, REPLICATION_FAILED, ...
  schema (old): execution_error, environment_error, ...
  neither == spec: SCIENTIFIC, EXPERIMENTAL, REPRODUCIBILITY, STATISTICAL, TECHNICAL,
  TOOL, SOURCE, AGENT, COORDINATION, HUMAN_BLOCK, CAPABILITY_LIMITATION
recommended_fix: "Canonicalize all three to spec §20."
verification_method: "tests/test_schemas.py::test_failure_enum_matches_code"
```

## Historial (append-only)
```
[iter 1] OPEN     — detected by Orchestrator reconciling the two builders' handoffs.
[iter 1] FIXED    — FIX-003: srmae/failures.py, schemas/failure.json, tests/test_failures.py all set to spec 11 types.
[iter 1] RESOLVED — verified: test_schemas.test_failure_enum_matches_code asserts schema==code; 51 tests OK.
```
