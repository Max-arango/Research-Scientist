---
project: scientific-research-mae
task: TASK-001 — audit-and-test
status: IN_PROGRESS
iteration: 1
---

# Project State

## Stack
- Language: Python 3.11+ (developed on 3.14)
- Stdlib only — no external deps
- Test runner: `python3 -m unittest discover`
- Linter: none configured
- Build: none

## Layout
```
scientific-research-mae/
  SKILL.md           orchestrator constitution (read by orchestrator)
  README.md          quick start
  agents/            11 agent contracts (.md)
  schemas/           13 JSON Schemas
  protocols/         5 operating procedures
  srmae/             stdlib core (15 modules)
  tests/             16 unittest files + util.py
  examples/          demo_research.py
  docs/              ARCHITECTURE.md
  reference/         loop-engine.md
```

## Git
- Repo: NOT a git repository
- Branch: n/a
- Last commit: n/a

## Real commands (from README)
- Test: `python3 -m unittest discover -s tests -q`
- Demo: `python3 examples/demo_research.py`