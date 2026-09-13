#!/usr/bin/env python3
"""B05-MAN fixture generator.

Creates the small set of PUBLIC, SYNTHETIC archives and inputs the manual
runbook drives the retained 7zz console binary against. Every password used
here is invented test data, never a real credential. Deterministic: running
this twice produces byte-identical inputs (archive contents are timestamped
by 7-Zip itself, so archive bytes are NOT expected to be identical run to
run -- only the plaintext inputs are).

Usage:
    python3 fixtures.py <work_dir>

Writes <work_dir>/src/*.txt (plaintext inputs) only. It does NOT invoke 7zz;
archive creation is done by the runbook's own steps so the human sees the
real CryptoGetTextPassword2 callback path exercised, not a pre-baked archive.
"""
import os
import sys

# Public synthetic passwords. None of these is a real credential of any
# person, account or system. Picked to be obviously fake and grep-able.
SYNTH_PASSWORDS = {
    "correct": "B05Synth-Correct-9f2a",
    "wrong": "B05Synth-WRONG-1234",
    "nonascii": "B05Synth-\u6ce8\u91cd-\u00e9\u00e8\u00fc-\u30c6\u30b9\u30c8",  # CJK + accented Latin + Katakana
}


def write(path, content_bytes):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(content_bytes)


def main():
    if len(sys.argv) != 2:
        print("usage: fixtures.py <work_dir>", file=sys.stderr)
        return 2
    work = sys.argv[1]
    src = os.path.join(work, "src")

    write(os.path.join(src, "item1.txt"),
          b"B05-MAN synthetic content item1 - not a secret.\n")
    write(os.path.join(src, "item2.txt"),
          b"B05-MAN synthetic content item2 - not a secret.\n")
    # Non-ASCII *filename* fixture for the legacy ZIP non-ASCII rejection
    # check (Section 6). This is about the ARCHIVE ENTRY NAME, not the
    # password -- kept in a separate directory so the archiving step in the
    # runbook can pick it deliberately.
    nonascii_dir = os.path.join(src, "nonascii-name")
    os.makedirs(nonascii_dir, exist_ok=True)
    write(os.path.join(nonascii_dir, "\u6587\u4ef6\u540d-\u30c6\u30b9\u30c8.txt"),
          b"B05-MAN synthetic content with a non-ASCII entry name.\n")

    print("fixtures written under:", src)
    print("synthetic passwords (public, synthetic, never real):")
    for k, v in SYNTH_PASSWORDS.items():
        print(f"  {k}: {v!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
