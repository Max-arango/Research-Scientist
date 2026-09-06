```yaml
task_id: TASK-001
iteration: 1
decided_by: orchestrator
status: APPROVED
acceptance_criteria:
  - { id: AC1,  met: true, evidence: "SKILL.md valid frontmatter (name+description) + all required sections; QA head/grep PASS" }
  - { id: AC2,  met: true, evidence: "grep -L over 11 sections × 11 agents → no file missing any (re-verified by orchestrator)" }
  - { id: AC3,  met: true, evidence: "json.load over schemas/*.json → 12 present, 0 missing, all parse" }
  - { id: AC4,  met: true, evidence: "import srmae ok; unittest 51/51 OK" }
  - { id: AC5,  met: true, evidence: "live IllegalTransition on illegal skip + empty-evidence strengthening; test_epistemic covers both" }
  - { id: AC6,  met: true, evidence: "why(VER-00001) reaches SRC ✓ EXP ✓; test_provenance asserts it" }
  - { id: AC7,  met: true, evidence: "4 levels + 5 canonical checkpoints; BLOCKED stays BLOCKED after approve()" }
  - { id: AC8,  met: true, evidence: "assess raises on 0 evidence; never ROBUST <2 indep; confidence<=0.5 high uncertainty; reasoning always set" }
  - { id: AC9,  met: true, evidence: "is_valid_value rejects RESULT/FACT w/o support; researcher.md forbids fabricating DOIs; demo asserts on every RESULT" }
  - { id: AC10, met: true, evidence: "snapshots.take/restore roundtrip; test_snapshots + demo restore assert" }
  - { id: AC11, met: true, evidence: "code FAILURE_TYPES==schema enum==11 canonical (symmetric diff empty); test_schemas guards it" }
  - { id: AC12, met: true, evidence: "verdict.json + adversary.md use 5-status enum; NOT_FALSIFIED≠true documented" }
  - { id: AC13, met: true, evidence: "demo exit 0, self-asserting spine; test_integration_demo runs it in-suite" }
  - { id: AC14, met: true, evidence: "python3 -m unittest discover → Ran 51 tests OK" }
  - { id: AC15, met: true, evidence: "demo prints traceability=1.0, unsupported_claim_rate=0.0, replication_rate=1.0, +6 more" }
gates:
  qa: PASS          # 15/15 criteria with executed evidence; independently re-verified key claims
  red_team: N/A     # deliverable has no runtime attack surface (offline stdlib lib + markdown)
  appsec: N/A       # in-deliverable safety_reviewer module reviewed by contract; no external I/O
blockers: []
overrides: []
required_action: ""
evidence_summary: |
  Independent re-runs by orchestrator (not trusting agent claims):
  - `python3 -m unittest discover -s tests -q` → Ran 51 tests, OK.
  - `python3 examples/demo_research.py` → exit 0, "All end-to-end invariants hold";
    traceability=1.0, unsupported_claim_rate=0.0, human_approval_count=5, experiment_count=3.
  - Two full demo runs → byte-identical stdout (reproducibility).
  - grep -L over 11 contract sections × 11 agents → none missing.
  - code FAILURE_TYPES == schemas/failure.json enum == 11 canonical types.
change_summary: |
  New skill scientific-research-mae/:
  - srmae/ (15 stdlib modules): ids, storage(append-only versioned), objects(Value+guard),
    epistemic(state machine), evidence(multi-dim engine), provenance(why-graph), snapshots,
    loops, hitl(5 checkpoints/4 levels), safety(classifier), failures(11 types), disputes,
    metrics(14), events.
  - agents/ 11 contracts (all 11 required sections each).
  - schemas/ 12 JSON Schemas (draft-07). protocols/ 5 docs.
  - SKILL.md, README.md, docs/ARCHITECTURE.md, reference/loop-engine.md.
  - examples/demo_research.py (end-to-end synthetic, self-asserting).
  - tests/ 14 files, 51 tests.
  Findings resolved this iteration: FINDING-001, -003, -004 (MEDIUM), -005 (LOW), all with
  regression tests. FINDING-002 (LOW, 12 ad-hoc metric key names) ACCEPTED — AC15 only needs
  them computed; documented in metrics.py.
notes: |
  APPROVED != deployed. This is a skill spec + stdlib library; "deploy" = install the skill.
  No git repo in target dir → no commit made (would require user authorization + git init).
  Honest scope limits (docs/ARCHITECTURE §8): live literature retrieval needs runtime network
  tools (core is offline/deterministic by design); safety reviewer is a keyword floor, not an IRB.
```
