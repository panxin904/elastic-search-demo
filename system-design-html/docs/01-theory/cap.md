---
title: CAP 定理
---

# CAP 定理


![CAP 定理 — 分布式系统三选二](/cap-theorem.svg)

> Eric Brewer 2000 年提出，2002 年 Gilbert & Lynch 给出形式化证明。

## 1. 一句话定义

> **在异步网络模型下，一个分布式系统不可能同时满足以下三项中的超过两项**：
> - **C**onsistency（一致性）：所有节点看到同一份数据
> - **A**vailability（可用性）：每个请求都能收到非错误响应
> - **P**artition tolerance（分区容错）：节点之间的网络断开时系统仍能继续工作

## 2. 三选二的真相

```
常见误解：可以三选二（CA / AP / CP）
真实情况：网络分区必然会发生 → P 是必选项
         → 实际只有 CP 和 AP 两种选择
         → 所谓"CA"系统（如单机 RDBMS）放弃了 P，不是分布式系统
```

## 3. 形式化定义

### 3.1 Consistency（这里指 Linearizability）

> 任何一次读都能读到某一次写的结果，且**与真实时间顺序一致**。

与"最终一致"不同：CAP 里的 C 是**最强的一致**——Linearizability。

### 3.2 Availability

> 系统中每个非故障节点收到的请求，都必须返回**非错误**响应。

注意：可以不返回最新数据，但**必须返回**（不抛 5xx）。

### 3.3 Partition Tolerance

> 节点之间的网络消息可以丢失、延迟、重复，**但节点本身必须继续运行**。

## 4. CAP 证明（直觉版）

```
假设两节点 N1、N2，网络断开（分区）：
   N1 ◄────────► N2  ✗  （网线拔了）

N1 收到写请求 W(x=1)，写入本地，N2 不知道。
N2 收到读请求 R(x=?)，返回什么？
  - 返回 0：违反一致性（读到旧值）
  - 等待分区恢复：违反可用性（要等网线插回去）
  - 返回 1：违反一致性（N2 没收到 W）

唯一选择：在 C 和 A 之间选一个。
```

## 5. CP vs AP 选型指南

### 5.1 CP 系统（一致性优先）

**行为**：分区期间拒绝写入或返回错误。

| 系统 | 用途 |
|---|---|
| **etcd / ZooKeeper** | 配置中心 / 分布式锁 / 服务发现 |
| **Consul** | 服务发现 + 健康检查 |
| **HBase** | 强一致列存 |
| **Redis Cluster（部分模式）** | WAIT 命令强制一致 |

**适用场景**：
- 金融账务（资金不能少）
- 分布式锁（锁不能两个客户端同时拿）
- 配置中心（配置必须全集群一致）

### 5.2 AP 系统（可用性优先）

**行为**：分区期间允许写入，恢复后解决冲突。

| 系统 | 冲突解决 |
|---|---|
| **Cassandra** | Last-Write-Wins（按时间戳） |
| **DynamoDB** | Vector Clock + 应用层合并 |
| **CouchDB** | MVCC + 应用层冲突解决 |
| **DNS** | TTL 过期后重新查询 |

**适用场景**：
- 社交媒体（点赞、评论可丢失 / 重复）
- 购物车（离线可写，恢复后合并）
- CDN / 缓存（数据过期无所谓）

## 6. 常见误区

### 6.1 CAP ≠ 静态三选一

> **CAP 是分区发生时的动态选择**，不是系统设计初期的静态决策。

系统**正常时**可以同时满足 CA；**分区期间**才被迫选 CP 或 AP。

### 6.2 CAP 里的 C ≠ ACID 里的 C

| CAP | ACID |
|---|---|
| Linearizability（读最新写） | 不违反数据库约束（如外键、唯一索引） |

ACID 的 C 强调"事务前后数据库处于一致状态"，CAP 的 C 强调"读到最新值"。两者**正交**。

### 6.3 不是非黑即白

实际系统通常有**可调节的一致性**：

```
Cassandra：
  consistency = ONE    →  AP 行为（快，可能读到旧值）
  consistency = QUORUM → 折中
  consistency = ALL    →  CP 行为（慢，但强一致）

📌 业务侧可以"按需"选择：
  - 读用户资料用 ONE（快）
  - 读支付结果用 QUORUM（可靠）
```

## 7. CAP 的现代扩展：PACELC

CAP 只讨论分区期间；PACELC 补了**正常时**的取舍：

```
分区（Partition）期间：在 A 和 C 之间选（CAP）
否则（Else）正常时：在 L（Latency）和 C 之间选

→ 如果没有分区，你愿意为了强一致而付出多少延迟？
```

### 7.1 PACELC 分类

| 系统 | P-A | P-C | E-L | E-C | 类型 |
|---|---|---|---|---|---|
| **DynamoDB** | ✓ | | ✓ | | PA/EL |
| **Cassandra** | ✓ | | ✓ | | PA/EL |
| **MongoDB (默认)** | ✓ | | ✓ | | PA/EL |
| **BigTable / HBase** | | ✓ | | ✓ | PC/EC |
| **MongoDB (WiredTiger)** | | ✓ | | ✓ | PC/EC |
| **VoltDB** | | ✓ | | ✓ | PC/EC |
| **Redis (单实例)** | | ✓ | | ✓ | PC/EC |

## 8. 工程实践

### 8.1 配置中心为什么是 CP？

```
配置中心场景：
  - N 个服务节点都要读到同一个配置
  - 配置错误可能引发雪崩
  - 不能让一部分节点读到 v1，另一部分读到 v2

→ 选 etcd / ZooKeeper（CP）
  - 即使分区也只允许一个分区提供读（另一个返回错误）
  - 拒绝写 vs 读旧配置，前者损失小
```

### 8.2 分布式锁为什么是 CP？

```
分布式锁场景：
  - 锁必须互斥
  - 如果两个客户端同时拿锁，后果严重
  - 必须保证"任何时刻只有一个持有者"

→ 用 etcd / ZooKeeper 的临时节点
  - 不能用 Redis（默认异步复制，可能两个客户端都 SETNX 成功）
  - 如果用 Redis 必须加 Redlock（仍是 AP）
```

### 8.3 购物车为什么是 AP？

```
购物车场景：
  - 用户离线时也要能加入购物车（不能拒绝写入）
  - 最终一致性即可（合并购物车）
  - 不能因为"暂时无法连到主节点"就丢数据

→ 用 DynamoDB / Cassandra
  - 本地写，本地读，异步同步
  - 冲突合并（按时间戳 / 业务规则）
```

## 9. 一句话总结

```
📌 CAP 不是"放弃一个"，而是"分区期间被迫二选一"
📌 系统正常时 CA 都可满足；只有分区时才有真正的取舍
📌 工程上 CAP 决定的是"分区期间系统的反应"
   - CP：拒绝写，等恢复
   - AP：继续写，恢复后合并冲突
📌 进阶看 PACELC：把"正常时的延迟 vs 一致性"也纳入取舍
```

## 10. 参考资料

- Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services (Gilbert & Lynch, 2002)
- CAP Twelve Years Later: How the "Rules" Have Changed (Brewer, 2012)
- Consistency Tradeoffs in Modern Distributed Database System Design (Daniel Abadi, 2012) —— PACELC
- DDIA 第 9 章

<!-- svg-injected:do-not-edit -->

![cap vs base](/cap-vs-base.svg)
