#!/usr/bin/env python3
"""The language files this fork ships must be the official ones, plus our own.

7-Zip loads Lang\\<id>.txt from its own directory. The upstream source tree
carries none of those files - they only come with the official binary
release - so this fork vendors them under Lang/. Two things have to stay
true, and neither is visible by looking at a diff:

  1. Every file still parses the way CPP/Common/Lang.cpp parses it. A file
     that fails to parse is silently dropped: that language just disappears
     from Options -> Language.

  2. Below its trailing fork block, every file is byte for byte the official
     one. The fork's own strings live at ids 30000+ and are *appended*; an
     id inserted in the middle would shift every following string onto the
     wrong control, and the file would still parse.

The sha256 of each official file (with CR removed, so that a checkout with
core.autocrlf=true cannot break the check - Lang.cpp strips CR too) is in
.github/lang/MANIFEST.sha256, written by .github/scripts/lang_tool.py.

    python3 .github/tests/lang_files_test.py [repo root]
"""
import hashlib
import os
import re
import sys

LANG_DIR = "Lang"
MANIFEST = os.path.join(".github", "lang", "MANIFEST.sha256")
SOURCE_META = os.path.join(".github", "lang", "SOURCE.txt")
UPSTREAM_README = os.path.join("DOC", "readme.txt")

SIGNATURE = ";!@Lang2@!UTF-8!"
FORK_MARKER = "; --- 7-Zip-fork additions: https://github.com/r404r/7zip ---"
FORK_ID_MIN = 30000
FORK_ID_MAX = 39999

# where the ids above are #defined, used and given their English fallback, so
# that a translation and the code that reads it cannot drift apart
SOURCE_DIR = os.path.join("CPP", "7zip", "UI")
DEFINE_RE = re.compile(r"^\s*#define\s+(\w+)\s+(\d+)\s*$")

# LangString() falls back to the .rc string table when a language file has no
# such id, so these four need an entry there as well; the rest fall back to
# the text of their own control or menu item
NEEDS_STRING_TABLE = (30000, 30001, 30005, 30006)

# the languages this fork promises to ship; en.ttt is the English reference
# LangPage.cpp counts its entries against, not a language of its own
REQUIRED = ("en.ttt", "ja.txt", "zh-cn.txt", "zh-tw.txt")

# id -> the English text, which is also what .rc carries. Every file in
# REQUIRED must define all of them; no other file may define any of them.
FORK_STRINGS = (
    (30000, "Auto"),
    (30001, "Incorrect code page"),
    (30002, "Name code page:"),
    (30003, "Use UTF-8 for file names"),
    (30004, "Name Code Page..."),
    (30005, "Name Code Page"),
    (30006, "Read the names of this archive as:"),
)


class ParseError(Exception):
    pass


DIGITS_RE = re.compile(r"^[0-9]+$")


def unescape(line, n):
    """The escapes Lang.cpp understands, and the one it rejects."""
    out = []
    i = 0
    while i < len(line):
        c = line[i]
        i += 1
        if c != "\\":
            out.append(c)
            continue
        if i == len(line):
            # in Lang.cpp the next character is the newline, and that case
            # makes OpenFromString give up on the whole file
            raise ParseError("line %d ends with a backslash" % n)
        d = line[i]
        i += 1
        if d == "n":
            out.append("\n")
        elif d == "t":
            out.append("\t")
        elif d == "\\":
            out.append("\\")
        else:
            out.append("\\")
            out.append(d)
    return "".join(out)


def parse(text):
    """id -> string, following CPP/Common/Lang.cpp::OpenFromString.

    CR is expected to be gone already (Lang.cpp strips it before parsing).
    """
    if text.startswith("﻿"):
        text = text[1:]
    lines = text.split("\n")
    if not lines or lines[0] != SIGNATURE:
        raise ParseError("first line is not %r but %r" % (SIGNATURE, lines[0][:40]))
    # the signature line ends with \n, so the body starts at the next line
    ids = {}
    cur = -1024
    for n, raw in enumerate(lines[1:], start=2):
        line = unescape(raw, n)
        if line.strip(" \t") == "":
            cur += 1
            continue
        if line.startswith(";"):
            cur += 1
            continue
        if DIGITS_RE.match(line):
            v = int(line)
            if v > (1 << 30):
                raise ParseError("line %d: id %d is out of range" % (n, v))
            if v < cur:
                raise ParseError("line %d: id %d goes back from %d" % (n, v, cur))
            cur = v
            continue
        if cur < 0:
            raise ParseError("line %d: a string before any id" % n)
        ids[cur] = line
        cur += 1
    return ids


