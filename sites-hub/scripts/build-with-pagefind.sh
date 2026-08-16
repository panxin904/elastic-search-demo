#!/usr/bin/env bash
# build-with-pagefind.sh — 28 站统一 build + Pagefind 索引（C4）
#
# 用法：
#   bash sites-hub/scripts/build-with-pagefind.sh           # 全 28 站
#   bash sites-hub/scripts/build-with-pagefind.sh ai kafka  # 指定子站
#
# 流程：每个子站 docs:build → pagefind 索引 → 输出到 .vitepress/dist/pagefind/
set -euo pipefail

# 加载 SITES 列表
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
source "$ROOT/sites-hub/scripts/sites.sh"

# 解析参数：可用站点 / 默认全部
if [[ $# -gt 0 ]]; then
  TARGETS=("$@")
else
  TARGETS=("${SITES[@]}")
fi

for site in "${TARGETS[@]}"; do
  project="$(site_to_project "$site")"
  project_dir="$ROOT/$project"
  
  if [[ ! -d "$project_dir" ]]; then
    echo "⚠️  $site → $project 不存在，跳过"
    continue
  fi
  
  echo ""
  echo "═══ $site ($project) ═══"
  cd "$project_dir"
  
  # 检查 node_modules
  if [[ ! -d "node_modules" ]]; then
    echo "  📦 npm install..."
    npm install --silent
  fi
  
  # VitePress build
  echo "  🏗️  vitepress build..."
  npm run docs:build 2>&1 | tail -3
  
  # Pagefind 索引
  if [[ -d ".vitepress/dist" ]]; then
    echo "  🔍 pagefind index..."
    npx pagefind --site .vitepress/dist 2>&1 | tail -5
  else
    echo "  ⚠️  .vitepress/dist 不存在，跳过 pagefind"
  fi
done

echo ""
echo "✅ 构建完成。可访问 https://java-px.bot.cd/<site>/ 验证 Pagefind UI（搜索框）"
