import unittest

from srmae import snapshots
from tests.util import fresh_store, TS


class TestSnapshots(unittest.TestCase):
    def test_take_restore_roundtrip(self):
        store = fresh_store()
        state = {
            "ts": TS,
            "claims": ["CLM-00001"],
            "hyps": ["HYP-00001"],
            "experiments": [],
            "results": ["RES-00001"],
            "failures": ["FLR-00001"],
            "agent_decisions": [{"a": "reviewer", "d": "reject"}],
            "human_decisions": [],
            "open_questions": ["why?"],
            "evidence_deltas": [],
            "next_actions": ["replicate"],
        }
        snap = snapshots.take(store, "LOOP-1", state)
        restored = snapshots.restore(store, snap["id"])
        for k in ("claims", "hyps", "results", "failures",
                  "agent_decisions", "open_questions", "next_actions"):
            self.assertEqual(restored[k], state[k])
        self.assertEqual(restored["loop_id"], "LOOP-1")
        self.assertEqual(restored["ts"], TS)


if __name__ == "__main__":
    unittest.main()
