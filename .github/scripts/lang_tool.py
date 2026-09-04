#!/usr/bin/env python3
"""Maintain the vendored Lang/ directory.

The upstream source tree has no language files; they ship only with the
official binary release. This fork vendors them so that the build is
reproducible and so that a new upstream release shows up as a readable diff.

    fetch     download the official installer, verify nothing else, unpack Lang/
    apply     append the fork's own strings (ids 30000+) to the files we translate
    manifest  record the sha256 of every file below its fork block
    refresh   fetch + apply + manifest, what to run after an upstream merge

    python3 .github/scripts/lang_tool.py refresh --version <upstream-version>

fetch needs a 7-Zip binary to unpack the installer (--seven, $SEVENZIP, 7zz
or 7z on PATH, or the one this tree builds). Nothing else here needs one, and
CI runs none of it: it only checks the result with
.github/tests/lang_files_test.py.
"""
import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LANG_DIR = os.path.join(ROOT, "Lang")
LANG_META = os.path.join(ROOT, ".github", "lang")
MANIFEST = os.path.join(LANG_META, "MANIFEST.sha256")
SOURCE = os.path.join(LANG_META, "SOURCE.txt")

URL = "https://www.7-zip.org/a/7z%s-x64.exe"

FORK_MARKER = "; --- 7-Zip-fork additions: https://github.com/r404r/7zip ---"
FORK_NOTE = "; ids 30000+ are the fork's own; always appended, never inserted"
FORK_ID_FIRST = 30000

# One entry per fork string, in id order starting at FORK_ID_FIRST, so the
# block needs a single id marker. "en" is what the .rc carries and what a
# language without a translation falls back to.
#
# Not translated on purpose: the code page names in
# CPP/7zip/UI/Common/NameCodePageProps.h and the literal "Auto" it parses
# back, and the "7-Zip-fork" menu caption, which is a name.
STRINGS = [
    # (id, en, ja, zh-cn, zh-tw)
    (30000, "Auto",
     "自動", "自动", "自動"),
    (30001, "Incorrect code page",
     "文字コードが正しくありません", "代码页无效", "字碼頁無效"),
    (30002, "Name code page:",
     "ファイル名の文字コード:", "文件名代码页：", "檔名字碼頁:"),
    (30003, "Use UTF-8 for file names",
     "ファイル名に UTF-8 を使う", "文件名使用 UTF-8", "檔名使用 UTF-8"),
    (30004, "Name Code Page...",
     "ファイル名の文字コード...", "文件名代码页...", "檔名字碼頁..."),
    (30005, "Name Code Page",
     "ファイル名の文字コード", "文件名代码页", "檔名字碼頁"),
    (30006, "Read the names of this archive as:",
     "このアーカイブのファイル名を次の文字コードとして読む:",
     "将此压缩包的文件名按以下代码页读取：",
     "將此壓縮檔的檔名以下列字碼頁讀取:"),
]

COLUMN = {"en.ttt": 1, "ja.txt": 2, "zh-cn.txt": 3, "zh-tw.txt": 4}


def die(msg):
    sys.stderr.write("error: %s\n" % msg)
    sys.exit(2)


def read(path):
    with open(path, "rb") as fh:
        return fh.read()


