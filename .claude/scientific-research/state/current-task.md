---
task_id: TASK-001
title: Audit and test scientific-research-mae skill vs spec
status: IN_PROGRESS
iteration: 1
phase: BOOTSTRAP
started_at: 2026-09-03
---

# Current Task

## Question (from user)
Analyze the full skill and test it in a controlled environment. Verify whether it
is complete and already satisfies the directives of the original spec
("PROMPT PARA CLAUDE CODE — SCIENTIFIC RESEARCH MAE SKILL", 34 sections).

## Type
AUDIT + VALIDATION (not a research investigation).

## Pipeline
1. ORCHESTRATOR — read spec, map spec→impl, run tests, run demo, write findings
2. (Optional sub-delegation skipped — main thread suffices for an audit)

## Acceptance criteria
- [ ] All 16 test files executed, results recorded
- [ ] demo_research.py executed end-to-end, results recorded
- [ ] Spec sections 1-34 mapped to existing artifacts (file:section table)
- [ ] FINDING-NNN.md per gap, with severity
- [ ] Production Decision emitted