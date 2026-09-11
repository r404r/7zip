"""Offline main -> capture -> BoundedRun fault injection; not native evidence."""
import base64
from contextlib import ExitStack
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import diagnostic as d
import prerequisite as p


class StopContractTest(unittest.TestCase):
    def exercise(self, fault, windows_supervision=False):
        # No real subprocess or reader thread is created. Synchronous mock readers
        # provide finite synthetic bytes; these are never frozen as oracle data.
        with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
            root = Path(tmp) / 'b04-approved-diagnostic'
            failed = False
            operations = []
            launches = []
            stream = io.StringIO()

            def guard(name, original):
                def call(*args, **kwargs):
                    if failed:
                        operations.append(name)
                    return original(*args, **kwargs)
                return call

            # Observe filesystem entrypoints as well as semantic collection APIs.
            # Keep guards active only during main; test-fixture cleanup is separate.
            for name in ('open', 'iterdir', 'stat', 'lstat', 'mkdir', 'unlink',
                         'rmdir', 'chmod', 'read_bytes', 'write_bytes', 'write_text'):
                stack.enter_context(mock.patch.object(Path, name, guard(name, getattr(Path, name))))
            for name in ('inventory', 'emit_bundle', 'cleanup'):
                stack.enter_context(mock.patch.object(d, name, guard(name, getattr(d, name))))

            def process(command, **kwargs):
                nonlocal failed
                if failed:
                    operations.append('launch')
                launches.append(command)
                raw, code = b'', 0
                if command[0] == 'cc':
                    (kwargs['cwd'] / 'probe').write_bytes(b'unit placeholder; never executed')
                elif command[-1] == '/usr/bin/true':
                    code = 1 if fault == 'rejection' else 0
                else:
                    sandbox = len(launches) == 4
                    raw = b''.join((name + (' 0' if sandbox and name in p.OUTSIDE else ' 1')
                                    + ' errno=0\n').encode() for name in p.INSIDE + p.OUTSIDE)
                # Inject on the first process: any later filesystem action or
                # launch is forbidden once the supervisor can observe the fault.
                if len(launches) == 1 and fault == 'native':
                    raw = b'B04-launch quiescent=false\n'
                proc = mock.Mock(stdout=io.BytesIO(raw), stderr=io.BytesIO(b''),
                                 returncode=code, pid=12345)

                def poll():
                    nonlocal failed
                    if fault in ('kill', 'wait'):
                        failed = True
                        raise RuntimeError('injected supervision failure')
                    if fault == 'timeout':
                        return None
                    return code

                proc.poll.side_effect = poll
                if fault == 'wait':
                    proc.wait.side_effect = subprocess.TimeoutExpired('unit', 5)
                return proc

            def thread(*, target, args, daemon):
                nonlocal failed
                result = mock.Mock()
                result.start.side_effect = lambda: target(*args)
                def alive():
                    nonlocal failed
                    if fault in ('reader', 'native'):
                        failed = True
                    return fault == 'reader'
                result.is_alive.side_effect = alive
                return result

            def killpg(pid, sig):
                nonlocal failed
                if sig == 0 and fault == 'leftover':
                    failed = True
                    return
                if sig == 9:
                    if fault == 'kill':
                        raise PermissionError('injected kill failure')
                    return
                raise ProcessLookupError

            env = dict(RUNNER_TEMP=tmp)
            stack.enter_context(mock.patch.dict(d.os.environ, env, clear=True))
            # Simulate both supervisor branches on any host, without changing
            # pathlib's global os.name or ever invoking real taskkill/killpg.
            os_proxy = mock.Mock(wraps=d.os)
            os_proxy.name = 'nt' if windows_supervision else 'posix'
            os_proxy.environ = d.os.environ
            stack.enter_context(mock.patch.object(d, 'os', os_proxy))
            stack.enter_context(mock.patch.object(d.signal, 'SIGKILL', 9, create=True))
            taskkill = stack.enter_context(mock.patch.object(d.subprocess, 'run'))
            if fault == 'kill':
                taskkill.side_effect = subprocess.CalledProcessError(1, 'taskkill')
            if fault == 'timeout':
                ticks = iter((0, 61))
                def clock():
                    nonlocal failed
                    value = next(ticks)
                    if value == 61:
                        failed = True
                    return value
                stack.enter_context(mock.patch.object(d.time, 'monotonic', side_effect=clock))
            stack.enter_context(mock.patch.object(d, 'check_identity'))
            stack.enter_context(mock.patch.object(d.platform, 'system', return_value='Linux'))
            stack.enter_context(mock.patch.object(d.platform, 'platform', return_value='offline-unit'))
            stack.enter_context(mock.patch.object(d.platform, 'freedesktop_os_release', create=True,
                                                  return_value={'VERSION_ID': '24.04'}))
            stack.enter_context(mock.patch.object(d.subprocess, 'check_output',
                                                  side_effect=['a' * 40, b'', 'a' * 40]))
            launch = stack.enter_context(mock.patch.object(d.subprocess, 'Popen', side_effect=process))
            stack.enter_context(mock.patch.object(d.threading, 'Thread', side_effect=thread))
            stack.enter_context(mock.patch.object(os_proxy, 'killpg', create=True, side_effect=killpg))
            stack.enter_context(mock.patch.object(d, 'observe'))
            stack.enter_context(mock.patch.object(d.sys, 'stdout', stream))
            result = d.main()
            self.assertEqual(operations, [], 'filesystem/collection/launch after fatal state')
            records = [json.loads(line.removeprefix('B04_RECORD '))
                       for line in stream.getvalue().splitlines() if line.startswith('B04_RECORD ')]
            names = [r['name'] for r in records]
            if fault in ('success', 'rejection'):
                self.assertEqual(result, 0 if fault == 'success' else 2)
                self.assertEqual(launch.call_count, 4 if fault == 'success' else 3)
                self.assertIn('report.json', names)
                report = json.loads(base64.b64decode(next(r['base64'] for r in records
                                                         if r['name'] == 'report.json')))
                self.assertEqual(report['controls_pass'], fault == 'success')
                self.assertTrue((root / 'attempt-consumed').is_file())
            else:
                self.assertEqual(result, 2)
                self.assertEqual(launch.call_count, 1)
                self.assertNotIn('report.json', names)
                self.assertIn('controller-failure', names)
                self.assertIn('unqualified-prefix/build-0.stdout', names)

    def test_fatal_state_crosses_all_layers_without_filesystem_work(self):
        for fault in ('native', 'reader', 'kill', 'wait', 'timeout', 'leftover'):
            with self.subTest(fault=fault):
                self.exercise(fault)

    def test_quiescent_success_and_startup_rejection_keep_bundle_and_cleanup(self):
        for outcome in ('success', 'rejection'):
            with self.subTest(outcome=outcome):
                self.exercise(outcome)

    def test_windows_termination_failures_also_stop_all_layers(self):
        for fault in ('kill', 'wait', 'timeout', 'reader', 'native'):
            with self.subTest(fault=fault):
                self.exercise(fault, windows_supervision=True)


if __name__ == '__main__':
    unittest.main()
