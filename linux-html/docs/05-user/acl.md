---
title: ACL 细粒度权限
date: 2026-08-15  # date-auto-injected
---

# ACL - 细粒度权限

> 当 rwx 三组不够用——给特定用户 / 组额外授权。

## 🤔 为什么需要 ACL

传统 Unix 权限：
- 属主 / 属组 / 其他，**只 3 组**
- 想给"某个特定用户 alice"开 rwx？没办法

ACL：
- 可以挂多个独立用户 / 组的权限
- 文件 / 目录都能用

```bash
# 传统：要么 644，要么 644（很死板）
# ACL：alice rw-, dev r-x, 其他 r--

chmod 644 file                   # r--r--r--
setfacl -m u:alice:rw file       # alice 加 rw
setfacl -m g:dev:r file          # dev 组 r
setfacl -m m::r file             # mask（最高权限）

# 最终：
# user:alice:rw-
# user::r-- (原属主)
# group::r-- (原属组)
# group:dev:r--
# mask::r--
# other::r--
```

## 📜 getfacl / setfacl

```bash
# 看
getfacl file

# 输出
# file: file
# owner: alice
# group: dev
# user::rw-
# user:bob:r--         # bob 只读
# group::r--
# mask::rwx            # mask（最高水位）
# other::r--

# 加
setfacl -m u:bob:r file
setfacl -m g:dev:rx file
setfacl -m m::r file             # 改 mask

# 递归
setfacl -R -m u:bob:rx dir/

# 默认 ACL（目录新建文件继承）
setfacm -m d:u:bob:rwx dir/

# 删
setfacl -x u:bob file            # 删 bob 的 ACL
setfacl -b file                  # 全部清除
```

## 📋 ACL 类型

| 类型 | 作用 |
|------|------|
| **Access ACL** | 文件 / 目录上的实际权限 |
| **Default ACL** | 目录上：新建文件 / 子目录自动继承 |

## 🧮 mask - 权限天花板

```
实际权限 = ACL 条目 & mask
```

```bash
getfacl file
# user::rwx
# user:alice:r--       ← 即使 alice 在 ACL 有 rwx
# mask::r--             ← 实际只能 r
```

**修改 mask 时**，所有 ACL 条目**会被 mask 限制**。这是 ACL 设计的"安全阀"。

## 🛠 实战

### 共享项目目录

```bash
# 5 人协作项目，要让"PM"额外写
groupadd project
usermod -aG project alice
usermod -aG project bob
usermod -aG project carol
usermod -aG project dave
usermod -aG project eve

mkdir /opt/project
chown :project /opt/project
chmod 2775 /opt/project             # SGID
chmod -R u+rwX,g+rwX,o+rX /opt/project
```

### 默认 ACL（继承）

```bash
# 在 /opt/projects 下新建文件 / 子目录，自动属于 dev 组 + 664
setfacl -m d:g:dev:rw /opt/projects
setfacl -m d:o::r /opt/projects

# 验证
mkdir /opt/projects/sub
getfacl /opt/projects/sub
# 会有 default ACL
```

### 跨用户交付

```bash
# alice 给 bob 一个特定文件读权
chmod 600 file
setfacl -m u:bob:r file
# 现在 bob 能读，alice 仍可写，其他人无权
```

## 🩺 排查

```bash
# "为什么 chmod 改了没用？"
ls -la file                        # 看 + 号
# -rw-r--r--+ 1 alice alice ...
#            ^               ← 有 ACL

# "删了用户的 ACL 怎么还原"
setfacl -k dir                      # 删 default ACL
setfacl -R -b dir                   # 递归清空

# 备份 ACL
getfacl -R /opt/project > acl-backup.txt
# 恢复
setfacl --restore=acl-backup.txt
```

## 🔄 备份与恢复

```bash
# 备份整个目录树的 ACL
getfacl -R /opt/project > /backup/project-acl.txt

# 恢复（要在 / 下）
cd /
setfacl --restore=/backup/project-acl.txt
```

## ⚠️ 限制

- 文件系统必须支持（ext4 / xfs / btrfs ✅；FAT / NTFS ❌）
- NFS v4 客户端要小心，ACL 不一定透传
- 复制文件时 ACL 不一定保留：`cp -a` 会保留；`cp` 默认不带

```bash
# 看是否支持
mount | grep acl
# /dev/sda1 on / type ext4 (rw,relatime,errors=remount-ro)

# 临时关掉（不推荐）
mount -o noacl /dev/sda1 /mnt
```

## 🔗 下一步

- [chmod 权限](/05-user/chmod)
- [chown / chgrp](/05-user/chown)
- [用户 / 用户组](/05-user/users-groups)