#!/usr/bin/env bash
# §8.62 C10 收尾：从 git log 自动生成 CHANGELOG.md（基于 Conventional Commits）
# 用法：bash sites-hub/scripts/build-changelog.sh [since-tag]
#   since-tag：起始 tag/branch（默认上一次 release tag，或 "v1.0"）
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

SINCE="${1:-}"
if [ -z "$SINCE" ]; then
  # 尝试找最新 tag
  SINCE=$(git tag --sort=-creatordate 2>/dev/null | head -1 || true)
fi
if [ -z "$SINCE" ]; then
  # 兜底：第一个 commit
  SINCE=$(git log --reverse --pretty=format:"%H" | head -1)
  if [ -z "$SINCE" ]; then
    SINCE="HEAD"
  fi
fi

OUTPUT="$ROOT/CHANGELOG.md"
TODAY=$(date +%Y-%m-%d)
TOTAL=$(git rev-list --count "${SINCE}..HEAD" 2>/dev/null || echo 0)

echo "生成 CHANGELOG：since=$SINCE, total commits=$TOTAL"

# 解析 Conventional Commits
FEAT=$(git log --pretty=format:"%s" "${SINCE}..HEAD" 2>/dev/null | grep -E "^feat(\(.*\))?:" | sed 's/^/  - /' || true)
FIX=$(git log --pretty=format:"%s" "${SINCE}..HEAD" 2>/dev/null | grep -E "^fix(\(.*\))?:" | sed 's/^/  - /' || true)
DOCS=$(git log --pretty=format:"%s" "${SINCE}..HEAD" 2>/dev/null | grep -E "^docs(\(.*\))?:" | sed 's/^/  - /' || true)
REFACTOR=$(git log --pretty=format:"%s" "${SINCE}..HEAD" 2>/dev/null | grep -E "^refactor(\(.*\))?:" | sed 's/^/  - /' || true)
CHORE=$(git log --pretty=format:"%s" "${SINCE}..HEAD" 2>/dev/null | grep -E "^chore(\(.*\))?:" | sed 's/^/  - /' || true)
PERF=$(git log --pretty=format:"%s" "${SINCE}..HEAD" 2>/dev/null | grep -E "^perf(\(.*\))?:" | sed 's/^/  - /' || true)
OTHER=$(git log --pretty=format:"%s" "${SINCE}..HEAD" 2>/dev/null | grep -vE "^(feat|fix|docs|refactor|chore|perf)(\(.*\))?:" | sed 's/^/  - /' || true)

section() {
  local title="$1"
  local content="$2"
  if [ -n "$content" ]; then
    echo "### $title"
    echo ""
    echo "$content"
    echo ""
  fi
}

{
  echo "# CHANGELOG"
  echo ""
  echo "> 自动生成 by \`sites-hub/scripts/build-changelog.sh\`"
  echo "> 范围：\`${SINCE}..HEAD\` · 共 $TOTAL 个 commit"
  echo "> 生成时间：$TODAY"
  echo ""
  section "✨ Features" "$FEAT"
  section "🐛 Bug Fixes" "$FIX"
  section "⚡ Performance" "$PERF"
  section "♻️ Refactor" "$REFACTOR"
  section "📚 Documentation" "$DOCS"
  section "🔧 Chore" "$CHORE"
  if [ -n "$OTHER" ]; then
    section "📦 Other" "$OTHER"
  fi
  echo "---"
  echo ""
  echo "**说明**：基于 Conventional Commits（feat/fix/docs/refactor/chore/perf）自动分类。"
  echo "Updates 列表（首页）仅展示 \`feat\` / \`fix\` / \`refactor\`。"
} > "$OUTPUT"

echo "✓ CHANGELOG.md written"
echo "  Feat: $(echo "$FEAT" | grep -c "^  - ")"
echo "  Fix:  $(echo "$FIX" | grep -c "^  - ")"
echo "  Docs: $(echo "$DOCS" | grep -c "^  - ")"
