#!/usr/bin/env python3
"""Every upstream file this fork modifies must say so in the file itself.

The LGPL (2.1, section 2b) wants the modified files to carry prominent
notices of the change and its date. The git history does not travel with
the source archives of a release, so the notice has to be in the file:

    // Modified in 7-Zip-fork, <year>: https://github.com/r404r/7zip

Checked here for every file that exists in main (the upstream mirror) and
differs from it. Files the fork adds are its own work and need no notice.

    python3 .github/tests/change_notice_test.py [repo root]
"""
import os
import subprocess
import sys

MARKER = "Modified in 7-Zip-fork"

# rewritten as the fork's own statement; its first paragraph says what it is
SKIP = {"README.md"}


def git(root, *args):
    return subprocess.run(["git", "-C", root] + list(args),
                          capture_output=True, text=True)


def main(root):
    if git(root, "rev-parse", "--verify", "origin/main").returncode != 0:
        # a shallow checkout on CI has no main: fetch it
        r = git(root, "fetch", "--no-tags", "origin", "main:refs/remotes/origin/main")
        if r.returncode != 0:
            print("cannot get origin/main:\n" + r.stderr)
            return 2
    base = "origin/main"

    changed = git(root, "diff", "--name-only", base + "...HEAD").stdout.split()
    failed = 0
    checked = 0
    for f in changed:
        if f in SKIP:
            print("  SKIP %s (the fork's own statement)" % f)
            continue
        if git(root, "cat-file", "-e", "%s:%s" % (base, f)).returncode != 0:
            continue  # added by the fork, not a modified upstream file
        checked += 1
        try:
            with open(os.path.join(root, f), encoding="utf-8", errors="replace") as fh:
                ok = MARKER in fh.read()
        except FileNotFoundError:
            ok = False  # deleted upstream file: nowhere to carry a notice
        if not ok:
            failed += 1
        print("  %-4s %s" % ("PASS" if ok else "FAIL", f))
    print("%d modified upstream files, %d without a notice" % (checked, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
