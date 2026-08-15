---
title: chown / chgrp
---

# chown / chgrp

> 改属主 / 属组。chmod 改的是"谁能做什么"，chown 改的是"文件属于谁"。

## 🛠 chown

```bash
chown alice file               # 改属主
chown alice:dev file           # 改属主 + 属组
chown :dev file                # 只改属组
chown -R alice dir/            # 递归

# 跟随软链
chown -h alice symlink         # 改软链本身（不跟随）

# 高级：--from
chown --from=alice alice2 file  # 仅当当前属主是 alice
```

## 🛠 chgrp

```bash
chgrp dev file                 # 改属组
chgrp -R dev dir/              # 递归
```

`chown :group file` 等价 `chgrp group file`。

## 🪟 看属主 / 属组

```bash
ls -l file                     # 第 3、4 列
stat file
stat -c '%U %G %n' file

# 用数字（UID / GID）
stat -c '%u %g %n' file
find . -uid 1000               # 找某 UID 的文件
find . -gid 1000               # 找某 GID 的文件
find / -nouser                # 无属主（用户被删后）
find / -nogroup                # 无属组
```

## 🚧 常见场景

### 1. Web 应用部署

```bash
# nginx 用 www-data 用户跑
sudo chown -R deploy:www-data /var/www/site
find /var/www/site -type d -exec chmod 755 {} +
find /var/www/site -type f -exec chmod 644 {} +
```

### 2. 共享项目目录

```bash
groupadd devteam
mkdir /opt/project
chown :devteam /opt/project
chmod 2775 /opt/project             # SGID：新文件自动归属
usermod -aG devteam alice
usermod -aG devteam bob
```

### 3. 备份脚本恢复

```bash
# 解 tar 时保留属主（默认是当前用户）
tar --same-owner -xf backup.tar.gz -C /restore

# 改回原属主
chown -R mysql:mysql /var/lib/mysql
```

### 4. 容器 / docker 卷

```bash
# /var/lib/docker-data 属主
chown -R 1000:1000 /var/lib/docker-data
# 这里 1000 是容器内用户的 UID
```

## 🛡 安全审计

```bash
# 找 SUID / SGID root 文件
find / -user root -perm -4000 2>/dev/null
find / -user root -perm -2000 2>/dev/null

# 找无属主文件（用户被删后）
find / -nouser -o -nogroup 2>/dev/null

# 找最近改属主的文件（可能异常）
find / -mtime -1 -exec stat -c '%y %U %G %n' {} \;
```

## 🧠 配合 SGID 共享目录

```bash
mkdir /opt/shared
chown :devteam /opt/shared
chmod 2775 /opt/shared
# alice 在 /opt/shared 创建文件，自动属 devteam 组
# bob 也能修改（都是 devteam 组成员）
```

## 🔧 高级：preserve-root / from

```bash
# 拒绝递归到 /
chown --preserve-root -R alice /

# 仅改属主为 alice 的文件
chown --from=alice bob file
```

## ❓ 常见问题

```bash
# chown: changing ownership of '...': Operation not permitted
# 普通用户只能改自己拥有的文件
# 用 sudo

# 文件在 SSH / NFS 上失败
# 可能是文件系统不支持（如 vboxsf、某些 SMB）
# 用 sudo 或换挂载方式

# 改完属主，进程访问拒绝
# 需要 reload 服务（部分服务缓存了 UID）
systemctl reload nginx
```

## 🔗 下一步

- [chmod 权限](/05-user/chmod)
- [用户 / 用户组](/05-user/users-groups)
- [sudo 提权](/05-user/sudo)