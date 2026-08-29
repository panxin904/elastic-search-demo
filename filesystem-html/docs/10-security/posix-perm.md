---
title: POSIX 权限模型
date: 2026-08-15  # date-auto-injected
---

# POSIX 权限模型 — Unix 文件权限的基础

> <span class="kg-badge kg-badge--security">安全权限</span>
> 三类用户 · rwx · 实战管理

POSIX 权限模型是 Unix/Linux 文件系统的**基础权限系统**。所有其他权限机制（ACL、SELinux）都是在它之上扩展。

## 1. 三类用户

每个文件 / 目录有三组权限：

```
-rwxr-xr--  1 alice developers 4096 Jan  1 12:00 myfile
 ▲▲▲▲▲▲▲▲▲▲▲
 │││││││││└└└┘└└└ other (其他人)
 │││││││││││
 ││││││└└└└└└─ group (所属组)
 ││││└└└└─────── user (owner)
 │││└───────────── setuid/setgid/sticky
 │└└────────────── file type (-/d/l/b)
```

- **user (u)**：文件所有者
- **group (g)**：所属组
- **other (o)**：其他人

## 2. 三种权限

| 权限 | 文件 | 目录 |
|------|------|------|
| **r** (read) | 读取内容 | 列出目录项 (ls) |
| **w** (write) | 修改内容 | 添加/删除文件 |
| **x** (execute) | 执行 | 进入目录 (cd) |

**目录权限的核心**：

- **r** 没 **x** = 能列文件名，不能访问文件元数据（怪异的 `ls -l` 效果）
- **x** 没 **r** = 能访问文件但不能列出（cd 进入后 ls 失败）
- **w** 在目录 = 能 add / remove 文件（即使你没文件自己的写权限）

## 3. 八进制速记

| 八进制 | 二进制 | 含义 |
|--------|--------|------|
| 0 | 000 | --- |
| 1 | 001 | --x |
| 2 | 010 | -w- |
| 3 | 011 | -wx |
| 4 | 100 | r-- |
| 5 | 101 | r-x |
| 6 | 110 | rw- |
| 7 | 111 | rwx |

常用值：

- `755` = `rwxr-xr-x`（所有者全权，其他只读+执行）
- `644` = `rw-r--r--`（所有者读写，其他只读）
- `600` = `rw-------`（仅所有者）
- `777` = `rwxrwxrwx`（**危险**，无脑全开）

## 4. 实战命令

```bash
# chmod
chmod 755 file
chmod u+x file
chmod g+w file
chmod o-r file
chmod -R 644 /var/log/app/   # 递归

# 数字模式
chmod 600 ~/.ssh/id_rsa      # 私钥

# 特殊位
chmod u+s /usr/bin/passwd     # setuid
chmod g+s /shared/dir         # setgid（新建文件继承组）
chmod +t /tmp                 # sticky（仅 owner 能删自己文件）
```

## 5. chown / chgrp

```bash
chown alice file
chown alice:developers file
chown -R alice:developers /project/
chgrp developers file
```

## 6. umask

新建文件 / 目录时的**默认权限掩码**：

```bash
umask
# 0022 → 新建文件 644（755-022），目录 755

# 设置
umask 007  # → 新建文件 660，目录 770
```

`umask 022` = 默认。开发服务器 `umask 002`（组成员共享）。

## 7. 实战：常见配置

```bash
# 私钥
chmod 600 ~/.ssh/id_rsa

# 公钥
chmod 644 ~/.ssh/id_rsa.pub

# SSH 目录
chmod 700 ~/.ssh

# Web 文件
find /var/www -type f -exec chmod 644 {} \;
find /var/www -type d -exec chmod 755 {} \;

# 日志
chmod 640 /var/log/app.log  # owner 写、组读、其他无
```

## 8. setuid / setgid / sticky

### 8.1 setuid（u+s）

```bash
chmod u+s /usr/bin/passwd
-rwsr-xr-x 1 root root 63736 Mar 22 14:25 /usr/bin/passwd
```

进程执行时**临时获得文件 owner 权限**。经典用：passwd 修改 /etc/shadow。

**风险**：滥用 = root。

### 8.2 setgid（g+s）

```bash
chmod g+s /shared/project
```

- 在目录上：新建文件**继承目录的组**
- 在文件上：进程执行时获得文件 group 权限

### 8.3 sticky（+t）

```bash
chmod +t /tmp
drwxrwxrwt
```

在目录上：用户只能删除**自己的文件**（防止其他用户删你的文件）。/tmp 默认开启。

## 9. umask 与进程继承

```bash
# /etc/profile
umask 022

# /etc/bashrc 或 ~/.bashrc
umask 077   # 个人 user 强保护
```

systemd service：

```ini
[Service]
UMask=0077
```

## 10. 实战：排查权限问题

```bash
# 用户无法访问文件？
ls -la /shared/project/
id username  # 看用户在哪些组

# 看具体权限
stat file
# 输出：
#   File: file
#   Access: (0644/-rw-r--r--)  Uid: ( 1000/alice)   Gid: ( 1000/alice)

# 看 ACL 是否更复杂
getfacl file
```

## 11. 实战：SUID/SGID 漏洞扫描

```bash
# 找所有 SUID
find / -perm -4000 2>/dev/null

# 找 SGID
find / -perm -2000 2>/dev/null

# 看可疑 SUID（owner 是 root）
find / -perm -4000 -user root 2>/dev/null | xargs ls -la
```

**安全建议**：SUID 越少越好。

## 12. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| 三类用户三组权限 | "u/g/o" |
| 目录 w = 增删文件 | "目录w=文件增删" |
| 八进制快速设置 | "777/755/644" |
| umask 控制默认权限 | "umask=默认" |
| SUID/SGID 慎用 | "SUID=高危" |

## 参考

- chmod(1) / chown(1) / umask(2) 手册
- 《Advanced Programming in the Unix Environment》