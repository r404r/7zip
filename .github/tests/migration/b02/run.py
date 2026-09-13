#!/usr/bin/env python3
"""Capture native identity without replacing native paths with display strings."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile

from fixtures import corpus


def sha(data):
    return hashlib.sha256(data).hexdigest()


def identity(name):
    if os.name == 'nt':
        data = name.encode('utf-16-le', 'surrogatepass')
        return {'tag': 'windows-u16', 'hex_le': data.hex()}
    return {'tag': 'unix-bytes', 'hex': os.fsencode(name).hex()}


def tree(root):
    result = []
    for directory, dirs, files in os.walk(root):
        for name in dirs + files:
            path = Path(directory) / name
            relative = os.path.relpath(path, root)
            result.append({'path': identity(relative), 'directory': path.is_dir(),
                           'content_sha256': sha(path.read_bytes()) if path.is_file() else None})
    return sorted(result, key=lambda item: json.dumps(item['path'], sort_keys=True))


def invoke(exe, args, cwd, env=None):
    r = subprocess.run([str(exe)] + args, cwd=cwd, env=env, capture_output=True, timeout=30)
    return {'argv': args, 'exit': r.returncode, 'stdout_hex': r.stdout.hex(), 'stderr_hex': r.stderr.hex()}


def filesystem(directory):
    """Exclusive creation records collisions; never overwrites a preexisting file."""
    directory.mkdir()
    observations = []
    names = ['Case.txt', 'case.txt', 'é.txt', 'e\u0301.txt', 'nonbmp-😀.txt', 'invalid-\ud800.txt', 'CON.txt', 'end. ', 'x' * 260]
    if os.name != 'nt':
        names += [os.fsdecode(b'bytes-\xff.txt'), os.fsdecode(b'bytes-\xfe.txt')]
    for name in names:
        try:
            with (directory / name).open('xb') as out:
                out.write(b'filesystem-probe\n')
            status = {'created': True}
        except (OSError, UnicodeError) as error:
            status = {'created': False, 'error_type': type(error).__name__, 'errno': getattr(error, 'errno', None), 'winerror': getattr(error, 'winerror', None)}
        # Unix lone surrogates that are not surrogateescape bytes are unrepresentable.
        try:
            native = identity(name)
        except UnicodeError:
            native = {'tag': 'unrepresentable-python-string', 'utf16_hex_le': name.encode('utf-16-le', 'surrogatepass').hex()}
        observations.append({'requested': native, **status})
    return {'operations': observations, 'tree': tree(directory)}


def capture(work):
    build = json.loads((work / 'build.json').read_text())
    exes = {name: Path(value['path']) for name, value in build['executables'].items()}
    for name, exe in exes.items():
        assert sha(exe.read_bytes()) == build['executables'][name]['sha256']
    result = {'schema': 1, 'platform': platform.system(), 'machine': platform.machine(),
              'codepage_authority': 'CANONICAL' if os.name == 'nt' else 'REPORT ONLY',
              'cases': {}, 'filesystem': None}
    with tempfile.TemporaryDirectory(prefix='b02-', dir=work) as temp:
        root = Path(temp)
        result['filesystem'] = filesystem(root / 'filesystem')
        for file in (root / 'filesystem').iterdir():
            os.utime(file, (946684800, 946684800))
        native: dict = {}
        native['create'] = invoke(exes['plain'], ['a', '-tzip', '-mtc=off', '-mta=off', '-bd', '-sccUTF-8', '../native.zip', '.'], root / 'filesystem')
        native['list'] = invoke(exes['plain'], ['l', '-slt', '-bd', '-sccUTF-8', 'native.zip'], root)
        native['extract'] = invoke(exes['plain'], ['x', '-aos', '-y', '-bd', '-sccUTF-8', '-onative-out', 'native.zip'], root)
        native['tree'] = tree(root / 'native-out')
        result['native_roundtrip'] = native
        for label, (fmt, data, extract) in corpus().items():
            cwd = root / label
            cwd.mkdir()
            (cwd / 'input.arc').write_bytes(data)
            fixture_dir = work / 'fixtures'
            fixture_dir.mkdir(exist_ok=True)
            fixture = fixture_dir / (label + '.' + fmt)
            if fixture.exists():
                assert fixture.read_bytes() == data
            else:
                fixture.write_bytes(data)
            entry = {'format': fmt, 'fixture_sha256': sha(data), 'cli': {}, 'handler': None}
            properties = {'default': [], 'unscoped932': ['-mcp=932'], 'unscoped936': ['-mcp=936'],
                          'unscoped65001': ['-mcp=65001'], 'scoped932': [f'-m{fmt}.cp=932'],
                          'scoped936': [f'-m{fmt}.cp=936'], 'scoped65001': [f'-m{fmt}.cp=65001'],
                          'other_scope': ['-mtar.cp=936' if fmt == 'zip' else '-mzip.cp=936'],
                          'ordered_override': ['-mcp=932', f'-m{fmt}.cp=936'],
                          'reverse_override': [f'-m{fmt}.cp=936', '-mcp=932'],
                          'invalid_cp_type': [f'-m{fmt}.cp=not-a-number']}
            for mode, props in properties.items():
                args = ['l', '-slt', '-sccUTF-8', '-bd'] + props + ['input.arc']
                listing = invoke(exes['plain'], args, cwd)
                probe_listing = invoke(exes['probe'], args, cwd)
                assert listing == probe_listing, f'instrumentation changed CLI listing: {label}/{mode}'
                observation: dict = {'listing': listing}
                if extract:
                    out = cwd / 'out'
                    out.mkdir()
                    # Explicit skip-existing policy bounds collision observation.
                    extraction = invoke(exes['plain'], ['x', '-aos', '-y', '-bd', '-sccUTF-8', '-oout'] + props + ['input.arc'], cwd)
                    observation['extraction'] = extraction
                    observation['tree'] = tree(out)
                    shutil.rmtree(out)
                else:
                    observation['extraction_excluded'] = 'UNC syntax is listing-only: no network share authorization'
                entry['cli'][mode] = observation
            env = os.environ.copy()
            env['B02_FORMAT'] = fmt
            probe = invoke(exes['probe'], [], cwd, env)
            assert probe['exit'] == 0, (label, probe)
            entry['handler_raw'] = probe
            entry['handler'] = json.loads(bytes.fromhex(probe['stdout_hex']))
            result['cases'][label] = entry
    return {'provenance': build, 'observations': result}


def compare(actual, expected):
    if actual['observations'] != expected['observations']:
        raise ValueError('Native observations differ; do not edit the baseline to pass')


def negative_controls(report):
    mutations = []
    changed = copy.deepcopy(report)
    changed['observations']['cases']['cp932-zip']['fixture_sha256'] = 'damaged'
    mutations.append(changed)
    changed = copy.deepcopy(report)
    changed['observations']['cases']['cp932-zip']['handler']['phases'][0]['items'][0]['wchar_units'].append(0)
    mutations.append(changed)
    changed = copy.deepcopy(report)
    changed['observations']['filesystem']['tree'].append({'path': 'damaged'})
    mutations.append(changed)
    changed = copy.deepcopy(report)
    changed['observations']['cases']['cp932-zip']['cli']['default']['listing']['exit'] += 1
    mutations.append(changed)
    for changed in mutations:
        try:
            compare(changed, report)
        except ValueError:
            continue
        raise AssertionError('negative control was accepted')
    return len(mutations)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('work', type=Path)
    parser.add_argument('--report', required=True, type=Path)
    parser.add_argument('--expect', type=Path)
    args = parser.parse_args()
    assert not args.report.exists(), 'Refuse to overwrite immutable observations'
    report = capture(args.work.resolve())
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    if args.expect:
        compare(report, json.loads(args.expect.read_text()))
    controls = negative_controls(report)
    print(f"Captured {len(report['observations']['cases'])} fixtures on {platform.system()}; {controls} negative controls rejected; {report['observations']['codepage_authority']}")


if __name__ == '__main__':
    main()
