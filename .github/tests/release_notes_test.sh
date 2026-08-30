#!/usr/bin/env bash
# The release notes list the commits of the fork and nothing else, also after
# the integration branch was rebased onto a newer upstream: the old tag then
# points into the old history, and a plain "prev..tag" would list the new
# upstream commits and every fork commit again under its new hash.
#
#   bash .github/tests/release_notes_test.sh
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
script="$here/../scripts/release_notes.sh"
failed=0
check() {  # check <name> <expected> <got>
  if [ "$2" = "$3" ]; then echo "  PASS $1"; else echo "  FAIL $1"; echo "    expected: $(echo "$2" | tr '\n' '|')"; echo "    got:      $(echo "$3" | tr '\n' '|')"; failed=$((failed+1)); fi
}

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
cd "$work"
git init -q -b main .
git config user.email t@example.com
git config user.name t
c() { echo "$1" >> "$1.txt"; git add -A; git commit -q -m "$1"; }

c "upstream 26.02"
git switch -q -c dev-main
c "fork a"
c "fork b"
git tag 26.02-fork.1

echo "-- first release: everything on top of upstream"
check "no previous release" "$(printf -- '- fork b\n- fork a')" "$("$script" 26.02-fork.1 main)"

git switch -q main
c "upstream 26.03"
git switch -q dev-main
git rebase -q main
c "fork c"
git tag 26.03-fork.1

echo "-- after a rebase onto a newer upstream"
check "only the fork commit that is new" "- fork c" "$("$script" 26.03-fork.1 main 26.02-fork.1)"
check "first release on the new upstream, without a previous: all fork commits" \
  "$(printf -- '- fork c\n- fork b\n- fork a')" "$("$script" 26.03-fork.1 main)"

git merge -q --no-ff -m "Merge pr/x" main 2>/dev/null || true
c "fork d"
git tag 26.03-fork.2
echo "-- merges are left out"
check "d only, no merge commit" "- fork d" "$("$script" 26.03-fork.2 main 26.03-fork.1)"

echo "$failed failed"
exit $((failed > 0))
