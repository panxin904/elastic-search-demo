---
title: 控制器演进
---

# ⚙️ 控制器演进

> Kafka 控制器经历了从 **ZooKeeper 选举**到 **KRaft 协议**的重大演进。本章对比两代控制器的设计与差异。

## 🎯 两代控制器对比

### Kafka 0.x - 2.x：ZooKeeper 模式

```
┌────────────────────────────────────────────┐
│              ZooKeeper Ensemble             │
│              (3 或 5 节点)                  │
│  - 存储集群元数据                            │
│  - 选举 Controller                          │
│  - 监听 Broker 上下线                       │
└────────────────────────────────────────────┘
            ↕ (双向通信)
┌────────────────────────────────────────────┐
│              Kafka Brokers                  │
│  - Broker 注册到 ZK                          │
│  - 竞争 Controller 角色（第一个在 ZK 创建临时节点） │
│  - Controller 监听 ZK 路径变化               │
└────────────────────────────────────────────┘
```

### Kafka 3.x：KRaft 模式

```
┌────────────────────────────────────────────┐
│          Kafka KRaft Cluster                │
│                                              │
│  ┌─────────────────────────────────────┐   │
│  │ Controller 集群（基于 Raft 协议）      │   │
│  │   Active + 多个 Standby              │   │
│  │   通过 Raft Log 同步元数据            │   │
│  └─────────────────────────────────────┘   │
│  ┌─────────────────────────────────────┐   │
│  │ Broker 集群                          │   │
│  │   每个节点同时是 Broker + Controller  │   │
│  │   读取 Active Controller 的日志      │   │
│  └─────────────────────────────────────┘   │
└────────────────────────────────────────────┘
```

## 🔄 ZooKeeper 时代的问题

### 1. 部署复杂

```
❌ 需要单独维护 ZK 集群
   - ZK 集群本身需要 3 或 5 节点
   - 增加运维成本

❌ 双集群运维
   - Kafka 集群 + ZK 集群
   - 监控、备份、升级都要管

❌ 网络分区敏感
   - ZK 半数以上节点宕机则 ZK 不可用
   - 影响 Kafka 集群
```

### 2. Controller 选举慢

```
ZK 选举流程：
  1. Broker 在 ZK 创建临时节点
  2. 节点变化触发 Watch
  3. 各 Broker 抢锁（临时节点）
  4. 第一个抢到的成为 Controller
  5. 其他 Broker 收到通知

选举耗时：10-30 秒
  - 期间 Kafka 集群只读
  - Producer 会收到 NotControllerException
  - 需要重试
```

### 3. 元数据性能瓶颈

```
ZK 的写入性能有限（强一致性）
  - 每个元数据变更都写入 ZK
  - 大量 Topic / Partition 时 ZK 成为瓶颈
  - 限制 Kafka 集群规模

集群规模限制：
  - 推荐 ≤ 200,000 个 Partition
  - 单个 Topic 最多 200,000 个 Partition
  - ZK 单节点写入 TPS ≈ 几万
```

### 4. 脑裂风险

```
场景：网络分区

ZK 集群：
  - 多数派节点（2/3）继续服务
  - 少数派节点（1/3）拒绝写入

Kafka 集群：
  - 与多数派 ZK 通信的 Broker：正常
  - 与少数派 ZK 通信的 Broker：失联
  
问题：
  - 少数派 ZK 的 Controller 也可能被"选举"出来
  - 出现多个 Controller（脑裂）
  - 需要复杂的防脑裂机制
```

## 🚀 KRaft 时代的优势

### 1. 简化部署

```
✅ 单一集群
   - 不再依赖 ZK
   - 只需部署 Kafka 集群

✅ 启动更快
   - Kafka Broker 启动同时启动 Controller
   - 无需连接 ZK

✅ 运维简单
   - 只需运维一套系统
   - 监控、备份、升级更简单
```

### 2. 快速选举

```
KRaft 选举流程（基于 Raft）：
  1. Follower 心跳超时（默认 1s）
  2. 增加 term，自增选举超时（随机 0-1s）
  3. 发起 RequestVote RPC
  4. 获得多数派投票后成为 Leader
  5. 立即开始处理请求

选举耗时：1-5 秒（比 ZK 快 5-10 倍）
```

### 3. 大规模支持

```
KRaft 优势：
  - 支持 100 万级 Partition
  - 单 Topic 可达 200,000+ Partition
  - 集群规模可达 1000+ Broker

性能对比：
  - ZooKeeper：~200,000 Partition 上限
  - KRaft：~1,000,000+ Partition
```

### 4. 强一致性保证

```
Raft 协议保证：
  - 选举安全性：同一 term 最多一个 Leader
  - 日志匹配性：Leader 日志与 Follower 一致
  - 提交安全性：已提交日志不会丢失
  - Leader 完整性：Leader 包含所有已提交日志

对比 ZooKeeper：
  - ZAB 协议类似 Raft，但实现复杂
  - KRaft 实现更现代、更易理解
```

## 📊 KRaft 关键设计

### 元数据日志（__cluster_metadata）

