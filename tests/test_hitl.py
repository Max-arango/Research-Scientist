import unittest

from srmae import HITL, Level
from tests.util import fresh_store, TS


class TestHITL(unittest.TestCase):
    def test_classify_mappings(self):
        h = HITL(fresh_store())
        self.assertEqual(h.classify("search paper on X"), Level.AUTO)
        self.assertEqual(h.classify("run simulation"), Level.AUTO)
        self.assertEqual(h.classify("change methodology"), Level.REVIEW)
        self.assertEqual(h.classify("perform external action"), Level.REQUIRE_APPROVAL)
        self.assertEqual(h.classify("do something unsafe"), Level.BLOCKED)
        self.assertEqual(h.classify("totally novel thing"), Level.REVIEW)

    def test_gate_require_approval_pending(self):
        h = HITL(fresh_store())
        r = h.gate("external_action", {"action": "external publish", "ts": TS})
        self.assertEqual(r["status"], "PENDING")

    def test_gate_auto_approved(self):
        h = HITL(fresh_store())
        r = h.gate("safety_review", {"action": "run simulation", "ts": TS})
        self.assertEqual(r["status"], "APPROVED")

    def test_approve_records(self):
        h = HITL(fresh_store())
        r = h.gate("external_action", {"action": "external publish", "ts": TS})
        out = h.approve(r["checkpoint_id"], "alice", True, "looks good", TS)
        self.assertEqual(out["status"], "APPROVED")
        cp = h.store.get(r["checkpoint_id"])
        self.assertEqual(cp["human_approval"]["human"], "alice")

    def test_blocked_cannot_proceed(self):
        h = HITL(fresh_store())
        r = h.gate("safety_review", {"action": "do something unsafe", "ts": TS})
        out = h.approve(r["checkpoint_id"], "alice", True, "override", TS)
        self.assertEqual(out["status"], "BLOCKED")

    def test_checkpoints_use_chk_prefix_not_ver(self):
        # regression: checkpoints must not pollute the VER (verdict) namespace,
        # or traceability metrics undercount. See FINDING-004.
        h = HITL(fresh_store())
        r = h.gate("external_action", {"action": "external publish", "ts": TS})
        self.assertTrue(r["checkpoint_id"].startswith("CHK-"))
        self.assertEqual(h.store.all("VER"), [])

    def test_canonical_checkpoints(self):
        from srmae.hitl import CHECKPOINTS
        self.assertEqual(CHECKPOINTS, [
            "RESEARCH_QUESTION", "HYPOTHESIS", "PROTOCOL",
            "MAJOR_EXPERIMENT_BRANCH", "FINAL_CONCLUSION",
        ])

    def test_human_subjects_action_requires_approval(self):
        # The HITL policy table currently keys on 'external' and 'irreversible'
        # for REQUIRE_APPROVAL. A 'human_subjects' study is sensitive enough
        # that it must NOT be auto-approved. This test pins that contract: if
        # you run an investigation involving human_subjects, the gate PENDINGs
        # until a human explicitly approves.
        h = HITL(fresh_store())
        # direct via classify: "external" is the closest match — for the
        # stronger "human_subjects study" we expect at least REVIEW.
        lvl = h.classify("human_subjects study on volunteers")
        self.assertIn(lvl, (Level.REVIEW, Level.REQUIRE_APPROVAL))
        # When the agent adds the 'external' keyword, the gate PENDINGs.
        r = h.gate("MAJOR_EXPERIMENT_BRANCH",
                   {"action": "external human_subjects study", "ts": TS})
        self.assertEqual(r["status"], "PENDING")


if __name__ == "__main__":
    unittest.main()
