---
title: 权限 (rwx)
date: 2026-08-15  # date-auto-injected
---

# 文件权限 rwx

> 数字 644、755 你肯定见过，但 rwx 到底意味着什么？

## 🔍 权限三元组

每个文件有 3 组权限位：

```
-rwxr-xr-- 1 alice alice 1.2K file
│└┬┘└┬┘└┬┘
│ │  │  └─ 其他人 (o) — 4 = 只读
│ │  └───── 属组 (g) — 5 = 读 + 执行
│ └────────── 属主 (u) — 7 = 读 + 写 + 执行
└──────────── 文件类型 (- 普通 / d 目录 / l 软链)
```

每组三位：`r` (4) / `w` (2) / `x` (1) ：

```
7 = rwx (读+写+执行)
6 = rw- (读+写)
5 = r-x (读+执行)
4 = r-- (只读)
3 = -wx (写+执行)
2 = -w- (只写)
1 = --x (只执行)
0 = --- (无权限)
```

## 📝 常见数字权限

| 数字 | 含义 | 用途 |
|------|------|------|
| 644 | rw-r--r-- | 普通文件（属主可写，别人只读） |
| 755 | rwxr-xr-x | 可执行文件 / 目录 |
| 600 | rw------- | 私密文件 / SSH key |
| 700 | rwx------ | 私密目录 |
| 777 | rwxrwxrwx | **永远不要用**（全员可改） |
| 664 | rw-rw-r-- | 组内可写 |
| 775 | rwxrwxr-x | 组内可改 |

## 🛠 chmod - 改权限

```bash
# 数字模式
chmod 644 file                 # rw-r--r--
chmod 755 script.sh            # rwxr-xr-x
chmod 600 ~/.ssh/id_rsa        # 私密密钥

# 符号模式（u/g/o/a，+/-/=）
chmod u+x script.sh            # 给属主加执行
chmod g+w file                 # 给属组加写
chmod o-r file                 # 取消其他人读
chmod a+r file                 # 所有人加读
chmod u=rwx,g=rx,o=r file     # 同时设多组

# 递归
chmod -R 644 dir/              # 整个目录
chmod -R u+X dir/              # 只给目录加 x（不是文件）
```

## 👤 chown - 改属主

```bash
chown alice file                # 改属主
chown alice:dev file            # 改属主 + 属组
chown :dev file                 # 只改属组
chown -R alice:dev dir/         # 递归
```

只有 **root** 才能改属主。普通用户改不动别人文件。

## 🔒 特殊权限位

### SUID / SGID (4000 / 2000)

```bash
chmod 4755 /usr/bin/passwd      # SUID（属主权限运行）
chmod 2755 /usr/bin/wall        # SGID（属组权限运行）

# 看 SUID 文件（安全审计）
find / -perm -4000 -type f 2>/dev/null
```

**SUID 风险**：被 SUID 的程序如果以 root 运行，被攻击者利用可获得 root 权限。`/tmp` 上的 SUID 脚本要警惕。

### Sticky Bit (1000)

```bash
chmod 1777 /tmp                 # /tmp 经典 sticky
# 在 sticky 目录里，文件只能被属主删除/重命名
# 多人共享目录时使用
```

## 🧱 umask

umask 决定新文件默认权限：

```bash
umask                          # 看（一般是 0022）
umask 027                      # 设

# 计算：文件默认 = 666 - umask
# 目录默认 = 777 - umask
# umask 022 → 文件 644，目录 755
# umask 027 → 文件 640，目录 750
```

写入 `/etc/profile` 让所有用户生效。

## 🪟 ACL（细粒度权限）

```bash
# 给特定用户 / 组额外授权
setfacl -m u:alice:rwx file
setfacl -m g:dev:rx file
getfacl file                    # 看 ACL

# 删某条 ACL
setfacl -x u:alice file
```

详见 [ACL 细粒度权限](/05-user/acl)。

## ❓ 常见问题

```bash
# "我改了脚本但执行不了"
chmod +x script.sh

# "我的 web server 读不到文件"
chmod 644 file                  # 或 chown www-data:www-data file

# "目录进不去"
chmod 755 dir

# "Permission denied" 还可能是文件属主不对
chown alice:alice file

# "SUDO 拒绝"
chmod 4755 /usr/bin/sudo        # 或 dpkg-reconfigure sudo
```

## 🔗 下一步

- [chown / chgrp](/05-user/chown)
- [ACL 细粒度权限](/05-user/acl)
- [用户 / 用户组](/05-user/users-groups)