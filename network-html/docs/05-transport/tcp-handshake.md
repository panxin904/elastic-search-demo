---
title: TCP 三次握手
---

# TCP 三次握手

<div class="nt-badge nt-badge-transport">传输层</div>
<div class="nt-badge nt-badge-interview">必考</div>

TCP 是面向连接的可靠协议，建立连接需要 **三次握手**（Three-Way Handshake），目的是同步双方序列号并确认收发能力。

## 1. 握手流程

```
       Client                          Server
         |                                |
         |  -------- SYN (seq=x) ---->    |  ① 客户端请求建立连接
         |                                |
         |  <--- SYN+ACK (seq=y, ack=x+1) |  ② 服务端同意
         |                                |
         |  -------- ACK (seq=x+1, ack=y+1) -->  ③ 客户端确认
         |                                |
         |  ======= ESTABLISHED ========>  |  连接建立
```

## 2. 标志位（Flags）

| Flag | 全称 | 含义 |
| --- | --- | --- |
| SYN | Synchronize | 同步序列号 |
| ACK | Acknowledgment | 确认号有效 |
| FIN | Finish | 关闭连接 |
| RST | Reset | 异常重置 |
| PSH | Push | 立即上交应用 |
| URG | Urgent | 紧急指针有效 |

## 3. 状态转换

| 阶段 | Client | Server |
| --- | --- | --- |
| ① | SYN_SENT（已发送 SYN） | LISTEN（监听） |
| ② | SYN_SENT | SYN_RCVD（收到 SYN） |
| ③ | ESTABLISHED | SYN_RCVD → ESTABLISHED |

## 4. 为什么是三次而不是两次？

| 次数 | 问题 |
| --- | --- |
| 两次 | 服务端发出 SYN+ACK 后**立即分配资源**，但客户端可能没收到 ACK 而不连 → 浪费服务端资源 |
| 三次 | 客户端最后一次 ACK 让服务端**确认客户端能收**，再分配资源，避免半开连接浪费 |

**核心目的：**
1. 双方都确认对方**收发能力正常**（4 项：自己发 / 收，对方发 / 收）
2. 同步双方初始序列号（ISN）

## 5. 半连接队列与全连接队列

```
SYN 到达 → 半连接队列（syn backlog）    ← 三次握手中
ACK 到达 → 移入全连接队列（accept queue） ← ESTABLISHED
            ↓
       应用 accept() 取走
```

| 队列 | 调优参数 |
| --- | --- |
| 半连接 | `tcp_max_syn_backlog` |
| 全连接 | `net.core.somaxconn` |
| syncookies | `tcp_syncookies`（防 SYN Flood） |

## 6. SYN Flood 攻击与防御

**攻击**：恶意客户端发大量 SYN，不回 ACK → 半连接队列打满。

**防御**：

| 措施 | 原理 |
| --- | --- |
| SYN Cookies | 不立即分配资源，序列号编码信息 |
| 增加半连接队列 | `tcp_max_syn_backlog` |
| 缩短超时 | `tcp_synack_retries` |
| 防火墙 / WAF | 丢弃异常 SYN |

## 7. 初始序列号 ISN

- 32 bit 随机数（RFC 6528 防攻击）
- 目的：防止**历史报文被新连接误接收**（TCP 序列号空间足够大）

## 8. 抓包示例（Wireshark）

```
No.   Time     Source          Dest            Protocol  Info
1     0.000    192.168.1.5     10.0.0.1        TCP       49842 → 80 [SYN] seq=0
2     0.001    10.0.0.1        192.168.1.5     TCP       80 → 49842 [SYN, ACK] seq=0 ack=1
3     0.002    192.168.1.5     10.0.0.1        TCP       49842 → 80 [ACK] seq=1 ack=1
```

## 9. TFO（TCP Fast Open）

跳过三次握手，**首次握手时携带数据**，减少 RTT。

```
1. 首次连接：正常三次握手 + 服务端发 TFO Cookie
2. 后续连接：SYN + Cookie + 数据
3. 服务端校验 Cookie 通过后直接接收数据
```

## 10. 常见面试题

1. **三次握手目的是什么？** 同步序列号 + 确认收发能力。
2. **为什么不是两次？** 防服务端单方面分配资源导致半开连接浪费。
3. **为什么不是四次？** 第二次 SYN+ACK 已合并，不需要单独 ACK。
4. **SYN Flood 怎么防？** SYN Cookies、增大 backlog、缩短超时。
5. **ISN 为什么随机？** 避免历史报文被新连接误收。
6. **握手期间丢包怎么办？** 超时重传 SYN，最多重试 `tcp_syn_retries`（默认 6）。
