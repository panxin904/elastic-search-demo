---
title: bash 基础语法
---

# bash 基础语法

> 写 shell 脚本的第一步。

## 🔤 变量

```bash
# 赋值
name="alice"
age=30
path=/usr/local/bin

# 使用
echo $name
echo "${name}_${age}"

# 只读
readonly name

# 命令结果赋值
today=$(date)
files=$(ls *.txt | wc -l)

# 算术
n=$((10 + 20))
n=$((n * 2))
# 或
let n+=1

# 环境变量
export PATH=/opt/bin:$PATH

# 数组
arr=(a b c d)
echo ${arr[0]}                # a
echo ${arr[@]}                # a b c d
echo ${#arr[@]}               # 4
arr+=(e f)
```

## 🔀 条件（if / case）

```bash
# if
if [ -f "$file" ]; then
  echo "exists"
elif [ -d "$file" ]; then
  echo "dir"
else
  echo "other"
fi

# 字符串
if [ "$a" = "$b" ]; then
if [ -z "$str" ]; then                  # 空
if [ -n "$str" ]; then                  # 非空
if [[ "$str" =~ ^abc ]]; then           # 正则

# 数字
if [ "$a" -eq "$b" ]; then             # 等于
if [ "$a" -lt "$b" ]; then              # 小于
if [ "$a" -ge "$b" ]; then              # 大于等于

# 文件
if [ -f "$f" ]; then                    # 文件存在
if [ -d "$f" ]; then                    # 目录
if [ -r "$f" ]; then                    # 可读
if [ -x "$f" ]; then                    # 可执行

# 复合
if [ -f "$f" ] && [ -r "$f" ]; then
if [[ -f "$f" && -r "$f" ]]; then
```

## 🔁 循环

```bash
# for 列表
for f in *.txt; do
  echo "$f"
done

# C 风格 for
for ((i=0; i<10; i++)); do
  echo $i
done

# while
while read line; do
  echo "$line"
done < file.txt

# until
until [ "$count" -ge 10 ]; do
  count=$((count + 1))
done

# break / continue
for f in *; do
  [[ "$f" == *.bak ]] && continue
  [[ ! -r "$f" ]] && break
done
```

## 🪛 函数

```bash
log() {
  local level=$1
  shift
  echo "[$(date +%H:%M:%S)] $level $*" >&2
}

log INFO "starting up..."
log ERROR "failed to connect"

# 返回值（0 = 成功）
is_root() {
  [ "$EUID" -eq 0 ]
}

if is_root; then
  echo "root user"
fi
```

## 📥 输入

```bash
# 位置参数
$0    # 脚本名
$1    # 第 1 个参数
$#    # 参数个数
$@    # 所有参数（数组）

# shift
shift                       # 丢掉 $1

# 读 stdin
read -p "name? " name
read -s -p "password? " pass   # 不显示
read -t 5 -p "5 sec timeout: " v   # 超时

# 默认值
name=${1:-anonymous}         # 缺省值
```

## 🔗 字符串

```bash
s="hello world"

# 长度
${#s}                         # 11

# 截取
${s:0:5}                      # hello
${s:6}                        # world

# 替换
${s/world/WORLD}              # hello WORLD
${s//o/0}                     # hell0 w0rld（全部）

# 去掉前缀/后缀
${s#hello}                    # 删最短前缀
${s%world}                    # 删最短后缀

# 大小写
echo "${s^^}"                 # HELLO WORLD（大写）
echo "${s,,}"                 # hello world（小写）

# 包含检查
if [[ "$s" == *"world"* ]]; then
  echo "contains"
fi
```

## 📦 数组

```bash
arr=(apple banana cherry)

# 访问
echo ${arr[0]}
echo ${arr[@]}
echo ${#arr[@]}

# 遍历
for fruit in "${arr[@]}"; do
  echo "$fruit"
done

# 切片
echo ${arr[@]:1:2}            # banana cherry

# 添加
arr+=(date)
arr[10]="kiwi"               # 跳位
```

## 🔗 关联数组（map）

```bash
declare -A ages
ages[alice]=30
ages[bob]=25

echo ${ages[alice]}
for name in "${!ages[@]}"; do
  echo "$name: ${ages[$name]}"
done
```

## 🔁 流程控制

```bash
# case
case "$action" in
  start)  systemctl start nginx ;;
  stop)   systemctl stop nginx ;;
  reload) systemctl reload nginx ;;
  *)      echo "unknown: $action" ;;
esac

# select（菜单）
select opt in start stop restart; do
  case $opt in
    start|stop|restart) break ;;
  esac
done
```

## 📂 进程替换（不用临时文件）

```bash
diff <(ls dir1) <(ls dir2)
# <(cmd) 把命令输出当作"文件"

# 实战
comm -12 <(sort a.txt | uniq) <(sort b.txt | uniq)   # 交集
```

## 🛡 严格模式（写在脚本开头）

```bash
#!/usr/bin/env bash
set -euo pipefail
# -e        出错立即退出
# -u        用了未定义变量报错
# -o pipefail   管道中任一步失败整体失败
IFS=$'\n\t'    # 默认 IFS 包含空格可能引 bug
```

## 🪤 trap - 清理

```bash
trap 'rm -f /tmp/mytmp$$' EXIT         # 脚本退出时清理
trap 'echo "interrupted"; exit 1' INT  # Ctrl+C
trap 'echo "error on line $LINENO"' ERR

cleanup() {
  rm -f /tmp/$tmpfile
}
trap cleanup EXIT
```

## 🧰 实战：写一个部署脚本

```bash
#!/usr/bin/env bash
set -euo pipefail

# 配置
APP=/opt/myapp
NEW_RELEASE="myapp-$(date +%Y%m%d-%H%M%S)"
PORT=8080

# 拉代码
git clone --depth 1 https://github.com/me/myapp.git /tmp/$NEW_RELEASE

# 编译
cd /tmp/$NEW_RELEASE
npm ci
npm run build

# 切版本
mkdir -p $APP/releases
mv /tmp/$NEW_RELEASE $APP/releases/
ln -sfn $APP/releases/$NEW_RELEASE $APP/current

# 重启
systemctl restart myapp

log() { echo "[$(date +%H:%M:%S)] $*" >&2; }
log "Deployed $NEW_RELEASE"
```

## 🔗 下一步

- [变量与参数](/11-shell/variables)
- [数组与字符串](/11-shell/arrays)
- [函数与脚本组织](/11-shell/functions)
- [调试与陷阱](/11-shell/debug)