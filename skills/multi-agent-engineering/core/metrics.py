"""System integrity metrics computed from the store.

Each metric is {value, how, meaning}. Metrics that cannot be computed from the
available data return value=None with an explanatory how/meaning.
"""
from __future__ import annotations

from .provenance import Provenance

_VALUE_KEYS = ("value", "content", "result", "conclusion")


def _values(obj: dict) -> list[dict]:
    """Extract embedded Value-shaped dicts (having a 'kind') from an object."""
    out = []
    for k in _VALUE_KEYS:
        v = obj.get(k)
        if isinstance(v, dict) and "kind" in v:
            out.append(v)
    for v in obj.get("values", []) or []:
        if isinstance(v, dict) and "kind" in v:
            out.append(v)
    return out


def _m(value, how: str, meaning: str) -> dict:
    return {"value": value, "how": how, "meaning": meaning}


def compute(store) -> dict:
    """Return the 14 integrity metrics."""
    prov = Provenance(store)
    claims = store.all("CLM")
    results = store.all("RES")
    hyps = store.all("HYP")
    experiments = store.all("EXP")
    verdicts = store.all("VER")
    sources = store.all("SRC")
    failures = store.all("FLR")
    disputes = store.all("DSP")

    # 1. unsupported_claim_rate
    bearing = claims + results
    unsupported = 0
    counted = 0
    for obj in bearing:
        for v in _values(obj):
            if v["kind"] in ("RESULT", "FACT"):
                counted += 1
                if not v.get("support"):
                    unsupported += 1
    ucr = (unsupported / counted) if counted else 0.0

    # 2. traceability: VER objects whose why() reaches >=1 SRC and >=1 EXP.
    def _reaches(node: dict, prefix: str) -> bool:
        if str(node.get("id", "")).startswith(prefix):
            return True
        for a in node.get("ancestry", []):
            if _reaches(a["node"], prefix):
                return True
        return False

    traced = 0
    for ver in verdicts:
        w = prov.why(ver["id"])
        if _reaches(w, "SRC") and _reaches(w, "EXP"):
            traced += 1
    traceability = (traced / len(verdicts)) if verdicts else None

    # 3. replication_rate: experiments marked independent among those completed.
    completed = [e for e in experiments if e.get("status") == "COMPLETED"]
    indep = [e for e in completed if e.get("independent") is True]
    replication_rate = (len(indep) / len(completed)) if completed else None

    # 4. contradiction_count
    contradictions = sum(
        1 for l in prov._load() if l["rel"] == "CONTRADICTS"
    ) if hasattr(prov, "_load") else None

    # 5. falsification_rate: falsified hypotheses / hypotheses.
    falsified = [h for h in hyps if h.get("state") == "FALSIFIED"]
    falsification_rate = (len(falsified) / len(hyps)) if hyps else None

    # 6. failure_log_size
    failure_log_size = len(failures)

    # 7. dispute_count
    dispute_count = len(disputes)

    # 8. unresolved_dispute_count
    unresolved = sum(1 for d in disputes if d.get("status") != "RESOLVED")

    # 9. human_approval_count: checkpoints (CHK) carrying a human_approval record.
    checkpoints = store.all("CHK")
    approvals = sum(1 for c in checkpoints if c.get("human_approval"))

    # 10. avg_support_per_claim
    supports = []
    for obj in bearing:
        for v in _values(obj):
            supports.append(len(v.get("support", [])))
    avg_support = (sum(supports) / len(supports)) if supports else None

    # 11. source_count
    source_count = len(sources)

    # 12. hypothesis_count
    hypothesis_count = len(hyps)

    # 13. experiment_count
    experiment_count = len(experiments)

    # 14. robust_verdict_rate: verdicts in ROBUST/HUMAN_REVIEWED.
    strong = [v for v in verdicts if v.get("state") in ("ROBUST", "HUMAN_REVIEWED")]
    robust_verdict_rate = (len(strong) / len(verdicts)) if verdicts else None

    return {
        "unsupported_claim_rate": _m(
            ucr, "fraction of RESULT/FACT Values with empty support",
            "high means claims asserted without backing"),
        "traceability": _m(
            traceability, "fraction of verdicts whose provenance reaches >=1 SRC and >=1 EXP",
            "how many conclusions trace back to sources and experiments"),
        "replication_rate": _m(
            replication_rate, "independent completed experiments / completed experiments",
            "how much of the work is independently replicated"),
        "contradiction_count": _m(
            contradictions, "count of CONTRADICTS provenance links",
            "amount of internal disagreement in the graph"),
        "falsification_rate": _m(
            falsification_rate, "FALSIFIED hypotheses / all hypotheses",
            "how often hypotheses were killed (healthy science falsifies)"),
        "failure_log_size": _m(
            failure_log_size, "count of FLR-* records",
            "how much failure was honestly recorded"),
        "dispute_count": _m(
            dispute_count, "count of DSP-* records",
            "how much adversarial review occurred"),
        "unresolved_dispute_count": _m(
            unresolved, "DSP-* not marked RESOLVED",
            "open disagreements still needing resolution"),
        "human_approval_count": _m(
            approvals, "checkpoints carrying a human_approval record",
            "human oversight actually exercised"),
        "avg_support_per_claim": _m(
            avg_support, "mean len(support) across value-bearing objects",
            "average depth of backing per claim"),
        "source_count": _m(
            source_count, "count of SRC-* objects",
            "size of the literature base"),
        "hypothesis_count": _m(
            hypothesis_count, "count of HYP-* objects",
            "breadth of hypotheses explored"),
        "experiment_count": _m(
            experiment_count, "count of EXP-* objects",
            "amount of experimentation performed"),
        "robust_verdict_rate": _m(
            robust_verdict_rate, "verdicts in ROBUST/HUMAN_REVIEWED / all verdicts",
            "share of conclusions that reached the top of the ladder"),
    }
