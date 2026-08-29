---
title: 函数与脚本组织
date: 2026-08-15  # date-auto-injected
---

# 函数与脚本组织

> 把脚本当成项目来组织，避免一切塞在一个 main 函数里。

## 📜 函数基础

```bash
# 定义
greet() {
  echo "hello, $1"
}

# 调用
greet alice                     # hello, alice
greet "bob smith"               # 引号防空格

# 多参数
add() {
  local a=$1
  local b=$2
  echo $((a + b))
}

add 3 5                         # 8
```

## 🔧 局部变量（`local`）

```bash
# 不加 local 会污染全局
foo() {
  x=10                          # 全局！
  local y=20                    # 局部
}

foo
echo $x                         # 10
echo $y                         # 空（函数外不可见）

# 最佳实践：函数里所有变量都加 local
process_file() {
  local file=$1
  local tmpdir=$(mktemp -d)
  # ...
  rm -rf "$tmpdir"
}
```

## ↩️ 返回值

```bash
# 0 = 成功，1-255 = 失败
is_file() {
  [ -f "$1" ]
}

if is_file /etc/passwd; then
  echo "yes"
fi

# 显式返回
divide() {
  if [ $2 -eq 0 ]; then
    echo "div by zero" >&2
    return 1                      # 错误退出码
  fi
  echo $(($1 / $2))
  return 0
}

result=$(divide 10 2)            # 5
echo $?                          # 0
```

## 📤 输出（stdout vs stderr）

```bash
# stdout - 正常输出
echo "normal output"

# stderr - 错误 / 日志
echo "error happened" >&2

# 用文件描述符
log() {
  echo "[$(date +%H:%M:%S)] $*" >&2
}

log "starting up"               # 不会污染 stdout
result=$(mycommand)             # 只拿 stdout
```

## 🎯 函数高级

### 默认参数

```bash
# bash < 4
greet() {
  local name=${1:-anonymous}
  echo "hello, $name"
}

# bash 4+: declare -A default
```

### 引用参数数组

```bash
# 接收任意数量参数
sum() {
  local total=0
  for n in "$@"; do
    ((total += n))
  done
  echo $total
}

sum 1 2 3 4 5                   # 15
```

### 函数库

```bash
# lib/utils.sh
log() { echo "[$(date +%H:%M:%S)] $*" >&2; }
err() { echo "[ERROR] $*" >&2; exit 1; }
require_root() { [[ $EUID -eq 0 ]] || err "must be root"; }

# main.sh
source /path/to/lib/utils.sh

require_root
log "starting"
```

## 📁 脚本结构（推荐）

```bash
#!/usr/bin/env bash
#
# deploy.sh - 部署脚本
#
set -euo pipefail
IFS=$'\n\t'

# === 常量 ===
readonly APP=/opt/myapp
readonly LOG=/var/log/deploy.log

# === 配置（可被环境变量覆盖） ===
ENV=${ENV:-prod}
BRANCH=${BRANCH:-main}

# === 工具函数 ===
log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG" >&2; }
err() { log "ERROR: $*" >&2; exit 1; }
require() { for cmd in "$@"; do command -v "$cmd" >/dev/null || err "missing: $cmd"; done; }

# === 业务函数 ===
preflight() {
  require git docker
  [ -d "$APP" ] || err "missing $APP"
}

deploy() {
  log "deploying $BRANCH to $ENV"
  cd "$APP"
  git fetch
  git checkout "$BRANCH"
  docker build -t myapp:latest .
  docker compose up -d
}

postcheck() {
  curl -f http://localhost/health || err "health check failed"
}

# === 主流程 ===
main() {
  preflight
  deploy
  postcheck
  log "done"
}

main "$@"
```

## 🎯 main 函数 + 参数

```bash
#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 [-v] [-d] [-h] NAME

Deploy NAME to server.

  -v  verbose
  -d  dry-run
  -h  show this help
EOF
}

VERBOSE=0
DRYRUN=0

main() {
  while getopts ":vdh" opt; do
    case $opt in
      v) VERBOSE=1 ;;
      d) DRYRUN=1 ;;
      h) usage; exit 0 ;;
      \?) echo "unknown: $OPTARG"; usage; exit 1 ;;
    esac
  done
  shift $((OPTIND - 1))

  local name=${1:?name required}

  echo "deploying $name (verbose=$VERBOSE dry=$DRYRUN)"

  # 真实逻辑
  # ...
}

main "$@"
```

## 📚 多个文件

```
project/
├── bin/
│   └── myapp                # 主入口
├── lib/
│   ├── utils.sh             # 通用工具
│   ├── log.sh               # 日志
│   └── config.sh            # 配置解析
└── README.md
```

```bash
# bin/myapp
#!/usr/bin/env bash
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
source "$SCRIPT_DIR/../lib/log.sh"
source "$SCRIPT_DIR/../lib/config.sh"
source "$SCRIPT_DIR/../lib/utils.sh"

main "$@"
```

## 🧪 模板项目

```bash
# 强类型（变量 + 函数）
config_file=$1
source "$config_file"        # 加载配置

# 锁（防止并发）
LOCKFILE=/var/lock/myapp.lock
( set -o noclobber; echo $$ > "$LOCKFILE" ) || err "already running"
trap "rm -f $LOCKFILE" EXIT

# 临时目录
tmp=$(mktemp -d)
trap "rm -rf $tmp" EXIT

# 完整错误
trap 'echo "failed at line $LINENO"' ERR
```

## 🔗 下一步

- [bash 基础语法](/11-shell/bash-syntax)
- [变量与参数](/11-shell/variables)
- [数组与字符串](/11-shell/arrays)
- [调试与陷阱](/11-shell/debug)