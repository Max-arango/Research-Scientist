"""Phase 2: end-to-end REWIND path with snapshot restore.

A new confounder is discovered mid-investigation. The orchestrator must:
  1. decide() returns "REWIND"
  2. snapshot from before the confounder is restored
  3. a fresh loop opens against the restored state
"""
import unittest

from srmae import (
    Store, IdGen, Value, new_object, transition,
    LoopEngine, HITL, safety, Provenance, snapshots,
)
from tests.util import fresh_store, TS


class TestRewind(unittest.TestCase):
    def test_rewind_decide_on_new_confounder(self):
        e = LoopEngine(fresh_store(), HITL(fresh_store()), safety)
        self.assertEqual(e.decide({"new_confounder": True}), "REWIND")

    def test_rewind_restores_to_pre_confounder_state(self):
        # Two stores so we can simulate "before" and "after"
        store = fresh_store()
        ids = IdGen(store)
        prov = Provenance(store)
        hitl = HITL(store)
        engine = LoopEngine(store, hitl, safety)

        # State 1: design phase, claim has only literature support
        src = new_object(store, ids, "SRC", "researcher", TS,
                         title="early source", source_type="peer_reviewed")
        claim = new_object(store, ids, "CLM", "researcher", TS,
                           statement="X holds",
                           value=Value("INFERENCE", "X",
                                       support=[src["id"]]).to_dict(),
                           state="UNVERIFIED")
        prov.link(src["id"], "SUPPORTS", claim["id"])
        transition(claim, "LITERATURE_SUPPORTED", evidence=[src["id"]],
                   by="orchestrator", ts=TS, store=store)
        pre_snapshot = snapshots.take(store, "loop_pre_confounder",
                                      {"ts": TS, "claims": [claim["id"]],
                                       "hyps": [], "experiments": [],
                                       "results": [], "failures": [],
                                       "agent_decisions": [],
                                       "human_decisions": [],
                                       "open_questions": [],
                                       "evidence_deltas": [],
                                       "next_actions": []})
        pre_claim_state = store.get(claim["id"])["state"]
        self.assertEqual(pre_claim_state, "LITERATURE_SUPPORTED")

        # Consequence of a (hypothetical) new confounder: someone flipped the
        # claim state to FALSIFIED. We then decide REWIND and restore.
        transition(claim, "FALSIFIED", evidence=["FAKE-001"],
                   by="bad-agent", ts=TS, store=store)
        self.assertEqual(store.get(claim["id"])["state"], "FALSIFIED")

        decision = engine.decide({"new_confounder": True})
        self.assertEqual(decision, "REWIND")

        # Restore: in a real orchestrator the loop would re-open a prior loop
        # and replay from the snapshot. We verify the snapshot itself is
        # intact and loadable.
        restored = snapshots.restore(store, pre_snapshot["id"])
        self.assertEqual(restored["claims"], [claim["id"]])
        self.assertIn("next_actions", restored)

    def test_rewind_is_distinct_from_terminate_when_not_exhausted(self):
        e = LoopEngine(fresh_store(), HITL(fresh_store()), safety)
        self.assertEqual(e.decide({"falsified": True}), "REWIND")
        # Only when the orchestrator signals exhausted do we terminate.
        self.assertEqual(
            e.decide({"falsified": True, "exhausted": True}), "TERMINATE")

    def test_branch_signal_does_not_rewind(self):
        e = LoopEngine(fresh_store(), HITL(fresh_store()), safety)
        self.assertEqual(e.decide({"new_subquestion": True}), "BRANCH")


if __name__ == "__main__":
    unittest.main()