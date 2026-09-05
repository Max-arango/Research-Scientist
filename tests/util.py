"""Test helpers: fresh temp Store and a fixed timestamp."""
from __future__ import annotations

import tempfile

from srmae import Store

TS = "2026-01-01T00:00:00Z"


def fresh_store() -> Store:
    """Return a Store rooted in a fresh temp directory."""
    return Store(tempfile.mkdtemp(prefix="srmae-test-"))
