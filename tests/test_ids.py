import unittest

from srmae import IdGen, Store
from tests.util import fresh_store


class TestIds(unittest.TestCase):
    def test_sequential_and_zero_pad(self):
        g = IdGen(fresh_store())
        self.assertEqual(g.next("CLM"), "CLM-00001")
        self.assertEqual(g.next("CLM"), "CLM-00002")
        self.assertEqual(g.next("SRC"), "SRC-00001")

    def test_restart_continuity(self):
        store = fresh_store()
        IdGen(store).next("HYP")
        IdGen(store).next("HYP")
        # New Store on same root, new IdGen -> continues.
        store2 = Store(str(store.root))
        self.assertEqual(IdGen(store2).next("HYP"), "HYP-00003")

    def test_bad_prefix_raises(self):
        with self.assertRaises(ValueError):
            IdGen(fresh_store()).next("XXX")


if __name__ == "__main__":
    unittest.main()
