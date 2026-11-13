"""One-shot approved acquisition. No retries, redirects, parsing or archive tools."""
import datetime
import hashlib
import http.client
import json
import os
from pathlib import Path
import ssl
import sys
from urllib.parse import urlsplit

from quarantine import check_headers, check_opaque_body, read_bounded

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
MATRIX = REPO / 'docs/ai-migration/qualification/b01-o1-rights-review.json'
MATRIX_SHA256 = '0f8af166ddbd150f951a1910525c1d842275f3e20e2ff9731b24ac39b70a02a8'
ROOT = Path('/home/ding/work/github/r404r/b01-quarantine-t_d32ff791')
IDS = ['DRF-OLD', 'DRF-SOLID', 'DRF-VOL']


def main():
    if sys.argv[1:] != ['--acquire-approved-seven']:
        raise SystemExit('Requires --acquire-approved-seven; never rerun without inspecting prior outcome')
    raw = MATRIX.read_bytes()
    if hashlib.sha256(raw).hexdigest() != MATRIX_SHA256:
        raise SystemExit('reviewed matrix digest mismatch')
    matrix = json.loads(raw)
    if list(matrix['candidates']) != IDS:
        raise SystemExit('candidate allowlist mismatch')
    os.umask(0o077)
    ROOT.mkdir(mode=0o700, exist_ok=False)  # no replacement or silent resumption
    notice = matrix['rights_common']['literal_selected_stanza'] + '\n'
    manifest = {
        'schema_version': 1, 'task_id': 't_d32ff791',
        'status': 'quarantine_incomplete', 'import_approved': False, 'qualified': False,
        'authority': 'B01 operator decision 批准方案1, recorded 1789128797; acquisition/quarantine only',
        'reviewed_parent_commit': '3cf4421d081b912763e326c47322f095211fbd47',
        'matrix_path': str(MATRIX.relative_to(REPO)), 'matrix_sha256': MATRIX_SHA256,
        'distribution': 'python-rarfile', 'version': '4.5-1',
        'quarantine_root': str(ROOT),
        'rights_limitations': {k: matrix['rights_common'][k] for k in
                              ('member_metadata_applicability', 'grant_authority', 'exceptions')},
        'hash_meaning': 'Identity of acquired opaque bytes only; not proof of rights or compatibility',
        'candidates': {}, 'accepted_fixtures': [], 'native_results_produced': False,
    }
    for cid in IDS:
        original = matrix['candidates'][cid]
        family = ROOT / cid
        family.mkdir(mode=0o700)
        (family / 'NOTICE.txt').write_text(notice, encoding='utf-8')
        (HERE / (cid + '-NOTICE.txt')).write_text(notice, encoding='utf-8')
        manifest['candidates'][cid] = {
            'status': 'quarantine', 'import_approved': False, 'qualified': False,
            'proposed_volume_order': original['proposed_volume_order'],
            'volume_order_basis': original['volume_order_basis'],
            'historical_writer': original['historical_writer'],
            'actual_member_hashes': None, 'actual_member_rights': None,
            'unknown_reason': 'No member parsing/extraction/rights inventory authorized in B01-Q',
            'files': []}
        for index, item in enumerate(original['files'], 1):
            manifest['candidates'][cid]['files'].append({
                'path': item['path'], 'original_url': item['retrieval_url'], 'final_url': None,
                'distribution': 'python-rarfile', 'version': '4.5-1', 'part_order': index,
                'declared_size': item['declared_size'], 'size_source_id': item['size_source_id'],
                'actual_size': None, 'sha256': None,
                'local_opaque_path': str(family / (Path(item['path']).name + '.opaque')),
                'notice_reference': cid + '-NOTICE.txt', 'local_notice_path': str(family / 'NOTICE.txt'),
                'notice_sha256': hashlib.sha256(notice.encode()).hexdigest(),
                'retrieval_outcome': 'not_attempted', 'retrieved_at_utc': None,
                'status': 'quarantine', 'import_approved': False, 'qualified': False,
            })

    def save():
        text = json.dumps(manifest, indent=2, ensure_ascii=False) + '\n'
        (HERE / 'manifest.json').write_text(text, encoding='utf-8')
        (ROOT / 'manifest.json').write_text(text, encoding='utf-8')

    save()
    try:
        for candidate in manifest['candidates'].values():
            for item in candidate['files']:
                url = item['original_url']
                parts = urlsplit(url)
                if parts.scheme != 'https' or parts.netloc != 'sources.debian.org' or parts.query or parts.fragment:
                    raise ValueError('source identity mismatch')
                item['retrieved_at_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                item['retrieval_outcome'] = 'request_started'
                save()
                connection = http.client.HTTPSConnection(parts.netloc, timeout=30,
                                                         context=ssl.create_default_context())
                try:
                    connection.request('GET', parts.path, headers={
                        'Accept': 'application/octet-stream', 'Accept-Encoding': 'identity',
                        'User-Agent': 'B01-Q-bounded-acquisition/1', 'Connection': 'close'})
                    response = connection.getresponse()
                    item['final_url'] = url  # http.client does not follow redirects
                    item['http_status'] = response.status
                    item['response_headers'] = {key: response.getheader(key) for key in
                        ('Content-Type', 'Content-Length', 'Content-Encoding', 'Transfer-Encoding',
                         'Location', 'ETag', 'Last-Modified')}
                    item['tls_validation'] = 'ssl.create_default_context; certificate and hostname verified'
                    check_headers(response.status, response.headers, item['declared_size'])
                    data = read_bounded(response, item['declared_size'])
                    check_opaque_body(data)
                    target = Path(item['local_opaque_path'])
                    with target.open('xb') as output:
                        output.write(data)
                    target.chmod(0o400)
                    item['actual_size'] = len(data)
                    item['sha256'] = hashlib.sha256(data).hexdigest()
                    # Independent reopen of local opaque bytes, never parse them.
                    reread = target.read_bytes()
                    if len(reread) != item['actual_size'] or hashlib.sha256(reread).hexdigest() != item['sha256']:
                        raise ValueError('local reread mismatch')
                    item['retrieval_outcome'] = 'acquired_quarantined'
                    print(json.dumps({'path': item['path'], 'size': item['actual_size'],
                                      'sha256': item['sha256']}), flush=True)
                finally:
                    connection.close()
                save()
    except Exception as error:
        item['retrieval_outcome'] = 'failed_stopped'
        item['error'] = f'{type(error).__name__}: {error}'
        save()
        print(item['error'], file=sys.stderr)
        return 1
    manifest['status'] = 'quarantine_complete'
    save()
    print('Seven opaque files acquired; no corpus import or qualification.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
