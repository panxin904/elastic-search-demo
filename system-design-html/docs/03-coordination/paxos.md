---
title: Paxos 共识算法
---

# Paxos 共识算法

> Lamport 1998 年提出。最经典的分布式共识算法，但因难懂闻名（"Paxos is beautiful but hard to understand"）。

## 1. 共识问题的形式化

```
N 个节点，每个节点可以提议一个值
通过消息传递，最终所有节点**决定**同一个值

要求：
  - Safety：决定的值是某个节点的提议值
  - Agreement：所有节点决定同一个值
  - Liveness：最终一定做出决定（FLP 不可能，这里假设部分同步）
```

## 2. Paxos 的角色

```
Proposer：发起提议
Acceptor：投票
Learner ：学习已决定的值

一个节点可以同时扮演多个角色
📌 实际实现中，节点 = Proposer + Acceptor + Learner
```

## 3. Basic Paxos 流程

### 3.1 两个阶段

```
Phase 1：Prepare（准备）
  - Proposer 选择提案编号 N
  - 向多数派 Acceptors 发 Prepare(N)
  - Acceptors 收到后：
    - 如果 N > 已见过的任何编号 → 承诺不再接受 < N 的提案
    - 返回已接受的最高编号提案（如果有）

Phase 2：Accept（接受）
  - 如果 Prepare 收到多数派响应
  - Proposer 发 Accept(N, value)
  - value 的选择：
    - 如果响应中有已接受提案 → 用其中最高编号的值
    - 否则 → 用自己的值
  - Acceptors 收到 Accept(N, value)：
    - 如果还没承诺过 < N 的提案 → 接受
    - 否则拒绝

决议达成：
  - 某个 value 被多数派 Acceptors 接受
  - 通知 Learners 学习
```

### 3.2 直觉

```
类比：会议室投票

Prepare 阶段：
  - "我要提议一个议题，谁支持我？"
  - "我承诺不投支持 < N 的其他提议"
  - "如果你们之前投过类似议题，告诉我"

Accept 阶段：
  - "我提议：value = X"
  - 已承诺的 Acceptors 必须接受
  - 多数派接受 → 决议达成

关键设计：
  - 编号 N 单调递增（全局唯一）
  - Prepare 拿到多数承诺 → 自己的提议不会被推翻
  - Acceptors 返回已有提案 → Proposer 必须沿用（避免提案被覆盖）
```

## 4. 提案编号的选择

```
要求：全局唯一、严格递增

简单实现：
  - 节点数 N
  - 节点 i 的编号 = i + N * round
  - round 从 0 开始，每次发起提议 +1

实际实现：
  - 高位 = 时间戳
  - 低位 = 节点 ID
  - 保证单调 + 全局唯一
```

## 5. 活锁问题（Liveness）

### 5.1 什么是活锁？

```
两个 Proposer 互相抢提案编号：
  P1: Prepare(1)
  P2: Prepare(2)
  P1: Prepare(3) （因为 P1 的 Accept 被拒绝）
  P2: Prepare(4)
  → 永远达不成共识
```

### 5.2 解决：随机退让

```
Proposer 发起 Prepare 后：
  - 超时未达成 → 随机等待 + 重试
  - 随机等待时间错开 → 降低冲突概率
  - 不能完全避免，但工程上足够
```

## 6. Multi-Paxos

### 6.1 为什么要扩展 Basic Paxos？

```
Basic Paxos 每条记录都要跑两轮 RPC
  - 性能差
  - 一个值要一次共识太贵

优化：选一个稳定的 Leader
  - 后续提案跳过 Prepare
  - 只跑 Accept 阶段
  - Leader 失效时重新选
```

### 6.2 Multi-Paxos 流程

```
1. 第一条记录：跑完整 Basic Paxos（Prepare + Accept）
   → 同时选出稳定的 Proposer（Leader）

2. 后续记录：
   - Leader 直接发 Accept(N, value)
   - 不需要 Prepare
   - 性能提升 1 倍

3. Leader 挂了：
   - 其他节点重新跑 Prepare
   - 选出新 Leader
```

