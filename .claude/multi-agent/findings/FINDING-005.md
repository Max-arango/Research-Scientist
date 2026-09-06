```yaml
id: FINDING-005
task_id: TASK-001
source: qa
type: FUNCTIONAL
severity: LOW
confidence: CONFIRMED
status: RESOLVED
signature: "examples/demo_research.py:storage-header:non-determinism"
affected_component: demo
description: >
  Demo stdout was byte-identical across runs EXCEPT the first line, which printed the
  randomized OS temp-dir path. Domain IDs and metrics were fully deterministic; only the
  scratch-dir label varied. QA local_ref qa-1.
impact: "Strict byte-for-byte diff of raw stdout differed; cosmetic, not functional."
evidence: "diff -> only '1c1 storage: /tmp/srmae_demo_<rand>'; grep -v storage -> identical."
recommended_fix: "Print a stable label instead of the random path."
verification_method: "diff of two full runs -> identical"
```

## Historial (append-only)
```
[iter 1] OPEN     — reported by QA (qa-1, LOW).
[iter 1] FIXED    — FIX-005: demo prints 'storage: <ephemeral temp dir>' stable label.
[iter 1] RESOLVED — verified: two full runs byte-identical (diff -q clean); 51 tests OK.
```
