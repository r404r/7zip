"""Opaque B01-Q bookkeeping. No archive parser or execution dependency."""
import hashlib
import json
import os
from pathlib import Path
import stat


MISSING_MIME_URLS = frozenset((
    'https://sources.debian.org/data/main/p/python-rarfile/4.5-1/test/files/rar3-old.r00',
    'https://sources.debian.org/data/main/p/python-rarfile/4.5-1/test/files/rar3-old.r01',
))


def check_headers(status, headers, declared_size, original_url=''):
    """Fail closed before reading payload, including redirects and error pages."""
    if hasattr(headers, 'get_all'):
        for name in ('Content-Length', 'Content-Type', 'Content-Encoding', 'Transfer-Encoding', 'Location'):
            if len(headers.get_all(name, [])) > 1:
                raise ValueError(f'duplicate response header: {name}')
    if status != 200:
        raise ValueError(f'unexpected HTTP status: {status}')
    if headers.get('Content-Length') != str(declared_size):
        raise ValueError(f'Content-Length mismatch: {headers.get("Content-Length")!r}')
    if headers.get('Transfer-Encoding') or headers.get('Content-Encoding'):
        raise ValueError('unexpected transfer/content encoding')
    if headers.get('Location'):
        raise ValueError('unexpected redirect location')
    raw_media = headers.get('Content-Type')
    if raw_media is None and original_url in MISSING_MIME_URLS:
        return  # Exact operator-approved absent-header exception; never infer MIME.
    media = (raw_media or '').split(';')[0].strip().lower()
    if media not in ('application/octet-stream', 'application/x-rar-compressed',
                     'application/vnd.rar', 'application/x-rar'):
        raise ValueError(f'unexpected Content-Type: {media!r}')


def read_bounded(response, declared_size):
    """Never request more than the remaining approved response bytes."""
    chunks = []
    remaining = declared_size
    while remaining:
        chunk = response.read(min(65536, remaining))
        if not chunk or len(chunk) > remaining:
            raise ValueError('response size mismatch')
        chunks.append(chunk)
        remaining -= len(chunk)
    return b''.join(chunks)


def verify_local(manifest, baseline, root, notice, require_complete=False):
    """Verify a pinned manifest and exact private tree, returning missing records.

    Callers authenticate baseline separately. Never traverse links or parse archives.
    This assumes a private, single-worker root; concurrent owner edits are forbidden.
    """
    def require(condition, message):
        if not condition:
            raise ValueError(message)

    def regular(path, size=None, mode=None):
        info = path.lstat()
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
                info.st_uid == os.getuid(), f'unsafe regular file: {path}')
        require(size is None or info.st_size == size, f'wrong size: {path}')
        require(mode is None or stat.S_IMODE(info.st_mode) == mode, f'wrong mode: {path}')
        return path.read_bytes()

    try:
        root = Path(root)
        require(root.is_absolute() and root.resolve() == root, 'unsafe root')
        require(manifest['quarantine_root'] == str(root), 'root mismatch')
        require({k: v for k, v in manifest.items() if k not in ('status', 'candidates')} ==
                {k: v for k, v in baseline.items() if k not in ('status', 'candidates')},
                'top-level metadata mismatch')
        require(manifest['status'] in ('quarantine_incomplete', 'quarantine_complete'), 'accepted status')
        require(list(manifest['candidates']) == list(baseline['candidates']), 'candidate set/order')
        expected_root = set(manifest['candidates']) | {'manifest.json'}
        if (root / 'resume.json').exists():
            expected_root.add('resume.json')
            regular(root / 'resume.json')
        require(set(p.name for p in root.iterdir()) == expected_root, 'extra/missing root file')
        require(json.loads(regular(root / 'manifest.json')) == baseline, 'original evidence changed')
        pending = []
        for directory in [root] + [root / cid for cid in manifest['candidates']]:
            info = directory.lstat()
            require(stat.S_ISDIR(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o700 and
                    info.st_uid == os.getuid(), 'unsafe directory')
        dynamic = {'final_url', 'actual_size', 'sha256', 'retrieval_outcome', 'retrieved_at_utc',
                   'http_status', 'response_headers', 'tls_validation', 'error'}
        for cid, family in manifest['candidates'].items():
            previous = baseline['candidates'][cid]
            require({k: v for k, v in family.items() if k != 'files'} ==
                    {k: v for k, v in previous.items() if k != 'files'}, 'family metadata changed')
            require(len(family['files']) == len(previous['files']), 'file count mismatch')
            directory = root / cid
            require(regular(directory / 'NOTICE.txt', len(notice)) == notice, 'notice mismatch')
            expected_files = {'NOTICE.txt'}
            for item, old in zip(family['files'], previous['files']):
                require({k: v for k, v in item.items() if k not in dynamic} ==
                        {k: v for k, v in old.items() if k not in dynamic}, 'file metadata changed')
                require(item['status'] == 'quarantine' and item['import_approved'] is False and
                        item['qualified'] is False, 'accepted file status')
                path = directory / (Path(item['path']).name + '.opaque')
                require(item['local_opaque_path'] == str(path), 'opaque path mismatch')
                require(item['local_notice_path'] == str(directory / 'NOTICE.txt') and
                        item['notice_sha256'] == hashlib.sha256(notice).hexdigest(), 'notice binding')
                outcome = item['retrieval_outcome']
                if old['retrieval_outcome'] == 'acquired_quarantined':
                    require(item == old, 'previous success changed')
                if outcome == 'acquired_quarantined':
                    require(item['final_url'] == item['original_url'], 'final URL mismatch')
                    if old['retrieval_outcome'] != 'acquired_quarantined':
                        check_headers(item['http_status'], item['response_headers'],
                                      item['declared_size'], item['original_url'])
                        require(item['tls_validation'] ==
                                'ssl.create_default_context; certificate and hostname verified', 'TLS evidence')
                        require(bool(item['retrieved_at_utc']) and 'error' not in item, 'retrieval evidence')
                    require(item['actual_size'] == item['declared_size'], 'actual size mismatch')
                    data = regular(path, item['declared_size'], 0o400)
                    require(hashlib.sha256(data).hexdigest() == item['sha256'], 'opaque hash mismatch')
                    expected_files.add(path.name)
                else:
                    require(outcome in ('not_attempted', 'request_started', 'failed_stopped'), 'unknown outcome')
                    require(item['actual_size'] is None and item['sha256'] is None, 'pending bytes claimed')
                    require(item['final_url'] in (None, item['original_url']), 'pending final URL mismatch')
                    pending.append(item)
            require(set(p.name for p in directory.iterdir()) == expected_files, 'extra/missing family file')
        require((manifest['status'] == 'quarantine_complete') == (not pending), 'completion status mismatch')
        require(not require_complete or not pending, 'incomplete quarantine')
        return pending
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise ValueError(f'invalid quarantine evidence: {error}') from error
