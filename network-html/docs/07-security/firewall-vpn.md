---
title: 防火墙与 VPN
---

# 防火墙与 VPN

<div class="nt-badge nt-badge-security">网络安全</div>
<div class="nt-badge nt-badge-cloud">基础设施</div>

防火墙是网络边界的第一道防线，VPN 在公网上构建安全加密隧道，两者共同构成企业网络的安全底座。

## 1. 防火墙分类

| 类别 | 工作层 | 特点 |
| --- | --- | --- |
| 包过滤防火墙 | L3/L4 | 检查 IP/端口/协议 |
| 状态检测 | L4 | 跟踪连接状态 |
| 应用网关 / WAF | L7 | 解析应用协议 |
| 下一代防火墙 NGFW | L7+ | DPI、IPS、沙箱 |
| Web 应用防火墙 WAF | L7 HTTP | 防 SQL/XSS |

## 2. iptables 基础

链（chain）：

| 链 | 作用 |
| --- | --- |
| PREROUTING | 路由前（DNAT） |
| INPUT | 流入本机 |
| FORWARD | 转发 |
| OUTPUT | 本机发出 |
| POSTROUTING | 路由后（SNAT） |

```bash
# 查看规则
iptables -L -n -v
iptables -t nat -L -n

# 默认策略
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# 允许已建立连接
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# 端口转发
iptables -t nat -A PREROUTING -d 1.2.3.4 -p tcp --dport 80 -j DNAT --to-destination 192.168.1.10:80
```

## 3. nftables（新工具）

```nft
table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;
        ct state established,related accept
        iif "lo" accept
        tcp dport { 22, 80, 443 } accept
    }
}
```

## 4. WAF（Web 应用防火墙）

| 模式 | 说明 |
| --- | --- |
| 部署 | 反向代理 / 透明 / 云端 |
| 检测 | 规则 / 签名 / 机器学习 |
| 功能 | 防 SQL/XSS/CC/爬虫 |
| 厂商 | Cloudflare、ModSecurity、长亭、雷池 |

## 5. 入侵检测 / 防御

| 类别 | 模式 | 工具 |
| --- | --- | --- |
| IDS | 旁路检测，告警 | Snort、Suricata、Zeek |
| IPS | 串联检测，阻断 | Suricata、Cisco IPS |
| HIDS | 主机层 | OSSEC、Wazuh |
| EDR | 端点检测响应 | CrowdStrike、奇安信 |

## 6. VPN 概念

VPN（Virtual Private Network）在**公网**上建立**加密隧道**，让远程用户像在内网一样访问。

| 类型 | 协议 | 特点 |
| --- | --- | --- |
| IPsec VPN | IPsec | 网络层，站点到站点 |
| SSL VPN | TLS | 应用层，远程访问 |
| PPTP | GRE + MPPE | 已淘汰 |
| L2TP | L2TP + IPsec | 常用 |
| OpenVPN | TLS | 开源、跨平台 |
| WireGuard | UDP | 现代、最快 |
| ZeroTier / Tailscale | 自研 | 简单易用 |
| 站点到站点 IPsec | — | 企业分支互联 |

## 7. IPsec 详解

### 7.1 组成

- **AH**（Authentication Header）：完整性 + 认证，不加密
- **ESP**（Encapsulating Security Payload）：加密 + 认证
- **IKE**（Internet Key Exchange）：密钥协商

### 7.2 模式

| 模式 | 加密范围 | 适用 |
| --- | --- | --- |
| 传输模式 | 仅 payload | 主机到主机 |
| 隧道模式 | 整个 IP 包 | 站点到站点、远程访问 |

### 7.3 协商

```
IKEv1: 6 条消息（主模式 3 对）
IKEv2: 4 条消息
```

支持 PSK（预共享密钥）和证书两种认证。

## 8. WireGuard

现代 VPN，性能与简洁并存。

```ini
# /etc/wireguard/wg0.conf
[Interface]
Address = 10.0.0.2/24
PrivateKey = <client private key>

[Peer]
PublicKey = <server public key>
Endpoint = vpn.example.com:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
```

```bash
wg-quick up wg0
wg show
```

优势：
- 基于 Curve25519、ChaCha20、Poly1305
- 代码量 ~4000 行（OpenVPN 10w+）
- 内核级性能
- 抗量子密码

## 9. SSL VPN

- 通过浏览器 HTTPS 访问
- 客户端：Java / ActiveX / 原生 APP
- 厂商：深信服、华为、Array

## 10. 企业组网方案

| 场景 | 方案 |
| --- | --- |
| 总部-分支 | IPsec VPN、SD-WAN |
| 远程办公 | SSL VPN、WireGuard |
| 多云互联 | SD-WAN、Transit Gateway |
| 零信任访问 | ZTNA、Cloudflare Access |

## 11. 实战：内网穿透

| 工具 | 协议 |
| --- | --- |
| frp | TCP/UDP/HTTP |
| nps | TCP/UDP |
| ngrok | HTTP/TCP |
| Tailscale | WireGuard |
| ZeroTier | P2P |

## 12. 实战：堡垒机

- 集中 SSH / RDP 入口
- 录屏、审计、命令控制
- 厂商：Jumpserver、Teleport、行云管家

## 13. 零信任（Zero Trust）

| 原则 | 含义 |
| --- | --- |
| 永不信任 | 默认不信任任何用户/设备 |
| 持续验证 | 每次访问都认证 |
| 最小权限 | 最小必要权限 |
| 假定入侵 | 设计时假设已被入侵 |

代表方案：BeyondCorp（Google）、ZTNA、Cloudflare Access、Cato Networks。

## 14. 常见面试题

1. **防火墙类型？** 包过滤、状态检测、应用层、NGFW。
2. **iptables 链？** PREROUTING、INPUT、FORWARD、OUTPUT、POSTROUTING。
3. **IPsec 模式？** 传输、隧道。
4. **VPN 协议？** IPsec、OpenVPN、WireGuard、SSL VPN。
5. **WireGuard 优势？** 简洁、高性能、抗量子。
6. **零信任核心？** 永不信任、持续验证、最小权限。

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [linux](https://java-px.bot.cd/linux/):Linux 网络栈
- [security](https://java-px.bot.cd/security/):网络安全
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 网络
