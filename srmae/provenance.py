"""Provenance graph: typed links between objects, persisted and reloadable."""
from __future__ import annotations

import json
from pathlib import Path

REL = {
    "SUPPORTS", "CONTRADICTS", "DERIVES", "PRODUCES", "TESTED_BY",
    "CHALLENGED_BY", "IMPLEMENTED_BY", "REPRODUCES", "ANALYZED_BY", "APPROVED_BY",
}


class Provenance:
    """Directed provenance links stored in links.jsonl under the store root."""

    def __init__(self, store):
        self.store = store
        self.path = Path(store.root) / "links.jsonl"

    def _load(self) -> list[dict]:
        if not self.path.exists():
            return []
        return [json.loads(l) for l in self.path.read_text().splitlines() if l.strip()]

    def link(self, src: str, rel: str, dst: str) -> dict:
        """Create src --rel--> dst."""
        if rel not in REL:
            raise ValueError(f"unknown rel {rel!r}")
        link = {"src": src, "rel": rel, "dst": dst}
        with self.path.open("a") as f:
            f.write(json.dumps(link, sort_keys=True) + "\n")
        return link

    def parents(self, id: str) -> list:
        """Return [(parent_id, rel)] for links pointing at id."""
        return [(l["src"], l["rel"]) for l in self._load() if l["dst"] == id]

    def children(self, id: str) -> list:
        """Return [(child_id, rel)] for links originating at id."""
        return [(l["dst"], l["rel"]) for l in self._load() if l["src"] == id]

    def _obj_meta(self, id: str) -> dict:
        """Pull experiment metadata and approvals from a stored object, if any."""
        try:
            obj = self.store.get(id)
        except KeyError:
            return {}
        meta: dict = {"id": id}
        for k in ("seed", "env", "params"):
            if k in obj:
                meta[k] = obj[k]
        if id.startswith("EXP"):
            meta["experiment"] = True
        if "human_approval" in obj:
            meta["human_approval"] = obj["human_approval"]
        return meta

    def why(self, id: str, _seen: set | None = None) -> dict:
        """Nested ancestry of id including experiment metadata (seed/env/params)
        and any human approvals found among ancestors. Cycle-guarded.

        Walks BOTH directions: parents (things that point AT id — e.g. sources
        that support a claim) and children (things id points TO — e.g. the
        experiments a claim was tested by). A claim "tested by" an experiment
        is as much a part of why-the-claim as the source that produced it.
        """
        if _seen is None:
            _seen = set()
        node = self._obj_meta(id)
        if id in _seen:
            node["cycle"] = True
            return node
        _seen = _seen | {id}
        ancestry = []
        # upstream: parents of id (things pointing AT id)
        for pid, rel in self.parents(id):
            ancestry.append({"rel": f"<-{rel}", "node": self.why(pid, _seen)})
        # downstream: children of id (things id points TO) — but only along
        # "uses" / "produces" / "tested_by" / "reproduces" / "challenged_by" /
        # "analyzed_by" / "implemented_by" relations, to avoid spurious loops.
        _DOWNSTREAM = {
            "TESTED_BY", "PRODUCES", "REPRODUCES", "CHALLENGED_BY",
            "ANALYZED_BY", "IMPLEMENTED_BY", "DERIVES", "APPROVED_BY",
        }
        for cid, rel in self.children(id):
            if rel in _DOWNSTREAM:
                ancestry.append({"rel": f"->{rel}", "node": self.why(cid, _seen)})
        if ancestry:
            node["ancestry"] = ancestry
        return node
