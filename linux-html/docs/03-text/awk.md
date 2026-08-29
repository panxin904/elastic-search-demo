---
title: awk
date: 2026-08-15  # date-auto-injected
---

# awk - 文本处理语言

> 比 grep 更强大：不仅匹配，还能"处理"。Linux 三剑客之一。

## 🧠 心智模型

```bash
awk 'pattern { action }' file
awk '/error/ { print }' file        # 打印所有匹配行
awk '{ print $1 }' file            # 打印每行第 1 列
```

`awk` 把每行当作记录，列按分隔符（默认空白）拆分。

## 🧪 内置变量

| 变量 | 含义 |
|------|------|
| `$0` | 整行 |
| `$1, $2, ...` | 第 N 列 |
| `NF` | 当前行的列数 |
| `NR` | 当前行号（全局累计） |
| `FNR` | 当前文件行号 |
| `FS` | 输入字段分隔符（默认空白） |
| `OFS` | 输出字段分隔符（默认空格） |
| `RS` | 输入记录分隔符（默认 \n） |

## 📜 基础

```bash
# 打印某列
awk '{print $1}' file                      # 第 1 列
awk '{print $1, $3}' file                  # 第 1、3 列
awk '{print $NF}' file                     # 最后一列

# 自定义分隔符
awk -F: '{print $1}' /etc/passwd           # : 分隔
awk -F',' '{print $1, $3}' data.csv        # , 分隔

# 加行号
awk '{print NR, $0}' file

# 仅打印匹配的行
awk '/error/ {print}' file                 # 等价 grep

# 反选
awk '!/error/ {print}' file
```

## 🔧 流程控制

```bash
# BEGIN / END
awk 'BEGIN { print "开始" } { print NR, $1 } END { print "完成" }' file

# 条件
awk '$3 > 100 { print $1 }' file           # 第 3 列 > 100
awk '$1 == "alice" { print }' file          # 字符串精确
awk 'NR > 1 && NR < 5' file                # 行号区间

# if
awk '{ if ($3 > 80) print "高:", $1; else print "低:", $1 }' file
```

## ➕ 数学

```bash
# 求和
awk '{ sum += $1 } END { print sum }' file

# 平均
awk '{ sum += $1; n++ } END { print sum/n }' file

# 最大 / 最小
awk 'NR == 1 { max = $1 } $1 > max { max = $1 } END { print max }' file

# 实战：统计 nginx 状态码
awk '{ count[$9]++ } END { for (code in count) print code, count[code] }' access.log
```

## 📦 字符串函数

| 函数 | 作用 |
|------|------|
| `length(s)` | 长度 |
| `substr(s, i, n)` | 子串 |
| `split(s, a, sep)` | 拆分到数组 a |
| `gsub(regex, replace, s)` | 全局替换 |
| `sub(regex, replace, s)` | 替换第一处 |
| `toupper(s)` / `tolower(s)` | 大小写 |
| `index(s, t)` | t 在 s 中的位置 |

```bash
# 提取邮箱用户名
awk -F@ '{print $1}' emails.txt

# 替换
awk '{ gsub(/foo/, "bar"); print }' file

# 大写
awk '{print toupper($1)}' file
```

## 🛠 实战组合

```bash
# 列出 /etc/passwd 中所有用户
awk -F: '{print $1}' /etc/passwd

# 统计每个 IP 访问次数（nginx）
awk '{ count[$1]++ } END { for (ip in count) print count[ip], ip }' access.log | sort -rn | head

# 取进程 PID + 命令
ps aux | awk '{print $2, $11}'

# 把 CSV 转 TSV
awk -F, 'BEGIN {OFS="\t"} {$1=$1; print}' file.csv

# 日志中找 5xx 错误
awk '$9 ~ /^5/ {print}' access.log

# 用 : 分隔，取第 1、第 3 列
awk -F: '{print $1 ":" $3}' /etc/passwd
```

## 🆚 awk vs 其他

| | grep | sed | awk |
|--|------|-----|-----|
| 匹配 | ✅ | ✅ | ✅ |
| 替换 | ❌ | ✅ | ✅ |
| 处理列 | ❌ | ❌ | ✅ |
| 计算 | ❌ | 弱 | ✅ |

## 🔗 下一步

- [sed](/03-text/sed)
- [sort / uniq](/03-text/sort-uniq)
- [xargs / find 配合](/03-text/xargs)