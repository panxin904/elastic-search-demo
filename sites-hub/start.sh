#!/bin/bash
# 静态网站一站式启动
# 优先使用 Nginx，没有则用 Python 备用方案
# 用法: ./start.sh [stop|build|start|status]
#
# 子站列表由 scripts/sites.sh 驱动（**唯一真相源**）。

set -e

HUB_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=scripts/sites.sh
source "$HUB_DIR/scripts/sites.sh"

# 项目目录名数组（按 SITES 顺序）
PROJECTS=()
for s in "${SITES[@]}"; do
  PROJECTS+=("$(site_to_project "$s")")
done

PY_HUB="$HUB_DIR/start-hub.py"
NGINX_CONF="$HUB_DIR/conf/nginx.conf"
NGINX_PREFIX="$HUB_DIR"

# 把 SITES 列表注入到 start-hub.py 的环境变量
export SITES_CSV=$(IFS=,; echo "${SITES[*]}")

cmd="${1:-start}"

build_all() {
  echo "=========================================="
  echo "  📦 构建 ${#PROJECTS[@]} 个网站"
  echo "=========================================="
  for proj in "${PROJECTS[@]}"; do
    proj_dir="$HUB_DIR/../$proj"
    if [ ! -d "$proj_dir" ]; then
      echo "❌ 目录不存在: $proj_dir"
      exit 1
    fi
    if [ ! -d "$proj_dir/.vitepress/dist" ] || [ "${REBUILD:-0}" = "1" ]; then
      echo ""
      echo "🔨 构建 $proj..."
      cd "$proj_dir"
      if [ ! -d node_modules ]; then
        echo "   安装依赖..."
        npm install --silent
      fi
      npm run docs:build 2>&1 | tail -2
    else
      echo "✅ $proj 已构建（跳过）"
    fi
  done
}

start_nginx() {
  if ! command -v nginx &> /dev/null; then
    return 1
  fi
  if pgrep -f "nginx.*sites-hub" &> /dev/null; then
    nginx -c "$NGINX_CONF" -p "$NGINX_PREFIX" -s reload
    echo "✅ nginx 已重新加载"
  else
    nginx -c "$NGINX_CONF" -p "$NGINX_PREFIX"
    echo "✅ nginx 已启动"
  fi
  return 0
}

start_python() {
  if lsof -i :8080 &> /dev/null; then
    echo "⚠️  8080 端口已被占用，请先停掉"
    return 1
  fi
  echo "ℹ️  使用 Python 备用方案（端口 8080）"
  cd "$HUB_DIR"
  nohup python3 "$PY_HUB" > "$HUB_DIR/hub.log" 2>&1 &
  echo $! > "$HUB_DIR/hub.pid"
  sleep 1
  echo "✅ Python 静态服务已启动 (PID: $(cat $HUB_DIR/hub.pid))"
}

case "$cmd" in
  build)
    REBUILD=1 build_all
    echo ""
    echo "✅ 构建完成"
    ;;
  stop)
    echo "停止所有相关服务..."
    if pgrep -f "nginx.*sites-hub" &> /dev/null; then
      nginx -c "$NGINX_CONF" -p "$NGINX_PREFIX" -s quit
      echo "✅ nginx 已停止"
    fi
    if [ -f "$HUB_DIR/hub.pid" ]; then
      kill "$(cat $HUB_DIR/hub.pid)" 2>/dev/null && echo "✅ Python hub 已停止"
      rm -f "$HUB_DIR/hub.pid"
    fi
    ;;
  status)
    echo "=== 状态检查 ==="
    if pgrep -f "nginx.*sites-hub" &> /dev/null; then
      echo "✅ nginx: 运行中"
    else
      echo "⚪ nginx: 未运行"
    fi
    if [ -f "$HUB_DIR/hub.pid" ] && kill -0 "$(cat $HUB_DIR/hub.pid)" 2>/dev/null; then
      echo "✅ Python hub: 运行中 (PID: $(cat $HUB_DIR/hub.pid))"
    else
      echo "⚪ Python hub: 未运行"
    fi
    ;;
  start|*)
    build_all
    echo ""
    echo "=========================================="
    echo "  🚀 启动统一访问入口"
    echo "=========================================="
    if start_nginx; then
      echo ""
      echo "  🌐 访问地址（nginx 端口 8081）:"
    else
      start_python
      echo ""
      echo "  🌐 访问地址（Python 端口 8080）:"
    fi
    echo "     首页导航:   http://localhost/"
    for s in "${SITES[@]}"; do
      echo "     /$s/  ->  http://localhost/$s/"
    done
    echo ""
    echo "  📁 查看日志: tail -f $HUB_DIR/hub.log"
    echo "  🛑 停止:     $0 stop"
    ;;
esac
