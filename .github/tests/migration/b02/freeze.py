#!/usr/bin/env python3
"""Freeze downloaded native reports losslessly, with checksummed provenance."""
import argparse
import gzip
import json
from pathlib import Path

from run import compare, sha
from validate import validate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('download', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    assert not args.destination.exists(), 'Immutable evidence directory already exists'
    candidates = sorted(args.download.glob('b02-*/capture.json'))
    assert len(candidates) == 3, 'Require all native platforms'
    manifests = []
    platforms = set()
    heads = set()
    for file in candidates:
        capture = json.loads(file.read_text())
        repeat = json.loads(file.with_name('repeat.json').read_text())
        validate(capture)
        compare(capture, repeat)
        obs, provenance = capture['observations'], capture['provenance']
        platforms.add(obs['platform'])
        heads.add(provenance['head'])
        assert provenance['run_id'], 'Not a native CI report'
        manifests.append((file.parent, obs['platform'], provenance))
    assert platforms == {'Windows', 'Linux', 'Darwin'}
    assert len(heads) == 1
    manifest: dict = {'head': heads.pop(), 'files': {}}
    for source, platform, provenance in manifests:
        destination = args.destination / platform
        destination.mkdir(parents=True)
        for path in sorted(source.rglob('*')):
            if not path.is_file():
                continue
            data = path.read_bytes()
            relative = path.relative_to(source)
            output = destination / relative
            if path.suffix in ('.json', '.log'):
                output = output.with_suffix(output.suffix + '.gz')
                encoded = gzip.compress(data, mtime=0)
                assert gzip.decompress(encoded) == data
            else:
                encoded = data
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(encoded)
            manifest['files'][str(output.relative_to(args.destination))] = {
                'source_sha256': sha(data), 'stored_sha256': sha(encoded),
                'source_bytes': len(data), 'stored_bytes': len(encoded),
                'run_id': provenance['run_id'], 'run_attempt': provenance['run_attempt']}
    (args.destination / 'manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    print(f"Frozen {len(manifest['files'])} native evidence files for {manifest['head']}")


if __name__ == '__main__':
    main()
