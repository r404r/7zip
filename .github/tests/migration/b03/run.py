#!/usr/bin/env python3
"""Capture real legacy CLI metadata/ZIP64/I/O observations in bounded sandboxes."""
import argparse
import base64
import ctypes
import hashlib
import json
import locale
import os
from pathlib import Path
import platform
import shutil
import stat
import subprocess
import tempfile
import time
import zipfile

HERE = Path(__file__).resolve().parent
BIG = (1 << 32) + 33
STAMP = 1700000001123456789


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8 << 20), b''):
            h.update(block)
    return h.hexdigest()


def command(argv, cwd, env=None, timeout=300):
    e = dict(os.environ)
    e.pop('B03_MODE', None)
    e.pop('B03_FAULT', None)
    e.update(env or {})
    r = subprocess.run([str(x) for x in argv], cwd=cwd, env=e, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, timeout=timeout)
    return dict(argv=[str(x) for x in argv], env=env or {}, exit=r.returncode,
                stdout_b64=base64.b64encode(r.stdout).decode(), stderr_b64=base64.b64encode(r.stderr).decode())


def inventory(root):
    result = []
    for p in sorted(root.rglob('*')):
        s = p.lstat()
        if not stat.S_ISREG(s.st_mode) and not stat.S_ISDIR(s.st_mode):
            raise AssertionError(f'Unexpected non-regular sandbox entry: {p}')
        item = dict(path=p.relative_to(root).as_posix(), native_name_hex=os.fsencode(p.name).hex() if os.name != 'nt' else p.name.encode('utf-16le', 'surrogatepass').hex(),
                    kind='dir' if p.is_dir() else 'file', mode=s.st_mode, size=s.st_size,
                    mtime_ns=s.st_mtime_ns, atime_ns=s.st_atime_ns, ctime_ns=s.st_ctime_ns,
                    blocks=getattr(s, 'st_blocks', None), attributes=getattr(s, 'st_file_attributes', None))
        if p.is_file():
            if s.st_size > 64 << 20:
                raise AssertionError('Small-file inventory refuses unbounded hashing')
            item['sha256'] = digest(p)
            if os.name == 'nt':
                ads = Path(str(p) + ':b03')
                item['ads_b03_sha256'] = digest(ads) if ads.exists() else None
            elif platform.system() == 'Darwin':
                names = command(['xattr', str(p)], root)
                assert names['exit'] == 0, names
                item['xattrs'] = {}
                for name in base64.b64decode(names['stdout_b64']).decode().splitlines():
                    value = command(['xattr', '-px', name, str(p)], root)
                    assert value['exit'] == 0, value
                    item['xattrs'][name] = bytes.fromhex(base64.b64decode(value['stdout_b64']).decode()).hex()
            elif hasattr(os, 'listxattr'):
                try:
                    item['xattrs'] = {n: os.getxattr(p, n).hex() for n in sorted(os.listxattr(p))}
                except OSError as exc:
                    item['xattrs_error'] = exc.errno
        result.append(item)
    return result


def fs_info(root):
    if os.name == 'nt':
        import ctypes.wintypes as w
        k = ctypes.WinDLL('kernel32', use_last_error=True)
        volume = ctypes.create_unicode_buffer(1024)
        k.GetVolumePathNameW.argtypes = [w.LPCWSTR, w.LPWSTR, w.DWORD]
        k.GetVolumePathNameW.restype = w.BOOL
        k.GetVolumeInformationW.argtypes = [w.LPCWSTR, w.LPWSTR, w.DWORD, ctypes.POINTER(w.DWORD), ctypes.POINTER(w.DWORD), ctypes.POINTER(w.DWORD), w.LPWSTR, w.DWORD]
        k.GetVolumeInformationW.restype = w.BOOL
        assert k.GetVolumePathNameW(str(root), volume, len(volume))
        name = ctypes.create_unicode_buffer(256)
        fs = ctypes.create_unicode_buffer(256)
        serial, maximum, flags = w.DWORD(), w.DWORD(), w.DWORD()
        assert k.GetVolumeInformationW(volume.value, name, len(name), ctypes.byref(serial), ctypes.byref(maximum), ctypes.byref(flags), fs, len(fs))
        return dict(type=fs.value, max_component=maximum.value, flags=flags.value, volume=volume.value)
    return command(['stat', '-f', '-c', '%T', str(root)] if platform.system() == 'Linux' else ['stat', '-f', '%T', str(root)], root)


