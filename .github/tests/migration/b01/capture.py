#!/usr/bin/env python3
"""B01 immutable CLI characterization. CLI diagnostics are NOT FFI numeric results."""
import argparse
import base64
import bz2
import gzip
import hashlib

import json
import lzma
from pathlib import Path
import platform
import shutil
import subprocess
import tarfile
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify_fixtures(manifest, directory):
    for fixture in manifest['fixtures']:
        for item in fixture['files']:
            if sha((directory / item['path']).read_bytes()) != item['sha256']:
                raise ValueError('immutable fixture digest mismatch: ' + item['path'])


def compare(actual, expected):
    if actual['platform'] != expected['platform']:
        raise ValueError('native platform mismatch')
    for key in ('manifest_sha256', 'observations', 'capabilities'):
        if actual[key] != expected[key]:
            raise ValueError(key + ' mismatch')


def diagnostics(text):
    # Literal CLI labels, not inferred NOperationResult or HRESULT mappings.
    labels = ['CRC Failed', 'Data Error', 'Headers Error', 'Unexpected end of archive',
              'Unsupported Method', 'Can not open the file as archive',
              'Cannot open the file as archive', 'Missing volume', 'Is not archive']
    return dict(domain='legacy-cli-text', labels=[s for s in labels if s in text],
                hresult=None, item_result=None, open_flags=None,
                numeric_unavailable_reason='CLI does not expose lossless structured engine outcomes')


def properties(text):
    blocks = []
    for block in text.replace('\r\n', '\n').split('\n\n'):
        fields = dict(line.split(' = ', 1) for line in block.splitlines() if ' = ' in line)
        keep = {k: v for k, v in fields.items() if k in ('Path', 'Type', 'Method', 'Size', 'CRC', 'Volumes', 'Volume Index', 'Offset', 'Physical Size', 'Total Physical Size', 'Headers Size', 'Tail Size', 'Errors', 'Warnings')}
        if keep:
            blocks.append(keep)
    return blocks  # retain order; names are not entry identity


