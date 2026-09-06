#!/usr/bin/env python3
"""Benchmark — REPLICATION (spec §32 case 5).

Take a pre-existing claim, attempt an independent_replication under the
original protocol, verify the claim state moves to REPRODUCED, and emit a
verdict that traces back through both the original and the replication
experiments.

SYNTHETIC. No real measurements. All inputs declared offline.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from srmae import (  # noqa: E402
    Store, IdGen, Value, new_object, is_valid_value,
    transition, Provenance, LoopEngine, HITL, SafetyClass, review,
    snapshots, metrics, events, log_failure,
)

TS = "2026-09-04T12:00:00Z"


def banner(msg: str) -> None:
    print(f"\n=== {msg} ===")


def main() -> int:
    root = tempfile.mkdtemp(prefix="srmae_repl_")
    store = Store(root)
    ids = IdGen(store)
    prov = Provenance(store)
    hitl = HITL(store)
    engine = LoopEngine(store, hitl, review)
    print("storage: <ephemeral temp dir>")

    # ---- original claim + original experiment (the one we are REPLICATING) ----
    banner("ORIGINAL CLAIM + ORIGINAL EXPERIMENT")
    src = new_object(store, ids, "SRC", "researcher", TS,
                     title="[SYNTHETIC] effect-X to replicate",
                     source_type="peer_reviewed", stance="supporting",
                     doi="10.0000/replication-target", note="declared synthetic")
    claim = new_object(store, ids, "CLM", "researcher", TS,
                       statement="effect-X holds under protocol P",
                       value=Value("INFERENCE", "X under P",
                                   support=[src["id"]]).to_dict(),
                       state="UNVERIFIED", epistemic_state="UNVERIFIED")
    prov.link(src["id"], "SUPPORTS", claim["id"])
    original_exp = new_object(store, ids, "EXP", "verification", TS,
                              protocol_id="PRO-00001", kind="replication",
                              independent=False, seed=42,
                              params={"x": 1.0}, runs=1, status="COMPLETED")
    original_res = new_object(store, ids, "RES", "verification", TS,
                              experiment_id=original_exp["id"],
                              value=Value("RESULT", {"delta": 0.020},
                                          support=[original_exp["id"]]).to_dict(),
                              metrics={"delta": 0.020}, status="COMPLETED")
    prov.link(claim["id"], "TESTED_BY", original_exp["id"])
    prov.link(original_exp["id"], "PRODUCES", original_res["id"])
    # advance claim to EXPERIMENTALLY_TESTED (has at least one experiment)
    transition(claim, "LITERATURE_SUPPORTED", evidence=[src["id"]],
               by="orchestrator", ts=TS, store=store)
    transition(claim, "EXPERIMENTALLY_TESTED", evidence=[original_exp["id"]],
               by="orchestrator", ts=TS, store=store)
    print(f"[ORIGINAL] {claim['id']} state={claim['state']}, "
          f"{original_exp['id']} delta=0.020")

    # ---- REPLICATION: a new experiment with a distinct seed and an explicit
    # independent_replication kind. Same protocol, fresh environment. --------
    banner("INDEPENDENT REPLICATION")
    repl_exp = new_object(store, ids, "EXP", "verification", TS,
                          protocol_id="PRO-00001", kind="independent_replication",
                          independent=True, seed=99, env="python3.14/cpu",
                          params={"x": 1.0}, runs=1, status="COMPLETED")
    # SYNTHETIC replication result — slightly different but same direction
    delta = 0.018
    repl_res = new_object(store, ids, "RES", "verification", TS,
                          experiment_id=repl_exp["id"],
                          value=Value("RESULT", {"delta": delta},
                                      support=[repl_exp["id"]]).to_dict(),
                          metrics={"delta": delta}, status="COMPLETED")
    prov.link(claim["id"], "TESTED_BY", repl_exp["id"])
    prov.link(repl_exp["id"], "PRODUCES", repl_res["id"])
    prov.link(repl_exp["id"], "REPRODUCES", original_res["id"])
    events.emit(store, events.EXPERIMENT_COMPLETED, TS, id=repl_exp["id"])
    print(f"[REPLICATION] {repl_exp['id']} seed=99 delta={delta}")

    # ---- evidence engine verdict -----------------------------------------
    # 1 independent_replication + 1 replication = 2 total experiments.
    # original is a non-independent replication (independent=False).
    independent = sum(1 for e in [original_exp, repl_exp] if e["independent"])
    repetitions = sum(1 for e in [original_exp, repl_exp] if not e["independent"])
    print(f"[EVIDENCE] independent_replications={independent}, "
          f"repetitions={repetitions}")

    # Claim moves REPRODUCED only if independent >= 1 AND repetitions >= 1.
    assert independent >= 1 and repetitions >= 1, "REPRODUCED requires 1+1"
    transition(claim, "REPRODUCED", evidence=[repl_exp["id"], original_exp["id"]],
               by="orchestrator", ts=TS, store=store)
    print(f"[CLAIM] {claim['id']} state={claim['state']}")

    # ---- provenance: why REPRODUCED must reach both experiments -----------
    banner("PROVENANCE — why REPRODUCED?")
    why = prov.why(claim["id"])

    def has_exp(node, exp_id):
        if node.get("id") == exp_id:
            return True
        for a in node.get("ancestry", []):
            if has_exp(a["node"], exp_id):
                return True
        return False

    assert has_exp(why, original_exp["id"]), "original exp missing from chain"
    assert has_exp(why, repl_exp["id"]), "replication exp missing from chain"
    print(f"[PROVENANCE] {claim['id']} ancestry reaches {original_exp['id']} AND "
          f"{repl_exp['id']}")

    # ---- metrics ----------------------------------------------------------
    banner("METRICS")
    m = metrics.compute(store)
    # replication_rate = independent / completed >= 0.5 (1 of 2)
    rr = m["replication_rate"]["value"]
    print(f"  replication_rate      = {rr}")
    print(f"  traceability          = {m['traceability']['value']}")
    print(f"  experiment_count      = {m['experiment_count']['value']}")

    # ---- invariants --------------------------------------------------------
    assert claim["state"] == "REPRODUCED"
    assert m["experiment_count"]["value"] == 2
    # 'replication_rate' is a value, not None
    assert rr is not None and rr >= 0.5

    banner("DONE")
    print("Replication path verified. Claim REPRODUCED with independent + "
          "original both in provenance. Exit 0.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())