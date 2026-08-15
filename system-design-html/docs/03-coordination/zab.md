---
title: ZAB 协议（ZooKeeper Atomic Broadcast）
---

# ZAB 协议

> ZooKeeper 2010 年前后提出。专为协调服务设计的原子广播协议，类似于 Raft 但有差异。

## 1. ZAB 是什么？

```
ZAB = ZooKeeper Atomic Broadcast
  - ZooKeeper 的核心一致性协议
  - 保证集群所有节点收到相同顺序的消息
  - 类似 Raft，但不是简单照搬

应用：ZooKeeper / 早期 HBase / Dubbo / Kafka（早期版本）
```

## 2. 与 Raft 的对比

```
┌──────────────┬──────────────────┬──────────────────┐
│              │ ZAB              │ Raft             │
├──────────────┼──────────────────┼──────────────────┤
│ 消息类型     │ 事务（zxid）     │ 日志条目         │
│ 顺序保证     │ 全序             │ 日志顺序         │
│ Leader 选举  │ Fast Leader      │ 多数派           │
│ 恢复策略     │ 重放 + 截断      │ 重放             │
│ 设计目标     │ 主备强一致       │ 通用共识         │
│ 工程成熟度   │ 非常高           │ 高               │
└──────────────┴──────────────────┴──────────────────┘

📌 ZAB 是"主备复制 + 原子广播"的组合
   Raft 是"日志复制 + Leader 选举"的组合
```

## 3. 核心概念

### 3.1 ZXID

```
ZXID = ZooKeeper Transaction ID
  - 64 位整数
  - 高 32 位 = epoch（Leader 周期）
  - 低 32 位 = counter（事务序号）

例：zxid = (5, 100)
  - epoch 5（当前是第 5 任 Leader）
  - 第 100 个事务
```

### 3.2 epoch

```
每次 Leader 切换：
  - 新 Leader 递增 epoch
  - 所有旧 epoch 的决议作废
  - 防止脑裂（两个 Leader 都声称权威）
```

### 3.3 状态

```
LOOKING：选举中
FOLLOWING：Follower
LEADING：Leader
OBSERVING：只读节点（不参与投票）
```

## 4. 协议阶段

```
ZAB 有三个阶段：

1. Fast Leader Election（快速选举）
   - 启动时或 Leader 挂了
   - 选出 ZXID 最大的节点为新 Leader

2. Recovery（恢复）
   - 新 Leader 同步历史
   - 保证所有 Follower 与 Leader 一致

3. Broadcast（广播）
   - 正常运行
   - Leader 接收请求，原子广播给 Follower
```

## 5. Fast Leader Election

### 5.1 选举流程

```
1. 所有节点初始 LOOKING
2. 每个节点投票给自己（包含 zxid、sid）
3. 节点间交换投票
4. 收到别人投票后比较：
   - 先比 zxid（越大越优先）
   - 再比 sid（myid，越大越优先）
5. 更新自己投票给"最优"
6. 某个节点的投票被多数派接受 → 当选

📌 比 Raft 选举快（不需要 election timeout 随机化）
   因为 ZAB 直接选 ZXID 最大的节点
```

### 5.2 为什么选 ZXID 最大？

```
ZXID 大 = 数据最新
  - 新 Leader 必须包含所有已提交的事务
  - ZXID 最大的节点数据最新
  - 选它可以避免数据回滚

对比 Raft：
  - Raft 用选举限制（候选人的日志 ≥ 多数派）
  - 效果相同
  - ZAB 实现更直接
```

## 6. Recovery 阶段

### 6.1 为什么需要？

```
新 Leader 刚当选：
  - Follower 可能不完整（缺一些事务）
  - Follower 可能多余（有 Leader 没有的提案）
  → 必须先把所有 Follower 同步到 Leader 的状态
```

### 6.2 同步流程

```
1. Leader 标记自己 epoch
2. Follower 收到 NEWLEADER 消息
3. Follower 发最新 zxid 给 Leader
4. Leader 对比 Follower 的状态：

   Follower 比 Leader 旧 → 发 SNAPSHOT 或 DIFF
   Follower 比 Leader 新 → 丢弃 Follower 的多余事务（trunc）
```

### 6.3 SNAPSHOT vs DIFF

