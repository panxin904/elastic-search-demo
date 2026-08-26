---
title: ICMP 协议
---

# ICMP 协议

<div class="nt-badge nt-badge-network">网络层</div>
<div class="nt-badge nt-badge-tools">诊断</div>

ICMP（Internet Control Message Protocol）是 IP 的伴随协议，用于在 IP 网络中传递**控制与差错消息**，是 `ping` / `traceroute` 的基础。

## 1. ICMP 作用

| 类别 | 例子 |
| --- | --- |
| 差错报告 | 目的不可达、超时、参数问题 |
| 探测工具 | Echo Request / Reply（ping） |
| 路由控制 | Redirect |
| 拥塞通知 | Source Quench（已废弃） |

## 2. ICMP 报文格式

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|     Type      |     Code      |          Checksum             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Identifier           |       Sequence Number         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                     Data (variable)                           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

| 字段 | 说明 |
| --- | --- |
| Type | 报文类型（0=Echo Reply，3=Dest Unreachable，8=Echo Request，11=Time Exceeded） |
| Code | 子类型，区分不同原因 |
| Checksum | 整个 ICMP 报文校验 |
| Identifier | 通常等于进程 PID |
| Sequence | 序号，用于配对 Request / Reply |

## 3. 常见 ICMP 类型

| Type | Code | 含义 | 触发场景 |
| --- | --- | --- | --- |
| 0 | 0 | Echo Reply | ping 应答 |
| 3 | 0 | Network Unreachable | 路由不可达 |
| 3 | 1 | Host Unreachable | 主机不在线 |
| 3 | 2 | Protocol Unreachable | 上层协议未开启 |
| 3 | 3 | Port Unreachable | 端口未监听 |
| 3 | 4 | Fragmentation Needed | DF 置位 + 需分片 |
| 4 | 0 | Source Quench | 拥塞（已废弃） |
| 5 | 0~3 | Redirect | 路由优化 |
| 8 | 0 | Echo Request | ping 请求 |
| 11 | 0 | TTL Exceeded | traceroute |
| 11 | 1 | Fragment Reassembly Time | 分片重组超时 |

## 4. ping 原理

```
源 ──ICMP Echo Request(seq=1)──> 目标
源 <──ICMP Echo Reply(seq=1)──── 目标

往返时延 = RTT (Round-Trip Time)
```

```bash
ping 8.8.8.8                  # 持续 ping
ping -c 4 baidu.com           # 发 4 个包
ping -s 1500 -M do 8.8.8.8    # 测 MTU（不分片）
ping -t 64 baidu.com          # 设置 TTL
```

## 5. traceroute 原理

利用 **IP 头 TTL 字段** + ICMP Time Exceeded：

```
TTL=1 ──> 第一跳路由器回 ICMP 11
TTL=2 ──> 第二跳路由器回 ICMP 11
TTL=3 ──> 第三跳路由器回 ICMP 11
...
TTL=N ──> 目标主机回 ICMP 0 (Echo Reply) 或 ICMP 3
```

```bash
traceroute baidu.com
traceroute -m 30 baidu.com       # 最大跳数
traceroute -I baidu.com          # 用 ICMP（部分服务器屏蔽 UDP）
```

## 6. Path MTU Discovery

发现从源到目标的最小 MTU，避免分片。

```
1. 源发送 DF=1 的 IP 包（1500 字节）
2. 某跳 MTU 较小 → 回 ICMP Type3 Code4 (Fragmentation Needed)
3. 源减小包长，重试
4. 直到不再收到该消息 → 找到路径 MTU
```

## 7. ICMP 报文种类总览

```
Type 0  ── Echo Reply
Type 3  ── Destination Unreachable
Type 4  ── Source Quench (deprecated)
Type 5  ── Redirect
Type 8  ── Echo Request
Type 11 ── Time Exceeded
Type 12 ── Parameter Problem
Type 13 ── Timestamp
Type 14 ── Timestamp Reply
Type 15 ── Information Request (deprecated)
Type 16 ── Information Reply (deprecated)
```

## 8. 实战命令

```bash
# 抓 ICMP 包
tcpdump -i eth0 icmp

# Windows
tracert baidu.com
pathping baidu.com

# Linux MTR（结合 ping + traceroute）
mtr -r -c 10 baidu.com
```

## 9. 安全与限速

- ICMP 是攻击面：Ping of Death、Smurf、ICMP Flood
- 网络中常限制 ICMP 速率或禁用部分类型
- 路由器上可用 ACL 过滤

## 10. 常见面试题

1. **ping 用的是 TCP 还是 UDP？** ICMP（类型 8/0）。
2. **traceroute 为什么用 UDP？** 早期路由器对 ICMP 限速；现代 traceroute -I 也用 ICMP。
3. **TTL 作用？** 防环路，限制跳数。初始 64/128。
4. **端口不可达是 ICMP 哪条？** Type 3 Code 3。
5. **Path MTU 怎么发现？** 通过 ICMP Type 3 Code 4 反馈。
6. **ICMP 报文封装在 IP 包中，协议号？** 1。


<!-- auto-enrich:do-not-edit -->

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
