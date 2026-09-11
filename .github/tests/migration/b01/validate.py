#!/usr/bin/env python3
"""Offline corpus integrity; does not replace live native qualification or review."""
import base64
import json
from pathlib import Path
import re
import capture
import summarize


def main():
    manifest_bytes = (capture.HERE / 'manifest.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    assert manifest['schema_version'] == 1
    capture.verify_fixtures(manifest, capture.HERE / 'fixtures')
    inventory = json.loads((capture.HERE / 'inventory.json').read_text())
    for name, os_name in [('linux', 'Linux'), ('windows', 'Windows'), ('macos', 'Darwin')]:
        report = json.loads((capture.HERE / 'oracles' / (name + '.json')).read_text())
        assert report['platform']['os'] == os_name
        lf = manifest_bytes.replace(b'\r\n', b'\n')
        representation = lf.replace(b'\n', b'\r\n') if name == 'windows' else lf
        assert report['manifest_sha256'] == capture.sha(representation), name
        assert report['provenance']['engine_diff'] == ''
        assert len(report['commands']) == len(report['observations']) == 96
        for command in report['commands'].values():
            base64.b64decode(command['stdout_base64'], validate=True)
            base64.b64decode(command['stderr_base64'], validate=True)
        for fixture in manifest['fixtures']:
            assert fixture['generator'] and fixture['version'] and fixture['license'] and fixture['provenance']
            for link in fixture['native_oracle_reports']:
                assert (capture.HERE / link).is_file(), link
            for operation in fixture['operations']:
                assert fixture['id'] + '/' + operation in report['observations']
        current = summarize.inventory(report)
        assert [r['format'] for r in current['formats']] == [r['format'] for r in inventory['formats']]
        assert len(set(r['format'] for r in current['formats'])) == len(current['formats'])
        print(name, 'manifest representation/raw encoding/operations/inventory PASS')
    assert all(not r['production_release'] for r in inventory['formats'])
    print('fixtures', len(manifest['fixtures']), 'immutable files', sum(len(f['files']) for f in manifest['fixtures']))
    print('formats', len(inventory['formats']), 'covered', sum(r['status'] == 'covered' for r in inventory['formats']),
          'unqualified', sum(r['status'] == 'unqualified' for r in inventory['formats']))
    doc = capture.REPO / 'docs/ai-migration/qualification/b01.md'
    for target in re.findall(r'\]\(([^)]+)\)', doc.read_text()):
        if not target.startswith('https://'):
            assert (doc.parent / target.split('#')[0]).exists(), target
    print('documentation local links PASS')


if __name__ == '__main__':
    main()
