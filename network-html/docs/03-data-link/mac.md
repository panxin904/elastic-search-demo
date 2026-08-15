---
title: MAC 地址
---

# 🔗 MAC 地址

> 网络设备的**物理地址**，是数据链路层的核心标识。

## 🎯 什么是 MAC 地址

**MAC（Media Access Control）地址**是网卡出厂时固化的 48 位物理地址，全球唯一。

```
MAC 地址格式（48 bit = 6 字节）：

00:1A:2B:3C:4D:5E
││ ││ ││ ││ ││ ││
││ └──┴┴──┴┴──┴┴ OUI（厂商代码）
└┴┴────────────── NIC（网卡序列）
```

## 📋 分类

### 单播 / 多播 / 广播

| 类型 | 第 8 位 | 范围 | 用途 |
|---|---|---|---|
| **单播** | 0 | 00:xx:xx:xx:xx:xx | 一对一通信 |
| **多播** | 1 | 01:xx:xx:xx:xx:xx | 一对多（一组）|
| **广播** | - | FF:FF:FF:FF:FF:FF | 局域网所有设备 |

### 全球唯一 vs 本地管理

| 范围 | 第 2 位 | 含义 |
|---|---|---|
| U/L = 0 | 全球唯一（OUI 分配）| 厂商出厂固定 |
| U/L = 1 | 本地管理 | 可手动修改 |

## 🛠️ 查看与修改 MAC

```bash
# Linux 查看 MAC
ip link show
# link/ether 00:1a:2b:3c:4d:5e

# Windows 查看
ipconfig /all

# 修改 MAC（Linux）
sudo ip link set dev eth0 down
sudo ip link set dev eth0 address 00:11:22:33:44:55
sudo ip link set dev eth0 up

# 查看厂商（OUI）
curl https://api.macvendors.com/00:1A:2B
# 返回厂商名称
```

## 🎯 MAC 地址作用

### 1. 局域网寻址

```
PC-A (192.168.1.100, MAC: AA:AA:AA:AA:AA:AA)
   ↓ 发送包给 PC-B (192.168.1.101)
   ↓ 需要 PC-B 的 MAC 地址
   ↓ 通过 ARP 协议获取
数据包：
[目标 MAC: BB:BB:BB:BB:BB:BB] [源 MAC: AA:AA:AA:AA:AA:AA] [IP 包]
```

### 2. 网络隔离

```bash
# 交换机基于 MAC 地址转发
# 路由器基于 IP 地址转发
```

### 3. 设备识别

- 网卡故障定位
- 网络准入控制（NAC）
- 软件授权（绑定 MAC）

## ⚠️ MAC 地址的局限

| 局限 | 说明 |
|---|---|
| 不能跨网段 | MAC 只在局域网内有效 |
| 可被修改 | 软件层面可改 MAC |
| 不安全 | 容易被伪造（MAC 欺骗）|

## 🛡️ 安全防护

**MAC 泛洪攻击（Flooding）：**
- 攻击者发送大量伪造 MAC
- 交换机的 MAC 表溢出
- 进入"失败开放"模式（类似集线器）

**防护：**
```bash
# 配置 MAC 地址学习数量限制（Cisco）
switchport port-security maximum 5
switchport port-security violation restrict

# 配置静态 MAC 绑定
switchport port-security mac-address 0011.2233.4455
```

## 🎓 面试高频问题

| 问题 | 关键点 |
|---|---|
| MAC 地址长度？| 48 位 = 6 字节 |
| MAC 地址能否跨网段？| 否，仅局域网内 |
| 单播/多播/广播？| 第 8 位 0/1，全 F 广播 |
| OUI 是什么？| 前 24 位厂商标识 |

---

- 下一章：[🔗 以太网与交换机](/03-data-link/ethernet)