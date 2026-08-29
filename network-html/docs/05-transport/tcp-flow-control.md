---
title: TCP 流量控制
date: 2026-08-15  # date-auto-injected
---

# TCP 流量控制

<div class="nt-badge nt-badge-transport">传输层</div>
<div class="nt-badge nt-badge-interview">中频</div>

流量控制（Flow Control）让**发送方速度匹配接收方处理能力**，避免淹没接收方。TCP 通过**滑动窗口**机制实现。

## 1. 什么是流量控制

- 目的：接收方别被发送方压垮
- 手段：接收方在 ACK 中告知**可用窗口大小（rwnd）**
- 发送方根据 rwnd 调整发送节奏

## 2. 滑动窗口原理

```
发送方视角：
  [ 已确认 ][ 已发未确认 ][ 可发送 ][ 不可用 ]
   ^                         ^
   left                     right = left + rwnd

收到 ACK → left 右移，right 右移
接收方告知 rwnd 变小 → right 左移（窗口收缩）
```

## 3. 窗口字段

- TCP 头中 `Window` 字段，**16 bit**，最大 65535 字节
- 引入**窗口缩放因子**（Window Scale）后，最大可达 1GB
  - 选项仅在三次握手时协商（Shift Count）

## 4. 零窗口与窗口探测

### 4.1 零窗口

当接收方缓冲区满时，回送 `rwnd=0`，发送方停止发送。

### 4.2 窗口探测

- 发送方定期发**1 字节数据**探测（Window Probe）
- 接收方处理完后回 ACK + 新 rwnd
- 防止对端 rwnd=0 后一直不告知恢复

### 4.3 死锁风险

- ACK 丢失 → 发送方等不到更新
- 通过**持续定时器**（Persistence Timer）解决
  - 初始值 = RTO
  - 翻倍指数退避
  - 收到 rwnd 更新后重置

## 5. 糊涂窗口综合征（Silly Window Syndrome）

- 接收方腾出几字节就告知窗口，导致发送方发"小包"
- **接收方解决**：Nagle 算法 / 窗口通告至少达到 MSS / 缓冲区的 1/2 才更新
- **发送方解决**：Nagle 算法（小包合并）

## 6. 窗口扩大选项（Window Scaling）

- 选项：3 字节，1 字节 shift count
- shift = 8 → 实际窗口 = 16bit × 256 = 1MB
- 三次握手协商，必须双方支持
- 高带宽长肥网络（LFN）必须开启

## 7. 流量控制 vs 拥塞控制

| 维度 | 流量控制 | 拥塞控制 |
| --- | --- | --- |
| 目的 | 接收方不被淹没 | 网络不被淹没 |
| 控制方 | 接收方 | 发送方（推测） |
| 指标 | rwnd | cwnd |
| 问题 | 接收方慢 | 路由器拥塞 |
| 触达条件 | 接收方 buffer 满 | 丢包 / 时延增加 |

发送方实际窗口 = min(rwnd, cwnd)

## 8. Linux 窗口相关参数

```bash
# 接收 / 发送缓冲区
net.ipv4.tcp_rmem = 4096 87380 6291456
net.ipv4.tcp_wmem = 4096 65536 4194304

# 窗口缩放
net.ipv4.tcp_window_scaling = 1

# 关闭 Nagle（实时小包）
TCP_NODELAY setsockopt

# 接收低水位 / 高水位
SO_RCVLOWAT / SO_RCVTIMEO
```

## 9. 抓包示例

```
Client → Server:  [PSH, ACK] Seq=1001 Ack=2001 Win=65535
Server → Client:  [ACK]        Seq=2001 Ack=1501 Win=32768   ← 窗口收缩
```

## 10. 常见面试题

1. **流量控制作用？** 防接收方被压垮。
2. **rwnd 是什么？** 接收方可用窗口。
3. **零窗口怎么办？** 持续定时器 + 窗口探测。
4. **Nagle 解决什么问题？** 糊涂窗口综合征。
5. **Window Scale 作用？** 突破 64KB 窗口上限。
6. **实际窗口由谁决定？** min(rwnd, cwnd)。
