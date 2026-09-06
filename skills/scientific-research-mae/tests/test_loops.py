import unittest

from srmae import LoopEngine, HITL
from srmae import safety
from tests.util import fresh_store


class TestLoops(unittest.TestCase):
    def _engine(self):
        store = fresh_store()
        return LoopEngine(store, HITL(store), safety)

    def test_decide_mappings(self):
        e = self._engine()
        self.assertEqual(e.decide({"new_confounder": True}), "REWIND")
        self.assertEqual(e.decide({"unresolved_dispute": True}), "ESCALATE")
        self.assertEqual(e.decide({"all_criteria_met": True}), "TERMINATE")
        self.assertEqual(e.decide({"falsified": True}), "REWIND")
        self.assertEqual(e.decide({"falsified": True, "exhausted": True}), "TERMINATE")
        self.assertEqual(e.decide({"new_subquestion": True}), "BRANCH")
        self.assertEqual(e.decide({}), "CONTINUE")

    def test_start_loop_persisted(self):
        e = self._engine()
        lid = e.start_loop("EXPERIMENT")
        self.assertEqual(e.store.get(lid)["phase"], "EXPERIMENT")

    def test_stalled_repeated_signature(self):
        e = self._engine()
        self.assertTrue(e.stalled([{"signature": "S"}, {"signature": "S"}]))
        self.assertFalse(e.stalled([{"signature": "S"}, {"signature": "T"}]))
        self.assertFalse(e.stalled([{"signature": "S"}]))


if __name__ == "__main__":
    unittest.main()
