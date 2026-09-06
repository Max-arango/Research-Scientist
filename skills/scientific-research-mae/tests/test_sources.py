"""Phase 5: litsearch record -> SOURCE bridge. Offline (no network)."""
import tempfile
import unittest
from pathlib import Path

from srmae import Store
from srmae.ids import IdGen
from srmae.sources import source_from_record


def _store():
    return Store(tempfile.mkdtemp(prefix="srmae_src_"))


class TestSources(unittest.TestCase):
    def test_real_doi_record_is_retrievable(self):
        store = _store()
        ids = IdGen(store)
        rec = {"doi": "10.1016/j.cell.2015.09.020", "url": "https://doi.org/x",
               "title": "A real paper", "authors": ["Doe, J"],
               "year": 2015, "source_type": "peer_reviewed",
               "retrievable": True, "origin": "crossref"}
        src = source_from_record(store, ids, rec)
        self.assertTrue(src["id"].startswith("SRC-"))
        self.assertTrue(src["retrievable"])
        self.assertEqual(src["doi"], "10.1016/j.cell.2015.09.020")
        self.assertNotIn("quality_assessment", src)  # agent's job, not the bridge's

    def test_no_identifier_is_not_retrievable(self):
        store = _store()
        ids = IdGen(store)
        rec = {"doi": None, "url": None, "arxiv_id": None, "title": "Mystery",
               "source_type": "secondary", "retrievable": False}
        src = source_from_record(store, ids, rec)
        self.assertFalse(src["retrievable"])
        self.assertIsNone(src["doi"])

    def test_buggy_record_claiming_retrievable_without_id_raises(self):
        store = _store()
        ids = IdGen(store)
        rec = {"doi": None, "url": None, "arxiv_id": None,
               "source_type": "preprint", "retrievable": True}
        with self.assertRaises(ValueError):
            source_from_record(store, ids, rec)

    def test_unknown_source_type_falls_back_to_secondary(self):
        store = _store()
        ids = IdGen(store)
        rec = {"doi": "10.1/x", "url": None, "title": "t",
               "source_type": "totally_made_up", "retrievable": True,
               "origin": "crossref"}
        src = source_from_record(store, ids, rec)
        self.assertEqual(src["source_type"], "secondary")

    def test_arxiv_only_record_is_retrievable(self):
        store = _store()
        ids = IdGen(store)
        rec = {"doi": None, "url": "http://arxiv.org/abs/2401.00001",
               "arxiv_id": "2401.00001", "title": "Preprint",
               "source_type": "preprint", "retrievable": True, "origin": "arxiv"}
        src = source_from_record(store, ids, rec)
        self.assertTrue(src["retrievable"])
        self.assertEqual(src["arxiv_id"], "2401.00001")


if __name__ == "__main__":
    unittest.main()