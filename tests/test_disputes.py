import unittest

from srmae import Dispute, needs_human
from tests.util import fresh_store, TS


class TestDisputes(unittest.TestCase):
    def test_open_resolve(self):
        store = fresh_store()
        did = Dispute.open(
            store, "is X true", ["a", "b"],
            [{"a": "yes"}, {"b": "no"}], ["SRC-00001"], TS,
        )
        self.assertTrue(did.startswith("DSP-"))
        resolved = Dispute.resolve(store, did, "consensus: yes", TS)
        self.assertEqual(resolved["status"], "RESOLVED")
        self.assertEqual(store.get(did)["resolution"], "consensus: yes")

    def test_needs_human_on_human_review(self):
        self.assertTrue(needs_human({"resolution": "human_review"}))
        self.assertTrue(needs_human({"severity": "high"}))
        self.assertFalse(needs_human({"severity": "normal", "resolution": "auto"}))


if __name__ == "__main__":
    unittest.main()
