#!/usr/bin/env python3
"""Tests for release_version.py: what a release tag of this fork may look like,
and what it turns into.

    python3 .github/tests/release_version_test.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import release_version as rv  # noqa: E402

failed = 0


def check(ok, what):
    global failed
    if not ok:
        failed += 1
    print("  %-4s %s" % ("PASS" if ok else "FAIL", what))


def parses(tag, upstream, fork, rc):
    got = rv.parse_tag(tag)
    check(got == (upstream, fork, rc), "%s -> %r (got %r)" % (tag, (upstream, fork, rc), got))


def rejects(tag):
    try:
        rv.parse_tag(tag)
    except ValueError:
        check(True, "%s is rejected" % tag)
        return
    check(False, "%s is rejected" % tag)


print("-- tag names")
parses("26.02-fork.1", "26.02", 1, None)
parses("26.02-fork.12", "26.02", 12, None)
parses("26.02-fork.3-rc.1", "26.02", 3, 1)
parses("27.00-fork.1", "27.00", 1, None)
rejects("26.02")                # the tag of upstream itself
rejects("v26.02-fork.1")        # no v prefix, upstream has none
rejects("26.02-fork.0")         # the first release is 1
rejects("26.02-fork.01")        # no leading zero, it would not sort
rejects("26.02-fork.1-rc.0")
rejects("26.02-fork.1-rc1")
rejects("26.02-fork")
rejects("26.2-fork.1")          # upstream writes two digits
rejects("26.02-fork.1-beta.1")  # only rc is defined
rejects("26.02-fork.1 ")

print("-- the upstream version in readme.txt")
check(rv.readme_version("7-Zip 26.02 Sources\n-------------------\n") == "26.02",
      "the first line of readme.txt gives 26.02")
check(rv.readme_version("7-Zip 27.00 Sources\n") == "27.00", "and 27.00")
try:
    rv.readme_version("nothing here\n")
    check(False, "a readme without a version is rejected")
except ValueError:
    check(True, "a readme without a version is rejected")

print("-- the tag must be based on the upstream version of the tagged tree")
check(rv.check_upstream("26.02-fork.3", "7-Zip 26.02 Sources\n") is None, "26.02-fork.3 on 26.02 sources: fine")
try:
    rv.check_upstream("26.02-fork.3", "7-Zip 26.03 Sources\n")
    check(False, "26.02-fork.3 on 26.03 sources is rejected")
except ValueError:
    check(True, "26.02-fork.3 on 26.03 sources is rejected")

print("-- what the tag becomes")
check(rv.msi_version("26.02-fork.3") == "26.2.3", "MSI version of 26.02-fork.3 is 26.2.3")
check(rv.msi_version("26.02-fork.3-rc.1") == "26.2.3", "an rc has the MSI version of the release it precedes")
check(rv.msi_version("27.00-fork.1") == "27.0.1", "MSI version of 27.00-fork.1 is 27.0.1")
check(rv.is_prerelease("26.02-fork.3-rc.1") is True, "rc is a prerelease")
check(rv.is_prerelease("26.02-fork.3") is False, "a release is not")
check(rv.release_title("26.02-fork.3", "") == "7-Zip-fork 26.02-fork.3", "title without an alias")
check(rv.release_title("26.02-fork.3", "Kanji") == '7-Zip-fork 26.02-fork.3 "Kanji"', "title with an alias")
check(rv.release_title("26.02-fork.3", "  Kanji \n") == '7-Zip-fork 26.02-fork.3 "Kanji"', "the alias is trimmed")
check(rv.asset_stem("26.02-fork.3") == "7zip-fork-26.02-fork.3", "asset names start with 7zip-fork-<tag>")

print("-- ordering")
tags = ["26.02-fork.10", "26.02-fork.2", "26.02-fork.10-rc.1", "27.00-fork.1", "26.02-fork.2-rc.3"]
check(sorted(tags, key=rv.sort_key) ==
      ["26.02-fork.2-rc.3", "26.02-fork.2", "26.02-fork.10-rc.1", "26.02-fork.10", "27.00-fork.1"],
      "fork numbers sort numerically, an rc comes before its release, a newer upstream comes last")

print("%d failed" % failed)
sys.exit(1 if failed else 0)
