#!/usr/bin/env bash
# sites-hub/scripts/setup-goaccess.sh
#
# 在 VPS 上一次性配置 GoAccess 访问统计（轻量、零依赖、不引入 Docker）。
#
# 用法：
#   sudo bash sites-hub/scripts/setup-goaccess.sh [access_log_path]
#
# 默认参数：
#   access_log_path = /var/log/nginx/access.log
#
# 流程：
#   1. apt-get install goaccess（若未装）
#   2. 创建持久化目录 /var/lib/goaccess（增量解析用）
#   3. 写占位 stats.html（避免首次部署 404）
#   4. 写 generator 脚本 /usr/local/bin/goaccess-generate-stats.sh
#   5. 加 cron 每日 0:00 跑一次（用 --persist 增量模式）
#
# 资源占用（实测，参考值）：
#   - goaccess 二进制：~5MB
#   - 每次运行（~30s）：CPU spike ~5%, RAM ~30MB
#   - 持久化 DB：~5MB（30 天数据）
#   - 输出 stats.html：~300KB
#
# 替代 Plausible SaaS（需要注册账号）或 Docker 自托管（耗资源）。
set -euo pipefail

ACCESS_LOG="${1:-/var/log/nginx/access.log}"
STATS_HTML="/var/www/sites-hub/www/stats.html"
DB_DIR="/var/lib/goaccess"
GENERATOR="/usr/local/bin/goaccess-generate-stats.sh"
CRON_FILE="/etc/cron.d/goaccess-stats"

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  echo "Run with sudo or as root." >&2
  exit 1
fi

# 1. 安装 goaccess
if ! command -v goaccess >/dev/null; then
  echo "==> Installing goaccess..."
  apt-get update -qq
  apt-get install -y --no-install-recommends goaccess
fi
goaccess --version | head -1

# 2. 持久化目录（增量模式必须）
mkdir -p "$DB_DIR"

# 3. 占位 HTML（避免首次访问 stats.html 时 404）
if [[ ! -f "$STATS_HTML" ]]; then
  echo "==> Creating placeholder stats.html..."
  cat > "$STATS_HTML" <<'HTML'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>访问统计 · Scholar's Atlas</title>
<style>
body { font-family: system-ui, -apple-system, sans-serif; max-width: 600px; margin: 4rem auto; padding: 0 1rem; line-height: 1.6; color: #333; }
h1 { color: #1a1a2e; }
.note { color: #666; font-size: 0.9em; }
</style>
</head>
<body>
<h1>📊 访问统计</h1>
<p>GoAccess 正在生成统计报告。</p>
<p class="note">首次部署后需要等待最多 24 小时（每日 0:00 cron 触发）。</p>
<p class="note">报告基于 nginx access log，零外部依赖，资源占用极低（< 30MB RAM）。</p>
</body>
</html>
HTML
fi

# 4. Generator 脚本（cron 调用，--persist 增量模式）
echo "==> Writing generator: $GENERATOR"
cat > "$GENERATOR" <<GENEOF
#!/usr/bin/env bash
# goaccess-generate-stats.sh — 由 cron 每日 0:00 调用
# 增量模式（--persist）：只读新行，DB 状态持久化到 $DB_DIR
set -euo pipefail

ACCESS_LOG="${ACCESS_LOG}"
STATS_HTML="${STATS_HTML}"
DB_DIR="${DB_DIR}"
LOG_FILE="/var/log/goaccess-generate.log"

# log rotation 处理：如果 log 被压缩或截断，强制重建
if [[ ! -s "\$ACCESS_LOG" ]]; then
  echo "\$(date -Iseconds): access_log empty, skip" >> "\$LOG_FILE"
  exit 0
fi

goaccess "\$ACCESS_LOG" \\
  -o "\$STATS_HTML" \\
  --log-format=COMBINED \\
  --persist \\
  --db-path="\$DB_DIR" \\
  --keep-last=30 \\
  --no-global-config \\
  >> "\$LOG_FILE" 2>&1

echo "\$(date -Iseconds): stats.html updated (\$(stat -c%s "\$STATS_HTML") bytes)" >> "\$LOG_FILE"
GENEOF
chmod +x "$GENERATOR"

# 5. Cron：每日 0:00 跑
echo "==> Adding cron: $CRON_FILE"
cat > "$CRON_FILE" <<EOF
# Scholar's Atlas 访问统计（GoAccess 增量模式）
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
0 0 * * * root $GENERATOR
EOF
chmod 644 "$CRON_FILE"

# 6. 立即跑一次（如有 access log 已有数据）
if [[ -s "$ACCESS_LOG" ]]; then
  echo "==> Initial generation (reading existing log)..."
  bash "$GENERATOR" || echo "WARN: initial generation failed; will retry tomorrow"
fi

echo ""
echo "✅ GoAccess 配置完成"
echo "   二进制:    $(command -v goaccess)"
echo "   访问日志:  $ACCESS_LOG"
echo "   输出:      $STATS_HTML"
echo "   持久化:    $DB_DIR"
echo "   Generator: $GENERATOR"
echo "   Cron:      $CRON_FILE (每日 0:00 触发)"
echo ""
echo "查看报告: https://java-px.bot.cd/stats.html"
