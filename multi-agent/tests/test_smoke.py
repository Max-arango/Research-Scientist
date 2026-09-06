"""Smoke test: the vendored core loads, IDs are stable, severity gates exist.
Stdlib only — no deps."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import (  # noqa: E402
    Store, IdGen, Value, is_valid_value, new_object,
    transition, assess, suggested_state, confidence,
    Provenance, snapshots, LoopEngine, HITL, Level, SafetyClass, review,
    Dispute, needs_human, log_failure, metrics,
)


class Smoke(unittest.TestCase):
    def test_imports(self):
        self.assertEqual(len([Level.AUTO, Level.REVIEW,
                              Level.REQUIRE_APPROVAL, Level.BLOCKED]), 4)
        self.assertEqual(SafetyClass.SAFE_AUTONOMOUS.value, "SAFE_AUTONOMOUS")

    def test_store_roundtrip(self):
        with tempfile.TemporaryDirectory() as root:
            store = Store(root)
            ids = IdGen(store)
            o = new_object(store, ids, "EVT", "test", "1970-01-01T00:00:00Z",
                           kind="loop", phase="QUESTION", status="OPEN")
            self.assertTrue(o["id"].startswith("EVT-"))
            again = store.get(o["id"])
            self.assertEqual(again["phase"], "QUESTION")

    def test_value_rejects_unsupported_fact(self):
        v = Value(kind="FACT", content="x")
        self.assertFalse(is_valid_value(v))
        v2 = Value(kind="FACT", content="x", support=["SRC-00001"])
        self.assertTrue(is_valid_value(v2))

    def test_evidence_engine_refuses_zero_evidence(self):
        with self.assertRaises(ValueError):
            assess({"id": "CLM-00001"}, [], [])

    def test_provenance_why_cycle_guarded(self):
        with tempfile.TemporaryDirectory() as root:
            store = Store(root)
            ids = IdGen(store)
            prov = Provenance(store)
            a = new_object(store, ids, "SRC", "t", "1970-01-01T00:00:00Z",
                           title="t")
            b = new_object(store, ids, "CLM", "t", "1970-01-01T00:00:00Z",
                           statement="s")
            prov.link(a["id"], "SUPPORTS", b["id"])
            why = prov.why(b["id"])
            self.assertIn("ancestry", why)

    def test_metrics_returns_expected_keys(self):
        with tempfile.TemporaryDirectory() as root:
            store = Store(root)
            m = metrics.compute(store)
            for k in ("unsupported_claim_rate", "traceability",
                      "replication_rate", "falsification_rate",
                      "failure_log_size", "human_approval_count"):
                self.assertIn(k, m)

    def test_safety_review(self):
        sc, reasons = review({"type": "simulation",
                              "description": "run on synthetic data"})
        self.assertEqual(sc, SafetyClass.SAFE_AUTONOMOUS)
        sc, reasons = review({"type": "bio", "description": "modify pathogen"})
        self.assertEqual(sc, SafetyClass.BLOCKED)

    def test_hitl_classify(self):
        with tempfile.TemporaryDirectory() as root:
            h = HITL(Store(root))
            self.assertEqual(h.classify("run simulation"), Level.AUTO)
            self.assertEqual(h.classify("change methodology"), Level.REVIEW)
            self.assertEqual(h.classify("external call"), Level.REQUIRE_APPROVAL)
            self.assertEqual(h.classify("unsafe action"), Level.BLOCKED)

    def test_dispute_needs_human(self):
        self.assertTrue(needs_human({"severity": "high"}))
        self.assertTrue(needs_human({"resolution": "human_review"}))
        self.assertFalse(needs_human({}))

    def test_failure_log_appends(self):
        with tempfile.TemporaryDirectory() as root:
            store = Store(root)
            fid = log_failure(store, type="TOOL", what="x", why="y",
                              impact="z", affected=[], resolution="r",
                              reproducible=False, changes_conclusions=False,
                              ts="1970-01-01T00:00:00Z")
            self.assertTrue(fid.startswith("FLR-"))


if __name__ == "__main__":
    unittest.main()