#!/bin/zsh

set -euo pipefail

SYSTEM_ROOT="${1:?Usage: update-ai-repos.sh /path/to/ai-dev-system [/path/to/ai-repos]}"
REPOS_DIR="${2:-$SYSTEM_ROOT/../ai-repos}"

if [ ! -d "$REPOS_DIR" ]; then
  echo "ERROR: Cannot find ai-repos directory: $REPOS_DIR"
  exit 1
fi

echo "Updating git repositories in: $REPOS_DIR"

updated=0
skipped=0
failed=0

while IFS= read -r git_dir; do
  repo_dir="$(dirname "$git_dir")"
  repo_name="$(basename "$repo_dir")"
  echo ""
  echo "==> $repo_name"
  if git -C "$repo_dir" pull --ff-only; then
    updated=$((updated + 1))
  else
    echo "WARN: pull failed for $repo_name"
    failed=$((failed + 1))
  fi
done < <(find "$REPOS_DIR" -mindepth 2 -maxdepth 2 -type d -name .git | sort)

while IFS= read -r non_git_dir; do
  repo_name="$(basename "$non_git_dir")"
  echo "SKIP: $repo_name (not a git repo)"
  skipped=$((skipped + 1))
done < <(find "$REPOS_DIR" -mindepth 1 -maxdepth 1 -type d ! -name .git ! -exec test -d "{}/.git" \; -print | sort)

echo ""
echo "Summary: updated=$updated failed=$failed skipped=$skipped"
echo "Refreshing registry after repo update..."

"$SYSTEM_ROOT/shared/scripts/refresh-registry.sh" "$SYSTEM_ROOT" "$REPOS_DIR"
python3 "$SYSTEM_ROOT/shared/scripts/ai-dev-registry.py" eval --root "$SYSTEM_ROOT"

echo "Done."
