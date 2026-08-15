---
title: sed
---

# sed - 流编辑器

> **s**tream **ed**itor。批量改文本最常用。

## 📜 基础

```bash
sed 's/old/new/' file                  # 单行替换（只替换第一处）
sed 's/old/new/g' file                 # 全局替换
sed -i 's/old/new/g' file             # 直接改文件（in-place）
sed -i.bak 's/old/new/g' file         # 先备份 file.bak 再改
```

## 📍 行选择

```bash
# 行号
sed '5d' file                         # 删第 5 行
sed '1,3d' file                       # 删 1-3 行
sed '/pattern/d' file                 # 删匹配行
sed '2a\hello' file                   # 第 2 行后插入 hello
sed '2i\hello' file                   # 第 2 行前插入
sed '2c\hello' file                   # 第 2 行替换为 hello

# 区间
sed -n '10,20p' file                  # 打印 10-20 行
sed -n '/start/,/end/p' file          # 区间打印
sed -n '/pattern/p' file              # 仅匹配行
```

## 🔄 替换

```bash
# 基础替换
sed 's/foo/bar/' file                 # 第一处
sed 's/foo/bar/g' file                # 所有

# 替换特定位置
sed 's/foo/bar/2' file                # 每行第 2 处
sed 's/foo/bar/2g' file               # 第 2 处及之后

# 大小写
sed 's/[A-Z]/\L&/g' file              # 大写转小写（GNU sed）
sed 's/[a-z]/\U&/g' file              # 小写转大写

# 分隔符
sed 's|/usr/local|/opt|g' file        # 用 | 避免 / 冲突
sed 's@/usr/local@/opt@g' file        # @ 也行

# 多命令
sed -e 's/a/b/' -e 's/c/d/' file
sed 's/a/b/; s/c/d/' file
```

## 🎯 行匹配

```bash
# 行首 / 行尾
sed '/^#/d' file                      # 删注释行（# 开头）
sed '/^$/d' file                      # 删空行

# 范围
sed '/start/,/end/d' file             # 删除区间
sed '/start/,/end/s/old/new/g' file   # 区间内替换

# 反选
sed '/pattern/!d' file                # 仅保留匹配行
sed '/pattern/!p' file                # 打印非匹配行
```

## 🛠 实战

```bash
# 批量改后缀
for f in *.html; do
  sed -i 's/old-class/new-class/g' "$f"
done

# 删除文件最后一行
sed -i '$d' file

# 添加一行到开头
sed -i '1i\# Auto-generated' file

# 添加一行到结尾
sed -i '$a\# end' file

# 大文件替换（流式处理）
sed 's/foo/bar/g' huge.txt > new.txt

# 多文件批量改
find . -name '*.conf' -exec sed -i 's/old_host/new_host/g' {} +

# 提取某些行
sed -n '1,5p; 10p' file              # 1-5 行 + 第 10 行
```

## 📊 与 awk 的取舍

| 场景 | 用 |
|------|-----|
| 简单替换 | sed |
| 列操作 | awk |
| 流式处理 | sed 更快 |
| 复杂条件 | awk 更强 |

```bash
# 例子：取某进程的 PID + 命令
ps aux | sed -n '/nginx/p' | awk '{print $2}'

# 取第 5 列大于 100 的行
awk '$5 > 100' file
```

## 🔗 下一步

- [awk](/03-text/awk)
- [sort / uniq](/03-text/sort-uniq)
- [xargs / find 配合](/03-text/xargs)