def capture(exe, manifest):
    report: dict = dict(schema_version=1, platform=dict(os=platform.system(), arch=platform.machine().lower()),
                  provenance=dict(commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO).decode().strip(),
                                  engine_diff=subprocess.check_output(['git', 'diff', 'd9c3b65', '--', 'C', 'CPP'], cwd=REPO).decode(),
                                  platform=platform.platform(), python=platform.python_version(),
                                  executable_sha256=sha(exe.read_bytes()), harness_sha256=sha(Path(__file__).read_bytes())),
                  manifest_sha256=sha((HERE / 'manifest.json').read_bytes()), commands={}, observations={})
    with tempfile.TemporaryDirectory(prefix='b01-') as tmp:
        root = Path(tmp)
        shutil.copytree(HERE / 'fixtures', root / 'fixtures')
        verify_fixtures(manifest, root / 'fixtures')

        def run(key, args, dest=None):
            argv = [str(exe), *map(str, args), '-sccUTF-8', '-bd']
            proc = subprocess.run(argv, cwd=root, input=b'', capture_output=True, timeout=120)
            def clean(text):
                return text.replace(str(root), '<TEMP>').replace(str(exe), '<EXE>').replace('\\', '/')
            out, err = proc.stdout.decode('utf-8', errors='strict'), proc.stderr.decode('utf-8', errors='strict')
            report['commands'][key] = dict(argv=argv, exit=proc.returncode,
                stdout_base64=base64.b64encode(proc.stdout).decode(), stderr_base64=base64.b64encode(proc.stderr).decode())
            obs: dict = dict(exit=proc.returncode, diagnostics=diagnostics(out + err))
            if args[0] == 'l':
                obs['properties'] = properties(clean(out))
            if dest is not None:
                obs['files'] = {p.relative_to(dest).as_posix(): dict(size=p.stat().st_size, sha256=sha(p.read_bytes()))
                                for p in sorted(dest.rglob('*')) if p.is_file()}
            report['observations'][key] = obs
            return out, proc.returncode

        out, code = run('capabilities', ['i'])
        if code:
            raise ValueError('capability enumeration failed')
        # Freeze registration rows verbatim, excluding banner / executable path.
        report['capabilities'] = out.replace('\r\n', '\n').split('Formats:\n', 1)[1].strip()
        for fixture in manifest['fixtures']:
            archive = root / 'fixtures' / fixture['id']
            for operation, verb in [('list', 'l'), ('test', 't'), ('extract', 'x')]:
                dest = root / ('out-' + fixture['id']) if verb == 'x' else None
                args = [verb, archive, '-y']
                if verb == 'l':
                    args.append('-slt')
                if dest is not None:
                    args.append('-o' + str(dest))
                run(fixture['id'] + '/' + operation, args, dest)
        # Controlled missing-volume copy; originals and immutable bytes untouched.
        missing = root / 'missing'
        missing.mkdir()
        shutil.copy(root / 'fixtures' / 'volume.7z.001', missing)
        for verb in ['l', 't', 'x']:
            dest = root / 'missing-out' if verb == 'x' else None
            run('missing-volume/' + verb, [verb, missing / 'volume.7z.001', '-y', *(['-slt'] if verb == 'l' else []),
                                          *(['-o' + str(dest)] if dest else [])], dest)
        # Explicit two-stage nested-chain extraction: do not imply automatic recursion.
        nested = root / 'nested-stage1'
        run('nested/stage1', ['x', root / 'fixtures/nested.tar.gz', '-y', '-o' + str(nested)], nested)
        stage2 = root / 'nested-stage2'
        run('nested/stage2', ['x', nested / 'nested.tar', '-y', '-o' + str(stage2)], stage2)
        payload = bytes(range(256)) * 16
        (root / 'payload.bin').write_bytes(payload)
        # Independent readers prevent coordinated writer/reader drift for these formats.
        for fmt in ['7z', 'zip', 'tar', 'gzip', 'bzip2', 'xz', 'wim']:
            archive = root / ('created.' + fmt)
            _, code = run('create/' + fmt, ['a', '-t' + fmt, archive, 'payload.bin'])
            if code == 0:
                run('created-test/' + fmt, ['t', archive])
                dest = root / ('created-out-' + fmt)
                run('created-extract/' + fmt, ['x', archive, '-y', '-o' + str(dest)], dest)
                if fmt == 'zip':
                    with zipfile.ZipFile(archive) as reader:
                        decoded = reader.read('payload.bin')
                elif fmt == 'tar':
                    with tarfile.open(archive) as reader:
                        member = reader.extractfile('payload.bin')
                        if member is None:
                            raise ValueError('created tar payload missing')
                        decoded = member.read()
                elif fmt in ('gzip', 'bzip2', 'xz'):
                    decoded = {'gzip': gzip.decompress, 'bzip2': bz2.decompress, 'xz': lzma.decompress}[fmt](archive.read_bytes())
                else:
                    decoded = None
                report['observations']['create/' + fmt]['independent_payload_sha256'] = sha(decoded) if decoded is not None else None
                if decoded is not None and decoded != payload:
                    raise ValueError('independent reader mismatch: ' + fmt)
        # Read-only and invalid create requests are measured, never guessed as UnsupportedCapability.
        for fmt in ['rar', 'iso', 'not-a-format']:
            run('create/' + fmt, ['a', '-t' + fmt, root / ('created.' + fmt), 'payload.bin'])
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('exe', type=Path)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--expect', type=Path)
    args = parser.parse_args()
    if args.report.resolve().is_relative_to(HERE) or (args.expect and args.report.resolve() == args.expect.resolve()):
        parser.error('capture must not overwrite checked-in corpus or expected report')
    manifest = json.loads((HERE / 'manifest.json').read_text())
    verify_fixtures(manifest, HERE / 'fixtures')
    report = capture(args.exe.resolve(), manifest)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    if args.expect:
        compare(report, json.loads(args.expect.read_text(encoding='utf-8')))
    print(f"B01 {report['platform']}: {len(report['observations'])} operations captured" + ('; comparison PASS' if args.expect else '; NOT yet reviewed'))


if __name__ == '__main__':
    main()
