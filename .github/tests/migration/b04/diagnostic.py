"""Single approved startup diagnostic; never an archive/qualification entrypoint."""
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import re
import stat
import signal
import shutil
import subprocess
import sys
import threading
import time
from prerequisite import SupervisionFailure

MAX_RECORD = 64 * 1024
MAX_LOG = 1024 * 1024
MAX_FILES = 64
MAX_SCRATCH = 64 * 1024 * 1024


def inventory(root):
    """Bound trusted fixed-tool outputs; never traverse a probe-created link."""
    count, size = 0, 0
    pending = [root]
    while pending:
        directory = pending.pop()
        for path in directory.iterdir():
            try:
                info = path.lstat()
            except FileNotFoundError:
                continue  # Trusted compiler may remove its own temporary file.
            count += 1  # Directories and link entries count too (conservative).
            relative = path.relative_to(root).as_posix()
            reparse = getattr(info, 'st_file_attributes', 0) & 0x400
            if stat.S_ISLNK(info.st_mode) or reparse:
                expected = {f'{phase}/work/{name}' for phase in ('baseline', 'sandbox')
                            for name in ('inside-sym', 'outside-sym')}
                if relative not in expected or not stat.S_ISLNK(info.st_mode):
                    raise RuntimeError('unexpected link/reparse entry; no traversal')
                size += info.st_size
            elif stat.S_ISDIR(info.st_mode):
                pending.append(path)
            elif stat.S_ISREG(info.st_mode):
                size += info.st_size
            else:
                raise RuntimeError('unexpected special file')
            if count > MAX_FILES or size > MAX_SCRATCH:
                raise RuntimeError('scratch budget exceeded')
    return count, size


def read_pipe(pipe, output, stop, cap):
    """A cap breach is failure, not a successful truncated record."""
    try:
        while len(output) < cap:
            chunk = pipe.read(min(4096, cap - len(output)))
            if not chunk:
                return
            output.extend(chunk)
        if pipe.read(1):
            stop.set()
    except OSError:
        stop.set()


class BoundedRun:
    """Fixed trusted compiler/tools and fixed no-descendant probe only.

    This is NOT a general untrusted process supervisor or a disk quota. The
    compile products are checked before copying; fixed probe writes are finite.
    Do not attach archive execution, arbitrary helpers or descendant controls.
    """
    def __init__(self, root):
        self.root = root
        self.seen = set()
        self.failed = False
        self.last_pipe_bytes = {}

    def __call__(self, command, directory, label, env=None):
        try:
            return self._run(command, directory, label, env)
        except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as exc:
            # Irreversible even if termination succeeds; not an exited rejection.
            self.failed = True
            raise SupervisionFailure(str(exc)) from exc

    def _run(self, command, directory, label, env=None):
        if self.failed or label in self.seen:
            raise RuntimeError('stopped or duplicate diagnostic stage')
        self.seen.add(label)
        command = list(map(str, command))
        inventory(self.root)
        if label.startswith('build-'):
            env = {**os.environ, 'TMPDIR': str(self.root),
                   'TEMP': str(self.root), 'TMP': str(self.root)}
        (directory / (label + '.command.json')).write_text(json.dumps(command))
        stop = threading.Event()
        output, error = bytearray(), bytearray()
        proc = subprocess.Popen(command, cwd=directory, env=env,
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            close_fds=True, start_new_session=os.name != 'nt')
        assert proc.stdout is not None and proc.stderr is not None
        readers = [threading.Thread(target=read_pipe, args=(pipe, data, stop, 16384), daemon=True)
                   for pipe, data in ((proc.stdout, output), (proc.stderr, error))]
        deadline = time.monotonic() + 60
        reason = None
        started = []
        try:
            for thread in readers:
                thread.start()
                started.append(thread)
            while proc.poll() is None:
                inventory(self.root)
                if stop.is_set() or time.monotonic() >= deadline:
                    raise RuntimeError('subprocess output cap or 60-second deadline')
                time.sleep(0.02)
        except (OSError, RuntimeError) as exc:
            reason = str(exc)
            self.failed = True
            if os.name != 'nt':
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            else:
                # Only our known compiler/launcher PID. Never a user-selected PID.
                # The native launcher also owns its probe in a kill-on-close Job.
                subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'],
                    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL, timeout=5, check=True)
            proc.wait(timeout=5)
        finally:
            try:
                for thread in started:
                    thread.join(timeout=1)
                if any(thread.is_alive() for thread in started):
                    reason = 'pipe remains open; quiescence not established'
                else:
                    proc.stdout.close()
                    proc.stderr.close()
                if stop.is_set():
                    reason = 'output cap/read failure; raw prefix is NOT complete evidence'
            finally:
                # Memory only, including kill/wait/join failure. A live reader
                # makes this an unqualified prefix, never complete evidence.
                self.last_pipe_bytes = {label + '.stdout': bytes(output),
                                        label + '.stderr': bytes(error)}
        if reason:
            raise RuntimeError(reason)
        if b'quiescent=false' in output or b'stage=timeout' in output or b'stage=cleanup' in output:
            raise RuntimeError('native launcher timeout/cleanup failure; stop guest work')
        if os.name != 'nt':
            try:
                os.killpg(proc.pid, 0)
            except ProcessLookupError:
                pass
            else:
                self.failed = True
                os.killpg(proc.pid, signal.SIGKILL)
                # SIGKILL is not proof of descendant quiescence. End this guest
                # without inventory, serialization, collection or cleanup.
                raise RuntimeError('leftover process group; no further launch/collection')
        inventory(self.root)
        (directory / (label + '.stdout')).write_bytes(output)
        (directory / (label + '.stderr')).write_bytes(error)
        return subprocess.CompletedProcess(command, proc.returncode, bytes(output), bytes(error))


