#!/usr/bin/env python3
"""Losslessly freeze/verify candidate evidence; never fabricate observations."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
from validate import compare, validate, negative_controls


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify(dest):
    manifest = json.loads((dest / 'manifest.json').read_text())
    assert manifest['status'] == 'unreviewed-candidate'
    reports = {}
    build_raw = None
    for name, info in manifest['files'].items():
        p = Path(name)
        assert not p.is_absolute() and '..' not in p.parts
        stored = (dest / p).read_bytes()
        assert len(stored) == info['stored_size'] and sha(stored) == info['stored_sha256'], name
        raw = gzip.decompress(stored)
        assert len(raw) == info['raw_size'] and sha(raw) == info['raw_sha256'], name
        if name in ('capture.json.gz', 'repeat.json.gz'):
            reports[name] = json.loads(raw)
        if name == 'build.json.gz':
            build_raw = raw
    assert build_raw is not None
    for report in reports.values():
        assert report['build_sha256'] == sha(build_raw)
        assert report['executables'] == json.loads(build_raw)['executables']
    compare(reports['capture.json.gz'], reports['repeat.json.gz'])
    negative_controls(reports['capture.json.gz'])
    print(f'PASS: {len(manifest["files"])} immutable evidence files')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('destination', type=Path)
    p.add_argument('--work', type=Path)
    p.add_argument('--capture', type=Path)
    p.add_argument('--repeat', type=Path)
    a = p.parse_args()
    if a.work is None:
        verify(a.destination)
        return
    assert a.capture and a.repeat
    assert not a.destination.exists(), 'Refuse to overwrite captured evidence'
    capture = json.loads(a.capture.read_text())
    repeat = json.loads(a.repeat.read_text())
    validate(capture)
    compare(capture, repeat)
    sources = {'capture.json': a.capture, 'repeat.json': a.repeat}
    for name in ('build.json', 'plain-build.log', 'probe-build.log'):
        sources[name] = a.work / name
    for label, report in [('capture', capture), ('repeat', repeat)]:
        root = Path(report['sandbox']).resolve()
        assert root.is_relative_to(a.work.resolve())
        for src in sorted(root.rglob('*')):
            if src.is_file() and (src.suffix in ('.zip', '.tar', '.7z') or src.parent.name == 'retained'):
                assert src.stat().st_size < 64 << 20
                sources[f'{label}-archives/{src.relative_to(root).as_posix()}'] = src
    a.destination.mkdir(parents=True)
    manifest = dict(status='unreviewed-candidate', platform=capture['platform'], files={})
    for name, path in sources.items():
        raw = path.read_bytes()
        stored = gzip.compress(raw, mtime=0)
        name += '.gz'
        target = a.destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(stored)
        manifest['files'][name] = dict(raw_size=len(raw), raw_sha256=sha(raw), stored_size=len(stored), stored_sha256=sha(stored))
    (a.destination / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    verify(a.destination)


if __name__ == '__main__':
    main()
