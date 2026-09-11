#!/usr/bin/env python3
"""Deterministic authored inputs, NOT invented expected engine outputs."""
import struct
import zlib


def zip_bytes(entries):
    local = bytearray()
    central = bytearray()
    for index, (name, flags, extra) in enumerate(entries):
        data = f'entry-{index}\n'.encode('ascii')
        crc = zlib.crc32(data)
        offset = len(local)
        local += struct.pack('<IHHHHHIIIHH', 0x04034b50, 20, flags, 0, 0, 0x21, crc, len(data), len(data), len(name), len(extra)) + name + extra + data
        central += struct.pack('<IHHHHHHIIIHHHHHII', 0x02014b50, 20, 20, flags, 0, 0, 0x21, crc, len(data), len(data), len(name), len(extra), 0, 0, 0, 0, offset) + name + extra
    return bytes(local + central + struct.pack('<IHHHHIIH', 0x06054b50, 0, 0, len(entries), len(entries), len(central), len(local), 0))


def unicode_extra(raw, text, valid=True, version=1):
    body = bytes([version]) + struct.pack('<I', zlib.crc32(raw) ^ (0 if valid else 1)) + text
    return struct.pack('<HH', 0x7075, len(body)) + body


def tar_bytes(name):
    assert len(name) <= 100
    header = bytearray(512)
    header[:len(name)] = name
    for start, length, value in ((100, 8, 0o644), (108, 8, 0), (116, 8, 0), (124, 12, 8), (136, 12, 0)):
        header[start:start+length] = f'{value:0{length-1}o}'.encode() + b'\0'
    header[148:156] = b'        '
    header[156] = ord('0')
    header[257:263] = b'ustar\0'
    header[263:265] = b'00'
    header[148:156] = f'{sum(header):06o}'.encode() + b'\0 '
    return bytes(header) + b'entry-0\n' + bytes(504 + 1024)


def corpus():
    result = {}
    for encoding, text in (('cp932', '日本語.txt'), ('cp936', '中文.txt'), ('utf-8', '日本中文😀.txt')):
        raw = text.encode(encoding)
        result[f'{encoding}-zip'] = ('zip', zip_bytes([(raw, 0, b'')]), True)
        result[f'{encoding}-tar'] = ('tar', tar_bytes(raw), True)
    raw = '日本語.txt'.encode('cp932')
    extra_text = 'extra-中文😀.txt'.encode()
    for label, flag, name, extra in (
        ('unicode-valid', 0, raw, unicode_extra(raw, extra_text)),
        ('unicode-bad-crc', 0, raw, unicode_extra(raw, extra_text, False)),
        ('unicode-bad-version', 0, raw, unicode_extra(raw, extra_text, version=2)),
        ('unicode-invalid-utf8', 0, raw, unicode_extra(raw, b'bad-\xff.txt')),
        ('efs-beats-extra', 0x800, 'efs-😀.txt'.encode(), unicode_extra('efs-😀.txt'.encode(), extra_text)),
        ('efs-invalid-utf8', 0x800, b'bad-\xff.txt', b''),
        ('efs-surrogate', 0x800, b'bad-\xed\xa0\x80.txt', b''),
        ('invalid-byte', 0, b'raw-\xff-\xfe.txt', b''),
        ('reserved', 0, b'CON.txt', b''),
        ('trailing-dot-space', 0, b'end. ', b''),
        ('long-component', 0, b'a' * 260 + b'.txt', b''),
        ('long-path', 0, (b'd' * 50 + b'/') * 6 + b'leaf.txt', b''),
        ('unc-syntax', 0, b'\\\\b02-invalid-host\\share\\leaf.txt', b''),
    ):
        result[label] = ('zip', zip_bytes([(name, flag, extra)]), label != 'unc-syntax')
    for label, names in (
        ('case-collision', ['Case.txt', 'case.txt']),
        ('normalization-collision', ['é.txt', 'e\u0301.txt']),
        ('duplicate-name', ['same.txt', 'same.txt']),
    ):
        result[label] = ('zip', zip_bytes([(name.encode(), 0x800, b'') for name in names]), True)
    return result
