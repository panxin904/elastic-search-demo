---
title: ACL 访问控制列表
---

# ACL — 比 POSIX 更精细的权限系统

> <span class="kg-badge kg-badge--security">安全权限</span>
> 用户级 · 组级 · 默认 ACL · 实战场景

POSIX 权限只有三类用户（owner/group/other），太粗。ACL（Access Control List）允许**任意多用户**、**任意多组**的细粒度权限控制。

## 1. ACL 类型

| ACL 类型 | 含义 |
|---------|------|
| **访问 ACL** | 单文件 / 目录的 ACL |
| **默认 ACL** | 目录的"模板"，新建文件 / 子目录继承 |

## 2. 启用 ACL

```bash
# ext4 默认支持
mount -o acl /dev/sda1 /mnt

# 永久
# /etc/fstab
/dev/sda1 /mnt ext4 defaults,acl 0 2

# 验证
mount | grep acl
```

xfs / btrfs 默认启用 ACL。

## 3. 实战：getfacl / setfacl

```bash
# 看 ACL
getfacl /home/project

# 设 ACL
setfacl -m u:bob:rw /home/project/file.txt
setfacl -m g:dev:rwx /home/project
setfacl -m m::rwx /home/project        # 修改 mask

# 删除 ACL
setfacl -x u:bob /home/project/file.txt

# 删除全部
setfacl -b /home/project

# 递归
setfacl -R -m u:bob:rwx /home/project
```

## 4. ACL 字段

```text
# file: /home/project
# owner: alice
# group: developers
user::rwx
user:bob:rw-
user:carol:r--
group::rwx
group:dev:r-x
mask::rwx
other::r-x
```

字段说明：

| 字段 | 含义 |
|------|------|
| `user::` | 文件 owner 权限（POSIX user） |
| `user:bob:rw-` | 命名用户的 ACL |
| `group::` | 文件 group 权限（POSIX group） |
| `group:dev:r-x` | 命名组的 ACL |
| `mask::rwx` | 有效权限上限 |
| `other::` | POSIX other |

## 5. mask 与 effective permissions

**mask 决定 ACL 的最大有效权限**：

```bash
setfacl -m u:bob:rw file.txt   # bob rw-
setfacl -m m::r file.txt       # mask r
getfacl file.txt
# user:bob:rw-        # effective: r--
# ↑ 因为 mask 是 r，effective 变成 r--
```

**mask 的修改**也会影响 chmod g= 的效果——小心！

```bash
chmod g=rx file.txt    # mask 也会被改成 rx
```

## 6. 默认 ACL（目录）

```bash
# 在目录上设置 default ACL
setfacl -d -m u:bob:rw /home/project
setfacl -d -m g:dev:rwx /home/project

# 之后在目录下创建的文件自动继承
touch /home/project/newfile
getfacl /home/project/newfile
# user:bob:rw-  （继承）
# group:dev:rwx （继承）
```

**关键**：

- 只对**目录**设默认 ACL 才有用
- 默认 ACL **不会**自动覆盖已有文件
- 文件没有 mask，但有效权限取 default ACL 的 mask

## 7. 实战：协作目录

```bash
# 设协作目录
mkdir /shared/dev
chmod 2775 /shared/dev              # setgid：新建文件继承目录组
chgrp dev /shared/dev               # 改组

# ACL：dev 组全权，qa 组只读，其他无
setfacl -m g:dev:rwx /shared/dev
setfacl -m g:qa:rx /shared/dev
setfacl -m o::--- /shared/dev

# 默认 ACL
setfacl -d -m g:dev:rwx /shared/dev
setfacl -d -m g:qa:rx /shared/dev
setfacl -d -m o::--- /shared/dev
```

```bash
# dev 用户 alice 创建
su alice
touch /shared/dev/alice-file
getfacl /shared/dev/alice-file
# group:dev:rwx  ← alice 默认组是 dev，自动全权
# group:qa:rx    ← qa 用户只读
# other::---
```

## 8. ACL 与 ls

```bash
# 有 ACL 的文件，ls -l 多一个 + 号
ls -l file.txt
-rw-rw----+ 1 alice dev 0 Jan 1 12:00 file.txt
                          ↑ 有 ACL
```

## 9. ACL 与工具兼容

| 工具 | 是否保留 ACL |
|------|------------|
| `cp -a` | ✅ |
| `rsync -a` | ✅（默认） |
| `tar` | ⚠️ 部分支持（--acls 标志） |
| `cp --preserve=all` | ✅ |
| `mv` | ✅（同 FS 内） |
| `zip` | ❌ |

```bash
# rsync 同步 ACL
rsync -aA /src/ /dst/

# tar 备份 ACL
tar --acls -czf backup.tar.gz /home
tar --acls -xzf backup.tar.gz -C /
```

## 10. 实战：NFSv4 ACL（与 POSIX ACL 不同）

NFSv4 的 ACL 是 **Windows NTFS ACL 模型**：

```bash
nfs4_setfacl -a A::owner@:rwaDdTtTnNcCo /file
nfs4_setfacl -a A::alice@domain:rxtcy /file

nfs4_getfacl /file
```

涉及 14 种权限（rwx + 高级操作）。

## 11. ACL 与 SELinux / AppArmor

- ACL：**文件系统级**权限（用户 / 组维度）
- SELinux：**内核级**强制访问控制（多维度 label）

两者独立设置。SELinux 拒绝时，ACL 通过也访问失败。

## 12. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| ACL 扩展 POSIX | "ACL=POSIX+" |
| mask = 有效权限上限 | "mask=上限" |
| 默认 ACL 在目录 | "默认=目录" |
| `+` 标志表示有 ACL | "+=有 ACL" |
| 备份要 --acls | "备份=带 ACL" |

## 参考

- getfacl(1) / setfacl(1) 手册
- POSIX.1e ACL 规范（草案）
- NFSv4 ACL 文档


<!-- auto-enrich:do-not-edit -->

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
