---
title: OSPF 与 BGP
date: 2026-08-15  # date-auto-injected
---

# OSPF 与 BGP

<div class="nt-badge nt-badge-network">路由协议</div>
<div class="nt-badge nt-badge-interview">高频</div>

OSPF（Open Shortest Path First）是主流的**链路状态 IGP**；BGP（Border Gateway Protocol）是互联网的**路径矢量 EGP**。两者共同支撑了企业内网与公网骨干的路由。

## 1. 对比概览

| 维度 | OSPF | BGP |
| --- | --- | --- |
| 类别 | IGP | EGP |
| 算法 | 链路状态（SPF） | 路径矢量 |
| 范围 | AS 内部 | AS 之间 |
| 收敛 | 快 | 较慢 |
| 度量 | Cost（接口带宽） | 路径属性（AS-Path、Local-Pref 等） |
| 默认 AD | 110 | 20（eBGP）/200（iBGP） |
| 协议号 | 89（IP） | 179（TCP） |
| 应用 | 企业网、运营商内部 | 互联网骨干、IDC 多线 |

## 2. OSPF 核心概念

### 2.1 区域（Area）

```
        Area 0 (Backbone)
        ┌────┴────┐
      Area 1   Area 2
```

- 区域 0 是骨干，所有非骨干必须连到骨干
- 多区域减少 LSDB 规模，SPF 重算范围缩小

### 2.2 Router ID

- 32 bit，唯一标识 OSPF 路由器
- 选举规则：手动 > Loopback IP > 物理接口最大 IP

### 2.3 LSA 类型

| Type | 名称 | 描述 |
| --- | --- | --- |
| 1 | Router LSA | 每个路由器产生，描述自身链路 |
| 2 | Network LSA | DR 产生，描述 MA 网络 |
| 3 | Summary LSA | ABR 通告区域间路由 |
| 4 | ASBR Summary | 通告 ASBR 位置 |
| 5 | AS External | AS 外部路由 |
| 7 | NSSA External | NSSA 区域外部 |

### 2.4 邻居关系

- **2-Way**：发现邻居
- **ExStart**：协商主从
- **Exchange**：交换 LSDB 摘要
- **Loading**：请求缺失 LSA
- **Full**：完全邻接

### 2.5 DR / BDR

- 广播 / NBMA 网络选举 DR（Designated Router）
- DR 减少邻接关系（n² → n）
- BDR 为 DR 备份

## 3. OSPF 网络类型

| 类型 | 邻居发现 | DR 选举 |
| --- | --- | --- |
| Broadcast | 自动 | 选举 |
| Point-to-Point | 自动 | 不选举 |
| NBMA | 手动 | 选举 |
| Point-to-Multipoint | 自动 | 不选举 |

## 4. OSPF 配置示例（Cisco）

```
router ospf 1
 router-id 1.1.1.1
 network 10.0.0.0 0.255.255.255 area 0
 network 192.168.1.0 0.0.0.255 area 1
 passive-interface default
 no passive-interface GigabitEthernet0/0
```

## 5. BGP 核心概念

### 5.1 AS（Autonomous System）

- 16 bit ASN（65535 公有，23456 私有替代 32 bit）
- 一个 AS 是一个独立管理域

### 5.2 eBGP vs iBGP

| 维度 | eBGP | iBGP |
| --- | --- | --- |
| 邻居 | 不同 AS | 同 AS |
| TTL | 默认 1 | 默认 255 |
| AS-Path | 增加 | 不变 |
| 防环 | AS-Path | 水平分割（不向 iBGP 反射学到的路由） |

### 5.3 路径属性

| 属性 | 类别 | 说明 |
| --- | --- | --- |
| Weight | Cisco 私有 | 本地优选，0~65535 |
| Local Preference | Well-known | AS 内优选 |
| AS-Path | Well-known | 防环 + 路径长度 |
| Origin | Well-known | IGP > EGP > Incomplete |
| MED（Multi-Exit Disc） | Optional | 告诉邻居怎么进来 |
| Next Hop | Well-known | 下一跳 |
| Community | Optional transitive | 路由标记 |

### 5.4 选路顺序

1. Weight 最高
2. Local Preference 最高
3. 本地起源（network/aggregate/redistribute）
4. AS-Path 最短
5. Origin 类型（IGP < EGP < Incomplete）
6. MED 最低
7. eBGP > iBGP
8. Next Hop IGP metric 最低
9. Router ID 最小

## 6. BGP 报文

| Type | 作用 |
| --- | --- |
| OPEN | 建立邻居 |
| KEEPALIVE | 保活（60s） |
| UPDATE | 通告路由（NLRI + 属性） |
| NOTIFICATION | 错误通知，拆连接 |
| ROUTE-REFRESH | 路由刷新 |

## 7. BGP 配置示例

```
router bgp 65010
 bgp router-id 1.1.1.1
 neighbor 10.0.0.2 remote-as 65020
 neighbor 10.0.0.2 description "ISP-A"
 network 192.168.1.0 mask 255.255.255.0
 !
 address-family ipv4 unicast
  neighbor 10.0.0.2 activate
  neighbor 10.0.0.2 route-map SET-LP in
```

## 8. OSPF 防环 vs BGP 防环

| OSPF | BGP |
| --- | --- |
| 每区域独立 SPF | AS-Path 长度 + 不接收含自身 ASN 的路由 |
| 区域间通过 ABR | iBGP 水平分割（全互联或 RR） |

## 9. 常见面试题

1. **OSPF 怎么选路？** SPF（Dijkstra），基于链路 Cost。
2. **BGP 怎么选路？** 多属性优先级排序（Weight > LocalPref > AS-Path...）。
3. **eBGP 默认 TTL？** 1（防跨 AS）。iBGP 255。
4. **iBGP 水平分割？** 从 iBGP 邻居学到的路由不传给其他 iBGP 邻居。
5. **BGP 为什么要全互联或 RR？** 防 iBGP 环路 + 保证同步。
6. **OSPF 区域 0 作用？** 骨干区域，所有非骨干必须连到它。