def split_fork_block(text):
    """(official part, fork part) of a file already decoded and CR-free."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line == FORK_MARKER:
            head = "\n".join(lines[:i])
            if head:
                head += "\n"
            return head, "\n".join(lines[i:])
    return text, ""


def decode(raw):
    """The bytes with CR removed - and nothing else. The byte order mark most
    of these files start with stays: the manifest is meant to cover it."""
    return raw.replace(b"\r", b"").decode("utf-8")


def lang_files():
    if not os.path.isdir(LANG_DIR):
        die("%s does not exist - run 'fetch' first" % LANG_DIR)
    return sorted(n for n in os.listdir(LANG_DIR)
                  if os.path.isfile(os.path.join(LANG_DIR, n)))


def find_7z(explicit):
    candidates = []
    if explicit:
        candidates.append(explicit)
    if os.environ.get("SEVENZIP"):
        candidates.append(os.environ["SEVENZIP"])
    for name in ("7zz", "7z", "7za"):
        found = shutil.which(name)
        if found:
            candidates.append(found)
    candidates += [
        os.path.join(ROOT, "CPP", "7zip", "Bundles", "Alone2", "_o", "7zz"),
        os.path.join(ROOT, "CPP", "7zip", "Bundles", "Alone2", "x64", "7zz.exe"),
    ]
    for c in candidates:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    die("no 7-Zip binary found to unpack the installer; pass --seven <path>")


def cmd_fetch(args):
    url = args.url or (URL % args.version.replace(".", ""))
    seven = find_7z(args.seven)
    tmp = tempfile.mkdtemp(prefix="lang-")
    try:
        installer = os.path.join(tmp, os.path.basename(url))
        print("downloading %s" % url)
        with urllib.request.urlopen(url) as resp, open(installer, "wb") as out:
            shutil.copyfileobj(resp, out)
        raw = read(installer)
        digest = hashlib.sha256(raw).hexdigest()
        print("%s  %s (%d bytes)" % (digest, os.path.basename(url), len(raw)))
        if args.sha256 and args.sha256 != digest:
            die("sha256 is %s, expected %s" % (digest, args.sha256))

        out_dir = os.path.join(tmp, "x")
        r = subprocess.run([seven, "x", "-y", "-o" + out_dir, installer, "Lang/*"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            die("%s could not unpack the installer:\n%s%s" % (seven, r.stdout, r.stderr))
        src = os.path.join(out_dir, "Lang")
        names = sorted(os.listdir(src))
        if not names:
            die("the installer has no Lang/ directory")

        if os.path.isdir(LANG_DIR):
            shutil.rmtree(LANG_DIR)
        shutil.copytree(src, LANG_DIR)
        print("unpacked %d files into Lang/" % len(names))

        os.makedirs(LANG_META, exist_ok=True)
        with open(SOURCE, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("The files in Lang/ come from the official 7-Zip release.\n\n")
            fh.write("version:   %s\n" % args.version)
            fh.write("url:       %s\n" % url)
            fh.write("sha256:    %s\n" % digest)
            fh.write("size:      %d bytes\n" % len(raw))
            fh.write("extracted: %d files\n" % len(names))
            fh.write("\nRe-create with:\n")
            fh.write("    python3 .github/scripts/lang_tool.py refresh --version %s\n"
                     % args.version)
        print("wrote %s" % os.path.relpath(SOURCE, ROOT))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0


def cmd_apply(_args):
    for name in lang_files():
        col = COLUMN.get(name)
        if col is None:
            continue
        path = os.path.join(LANG_DIR, name)
        raw = read(path)
        crlf = b"\r\n" in raw
        official, _ = split_fork_block(decode(raw))
        if not official.endswith("\n"):
            official += "\n"

        block = [FORK_MARKER, FORK_NOTE, str(FORK_ID_FIRST)]
        for i, row in enumerate(STRINGS):
            expected = FORK_ID_FIRST + i
            if row[0] != expected:
                die("STRINGS is not a run from %d: %d where %d belongs"
                    % (FORK_ID_FIRST, row[0], expected))
            block.append(row[col])
        text = official + "\n".join(block) + "\n"

        data = text.encode("utf-8")  # the byte order mark, if any, came along
        if crlf:
            data = data.replace(b"\n", b"\r\n")
        with open(path, "wb") as fh:
            fh.write(data)
        print("  %-10s + %d fork strings" % (name, len(STRINGS)))
    return 0


def cmd_manifest(_args):
    lines = [
        "# sha256 of every Lang/ file as it comes from the official release:",
        "# the bytes above its fork block, byte order mark included, with CR",
        "# removed (Lang.cpp strips CR too, so a checkout that rewrites line",
        "# endings cannot break this).",
        "# Written by .github/scripts/lang_tool.py, checked by",
        "# .github/tests/lang_files_test.py.",
    ]
    for name in lang_files():
        official, _ = split_fork_block(decode(read(os.path.join(LANG_DIR, name))))
        lines.append("%s  %s" % (hashlib.sha256(official.encode("utf-8")).hexdigest(),
                                 name))
    os.makedirs(LANG_META, exist_ok=True)
    with open(MANIFEST, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print("wrote %s (%d files)" % (os.path.relpath(MANIFEST, ROOT),
                                   len(lines) - 6))
    return 0


def cmd_refresh(args):
    return cmd_fetch(args) or cmd_apply(args) or cmd_manifest(args)


def main(argv):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    def with_fetch_args(sp):
        sp.add_argument("--version", required=True,
                        help="upstream version, as in DOC/readme.txt")
        sp.add_argument("--url", help="override the installer URL")
        sp.add_argument("--sha256", help="expected sha256 of the installer")
        sp.add_argument("--seven", help="path to a 7-Zip binary")

    with_fetch_args(sub.add_parser("fetch"))
    sub.add_parser("apply")
    sub.add_parser("manifest")
    with_fetch_args(sub.add_parser("refresh"))

    args = p.parse_args(argv)
    return {"fetch": cmd_fetch, "apply": cmd_apply,
            "manifest": cmd_manifest, "refresh": cmd_refresh}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
