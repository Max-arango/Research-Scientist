import unittest

from tests.util import fresh_store


class TestStorage(unittest.TestCase):
    def test_put_get_latest_and_history(self):
        store = fresh_store()
        store.put({"id": "CLM-00001", "version": 1, "x": "a"})
        store.put({"id": "CLM-00001", "version": 2, "x": "b"})
        self.assertEqual(store.get("CLM-00001")["x"], "b")
        # both versions on disk
        v1 = store.objects_dir / "CLM-00001.v1.json"
        v2 = store.objects_dir / "CLM-00001.v2.json"
        self.assertTrue(v1.exists() and v2.exists())

    def test_no_overwrite(self):
        store = fresh_store()
        store.put({"id": "SRC-00001", "version": 1})
        with self.assertRaises(ValueError):
            store.put({"id": "SRC-00001", "version": 1})

    def test_all_prefix_filter(self):
        store = fresh_store()
        store.put({"id": "CLM-00001", "version": 1})
        store.put({"id": "SRC-00001", "version": 1})
        self.assertEqual([o["id"] for o in store.all("CLM")], ["CLM-00001"])
        self.assertEqual(len(store.all()), 2)

    def test_events_append(self):
        store = fresh_store()
        store.append_event({"type": "A", "ts": "t"})
        store.append_event({"type": "B", "ts": "t"})
        evs = store.events()
        self.assertEqual([e["type"] for e in evs], ["A", "B"])


if __name__ == "__main__":
    unittest.main()
