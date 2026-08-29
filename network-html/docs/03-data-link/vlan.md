---
title: VLAN
date: 2026-08-15  # date-auto-injected
---

# 🔗 VLAN

> 虚拟局域网，在**物理交换机**上划分多个**逻辑上隔离**的网络。

## 🎯 为什么需要 VLAN

**没有 VLAN 的问题：**
- 所有设备在同一广播域
- 广播包泛滥（ARP、DHCP）
- 安全性差（任何设备互通）
- 网络规模受限

**VLAN 解决方案：**
```
一台物理交换机：192.168.1.0/24
├─ VLAN 10: 工程部 (端口 1-12)
├─ VLAN 20: 财务部 (端口 13-24)
└─ VLAN 30: 访客 WiFi (端口 25-36)

不同 VLAN 互相隔离 → 需路由器才能互通
```

## 📋 VLAN 类型

| 类型 | 描述 | 标识 |
|---|---|---|
| **基于端口** | 最常用 | 端口固定划分 |
| **基于 MAC** | MAC 地址划分 | 移动设备自动归类 |
| **基于协议** | 按协议类型 | IP/IPX 等 |
| **基于 IP 子网** | IP 网段划分 | 灵活 |
| **基于策略** | 组合多种规则 | 最灵活 |

## 🔌 Access 与 Trunk 端口

### Access 端口

接入终端的端口，**只属于一个 VLAN**。

```
PC ──── [Access 端口，VLAN 10] ──── 交换机
```

### Trunk 端口

交换机之间的端口，承载**多个 VLAN** 的流量。

```
交换机 A ──── [Trunk 端口] ──── 交换机 B
        VLAN 10/20/30 数据都通过
```

### 802.1Q 标记

在 Trunk 上用 4 字节 VLAN Tag 标识 VLAN ID：

```
普通以太网帧：
[Dest MAC][Src MAC][EtherType][Payload][FCS]

802.1Q 标记帧：
[Dest MAC][Src MAC][0x8100][Tag][EtherType][Payload][FCS]
                  ┌─────┴──────┐
                  │TPID(2B)|Pri(3b)|CFI|VLAN ID(12b)│
                  └─────────────────────┘
```

## 🔄 VLAN 间通信

### 1. 三层交换机（推荐）

```
[PC VLAN 10] → 交换机 → 交换机内置路由 → [PC VLAN 20]
                  ↑
            SVI 接口：interface vlan 10 / 20
```

### 2. 单臂路由

```
PC ──── 交换机 ──── Trunk ──── 路由器
                          ↑
              路由器通过子接口处理不同 VLAN
```

### 3. 路由器多接口

每个 VLAN 一根网线连路由器（不推荐）。

## 🏢 VLAN 配置实战

### 华为交换机

```bash
# 创建 VLAN
vlan batch 10 20 30

# Access 端口
interface GigabitEthernet0/0/1
port link-type access
port default vlan 10

# Trunk 端口
interface GigabitEthernet0/0/24
port link-type trunk
port trunk allow-pass vlan 10 20 30

# 三层接口（SVI）
interface Vlanif 10
ip address 192.168.10.1 255.255.255.0

# 查看 VLAN
display vlan
```

### Cisco 交换机

```bash
vlan 10
name Engineering
exit

interface Fa0/1
switchport mode access
switchport access vlan 10

interface Fa0/24
switchport mode trunk
switchport trunk allowed vlan 10,20,30

interface vlan 10
ip address 192.168.10.1 255.255.255.0
```

## 📊 私有 VLAN

**PVLAN（Private VLAN）** 用于更细粒度隔离：

```
主 VLAN（Primary）
├── 团体 VLAN（Community）：互相可通
├── 隔离 VLAN（Isolated）：互相不通
└── 混杂端口（Promiscuous）：与所有互通（如路由器）
```

**应用场景：**
- 酒店房间网络
- 数据中心多租户
- ISP 接入

## 🏢 Super VLAN

**多个子 VLAN 共享同一个 IP 网段**，节省 IP。

```
Super VLAN 10（192.168.10.0/22）
├── Sub VLAN 11：销售部
├── Sub VLAN 12：市场部
└── Sub VLAN 13：客服部

共享网关，节省 IP 地址
```

## ⚠️ VLAN 限制

| 限制 | 说明 |
|---|---|
| VLAN ID 数量 | 1-4094（12 bit）|
| Trunk 协议 | 需两端一致（Cisco 私有 ISL 已淘汰）|
| 跨数据中心 | 需 VXLAN（4094 × 16M 标识）|

## 🎓 面试高频问题

| 问题 | 关键点 |
|---|---|
| VLAN 作用？| 隔离广播域、提高安全 |
| Access vs Trunk？| Access 1 个 VLAN，Trunk 多 VLAN |
| 802.1Q Tag 长度？| 4 字节，VLAN ID 12 bit |
| VLAN 间通信？| 三层交换机 / 单臂路由 |

---

- 上一章：[🔗 以太网与交换机](/03-data-link/ethernet)
- 下一章：[🔗 STP / RSTP](/03-data-link/stp)