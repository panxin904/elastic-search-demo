---
title: 调试与陷阱
---

# 调试与陷阱

> shell 的"沉默失败"特性是最大杀手，这章讲怎么调试 + 常见坑。

## 🐛 调试模式

### set -x（命令追踪）

```bash
#!/usr/bin/env bash
set -x           # 打印每条命令
# ...
set +x           # 关闭
```

输出：

```
+ echo "hello"
+ test -f /tmp/foo
+ echo "next"
```

`PS4` 控制 trace 前缀：

```bash
export PS4='+ ${LINENO}: ${FUNCNAME[0]:-main}: '
# 输出：+ 42: main: echo "hello"
```

### 局部追踪

```bash
# 只对某个函数追踪
set -x
my_function
set +x
```

### bashdb（交互式调试）

```bash
sudo apt install bashdb
bashdb script.sh

# 调试命令
# n - 单步
# s - 进入函数
# c - 继续
# b N - 在第 N 行打断点
# p VAR - 打印变量
# q - 退出
```

## 📝 echo / printf 调试

```bash
log() { echo "[DEBUG] $*" >&2; }

log "now in main, file=$file"
log "var x = $x"

# 或 DEBUG trap（自动打印每行前）
trap 'echo "[DEBUG] $LINENO: x=$x" >&2' DEBUG
```

## 🪤 set -x 与 set -v

```bash
# -x: 命令展开后打印（看实际跑了什么）
set -x
echo $var                      # + echo something

# -v: 命令展开前打印
set -v
echo $var                      # echo $var
```

`-x` 更常用。

## 🔥 严格模式（防沉默失败）

```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# -e        出错立即退出
# -u        用了未定义变量报错
# -o pipefail   管道任一失败整体失败
# IFS         防 word splitting
```

**生产脚本默认就开**。

## 🪤 set 选项目录

| 选项 | 作用 |
|------|------|
| `-e` | 命令返回非 0 立即退出 |
| `-u` | 用未定义变量报错 |
| `-o pipefail` | 管道失败检测 |
| `-x` | 打印每条命令 |
| `-v` | 打印原始命令（展开前） |
| `-E` | 让 ERR trap 继承到函数 / 子 shell |
| `-T` | DEBUG / ERR trap 继承到子 shell |

```bash
set -euo pipefail                # 最常用组合
```

## 🪤 trap 调试

```bash
# ERR trap：每次出错打印
trap 'echo "ERROR at line $LINENO" >&2; exit 1' ERR

# DEBUG trap：每行前打印
trap 'echo "[LINE $LINENO]"' DEBUG

# EXIT trap：脚本退出时
trap 'rm -f /tmp/mytmp' EXIT
```

## ⚠️ 经典陷阱

### 1. 没引号 = 灾难

```bash
# ❌ 文件名有空格就出错
for f in $(ls); do echo "$f"; done
# 文件 "my file.txt" 被切成 "my" 和 "file.txt"

# ✅
for f in *; do echo "$f"; done
# 或
for f in "$(ls)"; do echo "$f"; done   # 但仍要小心

# 永远加引号
rm $file                         # ❌
rm "$file"                       # ✅
```

### 2. 未初始化变量

```bash
# ❌ typo 会静默失败
echo $USER                      # 空字符串
if [ "$USER" = "alice" ]; then   # 永远 false
  ...
fi

# ✅ set -u
set -u
echo $USER                      # 立即报错
```

### 3. [ vs [[

```bash
# [ 是 POSIX，[[ 是 bash 扩展
if [ "$a" = "$b" ]; then         # ✅
if [[ "$a" == "$b" ]]; then      # ✅，且支持正则
if [[ "$a" == *"x"* ]]; then     # ✅，通配
if [ "$a" = *"x"* ]; then        # ❌ 字面比较
```

### 4. 空格 in [ ]

```bash
if [ $a = $b ]; then            # ❌ "[" 后面必须有空格
if [ $a=$b ]; then               # ❌ 会变成 string 比较
if [ "$a" = "$b" ]; then        # ✅
```

### 5. 整数比较 vs 字符串比较

```bash
# ❌ 字符串比较
if [ "$a" -gt "$b" ]; then      # 报错（如 a 为空）
if [ "$a" > "$b" ]; then        # 字符串字典序

# ✅ 整数比较
if [[ "$a" -gt "$b" ]]; then
if (( a > b )); then            # 算术上下文

# 注意：[[ ... ]] 的 > 是字符串
if [[ "10" > "9" ]]; then        # false（字典序："1" < "9"）
```

### 6. 命令替换裁掉尾部换行

```bash
files=$(ls)                      # 末尾换行丢了！
# 改：
files=($(ls))                    # 数组
# 或
files="$(ls)"                    # 字符串保留
```

### 7. 子 shell 修改变量不返回

```bash
# ❌ counter 还是 0
counter=0
( counter=100 )                 # 子 shell
echo $counter                    # 0

# ✅ 同一 shell
counter=0
counter=100
echo $counter                    # 100
```

### 8. `cd` 失败还在原目录

```bash
# ❌
cd /some/path || true
rm -rf *

# ✅
cd /some/path || exit 1
rm -rf *
```

### 9. `find ... | while` 的变量问题

```bash
# ❌ while 在子 shell，$i 不回来
i=0
find . -name '*.txt' | while read f; do
  i=$((i+1))
done
echo $i                          # 0

# ✅ process substitution
i=0
while read f; do
  i=$((i+1))
done < <(find . -name '*.txt')
echo $i                          # 正确
```

### 10. 信号下后台进程

```bash
# ❌ Ctrl+C 会杀掉整个脚本，包括清理逻辑
trap "rm -f /tmp/lock" EXIT

# ✅ 用 sleep 长时间运行的脚本在子 shell 时，Ctrl+C 只杀子 shell
( sleep 60 ) &
wait
```

## 🩺 调试清单

```bash
# 1. 加上头部
#!/usr/bin/env bash
set -euo pipefail

# 2. 调试时
set -x
PS4='+ ${LINENO}: '

# 3. 关键变量打日志
log() { echo "[$(date +%T)] $*" >&2; }

# 4. 跑 dry-run
# 在命令前加 echo "would run:"：
echo "would run: rm -rf $dir"
# 改成
echo "rm -rf $dir"              # 临时只打
```

## 🧰 shellcheck（静态分析）

```bash
sudo apt install shellcheck

shellcheck script.sh
# 输出问题和建议：
# Line 12: Use $(...) instead of legacy `...`. [SC2006]
# Line 24: Quote this to prevent word splitting. [SC2086]
```

CI 集成：

```yaml
# GitHub Actions
- name: ShellCheck
  run: |
    sudo apt install shellcheck
    shellcheck scripts/*.sh
```

## 🔗 下一步

- [bash 基础语法](/11-shell/bash-syntax)
- [变量与参数](/11-shell/variables)
- [数组与字符串](/11-shell/arrays)
- [函数与脚本组织](/11-shell/functions)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [devops](https://java-px.bot.cd/devops/):DevOps 自动化
- [cloud-native](https://java-px.bot.cd/cloud-native/):云原生
- [network](https://java-px.bot.cd/network/):Linux 网络
