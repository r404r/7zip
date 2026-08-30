#!/usr/bin/env python3
"""The release tags of this fork, and what they turn into.

    26.02-fork.3         the third release of the fork on top of 7-Zip 26.02
    26.02-fork.3-rc.1    a release candidate for it (a prerelease on GitHub)

The upstream part must be the version of the tagged tree (readme.txt), so a
tag cannot claim an upstream version it is not built from. The MSI gets the
fork number as its third component: 26.2.3, which Windows Installer orders
correctly across fork releases and across upstream versions.

    python3 .github/tests/release_version.py <tag> <path to DOC/readme.txt> [<alias>]

prints one KEY=VALUE per line for the workflow: UPSTREAM, FORK, RC, MSI_VERSION,
PRERELEASE, TITLE, ASSET_STEM.
"""
import re
import sys

TAG_RE = re.compile(r"^(\d+\.\d{2})-fork\.([1-9]\d*)(?:-rc\.([1-9]\d*))?$")
README_RE = re.compile(r"^7-Zip (\d+\.\d{2}) ")


def parse_tag(tag):
    """-> (upstream, fork, rc or None); ValueError for anything else."""
    m = TAG_RE.match(tag)
    if not m:
        raise ValueError("not a release tag of this fork: %r" % tag)
    return m.group(1), int(m.group(2)), (int(m.group(3)) if m.group(3) else None)


def readme_version(text):
    m = README_RE.match(text)
    if not m:
        raise ValueError("no upstream version in the first line of readme.txt")
    return m.group(1)


def check_upstream(tag, readme_text):
    upstream = parse_tag(tag)[0]
    tree = readme_version(readme_text)
    if upstream != tree:
        raise ValueError("tag %s says upstream %s, the tree is 7-Zip %s" % (tag, upstream, tree))


def msi_version(tag):
    upstream, fork, _rc = parse_tag(tag)
    major, minor = upstream.split(".")
    return "%d.%d.%d" % (int(major), int(minor), fork)


def is_prerelease(tag):
    return parse_tag(tag)[2] is not None


def release_title(tag, alias):
    parse_tag(tag)
    alias = (alias or "").strip()
    title = "7-Zip-fork " + tag
    if alias:
        title += ' "%s"' % alias
    return title


def asset_stem(tag):
    parse_tag(tag)
    return "7zip-fork-" + tag


def sort_key(tag):
    upstream, fork, rc = parse_tag(tag)
    major, minor = (int(x) for x in upstream.split("."))
    # an rc sorts before the release it precedes
    return (major, minor, fork, 0 if rc is not None else 1, rc or 0)


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    tag, readme_path = argv[1], argv[2]
    alias = argv[3] if len(argv) > 3 else ""
    with open(readme_path, encoding="utf-8", errors="replace") as f:
        readme = f.read()
    check_upstream(tag, readme)
    upstream, fork, rc = parse_tag(tag)
    print("UPSTREAM=%s" % upstream)
    print("FORK=%d" % fork)
    print("RC=%s" % ("" if rc is None else rc))
    print("MSI_VERSION=%s" % msi_version(tag))
    print("PRERELEASE=%s" % ("true" if is_prerelease(tag) else "false"))
    print("TITLE=%s" % release_title(tag, alias))
    print("ASSET_STEM=%s" % asset_stem(tag))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except ValueError as e:
        print("error: %s" % e, file=sys.stderr)
        sys.exit(1)
