---
title: Raft 共识
---
# Raft 共识算法

## 1. 为什么需要共识

分布式系统多副本时，**所有节点必须对"某件事是否发生"达成一致**。例：leader 选举、配置变更、分布式锁。

```
单点：所有请求走 master，简单但 master 挂了就完蛋
多副本：每个节点独立决策 → 可能不一致
  → 需要"共识算法"让所有节点达成一致
```

## 2. Paxos vs Raft

- **Paxos**（Leslie Lamport 1990）：正确但**难懂难实现**
- **Raft**（Diego Ongaro 2014）：**易于理解**，与 Paxos 等价

Raft 设计目标：**可理解性**。三种状态 + 三个子问题。

## 3. Raft 三大子问题

```
1. Leader 选举（Leader Election）
   → 旧 leader 挂了，谁来当新 leader？

2. 日志复制（Log Replication）
   → leader 收到请求，怎么同步给 follower？

3. 安全性（Safety）
   → 如何保证所有节点在同一 index 看到同一条日志？
```

## 4. 角色与状态

```
        Candidate（候选人）
           ↑↓
        Leader（领导者）  ←→  Follower（追随者）
        - 处理写      - 同步日志
        - 复制日志    - 选举超时变 Candidate
        - 发送心跳
```

**Term（任期）单调递增**，每次选举 +1，是逻辑时钟。

## 5. Leader 选举流程

```
1. Follower 选举超时（150-300ms 随机）
   → 变 Candidate
   → term +1
   → 给自己投一票
   → 并行给其他节点发 RequestVote RPC

2. 其他节点收到 RequestVote：
   - 如果候选人的日志 ≥ 自己 → 同意
   - 否则拒绝（保证 leader 日志最新）
   - 每个 term 只能投一票

3. 候选人得票 > 半数 → 当选 leader
4. 没选出来 → 选举超时后重试（不同随机 timeout 防 split vote）
```

**关键约束**：候选人必须有"最新"的日志（通过 lastLogIndex / lastLogTerm 比较），保证 leader 数据不丢。

## 6. 日志复制流程

```
1. Client → Leader：set x = 5
2. Leader：log[term=N, idx=K] = (x, 5)
3. Leader：并行给所有 Follower 发 AppendEntries
4. Follower 收到 → 写本地 log
5. Follower 收到半数以上 → 给 Client 返回成功
6. Leader：commit index = K（标记为已提交）
7. 下次心跳：通知 Follower commit K
8. Follower 提交 log[K] → apply 到状态机
```

**注意**：写成功 = 半数节点写 log 成功，不等于所有节点都提交。**保证最终一致提交**。

## 7. 关键概念：一致性级别

| 级别 | 说明 | 性能 | 一致性 |
|------|------|------|---------|
| **线性一致** | 看到所有写，按全局顺序 | 慢 | 强 |
| **顺序一致** | 同一客户端看到自己写 | 中 | 中 |
| **因果一致** | 因在果前 | 中 | 中 |
| **最终一致** | 总会一致 | 快 | 弱 |

Raft 实现**线性一致**。

## 8. Raft 实战应用

| 系统 | 用 Raft 做什么 |
|------|----------------|
| **etcd** | k8s 配置存储 + leader 选举 |
| **Consul** | 服务发现 + 健康检查 |
| **Kafka**（KIP-500 之后）| controller quorum（KRaft 模式） |
| **TiDB** | 分布式 SQL 的 PD（Placement Driver）|
| **CockroachDB / etcd** | 分布式一致性存储 |

## 9. Raft 局限

- **写性能受 quorum 限制** = O(N) 消息
- **脑裂瞬间可能双 leader**（少数派自动 step down）
- **snapshot 频繁时性能下降**

## 10. 实战选型

```
场景：分布式 KV / 配置中心
  - 小规模（≤ 7 节点）：Raft / etcd
  - 中大规模：分片 + Raft（如 TiKV、CockroachDB）
  - 全球规模：CRDT / Dynamo 风格

场景：分布式协调
  - leader 选举：Raft（标准做法）
  - 分布式锁：etcd（lease + watch）
  - 集群成员：memberlist + gossip
```

## 🔗 下一步
- [CAP 定理](/03-ha-theory/cap)
- [Quorum 多数派](/03-ha-theory/quorum)
- [BASE / 最终一致性](/03-ha-theory/base)
