---
id: FINDING-001
title: multi-agent/ skeleton tree populated
severity: MEDIUM
status: RESOLVED
discovered_by: orchestrator
discovered_at: 2026-09-03
resolved_by: orchestrator
resolved_at: 2026-09-03
task: TASK-001
---

# Finding (resolved)

`multi-agent/` was empty. Resolved by vendoring `srmae/` as `core/` and adding
agent contracts, SKILL.md, policy.yml, templates, and a smoke test.

## Evidence of resolution
```
multi-agent/
├── SKILL.md                 operating protocol
├── agents/                 7 contracts
│   ├── orchestrator.md
│   ├── planner.md
│   ├── builder.md
│   ├── optimizer.md
│   ├── qa.md
│   ├── red_team.md
│   └── appsec.md
├── config/
│   └── policy.yml           defaults for loop/gates/HITL/severity
├── core/                    vendored from srmae/ (16 .py files)
├── templates/
│   ├── task.md
│   ├── finding.md
│   └── production-decision.md
└── tests/
    └── test_smoke.py        10 tests, all green
```

## Verification
- `python3 -m unittest tests.test_smoke -v` → 10/10 OK.
- Cross-tree isolation: SR-MAE 51/51 + MAE 10/10 + isolation check `is type(s1) is type(s2) = True`.
- Vendored core re-exports all `srmae` public API unchanged.

## Architecture note
Vendor, don't cross-import: the two skills are peers, not a hierarchy. Release
cadence of scientific-research-mae and multi-agent-engineering may diverge.