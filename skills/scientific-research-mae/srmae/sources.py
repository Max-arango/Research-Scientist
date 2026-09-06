"""Bridge: litsearch.py records -> validated SOURCE spine objects.

Keeps the anti-hallucination contract at the machine layer: a record without a
real identifier becomes a SOURCE with retrievable=false and no quality score.
The RESEARCHER agent still owns the justified quality_assessment; this module
only stamps the retrievable facts the API actually returned.
"""
from __future__ import annotations

from .objects import new_object

_SOURCE_TYPES = {
    "peer_reviewed", "preprint", "thesis", "technical_report", "dataset",
    "conference_paper", "review_article", "blog", "forum", "secondary",
}


def source_from_record(store, idgen, record: dict, *, by: str = "researcher",
                       ts: str = "1970-01-01T00:00:00Z", stance: str = "supporting") -> dict:
    """Create a SOURCE object from a litsearch record.

    Only fields the upstream API actually returned are stamped. A record with no
    doi AND no url is retrievable=false — never invented. Raises ValueError on a
    record that claims retrievable but carries no identifier (guards a buggy caller).
    """
    doi = record.get("doi")
    url = record.get("url")
    arxiv = record.get("arxiv_id")
    has_id = bool(doi or url or arxiv)
    retrievable = bool(record.get("retrievable")) and has_id
    if record.get("retrievable") and not has_id:
        raise ValueError("record claims retrievable but has no doi/url/arxiv_id")

    stype = record.get("source_type", "secondary")
    if stype not in _SOURCE_TYPES:
        stype = "secondary"

    return new_object(
        store, idgen, "SRC", by, ts,
        title=record.get("title"),
        authors=record.get("authors", []) or [],
        doi=doi,
        url=url,
        arxiv_id=arxiv,
        source_type=stype,
        publication_date=str(record["year"]) if record.get("year") else None,
        venue=record.get("venue"),
        retrievable=retrievable,
        origin=record.get("origin"),
        stance=stance,
        # NO quality_assessment here — the agent must add the justified object.
        note="stamped from litsearch record; quality pending agent appraisal",
    )
