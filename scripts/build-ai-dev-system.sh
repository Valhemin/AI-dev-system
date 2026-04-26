#!/bin/zsh

set -euo pipefail

ROOT="${1:-ai-dev-system}"
REPOS="${2:-ai-repos}"

echo "=================================================="
echo " AI Dev System ULTIMATE Rebuilder"
echo " ROOT : $ROOT"
echo " REPOS: $REPOS"
echo "=================================================="

# ==================================================
# Helpers
# ==================================================

log() {
  echo "$1"
}

mkdirp() {
  mkdir -p "$1"
}

write_file() {
  local file="$1"
  local content="$2"
  mkdir -p "$(dirname "$file")"
  printf "%s\n" "$content" > "$file"
  log "WROTE: $file"
}

copy_file() {
  local src="$1"
  local dest="$2"

  if [ -f "$src" ]; then
    mkdir -p "$(dirname "$dest")"
    cp "$src" "$dest"
    log "COPIED: $src -> $dest"
    return 0
  fi

  return 1
}

clone_or_update() {
  local url="$1"
  local dir="$2"

  mkdir -p "$REPOS"

  if [ -d "$REPOS/$dir/.git" ]; then
    log "UPDATING: $dir"
    git -C "$REPOS/$dir" pull --ff-only || log "WARN: pull failed for $dir, keeping existing copy"
  elif [ -d "$REPOS/$dir" ]; then
    log "WARN: $REPOS/$dir exists but is not a git repo. Skip clone."
  else
    log "CLONING: $dir"
    git clone "$url" "$REPOS/$dir"
  fi
}

find_any_doc() {
  local base="$1"
  shift

  if [ ! -d "$base" ]; then
    echo ""
    return 0
  fi

  for pattern in "$@"; do
    local found
    found="$(find "$base" -type f \( -name "SKILL.md" -o -name "AGENTS.md" -o -name "README.md" -o -name "*.mdc" -o -name ".cursorrules" -o -name "*.instructions.md" -o -name "*.prompt.md" -o -name "*.chatmode.md" \) -path "$pattern" 2>/dev/null | head -n 1)"
    if [ -n "$found" ]; then
      echo "$found"
      return 0
    fi
  done

  echo ""
}

first_existing_file() {
  for file in "$@"; do
    if [ -n "$file" ] && [ -f "$file" ]; then
      echo "$file"
      return 0
    fi
  done

  echo ""
}

copy_skill_dir() {
  local src="$1"
  local dest="$2"
  local src_dir
  local dest_dir

  src_dir="$(dirname "$src")"
  dest_dir="$(dirname "$dest")"

  mkdir -p "$dest_dir"
  cp -R "$src_dir/." "$dest_dir/"
  log "COPIED SKILL DIR: $src_dir -> $dest_dir"
}

generated_skill() {
  local id="$1"
  local name="$2"
  local desc="$3"
  local workflow="$4"
  local constraints="$5"

  cat <<EOF
---
name: $name
description: $desc
---

# $name

## Purpose

Use this compact fallback skill when no suitable community skill is imported.

## Workflow

$workflow

## Constraints

$constraints

## Output

1. Routing
2. Reasoning summary
3. Action / plan
4. Verification
5. Risk
EOF
}

import_skill_or_fallback() {
  local id="$1"
  local dest="$2"
  local name="$3"
  local desc="$4"
  local workflow="$5"
  local constraints="$6"
  shift 6

  local found=""
  for src in "$@"; do
    if [ -n "$src" ] && [ -f "$src" ]; then
      found="$src"
      break
    fi
  done

  if [ -n "$found" ]; then
    if [[ "$found" == *"SKILL.md" ]]; then
      copy_skill_dir "$found" "$dest"
      echo "$id|$dest|community-skill|$found" >> "$ROOT/shared/registry/imported-skills.tsv"
    else
      mkdir -p "$(dirname "$dest")"
      {
        echo "---"
        echo "name: ${name}"
        echo "description: Imported community guidance converted into a local SKILL.md. Use for $desc"
        echo "---"
        echo ""
        echo "# ${name}"
        echo ""
        echo "Source: $found"
        echo ""
        cat "$found"
      } > "$dest"
      log "CONVERTED DOC TO SKILL: $found -> $dest"
      echo "$id|$dest|community-doc-converted|$found" >> "$ROOT/shared/registry/imported-skills.tsv"
    fi
  else
    mkdir -p "$(dirname "$dest")"
    generated_skill "$id" "$name" "$desc" "$workflow" "$constraints" > "$dest"
    echo "$id|$dest|generated-fallback|local" >> "$ROOT/shared/registry/imported-skills.tsv"
    log "GENERATED FALLBACK SKILL: $id"
  fi
}

import_active_doc() {
  local id="$1"
  local src="$2"
  local dest="$3"
  local title="$4"
  local desc="$5"

  mkdir -p "$(dirname "$dest")"

  if [[ "$id" == workflow:* ]]; then
    cat > "$dest" <<EOF
---
name: $title
description: $desc
---

# $title

$desc

Source: ${src:-local}

## Portable Protocol

1. Classify the request and confirm this workflow is selected.
2. Load only relevant active skills, roles, pack catalogs, or leaf files.
3. Translate source-specific commands into the current AI/runtime capabilities.
4. Execute the smallest useful workflow slice.
5. Verify with concrete checks and report residual risk.

## Context Rule

Do not paste or load full source workflow content unless this active workflow is insufficient.
Use the source path or catalog item as leaf context only when needed.
EOF
    if [ -n "$src" ] && [ -f "$src" ]; then
      log "WRAPPED ACTIVE WORKFLOW: $src -> $dest"
      echo "$id|$dest|community-doc-wrapped|$src" >> "$ROOT/shared/registry/imported-skills.tsv"
    else
      log "GENERATED ACTIVE WORKFLOW: $id"
      echo "$id|$dest|generated-portable-doc|local" >> "$ROOT/shared/registry/imported-skills.tsv"
    fi
  elif [ -n "$src" ] && [ -f "$src" ]; then
    cp "$src" "$dest"
    log "COPIED ACTIVE DOC: $src -> $dest"
    echo "$id|$dest|community-doc|$src" >> "$ROOT/shared/registry/imported-skills.tsv"
  else
    cat > "$dest" <<EOF
---
name: $title
description: $desc
---

# $title

$desc

## Portable Workflow

1. Route the request.
2. Load only the smallest useful context.
3. Execute with explicit verification.
4. Report residual risk.
EOF
    log "GENERATED ACTIVE DOC: $id"
    echo "$id|$dest|generated-portable-doc|local" >> "$ROOT/shared/registry/imported-skills.tsv"
  fi
}

# ==================================================
# 1. Clone/update source repos
# ==================================================

# Core skill / agent repositories
clone_or_update "https://github.com/openai/skills.git" "openai-skills"
clone_or_update "https://github.com/vercel-labs/agent-skills.git" "agent-skills"
clone_or_update "https://github.com/affaan-m/everything-claude-code.git" "everything-claude-code"
clone_or_update "https://github.com/vudovn/antigravity-kit.git" "antigravity-kit"
clone_or_update "https://github.com/forrestchang/andrej-karpathy-skills.git" "andrej-karpathy-skills"
clone_or_update "https://github.com/PatrickJS/awesome-cursorrules.git" "awesome-cursorrules"
clone_or_update "https://github.com/FoundationAgents/MetaGPT.git" "MetaGPT"
clone_or_update "https://github.com/microsoft/autogen.git" "autogen"
clone_or_update "https://github.com/skillmatic-ai/awesome-agent-skills.git" "awesome-agent-skills"
clone_or_update "https://github.com/sickn33/antigravity-awesome-skills.git" "antigravity-awesome-skills"
clone_or_update "https://github.com/caramaschiHG/awesome-ai-agents-2026.git" "awesome-ai-agents-2026"

# Extra coding-focused community repos
clone_or_update "https://github.com/Kadajett/agent-nestjs-skills.git" "agent-nestjs-skills"
clone_or_update "https://github.com/l-mb/python-refactoring-skills.git" "python-refactoring-skills"
clone_or_update "https://github.com/alirezarezvani/claude-skills.git" "claude-skills"
clone_or_update "https://github.com/SnakeO/claude-debug-and-refactor-skills-plugin.git" "claude-debug-and-refactor-skills-plugin"
clone_or_update "https://github.com/VoltAgent/awesome-agent-skills.git" "voltagent-awesome-agent-skills"
clone_or_update "https://github.com/github/awesome-copilot.git" "awesome-copilot"
clone_or_update "https://github.com/jaktestowac/awesome-copilot-for-testers.git" "awesome-copilot-for-testers"

