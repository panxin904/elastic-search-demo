---
title: 一致性模型
date: 2026-08-15  # date-auto-injected
---

# 一致性模型

> 从最强到最弱的一致性等级，以及它们之间的工程取舍。

## 1. 一致性的本质

```
分布式系统的核心问题：
  多个节点各自有一份数据副本
  → 一个节点写入后，其他节点什么时候能看到？

答案：取决于一致性模型的强弱
  最强：写入瞬间所有节点可见
  最弱：写入可能要很久才同步到所有节点，甚至可能不一致
```

## 2. 一致性级别谱

```
强 ──────────────────────────────────────────── 弱

Strong / Linearizability
   │
   ↓
Sequential Consistency
   │
   ↓
Causal Consistency
   │
   ↓
Read-your-writes
   │
   ↓
Monotonic Reads
   │
   ↓
Eventual Consistency
```

## 3. 强一致：Linearizability

### 3.1 定义

> 任何一次读都能读到某一次写的结果，且**与真实时间顺序一致**。

也称为 **Linearizability** 或 **Strong Consistency**。

### 3.2 直觉

```
客户端 A 写 x=1（时刻 T1）
客户端 B 读 x   （时刻 T2 > T1）
→ B 必须读到 1
```

### 3.3 实现代价

- 写入必须等所有副本确认（或多数派）
- 通常引入同步协议（Raft / Paxos）
- 延迟高，吞吐受限

### 3.4 典型系统

- **etcd / ZooKeeper**（基于 Raft / ZAB）
- **Spanner**（基于 Paxos + TrueTime）
- **HBase**（强一致配置）
- **VoltDB**

## 4. 顺序一致：Sequential Consistency

### 4.1 定义

> 所有操作有一个**全局一致的执行顺序**，且每个客户端的操作顺序在该顺序中保持。

比 Linearizability 弱：允许操作重排，只要重排不违反每个客户端的本地顺序。

### 4.2 与 Linearizability 的区别

```
场景：两个客户端并发

A: write(x, 1)
B: write(y, 2)
C: read(x) → 0
D: read(y) → 2

Linearizability 要求：
  - 如果 C 读到 0，必须 D 也读到 0（A 的写还没传播）
  - 如果 D 读到 2，必须 C 也读到 2（B 的写先传播）
  → C 和 D 必须同时看到同一个版本

Sequential Consistency 允许：
  - C 读到 x=0，D 读到 y=2（不一致）
  - 但要求：存在一个全局顺序（先 A 后 B）
  - C 在该顺序之前看 x；D 在该顺序之后看 y
  → "不一致但有顺序"即可
```

### 4.3 典型系统

- **多数分布式数据库的默认级别**

## 5. 因果一致：Causal Consistency

### 5.1 定义

> 如果操作 A 因果上先于 B（causally precedes），所有节点必须先看到 A 再看到 B。

```
因果关系：
  - 写后读（read-after-write）：同客户端读自己写的值
  - 写后写（write-after-write）：同客户端按顺序写
  - 读后写（write-after-read）：基于读到的内容再写

非因果：
  - 两个客户端的并发写（无依赖关系）
```

### 5.2 直觉

```
Alice 发帖（操作 A）
Bob 评论 Alice 的帖子（操作 B，A 因果先于 B）
Carol 看帖子：必须先看到 A 再看到 B

但：
Alice 发帖 1（操作 X）
Alice 发帖 2（操作 Y，与 X 并发）
Carol 看：X 在前或 Y 在前都可以
```

### 5.3 典型系统

- **Cassandra**（可选配置）
- **COPS（因果+）**
- **MongoDB**（部分支持）

### 5.4 工程意义

```
📌 因果一致是"性价比最高的一致性"
   - 比 Linearizable 弱（允许并发操作无序）
   - 比 Eventual 强（保证因果链不被违反）
   - 适合社交、协作类应用
```

## 6. Read-your-writes Consistency

