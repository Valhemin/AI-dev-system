#!/bin/zsh

set -euo pipefail

ROOT="${AI_DEV_ROOT:-${1:-ai-dev-system}}"
REPOS="${AI_DEV_REPOS:-${2:-ai-repos}}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -f "$SCRIPT_DIR/ai-dev-registry.py" ]; then
  REGISTRY_SCRIPT="$SCRIPT_DIR/ai-dev-registry.py"
elif [ -f "$ROOT/shared/scripts/ai-dev-registry.py" ]; then
  REGISTRY_SCRIPT="$ROOT/shared/scripts/ai-dev-registry.py"
else
  echo "ERROR: Cannot find ai-dev-registry.py"
  exit 1
fi

python3 "$REGISTRY_SCRIPT" refresh --root "$ROOT" --repos "$REPOS"
