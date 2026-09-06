"""Schema integrity (AC3) + code/schema consistency (guards the multi-builder drift
that produced FINDING-003)."""
import glob
import json
import os
import unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_DIR = os.path.join(HERE, "schemas")


class TestSchemas(unittest.TestCase):
    def test_all_schemas_parse(self):
        files = glob.glob(os.path.join(SCHEMA_DIR, "*.json"))
        self.assertGreaterEqual(len(files), 12, "expected >=12 schemas")
        for f in files:
            with open(f) as fh:
                json.load(fh)  # raises on invalid JSON

    def test_expected_schema_set(self):
        names = {os.path.basename(f)[:-5] for f in glob.glob(os.path.join(SCHEMA_DIR, "*.json"))}
        expected = {"value", "source", "claim", "hypothesis", "protocol", "experiment",
                    "result", "critique", "verdict", "snapshot", "dispute", "failure"}
        self.assertTrue(expected.issubset(names), f"missing: {expected - names}")

    @staticmethod
    def _load(name):
        with open(os.path.join(SCHEMA_DIR, name)) as fh:
            return json.load(fh)

    def test_failure_enum_matches_code(self):
        from srmae import FAILURE_TYPES
        d = self._load("failure.json")
        schema_enum = d["properties"]["type"]["enum"]
        self.assertEqual(sorted(schema_enum), sorted(FAILURE_TYPES),
                         "failure.json enum must match srmae.FAILURE_TYPES")

    def test_value_enum_matches_code(self):
        from srmae import VALUE_KINDS
        d = self._load("value.json")
        schema_enum = set(d["properties"]["kind"]["enum"])
        self.assertEqual(schema_enum, set(VALUE_KINDS),
                         "value.json kind enum must match srmae.VALUE_KINDS")

    def test_verdict_status_enum(self):
        d = self._load("verdict.json")

        def find_enum_containing(o, needle):
            if isinstance(o, dict):
                if o.get("enum") and needle in o["enum"]:
                    return o["enum"]
                for v in o.values():
                    r = find_enum_containing(v, needle)
                    if r:
                        return r
            elif isinstance(o, list):
                for x in o:
                    r = find_enum_containing(x, needle)
                    if r:
                        return r
            return None

        enum = find_enum_containing(d, "NOT_FALSIFIED")
        self.assertIsNotNone(enum, "verdict schema must include NOT_FALSIFIED status")
        self.assertEqual(set(enum), {"SUPPORTED", "NOT_FALSIFIED", "STRONGLY_SUPPORTED",
                                     "INCONCLUSIVE", "FALSIFIED"})


if __name__ == "__main__":
    unittest.main()
