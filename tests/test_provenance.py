import unittest

from srmae import Provenance
from tests.util import fresh_store, TS


class TestProvenance(unittest.TestCase):
    def _seed(self, store):
        for oid, extra in [
            ("SRC-00001", {}),
            ("CLM-00001", {}),
            ("EXP-00001", {"seed": 42, "env": "py3.14", "params": {"n": 10}}),
            ("RES-00001", {}),
            ("VER-00001", {}),
        ]:
            store.put({"id": oid, "version": 1, **extra})

    def test_why_reaches_source_and_experiment(self):
        store = fresh_store()
        self._seed(store)
        p = Provenance(store)
        p.link("SRC-00001", "SUPPORTS", "CLM-00001")
        p.link("CLM-00001", "TESTED_BY", "EXP-00001")
        p.link("EXP-00001", "PRODUCES", "RES-00001")
        p.link("RES-00001", "DERIVES", "VER-00001")

        w = p.why("VER-00001")

        def reaches(node, prefix):
            if str(node.get("id", "")).startswith(prefix):
                return True
            return any(reaches(a["node"], prefix) for a in node.get("ancestry", []))

        self.assertTrue(reaches(w, "SRC"))
        self.assertTrue(reaches(w, "EXP"))
        # experiment metadata surfaced
        self.assertIn("EXP-00001", repr(w))
        self.assertIn("42", repr(w))

    def test_cycle_guard(self):
        store = fresh_store()
        store.put({"id": "CLM-00001", "version": 1})
        store.put({"id": "CLM-00002", "version": 1})
        p = Provenance(store)
        p.link("CLM-00001", "DERIVES", "CLM-00002")
        p.link("CLM-00002", "DERIVES", "CLM-00001")
        # must terminate
        w = p.why("CLM-00001")
        self.assertIsInstance(w, dict)

    def test_bad_rel_raises(self):
        p = Provenance(fresh_store())
        with self.assertRaises(ValueError):
            p.link("A", "NOPE", "B")


if __name__ == "__main__":
    unittest.main()
