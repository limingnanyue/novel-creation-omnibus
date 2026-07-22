#!/usr/bin/env bash
set -euo pipefail

# 鲁班过尺·结构尺(固化版):检查一个本地路径或 GitHub 仓库的发布就绪度。
# 源自 LearnPrompt/luban-skill (https://github.com/LearnPrompt/luban-skill)
# 自托管副本:让本项目可独立体检,不依赖外部 luban 仓库路径。
# Usage: check-skill-repo.sh <target-repo-path-or-github-url>

if [[ $# -lt 1 ]]; then
  echo "Usage: $(basename "$0") <target-repo-path-or-github-url>"
  exit 1
fi

INPUT="$1"
TMP_DIR=""
SOURCE_IS_GITHUB=0
PASS_COUNT=0
WARN_COUNT=0
FAIL_COUNT=0

cleanup() {
  if [[ -n "$TMP_DIR" && -d "$TMP_DIR" ]]; then
    rm -rf "$TMP_DIR"
  fi
}
trap cleanup EXIT

pass() {
  echo "PASS $1"
  PASS_COUNT=$((PASS_COUNT + 1))
}

warn() {
  echo "WARN $1"
  WARN_COUNT=$((WARN_COUNT + 1))
}

fail() {
  echo "FAIL $1"
  FAIL_COUNT=$((FAIL_COUNT + 1))
}

is_github_target() {
  [[ "$1" =~ ^https://github\.com/[^/]+/[^/]+/?$ ]] ||
    [[ "$1" =~ ^https://github\.com/[^/]+/[^/]+\.git$ ]] ||
    [[ "$1" =~ ^git@github\.com:[^/]+/[^/]+\.git$ ]] ||
    [[ "$1" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]]
}

to_clone_url() {
  local value="$1"
  if [[ "$value" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]]; then
    printf 'https://github.com/%s.git' "$value"
  elif [[ "$value" =~ ^https://github\.com/.+/.+[^.]$ ]]; then
    printf '%s.git' "${value%/}"
  else
    printf '%s' "$value"
  fi
}

resolve_target() {
  local value="$1"

  if [[ -d "$value" ]]; then
    (cd "$value" && pwd)
    return 0
  fi

  if is_github_target "$value"; then
    local clone_url
    clone_url="$(to_clone_url "$value")"
    TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/skill-miniloop.XXXXXX")"
    if git clone --depth 1 --quiet "$clone_url" "$TMP_DIR/repo" 2>"$TMP_DIR/clone.err"; then
      SOURCE_IS_GITHUB=1
      (cd "$TMP_DIR/repo" && pwd)
      return 0
    fi
    fail "could not clone GitHub target: $value"
    sed 's/^/WARN git clone: /' "$TMP_DIR/clone.err" || true
    echo ""
    echo "--- Summary ---"
    echo "PASS: $PASS_COUNT"
    echo "WARN: $WARN_COUNT"
    echo "FAIL: $FAIL_COUNT"
    exit 1
  fi

  fail "target path does not exist and input is not a supported GitHub target: $value"
  echo ""
  echo "--- Summary ---"
  echo "PASS: $PASS_COUNT"
  echo "WARN: $WARN_COUNT"
  echo "FAIL: $FAIL_COUNT"
  exit 1
}

find_skill_files() {
  local root="$1"
  find "$root" \
    \( -path '*/.git' -o -path '*/node_modules' -o -path '*/vendor' -o -path '*/.venv' -o -path '*/__pycache__' \) -prune \
    -o -name 'SKILL.md' -type f -maxdepth 6 -print 2>/dev/null | sort
}

contains_any() {
  local file="$1"
  local pattern="$2"
  [[ -f "$file" ]] && grep -qiE "$pattern" "$file" 2>/dev/null
}

TARGET="$(resolve_target "$INPUT")"
TARGET="$(cd "$TARGET" && pwd)"
README="$TARGET/README.md"

if [[ "$SOURCE_IS_GITHUB" -eq 1 ]] || is_github_target "$INPUT"; then
  pass "target source is GitHub URL; cloned shallow copy for local inspection"
fi

if [[ -f "$README" ]]; then
  pass "README.md exists"
else
  fail "README.md does not exist at repository root"
fi

SKILL_FILES="$(find_skill_files "$TARGET" || true)"
SKILL_COUNT="$(printf '%s\n' "$SKILL_FILES" | sed '/^$/d' | wc -l | tr -d ' ')"
PRIMARY_SKILL=""

if [[ "$SKILL_COUNT" -gt 0 ]]; then
  PRIMARY_SKILL="$(printf '%s\n' "$SKILL_FILES" | sed '/^$/d' | head -1)"
  PRIMARY_REL="${PRIMARY_SKILL#"$TARGET/"}"
  if [[ "$PRIMARY_REL" == "SKILL.md" ]]; then
    pass "SKILL.md exists at repository root"
  else
    pass "SKILL.md exists in subdirectory (${PRIMARY_REL}); nested skill repos are supported"
  fi
  if [[ "$SKILL_COUNT" -gt 1 ]]; then
    warn "multiple SKILL.md files found (${SKILL_COUNT}); use the report to choose the primary skill"
  fi
else
  fail "SKILL.md does not exist in root or scanned subdirectories"
fi

if [[ -d "$TARGET/examples" ]]; then
  if find "$TARGET/examples" -type f -not -name '.DS_Store' -print -quit 2>/dev/null | grep -q .; then
    pass "examples/ directory exists with at least one file"
  else
    warn "examples/ directory exists but appears empty"
  fi
elif [[ -f "$README" ]] && contains_any "$README" 'sample|example|demo|示例|样例|演示'; then
  warn "examples/ directory not found, but README mentions sample/demo/example"
else
  fail "examples/ directory not found and no sample/demo/example references in README"
fi

if [[ -d "$TARGET/scripts" ]]; then
  if find "$TARGET/scripts" -type f \( -name '*.sh' -o -perm -111 \) -print -quit 2>/dev/null | grep -q .; then
    pass "scripts/ directory exists with runnable script candidates"
  else
    warn "scripts/ directory exists but no runnable script candidates were found"
  fi
elif [[ -f "$README" ]] && contains_any "$README" '```(bash|sh)|npm run|pnpm|yarn|python |uv run|make |bash |sh '; then
  warn "scripts/ directory not found, but README mentions run commands"
else
  fail "scripts/ directory not found and no run commands referenced in README"
fi

if [[ -f "$README" ]]; then
  if contains_any "$README" 'Quick.?Start|快速开始|Install|安装|Setup|Run|运行|Usage|Verify|验证|Expected.?Output|预期输出'; then
    pass "README contains instructional keywords in English or Chinese"
  else
    fail "README missing instructional keywords (Quick Start, Install, Run, Verify, Expected Output)"
  fi

  if grep -qE '```(bash|sh|shell|zsh)' "$README" 2>/dev/null; then
    pass "README contains runnable shell code blocks"
  else
    warn "README missing shell code blocks"
  fi
fi

if [[ -n "$PRIMARY_SKILL" && -f "$PRIMARY_SKILL" ]]; then
  if contains_any "$PRIMARY_SKILL" 'trigger|触发|when to use|什么时候|workflow|工作流|input|输入|output|输出|safety|安全|do not|不要'; then
    pass "SKILL.md contains agent-facing workflow keywords"
  else
    fail "SKILL.md missing agent-facing workflow keywords"
  fi
fi

if find "$TARGET" \
  \( -path '*/.git' -o -path '*/node_modules' -o -path '*/vendor' \) -prune \
  -o \( -name '.env' -o -name '*.pem' -o -name 'id_rsa' -o -name '*token*' \) -type f -print -quit 2>/dev/null | grep -q .; then
  warn "potential secret-like files found; report does not read file contents"
else
  pass "no obvious secret-like files found in scanned paths"
fi

echo ""
echo "--- 出生证(birth-checklist) ---"

if [[ -f "$TARGET/LICENSE" || -f "$TARGET/LICENSE.md" ]]; then
  pass "LICENSE exists"
else
  warn "LICENSE missing (默认 MIT)"
fi

if [[ -f "$TARGET/.claude-plugin/marketplace.json" ]]; then
  pass ".claude-plugin/marketplace.json exists (plugin marketplace 双通道)"
else
  warn ".claude-plugin/marketplace.json missing"
fi

if find "$TARGET" -maxdepth 3 \( -path '*/.git' -o -path '*/node_modules' \) -prune \
  -o \( -name '*.gif' -o -name '*.mp4' -o -name '*.webm' \) -type f -print -quit 2>/dev/null | grep -q .; then
  pass "demo 视觉产物存在 (gif/mp4)"
  if find "$TARGET" -maxdepth 3 \( -path '*/.git' -o -path '*/node_modules' \) -prune \
    -o -name '*.tape' -type f -print -quit 2>/dev/null | grep -q .; then
    pass "demo 录制脚本入库 (vhs tape, showcase 可复现)"
  else
    warn "有 demo 但缺录制脚本 (*.tape) —— showcase 应可复现"
  fi
else
  warn "缺 demo GIF/视频 —— 产物前置是首屏信任的核心"
fi

if [[ -f "$README" ]] && grep -q 'npx skills add' "$README" 2>/dev/null; then
  pass "README 含一行安装 (npx skills add)"
else
  warn "README 缺 npx skills add 一行安装"
fi

if [[ -f "$README" ]] && grep -q 'skills\.sh/b/' "$README" 2>/dev/null; then
  pass "README 含 skills.sh 安装计数徽章"
else
  warn "README 缺 skills.sh 徽章 (https://skills.sh/b/owner/repo)"
fi

echo ""
echo "--- Summary ---"
echo "PASS: $PASS_COUNT"
echo "WARN: $WARN_COUNT"
echo "FAIL: $FAIL_COUNT"

if [[ "$FAIL_COUNT" -gt 0 ]]; then
  exit 1
fi
