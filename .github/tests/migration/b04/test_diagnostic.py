"""Offline controller tests. No compiler, native probe or sandbox launches."""
import base64
import hashlib
import io
import json
from pathlib import Path
import tempfile
import sys
import unittest
from unittest import mock


class DiagnosticTest(unittest.TestCase):
    def test_controller_stops_on_output_cap_or_native_cleanup_failure(self):
        import diagnostic as d
        for raw in (b'x' * 16385, b'B04-launch quiescent=false\n'):
            with self.subTest(raw_size=len(raw)), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                runner = d.BoundedRun(root)
                proc = mock.Mock(stdout=io.BytesIO(raw), stderr=io.BytesIO(b''), returncode=0)
                proc.poll.return_value = 0
                with mock.patch.object(d.subprocess, 'Popen', return_value=proc) as launch, \
                        mock.patch.object(d.os, 'killpg', create=True, side_effect=ProcessLookupError):
                    with self.assertRaises(RuntimeError):
                        runner(['unit-placeholder'], root, 'sandbox')
                    self.assertTrue(runner.failed)
                    with self.assertRaises(RuntimeError):
                        runner(['unit-placeholder'], root, 'different-label')
                    self.assertEqual(launch.call_count, 1)
                self.assertLessEqual(len(runner.last_pipe_bytes['sandbox.stdout']), 16384)

    def test_full_controller_exports_stopped_capture_and_cannot_repeat(self):
        import diagnostic as d
        import prerequisite as p
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(GITHUB_ACTIONS='true', GITHUB_EVENT_NAME='workflow_dispatch',
                       GITHUB_RUN_ATTEMPT='1', GITHUB_REPOSITORY='r404r/7zip',
                       GITHUB_REF='refs/heads/wt/t_2a64c953', GITHUB_SHA='a' * 40,
                       B04_APPROVED_SHA='a' * 40, B04_IMAGE='ubuntu-24.04',
                       ImageOS='ubuntu24', ImageVersion='unit-image', RUNNER_TEMP=tmp)
            commands = []

            def fake_process(command, **kwargs):
                # All process results in this unit test are synthetic. No native
                # execution and no evidence/golden files are produced from them.
                commands.append(command)
                cwd = kwargs['cwd']
                raw, code = b'', 0
                if command[0] == 'cc':
                    (cwd / 'probe').write_bytes(b'unit placeholder; never executed')
                elif command[-1] == '/usr/bin/true':
                    code = 1
                else:
                    raw = b''.join((name + ' 1 errno=0\n').encode() for name in p.INSIDE + p.OUTSIDE)
                proc = mock.Mock(stdout=io.BytesIO(raw), stderr=io.BytesIO(b''), returncode=code)
                proc.poll.return_value = code
                return proc

            stream = io.StringIO()
            with mock.patch.dict(d.os.environ, env, clear=True), \
                    mock.patch.object(d.platform, 'system', return_value='Linux'), \
                    mock.patch.object(d.platform, 'platform', return_value='unit-platform'), \
                    mock.patch.object(d.platform, 'machine', return_value='x86_64'), \
                    mock.patch.object(d.platform, 'freedesktop_os_release', create=True,
                                      return_value={'VERSION_ID': '24.04'}), \
                    mock.patch.object(d.subprocess, 'check_output', side_effect=['a' * 40, b'', 'a' * 40,
                                                                               'a' * 40, b'']), \
                    mock.patch.object(d.subprocess, 'Popen', side_effect=fake_process), \
                    mock.patch.object(d.os, 'killpg', create=True, side_effect=ProcessLookupError), \
                    mock.patch.object(d, 'observe'), mock.patch.object(d.sys, 'stdout', stream):
                self.assertEqual(d.main(), 2)
                count = len(commands)
                self.assertEqual(d.main(), 2)
                self.assertEqual(len(commands), count)
            self.assertEqual(len(commands), 3)  # Build, baseline, failed startup only.
            records = [json.loads(line.removeprefix('B04_RECORD '))
                       for line in stream.getvalue().splitlines() if line.startswith('B04_RECORD ')]
            report = json.loads(base64.b64decode(next(r['base64'] for r in records if r['name'] == 'report.json')))
            self.assertFalse(report['controls_pass'])
            self.assertNotIn('sandbox_returncode', report)
            self.assertEqual(report['startup_returncode'], 1)
            self.assertTrue((Path(tmp) / 'b04-approved-diagnostic' / 'attempt-consumed').is_file())

    def test_cleanup_removes_only_owned_data_and_preserves_attempt_marker(self):
        import diagnostic as d
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'attempt'
            root.mkdir()
            (root / 'control').write_bytes(b'only ours')
            d.cleanup(root)
            self.assertEqual([p.name for p in root.iterdir()], ['attempt-consumed'])

    def test_real_entry_rejects_unapproved_context_without_capture(self):
        import diagnostic as d
        import prerequisite as p
        with mock.patch.dict(d.os.environ, {}, clear=True), \
                mock.patch.object(d.subprocess, 'check_output', return_value='a' * 40), \
                mock.patch.object(p, 'capture') as capture, \
                mock.patch.object(d.sys, 'stdout', io.StringIO()):
            self.assertEqual(d.main(), 2)
            capture.assert_not_called()

    def test_bundle_is_all_or_nothing_and_does_not_follow_output_link(self):
        import diagnostic as d
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'report.json').write_bytes(b'{}\n')
            stream = io.StringIO()
            d.emit_bundle(root, ['report.json'], stream)
            self.assertIn('B04_RECORD ', stream.getvalue())
            stream = io.StringIO()
            with mock.patch.object(d, 'MAX_LOG', 1), self.assertRaises(RuntimeError):
                d.emit_bundle(root, ['report.json'], stream)
            self.assertEqual(stream.getvalue(), '')
            if sys.platform != 'win32':
                (root / 'link').symlink_to(root / 'report.json')
                with self.assertRaises(RuntimeError):
                    d.emit_bundle(root, ['link'], io.StringIO())

    def test_runner_rejects_duplicate_stage_before_process_creation(self):
        import diagnostic as d
        with tempfile.TemporaryDirectory() as tmp:
            runner = d.BoundedRun(Path(tmp))
            runner.seen.add('startup')
            with mock.patch.object(d.subprocess, 'Popen') as launch:
                with self.assertRaises(RuntimeError):
                    runner(['/usr/bin/true'], Path(tmp), 'startup')
                launch.assert_not_called()

    def test_runner_captures_raw_bytes_with_no_native_execution(self):
        import diagnostic as d
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            proc = mock.Mock()
            proc.stdout = io.BytesIO(b'fixed output')
            proc.stderr = io.BytesIO(b'fixed error')
            proc.poll.return_value = 0
            proc.wait.return_value = 0
            proc.returncode = 0
            with mock.patch.object(d.subprocess, 'Popen', return_value=proc), \
                    mock.patch.object(d.os, 'killpg', create=True, side_effect=ProcessLookupError):
                result = d.BoundedRun(root)(['unit-placeholder'], root, 'build-0')
            self.assertEqual(result.stdout, b'fixed output')
            self.assertEqual((root / 'build-0.stderr').read_bytes(), b'fixed error')

    def test_inventory_rejects_excess_files_bytes_and_links(self):
        import diagnostic as d
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'small').write_bytes(b'bounded')
            self.assertEqual(d.inventory(root), (1, 7))
            with mock.patch.object(d, 'MAX_FILES', 0), self.assertRaises(RuntimeError):
                d.inventory(root)
            with mock.patch.object(d, 'MAX_SCRATCH', 6), self.assertRaises(RuntimeError):
                d.inventory(root)
            # Link fixtures are unit data, never sandbox controls or archive input.
            if sys.platform != 'win32':
                (root / 'escape').symlink_to(root.parent)
                with self.assertRaises(RuntimeError):
                    d.inventory(root)

    def test_pipe_reader_stops_at_cap_without_unbounded_read(self):
        import diagnostic as d
        import threading
        output = bytearray()
        stop = threading.Event()
        d.read_pipe(io.BytesIO(b'x' * 100), output, stop, 16)
        self.assertEqual(len(output), 16)
        self.assertTrue(stop.is_set())

    def test_preflight_rejects_wrong_identity_or_rerun(self):
        import diagnostic as d
        env = dict(GITHUB_ACTIONS='true', GITHUB_EVENT_NAME='workflow_dispatch',
                   GITHUB_RUN_ATTEMPT='1', GITHUB_REPOSITORY='r404r/7zip',
                   GITHUB_REF='refs/heads/wt/t_2a64c953', GITHUB_SHA='a' * 40,
                   B04_APPROVED_SHA='a' * 40, B04_IMAGE='ubuntu-24.04',
                   ImageOS='ubuntu24', ImageVersion='test-image')
        d.check_identity(env, 'Linux', 'x86_64', 'a' * 40, '24.04')
        for key in ('GITHUB_RUN_ATTEMPT', 'GITHUB_SHA', 'B04_APPROVED_SHA',
                    'B04_IMAGE', 'ImageOS', 'GITHUB_REF', 'GITHUB_EVENT_NAME'):
            with self.subTest(key=key), self.assertRaises(RuntimeError):
                d.check_identity({**env, key: 'invalid'}, 'Linux', 'x86_64', 'a' * 40, '24.04')
        with self.assertRaises(RuntimeError):
            d.check_identity(env, 'Linux', 'arm64', 'a' * 40, '24.04')

    def test_log_transport_is_bounded_lossless_and_not_workflow_commands(self):
        import diagnostic as d
        raw = b'::error::not a workflow command\r\n\x00\xff'
        stream = io.StringIO()
        d.emit_record('sample.stderr', raw, stream)
        line = stream.getvalue()
        self.assertTrue(line.startswith('B04_RECORD '))
        record = json.loads(line.removeprefix('B04_RECORD '))
        self.assertEqual(base64.b64decode(record['base64'], validate=True), raw)
        self.assertEqual(record['sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual(record['bytes'], len(raw))
        with self.assertRaises(RuntimeError):
            d.emit_record('large', b'x' * d.MAX_RECORD, io.StringIO())


if __name__ == '__main__':
    unittest.main()
