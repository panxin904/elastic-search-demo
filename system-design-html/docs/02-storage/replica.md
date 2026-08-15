---
title: 主从复制与读写分离
---

# 主从复制与读写分离

> 复制是分布式的"双保险"——同一份数据存多份，一台挂了另一台顶上。

## 1. 复制模式

### 1.1 主从复制（Master-Slave / Leader-Follower）

```
写入：   Client → Master → 复制到所有 Slave
读取：   Client → Master 或 Slave

优点：
  - 简单（写入路径单一）
  - 读扩展（多个 Slave 分担读流量）

缺点：
  - Master 单点（要主主或自动切换）
  - 复制延迟（Slave 落后 Master）
```

### 1.2 主主复制（Master-Master）

```
两台都是 Master，互相复制
Client 写任一台都会被复制到另一台

优点：
  - 无单点
  - 双写能力

缺点：
  - 冲突解决复杂（双向写入可能冲突）
  - 自增 ID 等不兼容
```

### 1.3 无主复制（Leaderless）

```
写入：Client → 多个节点（写入 W 个副本算成功）
读取：Client → 多个节点（读取 R 个副本，取多数值）

代表：Cassandra / DynamoDB / Riak
优点：天然容错，无 Leader 切换
缺点：冲突解决复杂（见 quorum.md）
```

## 2. 同步 vs 异步复制

### 2.1 同步复制（Synchronous）

```
Master 写入步骤：
  1. 写入本地
  2. 等所有 Slave 确认
  3. 返回成功

优点：
  - Slave 永远是最新的
  - Master 挂了，Slave 可立即接管

缺点：
  - 延迟高（等所有 Slave）
  - 任一 Slave 慢都拖垮 Master
```

### 2.2 异步复制（Asynchronous）

```
Master 写入步骤：
  1. 写入本地
  2. 立即返回成功
  3. 异步把变更推给 Slave

优点：
  - 低延迟
  - Master 不被 Slave 拖垮

缺点：
  - Slave 可能落后（replication lag）
  - Master 挂了，未复制的变更丢失
```

### 2.3 半同步（Semi-Synchronous）

```
折中：
  - Master 写入本地
  - 至少等 1 个 Slave 确认
  - 其他 Slave 异步复制
  → 比同步快，比同步可靠
```

## 3. 复制延迟与一致性问题

### 3.1 复制延迟导致的现象

```
T1: 用户更新资料 → Master 收到
T2: Master 返回成功
T3: 用户刷新 → 读请求路由到 Slave
T4: Slave 还没收到 T1 的更新
→ 用户看到旧资料（"刚改的怎么没生效？"）

📌 这是分布式系统最常见的 UX 问题之一
```

### 3.2 解决方案

```
方案 1：强制读 Master
  写入后短期内的读都走 Master
  简单但把读压力集中在 Master

方案 2：粘性会话
  同一客户端的读固定走同一节点
  保证 read-your-writes（至少自己看到自己的写入）

方案 3：版本号 / 时间戳
  客户端记录写入的版本号
  读时要求 Slave 返回的版本 ≥ 期望版本

方案 4：读修复（Read Repair）
  读时检测到版本不一致，触发后台修复
  Cassandra 默认行为
```

## 4. 读写分离

### 4.1 架构

```
       ┌──────────────┐
       │   Master     │  ← 写入
       └──────┬───────┘
              │  异步复制
       ┌──────┴───────┐
       │              │
   ┌───▼──┐       ┌───▼──┐
   │Slave1│       │Slave2│   ← 读取
   └──────┘       └──────┘
```

### 4.2 路由策略

```
策略 1：基于角色
  - 配置读写分离代理（ProxySQL / MyCat）
  - 应用层显式区分读写（不同 DAO）

策略 2：基于延迟
  - 探测 Slave 延迟
  - 延迟过高的 Slave 临时下线

策略 3：基于权重
  - 多 Slave 按权重分配读流量
  - 性能好的 Slave 多分配
```

### 4.3 经典案例：MySQL 主从

