---
title: ufw / firewalld
---

# ufw / firewalld - 简化版防火墙

> iptables 的"易用前端"。

## 🆚 ufw vs firewalld

| | ufw | firewalld |
|--|-----|-----------|
| 适用 | Ubuntu / Debian | RHEL / CentOS / Fedora |
| 后端 | iptables / nftables | nftables |
| 配置 | 命令行 / /etc/ufw/* | firewall-cmd / XML |
| 复杂度 | 极简 | 中等 |

## 🛡 ufw (Ubuntu)

```bash
sudo ufw status                  # 看状态
sudo ufw status verbose          # 看详细规则

sudo ufw enable                  # 启用（开机自启）
sudo ufw disable                 # 停用

# 默认策略
sudo ufw default deny incoming   # 默认拒绝入站
sudo ufw default allow outgoing  # 默认放行出站

# 放行服务
sudo ufw allow ssh               # 等价 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 'Apache Full'     # 服务名（在 /etc/services）

# 限制 SSH 防暴力（每 30 秒最多 6 次连接）
sudo ufw limit ssh

# 限制特定 IP / 子网
sudo ufw allow from 192.168.1.0/24 to any port 22

# 删除规则
sudo ufw delete allow 80/tcp
sudo ufw status numbered         # 看编号
sudo ufw delete 3                # 删第 3 条

# 重置
sudo ufw reset
```

### ufw /etc/ufw/ 文件

```bash
ls /etc/ufw/
# user.rules          用户规则
# user6.rules         IPv6 用户规则
# before.rules        预规则（NAT）
```

也可以直接编辑（`sudo ufw reload`）。

## 🧱 ufw 应用示例

```bash
# SSH（限内网）
sudo ufw default deny incoming
sudo ufw allow from 192.168.1.0/24 to any port 22

# Web
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 数据库（仅内网）
sudo ufw allow from 10.0.0.0/8 to any port 3306

# 自定义
sudo ufw allow 5000:5010/tcp     # 端口段

# 拒绝 + 日志
sudo ufw deny log 23             # 拒绝 telnet + 记录
```

## 🔥 firewalld (RHEL)

```bash
# 服务管理
sudo firewall-cmd --state
sudo systemctl enable --now firewalld

# 看规则
sudo firewall-cmd --list-all
sudo firewall-cmd --list-services
sudo firewall-cmd --list-ports

# 放行服务
sudo firewall-cmd --add-service=http
sudo firewall-cmd --add-service=https
sudo firewall-cmd --add-port=8080/tcp

# 永久生效（运行时 + 重启后）
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload

# 删除
sudo firewall-cmd --remove-port=8080/tcp

# 区域（zone）
sudo firewall-cmd --get-active-zones
sudo firewall-cmd --get-default-zone
sudo firewall-cmd --set-default-zone=public
sudo firewall-cmd --zone=public --add-port=8080/tcp
sudo firewall-cmd --zone=internal --add-source=10.0.0.0/8

# 富规则（rich rule）
sudo firewall-cmd --add-rich-rule='rule family=ipv4 source address=10.0.0.0/24 service name=http accept'

# 应急：panic on（断所有连接）
sudo firewall-cmd --panic-on
sudo firewall-cmd --panic-off
```

## 🎨 zone 概念

| zone | 用途 | 默认规则 |
|------|------|---------|
| public | 不可信网络 | 仅放行白名单 |
| trusted | 完全可信 | 全部放行 |
| internal | 内部网 | 类似 trusted |
| dmz | 隔离区 | 放行特定服务 |
| block | 拒绝入站 | reject |
| drop | 丢弃入站 | drop（不回 RST） |

## 🛠 实战

### Ubuntu 服务器基础

```bash
sudo apt install ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status verbose
```

### RHEL 服务器基础

```bash
sudo yum install firewalld
sudo systemctl enable --now firewalld
sudo firewall-cmd --set-default-zone=public
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
sudo firewall-cmd --list-all
```

### Docker + firewalld 协同

```bash
# 容器走 docker zone
sudo firewall-cmd --zone=docker --add-port=8080/tcp
sudo firewall-cmd --permanent --zone=docker --add-port=8080/tcp
sudo firewall-cmd --reload
```

## ⚠️ 注意事项

- **远程改防火墙前先备份一条**：保留 22 端口放行
- **reload 才生效**（firewalld），iptables 立即生效
- **顺序重要**：firewalld 的 zone + service 处理有先后
- **K8s / OpenShift 默认禁用 firewalld**：用 NetworkPolicy 代替

## 🔗 下一步

- [iptables](/08-firewall-ssh/iptables)
- [OpenSSH 配置](/08-firewall-ssh/openssh)
- [sshd_config 加固](/13-security/sshd-config)