### 6.1 定义

> 客户端写入后，**自己**的读必须能读到刚才的写入。

最弱的一致性保证之一，但用户体感重要。

### 6.2 为什么需要？

```
用户场景：
  1. 用户提交表单
  2. 用户刷新页面
  3. 系统显示"提交成功"

如果 read-your-writes 不保证：
  → 用户可能看到旧值（"未提交"）
  → 用户困惑、重复提交

📌 这是 UX 底线：用户必须能看到自己的写入
```

### 6.3 实现方式

- 写入后，**粘性路由**到主节点 / Leader
- 写入时携带 token，读取时携带同一 token
- 客户端本地缓存写入，读取时合并

## 7. Monotonic Reads

### 7.1 定义

> 客户端一次读到的值，下次读到不能更旧。

```
场景：
  - 用户读文章，版本 v5
  - 用户刷新，版本 v3（更旧）
  → 违反 Monotonic Reads，用户体验怪异

📌 比 Read-your-writes 更弱（不要求自己写的立刻可见）
   但要求"不会读越来越旧"
```

## 8. Eventual Consistency

### 8.1 定义

> 如果没有新写入，所有副本最终会收敛到同一值。

最弱的一致性模型，但**最常用**。

### 8.2 工程保证

- 不保证时间窗口
- 通常是几秒到几分钟
- 不保证读到的版本（可能很旧）

### 8.3 典型系统

- **DNS**
- **Cassandra**（默认）
- **DynamoDB**（默认）
- **CouchDB**

### 8.4 适用场景

- 社交媒体（点赞数误差 ±1 没问题）
- CDN 缓存（过期几秒无所谓）
- 购物车（离线写、合并即可）

## 9. 内存序模型：x86 vs ARM

```
📌 一致性模型不仅是分布式问题，单机多核也有

x86 (TSO)：
  - 强内存序：写立即可见
  - 性能：中等

ARM (Relaxed)：
  - 弱内存序：写可能延迟可见
  - 性能：更高（移动端首选）

工程影响：
  - Java JMM 抽象掉硬件差异（volatile / synchronized）
  - C++ std::memory_order 提供精细控制
```

## 10. 工程实践：怎么选？

### 10.1 决策树

```
Q1: 是否涉及资金 / 库存扣减？
  Yes → Linearizability（Spanner / etcd）
  No  → 继续

Q2: 是否涉及协作（多用户互看对方操作）？
  Yes → Causal Consistency（COPS / 部分 Cassandra）
  No  → 继续

Q3: 用户是否需要看到自己刚写的？
  Yes → Read-your-writes（粘性路由）
  No  → 继续

Q4: 是否能容忍偶尔读到旧值？
  Yes → Eventual Consistency
  No  → 上一步：Read-your-writes
```

### 10.2 经典案例

| 业务 | 一致性模型 | 实现 |
|---|---|---|
| 银行转账 | Linearizability | Spanner / etcd |
| 朋友圈点赞 | Eventual | Cassandra |
| 评论回复 | Causal | COPS |
| 用户提交表单 | Read-your-writes | 粘性路由 |
| Git 协作编辑 | Causal | 自定义 CRDT |

## 11. 一句话总结

```
📌 一致性不是 0/1 二元，而是强度谱
📌 Linearizability 最强但最贵；Eventual 最弱但最便宜
📌 业务上 80% 场景用 Eventual / Read-your-writes 就够
📌 关键路径（资金、库存、锁）才需要 Linearizability
📌 Causal Consistency 是"性价比之王"（强于 Eventual，弱于 Linearizable）
```

## 12. 参考资料

- Linearizability: A Correctness Condition for Concurrent Objects (Herlihy & Wing, 1990)
- Time, Clocks, and the Ordering of Events (Lamport, 1978)
- Causality Is Required (and Desired) (Lloyd et al., 2020)
- DDIA 第 5、9 章
- JSR-133 (Java Memory Model)
