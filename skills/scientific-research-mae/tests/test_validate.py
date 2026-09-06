"""Phase 4: schema validator."""
import json
import tempfile
import unittest
from pathlib import Path

from srmae.objects import new_object
from srmae.validate import validate, SchemaError


class TestValidate(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="srmae_val_")
        # Mirror the schema layout the validator expects.
        repo_schemas = Path(__file__).resolve().parent.parent / "schemas"
        root_schemas = Path(self.root) / "schemas"
        root_schemas.mkdir()
        for p in repo_schemas.iterdir():
            (root_schemas / p.name).write_text(p.read_text())
        # Wrap root so the validator walks the same paths the package uses in prod.
        self.store_root = str(Path(self.root) / "store")
        Path(self.store_root).mkdir()
        schemas_link = Path(self.store_root).parent / "schemas"
        if not schemas_link.exists():
            schemas_link.symlink_to(root_schemas)

    def test_validate_claim_ok(self):
        from srmae import Store
        store = Store(self.store_root)
        from srmae.ids import IdGen
        ids = IdGen(store)
        obj = new_object(store, ids, "CLM", "researcher", "1970-01-01T00:00:00Z",
                         statement="x", source_ids=[], confidence=0.0,
                         status="UNVERIFIED", epistemic_state="UNVERIFIED",
                         claim_id="CLM-00001")
        # No exception = ok.
        validate(self.store_root, "CLM", obj)

    def test_validate_claim_missing_required(self):
        from srmae import Store
        store = Store(self.store_root)
        with self.assertRaises(SchemaError):
            validate(self.store_root, "CLM", {"id": "CLM-00001"})  # no statement

    def test_validate_claim_bad_enum(self):
        from srmae import Store
        store = Store(self.store_root)
        bogus = {"id": "CLM-00001", "version": 1, "created_at": "1970-01-01T00:00:00Z",
                 "created_by": "test", "provenance": [], "claim_id": "CLM-00001",
                 "statement": "x", "source_ids": [], "confidence": 0.0,
                 "status": "BOGUS_STATE", "epistemic_state": "UNVERIFIED"}
        with self.assertRaises(SchemaError):
            validate(self.store_root, "CLM", bogus)

    def test_unknown_prefix_no_crash(self):
        # CHK has no shipped schema; validator silently passes.
        validate(self.store_root, "CHK", {"id": "CHK-00001"})

    def test_new_object_validate_true_rejects(self):
        from srmae import Store
        from srmae.ids import IdGen
        store = Store(self.store_root)
        ids = IdGen(store)
        with self.assertRaises(SchemaError):
            new_object(store, ids, "CLM", "t", "1970-01-01T00:00:00Z",
                       validate=True,  # missing required fields
                       statement="x")  # missing source_ids, confidence, status, claim_id


if __name__ == "__main__":
    unittest.main()