```
配置：
  - master: 写入 + binlog
  - slave: relay log + 重放

问题：
  - 异步复制 → 延迟
  - 主从切换 → 数据丢失风险

解决：
  - 半同步（MySQL 5.7+ Semi-Sync）
  - MHA / Orchestrator 自动切换
  - GTID + 强同步复制（MySQL Group Replication）
```

## 5. 主从切换

### 5.1 为什么需要？

```
Master 故障场景：
  - 进程崩溃
  - 网络隔离
  - 磁盘损坏

需要自动把某个 Slave 提升为新 Master
```

### 5.2 切换流程

```
1. 探测故障
   - 心跳超时（通常 10-30s）
   - 多数 Slave 同意 Master 不可达

2. 选举新 Master
   - 数据最新的 Slave（基于 GTID / binlog 位点）
   - 提升为可写

3. 通知应用
   - VIP 漂移
   - DNS 切换
   - 配置中心推送

4. 其他 Slave 重新指向新 Master
```

### 5.3 数据丢失问题

```
风险场景：
  Master 写入本地成功
  还没复制给 Slave
  Master 挂了
  → Slave 提升为 Master，丢失这部分写入

📌 工程方案：
  - 半同步（至少 1 个 Slave 确认才返回）
  - 同步协议（Raft / Paxos 多数派）
  → 用一致性换可靠性
```

## 6. 多副本配置

### 6.1 副本数选择

```
副本数 = 3（业界默认）：
  - 可容忍 1 副本故障
  - 多数派 = 2
  - 性能 / 存储成本平衡

副本数 = 5：
  - 可容忍 2 副本故障
  - 多数派 = 3
  - 金融 / 强一致场景

副本数 = 7+：
  - 极端可靠性
  - 成本翻倍，延迟增加
  - 区块链 / 关键基础设施
```

### 6.2 副本分布

```
多机房部署：
  - 同机房 2 副本（性能）
  - 跨机房 1 副本（容灾）

多 AZ 部署（云）：
  - AZ1 1 副本
  - AZ2 1 副本
  - AZ3 1 副本
  → 整个 AZ 故障也不影响
```

## 7. 复制拓扑

### 7.1 一主多从

```
   Master
  /  |  \
 S1  S2  S3

简单，但 Master 是写入瓶颈
```

### 7.2 级联复制

```
   Master
     |
     S1 (中继)
   /  |  \
  S2  S3  S4

减少 Master 复制压力
但 S2-S4 延迟更大
```

### 7.3 双主 + 级联

```
   M1 ────→ S1
    ↑         |
    |         ↓
   M2 ←──── S2

复杂，能避免部分故障
但冲突解决麻烦
```

## 8. 一致性问题：读写一致性

### 8.1 最终一致性（默认）

```
写入：Master 立即返回，Slave 异步追平
读取：Slave 可能返回旧值
📌 99% 系统的默认行为
```

### 8.2 读己之写（Read-your-writes）

```
写入后短期内的读走 Master
其他读走 Slave
📌 用户体验底线
```

### 8.3 单调读（Monotonic Reads）

```
保证同一客户端读到的版本不"倒退"
→ 用户刷新不会看到"老于上次"的值
```

### 8.4 前缀读（Consistent Prefix Reads）

```
保留写入顺序
例：
  - 用户先插入主帖，再插入回复
  - 任何客户端看时，必须先看到主帖再看到回复
📌 因果一致的最弱形式
```

## 9. 一句话总结

```
📌 复制是"高可用 + 读扩展"的标配，与分片互补
📌 同步复制可靠但慢；异步复制快但有数据丢失风险
📌 半同步是工程折中：至少 1 个 Slave 确认
📌 主从切换要避免脑裂：数据最新者晋升
📌 复制延迟是分布式 UX 的头号问题：用粘性路由 / 版本号 / 读修复解决
📌 副本数 3 是默认；金融场景 5；跨机房多 AZ 分布
```

## 10. 参考资料

- MySQL High Availability (Charles Bell et al.)
- PostgreSQL Replication Documentation
- Dynamo: Amazon's Highly Available Key-value Store (SOSP 2007)
- Designing Data-Intensive Applications 第 5 章
- Raft Consensus Algorithm (Ongaro & Ousterhout, 2014)
