---
title: TCP 拥塞控制
---

# TCP 拥塞控制

<div class="nt-badge nt-badge-transport">传输层</div>
<div class="nt-badge nt-badge-interview">高频</div>

拥塞控制（Congestion Control）让发送方**探测**网络承载能力，避免注入过多数据导致路由器丢包与瘫痪。

## 1. 拥塞与流量控制区别

| 维度 | 拥塞控制 | 流量控制 |
| --- | --- | --- |
| 目标 | 防网络过载 | 防接收方过载 |
| 触发 | 路由器/链路 | 接收方 buffer |
| 控制方 | 发送方 | 接收方告知 |
| 信号 | 丢包 / RTT 增长 | rwnd=0 |

## 2. 四个核心状态机

| 状态 | 行为 |
| --- | --- |
| 慢启动（Slow Start） | cwnd 指数增长 |
| 拥塞避免（Congestion Avoidance） | cwnd 线性增长 |
| 快速重传（Fast Retransmit） | 3 dup ACK 立即重传 |
| 快速恢复（Fast Recovery） | cwnd 减半而非归零 |

## 3. 慢启动

- 初始 cwnd = 1 ~ 10 MSS（RFC 6928 推荐 10）
- 每收到一个 ACK，cwnd += 1 MSS
- 实际效果：**每 RTT 翻倍**（指数增长）
- 触发拥塞时 cwnd 阈值 ssthresh 调整

## 4. 拥塞避免

- 进入条件：cwnd ≥ ssthresh
- 每 RTT cwnd += 1 MSS
- 实际：**每 ACK 增加 1/cwnd**

## 5. 拥塞发生处理

### 5.1 经典算法（TCP Tahoe）

```
丢包事件:
  ssthresh = cwnd / 2
  cwnd = 1
  → 重新慢启动
```

### 5.2 现代算法（TCP Reno / NewReno）

```
3 个重复 ACK（轻度拥塞）:
  ssthresh = cwnd / 2
  cwnd = ssthresh
  → 快速恢复

超时（严重拥塞）:
  ssthresh = cwnd / 2
  cwnd = 1
  → 慢启动
```

## 6. 算法演进

| 算法 | 关键改进 |
| --- | --- |
| Tahoe | 慢启动 + 拥塞避免 + 拥塞时 cwnd 归 1 |
| Reno | 快速恢复（3 dup ACK 减半 cwnd） |
| NewReno | 改进多包丢失处理 |
| BIC | 二分查找最优窗口 |
| CUBIC | 默认 Linux 算法，用三次函数增长 |
| BBR（Bottleneck BW + RTT） | 主动测量瓶颈带宽和 RTT |

## 7. CUBIC 算法

- 替代 BIC，成为 Linux 默认
- 增长函数：

```
W(t) = C × (t - K)³ + W_max
其中 K = ∛(W_max × β / C)
```

- 优点：与 RTT 无关，公平性好，长肥网络高效

## 8. BBR 算法

- 不基于丢包，基于**带宽 × RTT** 测量
- 估计 `max_bw`（瓶颈带宽）和 `min_rtt`
- 工作状态：
  - Startup（指数探测）
  - Drain（排空队列）
  - ProbeBW（周期性探测）
  - ProbeRTT（保底测 RTT）

```
inflight = max_bw × min_rtt   （BDP，带宽时延积）
```

| 优势 | 不足 |
| --- | --- |
| 低延迟，高吞吐 | 与 CUBIC 抢带宽 |
| 不依赖丢包信号 | 公平性争议 |
| 抗随机丢包 | 部署需两端支持 |

## 9. 缓冲区膨胀（Bufferbloat）

- 路由器 / 交换机 buffer 过大 → 拥塞时延剧增
- 表现为 ping 时延飙高但带宽仍满
- 解决：
  - RED / CoDel 主动队列管理
  - 缩小 buffer
  - 启用 BBR / fq_codel

## 10. Linux 调优

```bash
# 查看当前拥塞算法
sysctl net.ipv4.tcp_congestion_control
# 或 cat /proc/sys/net/ipv4/tcp_congestion_control

# 切换
sysctl -w net.ipv4.tcp_congestion_control=bbr

# 队列调度
tc qdisc add dev eth0 root fq_codel

# 初始 cwnd
ip route change default via 1.1.1.1 initcwnd 10
```

## 11. 拥塞控制 vs 应用层

| 手段 | 层级 |
| --- | --- |
| TCP Reno/CUBIC/BBR | 内核 |
| QUIC BBRv2 | 用户态 |
| 应用层限流（令牌桶） | 业务层 |
| 多连接 / 多路复用 | 应用层 |

## 12. 常见面试题

1. **慢启动 cwnd 怎么增长？** 每 RTT 翻倍。
2. **拥塞避免 cwnd 怎么增长？** 每 RTT +1 MSS。
3. **3 dup ACK 如何处理？** 减半 cwnd + 快速恢复。
4. **CUBIC 与 BBR 区别？** CUBIC 基于丢包，BBR 基于带宽时延。
5. **Bufferbloat 怎么解？** AQM、fq_codel、BBR。
6. **为什么 cwnd 太大会丢包？** 超出瓶颈带宽，路由 buffer 满，丢包。
