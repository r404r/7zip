"""Offline partial documentation checks; NOT the pending byte-manifest verifier."""
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
report = REPO / 'docs/ai-migration/qualification/b01-quarantine-acquisition.md'
matrix_path = REPO / 'docs/ai-migration/qualification/b01-o1-rights-review.json'
matrix = json.loads(matrix_path.read_text())
manifest = json.loads((HERE / 'manifest.json').read_text())
assert hashlib.sha256(matrix_path.read_bytes()).hexdigest() == manifest['matrix_sha256']
assert manifest['schema_version'] == 1
assert manifest['status'] == 'quarantine_incomplete'
assert manifest['import_approved'] is False and manifest['qualified'] is False
files = [f for c in manifest['candidates'].values() for f in c['files']]
assert len(files) == 7
outcomes = {outcome: sum(f['retrieval_outcome'] == outcome for f in files)
            for outcome in ('acquired_quarantined', 'failed_stopped', 'not_attempted')}
assert outcomes == {'acquired_quarantined': 1, 'failed_stopped': 1, 'not_attempted': 5}
notice = (matrix['rights_common']['literal_selected_stanza'] + '\n').encode()
for cid in manifest['candidates']:
    assert (HERE / (cid + '-NOTICE.txt')).read_bytes() == notice
    assert (Path(manifest['quarantine_root']) / cid / 'NOTICE.txt').read_bytes() == notice
links = re.findall(r'\]\(([^)]+)\)', report.read_text())
for link in links:
    assert not link.startswith(('http:', 'https:'))
    assert (report.parent / link).is_file(), link
assert (Path(manifest['quarantine_root']) / 'manifest.json').read_bytes() == (HERE / 'manifest.json').read_bytes()
print('Partial JSON/notice/link checks PASS:', outcomes, 'local links:', len(links))
print('Not a full manifest verifier; pending negative controls are not claimed.')
