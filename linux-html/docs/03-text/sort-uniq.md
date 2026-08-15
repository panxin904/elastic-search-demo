---
title: sort / uniq
---

# sort / uniq

> 排序与去重，看似简单，组合起来是日志分析的利器。

## 📊 sort - 排序

```bash
sort file                          # 字典序（默认）
sort -n file                       # 数值
sort -r file                       # 反序
sort -k 2 file                     # 按第 2 列
sort -t: -k 3 -n /etc/passwd       # : 分隔，按第 3 列数值
sort -u file                       # 排序去重
sort -h file                       # 人类可读大小（1K / 2M / 3G）

# 多关键字
sort -k 1,1 -k 2n file             # 第 1 列字典序，第 2 列数值
sort -k 1 -k 3nr file              # 第 1 列字典序，第 3 列数值反序

# 输出
sort -o out file                   # 输出到文件
sort -c file                       # 检查是否已排序（不输出）

# 大小写
sort -f file                       # 忽略大小写
sort -d file                       # 仅字母数字，空格 + 其他先
```

## 🪄 uniq - 去重 / 计数

uniq **只能去重相邻行**，所以先 sort。

```bash
sort file | uniq                   # 去重
sort file | uniq -c                # 每行 + 出现次数
sort file | uniq -d                # 仅显示重复行
sort file | uniq -u                # 仅显示唯一行

# 跳过前 N 个字段
sort file | uniq -f 1              # 跳过第 1 列
sort file | uniq -s 5              # 跳过前 5 字符

# 大小写
sort file | uniq -i                # 忽略大小写
```

## 🛠 实战组合

```bash
# 出现次数 top 10
sort file | uniq -c | sort -rn | head

# nginx 访问最多的 IP
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head

# 状态码统计
awk '{print $9}' access.log | sort | uniq -c | sort -rn

# 找出唯一 IP
awk '{print $1}' access.log | sort -u | wc -l

# 出现超过 100 次的 IP
awk '{print $1}' access.log | sort | uniq -c | awk '$1 > 100' | sort -rn

# 日志中错误类型 top
grep 'ERROR' app.log | awk '{print $5}' | sort | uniq -c | sort -rn | head

# 找两个文件的差异
diff <(sort a.txt) <(sort b.txt)
comm -12 <(sort a.txt) <(sort b.txt)    # 共同
comm -23 <(sort a.txt) <(sort b.txt)    # 只在 a
comm -13 <(sort a.txt) <(sort b.txt)    # 只在 b
```

## 🧠 LC_ALL=C 加速

```bash
# 字节比较，避免 locale 转换
LC_ALL=C sort huge.txt          # 10x 加速
LC_ALL=C grep pattern huge.txt
```

## 📊 大文件优化

```bash
# 外部排序（内存不够时）
sort -S 1G -T /tmp huge.txt
# -S 内存限制 -T 临时目录

# 不需要真排序，只去重
awk '!seen[$0]++' file               # 等价 sort -u 但更省内存
```

## 🛠 实战：分析 CSV

```bash
# 假设 data.csv: name,age,city
sort -t, -k 2 -n data.csv           # 按年龄
sort -t, -k 3 -k 2n data.csv        # 先按城市，再按年龄
sort -t, -u -k 1 data.csv           # 按 name 去重
```

## 🔗 下一步

- [grep](/03-text/grep)
- [awk](/03-text/awk)
- [xargs / find 配合](/03-text/xargs)