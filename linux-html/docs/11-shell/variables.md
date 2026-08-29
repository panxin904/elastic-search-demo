---
title: 变量与参数
date: 2026-08-15  # date-auto-injected
---

# 变量与参数

> 脚本接收外界信息 + 在内部传递数据的核心。

## 🔤 变量基础

```bash
# 赋值（注意 = 不能有空格）
name="alice"
count=10

# 引用（建议加花括号）
echo $name
echo "${name}_${count}"
# 不加花括号有时会出错：
echo $name_default             # name + _default？应该是 "${name}_default"

# 只读
readonly LOG_LEVEL=INFO

# 删除
unset name

# 列出所有变量
set                           # 所有（含函数）
declare -p                    # 所有变量
```

## 🔢 数字

```bash
# 默认是字符串
a=10
b=20
echo $a + $b                  # 10 + 20（字面量）

# 算术（三种方式）
c=$((a + b))                  # POSIX
let c=a+b                     # bash builtin
((c = a + b))                 # bash 复合命令

# 自增
n=0
((n++))
echo $n                       # 1

# 浮点（bash 不直接支持，用 bc / awk）
echo "scale=2; 10/3" | bc       # 3.33
awk 'BEGIN {print 10/3}'      # 3.33333

# 进制
echo $((0xff))                # 255（16 进制）
echo $((010))                 # 8（8 进制）
echo $((2#1010))              # 10（二进制）
```

## 📋 特殊变量

| 变量 | 含义 |
|------|------|
| `$0` | 脚本名 |
| `$1` ... `$9` | 位置参数 |
| `${10}` | 第 10 个参数（要花括号） |
| `$#` | 参数个数 |
| `$@` | 所有参数（推荐） |
| `$*` | 所有参数（合并为字符串） |
| `$?` | 上一条命令退出码（0=成功） |
| `$$` | 当前 shell 的 PID |
| `$!` | 上一条后台命令的 PID |
| `$-` | 当前 shell 选项 |
| `$_` | 上一条命令最后一个参数 |

### "$@" vs "$*"

```bash
# "$@" 是数组
for arg in "$@"; do
  echo "[$arg]"                # 每个参数独立
done

# "$*" 是合并字符串
for arg in "$*"; do
  echo "[$arg]"                # 一个参数 = 整行
done
```

**几乎都用 `"$@"`**。

## 📥 读参数

```bash
# 缺省值
name=${1:-anonymous}          # 缺省字符串
port=${2:-8080}

# 必须传（缺了就报错）
required=${1:?error: usage: $0 <name>}

# shift
shift                         # $1 没了，$2 变成 $1
shift 2                       # 一次跳 2 个

# getopts（解析选项）
while getopts "abc:" opt; do
  case $opt in
    a) echo "a flag" ;;
    b) echo "b flag" ;;
    c) echo "c value: $OPTARG" ;;
    \?) echo "invalid" ;;
  esac
done
# 跑：./script.sh -a -c value -b
```

## 📖 read

```bash
read name                      # 读一行到 name
read -p "name? " name          # 带提示
read -s -p "pass? " pass        # 不回显（密码）
read -t 5 prompt               # 5 秒超时
read -r line                  # 不处理反斜杠
read -a arr                   # 读到数组

# 读 stdin / 文件
while IFS= read -r line; do
  echo "$line"
done < input.txt

# 读多个变量
read first second rest <<< "a b c d"
echo "$first / $second / $rest"
```

## 🌍 环境变量

```bash
# 查看
env                           # 全部环境变量
printenv                      # 同 env
echo $PATH

# 设
export PATH=/opt/bin:$PATH

# 临时（仅当前 shell）
LOCAL_VAR="x"

# 子进程继承
export GLOBAL_VAR="y"

# 用 set -a 自动 export
set -a
VAR1=val1
VAR2=val2
set +a
```

## 📦 命令替换

```bash
# $() 推荐
today=$(date +%Y-%m-%d)
files=$(ls *.txt | wc -l)

# 旧式（不推荐）
today=`date +%Y-%m-%d`

# 进程替换（生成"文件"）
diff <(ls dir1) <(ls dir2)

# 嵌套
result=$(echo "today is $(date +%F)")
```

## 🪞 间接引用

```bash
# 变量名引用变量
var="hello"
name="var"
echo ${!name}                 # hello（! 是 bash 特性）

# 数组下标引用
arr=(a b c)
i=1
echo ${arr[i]}                # b
```

## ⚠️ 常见陷阱

```bash
# 1. 变量未初始化（默认空字符串）
set -u                        # 用了未定义会报错
echo "$UNDEFINED_VAR"          # 用 set -u 后会报

# 2. 空格
name = "alice"                 # ❌ 这是 "name" "=" "alice"（启动命令）
name="alice"                   # ✅

# 3. 路径里有空格
ls $dir                        # ❌ dir="/tmp/my dir" → ls /tmp/my dir
ls "$dir"                      # ✅

# 4. glob 没引号
for f in $(ls); do             # ❌ 文件名有空格会断
for f in *; do                 # ✅
for f in "$(ls)"; do           # 或全引
```

## 🛡 类型声明

```bash
declare -i n=10                # 整数（赋值时自动算）
declare -r PI=3.14             # readonly
declare -a arr                 # 数组
declare -A map                 # 关联数组
declare -x VAR=value           # 等价 export
declare -u upper="hello"       # 自动大写
declare -l lower="HELLO"       # 自动小写
```

## 🛠 实战

```bash
# 读 JSON（jq）
name=$(jq -r '.name' file.json)
count=$(jq -r '.items | length' file.json)

# 读配置文件
. /etc/myapp.conf             # source
# 或
source /etc/myapp.conf
# 之后 config 里的变量都可用

# 配置文件示例
# /etc/myapp.conf
APP_PORT=8080
APP_LOG=/var/log/myapp.log
APP_DB_HOST=localhost
```

## 🔗 下一步

- [bash 基础语法](/11-shell/bash-syntax)
- [数组与字符串](/11-shell/arrays)
- [函数与脚本组织](/11-shell/functions)
- [调试与陷阱](/11-shell/debug)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [devops](https://java-px.bot.cd/devops/):DevOps 自动化
- [cloud-native](https://java-px.bot.cd/cloud-native/):云原生
- [network](https://java-px.bot.cd/network/):Linux 网络
