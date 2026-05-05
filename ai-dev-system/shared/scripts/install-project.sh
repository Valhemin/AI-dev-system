#!/bin/zsh

set -euo pipefail

SYSTEM_ROOT="${1:-ai-dev-system}"
PROJECT_ROOT="${2:-.}"
TOOL="${3:-all}"

if [ ! -d "$SYSTEM_ROOT" ]; then
  echo "ERROR: Cannot find system root: $SYSTEM_ROOT"
  exit 1
fi

if [ ! -d "$PROJECT_ROOT" ]; then
  echo "ERROR: Cannot find project root: $PROJECT_ROOT"
  exit 1
fi

mkdir -p "$PROJECT_ROOT/.ai-dev-system"
mkdir -p "$PROJECT_ROOT/.github"

STACKS=()
FRAMEWORKS=()

if [ -f "$PROJECT_ROOT/package.json" ]; then
  STACKS+=("javascript/typescript")
  grep -q "\"next\"" "$PROJECT_ROOT/package.json" 2>/dev/null && FRAMEWORKS+=("nextjs")
  grep -q "\"react\"" "$PROJECT_ROOT/package.json" 2>/dev/null && FRAMEWORKS+=("react")
  grep -q "\"@nestjs" "$PROJECT_ROOT/package.json" 2>/dev/null && FRAMEWORKS+=("nestjs")
  grep -q "\"playwright\"" "$PROJECT_ROOT/package.json" 2>/dev/null && FRAMEWORKS+=("playwright")
fi

[ -f "$PROJECT_ROOT/tsconfig.json" ] && STACKS+=("typescript")

if [ -f "$PROJECT_ROOT/requirements.txt" ] || [ -f "$PROJECT_ROOT/pyproject.toml" ] || [ -f "$PROJECT_ROOT/Pipfile" ]; then
  STACKS+=("python")
  grep -Rqi "fastapi" "$PROJECT_ROOT/requirements.txt" "$PROJECT_ROOT/pyproject.toml" 2>/dev/null && FRAMEWORKS+=("fastapi")
  grep -Rqi "django" "$PROJECT_ROOT/requirements.txt" "$PROJECT_ROOT/pyproject.toml" 2>/dev/null && FRAMEWORKS+=("django")
  grep -Rqi "selenium" "$PROJECT_ROOT/requirements.txt" "$PROJECT_ROOT/pyproject.toml" 2>/dev/null && FRAMEWORKS+=("selenium")
fi

if [ -f "$PROJECT_ROOT/Dockerfile" ] || [ -f "$PROJECT_ROOT/docker-compose.yml" ] || [ -f "$PROJECT_ROOT/compose.yml" ]; then
  FRAMEWORKS+=("docker")
fi

case "$TOOL" in
  claude)
    cp "$SYSTEM_ROOT/solo-dev/adapters/claude/CLAUDE.md" "$PROJECT_ROOT/CLAUDE.md"
    ;;
  cursor)
    cp "$SYSTEM_ROOT/solo-dev/adapters/cursor/.cursorrules" "$PROJECT_ROOT/.cursorrules"
    ;;
  chatgpt)
    cp "$SYSTEM_ROOT/solo-dev/adapters/chatgpt/project-instructions.md" "$PROJECT_ROOT/.ai-dev-system/chatgpt-project-instructions.md"
    ;;
  copilot)
    cp "$SYSTEM_ROOT/solo-dev/adapters/copilot/copilot-instructions.md" "$PROJECT_ROOT/.github/copilot-instructions.md"
    ;;
  all)
    cp "$SYSTEM_ROOT/solo-dev/adapters/claude/CLAUDE.md" "$PROJECT_ROOT/CLAUDE.md"
    cp "$SYSTEM_ROOT/solo-dev/adapters/cursor/.cursorrules" "$PROJECT_ROOT/.cursorrules"
    cp "$SYSTEM_ROOT/solo-dev/adapters/chatgpt/project-instructions.md" "$PROJECT_ROOT/.ai-dev-system/chatgpt-project-instructions.md"
    cp "$SYSTEM_ROOT/solo-dev/adapters/copilot/copilot-instructions.md" "$PROJECT_ROOT/.github/copilot-instructions.md"
    ;;
  *)
    echo "Unknown tool: $TOOL"
    echo "Use: claude | cursor | chatgpt | copilot | all"
    exit 1
    ;;
esac

# Copy AI_ENTRY.md as the main entry point for the project
cp "$SYSTEM_ROOT/AI_ENTRY.md" "$PROJECT_ROOT/.ai-dev-system/AI_ENTRY.md"

python3 "$SYSTEM_ROOT/shared/scripts/project-intake.py" \
  --system-root "$SYSTEM_ROOT" \
  --project-root "$PROJECT_ROOT"
python3 "$SYSTEM_ROOT/shared/scripts/update-project-memory.py" --project-root "$PROJECT_ROOT"
python3 "$SYSTEM_ROOT/shared/scripts/update-docs-from-source.py" --project-root "$PROJECT_ROOT"
python3 "$SYSTEM_ROOT/shared/scripts/project-doc-health.py" --project-root "$PROJECT_ROOT" >/dev/null || true

echo "Installed ai-dev-system adapter: $TOOL"
echo "Project docs: $PROJECT_ROOT/.ai-dev-system/"
