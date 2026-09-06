---
id: FINDING-006
title: Spec §33 "logical commits" is N/A — repo is not under git
severity: INFO
status: RESOLVED
discovered_by: orchestrator
discovered_at: 2026-09-03
task: TASK-001
---

# Finding

The user's spec §33 asks for logical commits with prefixes like
`feat(core):`, `feat(evidence):`, etc.
The working directory `/home/fellcrack/.../Research-Scientist/` is not a git repository.

## Evidence
```
$ git status
fatal: not a git repository
```

## Impact
- Cannot produce a commit history. The skill ships as files; history is the directory tree.
- This is a property of the working environment, not the skill itself.

## Recommended Action
If the user wants a versioned history:
```bash
cd /home/fellcrack/Trabajo/Personal/IA-Laboratorio/Claude/Skills/Skills-Developing/Research-Scientist
git init
git add scientific-research-mae/
# Then split into logical commits with the suggested prefixes.
```
Out of scope for the audit unless requested.