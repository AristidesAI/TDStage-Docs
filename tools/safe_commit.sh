#!/bin/sh
# Commit named paths through a PRIVATE index, in a repository several sessions share.
#
# Why this exists. On 2026-11-11 a commit here used `git add <one path>` and then
# a plain `git commit`, which commits the whole index - and the shared index was
# already holding four other files staged by another session, in a reverted
# state. The commit silently carried those reversions, one of them a privacy
# regression in a note the client reads. Path-scoped `add` does not make a
# path-scoped commit.
#
# Usage:
#   tools/safe_commit.sh -m "subject and body" path [path ...]
#   tools/safe_commit.sh -F message-file      path [path ...]
#
# It commits exactly the paths given, on the current branch, and refuses if the
# branch moved under it (the update-ref old-value check). It prints the commit's
# stat so you can read what went in before pushing.
set -eu

msg_mode=""; msg=""
case "${1:-}" in
  -m) msg_mode=-m; msg=${2:?message}; shift 2 ;;
  -F) msg_mode=-F; msg=${2:?message file}; shift 2 ;;
  *)  echo "usage: $0 -m MESSAGE|-F FILE path [path ...]" >&2; exit 2 ;;
esac
[ "$#" -ge 1 ] || { echo "$0: name at least one path" >&2; exit 2; }

top=$(git rev-parse --show-toplevel)
branch=$(git symbolic-ref --quiet --short HEAD) || {
  echo "$0: detached HEAD, commit it yourself" >&2; exit 2; }
old=$(git rev-parse HEAD)

idx=$(mktemp "${TMPDIR:-/tmp}/safe-index.XXXXXX")
rm -f "$idx"
trap 'rm -f "$idx"' EXIT INT TERM

GIT_INDEX_FILE=$idx; export GIT_INDEX_FILE
git read-tree HEAD
git add -- "$@"
tree=$(git write-tree)

if [ "$tree" = "$(git rev-parse "$old^{tree}")" ]; then
  echo "$0: those paths are identical to HEAD, nothing to commit" >&2
  exit 1
fi

if [ "$msg_mode" = -m ]; then
  new=$(git commit-tree "$tree" -p "$old" -m "$msg")
else
  new=$(git commit-tree "$tree" -p "$old" -F "$msg")
fi

# old-value form: fails rather than clobbering if someone else moved the branch
git update-ref "refs/heads/$branch" "$new" "$old"
unset GIT_INDEX_FILE

# Bring the SHARED index up to date for these paths only, so the working tree
# does not read as "staged, modified" afterwards. Never `git reset`: that would
# unstage another session's work.
git add -- "$@"

echo "committed on $branch:"
git --no-pager show --stat --oneline "$new" | sed 's/^/  /'
echo
echo "read that list before pushing. cd $top && git push origin $branch"
