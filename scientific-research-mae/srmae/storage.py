"""Append-only JSON object store with versioning, events, and counters."""
from __future__ import annotations

import json
from pathlib import Path


class Store:
    """Filesystem-backed append-only store.

    Objects are written to objects/<ID>.v<version>.json and never overwritten.
    Events append to events.jsonl. Counters persist in counters.json.
    """

    def __init__(self, root: str):
        self.root = Path(root)
        self.objects_dir = self.root / "objects"
        self.events_path = self.root / "events.jsonl"
        self.counters_path = self.root / "counters.json"
        self.objects_dir.mkdir(parents=True, exist_ok=True)

    def put(self, obj: dict) -> dict:
        """Write obj at its declared version; never overwrite a prior version."""
        oid = obj["id"]
        version = obj.get("version", 1)
        path = self.objects_dir / f"{oid}.v{version}.json"
        if path.exists():
            raise ValueError(f"version {version} of {oid} already exists (append-only)")
        path.write_text(json.dumps(obj, indent=2, sort_keys=True))
        return obj

    def get(self, id: str) -> dict:
        """Return the latest version of an object by id."""
        versions = sorted(
            self.objects_dir.glob(f"{id}.v*.json"),
            key=lambda p: int(p.name.rsplit(".v", 1)[1].split(".json")[0]),
        )
        if not versions:
            raise KeyError(id)
        return json.loads(versions[-1].read_text())

    def all(self, prefix: str | None = None) -> list:
        """Return latest version of every object, optionally filtered by id prefix."""
        latest: dict[str, tuple[int, Path]] = {}
        for p in self.objects_dir.glob("*.v*.json"):
            oid, ver = p.name.rsplit(".v", 1)
            ver_n = int(ver.split(".json")[0])
            if prefix and not oid.startswith(prefix):
                continue
            if oid not in latest or ver_n > latest[oid][0]:
                latest[oid] = (ver_n, p)
        return [json.loads(p.read_text()) for _, p in latest.values()]

    def append_event(self, ev: dict) -> dict:
        """Append an event dict as a JSON line."""
        with self.events_path.open("a") as f:
            f.write(json.dumps(ev, sort_keys=True) + "\n")
        return ev

    def events(self) -> list:
        """Read all events."""
        if not self.events_path.exists():
            return []
        return [json.loads(line) for line in self.events_path.read_text().splitlines() if line.strip()]

    def counters(self) -> dict:
        """Return persisted counter map {prefix: n}."""
        if not self.counters_path.exists():
            return {}
        return json.loads(self.counters_path.read_text())

    def set_counter(self, prefix: str, n: int) -> None:
        """Persist counter n for prefix."""
        c = self.counters()
        c[prefix] = n
        self.counters_path.write_text(json.dumps(c, sort_keys=True))
