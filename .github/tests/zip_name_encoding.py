#!/usr/bin/env python3
"""Check how zip file names are encoded by this build of 7-Zip.

    python3 .github/tests/zip_name_encoding.py <path to 7zz>

A zip can describe its file name encoding in two ways:

  bit 11 (EFS)   the name field itself is UTF-8. It is defined by the ZIP
                 specification, so any conforming reader understands it.
  extra 0x7075   an additional UTF-8 copy of the name. It is an Info-ZIP
                 extension, so fewer readers understand it.

Both are honored by 7-Zip itself, but bit 11 is the portable one, and it is
what an archive that travels between systems of different languages needs.

The interesting case is a name that CAN be represented in the local code page
of the machine that creates the archive - a Chinese name on a Chinese Windows,
say. Then 7-Zip writes the local bytes and does not set bit 11. "-mcp=936"
reproduces that on any machine, because it sets the code page that is used
instead of the local one.

The checks run only on Windows: the conversion to a code page is a no-op on
other systems, so there is nothing to check there. Elsewhere the script only
prints what it sees.
"""
import os
import struct
import subprocess
import sys
import tempfile

NAME = "中文文件名.txt"          # 中文文件名.txt
EOCD_SIG = b"\x50\x4b\x05\x06"
CD_SIG = 0x02014B50
ID_UNICODE_PATH = 0x7075
FLAG_UTF8 = 0x800


def read_central_dir(path):
    """Return (flags, raw name bytes, extra field ids) of the first entry."""
    with open(path, "rb") as f:
        buf = f.read()
    end = buf.rfind(EOCD_SIG)
    if end < 0:
        raise ValueError("%s: no end of central directory" % path)
    cd_offset = struct.unpack_from("<I", buf, end + 16)[0]
    if struct.unpack_from("<I", buf, cd_offset)[0] != CD_SIG:
        raise ValueError("%s: no central directory at %d" % (path, cd_offset))
    flags = struct.unpack_from("<H", buf, cd_offset + 8)[0]
    n_len, e_len = struct.unpack_from("<HH", buf, cd_offset + 28)
    name = buf[cd_offset + 46: cd_offset + 46 + n_len]
    extra = buf[cd_offset + 46 + n_len: cd_offset + 46 + n_len + e_len]
    ids, pos = [], 0
    while pos + 4 <= len(extra):
        eid, size = struct.unpack_from("<HH", extra, pos)
        ids.append(eid)
        pos += 4 + size
    return flags, name, ids


def encoding_of(raw):
    """Name the encoding of the raw name bytes, as far as it can be told."""
    if all(b < 0x80 for b in raw):
        return "ascii"
    try:
        raw.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        pass
    try:
        if raw.decode("gbk") == NAME:
            return "cp936"
    except UnicodeDecodeError:
        pass
    return "other"


# (label, extra 7zz arguments, expected bit 11, expected encoding, expected 0x7075)
# None means: only report, do not check.
CASES_WIN = [
    ("default",            [],                       None,  None,     None),
    ("cp=936",             ["-mcp=936"],             False, "cp936",  True),
    ("cp=936 + cu=on",     ["-mcp=936", "-mcu=on"],  True,  "utf-8",  False),
    ("cu=on",              ["-mcu=on"],              True,  "utf-8",  False),
]
CASES_OTHER = [(c[0], c[1], None, None, None) for c in CASES_WIN]


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    exe = os.path.abspath(argv[1])
    on_windows = sys.platform == "win32"
    cases = CASES_WIN if on_windows else CASES_OTHER
    if not on_windows:
        print("not Windows: reporting only, nothing is checked\n")

    d = tempfile.mkdtemp(prefix="zipenc-")
    with open(os.path.join(d, NAME), "w") as f:
        f.write("x\n")

    print("  %-16s %-7s %-9s %-8s %s" % ("options", "bit 11", "encoding", "0x7075", "name bytes"))
    failures = []
    for label, args, want_flag, want_enc, want_extra in cases:
        out = os.path.join(d, "o.zip")
        if os.path.exists(out):
            os.remove(out)
        r = subprocess.run([exe, "a"] + args + [out, NAME], cwd=d,
                           capture_output=True, text=True)
        if r.returncode != 0:
            failures.append("%s: 7zz failed: %s" % (label, (r.stdout + r.stderr)[-300:]))
            print("  %-16s FAILED TO CREATE" % label)
            continue

        flags, raw, ids = read_central_dir(out)
        got_flag = bool(flags & FLAG_UTF8)
        got_enc = encoding_of(raw)
        got_extra = ID_UNICODE_PATH in ids
        print("  %-16s %-7s %-9s %-8s %s"
              % (label, int(got_flag), got_enc, "yes" if got_extra else "no", raw.hex()))

        for what, got, want in (("bit 11", got_flag, want_flag),
                                ("encoding", got_enc, want_enc),
                                ("0x7075", got_extra, want_extra)):
            if want is not None and got != want:
                failures.append("%s: %s is %r, expected %r" % (label, what, got, want))

    print()
    if failures:
        for f in failures:
            print("  FAIL: %s" % f)
        return 1
    print("  ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
