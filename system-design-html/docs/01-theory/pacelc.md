---
title: PACELC 扩展
---

# PACELC 扩展

> Daniel Abadi 2012 年提出。CAP 的现代延伸，把"正常时的取舍"也纳入框架。

## 1. 为什么需要 PACELC？

```
CAP 的盲点：
  只讨论分区（P 期间）选 A 还是 C
  → 没有说"正常时"的取舍

实际系统日常运行几乎不在分区状态
  → 真正每天做决定的，是"没有分区时，A/C/L 怎么选"
```

## 2. PACELC 公式

```
P  ：Partition（网络分区）
A  ：Availability（可用性）
C  ：Consistency（一致性）
E  ：Else（否则，即无分区）
L  ：Latency（延迟）

全称：If Partition, choose between A and C;
      Else (no partition), choose between L and C.
```

翻译：
- **分区期间**：CAP（A vs C）
- **正常时**：**L vs C**（延迟 vs 一致性）

## 3. 6 种 PACELC 类型

| 类型 | P 时 | E 时 | 含义 |
|---|---|---|---|
| **PA/EL** | 选 A | 选 L | 分区时保可用，正常时保低延迟 |
| **PA/EC** | 选 A | 选 C | 分区时保可用，正常时保一致 |
| **PC/EL** | 选 C | 选 L | 分区时保一致，正常时保低延迟 |
| **PC/EC** | 选 C | 选 C | 全程一致（但慢） |
| **PA/PC** | — | — | 逻辑矛盾（无分区时不可能同时 A 和 C） |
| **PC/AL** | — | — | 同上 |

> 实际上只有前 4 种合法组合。

## 4. 典型系统分类

### 4.1 PA/EL（最常见的 NoSQL）

```
分区时选 A：分区期间允许写、返回可能旧值
正常时选 L：默认配置下读写延迟极低，不等所有副本

代表：
  DynamoDB
  Cassandra（默认 ONE/QUORUM）
  MongoDB（默认）
  Riak
  Voldemort
```

**特征**：高吞吐、低延迟、最终一致。

### 4.2 PA/EC

```
分区时选 A
正常时选 C：写入必须等多数副本确认才返回

代表：
  Cosmos DB（强一致模式）
  PNUTS（Yahoo!）
```

**特征**：分区时灵活，正常时强一致。

### 4.3 PC/EL

```
分区时选 C：分区期间拒绝写入，等恢复
正常时选 L：单分区读写走主节点，延迟低

代表：
  HBase（依赖 ZooKeeper 协调）
  Megastore（Google Spanner 前身）
```

**特征**：分区时严格，正常时高效。

### 4.4 PC/EC（最严格）

```
分区时选 C
正常时选 C：所有读写都要过多数派

代表：
  BigTable
  HBase（强一致配置）
  Redis（同步复制 + WAIT）
  Spanner（TrueTime）
  etcd / ZooKeeper
  VoltDB
```

**特征**：全程一致，但延迟高、可用性差。

## 5. 为什么 DynamoDB 是 PA/EL？

```
DynamoDB 写入路径：
  客户端 → 协调节点 → 本地持久化 → 异步复制到其他 AZ
                  ↓
                立即返回成功

没有分区时：
  L 优先：写入路径不等待跨 AZ 同步 → 几毫秒返回

有分区时：
  A 优先：当前 AZ 仍接受写入，其他 AZ 断开期间累积变更
         → 恢复后按 vector clock 合并冲突
```

**代价**：可能读到旧值。但用户场景（购物车、社交）能接受。

## 6. 为什么 Spanner 是 PC/EC？

```
Spanner 写入路径：
  客户端 → 主副本 → Paxos 多数派写入 → TrueTime 等待 → 返回

没有分区时：
  C 优先：必须多数副本确认；Paxos 协议有 2 轮 RPC

有分区时：
  C 优先：少数派分区拒绝写入（避免脑裂）

代价：延迟高（跨数据中心 Paxos 通常 50-100ms）
收益：全球强一致 + 外部一致性（Linearizability）
```

**代价**：贵。但 Google Ads / Play 钱包愿意为强一致付钱。

## 7. PACELC 的工程意义

### 7.1 不要用 PACELC 选系统

```
常见错误：
  "我们需要强一致 → 选 PC/EC 的系统"

实际：
  - 大部分请求不需要 Linearizability
  - PC/EC 系统吞吐低、成本高
  - 应该用 PA/EL 系统 + 应用层做关键路径的一致性校验
```

### 7.2 同系统不同配置

```
Cassandra：
  consistency = ONE   →  E 时选 L（不确认副本）
  consistency = QUORUM →  E 时接近 C（等多数副本）
  consistency = ALL   →  E 时严格 C（等全部副本）

📌 业务侧按需选：
  - 写日志用 ONE（快）
  - 写账户用 QUORUM（可靠）
```

### 7.3 同业务不同读写

```
📌 工程实践：读写路径分别配

例 1：电商
  读商品详情：W=1, R=1（ONE，快）
  写订单状态：W=QUORUM, R=QUORUM（可靠）

例 2：即时通讯
  读历史消息：W=1, R=1（ONE）
  写好友列表：W=QUORUM, R=QUORUM

例 3：监控指标
  全部 ONE（指标允许偶尔丢）
```

## 8. PACELC vs CAP 的关系

```
CAP = PACELC 中 "P 时" 的一个特例
PACELC = CAP + 正常时 E/L 的取舍

CAP：分区发生 → 怎么应对？
PACELC：分区发生 → 怎么应对？
        没分区时 → 怎么应对？
```

## 9. 一句话总结

```
📌 CAP 只说"分区期间"的取舍，PACELC 补了"正常时"的取舍
📌 4 种合法类型：PA/EL、PA/EC、PC/EL、PC/EC
📌 大部分 NoSQL 是 PA/EL（高吞吐、最终一致）
� 强一致系统（Spanner/etcd）是 PC/EC（贵但可靠）
📌 工程上：按业务路径选 consistency 等级，而不是一刀切选系统
```

## 10. 参考资料

- Consistency Tradeoffs in Modern Distributed Database System Design (Daniel Abadi, 2012)
- PACELC 原论文
- Spanner: Google's Globally-Distributed Database (OSDI 2012)
- DDIA 第 9 章