def check_identity(env, system, machine, commit, os_version):
    """The reviewed ref is necessary, never sufficient proof of authorization."""
    required = dict(GITHUB_ACTIONS='true', GITHUB_EVENT_NAME='workflow_dispatch',
                    GITHUB_RUN_ATTEMPT='1', GITHUB_REPOSITORY='r404r/7zip',
                    GITHUB_REF='refs/heads/wt/t_2a64c953')
    if any(env.get(key) != value for key, value in required.items()):
        raise RuntimeError('not the approved manual first-attempt context')
    if not re.fullmatch('[0-9a-f]{40}', commit) or not (
            commit == env.get('GITHUB_SHA') == env.get('B04_APPROVED_SHA')):
        raise RuntimeError('reviewed commit identity mismatch')
    tuples = {
        'Linux': ('ubuntu-24.04', 'ubuntu24', ('x86_64',), '24.04'),
        'Darwin': ('macos-26', 'macos26', ('arm64',), '26.'),
        'Windows': ('windows-2025-vs2026', 'win25', ('AMD64',), '10.0.26100'),
    }
    if system not in tuples:
        raise RuntimeError('unexpected OS')
    image, image_os, machines, version = tuples[system]
    if (env.get('B04_IMAGE') != image or not env.get('ImageOS', '').startswith(image_os)
            or machine not in machines or not os_version.startswith(version)
            or not env.get('ImageVersion')):
        raise RuntimeError('unexpected native image/architecture/version')


def emit_record(name, raw, stream):
    """Only encoded bytes cross the GitHub workflow command boundary."""
    if len(raw) >= MAX_RECORD:
        raise RuntimeError('record cap exceeded; no truncated evidence accepted')
    line = 'B04_RECORD ' + json.dumps(dict(name=name, bytes=len(raw),
        sha256=hashlib.sha256(raw).hexdigest(),
        base64=base64.b64encode(raw).decode('ascii')), separators=(',', ':')) + '\n'
    stream.write(line)
    return len(line.encode('ascii'))


def emit_bundle(root, names, stream):
    buffer = io.StringIO()
    total = 0
    for name in names:
        path = root / name
        # Caller owns root and fixes names. Collection occurs after fixed workers
        # exit. No recursive collection, child-selected names, or archive parsing.
        for component in (path, *path.parents):
            if component == root:
                break
            info = component.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
                raise RuntimeError('collector refuses link/reparse output')
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_size >= MAX_RECORD:
            raise RuntimeError('collector requires bounded regular file')
        with path.open('rb') as source:
            raw = source.read(MAX_RECORD)
        total += emit_record(name, raw, buffer)
        if total > MAX_LOG - 8192:  # Reserve room for fixed status/failure records.
            raise RuntimeError('encoded log budget exceeded; bundle not emitted')
    stream.write(buffer.getvalue())