def split_fork_block(text):
    """(official part, fork part). The fork part is '' when there is none."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line == FORK_MARKER:
            head = "\n".join(lines[:i])
            if head:
                head += "\n"
            return head, "\n".join(lines[i:])
    return text, ""


def sha256_of(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read(path):
    """The file with CR removed - and nothing else, byte order mark included,
    so that the hash below covers every byte the official file has."""
    with open(path, "rb") as fh:
        return fh.read().replace(b"\r", b"").decode("utf-8")


def load_manifest(root):
    path = os.path.join(root, MANIFEST)
    if not os.path.isfile(path):
        return None, "%s is missing" % MANIFEST
    entries = {}
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(None, 1)
            if len(parts) != 2 or len(parts[0]) != 64:
                return None, "%s line %d is not '<sha256>  <name>'" % (MANIFEST, n)
            entries[parts[1].strip()] = parts[0]
    if not entries:
        return None, "%s lists no file" % MANIFEST
    return entries, None


def load_versions(root):
    source_path = os.path.join(root, SOURCE_META)
    readme_path = os.path.join(root, UPSTREAM_README)
    try:
        with open(source_path, encoding="utf-8") as fh:
            source_text = fh.read()
        with open(readme_path, encoding="utf-8") as fh:
            readme_first = fh.readline().strip()
    except FileNotFoundError as e:
        return None, None, "%s is missing" % os.path.relpath(e.filename, root)
    source_match = re.search(r"^version:\s*(\S+)\s*$", source_text, re.M)
    readme_match = re.match(r"^7-Zip\s+(\d+\.\d+)\s+Sources$", readme_first)
    if not source_match:
        return None, None, "%s has no version field" % SOURCE_META
    if not readme_match:
        return None, None, "%s has an unexpected first line: %r" % (
            UPSTREAM_README, readme_first)
    return source_match.group(1), readme_match.group(1), None


def walk_sources(root, suffix):
    for dirpath, _dirs, names in os.walk(os.path.join(root, SOURCE_DIR)):
        for name in sorted(names):
            if name.endswith(suffix):
                path = os.path.join(dirpath, name)
                with open(path, encoding="utf-8", errors="replace") as fh:
                    yield os.path.relpath(path, root), fh.read()


def scan_defines(root):
    """id -> [(symbol, path)] for every #define under CPP/7zip/UI."""
    found = {}
    for rel, text in walk_sources(root, ".h"):
        for line in text.split("\n"):
            m = DEFINE_RE.match(line)
            if m:
                found.setdefault(int(m.group(2)), []).append((m.group(1), rel))
    return found


def users_of(root, symbol, suffix):
    """The files of that kind that mention the symbol (not as part of a longer one)."""
    pattern = re.compile(r"(?<![0-9A-Za-z_])%s(?![0-9A-Za-z_])" % re.escape(symbol))
    return [rel for rel, text in walk_sources(root, suffix) if pattern.search(text)]


