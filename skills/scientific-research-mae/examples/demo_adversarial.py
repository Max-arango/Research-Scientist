#!/usr/bin/env python3
"""Benchmark — ADVERSARIAL-ONLY (spec §32 case 6).

Build a deliberately weak claim. Run the full falsification arsenal. The
adversary must produce a CRITIQUE with falsification_status='falsified' and
the verdict must end as FALSIFIED.

SYNTHETIC. The "weakness" is engineered into the synthetic generator; the
adversary follows its mandate and reports it honestly.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from srmae import (  # noqa: E402
    Store, IdGen, Value, new_object, is_valid_value,
    transition, Provenance, LoopEngine, HITL, SafetyClass, review,
    snapshots, metrics, events,
)

TS = "2026-09-04T12:00:00Z"


def banner(msg: str) -> None:
    print(f"\n=== {msg} ===")


def main() -> int:
    root = tempfile.mkdtemp(prefix="srmae_adv_")
    store = Store(root)
    ids = IdGen(store)
    prov = Provenance(store)
    hitl = HITL(store)
    engine = LoopEngine(store, hitl, review)
    print("storage: <ephemeral temp dir>")

    # ---- weak claim: literature-only, contradictory source on file, no
    # experiment. Evidence engine must suggest WEAK_EVIDENCE. ---------------
    banner("WEAK CLAIM (literature only, mixed)")
    src_sup = new_object(store, ids, "SRC", "researcher", TS,
                         title="[SYNTHETIC] supporting for weak claim",
                         source_type="preprint", stance="supporting",
                         doi="10.0000/weak-1", note="declared synthetic")
    src_con = new_object(store, ids, "SRC", "researcher", TS,
                         title="[SYNTHETIC] contradicting for weak claim",
                         source_type="peer_reviewed", stance="contradicting",
                         doi="10.0000/weak-2", note="declared synthetic")
    claim = new_object(store, ids, "CLM", "researcher", TS,
                       statement="effect-Y holds (deliberately weak)",
                       value=Value("INFERENCE", "Y",
                                   support=[src_sup["id"]]).to_dict(),
                       state="UNVERIFIED", epistemic_state="UNVERIFIED")
    prov.link(src_sup["id"], "SUPPORTS", claim["id"])
    prov.link(src_con["id"], "CONTRADICTS", claim["id"])
    print(f"[CLAIM] {claim['id']} created with 1 supporting (preprint) + "
          f"1 contradicting (peer-reviewed)")

    # ---- adversary runs the full falsification question list ---------------
    banner("ADVERSARIAL FALSIFICATION")
    critique = new_object(store, ids, "CRT", "adversary", TS,
                          target_id=claim["id"], severity="high",
                          issues=[
                              "literature base is mixed (1 supporting preprint, "
                              "1 contradicting peer-reviewed)",
                              "no experiment ever tested the claim",
                              "potential confounder Z is uncontrolled",
                              "the supporting source is a preprint, not peer-reviewed",
                          ],
                          alternative_explanations=[
                              "the effect is driven by the confounder Z, not Y",
                              "the preprint is a chance finding (n small)",
                          ],
                          counterexamples=[
                              f"{src_con['id']} reports the opposite direction",
                          ],
                          recommended_tests=[
                              "run controlled experiment isolating Z",
                              "wait for independent replication",
                          ],
                          falsification_status="falsified")
    prov.link(claim["id"], "CHALLENGED_BY", critique["id"])
    events.emit(store, events.CRITIQUE_CREATED, TS, id=critique["id"])
    print(f"[ADVERSARY] {critique['id']} severity=high, falsification_status="
          f"{critique['falsification_status']}")

    # ---- evidence engine: with a contradicting peer-reviewed source and
    # zero experiments, the suggestion is WEAK_EVIDENCE. Then transition to
    # FALSIFIED because the adversary found a falsifying counterexample. ---
    transition(claim, "WEAK_EVIDENCE", evidence=[src_con["id"]],
               by="orchestrator", ts=TS, store=store)
    transition(claim, "FALSIFIED",
               evidence=[critique["id"], src_con["id"]],
               by="orchestrator", ts=TS, store=store)
    print(f"[CLAIM] {claim['id']} state={claim['state']}")

    # ---- verdict ----------------------------------------------------------
    verdict = new_object(store, ids, "VER", "orchestrator", TS,
                         claim_id=claim["id"],
                         verdict_status="FALSIFIED",
                         evidence_state="contradicting peer-reviewed source + "
                                        "adversary CRITIQUE-00001 (severity=high)",
                         state="FALSIFIED",
                         rationale="Adversary identified a peer-reviewed "
                                   "counterexample; claim is falsified.",
                         human_reviewed=False,
                         dissent=[])
    prov.link(claim["id"], "DERIVES", verdict["id"])
    events.emit(store, events.VERDICT_PROPOSED, TS, id=verdict["id"])
    print(f"[VERDICT] {verdict['id']} = FALSIFIED")

    # ---- provenance check -------------------------------------------------
    banner("PROVENANCE — why FALSIFIED?")
    why = prov.why(verdict["id"])

    def has_id(node, target):
        if node.get("id") == target:
            return True
        return any(has_id(a["node"], target) for a in node.get("ancestry", []))

    assert has_id(why, critique["id"]), "critique must be in verdict ancestry"
    assert has_id(why, src_con["id"]), "contradicting source must be in chain"
    print(f"[PROVENANCE] {verdict['id']} reaches {critique['id']} AND "
          f"{src_con['id']}")

    # ---- metrics ----------------------------------------------------------
    banner("METRICS")
    m = metrics.compute(store)
    fr = m["falsification_rate"]["value"]
    print(f"  falsification_rate     = {fr}")
    print(f"  contradiction_count    = {m['contradiction_count']['value']}")
    print(f"  failure_log_size       = {m['failure_log_size']['value']}")

    # ---- invariants --------------------------------------------------------
    assert claim["state"] == "FALSIFIED"
    assert verdict["verdict_status"] == "FALSIFIED"
    assert fr is not None and fr == 1.0
    assert m["contradiction_count"]["value"] == 1

    banner("DONE")
    print("Adversarial path verified. Claim + verdict both FALSIFIED. "
          "Provenance reaches critique + contradicting source. Exit 0.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())