### 6.3 实例：日志复制

```
每条日志 = 一次 Paxos 实例

Multi-Paxos 把日志当作无限流：
  log[0], log[1], log[2], ...

每个 slot 跑一次共识：
  - log[i] 的值 = 第 i 个共识决定的值
  - 顺序天然保证（日志有序）
```

## 7. Paxos vs Raft

```
┌──────────────┬──────────────────┬─────────────────┐
│              │ Paxos            │ Raft            │
├──────────────┼──────────────────┼─────────────────┤
│ 提出年份     │ 1998             │ 2014            │
│ 易懂度       │ 难               │ 易              │
│ Leader       │ 不强求           │ 必有             │
│ 日志顺序     │ 灵活             │ 严格             │
│ 工程实现     │ 多种变体         │ 标准化           │
│ 性能         │ 高               │ 高              │
│ 代表系统     │ Chubby, Spanner  │ etcd, Consul    │
└──────────────┴──────────────────┴─────────────────┘

📌 工程选型：
  - 需要深入定制 → Paxos（更灵活）
  - 标准分布式协调 → Raft（更简单）
```

## 8. Paxos 变体

### 8.1 Cheap Paxos

```
假设节点不会同时故障：
  - 只需 N + F - 1 个 Acceptors
  - F = 容忍故障数
  - 例：容忍 1 故障，只需 2 节点（不是 3）
```

### 8.2 Fast Paxos

```
减少一轮 RPC：
  - 客户端直接发 Accept 到多数派
  - 冲突时退化到 Classic Paxos
  - 性能更好，但实现复杂
```

### 8.3 EPaxos（Egalitarian Paxos）

```
无 Leader：
  - 任何节点都可以发提案
  - 用 dependency graph 处理并发
  - 延迟更低（地理分布式场景）
```

### 8.4 Mencius

```
轮值 Leader：
  - 每个节点轮流当 Leader
  - 减少单点瓶颈
  - 适合地理分布式
```

## 9. 工程陷阱

### 9.1 实现 Paxos 的真实难度

```
Lamport 原文（"The Part-Time Parliament"）：
  - 用希腊小岛议会做类比
  - 很多人读不懂
  - Lamport 自己也写了简化版

Google Chubby 工程师：
  "我们花了 1+ 年才确信 Chubby 的 Paxos 实现是对的"
  - 真正的 Paxos 比论文难
  - 边界情况多（网络分区、节点重启、磁盘故障）
```

### 9.2 推荐的简化路径

```
学习顺序：
  1. Raft（更易懂，建立直觉）
  2. Basic Paxos（理解核心思想）
  3. Multi-Paxos（理解优化）
  4. 看 Chubby / Spanner 实现（理解工程化）

📌 不要直接读原论文开始学 Paxos
   90% 的人会被劝退
```

## 10. 一句话总结

```
📌 Paxos 是分布式共识的"祖宗"，但因难懂被 Raft 取代主流
📌 Basic Paxos：Prepare + Accept 两阶段，多数派决定
📌 Multi-Paxos：稳定 Leader 优化，跳过 Prepare，性能翻倍
📌 活锁问题：随机退让降低冲突
📌 工程实现远比论文难，建议先学 Raft 再看 Paxos
📌 Chubby / Spanner / Megastore 都是 Paxos 系实现
```

## 11. 参考资料

- The Part-Time Parliament (Lamport, 1998) —— 原论文
- Paxos Made Simple (Lamport, 2001) —— 简化版
- Paxos Made Live (Chandra et al., 2007) —— Chubby 工程实践
- Spanner: Google's Globally-Distributed Database (OSDI 2012)
- In Search of an Understandable Consensus Algorithm (Ongaro & Ousterhout, 2014) —— Raft
- DDIA 第 9 章


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

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
