import unittest

from srmae import log_failure
from tests.util import fresh_store, TS


class TestFailures(unittest.TestCase):
    def test_log_failure_writes_flr(self):
        store = fresh_store()
        fid = log_failure(
            store, type="SCIENTIFIC", what="H1 wrong",
            why="data contradicts", impact="drop H1", affected=["HYP-00001"],
            resolution="abandon", reproducible=True, changes_conclusions=True, ts=TS,
        )
        self.assertTrue(fid.startswith("FLR-"))
        obj = store.get(fid)
        self.assertEqual(obj["type"], "SCIENTIFIC")
        self.assertTrue((store.objects_dir / f"{fid}.v1.json").exists())

    def test_bad_type_raises(self):
        store = fresh_store()
        with self.assertRaises(ValueError):
            log_failure(
                store, type="NOPE", what="", why="", impact="", affected=[],
                resolution="", reproducible=False, changes_conclusions=False, ts=TS,
            )


if __name__ == "__main__":
    unittest.main()
