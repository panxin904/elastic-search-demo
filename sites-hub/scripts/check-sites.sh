#!/usr/bin/env bash
# sites-hub/scripts/check-sites.sh
#
# 校验 SITES 单一真相源 与 下游产物 的一致性：
#   1. SITES 数组长度
#   2. www/index.html 卡片 href 列表
#   3. conf/nginx.conf  location / 块列表（静态生成，文件内可见）
#   4. deploy-vps.sh 动态生成（SITES 数组引用 + source sites.sh）
#   5. start-hub.py / start.sh / start-all.sh 引用 SITES 或 SITES_CSV
#   6. 每个 SITES[i] 对应的项目目录存在
#
# 任何不一致都会 exit 1，并打印差异。
# 在 build-release.sh 入口自动调用，避免漂移到 release 产物。
#
# 兼容性：macOS bash 3.2 / zsh 5 都能跑。

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
HUB_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$HUB_DIR/.." && pwd)"

# shellcheck source=scripts/sites.sh
source "$SCRIPT_DIR/sites.sh"

errors=0
note() { printf '  %s\n' "$*"; }
ok()   { printf '  \033[32m✓\033[0m %s\n' "$*"; }
fail() { printf '  \033[31m✗\033[0m %s\n' "$*"; errors=$((errors+1)); }

# 1. SITES 长度
SITES_N=${#SITES[@]}
ok "SITES array has $SITES_N sites"

# 2. www/index.html 卡片 href
INDEX_HTML="$HUB_DIR/www/index.html"
if [[ ! -f "$INDEX_HTML" ]]; then
  fail "Missing $INDEX_HTML"
  exit 1
fi
card_hrefs=$(grep -oE 'class="card"[^>]*href="/[a-z-]+/"' "$INDEX_HTML" \
  | sed -E 's|.*href="/([a-z-]+)/".*|\1|' | sort -u)
CARD_N=$(printf '%s\n' "$card_hrefs" | grep -c .)
note "www/index.html cards: $CARD_N"

# 3. conf/nginx.conf location / 块（静态生成）
NGINX_CONF="$HUB_DIR/conf/nginx.conf"
if [[ ! -f "$NGINX_CONF" ]]; then
  fail "Missing $NGINX_CONF"
  exit 1
fi
nginx_paths=$(grep -oE '^        location /[a-z-]+/ \{' "$NGINX_CONF" \
  | sed -E 's|^        location /([a-z-]+)/ \{$|\1|' | sort -u)
NGINX_N=$(printf '%s\n' "$nginx_paths" | grep -c .)
note "conf/nginx.conf location / blocks: $NGINX_N"

# 4. deploy-vps.sh：必须 source sites.sh + 引用 SITES 数组
DEPLOY="$HUB_DIR/deploy-vps.sh"
if [[ ! -f "$DEPLOY" ]]; then
  fail "Missing $DEPLOY"
  exit 1
fi
if grep -qE 'source.*sites\.sh' "$DEPLOY" && grep -qE 'SITES\[@\]' "$DEPLOY"; then
  ok "deploy-vps.sh sources sites.sh and uses SITES array (dynamic render)"
else
  fail "deploy-vps.sh does NOT source sites.sh or use SITES array"
fi
note "deploy-vps.sh: dynamic render (validated by source + SITES reference)"

# 5. start-hub.py：必须读 SITES_CSV 或有 SITES 兜底
PY_HUB="$HUB_DIR/start-hub.py"
if [[ ! -f "$PY_HUB" ]]; then
  fail "Missing $PY_HUB"
  exit 1
fi
if grep -qE 'SITES_CSV' "$PY_HUB" && grep -qE 'PROJECT_DIR_OVERRIDES' "$PY_HUB"; then
  ok "start-hub.py uses SITES_CSV env var + PROJECT_DIR_OVERRIDES"
else
  fail "start-hub.py missing SITES_CSV or PROJECT_DIR_OVERRIDES"
fi

# 6. start.sh / start-all.sh：必须 source sites.sh
for s in start.sh start-all.sh; do
  f="$HUB_DIR/$s"
  if [[ ! -f "$f" ]]; then
    fail "Missing $f"
    continue
  fi
  if grep -qE 'source.*sites\.sh' "$f" && grep -qE 'SITES\[@\]' "$f"; then
    ok "$s sources sites.sh and uses SITES array"
  else
    fail "$s does NOT source sites.sh or use SITES array"
  fi
done

# 7. 数量一致性
printf '%s\n' "${SITES[@]}" | sort > /tmp/_sites

if [[ "$SITES_N" -ne "$CARD_N" ]]; then
  fail "SITES($SITES_N) != cards($CARD_N)"
  printf '%s\n' "$card_hrefs" | sort > /tmp/_cards
  comm -23 /tmp/_sites /tmp/_cards | sed 's/^/    in SITES but not in cards: /'
  comm -13 /tmp/_sites /tmp/_cards | sed 's/^/    in cards but not in SITES: /'
else
  ok "SITES count == cards count ($SITES_N)"
fi

if [[ "$SITES_N" -ne "$NGINX_N" ]]; then
  fail "SITES($SITES_N) != nginx($NGINX_N)"
  printf '%s\n' "$nginx_paths" | sort > /tmp/_nginx
  comm -23 /tmp/_sites /tmp/_nginx | sed 's/^/    in SITES but not in nginx: /'
  comm -13 /tmp/_sites /tmp/_nginx | sed 's/^/    in nginx but not in SITES: /'
else
  ok "SITES count == nginx count ($SITES_N)"
fi

# 8. 内容一致性
if [[ "$SITES_N" -eq "$CARD_N" ]]; then
  printf '%s\n' "$card_hrefs" | sort > /tmp/_cards
  if diff -q /tmp/_sites /tmp/_cards > /dev/null; then
    ok "SITES and cards match exactly"
  else
    fail "SITES and cards differ:"
    diff /tmp/_sites /tmp/_cards | sed 's/^/    /'
  fi
fi

if [[ "$SITES_N" -eq "$NGINX_N" ]]; then
  printf '%s\n' "$nginx_paths" | sort > /tmp/_nginx
  if diff -q /tmp/_sites /tmp/_nginx > /dev/null; then
    ok "SITES and nginx match exactly"
  else
    fail "SITES and nginx differ:"
    diff /tmp/_sites /tmp/_nginx | sed 's/^/    /'
  fi
fi

# 9. 项目目录存在性
missing_dirs=0
for s in "${SITES[@]}"; do
  project="$(site_to_project "$s")"
  if [[ ! -d "$PROJECT_ROOT/$project" ]]; then
    fail "SITES entry '$s' maps to missing project dir: $PROJECT_ROOT/$project"
    missing_dirs=$((missing_dirs+1))
  fi
done
if [[ "$missing_dirs" -eq 0 ]]; then
  ok "All ${#SITES[@]} project directories exist"
fi

rm -f /tmp/_sites /tmp/_cards /tmp/_nginx

echo
if [[ "$errors" -gt 0 ]]; then
  printf '\033[31m✗ check-sites: %d error(s)\033[0m\n' "$errors"
  exit 1
fi
printf '\033[32m✓ check-sites: all consistency checks passed\033[0m\n'