```
存储：
  - 元数据写入 __cluster_metadata Topic
  - 内部 Topic，与业务数据隔离
  - 由 Controller 维护

格式：
  - 每条记录表示一次元数据变更
  - 如：创建 Topic、删除 Partition、修改 Broker

同步：
  - Active Controller 写入日志
  - Standby Controller 复制日志
  - Followers 异步追赶
```

### Raft 选举机制

```
节点状态：
  - Leader：处理所有写请求
  - Follower：复制日志
  - Candidate：选举中的候选

选举触发：
  - Follower 在 election.timeout 内未收到 Leader 心跳
  - 超时时间随机化（避免同时选举）
  - Follower 转为 Candidate，发起选举

投票规则：
  - 每个节点同一 term 只能投 1 票
  - Candidate 的日志至少和自己一样新（up-to-date check）
  - 获得多数派投票（n/2 + 1）即获胜

任期（Term）：
  - 单调递增整数
  - 每次选举开始新 Term
  - 旧的 Leader 收到新 Term 的请求会立即退位
```

### 元数据快照（Snapshot）

```
Snapshot = 元数据状态的完整快照
  - 定期生成（默认 5 分钟）
  - 用于 Follower 追赶
  - 减少日志保留时间

Snapshot 包含：
  - 所有 Topic 列表
  - 所有 Partition 状态
  - 所有 Broker 列表
  - 所有 ACL 配置

Follower 落后太多时：
  - 接收完整 Snapshot（而不是一条条日志）
  - 比 ApplyLog 更快
```

## 🔧 KRaft 配置

```properties
# ==== KRaft 模式开关 ====
process.roles=broker,controller
# 可选：broker,controller（混合）或 broker / controller（独立）

# ==== Controller 集群 ====
controller.quorum.voters=1@node1:9093,2@node2:9093,3@node3:9093
# voter 列表：id@host:port
# 必须奇数个（容忍 n/2 节点故障）

# ==== 监听器 ====
listeners=PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
controller.listener.names=CONTROLLER

# ==== 元数据日志 ====
metadata.log.dir=/data/kafka-meta          # KRaft 日志目录
metadata.log.max.retention.bytes=1073741824  # 日志保留上限
metadata.log.max.record.bytes=33554432      # 单条记录最大 32MB

# ==== 快照 ====
metadata.log.max.snapshot.interval.ms=3600000  # 快照间隔（默认 1 小时）

# ==== 选举相关 ====
controller.election.timeout.ms=30000          # 选举超时
controller.quorum.fetch.timeout.ms=2000        # 元数据获取超时
```

## 🔄 KRaft 与 ZooKeeper 迁移

### 从 ZK 迁移到 KRaft

```
Kafka 2.8+：KRaft 可用（但生产建议等 3.x）
Kafka 3.3+：KRaft 成熟
Kafka 3.5+：推荐生产环境使用 KRaft
```

迁移步骤：
```
1. Kafka 3.x 集群（默认 KRaft）
2. 不需要迁移工具
3. 直接部署 KRaft 集群
4. 旧 ZK 集群废弃
```

## 📊 性能对比

| 维度 | ZooKeeper 模式 | KRaft 模式 |
|------|---------------|-----------|
| 选举时间 | 10-30 秒 | 1-5 秒 |
| 集群规模 | ≤ 200K Partition | ≤ 1M+ Partition |
| 部署复杂度 | 高（双集群） | 低（单集群） |
| 元数据写入 | 受 ZK 性能限制 | 不受限 |
| 脑裂风险 | 需复杂处理 | Raft 保证 |
| 监控难度 | 高（双套监控） | 低 |
| 运维成本 | 高 | 低 |

## ⚠️ KRaft 的限制

```
⚠️ 单集群规模上限
   - 虽然比 ZK 大，但仍有上限
   - 推荐 ≤ 100 Broker

⚠️ 元数据延迟
   - 元数据变更需复制到所有 Broker
   - 大集群复制延迟较高

⚠️ Controller 仍是 Active-Standby
   - Active Controller 处理所有写
   - Standby 备机故障不影响（自动重选）
```

## 🛠️ KRaft 集群搭建示例

```properties
# 3 节点 KRaft 集群
# node1 配置
process.roles=broker,controller
node.id=1
listeners=PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
advertised.listeners=PLAINTEXT://node1:9092
controller.quorum.voters=1@node1:9093,2@node2:9093,3@node3:9093
controller.listener.names=CONTROLLER
log.dirs=/data/kafka-logs

# 启动命令
KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"
bin/kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c config/kraft/server.properties
bin/kafka-server-start.sh -daemon config/kraft/server.properties

# 验证
bin/kafka-broker-api-versions.sh --bootstrap-server node1:9092
bin/kafka-metadata-quorum.sh --bootstrap-server node1:9092 describe --status
```

## 🎯 总结

**控制器演进核心要点**：
- ✅ Kafka 3.x 推荐 KRaft 模式
- ✅ KRaft：基于 Raft 协议，选举快（秒级）
- ✅ KRaft：单集群 1M+ Partition
- ✅ 摆脱 ZooKeeper 依赖
- ✅ 简化部署、降低运维成本
- ⚠️ KRaft 仍需 3+ 节点集群
- ⚠️ 大集群需精细调优

**下一步：** [📋 常用命令总览](/03-cli/overview) — Kafka CLI 工具详解
