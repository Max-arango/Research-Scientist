---
id: FINDING-005
title: All 51 tests pass; demo end-to-end green
severity: INFO
status: VERIFIED
discovered_by: orchestrator
discovered_at: 2026-09-03
task: TASK-001
---

# Finding

Verified runtime behavior on this machine.

## Evidence
```
$ cd scientific-research-mae && python3 -m unittest discover -s tests -q
Ran 51 tests in 0.078s
OK

$ python3 examples/demo_research.py
=== LOOP 0..7 · ... ===
[ORCHESTRATOR] VER-00001 = SUPPORTED (modest: contradicting source on file)
=== METRICS ===
  unsupported_claim_rate   = 0.0
  traceability             = 1.0
  replication_rate         = 1.0
  falsification_rate       = 0.0
  failure_log_size         = 1
  human_approval_count     = 5
  experiment_count         = 3
  source_count             = 2
=== DONE ===
Exit 0.
```

Demo invariants asserted in code:
- `unsupported_claim_rate == 0.0` ✓
- `traceability == 1.0` (verdict reaches SRC + EXP) ✓
- `human_approval_count >= 5` (5 checkpoints exercised) ✓
- `experiment_count >= 3` ✓
- `source_count >= 2` ✓
- `verdict_status == "SUPPORTED"` (modest because contradicting source on file) ✓
- `needs_human({"resolution": "human_review"})` True ✓

## Conclusion
The spine runs. Source/Claim/Hypothesis/Protocol/Experiment/Result/Analysis/Critique/Verdict
form a real chain, evidence is required to advance, adversary records falsification attempt,
human approval is real, snapshot restore works, provenance `why()` reaches SRC + EXP.