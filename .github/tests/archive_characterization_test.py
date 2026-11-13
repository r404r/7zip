#!/usr/bin/env python3
"""Harness negative controls using a real built CLI and a real captured baseline.

Usage: python archive_characterization_test.py <7zz> <same-platform baseline>
Only temporary copies are deliberately damaged; checked-in oracles are untouched.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

EXE = str(Path(sys.argv.pop(1)).resolve(strict=True))
BASELINE = Path(sys.argv.pop(1)).resolve(strict=True)
HARNESS = Path(__file__).with_name("archive_characterization.py")


class HarnessControls(unittest.TestCase):
    def test_same_report_and_expect_is_rejected_without_overwriting(self):
        before = BASELINE.read_bytes()
        result = subprocess.run([sys.executable, str(HARNESS), EXE,
                                 "--report", str(BASELINE), "--expect", str(BASELINE)],
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 2)
        self.assertIn("must not overwrite", result.stderr)
        self.assertEqual(BASELINE.read_bytes(), before)

    def test_deliberate_observation_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data = json.loads(BASELINE.read_text())
            # Negative control, NOT a replacement golden or an engine observation.
            data["observations"]["capabilities"]["exit"] = 123456
            expected = root / "damaged.json"
            expected.write_text(json.dumps(data))
            report = root / "actual.json"
            result = subprocess.run([sys.executable, str(HARNESS), EXE,
                                     "--expect", str(expected), "--report", str(report)],
                                    capture_output=True, text=True, timeout=600)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Oracle disagreement", result.stderr)
            actual = json.loads(report.read_text())
            self.assertEqual(actual["result"], "FAILED")
            self.assertEqual(actual["observations"]["capabilities"]["exit"], 0)
            self.assertEqual(json.loads(expected.read_text())["observations"]["capabilities"]["exit"], 123456)

    def test_wrong_platform_baseline_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data = json.loads(BASELINE.read_text())
            data["provenance"]["system"] = "not-a-real-platform-negative-control"
            expected = root / "wrong-platform.json"
            expected.write_text(json.dumps(data))
            result = subprocess.run([sys.executable, str(HARNESS), EXE,
                                     "--expect", str(expected), "--report", str(root / "actual.json")],
                                    capture_output=True, text=True, timeout=600)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Baseline scope mismatch: system", result.stderr)


if __name__ == "__main__":
    unittest.main()
