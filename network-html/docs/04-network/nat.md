---
title: NAT 网络地址转换
---

# NAT 网络地址转换

<div class="nt-badge nt-badge-network">网络层</div>
<div class="nt-badge nt-badge-cloud">实战</div>

NAT（Network Address Translation）通过将**私有 IP** 映射为**公网 IP**，缓解 IPv4 地址枯竭，同时提供基础防护。

## 1. 为什么需要 NAT

| 问题 | NAT 的作用 |
| --- | --- |
| IPv4 地址枯竭 | 大量内网主机共享少量公网 IP |
| 内网安全 | 外部无法主动访问内网主机 |
| 地址重叠 | 多个内网可使用相同私网段 |
| ISP 变更 | 内网无需重新编号 |

## 2. NAT 分类

| 类型 | 全称 | 特点 |
| --- | --- | --- |
| 静态 NAT | Static NAT | 一对一固定映射 |
| 动态 NAT | Dynamic NAT | 公网池动态分配 |
| PAT / NAPT | Port Address Translation | 端口级多对一（最常用） |
| Easy IP | — | 直接用出接口 IP |
| NAT64 | — | IPv6 ↔ IPv4 |

## 3. 工作原理（以 PAT 为例）

```
内网 192.168.1.10:5000  →  公网 203.0.113.5:10001
内网 192.168.1.11:5000  →  公网 203.0.113.5:10002
内网 192.168.1.10:5001  →  公网 203.0.113.5:10003
```

通过**端口号**区分不同内网会话。

### 报文修改

| 方向 | 修改字段 |
| --- | --- |
| 出向 | 源 IP（私有→公网）、源端口（必要时改） |
| 入向 | 目的 IP（公网→私有）、目的端口 |
| 校验和 | IP / TCP / UDP checksum 重新计算 |

## 4. NAT 表项

```
Protocol  Inside IP:Port       Outside IP:Port
TCP       192.168.1.10:5000  → 203.0.113.5:10001
TCP       192.168.1.11:3389  → 203.0.113.5:10002
```

会话建立时记录，超时回收（UDP ~30s，TCP ~1h）。

## 5. NAT 类型（P2P 视角）

| 类型 | 说明 |
| --- | --- |
| Full Cone | 任何外网主机可主动发回 |
| Restricted Cone | 仅曾发往的外网 IP 可发回 |
| Port Restricted | 仅曾发往的 IP+Port 可发回 |
| Symmetric | 不同目的用不同映射端口 |

## 6. NAT 穿越（NAT Traversal）

| 场景 | 方案 |
| --- | --- |
| FTP 主动模式 | PORT 命令携带内网地址，ALG 改写 |
| FTP 被动模式 | 服务器告诉客户端公网地址 |
| P2P（STUN） | 探测外网映射，对称型 NAT 需 TURN |
| IPSec / VoIP | NAT-T 封装 UDP 4500 |
| 视频会议 | ICE / TURN / STUN |

## 7. NAT 限制

- **破坏端到端原则**：外部不能主动连内网
- 某些协议嵌入 IP（如 FTP、IPSec、H.323）需 ALG
- 跟踪困难，溯源成本高
- P2P、NAT 后服务发现复杂

## 8. Linux 配置示例

```bash
# 启用 IP 转发
echo 1 > /proc/sys/net/ipv4/ip_forward

# 简单的 MASQUERADE（出接口动态 IP）
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# 端口映射（公网 80 → 内网 192.168.1.10:8080）
iptables -t nat -A PREROUTING -d 203.0.113.5 -p tcp --dport 80 \
  -j DNAT --to-destination 192.168.1.10:8080
iptables -t nat -A POSTROUTING -d 192.168.1.10 -p tcp --dport 8080 \
  -j SNAT --to-source 203.0.113.5
```

## 9. 华为 / 思科 NAT 配置

### 华为

```
acl 2000
 rule 5 permit source 192.168.1.0 0.0.0.255
nat address-group 1 203.0.113.5 203.0.113.10
interface GigabitEthernet0/0/1
 ip address 203.0.113.5 255.255.255.0
 nat outbound 2000 address-group 1
```

### 思科

```
ip access-list extended NAT-ACL
 permit ip 192.168.1.0 0.0.0.255 any
ip nat pool PUBLIC 203.0.113.5 203.0.113.10 netmask 255.255.255.0
ip nat inside source list NAT-ACL pool PUBLIC overload
interface GigabitEthernet0/0
 ip nat inside
interface GigabitEthernet0/1
 ip nat outside
```

## 10. NAT vs 代理 vs 防火墙

| 维度 | NAT | 代理 | 防火墙 |
| --- | --- | --- | --- |
| 工作层 | 网络层（L3） | 应用层（L7） | 多层 |
| 透明性 | 对应用透明 | 应用需支持 | 透明 |
| 性能 | 高 | 中（解析协议） | 视实现 |
| 缓存 | 否 | 是 | 否 |
| 防护 | 弱 | 强 | 强 |

## 11. 常见面试题

1. **NAT 解决了什么问题？** IPv4 地址不足 + 内网隔离。
2. **NAPT 和 NAT 区别？** NAT 仅 IP 转换，NAPT 还转换端口，多对一。
3. **为什么 P2P 难穿透 NAT？** 外部无法主动访问内网映射端口。
4. **端口映射用哪种 NAT？** 静态 NAT / DNAT。
5. **对称型 NAT 难穿越的原因？** 不同目标映射端口不同，外部无法预测。
6. **IPv6 是否还需要 NAT？** 不需要，地址充足。但运营商仍可能部署 NAT64。