def main(root):
    fails = []

    def fail(msg):
        fails.append(msg)
        print("  FAIL %s" % msg)

    source_version, upstream_version, version_error = load_versions(root)
    if version_error:
        fail(version_error)
    elif source_version != upstream_version:
        fail("%s version %s does not match %s version %s" % (
            SOURCE_META, source_version, UPSTREAM_README, upstream_version))

    lang_dir = os.path.join(root, LANG_DIR)
    if not os.path.isdir(lang_dir):
        print("ERROR: %s/ is missing - the fork ships no language files" % LANG_DIR)
        return 1

    names = sorted(n for n in os.listdir(lang_dir)
                   if os.path.isfile(os.path.join(lang_dir, n)))
    if not names:
        print("ERROR: %s/ is empty" % LANG_DIR)
        return 1

    for want in REQUIRED:
        if want not in names:
            fail("%s/%s is missing" % (LANG_DIR, want))

    # anything that is not a language file must not end in .txt: LangPage.cpp
    # tries to open every .txt in the directory and complains about the ones
    # that do not parse
    manifest, err = load_manifest(root)
    if err:
        print("ERROR: " + err)
        return 1

    for extra in sorted(set(manifest) - set(names)):
        fail("%s is in the manifest but not in %s/" % (extra, LANG_DIR))

    fork_ids = dict(FORK_STRINGS)
    checked = 0

    for name in names:
        path = os.path.join(lang_dir, name)
        text = read(path)
        official, fork = split_fork_block(text)

        try:
            ids = parse(text)
        except ParseError as e:
            fail("%s does not parse: %s" % (name, e))
            continue

        checked += 1

        if ids.get(0) != "7-Zip":
            fail("%s: id 0 is %r, not '7-Zip' - Lang.cpp rejects the file"
                 % (name, ids.get(0)))

        if name not in manifest:
            fail("%s is not in the manifest" % name)
        elif sha256_of(official) != manifest[name]:
            fail("%s differs from the official file above its fork block" % name)

        if fork:
            # the block is at the end by construction of split_fork_block;
            # what has to be checked is that it only adds reserved ids
            try:
                block_ids = set(parse(SIGNATURE + "\n" + fork))
            except ParseError as e:
                fail("%s: the fork block does not parse: %s" % (name, e))
                block_ids = set()
            low = sorted(i for i in block_ids if i < FORK_ID_MIN)
            if low:
                fail("%s: the fork block defines id(s) %s below %d"
                     % (name, low, FORK_ID_MIN))

        present = {i for i in fork_ids if i in ids}
        if name in REQUIRED:
            for i, en in FORK_STRINGS:
                if i not in ids:
                    fail("%s does not define the fork string %d (%r)" % (name, i, en))
                elif not ids[i].strip():
                    fail("%s defines the fork string %d as empty" % (name, i))
        elif present:
            fail("%s defines fork string(s) %s - only %s carry them"
                 % (name, sorted(present), ", ".join(REQUIRED)))

    if checked == 0:
        print("ERROR: nothing was checked")
        return 1

    # A string in the language files that nothing reads is dead weight; an id
    # in the code that no language file translates shows up as English in an
    # otherwise translated dialog. Neither is visible from either side alone,
    # so tie the two together: every fork id must have a name, that name must
    # be used by the code, and the ones read through LangString() must have
    # their English in the string table as well.
    defines = scan_defines(root)
    for i, en in FORK_STRINGS:
        if i not in defines:
            fail("no #define under %s gives %d (%r) a name" % (SOURCE_DIR, i, en))
            continue
        symbols = {sym for sym, _rel in defines[i]}
        if len(symbols) > 1:
            fail("%d is #defined as %s" % (i, " and ".join(sorted(symbols))))
            continue
        symbol = defines[i][0][0]
        code = users_of(root, symbol, ".cpp")
        if not code:
            fail("nothing under %s uses %s (%d, %r)" % (SOURCE_DIR, symbol, i, en))
        rc = users_of(root, symbol, ".rc") if i in NEEDS_STRING_TABLE else []
        if i in NEEDS_STRING_TABLE and not rc:
            fail("%s (%d) is read with LangString but has no .rc string: a"
                 " language without a translation would show nothing" % (symbol, i))
        print("  %d %-30s %s" % (i, symbol, ", ".join(code + rc) or "-"))
    for i in sorted(defines):
        if FORK_ID_MIN <= i <= FORK_ID_MAX and i not in fork_ids:
            fail("%s is %d, in the fork's range, but no language file translates it"
                 % (defines[i][0][0], i))

    print("%d language files checked, %d problem(s)" % (checked, len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
