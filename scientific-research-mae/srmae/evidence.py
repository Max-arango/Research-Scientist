"""Evidence assessment: derive dimensions from sources/experiments and suggest
an epistemic state with deliberately modest, paired confidence."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EvidenceState:
    supporting_sources: int
    contradicting_sources: int
    independent_replications: int
    repetitions: int
    methodological_quality: str
    experimental_support: str
    uncertainty: str
    falsification_status: str
    reasoning: str


def assess(claim, sources: list, experiments: list) -> EvidenceState:
    """Derive an EvidenceState from evidence. Raises ValueError with no evidence.

    Source dicts may carry: stance ('supporting'|'contradicting'),
    source_type ('peer_reviewed' etc). Experiment dicts may carry:
    independent (bool), falsified (bool).
    """
    if not sources and not experiments:
        raise ValueError("cannot assess a claim with zero evidence")

    supporting = sum(1 for s in sources if s.get("stance", "supporting") != "contradicting")
    contradicting = sum(1 for s in sources if s.get("stance") == "contradicting")
    peer_reviewed = sum(1 for s in sources if s.get("source_type") == "peer_reviewed")

    independent = sum(1 for e in experiments if e.get("independent") is True)
    repetitions = sum(1 for e in experiments if e.get("independent") is not True)
    falsified = any(e.get("falsified") is True for e in experiments)

    if peer_reviewed >= 2:
        quality = "high"
    elif peer_reviewed == 1 or supporting >= 2:
        quality = "moderate"
    else:
        quality = "low"

    if independent >= 2:
        experimental_support = "strong"
    elif independent == 1 or repetitions >= 1:
        experimental_support = "moderate"
    elif experiments:
        experimental_support = "weak"
    else:
        experimental_support = "none"

    if falsified:
        uncertainty = "high"
    elif independent >= 2 and contradicting == 0:
        uncertainty = "low"
    elif supporting <= 1 or contradicting > 0:
        uncertainty = "high"
    else:
        uncertainty = "moderate"

    falsification_status = "falsified" if falsified else "not_falsified"

    reasoning = (
        f"{supporting} supporting source(s) ({peer_reviewed} peer-reviewed), "
        f"{contradicting} contradicting; {independent} independent replication(s), "
        f"{repetitions} repetition(s); methodological_quality={quality}, "
        f"experimental_support={experimental_support}, uncertainty={uncertainty}, "
        f"falsification_status={falsification_status}."
    )

    return EvidenceState(
        supporting_sources=supporting,
        contradicting_sources=contradicting,
        independent_replications=independent,
        repetitions=repetitions,
        methodological_quality=quality,
        experimental_support=experimental_support,
        uncertainty=uncertainty,
        falsification_status=falsification_status,
        reasoning=reasoning,
    )


def suggested_state(es: EvidenceState) -> str:
    """Suggest an epistemic state. Conservative: never ROBUST without >=2
    independent replications; never strong on a single source."""
    if es.falsification_status == "falsified":
        return "FALSIFIED"
    if es.contradicting_sources > es.supporting_sources:
        return "CONTRADICTED"
    if es.contradicting_sources > 0:
        return "WEAK_EVIDENCE"
    if es.supporting_sources <= 1 and es.independent_replications == 0:
        return "WEAK_EVIDENCE"

    if es.independent_replications >= 2:
        return "ROBUST"
    if es.independent_replications == 1 or es.repetitions >= 1:
        return "REPRODUCED"
    if es.experimental_support in ("moderate", "strong"):
        return "EXPERIMENTALLY_TESTED"
    if es.supporting_sources >= 2:
        return "LITERATURE_SUPPORTED"
    return "UNVERIFIED"


def confidence(es: EvidenceState) -> float:
    """Modest, paired confidence in 0..1. Capped at 0.9; <=0.5 when
    uncertainty is high. Always report alongside the epistemic state."""
    score = 0.1
    score += min(es.supporting_sources, 3) * 0.1
    score += min(es.independent_replications, 2) * 0.15
    score += min(es.repetitions, 2) * 0.05
    if es.methodological_quality == "high":
        score += 0.1
    elif es.methodological_quality == "moderate":
        score += 0.05
    score -= es.contradicting_sources * 0.15
    if es.falsification_status == "falsified":
        score = min(score, 0.1)
    if es.uncertainty == "high":
        score = min(score, 0.5)
    return max(0.0, min(0.9, round(score, 3)))
