#!/usr/bin/env bash
# Build all VitePress sites and create one deployable static archive.
#
# 子站清单来自 scripts/sites.sh（**唯一真相源**）。
# 新增站点只需改 sites.sh + 一张首页卡片 + 1 个项目目录。
#
# 用法：
#   ./build-release.sh                 # 正常构建（需要 node + npm + jq + 网络）
#   MOCK_BUILD=1 ./build-release.sh    # 跳过 npm，使用已有 .vitepress/dist（用于 CI dry-run）

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/sites.sh
source "$SCRIPT_DIR/scripts/sites.sh"

PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RELEASE_DIR="$PROJECT_ROOT/release"
STAGE_DIR="$RELEASE_DIR/sites-hub"
ARCHIVE="$RELEASE_DIR/sites-hub-static.tar.gz"
MOCK_BUILD="${MOCK_BUILD:-0}"

if [[ "$MOCK_BUILD" != "1" ]] && (! command -v node >/dev/null || ! command -v npm >/dev/null); then
  echo "node and npm are required to build the sites (or set MOCK_BUILD=1)." >&2
  exit 1
fi

if ! command -v jq >/dev/null; then
  echo "jq is required for data.json generation (T5). Install via: brew install jq" >&2
  exit 1
fi

if [[ ! -f "$SCRIPT_DIR/scripts/check-sites.sh" ]]; then
  echo "scripts/check-sites.sh not found; cannot enforce SITES consistency." >&2
  exit 1
fi

# Pre-build sanity check：保证 卡片数 == nginx location 数 == SITES 数
bash "$SCRIPT_DIR/scripts/check-sites.sh"

rm -rf "$STAGE_DIR"
mkdir -p "$STAGE_DIR"
# C9: 自动从 git log 生成 Updates 列表（在 cp stage 之前，确保 stage 副本带最新内容）
if [[ -f "$SCRIPT_DIR/scripts/build-updates-from-git.py" ]]; then
  echo "==> Generating Updates list from git log..."
  python3 "$SCRIPT_DIR/scripts/build-updates-from-git.py" || {
    echo "WARN: build-updates-from-git failed; index.html keeps previous Updates" >&2
  }
else
  echo "WARN: scripts/build-updates-from-git.py not found; skipping updates auto-gen" >&2
fi

