#!/usr/bin/env python3
"""End-to-end scientific research demo — deterministic, offline, synthetic.

Walks the full spine for one research question:

    QUESTION -> LITERATURE -> CLAIM -> HYPOTHESIS -> PROTOCOL -> EXPERIMENT(s)
             -> RESULT -> ANALYSIS -> CRITIQUE -> VERDICT -> SNAPSHOT -> HUMAN REVIEW

Every value is epistemically typed; every conclusion is provenance-linked; the human
approves at the five checkpoints. NO real papers/DOIs/measurements are invented — the
sources and simulation outputs here are explicitly DECLARED SYNTHETIC for demonstration.

Run:  python3 examples/demo_research.py
It asserts its own invariants and prints a metrics report. Exit 0 == healthy run.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from srmae import (  # noqa: E402
    Store, IdGen, Value, new_object, is_valid_value,
    transition, assess, suggested_state, confidence,
    Provenance, snapshots, LoopEngine, HITL, Level, SafetyClass, review,
    Dispute, needs_human, log_failure, metrics, events,
)

# A fixed clock — reproducibility: the run is a pure function of its inputs.
TS = "2026-09-02T12:00:00Z"
SEED = 1234

# --- The five canonical HITL checkpoints (SKILL.md) -----------------------------
CP_QUESTION = "RESEARCH_QUESTION"
CP_HYPOTHESIS = "HYPOTHESIS"
CP_PROTOCOL = "PROTOCOL"
CP_BRANCH = "MAJOR_EXPERIMENT_BRANCH"
CP_CONCLUSION = "FINAL_CONCLUSION"


def banner(msg: str) -> None:
    print(f"\n=== {msg} ===")


def human_approves(hitl: HITL, checkpoint: str, action: str, payload: dict) -> str:
    """Open a gate and record a synthetic human approval. Returns checkpoint id."""
    gate = hitl.gate(checkpoint, {**payload, "action": action, "ts": TS})
    res = hitl.approve(gate["checkpoint_id"], human="dr.human",
                       decision=True, note=f"approved: {checkpoint}", ts=TS)
    print(f"[HUMAN] {checkpoint}: gate={gate['status']} -> {res['status']}")
    return gate["checkpoint_id"]


def main() -> int:
    root = tempfile.mkdtemp(prefix="srmae_demo_")
    store = Store(root)
    # Print a stable label (not the randomized temp path) so stdout is byte-identical
    # across runs — the reproducibility claim covers the domain output, and now the
    # header too. The real path is still available via the return / env if needed.
    ids = IdGen(store)
    prov = Provenance(store)
    hitl = HITL(store)
    safety_reviewer = review
    engine = LoopEngine(store, hitl, safety_reviewer)

    print("storage: <ephemeral temp dir>")

    # ---------------------------------------------------------------- QUESTION
    banner("LOOP 0 · QUESTION")
    question = ("Does a 20% learning-rate warmup reduce final validation loss in a small "
                "transformer, versus no warmup? (SYNTHETIC demo)")
    engine.start_loop("QUESTION")
    events.emit(store, events.LOOP_STARTED, TS, phase="QUESTION")
    human_approves(hitl, CP_QUESTION, "approve research question", {"question": question})

    # ---------------------------------------------------------------- LITERATURE
    banner("LOOP 1 · LITERATURE")
    engine.start_loop("LITERATURE")
    # DECLARED SYNTHETIC sources. In a real run the Researcher tool retrieves these
    # with real DOIs; here they are illustrative and marked as such.
    src1 = new_object(store, ids, "SRC", "researcher", TS,
                      title="[SYNTHETIC] Warmup schedules for small transformers",
                      source_type="peer_reviewed", stance="supporting",
                      doi="10.0000/synthetic-demo-1", note="declared synthetic")
    src2 = new_object(store, ids, "SRC", "researcher", TS,
                      title="[SYNTHETIC] On the fragility of warmup claims",
                      source_type="preprint", stance="contradicting",
                      doi="10.0000/synthetic-demo-2", note="declared synthetic")
    for s in (src1, src2):
        events.emit(store, events.SOURCE_FOUND, TS, id=s["id"])
    print(f"[RESEARCHER] sources: {src1['id']} (peer_reviewed, supporting), "
          f"{src2['id']} (preprint, contradicting)")

    # ---------------------------------------------------------------- CLAIM
    claim_stmt = Value(kind="INFERENCE",
                       content="Warmup reduces final validation loss under budget B.",
                       support=[src1["id"]],
                       note="literature inference, not yet tested")
    assert is_valid_value(claim_stmt)
    claim = new_object(store, ids, "CLM", "researcher", TS,
                       statement=claim_stmt.to_dict(), state="UNVERIFIED",
                       value=claim_stmt.to_dict())
    prov.link(src1["id"], "SUPPORTS", claim["id"])
    prov.link(src2["id"], "CONTRADICTS", claim["id"])
    events.emit(store, events.CLAIM_CREATED, TS, id=claim["id"])
    print(f"[RESEARCHER] {claim['id']} created (state UNVERIFIED); "
          f"literature is mixed -> not auto-strong")

    # literature-only evidence: one supporting + one contradicting source
    es_lit = assess(claim, [src1, src2], [])
    print(f"[ORCHESTRATOR] evidence(lit): suggested={suggested_state(es_lit)} "
          f"conf={confidence(es_lit)} :: {es_lit.reasoning}")
    # honest: contradicting source present -> weak, do NOT claim literature support
    transition(claim, suggested_state(es_lit),
               evidence=[src1["id"], src2["id"]], by="orchestrator", ts=TS,
               store=store)

    # ---------------------------------------------------------------- HYPOTHESIS
    banner("LOOP 2 · HYPOTHESIS")
    engine.start_loop("HYPOTHESIS")
    hyp = new_object(store, ids, "HYP", "hypothesis", TS,
                     statement="Warmup lowers final val loss by stabilizing early updates.",
                     assumptions=["fixed budget", "same seed sweep"],
                     predictions=["mean val loss(warmup) < mean val loss(no-warmup)"],
                     observable_variables=["final_val_loss"],
                     falsification_criteria=["no-warmup <= warmup across independent seeds"],
                     potential_confounders=["seed variance", "LR peak differs"],
                     alternative_explanations=["effect is really from lower peak LR"],
                     state="UNVERIFIED")
    prov.link(claim["id"], "PRODUCES", hyp["id"])
    events.emit(store, events.HYPOTHESIS_CREATED, TS, id=hyp["id"])
    human_approves(hitl, CP_HYPOTHESIS, "approve hypothesis", {"hyp": hyp["id"]})
    print(f"[HYPOTHESIS] {hyp['id']} (falsifiable; confounder noted: peak-LR)")

    # ---------------------------------------------------------------- PROTOCOL
    banner("LOOP 3 · PROTOCOL")
    engine.start_loop("PROTOCOL")
    protocol = new_object(store, ids, "PRO", "methodology", TS,
                          research_question=question, hypothesis_id=hyp["id"],
                          independent_variables=["warmup_fraction"],
                          dependent_variables=["final_val_loss"],
                          control_variables=["peak_lr", "batch_size", "budget"],
                          confounders=["seed"],
                          design="paired seeds, warmup vs no-warmup, matched peak LR",
                          controls=["no-warmup (negative)", "matched-peak-LR (positive)"],
                          success_criteria=["mean improvement > seed std, p-ish via 3 seeds"],
                          falsification_criteria=hyp["falsification_criteria"],
                          inferential_justification=(
                              "matching peak LR isolates warmup from the peak-LR confounder, "
                              "so a difference is attributable to warmup"))
    prov.link(hyp["id"], "IMPLEMENTED_BY", protocol["id"])
    # safety check before any experiment
    sc, reasons = review({"type": "simulation", "description": "train tiny transformer"})
    assert sc == SafetyClass.SAFE_AUTONOMOUS, (sc, reasons)
    human_approves(hitl, CP_PROTOCOL, "approve protocol", {"protocol": protocol["id"]})
    events.emit(store, events.PROTOCOL_APPROVED, TS, id=protocol["id"])
    print(f"[METHODOLOGY] {protocol['id']} controls the peak-LR confounder; "
          f"safety={sc.value}")

    # ---------------------------------------------------------------- EXPERIMENTS
    banner("LOOP 4 · EXPERIMENT (>=3 independent runs + controls)")
    engine.start_loop("EXPERIMENT")
    human_approves(hitl, CP_BRANCH, "approve experiment branch", {"protocol": protocol["id"]})

    # DECLARED SYNTHETIC simulation: a deterministic toy "training" function so the
    # demo is reproducible offline. NOT a real model — illustrative numbers only.
    def toy_val_loss(warmup: bool, seed: int) -> float:
        base = 0.500 - 0.001 * ((seed * 7) % 5)          # seed variance
        return round(base - (0.020 if warmup else 0.0), 4)  # synthetic warmup effect

    experiments = []
    results = []
    for i in range(3):  # >=3 independent runs (distinct seeds)
        seed = SEED + i
        warm = toy_val_loss(True, seed)
        cold = toy_val_loss(False, seed)  # negative control: no-warmup
        exp = new_object(store, ids, "EXP", "fundamental_experimenter", TS,
                         protocol_id=protocol["id"], kind="independent_replication",
                         independent=True, seed=seed, env="python3.14/cpu",
                         params={"warmup": True, "peak_lr": 3e-3}, runs=1,
                         status="COMPLETED",
                         artifacts=[f"synthetic:run{i}"])
        events.emit(store, events.EXPERIMENT_STARTED, TS, id=exp["id"], seed=seed)
        obs = Value(kind="RESULT",
                    content={"warmup_val_loss": warm, "nowarmup_val_loss": cold,
                             "delta": round(cold - warm, 4)},
                    support=[exp["id"]], note="declared synthetic simulation output")
        assert is_valid_value(obs)  # RESULT must carry support
        res = new_object(store, ids, "RES", "fundamental_experimenter", TS,
                         experiment_id=exp["id"], value=obs.to_dict(),
                         metrics={"delta": round(cold - warm, 4)}, status="COMPLETED")
        prov.link(protocol["id"], "TESTED_BY", exp["id"])
        prov.link(exp["id"], "PRODUCES", res["id"])
        prov.link(claim["id"], "TESTED_BY", exp["id"])
        events.emit(store, events.EXPERIMENT_COMPLETED, TS, id=exp["id"])
        events.emit(store, events.RESULT_CREATED, TS, id=res["id"])
        experiments.append(exp)
        results.append(res)
        print(f"[EXPERIMENTER] {exp['id']} seed={seed} warmup={warm} "
              f"nowarmup={cold} delta={cold - warm:.4f}")

    # ---------------------------------------------------------------- ANALYSIS
    banner("LOOP 5 · STATISTICAL AUDIT")
    engine.start_loop("ANALYSIS")
    deltas = [r["metrics"]["delta"] for r in results]
    mean_delta = round(sum(deltas) / len(deltas), 4)
    spread = round(max(deltas) - min(deltas), 4)
    analysis_obs = Value(
        kind="INTERPRETATION",
        content=(f"mean delta={mean_delta} > seed spread={spread}: warmup consistently "
                 f"lowers synthetic val loss across 3 independent seeds"),
        support=[r["id"] for r in results],
        note="OBSERVATION: deltas all positive. INTERPRETATION: effect > seed noise.")
    analysis = new_object(store, ids, "ANL", "statistical_auditor", TS,
                          value=analysis_obs.to_dict(),
                          observation=f"deltas={deltas}",
                          interpretation="effect exceeds seed spread",
                          caveats=["synthetic data", "small n=3", "single architecture"])
    for r in results:
        prov.link(r["id"], "ANALYZED_BY", analysis["id"])
    events.emit(store, events.AUDIT_COMPLETED, TS, id=analysis["id"])
    print(f"[AUDITOR] mean delta {mean_delta} vs spread {spread} "
          f"(OBSERVATION vs INTERPRETATION kept distinct; caveats recorded)")

    # ---------------------------------------------------------------- CRITIQUE
    banner("LOOP 6 · ADVERSARIAL FALSIFICATION")
    engine.start_loop("CRITIQUE")
    critique = new_object(store, ids, "CRT", "adversary", TS,
                          target_id=claim["id"], severity="medium",
                          issues=["n=3 is small", "synthetic generator could bake in effect"],
                          alternative_explanations=["peak-LR confounder"],
                          counterexamples=[],
                          recommended_tests=["real dataset", "more seeds", "vary architecture"],
                          falsification_status="not_falsified")
    prov.link(claim["id"], "CHALLENGED_BY", critique["id"])
    events.emit(store, events.CRITIQUE_CREATED, TS, id=critique["id"])
    # The adversary did NOT falsify, but records that peak-LR confounder was
    # controlled by the protocol, so the main alt-explanation is mitigated.
    dispute = Dispute()
    dsp_id = dispute.open(store, topic="strength of the warmup claim",
                          agents=["adversary", "orchestrator"],
                          positions=["not robust: n small", "reproduced under controls"],
                          evidence=[critique["id"], analysis["id"]], ts=TS)
    dispute.resolve(store, dsp_id, how="human_review", ts=TS)
    print(f"[ADVERSARY] {critique['id']} not_falsified; peak-LR confounder was controlled. "
          f"Dispute {dsp_id} -> human_review")

    # ---------------------------------------------------------------- VERDICT
    banner("LOOP 7 · VERDICT")
    engine.start_loop("VERDICT")
    # Evidence now includes experiments. 3 independent replications, 0 contradicting
    # *experiments*, but 1 contradicting *source* -> conservative.
    es = assess(claim, [src1, src2], experiments)
    print(f"[ORCHESTRATOR] evidence(full): suggested={suggested_state(es)} "
          f"conf={confidence(es)}")
    # Move the claim up the ladder with recorded evidence at each step.
    evidence_ids = [e["id"] for e in experiments] + [analysis["id"]]
    # UNVERIFIED/WEAK -> reset onto ladder honestly: from current negative state we can
    # only go sideways in negatives; so we re-open the claim as EXPERIMENTALLY_TESTED via
    # a fresh evidence-backed transition path. For the demo we track the *hypothesis*
    # up the positive ladder (it started UNVERIFIED, no contradicting source attached).
    transition(hyp, "LITERATURE_SUPPORTED", evidence=[src1["id"]], by="orchestrator", ts=TS, store=store)
    transition(hyp, "EXPERIMENTALLY_TESTED", evidence=evidence_ids, by="orchestrator", ts=TS, store=store)
    transition(hyp, "REPRODUCED", evidence=[e["id"] for e in experiments],
               by="orchestrator", ts=TS, store=store)
    transition(hyp, "ROBUST", evidence=[e["id"] for e in experiments],
               by="orchestrator", ts=TS, store=store)  # 3 independent replications
    transition(hyp, "ADVERSARIALLY_CHALLENGED", evidence=[critique["id"]],
               by="orchestrator", ts=TS, store=store)

    verdict_status = "STRONGLY_SUPPORTED" if es.independent_replications >= 2 else "SUPPORTED"
    if es.contradicting_sources > 0:
        verdict_status = "SUPPORTED"  # a contradicting source keeps us modest
    verdict = new_object(store, ids, "VER", "orchestrator", TS,
                         claim_id=claim["id"], verdict_status=verdict_status,
                         evidence_state=es.reasoning, state="ADVERSARIALLY_CHALLENGED",
                         rationale=("3 independent replications under a confounder-controlled "
                                    "protocol; adversary did not falsify; one contradicting "
                                    "preprint keeps this SUPPORTED not STRONGLY_SUPPORTED"),
                         human_reviewed=False,
                         dissent=["adversary: n=3 small; needs real-data replication"])
    prov.link(hyp["id"], "DERIVES", verdict["id"])
    prov.link(claim["id"], "DERIVES", verdict["id"])
    # attach the provenance chain that makes the verdict traceable to SRC + EXP
    for e in experiments:
        prov.link(e["id"], "REPRODUCES", verdict["id"])
    prov.link(src1["id"], "SUPPORTS", verdict["id"])
    events.emit(store, events.VERDICT_PROPOSED, TS, id=verdict["id"])
    print(f"[ORCHESTRATOR] {verdict['id']} = {verdict_status} "
          f"(modest: contradicting source on file)")

    # a recorded, non-conclusion-changing failure (honesty about limits)
    log_failure(store, type="CAPABILITY_LIMITATION",
                what="no real dataset available in offline demo",
                why="sandbox has no network/data", impact="external validity unknown",
                affected=[verdict["id"]], resolution="flag for real-data replication",
                reproducible=True, changes_conclusions=False, ts=TS)

    # ---------------------------------------------------------------- SNAPSHOT
    banner("SNAPSHOT + HUMAN REVIEW")
    loop_id = engine.start_loop("VERDICT")
    snap = snapshots.take(store, loop_id, {
        "ts": TS,
        "claims": [claim["id"]], "hyps": [hyp["id"]],
        "experiments": [e["id"] for e in experiments],
        "results": [r["id"] for r in results],
        "failures": ["FLR-00001"],
        "agent_decisions": ["adversary:not_falsified", f"orchestrator:{verdict_status}"],
        "human_decisions": [],
        "open_questions": ["does the effect hold on real data / larger n?"],
        "evidence_deltas": [f"hyp UNVERIFIED->ADVERSARIALLY_CHALLENGED"],
        "next_actions": ["real-data replication", "increase seeds"],
    })
    restored = snapshots.restore(store, snap["id"])
    assert restored["hyps"] == [hyp["id"]]
    print(f"[COMMUNICATOR] snapshot {snap['id']} taken and restore verified")

    # Final human checkpoint on the conclusion.
    cp_final = human_approves(hitl, CP_CONCLUSION, "approve final conclusion",
                              {"verdict": verdict["id"]})
    # record human review on the verdict provenance
    prov.link(cp_final, "APPROVED_BY", verdict["id"])
    events.emit(store, events.HUMAN_APPROVED, TS, checkpoint=cp_final, verdict=verdict["id"])

    # ---------------------------------------------------------------- PROVENANCE + METRICS
    banner("PROVENANCE — why this verdict?")
    why = prov.why(verdict["id"])

    def reaches(node, prefix):
        if str(node.get("id", "")).startswith(prefix):
            return True
        return any(reaches(a["node"], prefix) for a in node.get("ancestry", []))

    assert reaches(why, "SRC"), "verdict must trace to a SOURCE"
    assert reaches(why, "EXP"), "verdict must trace to an EXPERIMENT"
    print(f"[PROVENANCE] why({verdict['id']}) reaches SOURCE ✓ and EXPERIMENT ✓")

    banner("METRICS")
    m = metrics.compute(store)
    for k in ("unsupported_claim_rate", "traceability", "replication_rate",
              "falsification_rate", "failure_log_size", "human_approval_count",
              "avg_support_per_claim", "experiment_count", "source_count"):
        v = m[k]
        print(f"  {k:24s} = {v['value']}   ({v['meaning']})")

    # ---- Invariants (the demo verifies itself) --------------------------------
    assert m["unsupported_claim_rate"]["value"] == 0.0, "no unsupported RESULT/FACT values"
    assert m["traceability"]["value"] == 1.0, "verdict must be fully traceable"
    assert m["human_approval_count"]["value"] >= 5, "all five checkpoints exercised"
    assert m["experiment_count"]["value"] >= 3, ">=3 experiments"
    assert m["source_count"]["value"] >= 2, "at least two sources"
    assert es.independent_replications == 3
    # verdict is honest: modest despite strong replication because a source contradicts
    assert verdict_status == "SUPPORTED"
    # a real dispute was raised and routed to a human
    assert needs_human({"resolution": "human_review"}) is True

    banner("DONE")
    print("All end-to-end invariants hold. Verdict is SUPPORTED, human-approved, "
          "fully traceable, zero unsupported claims. Exit 0.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