def sparse(path, size=BIG):
    with path.open('xb') as f:
        if os.name == 'nt':
            import msvcrt
            import ctypes.wintypes as w
            k = ctypes.WinDLL('kernel32', use_last_error=True)
            returned = w.DWORD()
            ok = k.DeviceIoControl(w.HANDLE(msvcrt.get_osfhandle(f.fileno())), 0x900c4,
                                   None, 0, None, 0, ctypes.byref(returned), None)
            if not ok:
                raise OSError(ctypes.get_last_error(), 'FSCTL_SET_SPARSE failed; refusing 4 GiB allocation')
        f.write(b'B03-BEGIN')
        f.seek(size - 7)
        f.write(b'B03-END')
    os.utime(path, ns=(STAMP, STAMP))
    s = path.stat()
    if hasattr(s, 'st_blocks'):
        assert s.st_blocks * 512 < 1 << 20, 'Sparse source unexpectedly allocated'
    return dict(size=s.st_size, blocks=getattr(s, 'st_blocks', None), attributes=getattr(s, 'st_file_attributes', None))


def probe(exe, archive, fmt, cwd):
    target = cwd / 'input.arc'
    if target.exists():
        target.unlink()
    # Hard link avoids copying sparse or multi-GiB inputs and stays on this volume.
    os.link(archive, target)
    try:
        r = command([exe], cwd, {'B03_MODE': fmt})
        assert r['exit'] == 0, r
        r['observed'] = json.loads(base64.b64decode(r['stdout_b64']))
        return r
    finally:
        target.unlink()


