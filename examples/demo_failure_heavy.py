#!/usr/bin/env python3
"""Benchmark — FAILURE-HEAVY (spec §32 case 7).

Drive multiple failure types through the system in one run, log each via the
11-type taxonomy, assert no failure is silently swallowed, and verify the
investigation can still emit a (modest) verdict that does NOT erase the
failures from the audit trail.

SYNTHETIC. The "failures" are triggered by the synthetic setup; the system
must log them honestly.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from srmae import (  # noqa: E402
    Store, IdGen, Value, new_object, is_valid_value,
    transition, Provenance, LoopEngine, HITL, SafetyClass, review,
    snapshots, metrics, events, log_failure, FAILURE_TYPES,
)

TS = "2026-09-04T12:00:00Z"


def banner(msg: str) -> None:
    print(f"\n=== {msg} ===")


def main() -> int:
    root = tempfile.mkdtemp(prefix="srmae_fail_")
    store = Store(root)
    ids = IdGen(store)
    prov = Provenance(store)
    hitl = HITL(store)
    engine = LoopEngine(store, hitl, review)
    print("storage: <ephemeral temp dir>")

    # ---- start a normal investigation -----------------------------------
    banner("INVESTIGATION START")
    src = new_object(store, ids, "SRC", "researcher", TS,
                     title="[SYNTHETIC] start point",
                     source_type="peer_reviewed", stance="supporting",
                     doi="10.0000/fail-base", note="declared synthetic")
    claim = new_object(store, ids, "CLM", "researcher", TS,
                       statement="effect-Q to be tested amid failures",
                       value=Value("INFERENCE", "Q",
                                   support=[src["id"]]).to_dict(),
                       state="UNVERIFIED", epistemic_state="UNVERIFIED")
    prov.link(src["id"], "SUPPORTS", claim["id"])
    transition(claim, "LITERATURE_SUPPORTED", evidence=[src["id"]],
               by="orchestrator", ts=TS, store=store)
    print(f"[CLAIM] {claim['id']} LITERATURE_SUPPORTED")

    # ---- trigger the full failure taxonomy, one record per type ----------
    # (we use a subset that maps to natural failure modes for this run)
    banner("LOGGING FAILURES (8 distinct types)")
    failures = []
    fixtures = [
        # (type, what, why, impact, affected, resolution, reproducible, changes)
        ("SOURCE", "unretrievable DOI for SRC-00099",
         "publisher 404 at fetch time", "literature base shrunk",
         [claim["id"]], "switch to preprint server", True, False),
        ("EXPERIMENTAL", "EXP-00001 crashed mid-run (OOM)",
         "matrix dimension overflow", "1 of 3 planned runs lost",
         [], "downsize + restart", True, False),
        ("STATISTICAL", "n=2 surviving runs, insufficient for paired test",
         "the OOM killed one arm", "cannot claim statistical significance",
         [claim["id"]], "report effect size with explicit uncertainty",
         True, False),
        ("REPRODUCIBILITY", "EXP-00002 not reproducible on a different host",
         "floating-point order differs across BLAS", "claimed effect shrinks to noise",
         [claim["id"]], "pin numpy + containerize", True, True),
        ("TOOL", "statistical_auditor tool returned malformed JSON",
         "agent emitted prose-only output", "analysis loop stalled 1 turn",
         [], "reject + re-prompt with strict schema", False, False),
        ("AGENT", "adversary emitted falsification_status='not_attempted' "
                  "with no reasoning",
         "context-too-large truncation", "one gate had to be redone",
         [claim["id"]], "split context, re-run adversary", False, False),
        ("COORDINATION", "handoff between methodology and verification lost "
                         "the confounder list",
         "yaml copy/paste dropped a field", "protocol PRO-00001 redone",
         [], "schema-validate handoff at receipt", True, False),
        ("CAPABILITY_LIMITATION", "no real dataset in this offline run",
         "sandbox has no network/data", "external validity unknown",
         [claim["id"]], "flag for real-data replication", True, False),
    ]
    for ftype, what, why, impact, affected, resolution, repro, changes in fixtures:
        assert ftype in FAILURE_TYPES, f"unknown failure type {ftype}"
        fid = log_failure(store, type=ftype, what=what, why=why,
                          impact=impact, affected=affected, resolution=resolution,
                          reproducible=repro, changes_conclusions=changes, ts=TS)
        failures.append(fid)
        print(f"  [{ftype:24s}] {fid}  changes_conclusions={changes}")

    # ---- one failure type is intentionally NOT triggered (HUMAN_BLOCK)
    # because it requires an actual human rejection; we document the gap. -
    # (it would be a single log_failure() call if a real human blocked.)

    # ---- ONE failure did change conclusions: REPRODUCIBILITY ------------
    # The verdict must acknowledge this — not erase it.
    banner("VERDICT (with dissent on record)")
    verdict = new_object(store, ids, "VER", "orchestrator", TS,
                         claim_id=claim["id"],
                         verdict_status="INCONCLUSIVE",
                         evidence_state="1 source, 0 surviving experiments, "
                                        "REPRODUCIBILITY failure on file",
                         state="UNVERIFIED",
                         rationale="Claim remains INCONCLUSIVE: experiments did "
                                   "not survive a host change (FLR-00004), and the "
                                   "remaining n is too small for a confident test. "
                                   "Failures preserved for re-investigation.",
                         human_reviewed=False,
                         dissent=["adversary: reproducibility failure shifts the "
                                  "burden to a controlled replication before any "
                                  "verdict stronger than INCONCLUSIVE is justified"])
    prov.link(claim["id"], "DERIVES", verdict["id"])
    events.emit(store, events.VERDICT_PROPOSED, TS, id=verdict["id"])
    print(f"[VERDICT] {verdict['id']} = INCONCLUSIVE (dissent recorded)")

    # ---- metrics ----------------------------------------------------------
    banner("METRICS")
    m = metrics.compute(store)
    fls = m["failure_log_size"]["value"]
    print(f"  failure_log_size       = {fls}")
    print(f"  contradiction_count    = {m['contradiction_count']['value']}")
    print(f"  unsupported_claim_rate = {m['unsupported_claim_rate']['value']}")

    # ---- snapshot the failure-heavy state for later review ---------------
    loop_id = engine.start_loop("VERDICT")
    snap = snapshots.take(store, loop_id, {
        "ts": TS,
        "claims": [claim["id"]],
        "hyps": [],
        "experiments": [],
        "results": [],
        "failures": failures,
        "agent_decisions": [f"orchestrator:INCONCLUSIVE"],
        "human_decisions": [],
        "open_questions": ["real-data replication?", "containerize env?"],
        "evidence_deltas": ["claim state held at UNVERIFIED — failures blocked ascent"],
        "next_actions": ["rerun with numpy pinned + container", "add 2 more seeds"],
    })
    print(f"[SNAPSHOT] {snap['id']} taken with {len(failures)} failure(s) on record")

    # ---- invariants --------------------------------------------------------
    assert fls == 8, f"expected 8 failures logged, got {fls}"
    assert verdict["verdict_status"] == "INCONCLUSIVE"
    assert verdict["dissent"], "dissent must be recorded, not erased"
    # no failure was deleted — every FLR id still resolves
    for fid in failures:
        assert store.get(fid)["type"] in FAILURE_TYPES
    # failure that 'changes_conclusions' is preserved
    changing = [f for f in store.all("FLR") if f["changes_conclusions"]]
    assert len(changing) == 1, "exactly one failure changes conclusions"

    banner("DONE")
    print("Failure-heavy path verified. 8 failures logged, 1 changes "
          "conclusions, verdict INCONCLUSIVE with dissent preserved. Exit 0.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())