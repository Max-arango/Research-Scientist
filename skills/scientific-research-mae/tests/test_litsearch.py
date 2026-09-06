"""Phase 5: litsearch pure-function tests. OFFLINE — no network calls.

Only the parse/format helpers are unit-tested here; the network subcommands are
integration-tested by the researcher demo (which is skipped when offline).
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import litsearch  # noqa: E402


class TestLitsearchPure(unittest.TestCase):
    def test_issued_year_parses(self):
        self.assertEqual(litsearch._issued_year({"date-parts": [[2015, 9, 20]]}), 2015)

    def test_issued_year_handles_missing(self):
        self.assertIsNone(litsearch._issued_year(None))
        self.assertIsNone(litsearch._issued_year({}))
        self.assertIsNone(litsearch._issued_year({"date-parts": [[]]}))

    def test_crossref_type_map(self):
        self.assertEqual(litsearch._CROSSREF_TYPE["journal-article"], "peer_reviewed")
        self.assertEqual(litsearch._CROSSREF_TYPE["posted-content"], "preprint")
        # unmapped types are handled by the caller's .get(default="secondary")
        self.assertNotIn("weird-type", litsearch._CROSSREF_TYPE)

    def test_cite_bibtex_shape(self):
        # monkeypatch _get_json to avoid network
        real = litsearch._get_json
        litsearch._get_json = lambda url: {"message": {
            "author": [{"family": "Bailey", "given": "Andrew"}],
            "issued": {"date-parts": [[2015]]},
            "title": ["A Paper"], "container-title": ["Cell"]}}
        try:
            out = litsearch._cite("10.1/x", "bibtex")
        finally:
            litsearch._get_json = real
        self.assertIn("@article{bailey2015", out)
        self.assertIn("doi = {10.1/x}", out)
        self.assertIn("journal = {Cell}", out)

    def test_cite_csl_shape(self):
        real = litsearch._get_json
        litsearch._get_json = lambda url: {"message": {
            "author": [{"family": "Bailey", "given": "Andrew"}],
            "issued": {"date-parts": [[2015]]},
            "title": ["A Paper"], "container-title": ["Cell"]}}
        try:
            out = json.loads(litsearch._cite("10.1/x", "csl"))
        finally:
            litsearch._get_json = real
        self.assertEqual(out["DOI"], "10.1/x")
        self.assertEqual(out["type"], "article-journal")

    def test_verify_flags_retracted_title(self):
        real = litsearch._get_json
        litsearch._get_json = lambda url: {"message": {
            "title": ["RETRACTED: bad science"], "type": "journal-article",
            "update-to": []}}
        try:
            out = litsearch._verify("10.1/x")
        finally:
            litsearch._get_json = real
        self.assertTrue(out["is_retracted"])

    def test_verify_clean_title_not_retracted(self):
        real = litsearch._get_json
        litsearch._get_json = lambda url: {"message": {
            "title": ["Good science"], "type": "journal-article", "update-to": []}}
        try:
            out = litsearch._verify("10.1/x")
        finally:
            litsearch._get_json = real
        self.assertFalse(out["is_retracted"])


if __name__ == "__main__":
    unittest.main()