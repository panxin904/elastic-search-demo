---
title: find / fd
---

# find / fd — 文件查找工具集

> <span class="kg-badge kg-badge--tools">工具集</span>
> 递归查找 · 高级过滤 · 性能与场景

find 是 POSIX 标准，fd 是 Rust 写的现代化替代。它们都能递归查找文件、过滤、按动作执行命令。

## 1. find 基础

```bash
# 按名字
find / -name "*.log"
find /home -iname "*.JPG"     # 不区分大小写

# 按类型
find / -type f                # 普通文件
find / -type d                # 目录
find / -type l                # 符号链接
find / -type b                # 块设备

# 按时间
find / -mtime -7              # 7 天内修改
find / -mtime +30             # 30 天前修改
find / -mmin -10              # 10 分钟内修改
find / -newer file.txt        # 比 file.txt 新

# 按大小
find / -size +100M
find / -size -1k

# 按权限
find / -perm 755
find / -user alice
find / -group developers
```

## 2. find 的逻辑运算

```bash
# 与（默认）
find / -name "*.log" -size +100M

# 或（-o）
find / \( -name "*.log" -o -name "*.txt" \) -size +10M

# 非（!）
find / -name "*.log" ! -path "/proc/*"
```

## 3. find 的动作

| 动作 | 含义 |
|------|------|
| `-print` | 打印路径（默认） |
| `-print0` | 用 \0 分隔（适合 xargs） |
| `-ls` | 类似 ls -l 输出 |
| `-exec cmd {} +` | 用每个文件作为参数执行命令 |
| `-exec cmd {} \;` | 每个文件启动一个 cmd |
| `-delete` | 删除 |
| `-fprintf` | 自定义格式输出 |

```bash
# 删 100 天前的 log
find /var/log -name "*.log" -mtime +100 -delete

# 批量改权限
find /home -type f -name "*.txt" -exec chmod 644 {} \;

# 用 xargs 处理
find / -name "*.conf" -print0 | xargs -0 grep "Listen"
```

## 4. 高级 find 技巧

### 4.1 -exec 与 + 的差别

```bash
# \; 每个文件启动一次
find . -exec md5sum {} \;
# md5sum file1
# md5sum file2
# md5sum file3

# + 所有文件一次传（更快）
find . -exec md5sum {} +
# md5sum file1 file2 file3
```

`+` 模式更高效，优先用。

### 4.2 安全删除

```bash
# 先 -print 看会删什么
find /var/log -name "*.log" -mtime +100 -print

# 再 -delete
find /var/log -name "*.log" -mtime +100 -delete
```

### 4.3 -regex / -iregex

```bash
find . -regex '.*\.\(jpg\|png\)$'
find . -iregex '.*\.\(jpg\|png\)$'
```

### 4.4 -depth

按深度优先（先处理深层）：

```bash
find / -depth -type d -empty -delete   # 删空目录
```

### 4.5 限深

```bash
find / -maxdepth 3 -name "*.conf"
find /home/alice -mindepth 2 -type f
```

### 4.6 -prune 排除目录

```bash
find / -path /proc -prune -o -name "*.log" -print
find / -path "*/node_modules" -prune -o -name "*.js" -print
```

## 5. fd — 现代替代

```bash
# 安装
apt install fd-find   # Debian/Ubuntu
dnf install fd-find   # Fedora
brew install fd       # macOS

# 默认用法（几乎等同 find）
fd log /var
fd '\.log$' /var

# 不区分大小写
fd -i readme

# 排除
fd -E node_modules -E .git
```

### 5.1 fd 的优势

- **默认忽略**：`node_modules`、`.git`、隐藏文件等（可改）
- **并行执行**：多线程搜索
- **彩色输出**：文件类型着色
- **Git 集成**：自动只搜 tracked 文件
- **更简单的正则**

### 5.2 fd 实战

```bash
# 同 git status 的文件
fd --type f                  # git tracked files

# 限定扩展名
fd -e rs                     # 只找 .rs 文件
fd -e py

# 并行执行命令
fd -e jpg -x convert {} {.}.png  # 每个 jpg 转 png

# 含内容搜索
fd -e py --exec rg "TODO"
```

## 6. find + xargs 安全姿势

```bash
# 关键：-print0 + -0（处理文件名中的空格/换行）
find . -name "*.log" -print0 | xargs -0 -I {} cp {} /backup/

# 或者 find 自带 -exec
find . -name "*.log" -exec cp {} /backup/ \;
```

## 7. 性能对比

```bash
# find 在大目录慢
time find / -name "*.log"

# fd 通常快 5-10 倍
time fd log /
```

fd 用 Rust 写，**多线程 + 智能 ignore + 更小 IO 调用**，在大型 repo / 文件系统上性能远好。

## 8. 实战场景

### 8.1 清理缓存

```bash
find /var/cache -type f -atime +30 -delete
```

### 8.2 找大文件

```bash
find / -type f -size +1G -exec du -h {} \; | sort -h
```

### 8.3 找权限问题

```bash
find / -type f -perm 777
```

### 8.4 找空目录 / 空文件

```bash
find / -type d -empty
find / -type f -empty -size 0
```

### 8.5 批量重命名

```bash
fd -e jpg -x mv {} "{}.bak"
```

## 9. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| find = POSIX 标准 | "find=标准" |
| fd = 现代替代 | "fd=5x 快" |
| -print0 + -0 安全 | "-print0=防空格" |
| -exec + 比 \; 快 | "+=批量" |
| -prune 排除目录 | "prune=剪枝" |

## 参考

- findutils 文档
- fd-find GitHub：<https://github.com/sharkdp/fd