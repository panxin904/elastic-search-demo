---
title: STP / RSTP
date: 2026-08-15  # date-auto-injected
---

# 🔗 STP / RSTP

> 生成树协议，防止**交换机环路**导致的广播风暴。

## 🎯 为什么需要 STP

**交换机环路的危害：**
```
SW1 ─── SW2
 │      │
 │      │
SW3 ─── SW4

如果形成环路：
1. 广播包无限循环（广播风暴）
2. MAC 表不断震荡
3. 网络完全瘫痪
```

## 🌳 STP 原理

**Spanning Tree Protocol（IEEE 802.1D）**

通过**选举**机制，关闭某些端口，打破环路：

```
SW1 ─── SW2      SW1 ─── SW2
 │      │   →     │      │
 │      │         │  X   │  (SW3-SW4 端口被关闭)
SW3 ─── SW4      SW3 ─── SW4
```

## 📊 STP 选举过程

### 1. 选举根桥（Root Bridge）

```
选举规则：Bridge ID 最小的交换机成为根桥
Bridge ID = 优先级（16 bit）+ MAC 地址（48 bit）

默认优先级：32768（0x8000）
```

**实例：**
- SW1: Priority 32768, MAC 00:00:00:00:00:01
- SW2: Priority 32768, MAC 00:00:00:00:00:02

→ SW1 为根桥（MAC 较小）

### 2. 选举根端口（Root Port）

每个**非根桥**交换机选择到根桥**路径开销最小**的端口作为根端口。

### 3. 选举指定端口（Designated Port）

每个**网段**选举一个指定端口，负责该网段的转发。

### 4. 阻塞其他端口

剩余端口进入 **Blocking** 状态，不转发数据。

## 🌲 端口状态

| 状态 | 监听 BPDU | 学习 MAC | 转发数据 | 说明 |
|---|---|---|---|---|
| Disabled | ❌ | ❌ | ❌ | 端口关闭 |
| Blocking | ✅ | ❌ | ❌ | 接收 BPDU，不学习 |
| Listening | ✅ | ❌ | ❌ | 准备转发 |
| Learning | ✅ | ✅ | ❌ | 学习 MAC 表 |
| Forwarding | ✅ | ✅ | ✅ | 正常转发 |
| Broken | ❌ | ❌ | ❌ | 端口故障 |

**收敛时间：30-50 秒**

## 📦 BPDU（桥协议数据单元）

交换机之间通过 BPDU 交换信息：

```
BPDU 字段：
- Root Bridge ID
- Sender Bridge ID
- Root Path Cost
- Message Age
- Hello Time（2 秒）
- Max Age（20 秒）
- Forward Delay（15 秒）
```

## ⚡ RSTP（快速生成树）

**Rapid Spanning Tree Protocol（IEEE 802.1w）**

### RSTP vs STP 对比

| 维度 | STP (802.1D) | RSTP (802.1w) |
|---|---|---|
| 收敛时间 | 30-50 秒 | < 6 秒 |
| 端口状态 | 5 种 | 3 种 |
| 端口角色 | 3 种 | 4 种 |
| BPDU 处理 | 被动 | 主动 |
| 拓扑变化通知 | 慢 | 快 |

### RSTP 端口状态

- **Discarding**（替代 Blocking + Listening）
- **Learning**
- **Forwarding**

### RSTP 端口角色

| 角色 | 含义 |
|---|---|
| Root Port | 到根桥的最佳端口 |
| Designated Port | 转发端口 |
| **Alternate Port** | 备份根端口（替代） |
| **Backup Port** | 备份指定端口（共享段） |

## 🌐 MSTP（多生成树）

**Multiple Spanning Tree Protocol（IEEE 802.1s）**

将多个 VLAN 映射到**几个生成树实例**，实现负载均衡。

```
MSTP 实例 1：VLAN 10, 20 → 走链路 A
MSTP 实例 2：VLAN 30, 40 → 走链路 B

避免单链路浪费
```

## ⚙️ 保护机制

### 1. BPDU Guard

收到 BPDU 时立即关闭端口（防非法设备接入）。

```bash
# 华为
stp bpdu-protection

# Cisco
spanning-tree portfast bpduguard
```

### 2. Root Guard

强制某端口不能成为根端口（防外部接入抢根）。

```bash
# Cisco
spanning-tree guard root
```

### 3. Loop Guard

防止单向链路导致阻塞端口误转为转发。

```bash
# Cisco
spanning-tree loopguard default
```

### 4. UDLD

检测单向链路故障（光纤常见）。

## 🛠️ 实战配置

### 华为

```bash
# 全局启用 STP
stp enable
stp mode rstp

# 设置优先级
stp priority 4096

# 端口配置
interface GigabitEthernet0/0/1
stp enable
stp edged-port enable    # 边缘端口（接入终端，立即 Forwarding）
```

### Cisco

```bash
spanning-tree mode rapid-pvst
spanning-tree vlan 1 priority 4096

interface Fa0/1
spanning-tree portfast
spanning-tree bpduguard enable
```

## 🎓 面试高频问题

| 问题 | 关键点 |
|---|---|
| STP 作用？| 防止交换机环路 |
| 根桥选举？| Bridge ID 最小（优先级 + MAC）|
| STP 收敛时间？| 30-50 秒 |
| RSTP 改进？| < 6 秒，端口角色更丰富 |

---

- 上一章：[🔗 VLAN](/03-data-link/vlan)
- 下一章：[🌍 IP 地址](/04-network/ip-address)