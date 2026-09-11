"""B04 prerequisite controls, not an archive execution authorization."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from typing import Any

INSIDE = ('create', 'rename', 'hardlink', 'symlink', 'readonly_denied')
OUTSIDE = ('absolute', 'traversal', 'symlink_escape', 'hardlink_alias')

def controls_pass(report):
    """A bounded file-write control result, never permission to run archives."""
    expected_baseline = {name: True for name in INSIDE + OUTSIDE}
    expected_sandbox = {**{name: True for name in INSIDE},
                        **{name: False for name in OUTSIDE}}
    return (report.get('baseline') == expected_baseline
            and report.get('sandbox') == expected_sandbox
            and report.get('sentinels_unchanged') is True
            and report.get('baseline_returncode') == 0
            and report.get('sandbox_returncode') == 0)


def run(command, directory, label, env=None):
    """Only fixed build/probe commands; preserve raw bytes even on failure."""
    command = list(map(str, command))
    (directory / (label + '.command.json')).write_text(json.dumps(command, indent=2))
    try:
        result = subprocess.run(command, cwd=directory, env=env, stdin=subprocess.DEVNULL,
                                capture_output=True, timeout=60, close_fds=True)
    except subprocess.TimeoutExpired as exc:
        (directory / (label + '.stdout')).write_bytes(exc.stdout or b'')
        (directory / (label + '.stderr')).write_bytes(exc.stderr or b'')
        raise RuntimeError(label + ' timed out; no qualification') from exc
    (directory / (label + '.stdout')).write_bytes(result.stdout)
    (directory / (label + '.stderr')).write_bytes(result.stderr)
    return result


def parse(raw):
    result = {}
    for line in raw.decode('ascii').splitlines():
        fields = line.split()
        if len(fields) < 3 or fields[0] in result or fields[1] not in ('0', '1'):
            raise ValueError('invalid or duplicate probe record')
        result[fields[0]] = fields[1] == '1'
    return result


def sandbox_command(system, envelope, executable, source):
    work, outside = envelope / 'work', envelope / 'outside'
    if system == 'Linux':
        # NEVER bind a host directory writable. Fresh tmpfs cannot arrive with
        # an external hardlink alias. /outside is a separate read-only mount.
        command = ['bwrap', '--unshare-all', '--die-with-parent', '--new-session',
                   '--cap-drop', 'ALL', '--clearenv', '--ro-bind', '/usr', '/usr']
        for name in ('bin', 'lib', 'lib64'):
            path = Path('/') / name
            if path.is_symlink():
                command += ['--symlink', os.readlink(path), str(path)]
            elif path.exists():
                command += ['--ro-bind', str(path), str(path)]
        command += ['--ro-bind', str(executable), '/probe',
                    '--tmpfs', '/probe-root', '--dir', '/probe-root/work',
                    '--ro-bind', str(outside), '/probe-root/outside',
                    '--chdir', '/probe-root/work', '--', '/probe',
                    '/probe-root/work', '/probe-root/outside']
        return command
    if system == 'Darwin':
        # Paths are generated ASCII paths; JSON quoting is also valid for these
        # sandbox profile strings. No network/mach-lookup blanket allow rule.
        profile = '(version 1)\n(deny default)\n(allow process-exec)\n'
        profile += '(allow sysctl-read)\n'
        for path in ('/usr', '/System', '/Library', str(envelope)):
            profile += '(allow file-read* (subpath ' + json.dumps(path) + '))\n'
        profile += '(allow file-write* (subpath ' + json.dumps(str(work)) + '))\n'
        (envelope / 'candidate.sb').write_text(profile)
        return ['/usr/bin/sandbox-exec', '-f', str(envelope / 'candidate.sb'),
                str(executable), str(work), str(outside)]
    if system == 'Windows':
        return [str(source / 'winlaunch.exe'), str(envelope)]
    raise RuntimeError('unsupported native platform: ' + system)


def capture(destination):
    destination = destination.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    source = Path(__file__).resolve().parent
    system = platform.system()
    report: dict[str, Any] = dict(schema=1, stage='file-write-prerequisite-candidate',
                  system=system, platform=platform.platform(),
                  hostile_execution_authorized=False, b04_complete=False,
                  controls_pass=False)
    try:
        if not str(destination).isascii():
            raise RuntimeError('candidate requires an ASCII disposable path; Unicode not qualified')
        report['source_commit'] = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip()
        report['source_sha256'] = {name: hashlib.sha256((source / name).read_bytes()).hexdigest()
                                   for name in ('prerequisite.py', 'probe.c', 'winlaunch.c')}
        if system == 'Windows':
            commands = [
                ['cl', '/nologo', '/W4', '/WX', '/std:c11', '/MT', str(source / 'probe.c'),
                 '/Fe:probe.exe'],
                ['cl', '/nologo', '/W4', '/WX', '/std:c11', '/MT', str(source / 'winlaunch.c'),
                 '/Fe:winlaunch.exe', '/link', 'userenv.lib', 'advapi32.lib']]
            executable = destination / 'probe.exe'
        else:
            commands = [['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                         str(source / 'probe.c'), '-o', 'probe']]
            executable = destination / 'probe'
        for index, command in enumerate(commands):
            build = run(command, destination, 'build-' + str(index))
            if build.returncode:
                raise RuntimeError('native probe build failed: ' + str(build.returncode))
        report['executable_sha256'] = hashlib.sha256(executable.read_bytes()).hexdigest()
        # Baseline and sandbox share no mutable files. Every external target is
        # a new control file, never a real host/user file. Baseline is intentional
        # unconfined control execution, not an archive or an isolation fallback.
        for label in ('baseline', 'sandbox'):
            envelope = destination / label
            work, outside = envelope / 'work', envelope / 'outside'
            work.mkdir(parents=True)
            outside.mkdir()
            for name in OUTSIDE:
                (outside / name).write_bytes(b'B04 control sentinel\n')
            copied = envelope / executable.name
            shutil.copy2(executable, copied)
            if label == 'baseline':
                command = [str(copied), str(work), str(outside)]
            else:
                command = sandbox_command(system, envelope, copied, destination)
            # Build inherits only the build environment; probes inherit none of
            # the CI credentials/settings. Windows needs SystemRoot for loader.
            env = {'PATH': os.defpath}
            if system == 'Windows':
                env['SystemRoot'] = os.environ['SystemRoot']
            result = run(command, destination, label, env)
            report[label + '_returncode'] = result.returncode
            raw = result.stdout
            if system == 'Windows':
                raw = (work / 'probe.log').read_bytes() if (work / 'probe.log').exists() else b''
                (destination / (label + '.probe.log')).write_bytes(raw)
            report[label] = parse(raw)
            report[label + '_sentinel_sha256'] = {
                name: hashlib.sha256((outside / name).read_bytes()).hexdigest() for name in OUTSIDE}
            if label == 'sandbox':
                report['sentinels_unchanged'] = all(
                    (outside / name).read_bytes() == b'B04 control sentinel\n' for name in OUTSIDE)
        report['controls_pass'] = controls_pass(report)
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as exc:
        report['failure'] = str(exc)
    (destination / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 0 if report['controls_pass'] else 2


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path, help='new evidence directory (must not exist)')
    args = parser.parse_args()
    sys.exit(capture(args.destination))
