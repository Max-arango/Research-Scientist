import unittest

from srmae import metrics, Provenance
from tests.util import fresh_store


class TestMetrics(unittest.TestCase):
    def test_unsupported_claim_rate_zero_on_clean_store(self):
        store = fresh_store()
        store.put({
            "id": "CLM-00001", "version": 1,
            "content": {"kind": "FACT", "content": "x", "support": ["SRC-00001"]},
        })
        store.put({
            "id": "RES-00001", "version": 1,
            "value": {"kind": "RESULT", "content": 3.14, "support": ["EXP-00001"]},
        })
        m = metrics.compute(store)
        self.assertEqual(m["unsupported_claim_rate"]["value"], 0.0)

    def test_unsupported_claim_rate_detects_empty_support(self):
        store = fresh_store()
        store.put({
            "id": "RES-00001", "version": 1,
            "value": {"kind": "RESULT", "content": 1, "support": []},
        })
        m = metrics.compute(store)
        self.assertEqual(m["unsupported_claim_rate"]["value"], 1.0)

    def test_traceability_computed(self):
        store = fresh_store()
        for oid in ("SRC-00001", "EXP-00001", "VER-00001"):
            store.put({"id": oid, "version": 1})
        p = Provenance(store)
        p.link("SRC-00001", "SUPPORTS", "EXP-00001")
        p.link("EXP-00001", "PRODUCES", "VER-00001")
        m = metrics.compute(store)
        self.assertEqual(m["traceability"]["value"], 1.0)

    def test_all_metrics_have_shape(self):
        m = metrics.compute(fresh_store())
        self.assertEqual(len(m), 14)
        for name, entry in m.items():
            self.assertIn("value", entry)
            self.assertIn("how", entry)
            self.assertIn("meaning", entry)


if __name__ == "__main__":
    unittest.main()
