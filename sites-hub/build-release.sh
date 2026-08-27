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

if [[ -f "$SCRIPT_DIR/scripts/build-audit-dashboard.py" ]]; then
  echo "==> Generating C3 content quality trend dashboard..."
  python3 "$SCRIPT_DIR/scripts/build-audit-dashboard.py" \
    --reports-dir "$SCRIPT_DIR/reports" \
    --output "$STAGE_DIR/www/audit-dashboard.html" \
    --max-weeks 12 || {
    echo "WARN: audit dashboard generation failed; release keeps previous dashboard if present" >&2
  }
else
  echo "WARN: scripts/build-audit-dashboard.py not found; skipping dashboard generation" >&2
fi

# VPS 渲染 nginx 配置需要 conf/（nginx.conf + 子站 vhost fragments）
cp -R "$SCRIPT_DIR/conf" "$STAGE_DIR/conf"
# T7: 自托管字体 (Latin subset woff2)
if [[ -d "$SCRIPT_DIR/www/fonts" ]]; then
  mkdir -p "$STAGE_DIR/www/fonts"
  for f in "$SCRIPT_DIR/www/fonts"/*.woff2; do
    [[ -f "$f" ]] && cp "$f" "$STAGE_DIR/www/fonts/"
  done
fi

# 并行构建循环（bash 3.2+ 兼容）：PARALLEL 默认 4，可环境变量覆盖
# 设计：
#   - 抽 build_one_site() 函数到后台进程跑（每站一个 log file）
#   - 主循环启动后台 + wait oldest（PARALLEL 满了等最早启动的完成）
#   - 完成后按 SITES 顺序排序 built_sites（保持 ld.json 输出顺序稳定）
#   - bash 3.2 没有 'wait -n'，用 wait PID（阻塞指定 PID）
PARALLEL="${PARALLEL:-4}"
declare -a built_sites=()
declare -a failed_sites=()
declare -a running_pids=()
declare -a running_sites=()
TMPDIR_BUILD="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_BUILD"' EXIT

build_one_site() {
  local s="$1"
  local log_file="$2"
  local project project_dir target_dir
  project="$(site_to_project "$s")"
  project_dir="$PROJECT_ROOT/$project"
  target_dir="$STAGE_DIR/$s"

  {
    if [[ ! -d "$project_dir" ]]; then
      echo "WARN: project dir missing for site '$s' -> $project_dir (skipping)" >&2
      echo "FAIL:$s"
      return 0
    fi

    if [[ "$MOCK_BUILD" == "1" ]]; then
      if [[ ! -d "$project_dir/.vitepress/dist" ]]; then
        echo "WARN: $s ($project) has no .vitepress/dist, MOCK_BUILD cannot use it (skipping)" >&2
        echo "FAIL:$s"
        return 0
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
        echo "FAIL:$s"
        return 0
      fi
    fi

    # Postbuild: copy public/ contents to dist/ (VitePress 1.6.4 doesn'"'"'t do this on macOS).
    # This is a known bug — affects favicon.ico / apple-touch-icon.png etc.
    if [ -d "$project_dir/.vitepress/public" ]; then
      cp -R "$project_dir/.vitepress/public/." "$project_dir/.vitepress/dist/" 2>/dev/null || true
    fi

    # 清理 macOS tar 残留的 ._* 元数据文件
    find "$project_dir/.vitepress/dist" -name '"'"'._*'"'"' -delete 2>/dev/null || true

    mkdir -p "$target_dir"
    cp -R "$project_dir/.vitepress/dist/." "$target_dir/"
    echo "OK:$s"
  } > "$log_file" 2>&1
}

# 主调度循环（§8.45 优化：wait_any 替代 head-of-line blocking）
# 原算法：等最早启动的 PID 完成 → 假定最早启动的最先完成 → 实际不一定
#   npm ci 时间差异大（10-30s），build 时间差异更大（5-30s），等最早启动会卡住
# 新算法：扫所有 running_pids，找到任意一个已完成的 PID 处理 + 立即启动新站
#   维持恒定 PARALLEL 并发，避免 head-of-line blocking
#   bash 3.2 兼容：kill -0 检测 + sleep 0.05 防 busy-wait（替代 bash 4.3+ wait -n）
process_log() {
  # process_log <pid> <site>
  local pid="$1" site="$2"
  local finished_log="$TMPDIR_BUILD/$site.log"
  if grep -q "^OK:" "$finished_log" 2>/dev/null; then
    built_sites+=("$site")
    printf "    [OK] %s\n" "$site"
  else
    failed_sites+=("$site")
    printf "    [FAIL] %s (log: %s)\n" "$site" "$finished_log"
  fi
}

wait_any() {
  # 扫 running_pids，找到第一个已完成的 PID，处理日志，从队列移除
  # 返回 0（找到了完成的 PID）
  while :; do
    # 用数字索引而非 ${!arr[@]:-}（后者在 bash 3.2 下对 declare -a 但非空数组返回空 i=''  导致 unset 错位）
    local n=${#running_pids[@]}
    for ((idx=0; idx<n; idx++)); do
      local pid="${running_pids[$idx]}"
      # kill -0 不发信号，仅检测 process 是否存活（返回 0 = 存活，1 = 已死）
      if ! kill -0 "$pid" 2>/dev/null; then
        # 已死 → wait 回收（不阻塞，因为 process 已死）
        wait "$pid" 2>/dev/null || true
        process_log "$pid" "${running_sites[$idx]}"
        # 从队列移除：splice idx（重建数组避免 unset 索引漂移）
        local new_pids=() new_sites=()
        for ((j=0; j<n; j++)); do
          if [[ $j -ne $idx ]]; then
            new_pids+=("${running_pids[$j]}")
            new_sites+=("${running_sites[$j]}")
          fi
        done
        running_pids=("${new_pids[@]+"${new_pids[@]}"}")
        running_sites=("${new_sites[@]+"${new_sites[@]}"}")
        return 0
      fi
    done
    # 短暂 sleep 防止 busy-wait（28 站场景下检查频率 ~10ms/次，开销可忽略）
    sleep 0.05
  done
}

echo "==> Parallel build (PARALLEL=$PARALLEL, sites=${#SITES[@]}, mode=wait_any)..."
for s in "${SITES[@]}"; do
  log_file="$TMPDIR_BUILD/$s.log"
  # 子 shell 解除 EXIT trap，避免 4 个并行 build 共享 TMPDIR_BUILD 时第一个完成的 rm -rf 把别人日志目录干掉
  (
    trap - EXIT
    build_one_site "$s" "$log_file"
  ) &
  pid=$!
  running_pids+=("$pid")
  running_sites+=("$s")

  # 满了就 wait_any（任意 PID 完成就处理 + 启动下一个）
  if [[ ${#running_pids[@]} -ge $PARALLEL ]]; then
    wait_any
  fi
done

# 等待剩余的
while [[ ${#running_pids[@]} -gt 0 ]]; do
  wait_any
done

# 按 SITES 顺序排序 built_sites（保持 ld.json / sitemap 输出顺序稳定）
declare -a _ordered=()
for s in "${SITES[@]}"; do
  for b in "${built_sites[@]}"; do
    [[ "$s" == "$b" ]] && { _ordered+=("$s"); break; }
  done
done
built_sites=("${_ordered[@]}")

echo "==> Build phase done: ${#built_sites[@]} built, ${#failed_sites[@]} failed"

# 同步 deploy 脚本
cp "$SCRIPT_DIR/deploy-vps.sh" "$STAGE_DIR/deploy-vps.sh"
chmod +x "$STAGE_DIR/deploy-vps.sh"

# Sync SITES drivers + T3 fail2ban into stage/scripts/ for VPS deploy
# (deploy-vps.sh on VPS does `source $SCRIPT_DIR/scripts/sites.sh`;
#  setup-fail2ban.sh on VPS copies filter + jail into /etc/fail2ban/)
mkdir -p "$STAGE_DIR/scripts"
# P18: render-sites-hub-conf.sh 加入 stage 同步列表（deploy-vps.sh + deploy-release.sh 共同依赖）
for f in sites.sh check-sites.sh render-nginx-conf.sh render-sites-hub-conf.sh          setup-fail2ban.sh fail2ban-nginx-auth.conf fail2ban-nginx-auth-filter.conf          setup-goaccess.sh          inject-stats.py          build-audit-dashboard.py          deploy-release.sh; do
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

# 生成 sitemap.xml + llms.txt + llms-full.txt + feed.xml（C12/C5）
# 调 build-sitemap-and-llms.py（已存在，145 行）覆盖 $SCRIPT_DIR/www/{sitemap,llms,feed}.{xml,txt}
if [[ -f "$SCRIPT_DIR/scripts/build-sitemap-and-llms.py" ]]; then
  echo "==> Generating sitemap + llms + feed for main portal + 28 sites..."
  python3 "$SCRIPT_DIR/scripts/build-sitemap-and-llms.py" >/dev/null
fi

# robots.txt（T4 SEO）
cat > "$SCRIPT_DIR/www/robots.txt" <<EOF
User-agent: *
Allow: /
Sitemap: https://java-px.bot.cd/sitemap.xml
EOF

# P3：预压缩元数据文件（nginx gzip_static 用）
# - sitemap.xml / llms.txt / llms-full.txt / feed.xml
# - -k 保留原文件；-9 最高压缩；-n 跳过文件名/时间戳（gzip_static 不需要 mtime 变化）
echo "==> Pre-compressing metadata files for nginx gzip_static..."
for f in sitemap.xml llms.txt llms-full.txt feed.xml; do
    src="$STAGE_DIR/www/$f"
    if [[ -f "$src" ]]; then
        gzip -kf9 -n "$src"
        # gzip 产物名为 $f.gz；size 输出
        printf '    %-20s %s -> %s\n' "$f"             "$(du -h "$src" | cut -f1)"             "$(du -h "${src}.gz" | cut -f1)"
    else
        echo "    WARN: $f not found, skip"
    fi
done

rm -f "$ARCHIVE"
tar -C "$RELEASE_DIR/sites-hub" -czf "$ARCHIVE" .

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
