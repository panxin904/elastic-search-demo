---
title: grep
---

# grep - 文本搜索

> 最高频文本命令。**g**lobal **r**egular **e**xpression **p**rint。

## 📜 基础

```bash
grep 'pattern' file               # 基础
grep 'pattern' file1 file2       # 多文件
grep -r 'pattern' dir             # 递归
grep -i 'pattern' file            # 忽略大小写
grep -n 'pattern' file            # 显示行号
grep -c 'pattern' file            # 只统计次数
grep -l 'pattern' dir/            # 只列出匹配的文件名
grep -L 'pattern' dir/            # 列出不匹配的文件
```

## 🔍 上下文

```bash
grep -A 3 'error' file             # 匹配后 3 行
grep -B 2 'error' file             # 匹配前 2 行
grep -C 5 'error' file             # 前后各 5 行
```

## ⚡ 反向 / 精确

```bash
grep -v 'pattern' file            # 反选（不要匹配的行）
grep -w 'word' file               # 全词匹配（不匹配 partword）
grep -x 'exact line' file         # 整行匹配
```

## 🔠 正则

```bash
# 基础正则（BRE）
grep '^start' file                # 行首
grep 'end$' file                  # 行尾
grep 'a.b' file                   # 任意字符（a + 任意 + b）
grep 'a*' file                    # 0 或多个 a
grep '[0-9]' file                 # 数字
grep '[abc]' file                 # a / b / c 之一
grep '\bword\b' file              # 单词边界

# 扩展正则（ERE）
grep -E 'err|warn' file           # 或
grep -E 'a{2,4}' file             # 2-4 个 a
grep -E '(ab)+' file              # 一组
grep -E 'foo|bar' file            # 多个匹配

# PCRE（-P，最强大）
grep -P '\d{3}-\d{4}' file       # Perl 风格
```

## 📂 目录 / 文件

```bash
# 递归 + 限制
grep -rn 'TODO' --include='*.ts' src/   # 只看 .ts
grep -rn 'TODO' --exclude-dir=node_modules --exclude-dir=.git .
grep -rl 'TODO' src/                    # 只列文件名

# 跳过二进制
grep -rI 'pattern' .                    # I = 忽略二进制

# 多个模式
grep -E 'foo|bar' file
grep -e 'foo' -e 'bar' file

# 取反多个
grep -v -E 'foo|bar' file
```

## 🛠 实战组合

```bash
# 查包含 ERROR 但不含 DEBUG 的行
grep 'ERROR' file | grep -v 'DEBUG'

# 统计每个错误出现次数
grep -oE 'ERROR [a-zA-Z_]+' app.log | sort | uniq -c | sort -rn

# 找进程并 grep
ps aux | grep -E 'nginx|node'

# 查文件里以 # 开头的注释
grep -E '^\s*#' config

# 找 404 的请求
grep ' 404 ' access.log

# 大文件加速
LC_ALL=C grep 'pattern' huge.txt    # 字节级比较，10x 加速
```

## 🚦 退出码

| 退出码 | 含义 |
|--------|------|
| 0 | 找到 |
| 1 | 没找到 |
| 2 | 错误（文件不存在等） |

常用于 shell 脚本：

```bash
if grep -q 'ERROR' log; then
  echo "出错了"
fi
```

## 🆚 替代品

| 工具 | 何时用 |
|------|--------|
| `ripgrep (rg)` | 默认首选（更快的 grep） |
| `ag` | 类似 rg |
| `git grep` | 仓库内（自动忽略 .gitignore） |

```bash
# ripgrep（推荐安装）
sudo apt install ripgrep
rg 'pattern'                      # 极简 + 快
rg -i 'pattern'                    # 大小写
rg 'pattern' -g '!node_modules'    # 排除
```

## 🔗 下一步

- [awk](/03-text/awk)
- [sed](/03-text/sed)
- [xargs / find 配合](/03-text/xargs)