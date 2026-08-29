---
title: 数据封装与解封装
date: 2026-08-15  # date-auto-injected
---

# 📦 数据封装与解封装

> 网络通信过程中数据如何被**层层包装**和**层层拆解**。

## 🎯 封装过程（发送方）

```
应用层   HTTP 报文     "GET / HTTP/1.1..."
        ↓
传输层   TCP 段       [TCP 头] + 数据
        ↓
网络层   IP 包        [IP 头] + TCP 段
        ↓
数据链路层 帧          [MAC 头] + IP 包 + [FCS]
        ↓
物理层   比特流       10101100 01010010...
```

**每层加上自己的头部（Header）**

## 🎯 解封装过程（接收方）

```
物理层   比特流        接收电信号
        ↓
数据链路层 帧           去掉 MAC 头
        ↓
网络层   IP 包          去掉 IP 头
        ↓
传输层   TCP 段         去掉 TCP 头
        ↓
应用层   HTTP 报文      交给浏览器处理
```

## 📊 各层头部格式

### TCP 头部（20 字节）

```
0                   1                   2                   3
0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Source Port          |       Destination Port        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                        Sequence Number                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Acknowledgment Number                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Data |           |U|A|P|R|S|F|                               |
| Offset| Reserved  |R|C|S|S|Y|I|            Window             |
|       |           |G|K|H|T|N|N|                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|           Checksum            |         Urgent Pointer        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Options                    |    Padding    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### IP 头部（20 字节）

```
0                   1                   2                   3
0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|Version|  IHL  |Type of Service|          Total Length         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Identification        |Flags|      Fragment Offset    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Time to Live |    Protocol   |         Header Checksum       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       Source Address                          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Destination Address                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### 以太网帧（最小 64 字节）

```
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|     6 字节   |     6 字节   | 2 字节 |  46-1500 字节  | 4 字节 |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Dest MAC    |   Src MAC    | Type  |    Payload    |   FCS   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   目标 MAC      源 MAC      协议类型  IP 包等        CRC 校验
```

## 🔄 实际抓包示例（Wireshark）

```
Frame 1: 74 bytes on wire (592 bits), 74 bytes captured (592 bits)
Ethernet II, Src: 00:1a:2b:3c:4d:5e, Dst: aa:bb:cc:dd:ee:ff
Internet Protocol Version 4, Src: 192.168.1.100, Dst: 93.184.216.34
Transmission Control Protocol, Src Port: 54321, Dst Port: 443
Transport Layer Security
    TLSv1.3 Record Layer: Handshake
        Client Hello
```

## 🎯 MTU（最大传输单元）

| 网络 | MTU（字节）|
|---|---|
| Ethernet | 1500 |
| PPPoE | 1492 |
| 4G LTE | 1500 |
| WiFi | 1500 |
| 巨型帧 (Jumbo Frame) | 9000 |

**分片：** 当 IP 包 > MTU 时，路由器会**分片**，到达后再**重组**。

```
原始包（3000 字节）→ MTU=1500 → 分为 2 片
  第 1 片：1500 字节（含 20 字节 IP 头）
  第 2 片：1500 字节（含 20 字节 IP 头）
```

**DF 位（Don't Fragment）：** 设置为 1 时不分片，超大则返回 ICMP 错误。
**MF 位（More Fragments）：** 还有分片时设置为 1。

## ⚠️ 常见问题

### 1. MSS（Maximum Segment Size）

```
MSS = MTU - IP 头 - TCP 头 = 1500 - 20 - 20 = 1460
```

TCP 协商时会取最小 MSS，避免分片。

### 2. Path MTU Discovery

路径上**最小 MTU** 决定最大包大小：
1. 发送包设置 DF=1
2. 中间路由器发现超出 MTU
3. 返回 ICMP "Fragmentation Needed"
4. 发送方降低包大小重试

### 3. 数据单位

| 层 | 单位 | 名称 |
|---|---|---|
| 应用层 | 报文 | Message |
| 传输层 | 段 | Segment（TCP）/ Datagram（UDP）|
| 网络层 | 包 | Packet / Datagram |
| 数据链路层 | 帧 | Frame |
| 物理层 | 比特 | Bit |

## 🛠️ 实际命令

```bash
# 查看本机 MTU
ip link show
# 或
netstat -i

# 设置 MTU
sudo ip link set eth0 mtu 1400

# 查看 MSS
ss -i

# 抓包看封装
tcpdump -i any -nn -X port 80
```

## 🎓 面试高频问题

| 问题 | 关键点 |
|---|---|
| 数据单位？| 报文/段/包/帧/比特 |
| 什么是 MTU？| 最大传输单元，Ethernet 默认 1500 |
| 什么是分片？| IP 包超过 MTU 时被拆分，到达后重组 |
| Path MTU Discovery？| 探测路径最小 MTU，避免分片 |

---

- 上一章：[📡 TCP/IP 四层模型](/01-basics/tcp-ip)
- 下一章：[📊 网络性能指标](/01-basics/metrics)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [linux](https://java-px.bot.cd/linux/):Linux 网络栈
- [security](https://java-px.bot.cd/security/):网络安全
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 网络
