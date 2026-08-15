---
title: auditd 审计
---

# auditd - Linux 审计系统

> 内核级审计：谁在何时对哪个文件做了什么。**合规、等保、追溯**必备。

## 📦 安装

```bash
sudo apt install auditd audispd-plugins

sudo systemctl enable --now auditd
sudo systemctl status auditd
```

## 📜 规则

规则在 `/etc/audit/rules.d/`（按字典序加载，数字越大越后）。

```bash
# 例子：/etc/audit/rules.d/myapp.rules

# 监控 /etc/passwd / /etc/shadow 变更
-w /etc/passwd -p wa -k passwd_changes
-w /etc/shadow -p wa -k passwd_changes

# 监控特权命令
-w /usr/bin/sudo -p x -k sudo_usage
-w /usr/bin/su -p x -k su_usage

# 监控 SSH 配置变更
-w /etc/ssh/sshd_config -p wa -k sshd_config

# 监控登录失败
-w /var/log/faillog -p wa -k logins
-w /var/log/lastlog -p wa -k logins
-w /var/log/tallylog -p wa -k logins

# 监控时间修改
-a always,exit -F arch=b64 -S adjtimex -S settimeofday -S clock_settime -k time_change

# 监控网络配置
-w /etc/issue -p wa -k system_locale
-w /etc/hosts -p wa -k system_locale
-w /etc/hostname -p wa -k system_locale

# 监控 mount
-w /etc/fstab -p wa -k mounts
```

## 🪛 ausearch - 查询

```bash
sudo ausearch -k passwd_changes      # 按 key
sudo ausearch -ts today              # 按时间
sudo ausearch -ts 2024-01-15         # 按日期
sudo ausearch -ts recent             # 最近 10 分钟
sudo ausearch -ui 1000               # 按 UID
sudo ausearch -m AVC                  # AVC（SELinux）拒绝

# 组合
sudo ausearch -k sshd_config -ts today
sudo ausearch -ua alice -ts today
```

## 📜 ausearch 输出解读

```
type=SYSCALL msg=audit(1705312345.123:4567): arch=c000003e syscall=2 success=yes exit=3 items=1 ppid=1234 pid=5678 auid=1000 uid=0 gid=0 euid=0 suid=0 fsuid=0 egid=0 sgid=0 fsgid=0 tty=pts0 ses=1 comm="vim" exe="/usr/bin/vim" key="passwd_changes"
type=CONFIG_CHANGE msg=audit(...)
```

| 字段 | 含义 |
|------|------|
| `type=` | SYSCALL / PATH / CONFIG_CHANGE / USER_AUTH … |
| `msg=audit(...)` | 时间戳 + 序列号 |
| `syscall=` | 系统调用编号 |
| `success=yes/no` | 是否成功 |
| `auid=1000` | 真实 UID（sudo 后仍记录原 UID） |
| `uid=0` | 当前有效 UID |
| `comm=` `exe=` | 进程名 / 可执行路径 |
| `key=` | 规则 key |

## 📊 aureport - 报告

```bash
sudo aureport                           # 全部
sudo aureport --summary                # 总览
sudo aureport -au                       # 认证
sudo aureport -m                        # 账户变更
sudo aureport -x                        # 执行
sudo aureport -f                        # 文件
sudo aureport --failed                  # 仅失败
```

## 🛠 实战：监控关键文件变更

```bash
sudo tee /etc/audit/rules.d/critical-files.rules << 'EOF'
# 认证 / 用户管理
-w /etc/passwd -p wa -k auth
-w /etc/shadow -p wa -k auth
-w /etc/group -p wa -k auth
-w /etc/sudoers -p wa -k auth
-w /etc/sudoers.d/ -p wa -k auth

# SSH
-w /etc/ssh/sshd_config -p wa -k sshd
-w /etc/ssh/ssh_host_*_key -p wa -k sshd

# 系统配置
-w /etc/passwd -p wa -k system
-w /etc/shadow -p wa -k system
-w /etc/group -p wa -k system

# 特权命令
-w /usr/bin/sudo -p x -k priv
-w /usr/bin/su -p x -k priv
-w /usr/sbin/useradd -p x -k priv
-w /usr/sbin/userdel -p x -k priv
-w /usr/sbin/usermod -p x -k priv

# 时间篡改
-a always,exit -F arch=b64 -S adjtimex -S settimeofday -S clock_settime -k time_change

# 内核模块
-w /sbin/insmod -p x -k modules
-w /sbin/rmmod -p x -k modules
-w /sbin/modprobe -p x -k modules

# 调度（防 cron 提权）
-w /etc/cron.allow -p wa -k cron
-w /etc/cron.deny -p wa -k cron
-w /etc/cron.d/ -p wa -k cron
-w /etc/crontab -p wa -k cron
-w /var/spool/cron/ -p wa -k cron
EOF

sudo augenrules --load
sudo systemctl restart auditd
```

## 🛠 实战：监控特权命令调用

```bash
sudo tee /etc/audit/rules.d/privileged.rules << 'EOF'
# 监控所有 setuid / setgid 调用
-a always,exit -F arch=b64 -S execve -F euid=0 -k root_commands
-a always,exit -F arch=b32 -S execve -F euid=0 -k root_commands
EOF

# 查谁跑了 su / sudo
sudo ausearch -k priv --interpret
```

## 🛠 实战：监控登录

```bash
# 已内置在 /etc/audit/rules.d/login.rules（多数发行版）
sudo ausearch -m USER_LOGIN -ts today --interpret
# 可看每个登录的 uid / 来源 IP / 时间
```

## 📚 规则语法速查

```
-w <path>          监视文件
-p <r|w|x|a>       监控的权限：read / write / exec / attribute
-k <key>            自定义 key（便于查询）
-a <list>,<action> 系统调用规则
-F <field>=<value> 过滤条件
-S <syscall>        系统调用名
```

例：

```bash
# 谁改了 /etc/passwd（成功 + 失败都记）
-a always,exit -F path=/etc/passwd -F perm=wa -k passwd_changes

# 谁用 sudo 跑了命令
-a always,exit -F path=/usr/bin/sudo -F perm=x -k sudo

# 哪个用户在修改时间
-a always,exit -F arch=b64 -S settimeofday -k time_change
```

## 🧹 性能 / 容量

audit 日志可能很大：

```bash
# 看大小
sudo ls -lh /var/log/audit/

# 配置 /etc/audit/auditd.conf
max_log_file = 50                # 单文件 50MB
max_log_file_action = ROTATE     # 滚动
num_logs = 5                     # 保留 5 个
space_left = 100                 # 100MB 触发
space_left_action = SYSLOG       # 只记日志，不停止

# 立即生成报告（性能）
sudo aureport --summary
```

## 🪤 ausearch --interpret

```bash
# 数字 pid / syscall → 名字
sudo ausearch -k passwd_changes --interpret

# 输出
# type=SYSCALL msg=audit(1705312345.123:4567): arch=x86_64 syscall=2 \
#   success=yes exit=3 items=1 ppid=1234 pid=5678 auid=alice uid=root \
#   comm="vim" exe="/usr/bin/vim" key="passwd_changes"
# 现在能直接读 auid=alice / syscall=openat
```

## 🔗 下一步

- [SELinux](/13-security/selinux)
- [sshd_config 加固](/13-security/sshd-config)
- [lynis 合规](/13-security/lynis)