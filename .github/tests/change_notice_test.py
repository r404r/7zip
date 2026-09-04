#!/usr/bin/env python3
"""Every upstream file this fork modifies must say so in the file itself.

The LGPL (2.1, section 2b) wants the modified files to carry prominent
notices of the change and its date. The git history does not travel with
the source archives of a release, so the notice has to be in the file,
at the top, in exactly this shape for C/C++-style files:

    // Modified in 7-Zip-fork, <year>: https://github.com/r404r/7zip

Files whose syntax does not support // comments use their native comment
form, such as # or an XML comment.

Checked for every file that exists in main (the upstream mirror) and
differs from it, renames included. Files the fork adds are its own work
and need no notice; a deleted file has nowhere to carry one.

    python3 .github/tests/change_notice_test.py [repo root]
"""
import os
import re
import subprocess
import sys

# anchored: the marker alone, somewhere in a string, is not a notice
NOTICE_TEXT = r"Modified in 7-Zip-fork, \d{4}: https://github\.com/r404r/7zip"
SLASH_NOTICE_RE = re.compile(r"^// " + NOTICE_TEXT + r"$")
HASH_NOTICE_RE = re.compile(r"^# " + NOTICE_TEXT + r"$")
SEMI_NOTICE_RE = re.compile(r"^; " + NOTICE_TEXT + r"$")
XML_NOTICE_RE = re.compile(r"^<!-- " + NOTICE_TEXT + r" -->$")
NOTICE_TOP_LINES = 5

# rewritten as the fork's own statement; its first paragraph says what it is
SKIP = {"README.md"}


def git(root, *args):
    return subprocess.run(["git", "-C", root] + list(args),
                          capture_output=True, text=True)


def die(msg):
    print("ERROR: " + msg)
    sys.exit(2)


def notice_re_for_path(path):
    name = os.path.basename(path)
    suffix = os.path.splitext(name)[1].lower()
    if (name == ".gitattributes" or name.startswith("makefile")
            or suffix in (".dsp", ".dsw", ".mak", ".py", ".sh", ".yaml", ".yml")):
        return HASH_NOTICE_RE
    if suffix == ".asm":
        return SEMI_NOTICE_RE
    if suffix in (".props", ".vcxproj", ".wxs", ".xml"):
        return XML_NOTICE_RE
    return SLASH_NOTICE_RE


def has_notice(root, path):
    notice_re = notice_re_for_path(path)
    try:
        with open(os.path.join(root, path), encoding="utf-8", errors="replace") as fh:
            for i, line in enumerate(fh):
                if i >= NOTICE_TOP_LINES:
                    break
                text = line.rstrip("\r\n")
                if notice_re.match(text):
                    return True
    except FileNotFoundError:
        pass
    return False


def main(root):
    if git(root, "rev-parse", "--verify", "origin/main").returncode != 0:
        r = git(root, "fetch", "--no-tags", "origin", "main:refs/remotes/origin/main")
        if r.returncode != 0:
            die("cannot get origin/main:\n" + r.stderr)
    base = "origin/main"

    # a shallow checkout (the default on CI) has no merge base with main:
    # the diff below would fail. Deepen until there is one.
    if git(root, "merge-base", base, "HEAD").returncode != 0:
        print("  (shallow history, fetching the rest)")
        r = git(root, "fetch", "--unshallow", "--no-tags", "origin")
        if git(root, "merge-base", base, "HEAD").returncode != 0:
            die("no merge base with %s even after fetch --unshallow:\n%s" % (base, r.stderr))

    r = git(root, "diff", "--name-status", "-z", "-M", base + "...HEAD")
    if r.returncode != 0:
        die("git diff failed:\n" + r.stderr)
    fields = r.stdout.split("\0")

    failed = checked = 0
    i = 0
    while i < len(fields) and fields[i]:
        status, path = fields[i], fields[i + 1]
        i += 2
        if status.startswith(("R", "C")):  # old path, then the one to check
            path = fields[i]
            i += 1
        if path in SKIP:
            print("  SKIP %s (the fork's own statement)" % path)
            continue
        if status.startswith("D"):
            continue  # nowhere to carry a notice
        if status.startswith("A"):
            continue  # the fork's own file
        # M, T, or the new side of R/C: an upstream file carrying our changes
        checked += 1
        ok = has_notice(root, path)
        if not ok:
            failed += 1
        print("  %-4s %s" % ("PASS" if ok else "FAIL", path))

    if checked == 0:
        # dev-main and pr/* always differ from main in upstream files;
        # zero means the comparison itself broke
        die("nothing was checked - that cannot be right on this branch")
    print("%d modified upstream files, %d without a notice" % (checked, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
