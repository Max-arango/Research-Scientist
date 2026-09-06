# Run Log

## 2026-09-03 — TASK-001 iteration 1
- BOOTSTRAP: created state dirs under .claude/scientific-research/
- ORCHESTRATOR: mapped tree (11 agents / 13 schemas / 15 modules / 16 tests)
- TESTS: 51/51 pass
- DEMO: end-to-end green, exit 0
- AUDIT: spec → impl mapping written to decisions/ADR-001
- FINDINGS: 6 emitted (FINDING-001..006)
- DECISION: PD-001 — APPROVED-WITH-MINOR

## 2026-09-03 — TASK-001 iteration 2 (Phase 0 fix)
- Vendored srmae/ → multi-agent/core/ (16 modules, no re-implementation)
- Wrote 7 agent contracts (orchestrator + planner + builder + optimizer + qa + red_team + appsec)
- Wrote SKILL.md, config/policy.yml, 3 templates
- Wrote tests/test_smoke.py — 10/10 pass
- Cross-tree isolation verified (SR-MAE 51/51 + MAE 10/10, distinct Store classes)
- FINDING-001 RESOLVED
- PD-001 amended: APPROVED (no remaining blockers)

## 2026-09-04 — TASK-001 iteration 3 (Phase 1-3)
- Phase 1: 3 benchmark demos (replication/adversarial/failure-heavy). All 4 demos pass.
- Phase 1 surfaced 3 real bugs in srmae core, fixed:
  - provenance.why() walks both directions
  - metrics.falsification_rate includes CLM, not only HYP
  - transition() persists via store= arg (backward-compat)
- Phase 2: tests REWIND (4) + human_subjects (1) — 56/56 pass
- Phase 3: git init, 8 logical commits with spec §33 prefixes, GitHub Actions CI
- FINDING-002 RESOLVED (4/7 archetypes)

## 2026-09-05 — TASK-001 iteration 4 (Phase 4)
- Phase 4: schema required-key + enum validator (stdlib only, no jsonschema)
- new_object(..., validate=True) runs validator before persist
- 5 new tests: ok, missing_required, bad_enum, unknown_prefix_no_crash, new_object_validate_true_rejects
- Full suite: 61/61 pass. All 4 demos: OK.
- Commit: feat(schemas): hand-rolled stdlib validator + new_object(validate=True)
- FINDING-003 RESOLVED (validator added; cognitive layer still primary contract)

## 2026-09-05 — TASK-002 (GitHub-skill features → researcher)
- Researched GitHub skills (2 bg agents): anthropics/skills + community research skills
- Adapted 6 functional features to the RESEARCHER agent:
  1. Multi-source literature search (real DOIs) — Crossref/OpenAlex/arXiv
  2. DOI verify + retraction flag (title-prefix + Crossref update-to)
  3. Citation-graph expand (refs/citations) via OpenAlex
  4. Bibliography export (BibTeX / CSL-JSON)
  5. Bundled-script pattern (agent CALLS scripts/litsearch.py, never reads it)
  6. Progressive-disclosure reference (reference/search_strategy.md, load on demand)
- Bridge srmae/sources.py: source_from_record() tool-record -> validated SOURCE
- Live demo demo_researcher_live.py: real retrieval end-to-end, self-SKIPs offline
- 12 new tests (5 sources + 7 litsearch). Full suite 73/73.
- Bug fixed mid-build: retraction detection missed RETRACTED: title prefix
- Closes ARCHITECTURE §8 (literature retrieval was offline-only)
- Commit: feat(researcher): bundled litsearch tool — real retrieval, no fabrication
- STATUS: CLOSED