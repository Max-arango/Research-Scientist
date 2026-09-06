import unittest

from srmae import can_transition, transition, IllegalTransition
from tests.util import TS


class TestEpistemic(unittest.TestCase):
    def test_legal_ladder_step(self):
        self.assertTrue(can_transition("UNVERIFIED", "LITERATURE_SUPPORTED"))
        obj = {"state": "UNVERIFIED"}
        transition(obj, "LITERATURE_SUPPORTED", evidence=["SRC-00001"], by="a", ts=TS)
        self.assertEqual(obj["state"], "LITERATURE_SUPPORTED")
        self.assertEqual(len(obj["state_history"]), 1)

    def test_illegal_skip_raises(self):
        obj = {"state": "UNVERIFIED"}
        with self.assertRaises(IllegalTransition):
            transition(obj, "ROBUST", evidence=["x"], by="a", ts=TS)

    def test_strengthening_empty_evidence_raises(self):
        obj = {"state": "UNVERIFIED"}
        with self.assertRaises(IllegalTransition):
            transition(obj, "LITERATURE_SUPPORTED", evidence=[], by="a", ts=TS)

    def test_falsified_from_anywhere(self):
        for start in ("UNVERIFIED", "ROBUST", "EXPERIMENTALLY_TESTED"):
            obj = {"state": start}
            transition(obj, "FALSIFIED", evidence=[], by="a", ts=TS)
            self.assertEqual(obj["state"], "FALSIFIED")


if __name__ == "__main__":
    unittest.main()
