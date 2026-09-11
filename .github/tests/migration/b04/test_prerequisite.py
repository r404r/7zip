"""Tests for the prerequisite-only fail-closed decision; no archives."""
import importlib.util
from pathlib import Path
import unittest
import subprocess
import sys
import tempfile
import json


class GateTest(unittest.TestCase):
    def test_diagnostic_native_run_remains_unqualified(self):
        import prerequisite as p
        evidence = Path(__file__).with_name('evidence') / '34572155278'
        reports = list(evidence.glob('*/report.json'))
        self.assertEqual(len(reports), 3)
        for path in reports:
            report = json.loads(path.read_bytes())
            self.assertFalse(p.controls_pass(report))
            self.assertFalse(report['hostile_execution_authorized'])
            self.assertFalse(report['b04_complete'])
            self.assertEqual(report['sandbox'], {})
            self.assertTrue(report['sentinels_unchanged'])
            self.assertEqual(report['source_commit'], '2b18c183d3a49dcef65ad1c4f4f1d507c68e7e9f')
            if report['system'] == 'Windows':
                self.assertTrue(report['launcher_rejection_pass'])
                self.assertIn(b'stage=launch api=CreateProcessW error=2',
                              (path.parent / 'sandbox.stdout').read_bytes())
                self.assertIn(b'stage=setup api=GetNamedSecurityInfoW error=2',
                              (path.parent / 'launcher-rejection.stdout').read_bytes())
            else:
                self.assertNotEqual(report['startup_returncode'], 0)
                sandbox = json.loads((path.parent / 'sandbox.command.json').read_bytes())
                startup = json.loads((path.parent / 'startup.command.json').read_bytes())
                self.assertEqual(startup, sandbox[:-3] + ['/usr/bin/true'])

    def test_captured_native_failures_are_rejected_not_skipped(self):
        import prerequisite as p
        evidence = Path(__file__).with_name('evidence')
        reports = list((evidence / '34569823142').glob('*/report.json'))
        self.assertEqual(len(reports), 3)
        for path in reports:
            report = json.loads(path.read_bytes())
            self.assertFalse(p.controls_pass(report), path)
            self.assertFalse(report['hostile_execution_authorized'])
            self.assertFalse(report['b04_complete'])
            self.assertTrue(report['sentinels_unchanged'])
            self.assertNotEqual(report['sandbox_returncode'], 0)
            self.assertEqual(report['baseline_returncode'], 0)
            suffix = '.probe.log' if report['system'] == 'Windows' else '.stdout'
            for phase in ('baseline', 'sandbox'):
                self.assertEqual(p.parse((path.parent / (phase + suffix)).read_bytes()),
                                 report[phase])
        local = json.loads((evidence / 'local-linux' / 'report.json').read_bytes())
        self.assertTrue(p.controls_pass(local))
        self.assertFalse(local['hostile_execution_authorized'])

    def test_native_candidate_emits_fail_closed_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / 'evidence'
            result = subprocess.run([sys.executable, str(Path(__file__).with_name('prerequisite.py')),
                                     str(destination)], capture_output=True, timeout=90)
            self.assertIn(result.returncode, (0, 2), result.stderr)
            self.assertTrue((destination / 'report.json').exists(), 'no native evidence report')
            report = json.loads((destination / 'report.json').read_text())
            self.assertIs(report['hostile_execution_authorized'], False)
            self.assertIs(report['b04_complete'], False)
            self.assertEqual(report['stage'], 'file-write-prerequisite-candidate')
            self.assertEqual(report['controls_pass'], result.returncode == 0)
            if report['system'] in ('Linux', 'Darwin'):
                self.assertIn('startup_returncode', report)
                self.assertTrue((destination / 'startup.command.json').exists())
                command = json.loads((destination / 'startup.command.json').read_text())
                self.assertEqual(command[-1], '/usr/bin/true')
            elif report['system'] == 'Windows':
                self.assertTrue(report['launcher_rejection_pass'])
                self.assertIn('B04-launch stage=', (destination / 'sandbox.stdout').read_text())

    def test_only_complete_real_control_relations_pass(self):
        import prerequisite as p
        inside = {name: True for name in p.INSIDE}
        outside = {name: False for name in p.OUTSIDE}
        report = dict(baseline={**inside, **{name: True for name in p.OUTSIDE}},
                      sandbox={**inside, **outside}, sentinels_unchanged=True,
                      baseline_returncode=0, sandbox_returncode=0)
        self.assertTrue(p.controls_pass(report))
        for name in p.OUTSIDE:
            damaged = {**report, 'sandbox': {**report['sandbox'], name: True}}
            self.assertFalse(p.controls_pass(damaged), name)
        for field in report:
            damaged = dict(report)
            del damaged[field]
            self.assertFalse(p.controls_pass(damaged), field)

    def test_missing_evidence_is_not_a_pass(self):
        path = Path(__file__).with_name('prerequisite.py')
        self.assertTrue(path.exists(), 'prerequisite runner is missing')
        spec = importlib.util.spec_from_file_location('prerequisite', path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertFalse(module.controls_pass({}))


if __name__ == '__main__':
    unittest.main()
