#!/usr/bin/env python3
"""Verify immutable captured bytes and summarize native outcomes offline."""
import argparse
import gzip
import json
from pathlib import Path

from run import compare, sha
from validate import validate


def verify(directory):
    manifest = json.loads((directory / 'manifest.json').read_text())
    for name, info in manifest['files'].items():
        stored = (directory / name).read_bytes()
        assert sha(stored) == info['stored_sha256'] and len(stored) == info['stored_bytes'], name
        data = gzip.decompress(stored) if name.endswith('.gz') else stored
        assert sha(data) == info['source_sha256'] and len(data) == info['source_bytes'], name
    for platform in ('Windows', 'Linux', 'Darwin'):
        capture = json.loads(gzip.decompress((directory / platform / 'capture.json.gz').read_bytes()))
        repeat = json.loads(gzip.decompress((directory / platform / 'repeat.json.gz').read_bytes()))
        assert capture['provenance']['head'] == manifest['head']
        validate(capture)
        compare(capture, repeat)
        cases = capture['observations']['cases']
        native = capture['observations']['native_roundtrip']
        print(platform, capture['provenance']['platform'])
        print(' native roundtrip exits:', {k: native[k]['exit'] for k in ('create', 'list', 'extract')})
        print(' native roundtrip tree:', json.dumps(native['tree']))
        for label in ('unicode-valid', 'unicode-bad-crc', 'efs-beats-extra', 'byte-escape-collision', 'long-component', 'long-path', 'reserved', 'trailing-dot-space', 'case-collision', 'normalization-collision'):
            case = cases[label]
            cli = case['cli']['default']
            print(' ', label, 'exits:', cli['listing']['exit'], cli['extraction']['exit'],
                  'tree:', json.dumps(cli['tree']))
        print(' option ordering trees match:', all(c['cli']['ordered_override'].get('tree') == c['cli']['scoped936'].get('tree') and c['cli']['reverse_override'].get('tree') == c['cli']['scoped932'].get('tree') for c in cases.values()))
    print(f"Verified {len(manifest['files'])} immutable evidence files; all native source relations and negative controls PASS")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=Path)
    verify(parser.parse_args().directory)
