#!/bin/bash
# 一键启动所有静态网站
# 用法: ./start-all.sh
#
# 子站列表由 scripts/sites.sh 驱动（**唯一真相源**）。
# 新增站点只改 sites.sh + 一张首页卡片 + 1 个项目目录。

set -e

HUB_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=scripts/sites.sh
source "$HUB_DIR/scripts/sites.sh"

# 项目目录名数组（按 SITES 顺序）
PROJECTS=()
for s in "${SITES[@]}"; do
  PROJECTS+=("$(site_to_project "$s")")
done

echo "========================================="
echo "  ${#SITES[@]} 个静态网站 - 一键启动"
echo "========================================="

# 1. 构建所有网站
for proj in "${PROJECTS[@]}"; do
  proj_dir="$HUB_DIR/../$proj"
  if [ -d "$proj_dir" ]; then
    echo ""
    echo "📦 构建 $proj..."
    cd "$proj_dir"
    if [ ! -d node_modules ]; then
      echo "   安装依赖..."
      npm install --silent
    fi
    npm run docs:build 2>&1 | tail -3
  else
    echo "WARN: project dir missing: $proj_dir" >&2
  fi
done

# 2. 启动 nginx
echo ""
echo "========================================="
echo "  🚀 启动 Nginx (单域名访问 ${#SITES[@]} 个网站)"
echo "========================================="

if ! command -v nginx &> /dev/null; then
  echo "❌ 未检测到 nginx，请先安装:"
  echo "   macOS:  brew install nginx"
  echo "   Ubuntu: sudo apt install nginx"
  echo "   CentOS: sudo yum install nginx"
  exit 1
fi

NGINX_CMD="nginx -c $HUB_DIR/conf/nginx.conf -p $HUB_DIR"
if pgrep -f "nginx.*sites-hub" &> /dev/null; then
  echo "nginx 已在运行，重新加载配置..."
  nginx -c $HUB_DIR/conf/nginx.conf -p $HUB_DIR -s reload
else
  echo "启动 nginx..."
  $NGINX_CMD
fi

echo ""
echo "✅ 启动成功！"
echo ""
echo "🌐 访问地址："
echo "   首页导航:    http://localhost/"
for s in "${SITES[@]}"; do
  echo "   /$s/  ->  http://localhost/$s/"
done
echo ""
echo "📁 停止: pkill -f 'nginx.*sites-hub'"
