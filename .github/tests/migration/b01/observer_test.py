#!/usr/bin/env python3
"""Observer parser, drift and non-destructive build-tree guard controls."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from numeric_capture import split_events, compare, negative
from prepare_observer import prepare
from capture import REPO


class ObserverTests(unittest.TestCase):
    def test_copies_native_assembly_dependencies_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'source'
            prepare(dest)
            for name in ('Asm/arm64/LzmaDecOpt.S', 'Asm/x86/AesOpt.asm'):
                self.assertTrue((dest / name).is_file(), name)
                self.assertEqual((dest / name).read_bytes(), (REPO / name).read_bytes())

    def test_preserves_non_observer_stderr_bytes(self):
        raw = b'\xffdiagnostic\r\nB01_NATIVE {"event":"item_result","NOperationResult":3}\r\nlast\x00'
        events, normal = split_events(raw)
        self.assertEqual(normal, b'\xffdiagnostic\r\nlast\x00')
        self.assertEqual(events, [{'event': 'item_result', 'NOperationResult': 3}])

    def test_rejects_malformed_observer_json(self):
        with self.assertRaises(json.JSONDecodeError):
            split_events(b'B01_NATIVE broken\n')

    def test_refuses_existing_destination_without_modifying_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / 'preserve'
            marker.write_bytes(b'unchanged')
            with self.assertRaisesRegex(ValueError, 'must not exist'):
                prepare(Path(tmp))
            self.assertEqual(marker.read_bytes(), b'unchanged')

    def test_actual_capture_negative_controls(self):
        report = json.loads(Path(REPORT_PATH).read_text())
        negative(report)
        changed = copy.deepcopy(report)
        changed['observations'] = {}
        with self.assertRaises(ValueError):
            compare(changed, report)


if __name__ == '__main__':
    REPORT_PATH = sys.argv.pop(1)
    unittest.main()