OPENAI="$REPOS/openai-skills"
VERCEL="$REPOS/agent-skills"
ECC="$REPOS/everything-claude-code"
AGKIT="$REPOS/antigravity-kit"
KARPATHY="$REPOS/andrej-karpathy-skills"
CURSOR="$REPOS/awesome-cursorrules"
METAGPT="$REPOS/MetaGPT"
AUTOGEN="$REPOS/autogen"
NESTJS_SKILLS="$REPOS/agent-nestjs-skills"
PY_REFACTOR="$REPOS/python-refactoring-skills"
CLAUDE_SKILLS="$REPOS/claude-skills"
DEBUG_REFACTOR="$REPOS/claude-debug-and-refactor-skills-plugin"
COPILOT="$REPOS/awesome-copilot"
COPILOT_TESTERS="$REPOS/awesome-copilot-for-testers"

# ==================================================
# 2. Fresh rebuild
# ==================================================

if [ -d "$ROOT" ]; then
  log "DELETING OLD SYSTEM: $ROOT"
  rm -rf "$ROOT"
fi

mkdirp "$ROOT"

mkdirp "$ROOT/bin"
mkdirp "$ROOT/shared/core"
mkdirp "$ROOT/shared/router"
mkdirp "$ROOT/shared/commands"
mkdirp "$ROOT/shared/skill-spec/skill-template"
mkdirp "$ROOT/shared/templates"
mkdirp "$ROOT/shared/registry"
mkdirp "$ROOT/shared/scripts"
mkdirp "$ROOT/shared/evaluation"
mkdirp "$ROOT/shared/sources"
mkdirp "$ROOT/shared/workflows"

mkdirp "$ROOT/solo-dev/rules"
mkdirp "$ROOT/solo-dev/skills/task"
mkdirp "$ROOT/solo-dev/skills/language"
mkdirp "$ROOT/solo-dev/skills/framework"
mkdirp "$ROOT/solo-dev/skills/problem"
mkdirp "$ROOT/solo-dev/skills/workflow"
mkdirp "$ROOT/solo-dev/workflows"
mkdirp "$ROOT/solo-dev/adapters/claude"
mkdirp "$ROOT/solo-dev/adapters/cursor"
mkdirp "$ROOT/solo-dev/adapters/cline"
mkdirp "$ROOT/solo-dev/adapters/chatgpt"
mkdirp "$ROOT/solo-dev/adapters/gemini"
mkdirp "$ROOT/solo-dev/adapters/continue"
mkdirp "$ROOT/solo-dev/adapters/copilot"
mkdirp "$ROOT/solo-dev/memory"

mkdirp "$ROOT/team-dev/roles"
mkdirp "$ROOT/team-dev/orchestration"
mkdirp "$ROOT/team-dev/protocols"
mkdirp "$ROOT/team-dev/workflows"
mkdirp "$ROOT/team-dev/quality"
mkdirp "$ROOT/team-dev/memory/decisions"
mkdirp "$ROOT/team-dev/governance"

mkdirp "$ROOT/packs/frontend"
mkdirp "$ROOT/packs/backend"
mkdirp "$ROOT/packs/fullstack"
mkdirp "$ROOT/packs/product"
mkdirp "$ROOT/packs/security"
mkdirp "$ROOT/packs/devops"
mkdirp "$ROOT/packs/testing"
mkdirp "$ROOT/packs/workflows"
mkdirp "$ROOT/packs/roles"
mkdirp "$ROOT/packs/rules"

: > "$ROOT/shared/registry/imported-skills.tsv"

# ==================================================
# 3. Source transparency
# ==================================================

copy_file "$KARPATHY/CLAUDE.md" "$ROOT/shared/sources/karpathy-CLAUDE.md" || true
copy_file "$ECC/CLAUDE.md" "$ROOT/shared/sources/ecc-CLAUDE.md" || true
copy_file "$AGKIT/README.md" "$ROOT/shared/sources/antigravity-kit-README.md" || true
copy_file "$METAGPT/README.md" "$ROOT/shared/sources/metagpt-README.md" || true
copy_file "$AUTOGEN/README.md" "$ROOT/shared/sources/autogen-README.md" || true
copy_file "$NESTJS_SKILLS/SKILL.md" "$ROOT/shared/sources/nestjs-community.SKILL.md" || true
copy_file "$PY_REFACTOR/README.md" "$ROOT/shared/sources/python-refactoring-README.md" || true
copy_file "$CLAUDE_SKILLS/README.md" "$ROOT/shared/sources/claude-skills-README.md" || true
copy_file "$DEBUG_REFACTOR/README.md" "$ROOT/shared/sources/debug-refactor-README.md" || true
copy_file "$COPILOT/README.md" "$ROOT/shared/sources/awesome-copilot-README.md" || true
copy_file "$COPILOT_TESTERS/README.md" "$ROOT/shared/sources/awesome-copilot-for-testers-README.md" || true

write_file "$ROOT/shared/registry/source-catalog.json" "[
  {
    \"repo\": \"openai/skills\",
    \"local_path\": \"$OPENAI\",
    \"priority\": 80,
    \"allowed_categories\": [\"task\", \"workflow\", \"other\"],
    \"notes\": \"Official OpenAI skill format reference and examples.\"
  },
  {
    \"repo\": \"vercel-labs/agent-skills\",
    \"local_path\": \"$VERCEL\",
    \"priority\": 85,
    \"allowed_categories\": [\"framework\", \"problem\"],
    \"notes\": \"Strong React, web design, deployment, and Vercel-specific skills.\"
  },
  {
    \"repo\": \"vudovn/antigravity-kit\",
    \"local_path\": \"$AGKIT\",
    \"priority\": 95,
    \"allowed_categories\": [\"task\", \"framework\", \"problem\", \"workflow\", \"role\"],
    \"notes\": \"Best general-purpose source for routing, debugging, architecture, clean code, parallel agents, and practical app work.\"
  },
  {
    \"repo\": \"affaan-m/everything-claude-code\",
    \"local_path\": \"$ECC\",
    \"priority\": 90,
    \"allowed_categories\": [\"language\", \"framework\", \"problem\", \"workflow\"],
    \"notes\": \"Good language and platform pattern coverage.\"
  },
  {
    \"repo\": \"alirezarezvani/claude-skills\",
    \"local_path\": \"$CLAUDE_SKILLS\",
    \"priority\": 70,
    \"allowed_categories\": [\"problem\", \"role\", \"product\", \"business\"],
    \"notes\": \"Large catalog. Use explicit manifest paths because broad path matching easily imports unrelated skills.\"
  },
  {
    \"repo\": \"jaktestowac/awesome-copilot-for-testers\",
    \"local_path\": \"$COPILOT_TESTERS\",
    \"priority\": 75,
    \"allowed_categories\": [\"task\", \"problem\", \"quality\"],
    \"notes\": \"Good QA, testing, and static analysis skills.\"
  },
  {
    \"repo\": \"PatrickJS/awesome-cursorrules\",
    \"local_path\": \"$CURSOR\",
    \"priority\": 65,
    \"allowed_categories\": [\"language\", \"framework\"],
    \"notes\": \"Useful framework rule packs. Convert carefully because many files are Cursor-specific docs rather than portable skills.\"
  }
]
"

# ==================================================
# 4. Skill spec
# ==================================================

write_file "$ROOT/shared/skill-spec/SKILL_SPEC.md" "# Skill Spec

A skill is a reusable capability stored as:

