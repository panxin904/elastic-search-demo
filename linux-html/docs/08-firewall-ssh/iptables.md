---
title: iptables
---

# iptables 防火墙

> Linux 内核级防火墙 netfilter 的用户空间管理工具。

## 🧠 概念：表 + 链 + 规则

```
表 (table)     - 用途
  filter       - 默认，访问控制（放行 / 拒绝）
  nat          - 网络地址转换（SNAT / DNAT）
  mangle       - 修改包头
  raw           - 跟踪连接
  security     - SELinux 标记

链 (chain)     - 在哪生效
  PREROUTING    - 进网卡前（NAT）
  INPUT         - 到本机（filter）
  FORWARD       - 转发（filter）
  OUTPUT        - 出本机（filter / nat）
  POSTROUTING   - 出网卡前（NAT）

规则 (rule)    - 匹配 + 动作
```

## 📜 基础命令

```bash
# 看规则（默认 filter 表）
sudo iptables -L -n
sudo iptables -L -n -v          # 看详细计数

# 看 nat / mangle
sudo iptables -t nat -L -n

# 看完整规则（含行号）
sudo iptables -L -n --line-numbers

# 清空
sudo iptables -F                # 所有规则
sudo iptables -X                # 自定义链
```

## 🎯 INPUT 链：管理入站

```bash
# 默认：拒绝所有
sudo iptables -P INPUT DROP

# 允许已建立连接
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# 允许 lo
sudo iptables -A INPUT -i lo -j ACCEPT

# 允许 SSH（端口 22）
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp -s 192.168.1.0/24 --dport 22 -j ACCEPT  # 仅内网

# 允许 HTTP / HTTPS
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# 允许 ICMP（ping）
sudo iptables -A INPUT -p icmp --icmp-type 8 -j ACCEPT
sudo iptables -A INPUT -p icmp -j ACCEPT     # 全部 ICMP（含 ping 响应）

# 允许特定 IP
sudo iptables -A INPUT -s 203.0.113.50 -j ACCEPT

# 拒绝特定 IP（log）
sudo iptables -A INPUT -s 198.51.100.0/24 -j LOG --log-prefix "DROPPED: "
sudo iptables -A INPUT -s 198.51.100.0/24 -j DROP
```

## 🏠 OUTPUT 链：管出站

```bash
# 默认放行所有出站（最常见）
sudo iptables -P OUTPUT ACCEPT

# 或白名单：仅允许特定出口
sudo iptables -A OUTPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
sudo iptables -A OUTPUT -o lo -j ACCEPT
sudo iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
sudo iptables -P OUTPUT DROP
```

## 🔀 FORWARD 链：转发（路由器/网关）

```bash
# 启用转发（NAT 网关）
sudo iptables -A FORWARD -i eth0 -o eth1 -j ACCEPT
sudo iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT

# 启用 ipv4 转发
sudo sysctl -w net.ipv4.ip_forward=1
# 永久：/etc/sysctl.conf → net.ipv4.ip_forward = 1
```

## 🔄 NAT：网络地址转换

```bash
# SNAT（内网 → 外网共用公网 IP）
sudo iptables -t nat -A POSTROUTING -s 192.168.1.0/24 -o eth0 -j MASQUERADE

# DNAT（端口转发：外网 80 → 内网 web 8080）
sudo iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 80 \
  -j DNAT --to-destination 192.168.1.10:8080

# 转发后 filter 也要放行
sudo iptables -A FORWARD -d 192.168.1.10 -p tcp --dport 8080 -j ACCEPT
```

## 🧰 常用模块

```bash
# multiport：多端口
sudo iptables -A INPUT -p tcp -m multiport --sports 22,80,443 -j ACCEPT

# connlimit：限制并发
sudo iptables -A INPUT -p tcp --dport 80 -m connlimit --connlimit-above 50 -j REJECT

# recent：防暴力破解
sudo iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --set
sudo iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --update --seconds 60 --hitcount 4 -j DROP
# 60 秒内连接 4 次以上 SSH 就 drop

# limit：限速
sudo iptables -A INPUT -p icmp --icmp-type 8 -m limit --limit 5/s -j ACCEPT
```

## 💾 持久化

```bash
# 装 iptables-persistent
sudo apt install iptables-persistent

# 保存
sudo netfilter-persistent save
sudo netfilter-persistent reload

# 或手工
sudo iptables-save > /etc/iptables.rules
sudo iptables-restore < /etc/iptables.rules
```

## 🧱 实战：Web 服务器

```bash
#!/bin/bash
# 通用 web 服务器规则
IPT=/sbin/iptables

$IPT -F INPUT
$IPT -P INPUT DROP

# 本地回环
$IPT -A INPUT -i lo -j ACCEPT

# 已建立连接
$IPT -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# SSH（限内网）
$IPT -A INPUT -p tcp -s 192.168.1.0/24 --dport 22 -j ACCEPT

# HTTP / HTTPS
$IPT -A INPUT -p tcp --dport 80 -j ACCEPT
$IPT -A INPUT -p tcp --dport 443 -j ACCEPT

# ICMP
$IPT -A INPUT -p icmp -j ACCEPT

# 防止 SSH 暴力破解
$IPT -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --set
$IPT -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --update --seconds 60 --hitcount 4 -j DROP

# 拒绝 + 日志
$IPT -A INPUT -m limit --limit 5/min -j LOG --log-prefix "iptables-denied: " --log-level 7
```

## ⚠️ 注意事项

- `iptables` 操作**立即生效**，没有 reload 概念
- 配错规则会**锁死 SSH** —— 永远先保留一条 ACCEPT 22
- 远程配防火墙前先开一个**长会话**作为 backup
- 调试：`-v -n` 看计数变化

```bash
# 安全调试：所有动作前加 LOG
sudo iptables -I INPUT 1 -j LOG --log-prefix "DEBUG: "

# 看计数（确认命中）
sudo iptables -L -n -v

# 不再需要时 -D 删除规则
```

## 🆚 iptables vs nftables

| | iptables | nftables |
|--|----------|----------|
| 后端 | xtables | nf_tables |
| 性能 | 中 | 快 |
| 语法 | 多命令 | 一套（nft） |
| 状态 | 仍主流 | 新默认（RHEL 8+ / Debian 11+） |

`nft` 是未来。Ubuntu 22 / Debian 12 起可用 `nft list ruleset`。

## 🔗 下一步

- [ufw / firewalld](/08-firewall-ssh/ufw-firewalld)
- [OpenSSH 配置](/08-firewall-ssh/openssh)
- [SELinux](/13-security/selinux)