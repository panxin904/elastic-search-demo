---
title: chmod 权限
date: 2026-08-15  # date-auto-injected
---

# chmod 权限

> 跟 [02-filesystem/permissions](/02-filesystem/permissions) 互补——这里更偏用户 / 安全场景。

## 🔍 数字 vs 符号

```bash
chmod 644 file             # rw-r--r--
chmod u+w file             # 给属主加 w
chmod go-r file            # 给属组和其他人减 r
```

详见 [02-filesystem/permissions](/02-filesystem/permissions)。

## 🎯 实战：网站部署权限

```bash
# 推荐：web 文件
chown -R deploy:www-data /var/www/site
find /var/www/site -type d -exec chmod 755 {} \;   # 目录 755
find /var/www/site -type f -exec chmod 644 {} \;   # 文件 644

# 共享目录（多用户可写）
chmod 2775 /opt/shared       # SGID（属组自动归属）
chmod 1775 /tmp/shared       # sticky bit（只能自己删自己）

# SSH 私钥（必须）
chmod 600 ~/.ssh/id_rsa
chmod 700 ~/.ssh
```

## 🪤 SUID / SGID / Sticky

详见 [permissions](/02-filesystem/permissions)。

```bash
# SUID：用户执行时以文件属主身份
chmod 4755 /usr/bin/passwd

# SGID：组内共享 + 自动归属
chmod 2775 /opt/shared

# sticky：只能自己删自己文件
chmod 1777 /tmp
```

## 🔐 umask 默认权限

```bash
umask                          # 看（0022）
umask 027                      # 改

# 文件默认 = 666 - umask（不算 x）
# 目录默认 = 777 - umask

# umask 022 → 文件 644，目录 755（最常见）
# umask 027 → 文件 640，目录 750（更严）
# umask 077 → 文件 600，目录 700（最严）

# 永久生效
echo 'umask 027' >> /etc/profile
```

## 🪞 setuid / setgid bit (2000)

```bash
# 让脚本以属主身份执行（不太安全，慎用）
chmod 4755 /opt/bin/admin-tool

# 看是否有 setuid
ls -l /usr/bin/su
# -rwsr-xr-x  1 root root  ...  /usr/bin/su
#     ^

# 安全审计
find / -perm -4000 -type f 2>/dev/null  # SUID
find / -perm -2000 -type f 2>/dev/null  # SGID
```

## 📐 ACL - 精细权限

需要给特定用户 / 组额外授权，普通 rwx 不够用：

```bash
# 给 alice 单独 rwx
setfacl -m u:alice:rwx file
setfacl -m u:alice:5 file           # r-x（数字）
setfacl -m g:dev:r file             # 给 dev 组

# 递归
setfacl -R -m u:alice:rwx /opt/project

# 默认 ACL（目录新建文件继承）
setfacl -m d:u:alice:rwx /opt/project

# 看 ACL
getfacl file

# 删
setfacl -x u:alice file
setfacl -b file                    # 全部清空
```

详见 [ACL](/05-user/acl)。

## 🪟 几个特殊的 umask

```bash
# 调试：脚本里临时改
umask 077
echo "secret" > file               # 文件 600
umask 022                          # 还原
```

## ❓ 常见问题

```bash
# "我的脚本不能执行"
chmod +x script.sh

# "目录进不去"
chmod 755 dir                      # 至少 x 位

# "我要给同事共享 /opt/work"
groupadd dev
chown :dev /opt/work
chmod 2775 /opt/work                # SGID
usermod -aG dev alice
usermod -aG dev bob
# 现在 alice / bob 都能读写

# "我的 SSH 一直要求密码"
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
chmod 644 ~/.ssh/authorized_keys

# "Web 上传目录 755 仍然不能写"
chmod 775 /var/www/upload
chown -R www-data:www-data /var/www/upload
# 或给 web 用户写权限
```

## 🛡 最小权限原则

| 场景 | 权限 |
|------|------|
| 配置文件 | 644 (root 可改) / 600 (root only) |
| 私密文件 | 600 |
| 脚本 | 755（带执行） |
| 共享目录 | 2775（SGID） |
| /tmp | 1777（sticky） |
| SSH 私钥 | 600（硬性） |

## 🔗 下一步

- [chown / chgrp](/05-user/chown)
- [用户 / 用户组](/05-user/users-groups)
- [ACL 细粒度权限](/05-user/acl)