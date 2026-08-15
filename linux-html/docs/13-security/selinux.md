---
title: SELinux
---

# SELinux

> **S**ecurity-**E**nhanced **Linux**。Linux 内核级强制访问控制（MAC）。CentOS / RHEL 默认开启。

## 🤔 为什么用 SELinux

传统 DAC（Discretionary Access Control）：
- 文件有 owner / mode，owner 想干啥就干啥
- 入侵后攻击者用被入侵的进程（apache）能跑任意命令

SELinux（MAC）：
- 即使你拿到了进程的属主身份，也只能访问策略允许的资源
- **最小权限原则**的强制实现

## 🧬 三种模式

```bash
getenforce                     # 看当前模式

# enforcing  - 强制执行（拦截违规）
# permissive - 警告但不拦截（仅记日志）
# disabled   - 完全关闭
```

```bash
# 改模式
sudo setenforce 1              # enforcing
sudo setenforce 0              # permissive

# 永久（/etc/selinux/config）
SELINUX=enforcing              # enforcing / permissive / disabled
sudo reboot                    # disabled ↔ enforcing 切换需要重启
```

## 🔑 核心概念

### 标签

每个文件、进程、端口都有 SELinux **标签**（context）：

```
user:role:type:sensitivity
       │  │    │      │
       │  │    │      └─ MLS（多级安全，可选）
       │  │    └─ 类型（最重要的部分）
       │  └─ 角色
       └─ SELinux 用户
```

```bash
ls -Z file                     # 看文件标签
ps -efZ | grep nginx           # 看进程标签
ss -tnlpZ                      # 看端口标签
```

例：

```
system_u:object_r:httpd_sys_content_t:s0 /var/www/html/index.html
system_u:system_r:httpd_t:s0       1234 ?  00:00:01 nginx
```

### 类型强制（Type Enforcement）

> 大部分策略基于 type。最常见。

```
nginx worker 进程的 type:  httpd_t
httpd_t 能访问:        httpd_sys_content_t（http 内容）
                      httpd_sys_content_rw_t（http 可写内容）
```

## 📜 排查

### 服务起不来 = 多半 SELinux

```bash
# 看是不是 SELinux 阻止
sudo ausearch -m AVC --start today   # AVC 拒绝日志
sudo ausearch -m AVC -ts recent

# 看具体规则
sudo audit2why < /var/log/audit/audit.log
```

### 给文件打 / 改标签

```bash
# 看当前标签
ls -Z /var/www/html/
ls -dnZ /var/www/html/

# 加类型（e.g. http 内容）
sudo semanage fcontext -a -t httpd_sys_content_t '/webapp(/.*)?'
sudo restorecon -R /webapp

# 改布尔值（动态策略开关）
getsebool -a | grep httpd
sudo setsebool -P httpd_can_network_connect on
# -P 永久
```

### 临时降级（不要生产）

```bash
# 排查期间
sudo setenforce 0              # permissive
# 解决后再 setenforce 1
```

## 🛠 实战

### Apache / Nginx 自定义目录

```bash
# 改了 DocumentRoot 路径 → SELinux 拒绝访问
sudo mkdir /webapp
sudo chown -R apache:apache /webapp
sudo chcon -R -t httpd_sys_content_t /webapp    # 临时
# 永久
sudo semanage fcontext -a -t httpd_sys_content_t '/webapp(/.*)?'
sudo restorecon -R /webapp
```

### 端口监听

```bash
# nginx 想用 8081（默认策略只允许 80/443）
sudo semanage port -a -t http_port_t -p tcp 8081
# 看允许的端口
sudo semanage port -l | grep http_port_t
```

### 用户映射（sudo）

```bash
# sudo 时 SELinux 用户改变
sudo -i                         # 变成 unconfined_u
# 应用系统（apache）跑还是 system_u

# 改 SELinux 用户
sudo semanage login -a -s user_u alice
```

## 🩺 关键命令

| 命令 | 作用 |
|------|------|
| `getenforce` | 当前模式 |
| `setenforce 0/1` | permissive / enforcing |
| `getsebool -a` | 列出布尔值 |
| `setsebool -P NAME on` | 开 + 永久 |
| `semanage fcontext -a -t TYPE PATH` | 加文件类型规则 |
| `restorecon -R DIR` | 应用默认 / 自定义规则 |
| `chcon -t TYPE FILE` | 临时改标签（重启会丢） |
| `ausearch -m AVC` | 查拒绝日志 |
| `audit2allow -M mypol` | 生成自定义策略模块 |

## 🪤 故障模板

```bash
# 1. 服务起不来
sudo systemctl status myapp | tail
journalctl -u myapp -n 30 | tail

# 2. 看 SELinux 是否阻止
sudo ausearch -m AVC --start today -ts recent | grep myapp

# 3. 看具体命令的拒绝
sudo ausearch -ts recent -m AVC | tail -5

# 4. 临时允许
sudo setenforce 0
sudo systemctl restart myapp     # 看是否能起来
# 还是起不来 → 不是 SELinux

# 5. 永久策略（基于 audit log）
sudo ausearch -m AVC --start today | audit2allow -M mypol
sudo semodule -i mypol.pp
sudo setenforce 1
sudo systemctl restart myapp
```

## 🔗 下一步

- [AppArmor](/13-security/apparmor)
- [sshd_config 加固](/13-security/sshd-config)
- [auditd 审计](/13-security/auditd)
- [OpenSSH 配置](/08-firewall-ssh/openssh)