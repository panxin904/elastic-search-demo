---
title: 数组与字符串
date: 2026-08-15  # date-auto-injected
---

# 数组与字符串处理

> shell 的字符串处理比 Python 弱，但日常够用。

## 📦 索引数组

```bash
# 声明
arr=()
arr=(a b c d)

# 赋值（按索引）
arr[0]="first"
arr[1]="second"
arr[10]="tenth"               # 跳位可以

# 访问
echo ${arr[0]}                 # first
echo ${arr[@]}                 # 全部
echo ${arr[*]}                 # 同上
echo ${#arr[@]}                # 元素个数
echo ${!arr[@]}                # 所有索引

# 切片
echo ${arr[@]:1:2}             # 从 1 开始取 2 个
echo ${arr[@]:2}               # 从 2 开始到末尾

# 添加
arr+=(e f g)                  # 追加多个

# 删除
unset arr[2]                  # 删一项
unset arr                     # 删整个
```

## 📋 关联数组（map）

```bash
declare -A ages
ages[alice]=30
ages[bob]=25
ages[carol]=35

# 访问
echo ${ages[alice]}
echo ${!ages[@]}               # 所有 key
echo ${ages[@]}                # 所有 value
echo ${#ages[@]}               # key 个数

# 遍历
for name in "${!ages[@]}"; do
  echo "$name: ${ages[$name]}"
done
```

## 🔤 字符串操作

### 长度

```bash
s="hello world"
echo ${#s}                     # 11
```

### 切片

```bash
echo ${s:0:5}                  # hello（从 0 取 5 个）
echo ${s:6}                    # world（从 6 到末尾）
echo ${s: -5}                  # world（最后 5 个；空格必加）
echo ${s:0: -6}                # hello（除最后 6 个）
```

### 替换

```bash
# 替换第一处
echo ${s/world/WORLD}          # hello WORLD

# 全部替换
echo ${s//o/0}                 # hell0 w0rld

# 替换前缀 / 后缀
echo ${s/#hello/HI}            # HI world（仅前缀）
echo ${s/%world/!}              # hello !（仅后缀）
```

### 去掉前缀 / 后缀

```bash
f=/var/log/app.log

# 删最短前缀
echo ${f#*/}                   # log/app.log

# 删最长前缀
echo ${f##*/}                  # app.log

# 删最短后缀
echo ${f%.*}                   # /var/log/app

# 删最长后缀
echo ${f%%.*}                  # /var/log/app（扩展名在最后）

# 实战：取文件名 / 扩展名 / 目录
file=/home/user/app.log.tar.gz
echo "文件名: ${file##*/}"        # app.log.tar.gz
echo "扩展名: ${file##*.}"        # gz
echo "去扩展名: ${file%.*}"       # /home/user/app.log.tar
echo "目录: ${file%/*}"           # /home/user
```

### 大小写

```bash
s="Hello World"

echo "${s^^}"                  # HELLO WORLD（大写）
echo "${s,,}"                  # hello world（小写）
echo "${s~}"                   # hELLO wORLD（首字母小写，bash 4+）

# 字符类转换
s="abc"
echo "${s^^[ab]}"              # ABc（只转 ab）
```

## 🔢 数组操作

### 排序 / 去重

```bash
# 排序
arr=(5 2 8 2 9 1)
sorted=($(printf '%s\n' "${arr[@]}" | sort -n))
echo "${sorted[@]}"            # 1 2 2 5 8 9

# 去重（先 sort 才能去重）
unique=($(printf '%s\n' "${arr[@]}" | sort -u))

# 同时去重并保留顺序（awk）
arr=(c a b a c)
unique=($(printf '%s\n' "${arr[@]}" | awk '!seen[$0]++'))
echo "${unique[@]}"            # c a b
```

### 关联数组操作

```bash
declare -A user
user=([name]=alice [age]=30 [city]=Beijing)

# 转 JSON
echo "{"
for k in "${!user[@]}"; do
  echo "  \"$k\": \"${user[$k]}\","
done
echo "}"

# 排序后输出
for k in $(echo "${!user[@]}" | tr ' ' '\n' | sort); do
  echo "$k => ${user[$k]}"
done
```

## 🔗 实战：处理 CSV

```bash
# 简单解析
while IFS=, read -r name age city; do
  echo "Name: $name, Age: $age, City: $city"
done < data.csv

# 带引号的复杂 CSV（用 python）
python3 -c "
import csv, sys
for row in csv.reader(sys.stdin):
    print(row)
" < data.csv
```

## 🛠 实战：批量重命名

```bash
# 把 .jpeg 改成 .jpg
for f in *.jpeg; do
  mv "$f" "${f%.jpeg}.jpg"
done

# 加前缀
for f in *.log; do
  mv "$f" "bak-$f"
done

# 批量改日期
for f in IMG_2024*.jpg; do
  d=$(echo "$f" | grep -oE '2024[0-9]{4}')
  new="renamed-$d-${f#IMG_2024*}"
  mv "$f" "$new"
done
```

## 🧹 删除空行 / 重复行

```bash
# 删空行
grep -v '^$' file > file2
sed '/^$/d' file > file2
awk 'NF' file > file2              # awk 智能删除"空"

# 去重（保留顺序）
awk '!seen[$0]++' file > file2
```

## 🪤 字符串转数组

```bash
# IFS 分隔
sentence="a b c d"
words=($sentence)
echo "${words[@]}"               # a b c d

# read -ra
read -ra parts <<< "x,y,z,1,2,3"
echo "${parts[@]}"

# 自定义分隔符
text="apple,banana,cherry"
IFS=',' read -ra fruits <<< "$text"
echo "${fruits[@]}"
```

## 🛡 安全注意

```bash
# 永远加双引号（防空格 / 通配）
rm "$file"                       # ✅
rm $file                         # ❌

# 字符串比较
if [[ "$str" == *"pattern"* ]]; then  # ✅ 用 [[ ]]
if [ "$str" = "pattern" ]; then         # ⚠ 用 [ ] 时要引
```

## 🔗 下一步

- [bash 基础语法](/11-shell/bash-syntax)
- [变量与参数](/11-shell/variables)
- [函数与脚本组织](/11-shell/functions)
- [调试与陷阱](/11-shell/debug)


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [devops](https://java-px.bot.cd/devops/):DevOps 自动化
- [cloud-native](https://java-px.bot.cd/cloud-native/):云原生
- [network](https://java-px.bot.cd/network/):Linux 网络
