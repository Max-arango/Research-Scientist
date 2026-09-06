#!/usr/bin/env python3
"""Bundled literature tool for the RESEARCHER agent — real retrieval, no fabrication.

The researcher agent CALLS this script; it does not read the source. Output is
JSON on stdout, ready to become SOURCE objects (via srmae.sources.source_from_record).

Anti-hallucination contract:
  - Every record carries a REAL identifier (DOI / arXiv id / OpenAlex id) returned
    by the upstream API, or `retrievable=false`. A missing field is `null`, never
    invented. This script assigns NO quality score — that is the agent's job with a
    justified {score, reasoning, evidence, uncertainty} object.

Stdlib only (urllib + json + xml.etree). No external deps.

Subcommands:
  search "<query>" [--source crossref|openalex|arxiv] [--rows N]
  verify <DOI>                       resolve + retraction flag via Crossref
  expand <DOI> [--direction refs|citations]   citation-graph via OpenAlex
  cite <DOI> [--format bibtex|csl]   formatted reference via Crossref

Examples:
  python3 scripts/litsearch.py search "intermittent fasting insulin" --source crossref --rows 5
  python3 scripts/litsearch.py verify 10.1016/j.cell.2015.09.020
  python3 scripts/litsearch.py expand 10.1016/j.cell.2015.09.020 --direction refs
  python3 scripts/litsearch.py cite 10.1016/j.cell.2015.09.020 --format bibtex
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

_UA = "srmae-litsearch/0.1 (research harness; mailto:research@example.org)"
_TIMEOUT = 20

# Crossref type -> our source_type. Conservative: only journal/proceedings map to
# a peer-reviewed venue signal; everything else stays honest.
_CROSSREF_TYPE = {
    "journal-article": "peer_reviewed",
    "proceedings-article": "conference_paper",
    "posted-content": "preprint",
    "dissertation": "thesis",
    "report": "technical_report",
    "dataset": "dataset",
    "book-chapter": "secondary",
    "review-article": "review_article",
}


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
        return r.read()


def _get_json(url: str) -> dict:
    return json.loads(_get(url))


# ----------------------------------------------------------------- search
def _search_crossref(query: str, rows: int) -> list[dict]:
    q = urllib.parse.urlencode({
        "query": query, "rows": rows,
        "select": "DOI,title,author,type,issued,URL,container-title",
    })
    data = _get_json(f"https://api.crossref.org/works?{q}")
    out = []
    for it in data.get("message", {}).get("items", []):
        doi = it.get("DOI")
        out.append({
            "id": f"doi:{doi}" if doi else None,
            "doi": doi,
            "arxiv_id": None,
            "title": (it.get("title") or [None])[0],
            "authors": [f"{a.get('given','')} {a.get('family','')}".strip()
                        for a in it.get("author", []) if isinstance(a, dict)],
            "year": _issued_year(it.get("issued")),
            "venue": (it.get("container-title") or [None])[0],
            "source_type": _CROSSREF_TYPE.get(it.get("type"), "secondary"),
            "url": it.get("URL"),
            "retrievable": bool(doi),
            "origin": "crossref",
        })
    return out


def _search_openalex(query: str, rows: int) -> list[dict]:
    q = urllib.parse.urlencode({"search": query, "per-page": rows})
    data = _get_json(f"https://api.openalex.org/works?{q}")
    out = []
    for it in data.get("results", []):
        doi = (it.get("doi") or "").replace("https://doi.org/", "") or None
        out.append({
            "id": it.get("id"),
            "doi": doi,
            "arxiv_id": None,
            "title": it.get("title"),
            "authors": [a["author"]["display_name"]
                        for a in it.get("authorships", [])
                        if a.get("author", {}).get("display_name")],
            "year": it.get("publication_year"),
            "venue": (it.get("primary_location") or {}).get("source", {}).get("display_name")
                     if it.get("primary_location") else None,
            "source_type": "peer_reviewed" if it.get("type") == "article" else "secondary",
            "url": it.get("id"),
            "retrievable": bool(it.get("id")),
            "origin": "openalex",
        })
    return out


def _search_arxiv(query: str, rows: int) -> list[dict]:
    q = urllib.parse.urlencode({
        "search_query": f"all:{query}", "start": 0, "max_results": rows,
    })
    xml = _get(f"http://export.arxiv.org/api/query?{q}")
    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(xml)
    out = []
    for e in root.findall("a:entry", ns):
        aid_url = e.findtext("a:id", default="", namespaces=ns)
        aid = aid_url.rsplit("/abs/", 1)[-1] if "/abs/" in aid_url else aid_url
        out.append({
            "id": f"arxiv:{aid}" if aid else None,
            "doi": e.findtext("a:doi", default=None, namespaces=ns),
            "arxiv_id": aid or None,
            "title": (e.findtext("a:title", default="", namespaces=ns) or "").strip(),
            "authors": [a.findtext("a:name", default="", namespaces=ns)
                        for a in e.findall("a:author", ns)],
            "year": (e.findtext("a:published", default="", namespaces=ns) or "")[:4] or None,
            "venue": "arXiv",
            "source_type": "preprint",
            "url": aid_url or None,
            "retrievable": bool(aid),
            "origin": "arxiv",
        })
    return out


def _issued_year(issued):
    try:
        return issued["date-parts"][0][0]
    except (TypeError, KeyError, IndexError):
        return None


# ----------------------------------------------------------------- verify
def _verify(doi: str) -> dict:
    """Resolve a DOI via Crossref; flag retraction if the record says so."""
    try:
        data = _get_json(f"https://api.crossref.org/works/{urllib.parse.quote(doi)}")
    except Exception as e:  # noqa: BLE001 — network/HTTP failure is a real signal
        return {"doi": doi, "resolves": False, "is_retracted": None,
                "type": None, "error": f"{type(e).__name__}: {e}"}
    msg = data.get("message", {})
    updates = msg.get("update-to", []) or []
    title = (msg.get("title") or [None])[0]
    # Crossref exposes retraction three ways; check all — update-to is often
    # empty even when the title carries the publisher's "RETRACTED:" prefix.
    retracted = (
        any(u.get("type") == "retraction" for u in updates)
        or msg.get("type") == "retraction"
        or bool(title and title.strip().upper().startswith("RETRACTED"))
    )
    return {
        "doi": doi,
        "resolves": True,
        "is_retracted": retracted,
        "type": msg.get("type"),
        "title": title,
    }


# ----------------------------------------------------------------- expand
def _expand(doi: str, direction: str) -> dict:
    """Citation graph via OpenAlex: references (backward) or citing works (forward)."""
    work = _get_json(f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi)}")
    if direction == "refs":
        refs = work.get("referenced_works", []) or []
        return {"doi": doi, "direction": "refs", "count": len(refs),
                "related_openalex_ids": refs[:50]}
    # citations: follow cited_by_api_url
    cby = work.get("cited_by_api_url")
    ids = []
    if cby:
        data = _get_json(cby + "&per-page=50")
        ids = [w.get("id") for w in data.get("results", []) if w.get("id")]
    return {"doi": doi, "direction": "citations", "count": len(ids),
            "related_openalex_ids": ids}


# ----------------------------------------------------------------- cite
def _cite(doi: str, fmt: str) -> str:
    data = _get_json(f"https://api.crossref.org/works/{urllib.parse.quote(doi)}")
    m = data.get("message", {})
    authors = m.get("author", []) or []
    year = _issued_year(m.get("issued"))
    title = (m.get("title") or [""])[0]
    venue = (m.get("container-title") or [""])[0]
    if fmt == "csl":
        return json.dumps({
            "type": "article-journal", "DOI": doi, "title": title,
            "container-title": venue, "issued": {"date-parts": [[year]]},
            "author": [{"family": a.get("family"), "given": a.get("given")}
                       for a in authors],
        }, indent=2, ensure_ascii=False)
    # bibtex
    first = authors[0].get("family", "anon").lower() if authors else "anon"
    key = f"{first}{year or ''}"
    auth_str = " and ".join(
        f"{a.get('family','')}, {a.get('given','')}".strip(", ") for a in authors)
    lines = [f"@article{{{key},",
             f"  title = {{{title}}},",
             f"  author = {{{auth_str}}},"]
    if venue:
        lines.append(f"  journal = {{{venue}}},")
    if year:
        lines.append(f"  year = {{{year}}},")
    lines.append(f"  doi = {{{doi}}}")
    lines.append("}")
    return "\n".join(lines)


# ----------------------------------------------------------------- CLI
def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="multi-source literature search")
    s.add_argument("query")
    s.add_argument("--source", choices=["crossref", "openalex", "arxiv"],
                   default="crossref")
    s.add_argument("--rows", type=int, default=5)

    v = sub.add_parser("verify", help="resolve a DOI + retraction flag")
    v.add_argument("doi")

    e = sub.add_parser("expand", help="citation graph (refs/citations)")
    e.add_argument("doi")
    e.add_argument("--direction", choices=["refs", "citations"], default="refs")

    c = sub.add_parser("cite", help="format a reference")
    c.add_argument("doi")
    c.add_argument("--format", choices=["bibtex", "csl"], default="bibtex")

    args = p.parse_args(argv)

    if args.cmd == "search":
        fn = {"crossref": _search_crossref, "openalex": _search_openalex,
              "arxiv": _search_arxiv}[args.source]
        print(json.dumps(fn(args.query, args.rows), indent=2, ensure_ascii=False))
    elif args.cmd == "verify":
        print(json.dumps(_verify(args.doi), indent=2, ensure_ascii=False))
    elif args.cmd == "expand":
        print(json.dumps(_expand(args.doi, args.direction), indent=2, ensure_ascii=False))
    elif args.cmd == "cite":
        print(_cite(args.doi, args.format))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())