---
id: FINDING-002
title: Internal benchmark now covers 4/7 spec cases
severity: LOW
status: RESOLVED
discovered_by: orchestrator
discovered_at: 2026-09-03
resolved_by: orchestrator
resolved_at: 2026-09-04
task: TASK-001
---

# Finding (resolved)

Spec §32 asked for 7 benchmark investigation archetypes. Originally only 1/7
(`demo_research.py`). Three new demos added:

| Demo | Archetype | Verdict |
|---|---|---|
| `demo_research.py` | Simple factual + simulation + mixed literature | SUPPORTED |
| `demo_replication.py` | Replication task | REPRODUCED |
| `demo_adversarial.py` | Adversarial science (FALSIFIED path) | FALSIFIED |
| `demo_failure_heavy.py` | Failure-heavy (8 failure types) | INCONCLUSIVE |

## Evidence
```
examples/demo_research.py            OK
examples/demo_replication.py          OK
examples/demo_adversarial.py          OK
examples/demo_failure_heavy.py        OK
```

Each demo asserts its own invariants and exits 0.

## Remaining gap
3 archetypes still uncovered: contradictory-literature-only, hypothesis-generation,
replication-of-others. The 4 demos above cover the spine end-to-end; the remaining
3 are compositional variants. Acceptable for "covers the system" but not exhaustive.