```
SNAPSHOT（全量）：
  - Follower 落后太多
  - 直接发整个数据快照

DIFF（增量）：
  - Follower 落后不多
  - 发 leaderLastZxid 之后的所有事务
  - Follower 重放追上
```

## 7. Broadcast 阶段

### 7.1 流程

```
1. Leader 收到客户端请求
2. Leader 生成 zxid（epoch 不变，counter +1）
3. Leader 发 PROPOSAL 给所有 Follower
4. Follower 写入事务日志，返回 ACK
5. Leader 收到多数派 ACK → COMMIT
6. Leader 发 COMMIT 给 Follower
7. Follower 应用事务到内存
8. Leader 返回成功给客户端
```

### 7.2 与 Raft 对比

```
┌──────────────────────┬─────────────────�────────────────┐
│                      │ ZAB Broadcast   │ Raft AppendEn. │
├──────────────────────┼─────────────────┼────────────────┤
│ 消息数（提交）        │ 2 (PROPOSAL+COMMIT) │ 1（心跳内）│
│ Follower 写日志时机   │ 收到 PROPOSAL   │ 收到 AppendEn. │
│ Follower 提交时机     │ 收到 COMMIT     │ 心跳内被告知   │
│ 顺序保证             │ zxid 严格       │ log index 严格 │
└──────────────────────┴─────────────────┴────────────────┘

📌 ZAB 多一轮 COMMIT 消息，但更明确
   Raft 性能略优
```

## 8. ZAB 的关键保证

### 8.1 全序广播（Total Order Broadcast）

```
所有 Follower 收到的事务顺序一致
  - 即使是并发的请求
  - 也要按 zxid 顺序应用
  → 状态机收敛
```

### 8.2 原子性

```
事务要么全部提交，要么全部不提交
  - 多数派 ACK → 提交
  - 任一失败 → 不提交
  → 与 2PC 的差异：不依赖协调者的两阶段阻塞
```

### 8.3 因果一致性

```
同一客户端的请求严格按顺序处理
不同客户端的请求可能并发但有序
```

## 9. ZAB 与 2PC 的区别

```
2PC（两阶段提交）：
  - 同步阻塞
  - 协调者故障可能卡死
  - 数据一致但可用性差

ZAB Broadcast：
  - 异步广播
  - Leader 挂了选举新 Leader
  - 不阻塞
  → 性能 + 可用性大幅提升
```

## 10. ZAB 的工程实践

### 10.1 ZooKeeper 集群

```
配置：
  - 奇数节点（3/5/7）
  - 半数为 follower
  - 1 个 leader

容错：
  - N=3：容忍 1 故障
  - N=5：容忍 2 故障
  - 性能下降随 N 增加
```

### 10.2 ZK 的应用场景

```
1. 分布式锁：
   - 临时顺序节点
   - 最小节点持锁

2. 服务注册与发现：
   - Dubbo 服务注册
   - Kafka 早期版本

3. 配置中心：
   - 监听节点变化（watch）
   - 配置变更实时推送

4. 分布式队列：
   - 顺序节点天然有序
```

### 10.3 ZK 的局限

```
1. 写性能瓶颈：
   - 所有写都过 Leader
   - 单点写入

2. ZAB 协议本身：
   - 不支持拜占庭容错
   - 假设节点崩溃而非恶意

3. 运维复杂：
   - ZAB 选举时间可能较长（秒级）
   - 集群扩展需要重启
```

## 11. 一句话总结

```
📌 ZAB = ZooKeeper 专用的原子广播协议，与 Raft 思路类似但有差异
� ZXID（64位）= epoch（高32） + counter（低32）
📌 选举直接选 ZXID 最大的节点（数据最新）
📌 Recovery 阶段同步 Follower 到 Leader 状态
📌 Broadcast 阶段保证事务全序 + 原子性
📌 ZooKeeper 是分布式协调的事实标准（虽然现在 etcd 更流行）
📌 学习 ZAB = 理解"工业级 Paxos/Raft"的具体实现
```

## 12. 参考资料

- ZooKeeper: Wait-free coordination for Internet-scale systems (Hunt et al., 2010)
- ZooKeeper's Atomic Broadcast Protocol (Junqueira, 2014)
- Apache ZooKeeper 官方文档
- etcd vs ZooKeeper 对比文章
- DDIA 第 9 章
