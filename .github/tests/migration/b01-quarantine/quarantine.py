"""Opaque B01-Q bookkeeping. No archive parser or execution dependency."""


def check_headers(status, headers, declared_size):
    """Fail closed before reading payload, including redirects and error pages."""
    if status != 200:
        raise ValueError(f'unexpected HTTP status: {status}')
    if headers.get('Content-Length') != str(declared_size):
        raise ValueError(f'Content-Length mismatch: {headers.get("Content-Length")!r}')
    if headers.get('Transfer-Encoding') or headers.get('Content-Encoding'):
        raise ValueError('unexpected transfer/content encoding')
    media = headers.get('Content-Type', '').split(';')[0].strip().lower()
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
