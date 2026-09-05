import unittest

from srmae import review, SafetyClass


class TestSafety(unittest.TestCase):
    def test_bio_pathogen_blocked(self):
        cls, reasons = review({"description": "culture a pathogen"})
        self.assertEqual(cls, SafetyClass.BLOCKED)
        self.assertTrue(reasons)

    def test_physical_requires_human(self):
        cls, reasons = review({"type": "physical", "irreversible": True})
        self.assertEqual(cls, SafetyClass.HUMAN_APPROVAL_REQUIRED)

    def test_human_subjects_requires_human(self):
        cls, _ = review({"description": "study with human_subjects"})
        self.assertEqual(cls, SafetyClass.HUMAN_APPROVAL_REQUIRED)

    def test_simulation_safe(self):
        cls, reasons = review({"description": "pure simulation of orbits"})
        self.assertEqual(cls, SafetyClass.SAFE_AUTONOMOUS)

    def test_default_supervised(self):
        cls, _ = review({"description": "reorganize notes"})
        self.assertEqual(cls, SafetyClass.SUPERVISED)


if __name__ == "__main__":
    unittest.main()
