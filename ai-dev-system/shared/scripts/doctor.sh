#!/bin/zsh

set -euo pipefail

ROOT="${1:-ai-dev-system}"

required=(
  "AI_ENTRY.md"
  "solo-dev/AI_DEV.md"
  "team-dev/AI_TEAM.md"
  "solo-dev/rules/CORE.md"
  "solo-dev/rules/SELF_CHECK.md"
  "shared/router/LANGUAGE_ROUTER.md"
  "shared/router/MODE_ROUTER.md"
  "shared/router/ROUTER.md"
  "shared/registry/SKILL_INDEX.md"
  "shared/registry/skills.json"
  "shared/registry/catalog.json"
  "shared/registry/activation-report.json"
  "shared/registry/ACTIVATION_REPORT.md"
  "shared/registry/bundles.json"
  "shared/registry/source-strategy.json"
  "shared/router/STACK_KEYWORDS.json"
  "shared/router/PROBLEM_KEYWORDS.json"
  "shared/evaluation/routing-eval.json"
  "shared/registry/imported-skills.tsv"
  "packs/workflows/catalog.json"
  "packs/roles/catalog.json"
  "packs/rules/catalog.json"
  "shared/scripts/install-project.sh"
  "shared/scripts/project-intake.py"
  "shared/scripts/project-skill-scaffold.py"
  "shared/scripts/project-doc-health.py"
  "shared/scripts/project-dedupe-report.py"
  "shared/scripts/project-brief.py"
  "shared/scripts/update-project-memory.py"
  "shared/scripts/project-status.py"
  "shared/scripts/update-docs-from-source.py"
  "shared/scripts/session-save.py"
  "shared/scripts/session-resume.py"
  "shared/scripts/refresh-registry.sh"
  "shared/scripts/ai-dev-registry.py"
  "shared/scripts/freeze-source-metadata.py"
  "bin/ai-dev"
)

echo "Checking $ROOT"

for file in "${required[@]}"; do
  if [ -f "$ROOT/$file" ]; then
    echo "OK: $file"
  else
    echo "MISSING: $file"
  fi
done

echo ""
echo "Skill source summary:"
awk -F "|" "{count[\$3]++} END {for (k in count) print k \": \" count[k]}" "$ROOT/shared/registry/imported-skills.tsv" 2>/dev/null || true

echo ""
echo "Community/conversion skills:"
awk -F "|" "\$3 ~ /community/ {print \"- \" \$1 \" -> \" \$2 \" (\" \$3 \")\"}" "$ROOT/shared/registry/imported-skills.tsv" 2>/dev/null || true

echo ""
echo "Generated fallback skills:"
awk -F "|" "\$3 == \"generated-fallback\" {print \"- \" \$1}" "$ROOT/shared/registry/imported-skills.tsv" 2>/dev/null || true

echo ""
echo "Catalog summary:"
python3 - "$ROOT" <<PY 2>/dev/null || true
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
skills = json.load((root / "shared/registry/skills.json").open())
catalog = json.load((root / "shared/registry/catalog.json").open())
active_review = [s for s in skills if s.get("health") != "ok"]
print(f"active skills: {len(skills)}")
print(f"catalog items: {len(catalog)}")
print(f"active review: {len(active_review)}")
PY
