"""Integration test (AC13): the end-to-end demo runs clean and exits 0.

The demo asserts its own scientific invariants (traceability==1, unsupported==0, 5
human approvals, >=3 experiments, honest SUPPORTED verdict). Running it here makes
those invariants part of the suite.
"""
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO = os.path.join(HERE, "examples", "demo_research.py")


class TestIntegrationDemo(unittest.TestCase):
    def test_demo_runs_and_exits_zero(self):
        proc = subprocess.run([sys.executable, DEMO], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"demo failed:\n{proc.stdout}\n{proc.stderr}")
        self.assertIn("All end-to-end invariants hold", proc.stdout)
        self.assertIn("traceability             = 1.0", proc.stdout)
        self.assertIn("unsupported_claim_rate   = 0.0", proc.stdout)


if __name__ == "__main__":
    unittest.main()
