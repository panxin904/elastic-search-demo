#!/usr/bin/env bash
# sites-hub/scripts/spell-check.sh
# 拼写检查 (codespell)
# 跳过: node_modules / .vitepress / dist / release / public / package-lock.json / 二进制
# 用法: bash sites-hub/scripts/spell-check.sh [--fix]

set -eo pipefail
CODESPELL="${CODESPELL:-/Users/a1111/Library/Python/3.9/bin/codespell}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

EXTRA_ARGS=()
if [[ "${1:-}" == "--fix" ]]; then
  EXTRA_ARGS+=("--write-changes")
fi

# 跳过列表（glob 模式）
SKIP='*.json,*.lock,*.yaml,*.yml,*.ts,*.mts,*.mjs,*.pyc,*.png,*.jpg,*.jpeg,*.svg,*.woff,*.woff2,*.ico,*.gif,*.webp,*.tar.gz,*.zip'

# 项目白名单（专有名词、技术词、缩写）
IGNORE_FILE="$ROOT/sites-hub/scripts/.codespell-ignore"
[[ -f "$IGNORE_FILE" ]] || touch "$IGNORE_FILE"

# 用目录方式传给 codespell（避免 ARG_MAX）
# codespell 会自动递归子目录 + 用 --skip 排除
cd "$ROOT"

# 项目实际可扫的目录（不含 node_modules / .vitepress / dist / release / .git）
TARGETS=(
  ai-html/docs
  architecture-html/docs
  bigdata-html/docs
  chaos-html/docs
  clickhouse-html/docs
  cloud-html/docs
  cloud-native-html/docs
  design-pattern-html/docs
  devops-html/docs
  es-html/docs
  filesystem-html/docs
  frontend-html/docs
  go-html/docs
  java-html/docs
  java-language-html/docs
  kafka-html/docs
  linux-html/docs
  mysql-html/docs
  network-html/docs
  observability-html/docs
  postgresql-html/docs
  python-html/docs
  redis-html/docs
  rust-html/docs
  security-html/docs
  system-design-html/docs
  tools-html/docs
  video-html/docs
  java-web-manual/docs
  shared-assets
  sites-hub/scripts
  sites-hub/www
  sites-hub/conf
  sites-hub/build-release.sh
  sites-hub/deploy-vps.sh
  sites-hub/SOP-ADD-SITE.md
  sites-hub/OPTIMIZATION.md
  sites-hub/OPTIMIZATION-CONTENT.md
  README.md
)

# 过滤存在的
EXISTING=()
for t in "${TARGETS[@]}"; do
  [[ -e "$t" ]] && EXISTING+=("$t")
done

echo "Scanning ${#EXISTING[@]} targets (${#TARGETS[@]} configured)..."

"$CODESPELL" \
  --skip="$SKIP" \
  --ignore-words="$IGNORE_FILE" \
  "${EXTRA_ARGS[@]}" \
  "${EXISTING[@]}"
