#!/usr/bin/env bash
# The release notes list the commits of the fork and nothing else: not the
# upstream commits that were merged into the integration branch, and not the
# fork commits again after a rebase (the old tag then points into the old
# history, and a plain "prev..tag" would list them under their new hashes).
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

# from now on upstream is merged into dev-main, not rebased (PR-009)
git switch -q main
c "upstream 26.04"
git switch -q dev-main
git merge -q --no-ff -m "Merge main: 7-Zip 26.04" main
c "fork d"
git tag 26.04-fork.1

echo "-- after a merge of a newer upstream"
check "the merge commit has two parents" "2" "$(git rev-list --parents -n 1 HEAD~1 | wc -w | xargs expr -1 +)"
check "the previous release is still an ancestor" "yes" "$(git merge-base --is-ancestor 26.03-fork.1 26.04-fork.1 && echo yes)"
check "only the fork commit that is new, not the upstream one, not the merge" "- fork d" "$("$script" 26.04-fork.1 main 26.03-fork.1)"
check "first release on 26.04 without a previous: every fork commit, once" \
  "$(printf -- '- fork d\n- fork c\n- fork b\n- fork a')" "$("$script" 26.04-fork.1 main)"

echo "$failed failed"
exit $((failed > 0))