def observe(root, executable, report, runner):
    """Read only named identity/policy fields; never full environment/audit dumps."""
    system = platform.system()
    report['diagnostic_source_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report['image'] = {key: os.environ.get(key) for key in
                       ('ImageOS', 'ImageVersion', 'B04_IMAGE', 'GITHUB_RUN_ID', 'GITHUB_RUN_ATTEMPT')}
    report['machine'] = platform.machine()
    report['generated_executable'] = dict(path=str(executable.resolve()),
        mode=stat.S_IMODE(executable.stat().st_mode), bytes=executable.stat().st_size)
    # Two copied executables plus fixed objects/logs must fit with ample headroom.
    if executable.stat().st_size > 4 * 1024 * 1024:
        raise RuntimeError('unexpected fixed probe size; no copies or launch')
    report['policy_reads'] = {}
    if system == 'Linux':
        for name in ('/proc/self/attr/current',
                     '/proc/sys/kernel/apparmor_restrict_unprivileged_userns',
                     '/proc/sys/kernel/unprivileged_userns_clone'):
            try:
                with open(name, 'rb') as source:
                    raw = source.read(4096)
                if len(raw) == 4096:
                    raise RuntimeError('policy field cap')
                report['policy_reads'][name] = raw.decode('ascii').strip()
            except OSError as exc:
                report['policy_reads'][name] = {'unavailable_errno': exc.errno}
        bwrap = shutil.which('bwrap')
        if not bwrap:
            raise RuntimeError('bubblewrap missing; no installation fallback')
        path = Path(bwrap).resolve()
        report['bubblewrap'] = dict(path=str(path), mode=stat.S_IMODE(path.stat().st_mode),
                                   sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        commands = [[bwrap, '--version'],
                    ['/usr/bin/dpkg-query', '-W', '-f=${Version}\n', 'bubblewrap']]
    elif system == 'Darwin':
        commands = [['/usr/bin/file', str(executable)],
                    ['/usr/bin/codesign', '--display', '--verbose=2', str(executable)],
                    ['/usr/bin/otool', '-L', str(executable)]]
    else:
        commands = []  # winlaunch records type/final-path and immediate API errors.
    report['identity_returncodes'] = []
    for index, command in enumerate(commands):
        result = runner(command, root, 'identity-' + str(index), {'PATH': os.defpath})
        report['identity_returncodes'].append(result.returncode)
        if result.returncode:
            raise RuntimeError('identity tool rejected fixed binary; no launch')
    # Audit/crash databases can contain unrelated job/user information. No broad
    # retrieval is allowed by this entry. Missing exact denial remains a blocker.
    report['audit_crash_records'] = 'not collected; no safe process-specific source established'


def cleanup(root):
    """Only after fixed processes have exited; refuse unfamiliar reparse entries."""
    inventory(root)

    def remove_contents(directory):
        for path in directory.iterdir():
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode):
                path.unlink()  # Never chmod or resolve a link target.
            elif stat.S_ISDIR(info.st_mode):
                remove_contents(path)
                path.rmdir()
            else:
                path.chmod(0o600)  # Fixed readonly control, after all writers exit.
                path.unlink()

    remove_contents(root)
    if any(root.iterdir()):
        raise RuntimeError('cleanup incomplete')
    (root / 'attempt-consumed').write_bytes(b'No retry in this job.\n')


def main():
    import prerequisite as p
    runner = None
    try:
        source = Path(__file__).resolve().parent
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source,
                                         timeout=60, text=True).strip()
        system = platform.system()
        version = (platform.freedesktop_os_release().get('VERSION_ID', '') if system == 'Linux'
                   else platform.mac_ver()[0] if system == 'Darwin' else platform.version())
        check_identity(os.environ, system, platform.machine(), commit, version)
        if subprocess.check_output(['git', 'diff', '--name-only', 'HEAD'], cwd=source, timeout=60):
            raise RuntimeError('tracked source is dirty')
        root = Path(os.environ['RUNNER_TEMP']).resolve() / 'b04-approved-diagnostic'
        # capture creates this exclusive directory. A repeated call cannot reuse
        # it. The dispatcher/operator separately enforces ONE workflow dispatch.
        if root.exists():
            raise RuntimeError('attempt directory already exists; no retry')
        runner = BoundedRun(root)
        result = p.capture(root, run_command=runner,
            observe=lambda root, exe, report: observe(root, exe, report, runner), emit=False)
        if runner.failed:
            raise SupervisionFailure('supervisor failed; no further collection/cleanup in this guest')
        inventory(root)
        names = ['report.json']
        for label in sorted(runner.seen):
            for suffix in ('.command.json', '.stdout', '.stderr'):
                if (root / (label + suffix)).exists():
                    names.append(label + suffix)
        for name in ('baseline.probe.log', 'sandbox.probe.log', 'sandbox/candidate.sb'):
            if (root / name).exists():
                names.append(name)
        emit_bundle(root, names, sys.stdout)
        cleanup(root)
        print('B04_STATUS cleanup=owned-files-removed attempt=consumed b04_complete=false')
        return result
    except SupervisionFailure as exc:
        for name, raw in (runner.last_pipe_bytes if runner is not None else {}).items():
            emit_record('unqualified-prefix/' + name, raw, sys.stdout)
        emit_record('controller-failure', str(exc).encode('utf-8')[:4096], sys.stdout)
        return 2
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as exc:
        emit_record('controller-failure', str(exc).encode('utf-8')[:4096], sys.stdout)
        return 2


if __name__ == '__main__':
    sys.exit(main())
