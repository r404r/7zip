#!/usr/bin/env python3
"""Bounded native full-volume observations; never fill a host filesystem.

Only newly created 64 MiB disk images are mount/format targets. No physical disk
number, existing image, global policy change or privilege escalation is used.
An unavailable image facility is a qualification failure, not ENOSPC evidence.
"""
import base64
from contextlib import contextmanager
import errno
import os
from pathlib import Path
import platform
import shutil
from typing import Any

LIMIT = 64 << 20


def fill_tail(write, tell, record):
    """Bounded coarse-to-fine writes, not evidence of an archive-layer error."""
    record['fill_steps'] = []
    attempted = 0
    for chunk in (1 << 20, 64 << 10, 4096):
        step: dict[str, Any] = dict(chunk=chunk, writes=0)
        record['fill_steps'].append(step)
        while True:
            attempted += chunk
            assert attempted <= LIMIT + (2 << 20), 'Image fill exceeded write budget'
            try:
                n = write(b'F' * chunk)
                assert n is not None and 0 < n <= chunk, 'Invalid filler short write'
                step['writes'] += 1
                assert tell() <= LIMIT, 'Filler exceeded image size'
            except OSError as exc:
                error = dict(errno=exc.errno, winerror=getattr(exc, 'winerror', None))
                step['error'] = error
                assert exc.errno == errno.ENOSPC or error['winerror'] == 112
                record['fill_error'] = error
                break
    record['filled_size'] = tell()


def check_mount(root, parent, info, parent_info):
    assert not root.is_symlink(), 'Refuse symbolic-link mount target'
    usage = shutil.disk_usage(root)
    assert 1 << 20 < usage.total <= LIMIT, 'Refuse to fill a host-sized filesystem'
    if os.name == 'nt':
        assert Path(info['volume']) == root, 'VHD not mounted at owned directory'
        assert info['volume'] != parent_info['volume'], 'VHD mount is on host volume'
    else:
        assert root.stat().st_dev != parent.stat().st_dev, 'Image not mounted: host device'
        assert Path(info['mount_point']) == root
    return dict(total=usage.total, free=usage.free)


@contextmanager
def mounted(case, result, command, fs_info):
    root = case / 'mounted'
    root.mkdir()
    assert shutil.disk_usage(case).free > LIMIT + (512 << 20)
    parent_info = fs_info(case)
    result['parent_filesystem'] = parent_info
    result['setup'] = []
    system = platform.system()
    image = case / ('bounded.vhd' if os.name == 'nt' else 'bounded.dmg')
    assert not image.exists()
    assert not any(c in str(case) for c in '\r\n"'), 'Unsafe native command path'

    def diskpart(label, lines):
        script = case / (label + '.txt')
        script.write_text('\n'.join(lines) + '\n', encoding='ascii')
        raw = command(['diskpart', '/s', str(script)], case)
        raw['script'] = lines
        return raw

    try:
        if os.name == 'nt':
            # create vdisk focuses only the new image; select it explicitly again.
            # No select disk/clean command can address a host physical disk.
            raw = diskpart('mount', [f'create vdisk file="{image}" maximum=64 type=fixed',
                                    f'select vdisk file="{image}"', 'attach vdisk',
                                    'create partition primary', 'format fs=ntfs quick label=B03FULL',
                                    f'assign mount="{root}"'])
            result['setup'].append(raw)
            assert raw['exit'] == 0, raw
        elif system == 'Darwin':
            for argv in (['hdiutil', 'create', '-size', '64m', '-fs', 'HFS+', '-volname', 'B03FULL', str(image)],
                         ['hdiutil', 'attach', '-nobrowse', '-mountpoint', str(root), str(image)]):
                raw = command(argv, case)
                result['setup'].append(raw)
                assert raw['exit'] == 0, raw
        else:
            raise AssertionError('Image full-volume helper is Windows/macOS only')
        result['filesystem'] = fs_info(root)
        result['capacity'] = check_mount(root, case, result['filesystem'], parent_info)
        yield root
    finally:
        # Exact image/mount only; no forced detach and no unmounting other volumes.
        if os.name == 'nt' and image.exists():
            result['cleanup'] = diskpart('detach', [f'select vdisk file="{image}"', 'detach vdisk'])
        elif system == 'Darwin' and root.stat().st_dev != case.stat().st_dev:
            result['cleanup'] = command(['hdiutil', 'detach', str(root)], case)
        if 'cleanup' in result:
            assert result['cleanup']['exit'] == 0, result['cleanup']
            # diskpart may return zero even when a script command failed.
            result['detached'] = (root.stat().st_dev == case.stat().st_dev if os.name != 'nt'
                                  else fs_info(root)['volume'] == parent_info['volume'])
            assert result['detached'], 'Image still mounted after detach'


def observe(plain, sandbox, result, command, fs_info, digest):
    """Exercise retained create/update after measuring less than input capacity."""
    result['layer'] = 'COutFileStream / bounded image filesystem'
    result['operations'] = []
    result['completed'] = False
    source = sandbox / 'fault-input/payload.bin'
    for operation in ('create', 'update'):
        case = sandbox / ('kernel-full-' + operation)
        case.mkdir()
        record: dict[str, Any] = dict(operation=operation)
        result['operations'].append(record)
        with mounted(case, record, command, fs_info) as root:
            archive = root / 'out.zip'
            if operation == 'update':
                shutil.copyfile(sandbox / 'update-write-full/out.zip', archive)
                record['before_sha256'] = digest(archive)
            # Prove writes work before exhaustion (reject read-only/launch errors).
            control = root / 'control.zip'
            record['control'] = command([plain, 'a', '-tzip', '-mx=0', control, source], sandbox)
            assert record['control']['exit'] == 0
            record['control_test'] = command([plain, 't', control], sandbox)
            assert record['control_test']['exit'] == 0
            control.unlink()
            filler = root / 'filler.bin'
            with filler.open('xb', buffering=0) as f:
                fill_tail(f.write, f.tell, record)
                assert 16 << 10 < f.tell() <= LIMIT
                f.truncate(f.tell() - (16 << 10))
            # Recheck the owned mount immediately before the error-path operation.
            record['capacity_before_archive'] = check_mount(root, case, fs_info(root), record['parent_filesystem'])
            record['free_before_archive'] = shutil.disk_usage(root).free
            assert record['free_before_archive'] < source.stat().st_size
            record['run'] = command([plain, 'a' if operation == 'create' else 'u', '-tzip', '-mx=0',
                                     '-mmt=off', '-mtc=off', '-mta=off', archive, source], sandbox)
            # Save disposition before any filler cleanup. Temp archives are bounded.
            record['disposition'] = [dict(name=p.name, size=p.stat().st_size, sha256=digest(p))
                                     for p in sorted(root.iterdir()) if p.is_file() and p != filler]
            retained = case / 'retained'
            retained.mkdir()
            for item in record['disposition']:
                assert item['size'] < 1 << 20, 'Full-volume output exceeded fixture bound'
                shutil.copyfile(root / item['name'], retained / item['name'])
            if archive.exists():
                record['after_sha256'] = digest(archive)
                record['test_after'] = command([plain, 't', archive], sandbox)
            assert record['run']['exit'] != 0
            message = base64.b64decode(record['run']['stderr_b64'])
            assert b'No space left on device' in message or b'There is not enough space on the disk' in message, message
            filler.unlink()
    result['completed'] = True
