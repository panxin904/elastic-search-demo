---
title: sudo 提权
---

# sudo 提权

> 让普通用户在不共享 root 密码的情况下，做有限的高权限操作。

## 📜 基础

```bash
sudo cmd                  # 以 root 身份跑
sudo -u alice cmd         # 以 alice 跑
sudo -i                   # 切 root 交互 shell
sudo -s                   # 用 root shell（保留当前目录）
sudo !!                   # 上一条命令加 sudo

# 看自己的 sudo 权限
sudo -l

# 不输密码（如果你有 NOPASSWD 权限）
sudo -n cmd
```

## 🔑 /etc/sudoers

```bash
sudo visudo            # ⚠ 必须用 visudo（带语法检查）
sudo visudo -f /etc/sudoers.d/devops   # 在独立文件里加规则
```

格式：

```
who  where=(as_whom)  what  [tag]
```

| 字段 | 含义 |
|------|------|
| `who` | 用户 / %组 / User_Alias |
| `where` | 主机（基本不用，全用 ALL） |
| `(as_whom)` | 模拟身份（默认 ALL） |
| `what` | 命令 / 命令别名 / Cmnd_Alias |
| `tag` | NOPASSWD / NOEXEC / SETENV 等 |

### 例子

```bash
# 单用户全权
alice    ALL=(ALL:ALL) ALL

# 单用户免密码
bob      ALL=(ALL) NOPASSWD: ALL

# 用户组
%devops  ALL=(ALL) ALL
%wheel   ALL=(ALL) ALL          # 多数发行版默认

# 只允许特定命令
nginx    ALL=(root) /bin/systemctl reload nginx, /bin/systemctl restart nginx

# 限制可执行的命令参数（更严）
deploy   ALL=(root) /usr/bin/systemctl * nginx
deploy   ALL=(root) /usr/sbin/nginx -s reload
```

## 🪵 User_Alias / Cmnd_Alias

```bash
# 在 /etc/sudoers 或 /etc/sudoers.d/* 里

User_Alias ADMINS = alice, bob, %wheel
Cmnd_Alias SERVICES = /bin/systemctl *, /usr/bin/systemctl *

ADMINS  ALL=(root) SERVICES
```

## 🕐 时间窗口

```bash
# 仅工作时间
admins   ALL=(ALL) ALL  TIMEOUT=5
# 5 分钟无操作自动退出 sudo

# 定期 sudo 重认证（默认 5 分钟）
Defaults timestamp_timeout=15
```

## 🔐 安全实践

### 1. 最小权限

```bash
# ❌ 给运维全权
ops  ALL=(ALL) ALL

# ✅ 拆细
ops  ALL=(root) /bin/systemctl *
ops  ALL=(root) /usr/bin/vim /etc/nginx/*.conf
ops  ALL=(root) /usr/bin/journalctl *
ops  ALL=(root) NOPASSWD: /sbin/reboot, /sbin/shutdown
```

### 2. 强制日志

```bash
Defaults  log_input
Defaults  log_output
Defaults  iolog_dir=/var/log/sudo-io/%{user}
Defaults  logfile=/var/log/sudo
```

### 3. 强制 TTY

```bash
Defaults  requiretty           # 必须从真 tty 登录才能 sudo
# 取消：Defaults !requiretty
```

### 4. 防 LD_PRELOAD 提权

```bash
Defaults  env_reset
Defaults  env_keep = "LANG LC_ALL"
# 清空用户环境变量（防 LD_PRELOAD 攻击）
```

### 5. 审计

```bash
# 看 sudo 用了什么
journalctl _COMM=sudo -f
grep sudo /var/log/auth.log
```

## 📋 常用 sudo 配置示例

```bash
# /etc/sudoers.d/deploy
Defaults env_reset
Defaults secure_path = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# web 运维：重启 nginx + 看日志
webops  ALL=(root) /bin/systemctl reload nginx, \
                   /bin/systemctl restart nginx, \
                   /usr/bin/journalctl -u nginx

# DBA：只管 mysql
dba     ALL=(root) /bin/systemctl * mysql, \
                   /usr/bin/mysql, \
                   /usr/bin/mysqldump

# 部署：拉代码 + 重启
deploy  ALL=(root) /usr/bin/git pull, \
                   /usr/bin/systemctl restart myapp
```

## 🛠 实战：给团队成员加 sudo

```bash
# 1. 创建组
groupadd devops

# 2. 加成员
usermod -aG devops alice
usermod -aG devops bob

# 3. 写规则
cat > /etc/sudoers.d/devops <<EOF
%devops ALL=(ALL) ALL
EOF
chmod 440 /etc/sudoers.d/devops

# 4. 验证
sudo -l -U alice       # 看 alice 的权限
```

## 🔧 调试 sudo 失败

```bash
sudo -l                # 看自己权限
sudo -V                # sudo 版本信息

# "alice is not in the sudoers file"
# 1. 加进 /etc/sudoers 或 /etc/sudoers.d/xxx
# 2. 检查文件权限：440
chmod 440 /etc/sudoers.d/devops
visudo -c              # 检查语法

# "sudo: PAM authentication error"
# /etc/pam.d/sudo 配置问题

# 看到密码错误 / 密码过期
sudo -K                # 清空凭据缓存
sudo -k                # 同上

# 完整日志
journalctl -u sudo --since "1 hour ago"
```

## 🔗 下一步

- [用户 / 用户组](/05-user/users-groups)
- [chown / chgrp](/05-user/chown)
- [ACL 细粒度权限](/05-user/acl)
- [安全加固](/13-security/sshd-config)