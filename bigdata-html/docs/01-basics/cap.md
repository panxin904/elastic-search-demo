---
title: 大数据 CAP 选型
---
# 大数据场景的 CAP 选型

## 1. CAP 定理回顾

```
C - Consistency（一致性）
A - Availability（可用性）
P - Partition tolerance（分区容忍）

分布式系统必须容忍 P → C 和 A 二选一
```

## 2. 大数据场景的 CAP 选型

### 2.1 CP 系统（强一致）

```
HDFS NameNode（Active + Standby）
HBase（强一致读写）
Kafka（ISR 副本强一致）
ZooKeeper（ZAB 协议）
etcd（raft 协议）
```

**适用**：金融、配置、leader 选举
**代价**：分区时部分节点不可写

### 2.2 AP 系统（高可用）

```
Cassandra（最终一致）
DynamoDB（最终一致）
S3（最终一致）
Cassandra / Riak
```

**适用**：电商购物车、社交 feed
**代价**：可能读到旧数据

### 2.3 现代数据栈的 CAP 选型

| 系统 | 一致性 | 选型 |
|------|--------|------|
| HDFS | CP | 强一致（namenode quorum） |
| HBase | CP | 强一致 |
| Kafka | CP（ISR 可选 AP） | 强一致 |
| Cassandra | AP | 最终一致 |
| S3 | AP | 最终一致 |
| Hive / Spark | 弱 | 批处理一致 |
| Flink | 配置选择 | exactly-once |
| Iceberg / Hudi | 快照隔离 | 强一致（ACID） |

## 3. 大数据场景的妥协

### 3.1 强一致 + 高可用 不可能

分布式系统不能同时满足：
- 强一致（如转账）
- 高可用（不挂）
- 网络分区（必然）

→ 选 CP（金融）或 AP（互联网）

### 3.2 实时与一致

实时 ≠ 强一致
- 实时：延迟低（毫秒-秒）
- 一致：所有节点看同一份数据

→ Flink 内部用 exactly-once（通过 checkpoint + 两阶段提交）
→ Kafka 事务（0.11+）

## 4. 大数据系统的 CAP 妥协实例

### 4.1 HDFS

```
NameNode（主）+ Standby NameNode
  → 强一致（CAP 中 CP）
  → 故障时切主（几十秒）
  → 牺牲可用性保一致性
```

### 4.2 Kafka

```
Leader + Followers（ISR）
  → 默认：ack=all 一致
  → ack=1：丢消息
  → 强一致（Leader 写 + 副本同步）
```

### 4.3 Cassandra

```
Masterless + Gossip
  → 写可用（任意节点）
  → 读可能旧（最终一致）
  → 写读 eventual consistency
```

## 5. 大数据系统的 HA 设计

### 5.1 主备（Active-Passive）

```
Active 写 → 同步 → Standby
 故障 → 切换 Standby
```

代表：HDFS NameNode HA / Kafka MirrorMaker / MySQL MHA

### 5.2 多主（Multi-Master）

```
各节点都可写
  → 数据冲突（last-write-wins）
  → LWW / CRDT / Vector Clock
```

代表：Cassandra / Riak

### 5.3 Quorum（多数派）

```
W + R > N
  写：W 个节点确认
  读：R 个节点响应
  → 保证至少读到一个最新值
```

代表：Kafka ISR / etcd Raft / ZooKeeper ZAB

## 6. 大数据场景的最终一致性

```
适用：社交 / 购物车 / 计数 / 缓存
  → 允许短暂不一致
  → 异步修复
  → 自动收敛

实现：
  - 读时修复（Read Repair）
  - 后台修复（Anti-entropy）
  - 版本号 / Vector Clock
```

## 7. 实战选型

| 业务 | CAP 选 | 理由 |
|------|--------|------|
| 金融交易 | CP | 不能超卖 / 漏单 |
| 用户画像 | AP | 延迟敏感 |
| 库存 | CP | 不能超卖 |
| 评论 / 点赞 | AP | 偶尔少也 OK |
| 配置中心 | CP | 配置不一致 = 系统错乱 |
| 购物车 | AP | 延迟敏感 |
| 消息队列 | CP | 消息丢失 = 业务事故 |
| 实时指标 | AP | 偶尔少计算 OK |

## 8. 现代数据栈的 CAP 选型建议

```
1. 底层存储（HDFS / OSS）：CP（强一致）
2. 消息队列（Kafka）：CP（强一致 + 高可用）
3. NoSQL（Cassandra）：AP（最终一致）
4. 关系数据库（MySQL）：CA（但分布式下不可能严格 CA）
5. 缓存（Redis）：AP（最终一致）
6. 时序数据库（InfluxDB）：AP（最终一致）
7. 数据湖（Iceberg）：AP（最终一致）
8. 实时数仓（ClickHouse）：AP（最终一致）
```

## 9. 大数据系统的容错模型

| 模型 | 描述 | 代表 |
|------|------|------|
| 主备（Active-Passive） | 写主 → 同步 → 备 | HDFS NN HA |
| 多主（Multi-Master） | 双写 → 冲突解决 | Cassandra |
| Quorum | W + R > N | Kafka / ZooKeeper |
| Gossip | 节点间扩散 | Cassandra |
| CRDT | 无冲突数据结构 | Riak |

## 10. 实战案例

**阿里双11秒杀**：
- 库存扣减：Redis Lua 原子（AP 但 ordered）
- 订单创建：TCC（CP 但性能差）
- 商品展示：AP（最终一致）

**Netflix 推荐系统**：
- 用户画像：AP（Cassandra）
- 实时特征：Kafka Streams
- 训练数据：HDFS + Iceberg（最终一致）

## 🔗 下一步
- [HDFS 架构](/02-hdfs/architecture)
- [Kafka Streams](/07-kafka-streaming/streams)
- [OLAP vs OLTP](/08-modeling/olap-oltp)