\`\`\`txt
skill-name/
  SKILL.md
  scripts/
  references/
\`\`\`

Required frontmatter:

\`\`\`md
---
name: skill-name
description: Clear trigger condition and task scope.
category: task|language|framework|problem|role|workflow|other
intent:
  - bug_fix
  - feature_dev
stacks:
  - typescript
roles:
  - implementer
mode: quick|hybrid|full
risk: low|medium|high
---
\`\`\`

Rules:
1. Select by metadata first.
2. Load full SKILL.md only when selected.
3. Prefer community skill.
4. Use generated fallback only if no good community skill exists.
5. Keep fallback skills compact.
6. Do not load all skills into context.
7. Preserve scripts/, references/, and assets/ when importing community skills.
8. Reject or flag imported skills whose name/description do not match the target slot.

Recommended metadata:
- source_repo
- source_path
- source_commit
- source_license
- confidence: high|medium|low
- requires_approval: true|false
- tools
- inputs
- outputs
"

write_file "$ROOT/shared/skill-spec/skill-template/SKILL.md" "---
name: skill-name
description: Clear trigger condition and task scope.
---

# Skill Name

## Purpose

## Workflow

## Output

## Constraints
"

# ==================================================
# 5. Import/generate task skills
# ==================================================

for d in bug-fix code-review feature-dev refactor testing documentation; do
  mkdirp "$ROOT/solo-dev/skills/task/$d"
done

import_skill_or_fallback "task:bug-fix" "$ROOT/solo-dev/skills/task/bug-fix/SKILL.md" "bug-fix" \
  "fixing bugs, runtime errors, failing tests, regressions, stack traces, or incorrect behavior." \
  "1. Identify expected vs actual behavior.
2. Read the first meaningful error.
3. Locate the smallest relevant code path.
4. Identify root cause before editing.
5. Apply the minimal safe fix.
6. Verify with the smallest relevant test/check." \
  "- Do not rewrite unrelated code.
- Do not invent files, APIs, command outputs, or test results.
- Escalate if fix touches auth, data deletion, deployment, or secrets." \
  "$(first_existing_file \
    "$AGKIT/.agent/skills/systematic-debugging/SKILL.md" \
    "$CLAUDE_SKILLS/engineering/focused-fix/SKILL.md" \
    "$ECC/skills/agent-introspection-debugging/SKILL.md")"

import_skill_or_fallback "task:code-review" "$ROOT/solo-dev/skills/task/code-review/SKILL.md" "code-review" \
  "reviewing code for correctness, maintainability, security, performance, and regressions." \
  "1. Check requirement alignment.
2. Check correctness and edge cases.
3. Check security and data handling.
4. Check maintainability and minimality.
5. Check test coverage.
6. Return severity-based findings." \
  "- Do not rewrite code unless asked.
- Separate critical issues from suggestions.
- Avoid style-only noise unless it affects maintainability." \
  "$(find_any_doc "$VERCEL" "*/code-review*" "*/review*")" \
  "$(find_any_doc "$CLAUDE_SKILLS" "*/code-review*" "*/review*")" \
  "$(find_any_doc "$AGKIT" "*/code-review*" "*/review*")"

import_skill_or_fallback "task:feature-dev" "$ROOT/solo-dev/skills/task/feature-dev/SKILL.md" "feature-dev" \
  "implementing a small or medium feature with clear requirements." \
  "1. Restate expected behavior.
2. Inspect existing conventions.
3. Identify affected files/components.
4. Implement smallest usable slice.
5. Add or suggest relevant tests.
6. Check regressions." \
  "- Do not introduce architecture unless needed.
- Do not rewrite unrelated modules.
- Keep scope aligned with request." \
  "$(first_existing_file \
    "$AGKIT/.agent/skills/app-builder/SKILL.md" \
    "$AGKIT/.agent/skills/plan-writing/SKILL.md")"

import_skill_or_fallback "task:refactor" "$ROOT/solo-dev/skills/task/refactor/SKILL.md" "refactor" \
  "improving code structure without changing external behavior." \
  "1. Define behavior that must remain unchanged.
2. Identify the highest-impact code smell.
3. Make the smallest structural improvement.
4. Preserve public APIs.
5. Suggest regression checks." \
  "- No behavior change unless requested.
- Avoid broad rewrites.
- Prefer one safe transformation at a time." \
  "$(first_existing_file \
    "$AGKIT/.agent/skills/clean-code/SKILL.md" \
    "$PY_REFACTOR/skills/py-refactor/SKILL.md" \
    "$CLAUDE_SKILLS/engineering/tech-debt-tracker/SKILL.md")"

import_skill_or_fallback "task:testing" "$ROOT/solo-dev/skills/task/testing/SKILL.md" "testing" \
  "writing, improving, or reviewing tests and test strategy." \
  "1. Identify behavior under test.
2. Cover happy path.
3. Cover edge cases.
4. Cover failure path.
5. Keep tests deterministic.
6. Avoid testing implementation details unless necessary." \
  "- Do not claim tests pass unless run.
- Prefer stable selectors and deterministic data.
- Keep tests close to user-visible behavior where possible." \
  "$(first_existing_file \
    "$AGKIT/.agent/skills/testing-patterns/SKILL.md" \
    "$AGKIT/.agent/skills/tdd-workflow/SKILL.md" \
    "$COPILOT_TESTERS/skills/designing-functional-tests/SKILL.md")"

import_skill_or_fallback "task:documentation" "$ROOT/solo-dev/skills/task/documentation/SKILL.md" "documentation" \
  "writing README, usage guides, API docs, comments, or technical explanations." \
  "1. Identify target reader.
2. Explain purpose first.
3. Provide setup/usage steps.
4. Include examples.
5. Mention caveats and limitations." \
  "- Be actionable.
- Avoid vague claims.
- Do not invent unsupported behavior." \
  "$(find_any_doc "$OPENAI" "*/documentation*" "*/doc*")" \
  "$(find_any_doc "$CLAUDE_SKILLS" "*/documentation*" "*/doc*")" \
  "$(find_any_doc "$AGKIT" "*/documentation*" "*/doc*")"

# ==================================================
# 6. Import/generate language skills
# ==================================================

for d in python typescript javascript sql go rust java cpp csharp php ruby; do
  mkdirp "$ROOT/solo-dev/skills/language/$d"
done

import_skill_or_fallback "language:python" "$ROOT/solo-dev/skills/language/python/SKILL.md" "python-dev" \
  "Python code, asyncio, scripts, automation, data processing, backend services, and GUI apps." \
  "1. Identify Python version/runtime if relevant.
2. Inspect imports and dependency style.
3. Check sync vs async boundaries.
4. Preserve existing project style.
5. Suggest minimal tests or reproduction." \
  "- Watch for unawaited coroutine, blocking async calls, event-loop misuse, thread-safety, mutable defaults.
- Do not change environment/dependency assumptions without stating them." \
  "$(first_existing_file \
    "$AGKIT/.agent/skills/python-patterns/SKILL.md" \
    "$PY_REFACTOR/skills/py-code-health/SKILL.md" \
    "$PY_REFACTOR/skills/py-refactor/SKILL.md" \
    "$ECC/skills/python-testing/SKILL.md")"

import_skill_or_fallback "language:typescript" "$ROOT/solo-dev/skills/language/typescript/SKILL.md" "typescript-dev" \
  "TypeScript code, type errors, Node.js, Next.js, NestJS, frontend/backend TS apps." \
  "1. Inspect types and tsconfig assumptions.
2. Preserve type safety.
3. Avoid any unless justified.
4. Fix root mismatch, not symptoms.
5. Keep runtime and compile-time behavior aligned." \
  "- Avoid unsafe any.
- Check null/undefined, module import/export, DTO/API mismatch, async promises." \
  "$(first_existing_file \
    "$COPILOT_TESTERS/skills/static-code-analysis-typescript/SKILL.md" \
    "$AGKIT/.agent/skills/clean-code/SKILL.md")"

import_skill_or_fallback "language:javascript" "$ROOT/solo-dev/skills/language/javascript/SKILL.md" "javascript-dev" \
  "JavaScript, Node.js, browser code, npm tooling, and runtime errors." \
  "1. Identify runtime: browser, Node, bundler, framework.
2. Check module system: ESM or CommonJS.
3. Inspect async behavior.
4. Keep changes minimal.
5. Suggest runtime verification." \
  "- Watch undefined/null access, promise errors, module mismatch, dependency version issues." \
  "$(first_existing_file \
    "$CURSOR/rules/javascript-typescript-code-quality-cursorrules-pro/README.md" \
    "$CURSOR/rules/html-tailwind-css-javascript-cursorrules-prompt-fi/README.md" \
    "$AGKIT/.agent/skills/clean-code/SKILL.md")"

import_skill_or_fallback "language:sql" "$ROOT/solo-dev/skills/language/sql/SKILL.md" "sql-dev" \
  "SQL queries, schema design, migrations, indexes, joins, transactions, and database debugging." \
  "1. Identify database type if possible.
2. Understand schema and relationships.
3. Check query correctness.
4. Check indexes/performance.
5. Consider transaction safety.
6. Avoid destructive migration without approval." \
  "- Watch N+1 queries, missing indexes, unsafe migrations, wrong joins, SQL injection." \
  "$(find_any_doc "$CLAUDE_SKILLS" "*/sql*" "*/database*")" \
  "$(find_any_doc "$AGKIT" "*/sql*" "*/database*")"

for lang in go rust java cpp csharp php ruby; do
  lang_src=""
  case "$lang" in
    go)
      lang_src="$(first_existing_file "$ECC/skills/golang-patterns/SKILL.md" "$ECC/.kiro/skills/golang-patterns/SKILL.md")"
      ;;
    rust)
      lang_src="$(first_existing_file "$AGKIT/.agent/skills/rust-pro/SKILL.md" "$ECC/skills/rust-testing/SKILL.md")"
      ;;
    java)
      lang_src="$(first_existing_file "$ECC/skills/java-coding-standards/SKILL.md")"
      ;;
    cpp)
      lang_src="$(first_existing_file "$ECC/skills/cpp-coding-standards/SKILL.md" "$ECC/skills/cpp-testing/SKILL.md")"
      ;;
    csharp)
      lang_src="$(first_existing_file "$ECC/skills/csharp-testing/SKILL.md")"
      ;;
    php)
      lang_src="$(first_existing_file "$ECC/skills/laravel-security/SKILL.md" "$ECC/skills/laravel-tdd/SKILL.md")"
      ;;
    ruby)
      lang_src=""
      ;;
  esac

  import_skill_or_fallback "language:$lang" "$ROOT/solo-dev/skills/language/$lang/SKILL.md" "$lang-dev" \
    "$lang code review, debugging, feature work, and refactoring." \
    "1. Identify runtime/toolchain.
2. Inspect project conventions.
3. Make minimal, idiomatic changes.
4. Preserve behavior.
5. Suggest relevant verification." \
    "- Do not invent APIs or dependencies.
- Follow existing project style." \
    "$lang_src"
done

# ==================================================
# 7. Import/generate framework skills
# ==================================================

for d in react nextjs web-design nestjs nodejs fastapi django playwright selenium docker vue angular svelte react-native; do
  mkdirp "$ROOT/solo-dev/skills/framework/$d"
done

import_skill_or_fallback "framework:react" "$ROOT/solo-dev/skills/framework/react/SKILL.md" "react-dev" \
  "React components, hooks, state, effects, rendering, forms, and UI behavior." \
  "1. Identify component responsibility.
2. Check state ownership.
3. Check effect dependencies.
4. Check render performance.
5. Check loading/error/empty states." \
  "- Watch derived state misuse, infinite render loops, inaccessible interactions." \
  "$(first_existing_file \
    "$VERCEL/skills/react-best-practices/SKILL.md" \
    "$AGKIT/.agent/skills/nextjs-react-expert/SKILL.md")"

import_skill_or_fallback "framework:nextjs" "$ROOT/solo-dev/skills/framework/nextjs/SKILL.md" "nextjs-dev" \
  "Next.js App Router, Pages Router, server components, client components, route handlers, caching, and deployment issues." \
  "1. Identify App Router or Pages Router.
2. Check server vs client boundary.
3. Check data fetching and caching.
4. Check route handlers.
5. Review loading/error/not-found states.
6. Check environment variables and deployment behavior." \
  "- Watch unnecessary client components, server-only code in client components, stale cache, missing states." \
  "$(first_existing_file \
    "$AGKIT/.agent/skills/nextjs-react-expert/SKILL.md" \
    "$ECC/skills/nextjs-turbopack/SKILL.md")"

import_skill_or_fallback "framework:web-design" "$ROOT/solo-dev/skills/framework/web-design/SKILL.md" "web-design" \
  "landing pages, UI design, visual hierarchy, frontend polish, and web UI review." \
  "1. Define page purpose.
2. Establish visual hierarchy.
3. Check layout, spacing, typography.
4. Handle responsive states.
5. Check accessibility basics." \
  "- Avoid generic clutter.
- Keep UI state handling clear.
- Do not over-design beyond task." \
  "$(find_any_doc "$VERCEL" "*/web-design-guidelines*")" \
  "$(find_any_doc "$OPENAI" "*/frontend-skill*")"

import_skill_or_fallback "framework:nestjs" "$ROOT/solo-dev/skills/framework/nestjs/SKILL.md" "nestjs-dev" \
  "NestJS modules, controllers, services, providers, dependency injection, guards, interceptors, and backend APIs." \
  "1. Identify module/controller/service boundary.
2. Check provider registration.
3. Check imports/exports between modules.
4. Validate DTOs and pipes.
5. Check dependency injection errors.
6. Review guards/interceptors if relevant." \
  "- Watch provider not registered, circular dependency, missing exports, wrong injection token." \
  "$NESTJS_SKILLS/SKILL.md" \
  "$(find_any_doc "$NESTJS_SKILLS" "*/SKILL.md" "*/AGENTS.md")" \
  "$(find_any_doc "$CLAUDE_SKILLS" "*/nestjs*" "*/nest*")"

for fw in nodejs fastapi django playwright selenium docker vue angular svelte react-native; do
  fw_src=""
  case "$fw" in
    nodejs)
      fw_src="$(first_existing_file "$AGKIT/.agent/skills/nodejs-best-practices/SKILL.md")"
      ;;
    fastapi)
      fw_src="$(first_existing_file \
        "$CURSOR/rules/python-fastapi-best-practices-cursorrules-prompt-f/README.md" \
        "$CURSOR/rules/python-fastapi-scalable-api-cursorrules-prompt-fil/README.md")"
      ;;
    django)
      fw_src="$(first_existing_file "$ECC/skills/django-patterns/SKILL.md" "$ECC/skills/django-security/SKILL.md")"
      ;;
    playwright)
      fw_src="$(first_existing_file "$CLAUDE_SKILLS/engineering-team/playwright-pro/SKILL.md" "$COPILOT_TESTERS/skills/api-playwright-test-developer/SKILL.md")"
      ;;
    selenium)
      fw_src="$(first_existing_file "$CLAUDE_SKILLS/engineering/browser-automation/SKILL.md")"
      ;;
    docker)
      fw_src="$(first_existing_file "$CLAUDE_SKILLS/engineering/docker-development/SKILL.md" "$ECC/skills/docker-patterns/SKILL.md")"
      ;;
    vue)
      fw_src="$(first_existing_file \
        "$CURSOR/rules/vue3-composition-api-cursorrules-prompt-file/README.md" \
        "$CURSOR/rules/vue-3-nuxt-3-development-cursorrules-prompt-file/README.md")"
      ;;
    angular)
      fw_src="$(first_existing_file "$CURSOR/rules/angular-typescript-cursorrules-prompt-file/README.md")"
      ;;
    svelte)
      fw_src="$(first_existing_file \
        "$CURSOR/rules/sveltekit-typescript-guide-cursorrules-prompt-file/README.md" \
        "$CURSOR/rules/svelte-5-vs-svelte-4-cursorrules-prompt-file/README.md")"
      ;;
    react-native)
      fw_src="$(first_existing_file "$VERCEL/skills/react-native-skills/SKILL.md")"
      ;;
  esac

  import_skill_or_fallback "framework:$fw" "$ROOT/solo-dev/skills/framework/$fw/SKILL.md" "$fw-dev" \
    "$fw development, debugging, review, and implementation tasks." \
    "1. Identify framework conventions.
2. Locate relevant component/module/config.
3. Apply minimal framework-idiomatic change.
4. Check common failure modes.
5. Suggest verification." \
    "- Follow existing project conventions.
- Do not introduce unrelated architecture." \
    "$fw_src"
done

# ==================================================
# 8. Import/generate problem skills
# ==================================================

for d in async-debug api-debug database-debug dependency-debug build-error performance-debug auth-security git-workflow deployment-debug; do
  mkdirp "$ROOT/solo-dev/skills/problem/$d"
done

import_skill_or_fallback "problem:async-debug" "$ROOT/solo-dev/skills/problem/async-debug/SKILL.md" "async-debug" \
  "async/await, coroutine, event loop, threading, deadlock, GUI async integration, and concurrency bugs." \
  "1. Identify event loop ownership.
2. Identify sync/async boundary.
3. Find blocking calls.
4. Check awaited vs unawaited coroutines.
5. Check cancellation and cleanup.
6. Check thread safety." \
  "- Watch coroutine was never awaited, event loop already running, blocking IO, unsafe GUI thread update." \
  "$(find_any_doc "$CLAUDE_SKILLS" "*/async*" "*/concurrency*")" \
  "$(find_any_doc "$DEBUG_REFACTOR" "*/async*" "*/concurrency*")"

import_skill_or_fallback "problem:api-debug" "$ROOT/solo-dev/skills/problem/api-debug/SKILL.md" "api-debug" \
  "API errors, endpoints, status codes, request/response mismatch, validation, and integration bugs." \
  "1. Identify endpoint and method.
2. Check request payload.
3. Check validation.
4. Check auth/permission.
5. Check service/database layer.
6. Check response shape and status code." \
  "- Watch 400 validation mismatch, 401/403 auth issue, 404 route mismatch, 500 unhandled exception." \
  "$(first_existing_file \
    "$AGKIT/.agent/skills/api-patterns/SKILL.md" \
    "$ECC/skills/api-design/SKILL.md")"

import_skill_or_fallback "problem:database-debug" "$ROOT/solo-dev/skills/problem/database-debug/SKILL.md" "database-debug" \
  "database errors, SQL, migrations, transactions, indexes, ORM issues, and data consistency bugs." \
  "1. Identify database and ORM/query layer.
2. Check schema and migration state.
3. Check query correctness.
4. Check transactions.
5. Check performance/indexes.
6. Avoid destructive operations without approval." \
  "- Watch migration drift, missing indexes, wrong relation, rollback risk, data loss." \
  "$(first_existing_file \
    "$ECC/skills/database-migrations/SKILL.md" \
    "$AGKIT/.agent/skills/database-design/SKILL.md" \
    "$CLAUDE_SKILLS/engineering/sql-database-assistant/SKILL.md")"

import_skill_or_fallback "problem:dependency-debug" "$ROOT/solo-dev/skills/problem/dependency-debug/SKILL.md" "dependency-debug" \
  "dependency injection, module resolution, import/export, circular dependency, provider, and package resolution errors." \
  "1. Identify dependency graph.
2. Check import/export boundaries.
3. Check provider/module registration.
4. Check circular dependencies.
5. Check package version mismatch.
6. Fix root cause, not symptoms." \
  "- Watch provider not found, circular import, wrong module export, ESM/CommonJS mismatch." \
  "$(first_existing_file \
    "$CLAUDE_SKILLS/engineering/dependency-auditor/SKILL.md" \
    "$NESTJS_SKILLS/SKILL.md")"

import_skill_or_fallback "problem:build-error" "$ROOT/solo-dev/skills/problem/build-error/SKILL.md" "build-error" \
  "compile errors, bundler errors, TypeScript errors, dependency build failures, and CI build problems." \
  "1. Read first meaningful error.
2. Identify build tool.
3. Check config files.
4. Check dependency versions.
5. Check import paths.
6. Suggest minimal fix." \
  "- Watch tsconfig mismatch, module resolution error, missing env, package version conflict." \
  "$(first_existing_file \
    "$ECC/skills/agent-introspection-debugging/SKILL.md" \
    "$(find_any_doc "$CLAUDE_SKILLS" "*/build*" "*/compile*")")"

import_skill_or_fallback "problem:performance-debug" "$ROOT/solo-dev/skills/problem/performance-debug/SKILL.md" "performance-debug" \
  "slow code, timeouts, high CPU, memory leaks, inefficient queries, and frontend performance issues." \
  "1. Identify symptom.
2. Locate bottleneck.
3. Separate measurement from guess.
4. Optimize highest-impact area.
5. Avoid premature optimization.
6. Suggest benchmark/profiling method." \
  "- Watch N+1 queries, large bundle, unnecessary re-render, memory leak, blocking IO, missing cache." \
  "$(first_existing_file \
    "$AGKIT/.agent/skills/performance-profiling/SKILL.md" \
    "$CLAUDE_SKILLS/engineering/performance-profiler/SKILL.md")"

import_skill_or_fallback "problem:auth-security" "$ROOT/solo-dev/skills/problem/auth-security/SKILL.md" "auth-security" \
  "authentication, authorization, token, session, cookie, permissions, access control, and security-sensitive bugs." \
  "1. Identify auth flow.
2. Check server-side authorization.
3. Check token/session handling.
4. Check cookie security.
5. Check role/permission boundaries.
6. Escalate high-risk changes." \
  "- Watch client-only auth checks, insecure cookies, token leakage, missing permission checks." \
  "$(first_existing_file \
    "$ECC/skills/security-review/SKILL.md" \
    "$AGKIT/.agent/skills/vulnerability-scanner/SKILL.md" \
    "$CLAUDE_SKILLS/engineering-team/senior-security/SKILL.md")"

import_skill_or_fallback "problem:git-workflow" "$ROOT/solo-dev/skills/problem/git-workflow/SKILL.md" "git-workflow" \
  "Git rebase, merge conflicts, detached HEAD, force push, branch recovery, and PR workflow issues." \
  "1. Check branch/status first.
2. Identify operation in progress.
3. Avoid destructive commands first.
4. Preserve work before rewriting history.
5. Use force-with-lease instead of force when needed.
6. Explain recovery path." \
  "- Watch detached HEAD, rebase in progress, unresolved conflict, wrong upstream, unsafe force push." \
  "$(first_existing_file \
    "$ECC/skills/git-workflow/SKILL.md" \
    "$CLAUDE_SKILLS/engineering/git-worktree-manager/SKILL.md")"

import_skill_or_fallback "problem:deployment-debug" "$ROOT/solo-dev/skills/problem/deployment-debug/SKILL.md" "deployment-debug" \
  "deployment, Docker, CI/CD, environment variables, production errors, rollback, and release issues." \
  "1. Identify environment.
2. Check build logs.
3. Check env variables.
4. Check runtime logs.
5. Check rollback path.
6. Require approval for production changes." \
  "- Watch missing env var, build/runtime mismatch, container port mismatch, migration failure, secret exposure." \
  "$(first_existing_file \
    "$ECC/skills/deployment-patterns/SKILL.md" \
    "$AGKIT/.agent/skills/deployment-procedures/SKILL.md" \
    "$VERCEL/skills/deploy-to-vercel/SKILL.md")"

# ==================================================
# 9. Import selective routing/orchestration skills, roles, and workflows
# ==================================================

for d in architecture plan-writing tdd-workflow webapp-testing; do
  mkdirp "$ROOT/solo-dev/skills/task/$d"
done
mkdirp "$ROOT/solo-dev/skills/framework/frontend-design"
for d in intelligent-routing parallel-agents; do
  mkdirp "$ROOT/solo-dev/skills/workflow/$d"
done

import_skill_or_fallback "task:architecture" "$ROOT/solo-dev/skills/task/architecture/SKILL.md" "architecture" \
  "architecture discovery, pattern selection, trade-off analysis, and cross-module design decisions." \
  "1. Discover current architecture.
2. Identify constraints.
3. Compare viable patterns.
4. Select the smallest design that fits.
5. Record trade-offs and verification." \
  "- Do not introduce architecture without a concrete need.
- Preserve existing boundaries where possible." \
  "$AGKIT/.agent/skills/architecture/SKILL.md"

import_skill_or_fallback "task:plan-writing" "$ROOT/solo-dev/skills/task/plan-writing/SKILL.md" "plan-writing" \
  "writing concise implementation plans, task breakdowns, and decision-complete specs." \
  "1. State goal and success criteria.
2. Identify affected areas.
3. Define implementation steps.
4. Define tests and acceptance checks.
5. Capture assumptions." \
  "- Keep plans short and actionable.
- Avoid vague meta-planning." \
  "$AGKIT/.agent/skills/plan-writing/SKILL.md"

import_skill_or_fallback "task:tdd-workflow" "$ROOT/solo-dev/skills/task/tdd-workflow/SKILL.md" "tdd-workflow" \
  "test-first implementation, regression reproduction, and red-green-refactor workflow." \
  "1. Capture behavior as a failing test.
2. Implement the smallest passing change.
3. Refactor safely.
4. Run focused verification." \
  "- Do not over-test internals.
- Keep tests deterministic." \
  "$AGKIT/.agent/skills/tdd-workflow/SKILL.md"

import_skill_or_fallback "task:webapp-testing" "$ROOT/solo-dev/skills/task/webapp-testing/SKILL.md" "webapp-testing" \
  "web application testing, E2E flows, accessibility checks, and browser verification." \
  "1. Identify user flow.
2. Choose unit, integration, or E2E level.
3. Use stable selectors.
4. Cover loading, empty, error, and success states.
5. Verify in browser when relevant." \
  "- Do not claim browser checks ran unless they did.
- Avoid brittle selectors." \
  "$AGKIT/.agent/skills/webapp-testing/SKILL.md"

import_skill_or_fallback "framework:frontend-design" "$ROOT/solo-dev/skills/framework/frontend-design/SKILL.md" "frontend-design" \
  "frontend UI/UX design, responsive layouts, interaction polish, typography, color systems, and visual QA." \
  "1. Identify the user's workflow.
2. Establish hierarchy, spacing, and responsive behavior.
3. Check accessibility and interaction states.
4. Verify layout visually when possible." \
  "- Use domain-appropriate UI density.
- Do not add decorative clutter." \
  "$AGKIT/.agent/skills/frontend-design/SKILL.md"

import_skill_or_fallback "workflow:intelligent-routing" "$ROOT/solo-dev/skills/workflow/intelligent-routing/SKILL.md" "intelligent-routing" \
  "automatic routing to task, stack, problem, role, and workflow capabilities." \
  "1. Detect intent, stack, problem, role, and workflow.
2. Select at most one item per routing category.
3. Prefer active core.
4. Use pack catalogs before leaf inventory." \
  "- Keep entry context lean.
- Do not load every skill or role." \
  "$AGKIT/.agent/skills/intelligent-routing/SKILL.md"

import_skill_or_fallback "workflow:parallel-agents" "$ROOT/solo-dev/skills/workflow/parallel-agents/SKILL.md" "parallel-agents" \
  "coordinating multiple specialist roles for complex tasks, reviews, and cross-domain analysis." \
  "1. Split independent domains.
2. Assign the minimum useful roles.
3. Run discovery first when scope is unknown.
4. Synthesize findings into one actionable result." \
  "- Use only when a single role is insufficient.
- Keep role count small." \
  "$AGKIT/.agent/skills/parallel-agents/SKILL.md"

for role in orchestrator explorer-agent project-planner frontend-specialist backend-specialist qa-automation-engineer security-auditor code-archaeologist devops-engineer database-architect; do
  role_id="${role/-agent/}"
  role_id="${role_id/-specialist/}"
  role_id="${role_id/-engineer/}"
  case "$role" in
    explorer-agent) role_id="explorer" ;;
    project-planner) role_id="project-planner" ;;
    frontend-specialist) role_id="frontend-specialist" ;;
    backend-specialist) role_id="backend-specialist" ;;
    qa-automation-engineer) role_id="qa-automation" ;;
    security-auditor) role_id="security-auditor" ;;
    code-archaeologist) role_id="code-archaeologist" ;;
    devops-engineer) role_id="devops-engineer" ;;
    database-architect) role_id="database-architect" ;;
  esac
  import_active_doc "role:$role_id" "$AGKIT/.agent/agents/$role.md" "$ROOT/team-dev/roles/$role_id.md" "$role_id" \
    "Specialist role for $role_id work. Use in FULL/team mode only when routing selects this role."
done

for wf in plan create debug test preview deploy orchestrate; do
  import_active_doc "workflow:$wf" "$AGKIT/.agent/workflows/$wf.md" "$ROOT/shared/workflows/$wf.md" "$wf" \
    "Portable workflow for $wf requests. Load only when selected by router."
done

import_active_doc "workflow:quality-gate" "$(first_existing_file "$ECC/commands/quality-gate.md" "$ECC/.opencode/commands/quality-gate.md" "$CLAUDE_SKILLS/commands/project-health.md")" "$ROOT/shared/workflows/quality-gate.md" "quality-gate" \
  "Portable verification gate for lint, typecheck, tests, security, coverage, and release readiness."

import_active_doc "workflow:verify" "$(first_existing_file "$ECC/commands/verify.md" "$ECC/.opencode/commands/verify.md" "$CLAUDE_SKILLS/commands/project-health.md")" "$ROOT/shared/workflows/verify.md" "verify" \
  "Portable verification workflow for proving a change works with focused checks and clear residual risk."

import_active_doc "workflow:context-budget" "$(first_existing_file "$ECC/commands/context-budget.md" "$CLAUDE_SKILLS/engineering-team/context-engine/SKILL.md")" "$ROOT/shared/workflows/context-budget.md" "context-budget" \
  "Portable context economy workflow for reducing token usage while preserving routing and task-critical facts."

import_active_doc "workflow:multi-plan" "$(first_existing_file "$ECC/commands/multi-plan.md" "$CLAUDE_SKILLS/docs/orchestration.md")" "$ROOT/shared/workflows/multi-plan.md" "multi-plan" \
  "Portable multi-perspective planning workflow for complex decisions without depending on one IDE or agent runtime."

import_active_doc "workflow:multi-execute" "$(first_existing_file "$ECC/commands/multi-execute.md" "$CLAUDE_SKILLS/docs/orchestration.md")" "$ROOT/shared/workflows/multi-execute.md" "multi-execute" \
  "Portable coordinated execution workflow for independent tasks, role handoffs, and final synthesis."

# ==================================================
# 10. Build skill index
# ==================================================

write_file "$ROOT/shared/registry/SKILL_INDEX.md" "# Skill Index

Read this file first. Load full SKILL.md only after selecting a skill.

## Skills

"

while IFS="|" read -r id dest source_status src; do
  name="$(grep -m1 '^name:' "$dest" 2>/dev/null | sed 's/^name:[ ]*//' || true)"
  desc="$(grep -m1 '^description:' "$dest" 2>/dev/null | sed 's/^description:[ ]*//' || true)"
  [ -z "$name" ] && name="$id"
  [ -z "$desc" ] && desc="Use for $id."
  {
    echo "- $id"
    echo "  - name: $name"
    echo "  - path: $dest"
    echo "  - source: $source_status"
    echo "  - description: $desc"
    echo ""
  } >> "$ROOT/shared/registry/SKILL_INDEX.md"
done < "$ROOT/shared/registry/imported-skills.tsv"

# ==================================================
# 10. Ultra router: QUICK/HYBRID/FULL + language
# ==================================================

write_file "$ROOT/shared/router/LANGUAGE_ROUTER.md" "# Language Router

This rule is mandatory.

For every request:

1. Detect the user's primary language.
2. If not English:
   - internally translate only routing-relevant phrases into English
   - use that English meaning to map intent, mode, role, skill, workflow, risk
3. Keep code, logs, stack traces, commands, paths, package names, APIs, identifiers unchanged.
4. Final answer must be in the same primary language as the user's latest request, unless explicitly requested otherwise.

Do not expose internal translation unless the user asks.
"

write_file "$ROOT/shared/router/MODE_ROUTER.md" "# Mode Router

Use QUICK / HYBRID / FULL before deciding solo-dev or team-dev.

## QUICK

Use when:
- one file
- isolated change
- no cross-layer effect
- no architecture decision
- low risk
- requirement is clear

Behavior:
- solo-dev
- minimal diff
- no long plan
- no team simulation

## HYBRID

Use when:
- 2-3 files
- one layer only
- clear change
- low to medium risk
- may need short review gate

Behavior:
- solo-dev with compact review
- short plan
- selected skills only

## FULL

Use when:
- many files
- cross-layer
- new screen/service/API/module
- architecture decision
- unclear scope
- production/security/data/deployment risk

Behavior:
- team-dev
- selected roles only
- planning + review gates
"

write_file "$ROOT/shared/router/ROUTER.md" "# Router

## Mandatory order

1. Use LANGUAGE_ROUTER.
2. Use MODE_ROUTER to select QUICK / HYBRID / FULL.
3. Respect explicit user request:
   - if user says solo-dev, avoid FULL unless high-risk
   - if user says team-dev, use FULL or HYBRID-team depending on scope
4. Detect intent.
5. Detect stack.
6. Detect problem.
7. Detect optional workflow and role.
8. Read SKILL_INDEX.
9. Select:
   - max 1 task skill
   - max 1 stack skill: language or framework
   - max 1 problem skill
   - max 1 role for FULL/team mode
   - optional workflow
10. If request says plan, orchestrate, team, multi-agent, review, test, preview, quality gate, verify, or context budget, inspect workflow/role packs before leaf inventory.
11. If no active core item fits, inspect relevant packs/*/catalog.json.
12. Load leaf inventory item only after pack catalog selection.
13. Load full SKILL.md or active role/workflow only after selection.

## Intent list

- bug_fix
- feature_dev
- refactor
- code_review
- testing
- documentation
- architecture
- product_planning
- incident_debug
- security_review
- deployment
- orchestration
- preview
- quality_gate
- context_budget
- legacy_discovery

## Overengineering guard

Default to QUICK when safe.
Use HYBRID when change touches a few files but remains one layer.
Use FULL only when scope/risk requires it.
"

write_file "$ROOT/shared/router/STACK_DETECTOR.md" "# Stack Detector

Lean rule: prefer shared/router/STACK_KEYWORDS.json when available.
Use this file only as human fallback.
"

write_file "$ROOT/shared/router/PROBLEM_DETECTOR.md" "# Problem Detector

Lean rule: prefer shared/router/PROBLEM_KEYWORDS.json when available.
Use this file only as human fallback.
"

# ==================================================
# 11. Core rules and entry
# ==================================================

write_file "$ROOT/solo-dev/rules/CORE.md" "# Solo Core Rules

1. Inspect before editing.
2. Minimal diff by default.
3. Do not invent files, APIs, libraries, command outputs, or test results.
4. Use QUICK/HYBRID unless FULL is required.
5. Select skills by metadata first; load full SKILL.md only when selected.
6. For risky/destructive actions, request approval.
7. Reply in the user's latest primary language.
8. Keep code/logs/commands/paths/package names unchanged.
9. If context was compacted or behavior drifts, run SELF_CHECK.
"

write_file "$ROOT/solo-dev/rules/SELF_CHECK.md" "# SELF_CHECK

Run when context is compacted, task changes, or behavior drifts.

Check:
1. Is current mode QUICK / HYBRID / FULL correct?
2. Is output language same as user's latest primary language?
3. Did I translate only routing signals internally?
4. Did I preserve code/logs/commands/paths/package names?
5. Is selected task/stack/problem skill correct?
6. Is this action high-risk/destructive?
7. Am I following minimal diff?
8. Did I claim anything unverified?

If failed:
- restate routing decision
- reload AI_ENTRY.md
- continue with smallest sufficient context
"

write_file "$ROOT/solo-dev/rules/PROMPT_ECONOMY.md" "# Prompt Economy

1. Use AI_ENTRY.md first.
2. Use SKILL_INDEX before full skills.
3. Do not load all roles or all skills.
4. Prefer path references over pasted content.
5. Keep routing decision short.
6. Only use FULL if it adds value.
"

write_file "$ROOT/AI_ENTRY.md" "# AI_ENTRY

Lean default entry. Keep initial context near 1-2k tokens.

## Load order

1. shared/router/LANGUAGE_ROUTER.md
2. shared/router/MODE_ROUTER.md
3. shared/router/ROUTER.md
4. shared/registry/SKILL_INDEX.md
5. solo-dev/rules/CORE.md
6. selected SKILL.md only
7. Optional selected role/workflow only when routed
8. If no active skill fits: search shared/registry/catalog.json or relevant packs/*/catalog.json
9. solo-dev/rules/SELF_CHECK.md when context is compacted or drifting

## Decision

Choose one:

- QUICK: one file, isolated change, no architecture, low risk
- HYBRID: 2-3 files, one layer, clear change, low/medium risk
- FULL: many files, cross-layer, new screen/service/API, architecture, unclear scope, production/security/data/deployment risk

## Mapping

- QUICK -> solo-dev
- HYBRID -> solo-dev + compact review
- FULL -> team-dev with selected roles only

## Team / workflow routing

- Select at most 1 role: orchestrator, explorer, frontend, backend, database, QA, security, DevOps, or legacy discovery.
- Select at most 1 workflow: plan, create, debug, test, preview, deploy, orchestrate, quality-gate, verify, context-budget, multi-plan, or multi-execute.
- Use packs/roles, packs/workflows, and packs/rules only after active core is insufficient.

## Behavior

- Default to QUICK when safe.
- Do not over-engineer.
- Select skills by metadata first.
- Load full skill, role, or workflow only when selected.
- Prefer active core. Use pack catalog before leaf inventory.
- Always answer in the user's latest primary language.
- Keep code, logs, commands, paths, package names, and APIs unchanged.

## Default output

1. Mode: QUICK / HYBRID / FULL
2. Routing: selected skills/roles
3. Plan or root cause
4. Action / implementation
5. Verification
6. Risk
"

write_file "$ROOT/solo-dev/AI_DEV.md" "# AI_DEV

Use AI_ENTRY.md.

Solo-dev means:
- QUICK by default
- HYBRID if small multi-file but one-layer
- minimal diff
- selected skills only
- no team simulation
"

write_file "$ROOT/team-dev/AI_TEAM.md" "# AI_TEAM

Use AI_ENTRY.md with FULL mode.

Use FULL only for:
- product planning
- architecture
- multi-component features
- release
- production incidents
- security-sensitive work
- data/destructive/deployment changes

Select only needed roles.
Do not simulate a full team unless required.
"

# ==================================================
# 12. Team orchestration
# ==================================================

write_file "$ROOT/team-dev/orchestration/AGENT_SELECTION.md" "# Agent Selection

| Situation | Roles |
|---|---|
| PRD / MVP / scope | Product Manager, Tech Lead |
| Architecture | Architect, Tech Lead, Security Reviewer if risk exists |
| Backend feature | Tech Lead, Backend Engineer, QA |
| Frontend feature | Tech Lead, Frontend Engineer, QA |
| Fullstack feature | Tech Lead, Backend Engineer, Frontend Engineer, QA |
| Production incident | Tech Lead, DevOps, Relevant Engineer, Security Reviewer |
| Security-sensitive | Security Reviewer, Relevant Engineer |
"

write_file "$ROOT/team-dev/orchestration/CONTEXT_LOADING.md" "# Context Loading

1. Start with AI_ENTRY.md.
2. Read registry/index before full files.
3. Load selected roles only.
4. Load selected skills only.
5. Load selected workflows/checklists only.
6. Never load the whole system unless maintaining the framework.
"

write_file "$ROOT/team-dev/protocols/REVIEW_GATES.md" "# Review Gates

1. Requirement clarity
2. Architecture sanity
3. Implementation correctness
4. Test coverage
5. Security review
6. Release readiness
"

write_file "$ROOT/team-dev/governance/HUMAN_APPROVAL.md" "# Human Approval

Require approval for:

1. Data deletion
2. Production deployment
3. Auth/security changes
4. Payment/billing logic
5. Destructive shell commands
6. Database migrations that can lose data
7. Force push or history rewrite
"

write_file "$ROOT/team-dev/quality/CODE_REVIEW.md" "# Code Review Checklist

1. Correctness
2. Edge cases
3. Error handling
4. Security
5. Maintainability
6. Performance
7. Tests
"

write_file "$ROOT/team-dev/quality/SECURITY.md" "# Security Checklist

1. No hardcoded secrets
2. No token leaks
3. Validate external input
4. Server-side auth checks
5. Least privilege
6. Rate limit when needed
7. Safe logging
"

for role in product-manager architect tech-lead backend-engineer frontend-engineer qa-engineer security-reviewer devops-engineer reviewer; do
  if [ -f "$ROOT/team-dev/roles/$role.md" ]; then
    log "KEEPING IMPORTED ROLE: $ROOT/team-dev/roles/$role.md"
    continue
  fi
  write_file "$ROOT/team-dev/roles/$role.md" "# $role

Use only when selected by AI_ENTRY.md in FULL mode.

Responsibilities:
- stay within role scope
- produce actionable output
- avoid unrelated work
- hand off clearly
"
done

# ==================================================
# 13. Workflows / commands / packs
# ==================================================

write_file "$ROOT/solo-dev/workflows/QUICK.md" "# QUICK Workflow

1. Confirm isolated scope.
2. Select skill.
3. Make minimal change.
4. Verify.
5. Report risk.
"

write_file "$ROOT/solo-dev/workflows/HYBRID.md" "# HYBRID Workflow

1. Confirm 2-3 files / one layer.
2. Select task + stack/problem skills.
3. Make compact plan.
4. Implement.
5. Run compact review.
6. Verify.
"

write_file "$ROOT/team-dev/workflows/FULL.md" "# FULL Workflow

1. Clarify goal.
2. Select roles.
3. Plan architecture/scope.
4. Split tasks.
5. Apply review gates.
6. Verify and summarize risk.
"

write_file "$ROOT/shared/commands/quick.md" "# /quick

Entry:
- AI_ENTRY.md

Force preference:
- QUICK unless risk requires escalation.
"

write_file "$ROOT/shared/commands/hybrid.md" "# /hybrid

Entry:
- AI_ENTRY.md

Use HYBRID for 2-3 files, one layer, clear scope.
"

write_file "$ROOT/shared/commands/full.md" "# /full

Entry:
- AI_ENTRY.md

Use FULL for architecture, multi-component, production, security, data, deployment, or unclear scope.
"

for pack in frontend backend fullstack product security devops testing; do
  write_file "$ROOT/packs/$pack/README.md" "# $pack Pack

Use when work focuses on $pack.

Entry:
- AI_ENTRY.md

Rule:
Route first. Load selected skills only.
"
done

# ==================================================
# 14. Adapters
# ==================================================

write_file "$ROOT/solo-dev/adapters/claude/CLAUDE.md" "# Claude Adapter

Use ai-dev-system.

Primary entry:
- AI_ENTRY.md

Important:
- QUICK / HYBRID / FULL first.
- Do not load all files.
- Read SKILL_INDEX before full skills.
- Load selected skill only.
- Use LANGUAGE_ROUTER.
- Reply in the user's latest primary language.
- Run SELF_CHECK if context was compacted or behavior drifts.
"

write_file "$ROOT/solo-dev/adapters/cursor/.cursorrules" "Use ai-dev-system.

Primary entry:
AI_ENTRY.md

Rules:
- choose QUICK / HYBRID / FULL first
- use LANGUAGE_ROUTER
- use SKILL_INDEX before full skills
- selected skills only
- minimal diff
- no invented files/APIs
- answer in user language
- run SELF_CHECK after compaction or drift
"

write_file "$ROOT/solo-dev/adapters/chatgpt/project-instructions.md" "Use ai-dev-system.

Primary entry:
- AI_ENTRY.md

Rules:
- choose QUICK / HYBRID / FULL first
- use LANGUAGE_ROUTER
- answer in user's latest primary language
- keep code/logs/commands/paths/package names unchanged
- route, select skills, then execute with minimal context
"

write_file "$ROOT/solo-dev/adapters/cline/custom-instructions.md" "Use ai-dev-system via AI_ENTRY.md.
Route QUICK / HYBRID / FULL first.
Use LANGUAGE_ROUTER.
Load selected skills only.
Avoid overengineering.
"

write_file "$ROOT/solo-dev/adapters/gemini/GEMINI.md" "# Gemini Adapter

Use AI_ENTRY.md as the main entry.
Choose QUICK / HYBRID / FULL first.
Use LANGUAGE_ROUTER and answer in the user's latest primary language.
"

write_file "$ROOT/solo-dev/adapters/continue/config.yaml" "name: ai-dev-system
entry: AI_ENTRY.md
rules:
  - choose quick hybrid full first
  - route first
  - use language router
  - answer in user language
  - use skill index
  - selected skills only
  - minimal diff
  - self check after compaction
"

write_file "$ROOT/solo-dev/adapters/copilot/copilot-instructions.md" "Use ai-dev-system via AI_ENTRY.md.

Rules:
- choose QUICK / HYBRID / FULL first
- use SKILL_INDEX before full skills
- load selected skills only
- answer in user's latest primary language
- keep code/logs/commands unchanged
"

# ==================================================
# 15. Installer and single command CLI
# ==================================================

write_file "$ROOT/shared/scripts/install-project.sh" '#!/bin/zsh

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

PROFILE="$PROJECT_ROOT/.ai-dev-system/project-profile.md"

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

cat > "$PROFILE" <<EOF
# AI Dev System Project Profile

## Detected stacks

${STACKS[@]}

## Detected frameworks/tools

${FRAMEWORKS[@]}

## Entry

- AI_ENTRY.md

## Usage

Use ai-dev-system.
Route QUICK / HYBRID / FULL first, then execute.

## Context rule

Do not load all files.
Use LANGUAGE_ROUTER.
Use SKILL_INDEX first.
Load selected skills only.
Run SELF_CHECK after compaction.
EOF

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

echo "Installed ai-dev-system adapter: $TOOL"
echo "Project profile: $PROFILE"
'

chmod +x "$ROOT/shared/scripts/install-project.sh"

write_file "$ROOT/bin/ai-dev" '#!/bin/zsh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYSTEM_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cmd="${1:-help}"

case "$cmd" in
  install)
    project="${2:-.}"
    tool="${3:-all}"
    "$SYSTEM_ROOT/shared/scripts/install-project.sh" "$SYSTEM_ROOT" "$project" "$tool"
    ;;
  doctor)
    "$SYSTEM_ROOT/shared/scripts/doctor.sh" "$SYSTEM_ROOT"
    ;;
  entry)
    mode="${2:-lean}"
    case "$mode" in
      lean)
        echo "$SYSTEM_ROOT/AI_ENTRY.md"
        ;;
      team)
        echo "$SYSTEM_ROOT/team-dev/AI_TEAM.md"
        ;;
      full)
        echo "$SYSTEM_ROOT/team-dev/workflows/FULL.md"
        ;;
      *)
        echo "Usage: ai-dev entry [lean|team|full]"
        exit 1
        ;;
    esac
    ;;
  refresh-catalog)
    repos="${2:-$SYSTEM_ROOT/../ai-repos}"
    "$SYSTEM_ROOT/shared/scripts/refresh-registry.sh" "$SYSTEM_ROOT" "$repos"
    python3 "$SYSTEM_ROOT/shared/scripts/ai-dev-registry.py" eval --root "$SYSTEM_ROOT"
    ;;
  search-skill)
    query="${2:-}"
    if [ -z "$query" ]; then
      echo "Usage: ai-dev search-skill \"query\""
      exit 1
    fi
    python3 "$SYSTEM_ROOT/shared/scripts/ai-dev-registry.py" search --root "$SYSTEM_ROOT" --query "$query"
    ;;
  search-role)
    query="${2:-}"
    if [ -z "$query" ]; then
      echo "Usage: ai-dev search-role \"query\""
      exit 1
    fi
    python3 "$SYSTEM_ROOT/shared/scripts/ai-dev-registry.py" search --root "$SYSTEM_ROOT" --query "$query" --type agent
    ;;
  search-workflow)
    query="${2:-}"
    if [ -z "$query" ]; then
      echo "Usage: ai-dev search-workflow \"query\""
      exit 1
    fi
    python3 "$SYSTEM_ROOT/shared/scripts/ai-dev-registry.py" search --root "$SYSTEM_ROOT" --query "$query" --type workflow
    ;;
  eval-routing)
    python3 "$SYSTEM_ROOT/shared/scripts/ai-dev-registry.py" eval --root "$SYSTEM_ROOT"
    ;;
  help|*)
    echo "ai-dev commands:"
    echo "  ai-dev install /path/to/project [claude|cursor|chatgpt|copilot|all]"
    echo "  ai-dev doctor"
    echo "  ai-dev entry [lean|team|full]"
    echo "  ai-dev refresh-catalog [path/to/ai-repos]"
    echo "  ai-dev search-skill \"query\""
    echo "  ai-dev search-role \"query\""
    echo "  ai-dev search-workflow \"query\""
    echo "  ai-dev eval-routing"
    ;;
esac
'

chmod +x "$ROOT/bin/ai-dev"

# ==================================================
# 16. Doctor
# ==================================================

write_file "$ROOT/shared/scripts/doctor.sh" '#!/bin/zsh

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
  "shared/router/STACK_KEYWORDS.json"
  "shared/router/PROBLEM_KEYWORDS.json"
  "shared/evaluation/routing-eval.json"
  "shared/registry/imported-skills.tsv"
  "packs/workflows/catalog.json"
  "packs/roles/catalog.json"
  "packs/rules/catalog.json"
  "shared/scripts/install-project.sh"
  "shared/scripts/refresh-registry.sh"
  "shared/scripts/ai-dev-registry.py"
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
'

chmod +x "$ROOT/shared/scripts/doctor.sh"

copy_file "ai-dev-registry.py" "$ROOT/shared/scripts/ai-dev-registry.py" || true
copy_file "refresh-ai-dev-skill-index.sh" "$ROOT/shared/scripts/refresh-registry.sh" || true
chmod +x "$ROOT/shared/scripts/refresh-registry.sh" 2>/dev/null || true
chmod +x "$ROOT/shared/scripts/ai-dev-registry.py" 2>/dev/null || true

if [ -f "$ROOT/shared/scripts/refresh-registry.sh" ]; then
  AI_DEV_ROOT="$ROOT" AI_DEV_REPOS="$REPOS" "$ROOT/shared/scripts/refresh-registry.sh"
  python3 "$ROOT/shared/scripts/ai-dev-registry.py" eval --root "$ROOT"
fi

"$ROOT/shared/scripts/doctor.sh" "$ROOT"

echo ""
echo "=================================================="
echo "DONE"
echo "Created: $ROOT"
echo "Repos:   $REPOS"
echo "=================================================="
echo ""
echo "One-command project install:"
echo "  $ROOT/bin/ai-dev install /path/to/project all"
echo ""
echo "Main entry:"
echo "  $ROOT/AI_ENTRY.md"
echo ""
echo "Prompt:"
echo "  Use ai-dev-system. Route QUICK / HYBRID / FULL first, then execute."
