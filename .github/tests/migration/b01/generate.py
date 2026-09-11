#!/usr/bin/env python3
"""One-shot fixture authoring, never run by regression CI; refuses replacement."""
import argparse
import bz2
import gzip
import hashlib
import io
import json
import lzma
from pathlib import Path
import platform
import struct
import subprocess
import zipfile
import tarfile

HERE = Path(__file__).resolve().parent
PAYLOAD = bytes(range(256)) * 16


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('exe', type=Path)
    args = parser.parse_args()
    exe = args.exe.resolve()
    dest = HERE / 'fixtures'
    dest.mkdir()  # deliberate refusal to overwrite immutable evidence
    records = []

    def save(name, data, fmt, method, recipe, generator='CPython stdlib', base=None):
        (dest / name).write_bytes(data)
        records.append(dict(id=name, files=[dict(path=name, sha256=hashlib.sha256(data).hexdigest())],
                            format=fmt, method=method, generator=generator,
                            version=platform.python_version() if generator == 'CPython stdlib' else version,
                            license='Generated numeric byte sequence; no third-party archive payload. Scripts follow repository licensing.',
                            provenance=dict(recipe=recipe, source='generate.py', base=base),
                            operations=['list', 'test', 'extract'], native_oracle_reports=[]))

    for label, method in [('store', zipfile.ZIP_STORED), ('deflate', zipfile.ZIP_DEFLATED),
                          ('bzip2', zipfile.ZIP_BZIP2), ('lzma', zipfile.ZIP_LZMA)]:
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w') as archive:
            info = zipfile.ZipInfo('payload.bin', (2023, 11, 14, 22, 13, 20))
            info.compress_type = method
            archive.writestr(info, PAYLOAD)
        save(f'{label}.zip', stream.getvalue(), 'zip', label, f'zipfile method={method}, fixed timestamp, payload.bin=bytes(range(256))*16')
    stored = (dest / 'store.zip').read_bytes()
    crc = bytearray(stored)
    offset = 30 + struct.unpack_from('<H', crc, 26)[0] + struct.unpack_from('<H', crc, 28)[0]
    crc[offset] ^= 1
    save('crc.zip', bytes(crc), 'zip', 'store', f'Flip first payload byte at {offset}, retain CRC', base='store.zip')
    unsupported = bytearray(stored)
    struct.pack_into('<H', unsupported, 8, 65535)
    struct.pack_into('<H', unsupported, unsupported.index(b'PK\x01\x02') + 10, 65535)
    save('unsupported.zip', bytes(unsupported), 'zip', '65535', 'Set local/central compression method to 65535', base='store.zip')
    damaged = bytearray((dest / 'deflate.zip').read_bytes())
    damaged[offset] = 7  # reserved DEFLATE block type, not a guessed expected result
    save('data.zip', bytes(damaged), 'zip', 'deflate', f'Set first compressed byte at {offset} to 7', base='deflate.zip')
    save('truncated.zip', stored[:16], 'zip', 'store', 'Keep first 16 bytes', base='store.zip')
    save('misnamed.dat', stored, 'zip', 'store', 'Identical bytes, non-archive extension', base='store.zip')
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w', format=tarfile.USTAR_FORMAT) as archive:
        info = tarfile.TarInfo('payload.bin')
        info.size, info.mtime, info.mode = len(PAYLOAD), 1700000000, 0o644
        archive.addfile(info, io.BytesIO(PAYLOAD))
    tar = stream.getvalue()
    save('payload.tar', tar, 'tar', 'ustar', 'tarfile USTAR numeric payload, uid/gid=0, mtime=1700000000')
    for name, data, fmt, method in [('payload.gz', gzip.compress(PAYLOAD, mtime=0), 'gzip', 'deflate'),
                                    ('payload.bz2', bz2.compress(PAYLOAD), 'bzip2', 'bzip2'),
                                    ('payload.xz', lzma.compress(PAYLOAD), 'xz', 'lzma2'),
                                    ('payload.lzma', lzma.compress(PAYLOAD, format=lzma.FORMAT_ALONE), 'lzma', 'lzma'),
                                    ('nested.tar.gz', gzip.compress(tar, mtime=0), 'gzip', 'deflate+tar')]:
        save(name, data, fmt, method, 'stdlib default compression; gzip mtime=0; input numeric payload or payload.tar')
    version = subprocess.check_output([str(exe), 'i']).decode('utf-8')
    (dest / 'payload.bin').write_bytes(PAYLOAD)
    commands = []
    for name, options in [('copy.7z', ['-m0=Copy']), ('lzma2.7z', ['-m0=LZMA2']),
                           ('volume.7z', ['-m0=Copy', '-v1k'])]:
        argv = [str(exe), 'a', name, 'payload.bin', *options, '-mtc=off', '-mta=off', '-mtm=off']
        proc = subprocess.run(argv, cwd=dest, capture_output=True, check=True)
        commands.append(dict(argv=argv, exit=proc.returncode, stdout=proc.stdout.decode(), stderr=proc.stderr.decode()))
        files = sorted(dest.glob(name + '*'))
        save_name = files[0].name
        # Archives already exist; register them without regenerating their bytes.
        records.append(dict(id=save_name, files=[dict(path=p.name, sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files],
                            format='7z' if len(files) == 1 else 'Split', method=options[0], generator='retained Alone2', version=version,
                            license='Generated numeric byte sequence; no third-party archive payload. Engine licensing unchanged.',
                            provenance=dict(recipe=argv, source='generate.py', base=None),
                            operations=['list', 'test', 'extract'], native_oracle_reports=[]))
    header = bytearray((dest / 'copy.7z').read_bytes())
    header[12] ^= 1
    save('header.7z', bytes(header), '7z', 'Copy', 'Flip start-header byte 12 without updating start-header CRC', 'retained Alone2', 'copy.7z')
    save('truncated.7z', (dest / 'copy.7z').read_bytes()[:16], '7z', 'Copy', 'Keep first 16 bytes', 'retained Alone2', 'copy.7z')
    (dest / 'payload.bin').unlink()
    manifest = dict(schema_version=1, fixtures=records,
                    payload=dict(recipe='bytes(range(256))*16', sha256=hashlib.sha256(PAYLOAD).hexdigest(), size=len(PAYLOAD)),
                    authoring=dict(python=platform.python_version(), platform=platform.platform(),
                                   executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(), commands=commands,
                                   commit=subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()),
                    qualification='Only explicitly measured cases; all other capabilities remain unqualified')
    (HERE / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
