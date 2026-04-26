#!/bin/zsh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SYSTEM_ROOT="${2:-$ROOT_DIR/ai-dev-system}"
REPOS_DIR="${1:-$ROOT_DIR/ai-repos}"

"$SYSTEM_ROOT/shared/scripts/update-ai-repos.sh" "$SYSTEM_ROOT" "$REPOS_DIR"
