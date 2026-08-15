---
title: 三阶段提交（3PC）
---

# 三阶段提交（3PC）

> Two-Phase Commit 的改进版。引入 PreCommit 阶段，但并未从根本上解决问题。

## 1. 3PC 的动机

```
2PC 的两大问题：
  1. 同步阻塞：Participants 锁定资源等 Coordinator
  2. 协调者单点：Coordinator 挂了 Participants 不知如何

3PC 的目标：
  - 减少阻塞时间
  - 在 Coordinator 故障时 Participants 能自主决定
```

## 2. 三阶段流程

### 2.1 阶段 1：CanCommit（询问）

```
Coordinator:
  1. 发 CanCommit 给所有 Participants
  2. 不写日志，不锁资源

Participants:
  1. 检查自己能否提交（资源、状态、依赖）
  2. 返回 YES / NO
  3. 不锁资源

📌 这一阶段是"试探"，不真正执行事务
```

### 2.2 阶段 2：PreCommit（预提交）

```
如果所有 Participants 都返回 YES：

Coordinator:
  1. 写日志（preCommit）
  2. 发 PreCommit 给所有 Participants
  3. 进入"等待 ACK"

Participants:
  1. 收到 PreCommit
  2. 执行本地事务（写 undo/redo log）
  3. 锁定资源
  4. 返回 ACK

如果任一 Participant 返回 NO：
  → 直接 abort（不进 PreCommit）
```

### 2.3 阶段 3：DoCommit（执行）

```
Coordinator:
  1. 收到所有 ACK
  2. 写日志（commit）
  3. 发 DoCommit 给所有 Participants

Participants:
  1. 收到 DoCommit
  2. 真正提交本地事务
  3. 释放锁
  4. 返回 ACK

Coordinator:
  1. 收到所有 ACK
  2. 写日志（end）
```

## 3. 与 2PC 的关键差异

```
┌──────────────┬──────────────────┬──────────────────┐
│              │ 2PC              │ 3PC              │
├──────────────┼──────────────────┼──────────────────┤
│ 阶段数       │ 2                │ 3                │
│ 资源锁定时机 │ Prepare 后立即锁 │ PreCommit 后才锁 │
│ CanCommit    │ 无               │ 有               │
│ 协调者超时   │ Participants 卡住│ Participants 自主│
│ 适用网络     │ 同步/部分同步    │ 部分同步         │
│ 实现复杂度   │ 中               │ 高               │
│ 性能         │ 较低             │ 略高             │
└──────────────┴──────────────────┴──────────────────┘
```

## 4. 关键改进：超时自动提交

### 4.1 2PC 的问题

```
Participants 在 Prepare 后：
  - 锁定资源
  - 等 Coordinator 发 Commit 或 Abort
  - Coordinator 挂了 → 永远等
  → 永久阻塞
```

### 4.2 3PC 的解决

```
Participants 在 PreCommit 后（ACK 已发）：
  - 锁定资源
  - 等 Coordinator 发 DoCommit
  - 超时未收到 → **自动提交**

逻辑：
  - 既然我已经在 PreCommit 阶段，说明 Coordinator 决定提交
  - 多数派都在 PreCommit 阶段
  - 即使 Coordinator 挂了，多数派会重选
  - 新 Coordinator 会发 DoCommit
  → 安全自动提交

📌 但这个前提是"多数派都在 PreCommit 阶段"
   网络分区可能打破这个前提
```

## 5. 3PC 仍然存在的问题

### 5.1 网络分区

```
场景：
  Coordinator 在 PreCommit 阶段挂
  P1, P2 在 PreCommit（已 ACK）
  P3 在 CanCommit（未 ACK）

P1, P2 超时 → 自动提交
P3 等超时 → abort

📌 分区导致状态不一致
```

### 5.2 假设过强

```
3PC 假设：
  - 网络延迟有上界
  - 节点不会同时故障
  - 大多数节点能通信

真实场景：
  - 网络可能完全异步（无限延迟）
  - 节点可能同时挂
  → 假设过强可能不成立
```

### 5.3 实现复杂

```
多了 CanCommit 阶段：
  - 状态机更复杂
  - 日志更多
  - 故障恢复更麻烦
  - 实际工程价值不大
```

## 6. 工程上为什么不用 3PC？

```
1. 实现复杂，性价比低
2. 并不能解决所有 2PC 的问题（网络分区）
3. 假设过强，真实系统不满足
4. 工业界没有广泛实现

📌 主流的"分布式事务"解决方案是：
   - TCC（业务侵入式补偿）
   - Saga（长事务拆小）
   - 本地消息表 + MQ（异步最终一致）
   - 事务消息（RocketMQ / Kafka）

不是 2PC / 3PC
```

## 7. 3PC 的真实应用

```
学术界：
  - 教学价值（理解事务协议演进）

工业界：
  - 几乎不用
  - 一些数据库内部借鉴思想
  - 部分消息中间件参考

📌 如果有人和你说"我们用 3PC"，大概率是误解或简化说法
```

## 8. 替代方案

### 8.1 业务层：Saga

```
将长事务拆成多个短事务：
  - 每个短事务有对应的补偿操作
  - 部分失败时执行补偿
  → 见 saga.md
```

### 8.2 业务层：TCC

```
Try - Confirm - Cancel：
  - Try：预留资源
  - Confirm：真正扣减
  - Cancel：释放预留
  → 见 tcc.md
```

### 8.3 消息层：本地消息表

```
业务事务 + 消息表 + MQ：
  1. 业务 + 消息写在同一本地事务
  2. 后台 worker 投递消息
  3. 下游消费 + 处理
  → 见 local-message-table.md
```

### 8.4 消息层：事务消息

```
RocketMQ / Kafka 事务消息：
  - 半消息机制
  - 二阶段确认
  → 见 transactional-message.md
```

## 9. 历史与影响

```
3PC 的提出：
  - Gray 1978 年描述
  - Skeen 1981 年形式化

3PC 的命运：
  - 学术上有价值
  - 工程上几乎未被采用
  - 被 TCC / Saga 等业务层方案取代

📌 学习 3PC 的价值：
  - 理解分布式事务的演进
  - 知道为什么"加一阶段"并不解决问题
  - 看到"理论完美 / 工程失败"的典型例子
```

## 10. 一句话总结

```
� 3PC 是 2PC 的改进版，引入 CanCommit + PreCommit 两阶段
📌 关键改进：PreCommit 后超时可以自动提交（减少阻塞）
📌 但网络分区下仍可能不一致
📌 工业界几乎不用 3PC，被 TCC / Saga / 消息方案取代
📌 学习 3PC 的价值在于理解"为什么协议演进没有终点"
📌 现代分布式事务的正确思路：用业务补偿替代锁资源
```

## 11. 参考资料

- Transaction Recovery in Distributed Database Systems (Gray, 1978)
- Nonblocking Commit Protocols (Skeen, 1981)
- 3PC 形式化定义 (Skeen & Stonebraker, 1983)
- DDIA 第 9 章
- Seata 文档（TCC / Saga 实现参考）
