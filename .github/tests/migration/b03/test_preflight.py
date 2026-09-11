#!/usr/bin/env python3
"""Offline safety tests. Modelled writes are NOT native oracle evidence."""
import errno
import io
import unittest
from pathlib import Path
import tempfile
from types import SimpleNamespace
from unittest.mock import patch
import full_volume


class TailTests(unittest.TestCase):
    def test_cleanup_runs_after_probe_failure_and_checks_detachment(self):
        # Only in-memory platform/command seams and empty temp directories.
        # No hdiutil/diskpart process, mount, sparse file, or filling occurs.
        for still_mounted in (False, True):
            with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent / 'work') as tmp:
                case = Path(tmp)
                root = case / 'mounted'
                active = False
                calls = []
                def command(argv, cwd):
                    nonlocal active
                    calls.append(argv)
                    if 'attach' in argv:
                        active = True
                    if 'detach' in argv:
                        active = still_mounted
                    return dict(exit=0)
                original_stat = Path.stat
                def stat(path, *args, **kwargs):
                    if path == root:
                        return SimpleNamespace(st_dev=2 if active else 1)
                    if path == case:
                        return SimpleNamespace(st_dev=1)
                    return original_stat(path, *args, **kwargs)
                record = {}
                with patch.object(full_volume.os, 'name', 'posix'), \
                     patch.object(full_volume.platform, 'system', return_value='Darwin'), \
                     patch.object(full_volume.shutil, 'disk_usage', return_value=SimpleNamespace(free=1 << 30)), \
                     patch.object(full_volume, 'check_mount', return_value={}), \
                     patch.object(Path, 'stat', stat):
                    expected = 'still mounted' if still_mounted else 'deliberate probe failure'
                    with self.assertRaisesRegex(AssertionError, expected):
                        with full_volume.mounted(case, record, command, lambda path: {}):
                            raise AssertionError('deliberate probe failure')
                self.assertEqual(calls[-1], ['hdiutil', 'detach', str(root)])
                self.assertEqual(record['detached'], not still_mounted)

    def test_workflow_contains_no_full_capture_or_push_native_entry(self):
        workflow = (Path(__file__).resolve().parents[3] / 'workflows/b03-native.yml').read_text()
        self.assertIn("if: github.event_name == 'workflow_dispatch' && github.run_attempt == 1 && inputs.reviewed_sha == github.sha", workflow)
        self.assertNotIn('/run.py ', workflow)
        self.assertNotIn('/freeze.py ', workflow)
        self.assertIn('os: [macos-latest, windows-latest]', workflow)

    def test_fill_is_bounded_even_if_no_enospc(self):
        position = 0
        def write(data):
            nonlocal position
            position += len(data)
            return len(data)
        with patch.object(full_volume, 'LIMIT', 1 << 20):
            with self.assertRaisesRegex(AssertionError, 'exceeded'):
                full_volume.fill_tail(write, lambda: position, {})

    def test_unrelated_error_and_zero_progress_rejected(self):
        def denied(data):
            raise OSError(errno.EACCES, 'model denied')
        for write in (denied, lambda data: 0):
            with self.assertRaises(AssertionError):
                full_volume.fill_tail(write, lambda: 0, {})

    def test_execution_gate_rejects_unreviewed_and_rerun(self):
        import preflight
        good = dict(GITHUB_EVENT_NAME='workflow_dispatch', GITHUB_RUN_ATTEMPT='1',
                    GITHUB_SHA='a' * 40, B03_REVIEWED_SHA='a' * 40)
        preflight.check_gate(good, 'Windows')
        for key, value in [('GITHUB_EVENT_NAME', 'push'), ('GITHUB_RUN_ATTEMPT', '2'),
                           ('B03_REVIEWED_SHA', 'b' * 40)]:
            with self.assertRaises(AssertionError):
                preflight.check_gate(dict(good, **{key: value}), 'Windows')
        with self.assertRaises(AssertionError):
            preflight.check_gate(good, 'Linux')

    def test_large_request_enospc_does_not_mean_tail_is_full(self):
        # Deliberately model residual capacity from both failed native reports.
        for residual in (167936 - 16384, 499712 - 16384):
            with self.subTest(residual=residual):
                stream = io.BytesIO()
                def write(data):
                    left = residual - stream.tell()
                    if len(data) > left:
                        raise OSError(errno.ENOSPC, 'model full')
                    return stream.write(data)
                record = {}
                with patch.object(full_volume, 'LIMIT', 1 << 20):
                    full_volume.fill_tail(write, stream.tell, record)
                self.assertLess(residual - stream.tell(), 4096)
                self.assertEqual(record['fill_error']['errno'], errno.ENOSPC)
                self.assertEqual(record['fill_steps'][-1]['chunk'], 4096)


if __name__ == '__main__':
    (Path(__file__).resolve().parent / 'work').mkdir(exist_ok=True)
    unittest.main()
