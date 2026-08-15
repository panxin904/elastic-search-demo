---
title: UDP 协议
---

# UDP 协议

<div class="nt-badge nt-badge-transport">传输层</div>
<div class="nt-badge nt-badge-basics">入门</div>

UDP（User Datagram Protocol）是一种**无连接、不可靠、面向报文**的传输层协议，追求**低延迟**和**简单**。

## 1. UDP 特性

| 特性 | 说明 |
| --- | --- |
| 无连接 | 通信前不握手，发送即结束 |
| 不可靠 | 不确认、不重传、不排序 |
| 面向报文 | 一次 send 对应一个完整报文 |
| 头部小 | 固定 8 字节 |
| 无拥塞控制 | 不会自动降速 |
| 支持单播 / 组播 / 广播 | 一对多通信 |
| 全双工 | 同一 socket 可收发 |

## 2. UDP 报文格式

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Source Port (16)     |    Destination Port (16)      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|        Length (16)            |        Checksum (16)          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                     Data (variable)                           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

| 字段 | 长度 | 说明 |
| --- | --- | --- |
| Source Port | 2B | 可选，0 表示无 |
| Dest Port | 2B | 必填 |
| Length | 2B | 头部 + 数据总长度 |
| Checksum | 2B | 可选，IPv6 强制 |

> UDP 长度 = 头部 8B + 数据，最小 8B，理论最大 65535B（含 IP 头会分片）。

## 3. UDP vs TCP

| 维度 | UDP | TCP |
| --- | --- | --- |
| 连接 | 无 | 三次握手建立 |
| 可靠性 | 无 | ACK + 重传 |
| 顺序 | 不保证 | 保证 |
| 流量控制 | 无 | 滑动窗口 |
| 拥塞控制 | 无 | CUBIC / BBR |
| 头部 | 8B | 20~60B |
| 速度 | 快 | 慢 |
| 适用 | 实时 | 可靠传输 |

## 4. UDP 适用场景

| 场景 | 原因 |
| --- | --- |
| DNS 查询 | 单包往返，简单快 |
| 视频 / 语音直播 | 实时性 > 偶尔丢包 |
| 在线游戏 | 低延迟 |
| 广播 / 组播 | 一对多 |
| 物联网上报 | 省资源、容忍丢 |
| QUIC / HTTP/3 | 在 UDP 上实现可靠 |

## 5. UDP 单播 / 广播 / 组播

```
单播 Unicast    ──>  一对一
广播 Broadcast  ──>  255.255.255.255（全网段）
组播 Multicast  ──>  224.0.0.0 ~ 239.255.255.255
```

## 6. UDP 编程示例（Python）

```python
import socket

# 服务端
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(('0.0.0.0', 9999))
while True:
    data, addr = server.recvfrom(1024)
    print(f"recv from {addr}: {data}")
    server.sendto(b'pong', addr)

# 客户端
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.sendto(b'ping', ('127.0.0.1', 9999))
data, addr = client.recvfrom(1024)
print(f"recv: {data}")
```

## 7. UDP 校验和计算

```
1. 把伪头部（源/目标 IP + 协议号 + UDP 长度）补到 UDP 前
2. 数据按 16 bit 分组相加，溢出回卷
3. 取反码
```

伪头部用于跨层校验，防止 IP 篡改后 UDP 仍"正确"。

## 8. UDP 工具

```bash
# 监听 UDP 端口
nc -ul 9999
tcpdump -i eth0 udp port 53

# 测试带宽
iperf3 -u -c 192.168.1.1 -b 100M -t 10
```

## 9. UDP 常见问题

| 问题 | 说明 |
| --- | --- |
| MTU 与分片 | UDP 包 > MTU 会在 IP 层分片，丢一片全部重传 |
| 端口不可达 | 返回 ICMP Port Unreachable，recvfrom 会抛 ConnectionRefusedError |
| 资源耗尽 | 大量无连接状态下，文件描述符易满 |

## 10. 常见面试题

1. **UDP 为什么不可靠？** 无 ACK / 重传 / 顺序保证。
2. **UDP 头部多少字节？** 8 字节。
3. **DNS 用 UDP 还是 TCP？** 常规用 UDP（53），响应 > 512B 或 zone transfer 用 TCP。
4. **UDP 适用场景？** 实时音视频、游戏、广播、DNS、QUIC。
5. **UDP 最大报文？** 65535 - 20(IP) - 8(UDP) = 65507 字节。
6. **QUIC 为什么基于 UDP？** 避开 TCP 内核修改困难，自定义可靠传输。