cp -R "$SCRIPT_DIR/www" "$STAGE_DIR/www"
# T7: 自托管字体 (Latin subset woff2)
if [[ -d "$SCRIPT_DIR/www/fonts" ]]; then
  mkdir -p "$STAGE_DIR/www/fonts"
  for f in "$SCRIPT_DIR/www/fonts"/*.woff2; do
    [[ -f "$f" ]] && cp "$f" "$STAGE_DIR/www/fonts/"
  done
fi

# 构建循环：完全由 SITES 驱动
declare -a built_sites=()
declare -a failed_sites=()
for s in "${SITES[@]}"; do
  project="$(site_to_project "$s")"
  project_dir="$PROJECT_ROOT/$project"
  target_dir="$STAGE_DIR/$s"

  if [[ ! -d "$project_dir" ]]; then
    echo "WARN: project dir missing for site '$s' -> $project_dir (skipping)" >&2
    failed_sites+=("$s")
    continue
  fi

  if [[ "$MOCK_BUILD" == "1" ]]; then
    if [[ ! -d "$project_dir/.vitepress/dist" ]]; then
      echo "WARN: $s ($project) has no .vitepress/dist, MOCK_BUILD cannot use it (skipping)" >&2
      failed_sites+=("$s")
      continue
    fi
    echo "==> [MOCK] Reusing dist for $s ($project)"
  else
    echo "==> Building $s ($project)"
    if ! (
      cd "$project_dir"
      # package-lock.json is committed for every site; npm ci keeps builds reproducible.
      npm ci
      npm run docs:build
    ); then
      echo "WARN: build failed for $s ($project)" >&2
      failed_sites+=("$s")
      continue
    fi
  fi

  # Postbuild: copy public/ contents to dist/ (VitePress 1.6.4 doesn't do this on macOS).
  # This is a known bug — affects favicon.ico / apple-touch-icon.png etc.
  if [ -d "$project_dir/.vitepress/public" ]; then
    cp -R "$project_dir/.vitepress/public/." "$project_dir/.vitepress/dist/" 2>/dev/null || true
  fi

  # 清理 macOS tar 残留的 ._* 元数据文件
  find "$project_dir/.vitepress/dist" -name '._*' -delete 2>/dev/null || true

  mkdir -p "$target_dir"
  cp -R "$project_dir/.vitepress/dist/." "$target_dir/"
  built_sites+=("$s")
done

# 同步 deploy 脚本
cp "$SCRIPT_DIR/deploy-vps.sh" "$STAGE_DIR/deploy-vps.sh"
chmod +x "$STAGE_DIR/deploy-vps.sh"

# Sync SITES drivers + T3 fail2ban into stage/scripts/ for VPS deploy
# (deploy-vps.sh on VPS does `source $SCRIPT_DIR/scripts/sites.sh`;
#  setup-fail2ban.sh on VPS copies filter + jail into /etc/fail2ban/)
mkdir -p "$STAGE_DIR/scripts"
for f in sites.sh check-sites.sh render-nginx-conf.sh          setup-fail2ban.sh fail2ban-nginx-auth.conf fail2ban-nginx-auth-filter.conf          setup-goaccess.sh          inject-stats.py; do
  if [[ -f "$SCRIPT_DIR/scripts/$f" ]]; then
    cp "$SCRIPT_DIR/scripts/$f" "$STAGE_DIR/scripts/$f"
    chmod +x "$STAGE_DIR/scripts/$f"
  fi
done

# 生成 data.json（T5 数字单一来源）
SITES_N=${#SITES[@]}
BUILT_N=${#built_sites[@]}
PAGES_N=$(find "$STAGE_DIR" -name '*.html' | wc -l | tr -d ' ')
NODES_N=$( { grep -rhoE 'data-node="[^"]+"' "$STAGE_DIR"/ 2>/dev/null || true; } | sort -u | wc -l | tr -d ' ')
WIDGETS_N=$( { grep -rhoE 'class="(graph|mindmap|cheatsheet)' "$STAGE_DIR"/ 2>/dev/null || true; } | wc -l | tr -d ' ')
jq -n \
  --argjson sites  "$SITES_N" \
  --argjson built  "$BUILT_N" \
  --argjson pages  "$PAGES_N" \
  --argjson nodes  "$NODES_N" \
  --argjson widgets "$WIDGETS_N" \
  '{sites:$sites,built:$built,pages:$pages,nodes:$nodes,widgets:$widgets}' > "$STAGE_DIR/www/data.json"

# 生成 ld+json（T4 SEO）
{
  printf '{"@context":"https://schema.org","@type":"CollectionPage",'
  printf '"name":"Scholar'"'"'s Atlas","url":"https://java-px.bot.cd/",'
  printf '"inLanguage":"zh-CN","hasPart":['
  first=1
  for s in "${built_sites[@]}"; do
    [ "$first" -eq 0 ] && printf ','
    printf '{"@type":"WebSite","name":"%s","url":"https://java-px.bot.cd/%s/"}' "$s" "$s"
    first=0
  done
  printf ']}'
} > "$STAGE_DIR/www/ld.json"

# 生成 sitemap.xml（T4 SEO）
cat > "$STAGE_DIR/www/sitemap.xml" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://java-px.bot.cd/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>
EOF
for s in "${built_sites[@]}"; do
  echo "  <url><loc>https://java-px.bot.cd/$s/</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>" \
    >> "$STAGE_DIR/www/sitemap.xml"
done
echo "</urlset>" >> "$STAGE_DIR/www/sitemap.xml"

# robots.txt（T4 SEO）
cat > "$STAGE_DIR/www/robots.txt" <<EOF
User-agent: *
Allow: /
Sitemap: https://java-px.bot.cd/sitemap.xml
EOF

rm -f "$ARCHIVE"
tar -C "$RELEASE_DIR" -czf "$ARCHIVE" sites-hub

echo
echo "==> Release archive created: $ARCHIVE"
echo "==> Sites built: ${#built_sites[@]}/${#SITES[@]}"
echo "==> data.json: $(cat "$STAGE_DIR/www/data.json")"

# T5: 把 data.json 里的真实数字注入到 index.html
# (hero-stats / brand-sub / footer / about / og:title / og:description)
if [[ -f "$SCRIPT_DIR/scripts/inject-stats.py" ]]; then
  echo "==> Injecting stats into index.html..."
  python3 "$SCRIPT_DIR/scripts/inject-stats.py" || {
    echo "WARN: inject-stats failed; index.html may have stale numbers" >&2
  }
else
  echo "WARN: scripts/inject-stats.py not found; skipping stat injection" >&2
fi
if [[ ${#failed_sites[@]} -gt 0 ]]; then
  echo "==> Failed sites: ${failed_sites[*]}" >&2
  exit 1
fi
