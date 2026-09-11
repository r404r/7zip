"""One bounded continuation; offline by default. Stage review required before GETs.

Original manifest and failed-response evidence are never overwritten. resume.json
is both a durable attempt marker and a separate result. Any interruption or second
failure requires inspection, not a rerun/delete/retry loop. No archive libraries.
"""
import copy
import datetime
import hashlib
import http.client
import json
import os
from pathlib import Path
import ssl
import stat
import sys
from urllib.parse import urlsplit

from acquire import HERE, IDS, MATRIX, MATRIX_SHA256, ROOT
from quarantine import check_headers, read_bounded, verify_local

BASELINE_SHA256 = '5bf0600459996c638697eb902d789670186db72197d65665b3ee881b0f59655e'


def load_evidence():
    raw = (HERE / 'manifest.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != BASELINE_SHA256:
        raise ValueError('original stopped manifest digest mismatch')
    matrix_raw = MATRIX.read_bytes()
    if hashlib.sha256(matrix_raw).hexdigest() != MATRIX_SHA256:
        raise ValueError('reviewed matrix digest mismatch')
    baseline = json.loads(raw)
    matrix = json.loads(matrix_raw)
    if list(baseline['candidates']) != IDS or list(matrix['candidates']) != IDS:
        raise ValueError('candidate allowlist mismatch')
    notice = (matrix['rights_common']['literal_selected_stanza'] + '\n').encode()
    for cid in IDS:
        files = baseline['candidates'][cid]['files']
        originals = matrix['candidates'][cid]['files']
        if len(files) != len(originals):
            raise ValueError('pinned file count mismatch')
        for index, (item, original) in enumerate(zip(files, originals), 1):
            if (item['path'], item['original_url'], item['declared_size'], item['part_order']) != (
                    original['path'], original['retrieval_url'], original['declared_size'], index):
                raise ValueError('matrix source/size/order mismatch')
        if (HERE / (cid + '-NOTICE.txt')).read_bytes() != notice:
            raise ValueError('tracked notice mismatch')
    return baseline, notice


def fetch_one(item):
    """GET exactly the preflight-bound URL; no redirects, alternate sources or retry."""
    url = item['original_url']
    parts = urlsplit(url)
    if parts.scheme != 'https' or parts.netloc != 'sources.debian.org' or parts.query or parts.fragment:
        raise ValueError('source identity mismatch')
    connection = http.client.HTTPSConnection(parts.netloc, timeout=30, context=ssl.create_default_context())
    try:
        connection.request('GET', parts.path, headers={
            'Accept': 'application/octet-stream', 'Accept-Encoding': 'identity',
            'User-Agent': 'B01-Q-bounded-acquisition/1', 'Connection': 'close'})
        response = connection.getresponse()
        item.update(final_url=url, http_status=response.status,
                    response_headers={key: response.getheader(key) for key in
                        ('Content-Type', 'Content-Length', 'Content-Encoding', 'Transfer-Encoding',
                         'Location', 'ETag', 'Last-Modified')},
                    tls_validation='ssl.create_default_context; certificate and hostname verified')
        check_headers(response.status, response.headers, item['declared_size'], url)
        data = read_bounded(response, item['declared_size'])
        if data.lstrip().lower().startswith((b'<!doctype html', b'<html')):
            raise ValueError('unexpected HTML body; not retained as archive')
        return data
    finally:
        connection.close()


def run_resume(baseline, root, notice, fetch=fetch_one):
    """Only the six verified missing records; fetch injection is for local controls."""
    state = root / 'resume.json'
    if state.exists() or state.is_symlink():
        raise ValueError('resume already attempted; preserve evidence and inspect, never rerun')
    manifest = copy.deepcopy(baseline)
    pending = verify_local(manifest, baseline, root, notice)
    if len(pending) != 6 or [f['retrieval_outcome'] for f in pending] != ['failed_stopped'] + ['not_attempted'] * 5:
        raise ValueError('not the approved stopped six-file continuation')
    os.umask(0o077)
    # Exclusive attempt marker is created before any network, so retries fail closed.
    with state.open('x', encoding='utf-8') as output:
        json.dump(manifest, output, indent=2, ensure_ascii=False)
        output.write('\n')
        output.flush()
        os.fsync(output.fileno())

    def save():
        temporary = root / '.resume.json.tmp'
        with temporary.open('x', encoding='utf-8') as output:
            json.dump(manifest, output, indent=2, ensure_ascii=False)
            output.write('\n')
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, state)  # Replace only this new attempt's own state.

    for item in pending:
        try:
            for key in ('error', 'response_headers', 'http_status', 'tls_validation'):
                item.pop(key, None)  # Prior response remains verbatim in original manifest.
            item.update(final_url=None, retrieval_outcome='request_started',
                        retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
            save()
            data = fetch(item)
            if len(data) != item['declared_size']:
                raise ValueError('actual response size mismatch')
            target = Path(item['local_opaque_path'])
            with target.open('xb') as output:
                output.write(data)
                output.flush()
                os.fsync(output.fileno())
            target.chmod(0o400)
            item.update(actual_size=len(data), sha256=hashlib.sha256(data).hexdigest(),
                        retrieval_outcome='acquired_quarantined')
            if item is pending[-1]:
                manifest['status'] = 'quarantine_complete'
            verify_local(manifest, baseline, root, notice)  # Reopen and hash every acquired file.
            save()
        except Exception as error:
            manifest['status'] = 'quarantine_incomplete'
            item.update(retrieval_outcome='failed_stopped', error=f'{type(error).__name__}: {error}')
            save()
            print(item['error'], file=sys.stderr)
            return 1
    verify_local(manifest, baseline, root, notice, require_complete=True)
    return 0


def main():
    args = sys.argv[1:]
    if args not in (['--preflight'], ['--verify-complete'], ['--resume-reviewed-six']):
        raise SystemExit('Use --preflight (offline), --verify-complete (offline), or --resume-reviewed-six AFTER stage PASS')
    baseline, notice = load_evidence()
    manifest = baseline
    if args == ['--verify-complete']:
        state = ROOT / 'resume.json'
        if ROOT.resolve() != ROOT or not stat.S_ISREG(state.lstat().st_mode):
            raise ValueError('unsafe resume state')
        manifest = json.loads(state.read_text())
    pending = verify_local(manifest, baseline, ROOT, notice, require_complete=args == ['--verify-complete'])
    if hashlib.sha256((ROOT / 'manifest.json').read_bytes()).hexdigest() != BASELINE_SHA256:
        raise ValueError('durable original manifest bytes changed')
    if args == ['--resume-reviewed-six']:
        return run_resume(baseline, ROOT, notice)
    print(json.dumps({'offline': True, 'pending_paths': [f['path'] for f in pending],
                      'status': manifest['status'], 'import_approved': False, 'qualified': False}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
