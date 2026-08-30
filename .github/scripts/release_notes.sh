#!/usr/bin/env bash
# The commits of the fork that are new in a release, one line each.
#
#   release_notes.sh <tag> <upstream ref> [<previous release tag>]
#
# Never an upstream commit: those are reachable from <upstream ref> (main, the
# mirror of the upstream tag). With a previous release, none whose patch was
# already in it: after dev-main was rebased onto a newer upstream every fork
# commit has a new hash, and --cherry-pick sees through that.
set -euo pipefail
tag=$1
upstream=$2
prev=${3:-}
if [ -n "$prev" ]; then
  git log --no-merges --cherry-pick --right-only --format='- %s' "$prev...$tag" "^$upstream"
else
  git log --no-merges --format='- %s' "$upstream..$tag"
fi
