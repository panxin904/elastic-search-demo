---
title: DNS 解析
date: 2026-08-15  # date-auto-injected
---

# DNS 解析

> `nslookup` / `dig` / `host` / `resolvectl` 都能查 DNS。

## 🔧 命令对比

| | dig | nslookup | host | resolvectl |
|--|-----|----------|------|------------|
| 输出 | 详细（默认） | 友好 | 极简 | systemd-resolved |
| 指定 server | ✅ | ✅ | ✅ | ✅ |
| 反向 | ✅ | ✅ | ✅ | ✅ |
| trace | ✅ | ❌ | ❌ | ❌ |
| 类型过滤 | -t A/AAAA/MX | -type= | ❌ | --type= |

## 📜 基础查询

```bash
# A 记录（IPv4）
dig example.com
dig +short example.com         # 简洁输出

# AAAA（IPv6）
dig AAAA example.com

# MX（邮件）
dig MX example.com

# 全部
dig ANY example.com

# 反向（PTR）
dig -x 8.8.8.8
```

## 🎯 指定 DNS 服务器

```bash
dig @8.8.8.8 example.com        # 用 Google DNS
dig @1.1.1.1 example.com        # 用 Cloudflare DNS
dig @202.106.0.20 example.com   # 中国联通
```

## 🛤️ 跟踪解析过程

```bash
dig +trace example.com
# 显示从根 → TLD → 权威服务器的完整路径
```

## 🔍 dig 输出字段

```
; <<>> DiG 9.18 <<>> example.com
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0

;; QUESTION SECTION:
;example.com.            IN      A

;; ANSWER SECTION:
example.com.     86400   IN      A       93.184.216.34

;; Query time: 12 msec
;; SERVER: 8.8.8.8#53
;; WHEN: ...
;; MSG SIZE  rcvd: 56
```

| 字段 | 含义 |
|------|------|
| `status` | NOERROR / NXDOMAIN（不存在）/ SERVFAIL |
| `flags` | `aa`（权威）/ `rd`（递归）/ `ra`（递归可用） |
| `ANSWER` | 结果记录数 |
| `TTL` | 缓存时间（秒） |

## 🔧 nslookup

```bash
nslookup example.com             # 默认 server
nslookup example.com 8.8.8.8      # 指定 server
nslookup -type=MX example.com
nslookup -type=NS example.com    # NS 记录
```

## 🪄 host

```bash
host example.com                 # 等价 dig +short
host -t MX example.com
host -t NS example.com           # 列出权威 NS
```

## 🪟 systemd-resolved (resolvectl)

```bash
resolvectl status                # 看 DNS 配置
resolvectl query example.com
resolvectl -t MX example.com

# 设置 DNS（临时）
sudo resolvectl dns eth0 8.8.8.8 1.1.1.1
```

## 📋 /etc/resolv.conf

```bash
cat /etc/resolv.conf
# nameserver 8.8.8.8
# nameserver 1.1.1.1
# search example.com
```

⚠️ 不要手动编辑——`systemd-resolved` / `NetworkManager` 会覆盖。

## 🛠 实战

### DNS 不通排查

```bash
# 1. 是否能解析
nslookup example.com

# 2. 慢？
dig example.com | grep "Query time"
# > 100ms 算慢

# 3. 哪个 server 慢
for d in 8.8.8.8 1.1.1.1 202.106.0.20; do
  dig @$d example.com +stats | grep "Query time"
done

# 4. 看是否是某个域名慢
time dig github.com
time dig baidu.com
```

### 反向 DNS（IP 反查域名）

```bash
dig -x 8.8.8.8 +short
# google-public-dns-a.google.com.
```

邮件服务器的反向解析很重要——很多邮件服务拒收无反向 DNS 的 IP。

### DNS 缓存

```bash
# systemd-resolved 看命中
resolvectl statistics

# 清缓存
sudo resolvectl flush-caches
sudo systemd-resolve --flush-caches    # 旧版本

# NSCD（nscd）
sudo nscd -i hosts

# dnsmasq（本地 DNS）
sudo killall -HUP dnsmasq

# 应用级缓存（curl）
# 默认无
```

### 记录类型速查

| 类型 | 含义 |
|------|------|
| A | IPv4 |
| AAAA | IPv6 |
| CNAME | 别名 |
| MX | 邮件服务器 |
| NS | 权威 DNS |
| TXT | 文本（SPF / DKIM / 域名验证） |
| SOA | 起始授权记录 |
| PTR | 反向 DNS |
| CNAME | 别名 |
| SRV | 服务定位（LDAP / SIP） |
| CAA | 限定 CA |

```bash
# TXT 记录（SPF）
dig TXT example.com
# "v=spf1 include:_spf.google.com ~all"
```

## 🪛 调试高级

```bash
# 完整 trace
dig +trace example.com

# 强制 TCP（避免 UDP 丢包）
dig +tcp example.com

# 指定 EDNS（更大响应）
dig +bufsize=4096 example.com

# 实时观察（per-second）
watch -n 1 dig example.com +short

# 看 /etc/hosts
getent hosts example.com
# 看是否走 hosts

# 看 nsswitch 配置
cat /etc/nsswitch.conf
# hosts: files dns    ← files = /etc/hosts 在 dns 之前
```

## 🔗 下一步

- [ip / ifconfig](/07-network/ip)
- [ping / traceroute](/07-network/ping)
- [OpenSSH 配置](/08-firewall-ssh/openssh)