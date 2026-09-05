import unittest

from srmae import assess, suggested_state, confidence


class TestEvidence(unittest.TestCase):
    def test_zero_evidence_raises(self):
        with self.assertRaises(ValueError):
            assess("claim", [], [])

    def test_never_robust_under_two_replications(self):
        es = assess(
            "c",
            [{"source_type": "peer_reviewed"}],
            [{"independent": True}],  # only 1 independent
        )
        self.assertNotEqual(suggested_state(es), "ROBUST")

    def test_robust_needs_two_independent(self):
        es = assess(
            "c",
            [{"source_type": "peer_reviewed"}, {"source_type": "peer_reviewed"}],
            [{"independent": True}, {"independent": True}],
        )
        self.assertEqual(suggested_state(es), "ROBUST")

    def test_confidence_capped_high_uncertainty(self):
        es = assess("c", [{"stance": "contradicting"}], [{"independent": True}])
        self.assertEqual(es.uncertainty, "high")
        self.assertLessEqual(confidence(es), 0.5)

    def test_confidence_upper_cap(self):
        es = assess(
            "c",
            [{"source_type": "peer_reviewed"}] * 5,
            [{"independent": True}] * 3,
        )
        self.assertLessEqual(confidence(es), 0.9)

    def test_reasoning_non_empty(self):
        es = assess("c", [{"source_type": "peer_reviewed"}], [])
        self.assertTrue(es.reasoning.strip())

    def test_falsified_wins(self):
        es = assess("c", [{"source_type": "peer_reviewed"}], [{"falsified": True}])
        self.assertEqual(suggested_state(es), "FALSIFIED")


if __name__ == "__main__":
    unittest.main()
