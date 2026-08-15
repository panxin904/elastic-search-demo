---
title: CAP 定理
---
# CAP 定理

## 1. 三选二（不可能三角）

Eric Brewer 2000 年提出，2002 年 Gilbert & Lynch 证明：

- **C**onsistency（一致性）：所有节点同时看到同一份数据
- **A**vailability（可用性）：每个请求都能收到响应（不保证最新）
- **P**artition tolerance（分区容忍）：网络分区时系统仍能继续工作

```
           C
          / \
         /   \
        /     \
       A ----- P
   网络分区必然发生（P）
   所以只能选 C 或 A
```

**实际含义**：分布式系统**必须容忍网络分区**（P），所以在 C 和 A 之间二选一。

## 2. CP vs AP 实战

### CP 系统（一致性优先）

- **HBase / ZooKeeper / etcd / Consul**
- 分区时 → 拒绝服务（牺牲 A）保证 C
- 适用：金融、配置、leader 选举

### AP 系统（可用性优先）

- **Cassandra / DynamoDB / Riak**
- 分区时 → 继续服务（牺牲 C）保证 A
- 适用：购物车、社交 feed
- 一致性通过 **read repair** / **anti-entropy** 异步修复

### CA（不存在严格意义）

传统单机关系数据库（MySQL 主从）= CA 假设无网络分区。**分布式下不可能严格 CA**。

## 3. 经典案例

| 系统 | 选 | 原因 |
|------|----|------|
| ZooKeeper | CP | leader 选举需要 quorum |
| Eureka / Nacos | AP | 服务发现，宁可读到旧数据也不能挂 |
| Cassandra | AP | 优先可用，read repair 修一致 |
| Redis Cluster | AP（默认） | 主从切换不影响服务 |
| Kafka | CP（ISR） | 强一致日志，牺牲写可用性 |

## 4. CAP 的 12 年扩展：CAP 12 年后

Eric Brewer 2017 年回顾：CAP 经常被误解。实际系统不是"非此即彼"，而是：
- 正常运行（无分区）时同时保证 C + A
- 仅在分区期间做取舍（牺牲其中一个）
- 分区期多长？影响恢复策略

## 5. PACELC

更精确的扩展：在没有分区时也要权衡（latency vs consistency）。

```
if Partition: trade off A vs C
else: trade off Latency vs Consistency
```

- **Dynamo / Cassandra**: PC/EL（低延迟，最终一致）
- **HBase / MongoDB**: PC/EC（强一致，但延迟高）
- **Spanner / CockroachDB**: PA/EC（分区时保 A，平时强一致 + 短延迟）

## 6. 实战选型指南

```java
// 问 3 个问题：
// 1. 分区发生时：业务宁可不服务，还是返回旧数据？
// 2. 平时：可以接受最终一致吗（毫秒级/秒级延迟）？
// 3. 有没有强一致的金融/合同需求？

// 选 CP：强一致、配置中心、leader 选举
// → 用 etcd / Zookeeper / Spanner

// 选 AP：用户体验、社交 feed
// → 用 DynamoDB / Cassandra / Nacos

// 折中：CP 系统在内部（写路径）+ AP 在外部（读路径）
// → 写 Spanner，读缓存用 Cassandra
```

## 7. CAP 的现实应用

| 业务 | 选 | 理由 |
|------|----|------|
| 支付 | CP | 不能超卖、不能漏单 |
| 社交 feed | AP | 慢 1 秒显示也 OK |
| 库存 | CP | 超卖 = 灾难 |
| 评论 | AP | 偶尔少评论无所谓 |
| 配置 | CP | 配置不一致 = 系统错乱 |
| 用户画像 | AP | 近似即可 |

## 🔗 下一步
- [BASE / 最终一致性](/03-ha-theory/base)
- [Raft 共识](/03-ha-theory/raft)
- [Quorum 多数派](/03-ha-theory/quorum)
- [幂等性设计](/03-ha-theory/idempotency)