def capture(work, report):
    build = json.loads((work / 'build.json').read_text())
    plain = Path(build['executables']['plain']['path'])
    tested = Path(build['executables']['probe']['path'])
    for variant, exe in [('plain', plain), ('probe', tested)]:
        assert digest(exe) == build['executables'][variant]['sha256']
    result = dict(schema=1, platform=platform.system(), platform_detail=platform.platform(),
                  locale=locale.setlocale(locale.LC_ALL, None), timezone=list(time.tzname),
                  build_sha256=digest(work / 'build.json'), executables=build['executables'],
                  cases=[], probes=[], faults=[], large={}, limitations=[])
    result['harness_sha256'] = {p.name: digest(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.suffix in ('.py', '.inc', '.yml')}
    mask = os.umask(0)
    os.umask(mask)
    result['umask'] = mask
    sandbox = Path(tempfile.mkdtemp(prefix='b03-', dir=work))
    result['sandbox'] = str(sandbox)
    result['filesystem'] = fs_info(sandbox)
    # Save partial evidence on exceptions; failed runs must never become goldens.
    try:
        inputs = sandbox / 'inputs'
        inputs.mkdir()
        (inputs / 'directory').mkdir()
        (inputs / 'directory/child.txt').write_bytes(b'directory payload\n')
        (inputs / 'executable.sh').write_bytes(b'#!/bin/sh\nexit 0\n')
        (inputs / 'readonly.txt').write_bytes(b'readonly payload\n')
        (inputs / 'fractional.txt').write_bytes(b'fractional timestamp\n')
        os.chmod(inputs / 'executable.sh', 0o755)
        os.chmod(inputs / 'readonly.txt', 0o444)
        os.chmod(inputs / 'directory', 0o750)
        capability = {}
        if os.name == 'nt':
            try:
                Path(str(inputs / 'fractional.txt') + ':b03').write_bytes(b'native ADS payload')
                capability['ads'] = 'created'
            except OSError as exc:
                capability['ads'] = dict(winerror=exc.winerror)
            capability['security'] = command(['icacls', str(inputs)], sandbox)
        else:
            key = 'user.b03' if platform.system() == 'Linux' else 'org.b03'
            if platform.system() == 'Darwin':
                capability['xattr'] = command(['xattr', '-w', key, 'native xattr payload', str(inputs / 'fractional.txt')], sandbox)
            else:
                try:
                    os.setxattr(inputs / 'fractional.txt', key, b'native xattr payload')
                    capability['xattr'] = dict(name=key, status='created')
                except OSError as exc:
                    capability['xattr'] = dict(errno=exc.errno)
            if platform.system() == 'Darwin':
                capability['acl'] = command(['chmod', '+a', 'everyone deny delete', str(inputs / 'fractional.txt')], sandbox)
            elif shutil.which('setfacl'):
                capability['acl'] = command(['setfacl', '-m', 'u:65534:r--', str(inputs / 'fractional.txt')], sandbox)
            else:
                capability['acl'] = 'unavailable: setfacl not installed; no portable ACL claim'
        for p in sorted(inputs.rglob('*'), reverse=True):
            os.utime(p, ns=(STAMP - 123456789, STAMP))
        result['capability_setup'] = capability
        result['inputs'] = inventory(inputs)
        for fmt in ('7z', 'zip', 'tar'):
            for zone in ('UTC0', 'EST5EDT'):
                case = sandbox / f'{fmt}-{zone}'
                case.mkdir()
                archive = case / f'metadata.{fmt}'
                opts = ['-mtc=off', '-mta=off'] if fmt != 'tar' else []
                c = dict(format=fmt, zone=zone)
                c['create'] = command([plain, 'a', f'-t{fmt}', '-mx=0', '-mmt=off', *opts, archive, '.'], inputs, {'TZ': zone})
                assert c['create']['exit'] == 0, c
                c['archive_sha256'] = digest(archive)
                c['properties'] = probe(tested, archive, fmt, case)
                c['list_plain'] = command([plain, 'l', '-slt', archive.name], case, {'TZ': zone})
                c['list_probe'] = command([tested, 'l', '-slt', archive.name], case, {'TZ': zone})
                assert c['list_plain']['stdout_b64'] == c['list_probe']['stdout_b64']
                assert c['list_plain']['stderr_b64'] == c['list_probe']['stderr_b64']
                assert c['list_plain']['exit'] == c['list_probe']['exit'] == 0
                out = case / 'extracted'
                out.mkdir()
                c['extract'] = command([plain, 'x', '-y', '-aos', archive.name, f'-o{out}'], case, {'TZ': zone})
                c['outputs'] = inventory(out)
                result['cases'].append(c)
        # Explicit creation property switches, including archive-security opt-ins.
        for label, fmt, opts in [('times-on', '7z', ['-mtc=on', '-mta=on']),
                                  ('security-on', '7z', ['-sni', '-sns', '-mtc=off', '-mta=off']),
                                  ('acl-only', '7z', ['-sni', '-mtc=off', '-mta=off']),
                                  ('ads-only', '7z', ['-sns', '-mtc=off', '-mta=off']),
                                  ('invalid-property', 'zip', ['-mnot_a_property=1'])]:
            case = sandbox / label
            case.mkdir()
            archive = case / f'out.{fmt}'
            c = dict(label=label, format=fmt, create=command([plain, 'a', f'-t{fmt}', '-mx=0', '-mmt=off', *opts, archive, '.'], inputs))
            if archive.exists():
                c['archive_sha256'] = digest(archive)
                c['properties'] = probe(tested, archive, fmt, case)
                out = case / 'out'
                out.mkdir()
                c['extract'] = command([plain, 'x', '-y', '-aos', '-sni', '-sns', archive, f'-o{out}'], case)
                c['outputs'] = inventory(out)
                if os.name == 'nt':
                    c['security_after'] = command(['icacls', str(out)], case)
            result['probes'].append(c)
        # Bounded deterministic non-compressible enough payload; no user data.
        fault_input = sandbox / 'fault-input'
        fault_input.mkdir()
        payload = b''.join(hashlib.sha256(str(i).encode('ascii')).digest() for i in range(2048))
        (fault_input / 'payload.bin').write_bytes(payload)
        os.utime(fault_input / 'payload.bin', ns=(STAMP, STAMP))
        result['fault_input_sha256'] = digest(fault_input / 'payload.bin')
        for operation in ('create', 'update'):
            for mode in ('none', 'write-short', 'read-short', 'write-full', 'read-error', 'missing-input'):
                case = sandbox / f'{operation}-{mode}'
                case.mkdir()
                source = case / 'payload.bin'
                source.write_bytes(b'original\n' if operation == 'update' else payload)
                os.utime(source, ns=(STAMP, STAMP))
                archive = case / 'out.zip'
                c = dict(operation=operation, mode=mode)
                if operation == 'update':
                    c['seed'] = command([plain, 'a', '-tzip', '-mx=0', '-mtc=off', '-mta=off', archive.name, source.name], case)
                    assert c['seed']['exit'] == 0
                    c['before_sha256'] = digest(archive)
                    source.write_bytes(payload)
                    os.utime(source, ns=(STAMP + 10000000000, STAMP + 10000000000))
                env = {'B03_FAULT': mode} if mode not in ('none', 'missing-input') else {}
                c['run'] = command([tested, 'a' if operation == 'create' else 'u', '-tzip', '-mx=0', '-mmt=off', '-mtc=off', '-mta=off', archive.name, 'absent.bin' if mode == 'missing-input' else source.name], case, env)
                c['disposition'] = inventory(case)
                if archive.exists():
                    c['after_sha256'] = digest(archive)
                    c['test_after'] = command([plain, 't', archive.name], case)
                result['faults'].append(c)
        # Real kernel ENOSPC without filling the host volume (Linux /dev/full).
        if platform.system() == 'Linux':
            full_argv = [str(plain), 'x', '-so', str(sandbox / 'create-none/out.zip')]
            with open('/dev/full', 'wb', buffering=0) as full:
                r = subprocess.run(full_argv, cwd=fault_input,
                                   stdout=full, stderr=subprocess.PIPE, timeout=60)
            result['kernel_full'] = dict(argv=full_argv, exit=r.returncode, stderr_b64=base64.b64encode(r.stderr).decode(),
                                         target='/dev/full', layer='CStdOutFileStream / kernel ENOSPC')
        else:
            result['kernel_full'] = dict(status='not exercised', reason='No bounded full volume provisioned; write-full is explicit stream-boundary injection, not kernel evidence')
        bigdir = sandbox / 'large'
        bigdir.mkdir()
        small = bigdir / 'small-sparse.bin'
        result['sparse_roundtrip'] = dict(source=sparse(small, 16 << 20))
        small_arc = bigdir / 'sparse.7z'
        result['sparse_roundtrip']['create'] = command([plain, 'a', '-t7z', '-mx=1', '-mmt=off', '-mtc=off', '-mta=off', small_arc.name, small.name], bigdir)
        sparse_out = bigdir / 'sparse-out'
        sparse_out.mkdir()
        result['sparse_roundtrip']['extract'] = command([plain, 'x', '-aos', '-y', small_arc.name, f'-o{sparse_out}'], bigdir)
        result['sparse_roundtrip']['outputs'] = inventory(sparse_out)
        result['sparse_roundtrip']['source_sha256'] = digest(small)
        big = bigdir / 'big.bin'
        result['large']['source'] = sparse(big)
        result['large']['seek'] = probe(tested, big, 'io', bigdir)
        archive = bigdir / 'large.zip'
        result['large']['create'] = command([plain, 'a', '-tzip', '-mx=1', '-mmt=off', '-mtc=off', '-mta=off', archive.name, big.name], bigdir, timeout=600)
        assert result['large']['create']['exit'] == 0
        assert archive.stat().st_size < 64 << 20, 'Compressed archive bound exceeded'
        result['large']['archive_size'] = archive.stat().st_size
        result['large']['archive_sha256'] = digest(archive)
        result['large']['properties'] = probe(tested, archive, 'zip', bigdir)
        with zipfile.ZipFile(archive) as z:
            info = z.infolist()[0]
            result['large']['zip_central'] = dict(file_size=info.file_size, compress_size=info.compress_size, extract_version=info.extract_version, extra_hex=info.extra.hex(), crc=info.CRC)
        result['large']['source_sha256'] = digest(big)
        argv = [str(plain), 'x', '-so', archive.name]
        with tempfile.TemporaryFile() as err:
            child = subprocess.Popen(argv, cwd=bigdir, stdout=subprocess.PIPE, stderr=err)
            h = hashlib.sha256()
            count = 0
            while True:
                block = child.stdout.read(8 << 20)
                if not block:
                    break
                count += len(block)
                assert count <= BIG, 'Unexpected decompression expansion'
                h.update(block)
            code = child.wait(timeout=60)
            err.seek(0)
            result['large']['extract_stdout'] = dict(argv=argv, exit=code, bytes=count, sha256=h.hexdigest(), stderr_b64=base64.b64encode(err.read()).decode())
        assert code == 0 and count == BIG and h.hexdigest() == result['large']['source_sha256']
        result['limitations'] = ['One tested filesystem per runner, not all supported volumes.',
                                'Windows/macOS kernel-full volume not provisioned; injected stream error is labeled separately.',
                                'Raw CTime/ATime observations retained; volatile times excluded only from repeat comparator.',
                                'Large extraction streams to a hash, not a 4 GiB allocated output file; sparse allocation preservation is not asserted.',
                                'No GUI, desktop, network-volume, privilege escalation or portable ACL mapping claim.']
        result['completed'] = True
    finally:
        report.write_text(json.dumps(result, indent=2) + '\n')
        # Retain bounded sandbox for forensic inspection; each run uses a fresh one.
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument('work', type=Path)
    p.add_argument('--report', required=True, type=Path)
    p.add_argument('--expect', type=Path)
    args = p.parse_args()
    assert not args.report.exists(), 'Refuse to overwrite an observation'
    result = capture(args.work.resolve(), args.report.resolve())
    if args.expect:
        from validate import compare, negative_controls
        expected = json.loads(args.expect.read_text())
        compare(expected, result)
        negative_controls(expected)
    from validate import validate
    validate(result)
    print(f'PASS {result["platform"]}: {args.report}')


if __name__ == '__main__':
    main()
