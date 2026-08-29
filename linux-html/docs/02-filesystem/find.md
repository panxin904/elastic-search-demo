---
title: find 查找
date: 2026-08-15  # date-auto-injected
---

# find - 查找文件

> 最高频的搜索命令。比 `ls -R` 强大得多。

## 📜 基础

```bash
find /etc -name '*.conf'             # 找 /etc 下 .conf 文件
find . -type f                       # 仅文件
find . -type d                       # 仅目录
find . -type l                       # 仅软链
```

## 🎯 条件组合

```bash
# 按大小
find . -size +100M                   # 大于 100MB
find . -size -1k                     # 小于 1KB
find . -size +10M -size -100M        # 区间

# 按时间（天）
find . -mtime -7                      # 7 天内修改
find . -mtime +30                     # 30 天前修改
find . -atime +90                     # 90 天前访问

# 按分钟
find . -mmin -60                      # 60 分钟内改

# 按用户
find / -user alice
find / -uid 1000
find / -group dev

# 按权限
find / -perm 644                     # 权限等于 644
find / -perm -u+w                    # 至少 u+w
find / -perm /u+w                    # 任一为 u+w

# 按文件名
find . -name '*.log'                 # 通配符（要加引号！）
find . -iname 'README'               # 忽略大小写
find . -name '*.js' -not -path '*/node_modules/*'   # 排除

# 多个条件
find . -name '*.log' -size +10M       # AND
find . -name 'a*' -o -name 'b*'       # OR
```

## 🧰 -exec / -delete

```bash
# 找到后删
find /tmp -name '*.tmp' -mtime +7 -delete

# 找并执行命令
find . -name '*.js' -exec wc -l {} \;
find . -name '*.js' -exec wc -l {} +
find . -name '*.js' -exec rm {} \;

# {} 是占位符，\; 或 + 是结束符
# + 比 \; 快（一次传多个文件）

# 找并询问
find . -name '*.bak' -ok rm {} \;    # 每次删前 y/n
```

## 🛠 实战组合

```bash
# 最近 1 天修改的文件
find /var/log -mtime -1 -ls

# 找大文件并按大小排序
find / -size +500M -type f -exec ls -lh {} \; | sort -k5 -h

# 找空文件 / 空目录
find . -type f -empty
find . -type d -empty

# 找无属主文件（属主被删后留下）
find / -nouser -o -nogroup

# 按 inode 找硬链
find / -inum 12345

# 找被设置 SUID 的可执行文件
find / -perm -4000 -type f
```

## 🔗 与 grep 配合

```bash
# 找文件 + 在文件内搜索
find . -name '*.log' -exec grep -l 'error' {} +

# 替代：grep -r
grep -r 'error' --include='*.log' .
```

## 🔗 与 xargs 配合

```bash
# 大批量时 xargs 比 -exec 更高效
find . -name '*.log' | xargs rm
find . -name '*.js' -print0 | xargs -0 wc -l   # 处理文件名带空格
```

## 🔧 加速技巧

```bash
# 排除 /proc /sys /dev
find / -path '/proc' -prune -o -path '/sys' -prune -o -name '*.log' -print

# 用 locate 更快（基于索引）
sudo updatedb
locate nginx.conf

# 限制深度
find / -maxdepth 3 -name 'nginx'

# 跳过其他文件系统
find / -xdev -name '*.log'
```

## 🆚 替代品

| 工具 | 优点 |
|------|------|
| `fd` | 比 find 快 10x、语法友好 |
| `locate` | 基于索引，毫秒级（依赖 updatedb） |
| `ripgrep --files` | 按内容 + 文件名搜 |

```bash
# fd（推荐安装）
sudo apt install fd-find      # 命令叫 fdfind
fd '*.log'                   # 极简语法

# locate
sudo apt install mlocate && sudo updatedb
locate nginx.conf
```

## 🔗 下一步

- [grep](/03-text/grep)
- [xargs / find 配合](/03-text/xargs)
- [ls / cp / mv](/02-filesystem/ls)