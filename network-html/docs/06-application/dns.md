---
title: DNS 域名解析
---

# DNS 域名解析

<div class="nt-badge nt-badge-app">应用层</div>
<div class="nt-badge nt-badge-basics">基础</div>

DNS（Domain Name System）将人类可读的域名（如 `www.example.com`）转换为 IP 地址，是互联网的"电话簿"。

## 1. DNS 核心概念

| 概念 | 说明 |
| --- | --- |
| 域名空间 | 树形结构，根 → 顶级域 → 二级域 |
| 域名服务器 | 提供解析服务的服务器 |
| 资源记录 | 域名的具体信息（A、AAAA、MX...） |
| 解析器 | 客户端发起查询的程序 |
| 缓存 | 减少重复查询 |

## 2. 域名层级

```
                .                          ← 根
                |
       +--------+--------+
       |                 |
      .com              .cn                ← 顶级域 (TLD)
       |                 |
   +---+---+         +---+---+
   |       |         |       |
example  baidu   example  aliyun             ← 二级域
   |
www  api  mail                              ← 子域
```

完整域名：根以 `.` 结尾，如 `www.example.com.`

## 3. 域名服务器类型

| 类型 | 作用 |
| --- | --- |
| 根域名服务器 | 全球 13 组，管理 TLD |
| TLD 服务器 | `.com` / `.cn` / `.org` 等 |
| 权威 DNS | 某域的最终答案 |
| 递归 DNS | 替客户端完整查询（运营商 / 8.8.8.8） |
| 转发 DNS | 转发到上游递归 |

## 4. DNS 查询流程

```
客户端 → 递归 DNS → 根 → TLD → 权威
```

**递归查询**：客户端只问一次，递归 DNS 帮它问到底。
**迭代查询**：每个服务器返回"问下一个"。

```
Client → Local DNS: www.example.com?
Local DNS → Root: ?
Root: 问 .com 服务器
Local DNS → .com TLD: ?
.com: 问 example.com 的权威
Local DNS → Authoritative: ?
Authoritative: 93.184.216.34
Local DNS → Client: 93.184.216.34
```

## 5. 资源记录类型

| 类型 | 含义 | 示例 |
| --- | --- | --- |
| A | IPv4 地址 | example.com A 93.184.216.34 |
| AAAA | IPv6 地址 | example.com AAAA 2606:2800:220:1:... |
| CNAME | 别名 | www.example.com CNAME example.com |
| MX | 邮件服务器 | example.com MX 10 mail.example.com |
| NS | 权威 DNS | example.com NS ns1.example.com |
| TXT | 文本（SPF/DKIM） | "v=spf1 include:_spf.google.com ~all" |
| SOA | 起始授权 | 主 DNS、管理员邮箱、序列号 |
| SRV | 服务定位 | _sip._tcp.example.com SRV 10 60 5060 sip.example.com |
| PTR | 反向解析 | 34.216.184.93.in-addr.arpa PTR example.com |
| CAA | CA 授权 | example.com CAA 0 issue "letsencrypt.org" |

## 6. DNS 报文

```
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|  ID (16)     | QR | Op | AA|TC|RD|RA| Z | RCODE|
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|  QDCOUNT      |  ANCOUNT     | NSCOUNT     | ARCOUNT |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|              Question / Answer / ...          |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
```

| 字段 | 含义 |
| --- | --- |
| QR | 0=查询 1=响应 |
| Opcode | 0=标准查询 |
| AA | 权威回答 |
| TC | 截断 |
| RD | 期望递归 |
| RA | 可递归 |
| RCODE | 响应码（0=无错、3=不存在 NXDOMAIN） |

## 7. DNS 协议

- 端口：53（UDP / TCP）
- UDP 报文上限 512B，超出走 TCP
- 响应 > 512B → EDNS 扩展（典型 4096B）
- 区域传输（AXFR/IXFR）必须用 TCP

## 8. 完整解析流程（含缓存）

```
1. 浏览器检查自身缓存
2. 操作系统检查 hosts / nscd / systemd-resolved
3. 路由器 DNS（如有）
4. 递归 DNS（运营商 / 8.8.8.8）
   - 检查本地缓存
   - 问根 → 问 TLD → 问权威
5. 缓存到递归 DNS（TTL）
6. 返回给客户端
7. 客户端缓存（受 TTL 控制）
```

## 9. 智能 DNS 与 GSLB

- **智能 DNS**：根据客户端 IP、地理位置、运营商返回不同结果
- **GSLB**（Global Server Load Balancing）：跨地域流量调度
- 应用：CDN 调度、跨境访问加速、灾备

## 10. DNS 安全

| 攻击 | 防御 |
| --- | --- |
| DNS 欺骗 / 缓存投毒 | DNSSEC（签名验证） |
| DNS 劫持 | DoH / DoT（加密查询） |
| DDoS | Anycast 扩散、限速、源认证 |
| 子域接管 | 监控 dangling CNAME |

### DoH / DoT

| 协议 | 端口 | 形式 |
| --- | --- | --- |
| DoT（DNS over TLS） | 853 | TLS 加密 |
| DoH（DNS over HTTPS） | 443 | HTTPS 包装 |

## 11. 常用命令

```bash
# 基础查询
dig example.com
dig +short example.com A

# 指定 DNS
dig @8.8.8.8 example.com

# 跟踪
dig +trace example.com

# 反向
dig -x 8.8.8.8

# 批量
nslookup example.com
host example.com
```

## 12. 常见面试题

1. **DNS 端口？** 53（UDP/TCP）。
2. **DNS 用 TCP 还是 UDP？** 多数用 UDP，> 512B / 区域传输用 TCP。
3. **递归 vs 迭代？** 递归：客户端问一次，DNS 帮到底；迭代：客户端多次问。
4. **DNS 缓存多久？** 由记录的 TTL 决定。
5. **CNAME 与 A 区别？** CNAME 是别名（需要再解析一次），A 直接给 IP。
6. **DNS 攻击常见？** 缓存投毒、DDoS、域名劫持。

<!-- svg-injected:do-not-edit -->

![dns resolution](/dns-resolution.svg)
