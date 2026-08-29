---
title: Paxos/Raft 概述
date: 2026-08-15  # date-auto-injected
---

# 📜 Paxos/Raft 概述

> 分布式一致性的两大经典算法。Redis Sentinel / Cluster 都涉及 leader 选举思想，理解 Paxos / Raft 是深入 Redis 高可用的关键。

## 一、分布式一致性核心问题

### 1.1 问题定义

在分布式系统中，多个节点需要对某个值达成一致，且要容忍节点故障、网络分区。**FLP 不可能定理**（Fischer-Lynch-Patterson）证明：在网络可能丢失消息的异步系统中，**不存在一个能保证一致的共识算法**。

工程上的妥协：

```text
FLP 定理 + 现实约束
   │
   ├─ 加超时机制（部分同步模型）→ Paxos / Raft 可行
   ├─ 加多数派约束（2F+1 节点容 F 个故障）→ 工业可用
   └─ 接受偶发不一致 + 业务补偿 → 工程落地
```

### 1.2 CAP 定理

```text
一致性 (Consistency)
可用性 (Availability)
分区容忍 (Partition tolerance)
   │
   └─ 分布式系统必须容忍分区 → 在 C 和 A 之间取舍
```

Redis 主从 + Sentinel 是 **AP**（高可用优先，最终一致）。
Zookeeper / etcd 是 **CP**（强一致优先）。

## 二、Paxos 算法

Leslie Lamport 于 1998 年提出，被誉为"分布式共识的圣杯"。Google Chubby / Zookeeper Zab 都基于 Paxos 思想。

### 2.1 角色

```text
Proposer  : 提案发起者，提出 value (value, proposal_id)
Acceptor  : 投票者，对提案进行 accept / reject
Learner   : 学习者，从 Accept 阶段学习已选定的 value
```

### 2.2 Basic Paxos 两阶段

#### Phase 1: Prepare（准备）

```text
Proposer                           Acceptors
   │                                   │
   │── Prepare(N) ───────────────────► │  N 是递增的提案号
   │                                   │
   │                          ┌────────┴────────┐
   │                          ▼                 ▼
   │                    Acceptor 1       Acceptor 2
   │                    收到 N          收到 N'
   │                          │                 │
   │                          ▼                 ▼
   │  ◄── Promise(N, noAccept) ───  ◄── Promise(N', accepted V) ──
   │
   ├─ 若 Acceptor 已接受过提案，Promise 带 (accepted_proposal_id, accepted_value)
   └─ Proposer 必须用 Acceptor 已接受的 value 重新提案
```

#### Phase 2: Accept（接受）

```text
Proposer                           Acceptors
   │                                   │
   │── Accept(N, V) ────────────────► │  V 是 Phase 1 中选定的 value
   │                                   │
   │                          ┌────────┴────────┐
   │                          ▼                 ▼
   │                      Accepted        Accepted
   │                          │                 │
   │  ◄── Accepted(N, V) ─── ◄── Accepted(N, V) ──
   │
   └─ 多数派 Accept → value 被选定
```

### 2.3 Basic Paxos 难点

1. **活锁**：多个 Proposer 轮流提更高编号，导致 Phase 2 永远到不了多数派。
2. **难理解**：Lamport 论文数学化强，工程实现困难。
3. **效率低**：一次提案需要 2 轮 RPC。

### 2.4 Multi-Paxos

工业级优化：

```text
1. 选举一个稳定 Leader（Proposer）
2. Leader 直接跳过 Prepare 阶段
3. 连续提案只需一轮 RPC（Accept）
4. 大幅提升吞吐量
```

Zookeeper Zab、Raft 本质都是 Multi-Paxos 的简化版。

## 三、Raft 算法

Diego Ongaro 2014 年提出，目标是"可理解性"。分三部分：

1. **Leader 选举**（Leader Election）
2. **日志复制**（Log Replication）
3. **安全性**（Safety）

### 3.1 角色与状态

```text
         ┌──────────┐
         │ Follower │ ◄──────────────────┐
         └──────────┘                    │
              │                          │
   election timeout                       │
              ▼                          │
         ┌──────────┐  higher term      │
         │Candidate │ ──────────────────►│
         └──────────┘                    │
              │                          │
              │ majority votes           │
              ▼                          │
         ┌──────────┐                    │
         │  Leader  │ ───────────────────┘
         └──────────┘   append entries
```

每个节点有三种状态：

| 状态 | 角色 | 职责 |
|------|------|------|
| Follower | 被动 | 响应 Leader 的心跳和日志同步 |
| Candidate | 候选 | 选举期间，发送 RequestVote |
| Leader | 主 | 处理写请求，同步日志到多数派 |

### 3.2 Leader 选举

```text
1. Follower 在 election timeout（150~300ms 随机）内没收到 Leader 心跳
2. Follower 变成 Candidate，term +1
3. Candidate 投票给自己
4. 向其他节点发 RequestVote RPC
5. 收到多数派投票 → 成为 Leader
6. 收到 AppendEntries（来自 Leader）→ 退回 Follower
7. 收到更高 term → 退回 Follower
```

**关键概念：Term（任期）**

```text
Term 1:    Leader A
Term 2:    A 故障 → 选 B 为 Leader
Term 3:    B 故障 → 选 C 为 Leader
Term 4:    C 仍是 Leader
```

Term 单调递增，每个 Term 最多一个 Leader。

### 3.3 日志复制

```text
Client        Leader         Followers
   │             │                │
   │── SET x=1 ─►│                │
   │             │── AppendEntries(term, prevIndex, prevTerm, entries) ──►
   │             │◄── Success ────│
   │             │── AppendEntries(...) ──►
   │             │◄── Success ────│
   │             │  (多数派成功)
   │             │── Commit ─────►│
   │◄── OK ──────│                │
   │             │                │
   └─────── 状态机执行 x=1 ───────┘
```

**日志条目结构**

```text
┌──────────┬──────────┬──────────┬──────────┐
│ Term 4   │ Term 4   │ Term 5   │ Term 5   │
│ SET x=1  │ SET y=2  │ SET x=3  │ DEL z    │
└──────────┴──────────┴──────────┴──────────┘
     committed    committed   committed   committed
```

每条日志都标注 Term，复制到多数派后 committed，可应用到状态机。

### 3.4 安全性保证

Raft 的 5 个不变量：

1. **Election Safety**：每个 Term 最多一个 Leader。
2. **Leader Append-Only**：Leader 不会删除或覆盖本地日志。
3. **Log Matching**：相同 index + term 的日志条目内容相同，且前面所有条目都相同。
4. **Leader Completeness**：已 committed 的日志一定存在于所有更高 Term 的 Leader 中。
5. **State Machine Safety**：相同 index 的日志条目最终应用到状态机的命令相同。

## 四、Raft vs Paxos 对比

| 维度 | Paxos | Raft |
|------|-------|------|
| 提出时间 | 1998 | 2014 |
| 可理解性 | 极难 | 相对简单 |
| 工业实现 | Chubby、Zab | etcd、Consul、TiKV |
| Leader | 任意 Proposer | 强 Leader |
| 日志 | 不保证连续 | 强一致连续 |
| 工程友好度 | 难 | 易 |

**Raft 是 Paxos 的简化工程版**，牺牲一定灵活性换取可理解性。

## 五、Redis Sentinel 的 Leader 选举

Redis Sentinel 用类似 Raft 的机制选 Leader Sentinel：

```text
1. 当主节点被多数 Sentinel 判定客观下线
2. 每个 Sentinel 都可以成为 Leader 候选人
3. 每个 Sentinel 发 Sentinel is-master-down-by-addr 命令要求选自己
4. 收到多数 Sentinel 同意 → 成为 Leader Sentinel
5. Leader Sentinel 选一个从节点升级为主
```

**与 Raft 的差异**：

| 维度 | Raft | Sentinel |
|------|------|----------|
| 选举时机 | 任意时机（election timeout） | 仅当主节点客观下线 |
| Term | 全局递增 | 每个 Sentinel 独立纪元（config_epoch） |
| 节点角色 | 持久角色 | Leader Sentinel 是临时的 |
| 日志复制 | 有日志条目要复制 | 主要是配置变更 |

Sentinel 选举更轻量，不需要日志复制，但缺乏强 Leader 概念。

## 六、Redis Cluster 的故障转移

Cluster 中每个 Master 都可以发起选举（不是全局单 Leader）：

```text
1. Master A 故障，从 B/C/D 中选一个从节点（如 B2）升主
2. B2 自增 configEpoch（局部 term）
3. B2 向所有 Master 发 FAILOVER_AUTH_REQUEST
4. 每个 Master 在当前 epoch 内只能投一票
5. B2 收到多数派投票（≥ N/2 + 1）→ 成为新 Master
6. B2 广播自己是新 Master，其他节点更新路由表
```

**关键设计**

- **局部 epoch**：每个槽的故障转移独立选举，不像 Raft 那样全局共享 term。
- **cluster-node-timeout 默认 15 秒**：超时触发选举。
- **replica-priority 0**：可以禁止某个从节点参与选举（如弱机器）。

## 七、共识算法工业实践

| 系统 | 算法 | 用途 |
|------|------|------|
| Zookeeper | Zab（Multi-Paxos 变体） | 配置中心 / 分布式锁 |
| etcd | Raft | K8s 配置 |
| Consul | Raft | 服务发现 |
| TiKV | Raft | 分布式 KV |
| CockroachDB | Raft | 分布式 SQL |
| Redis Sentinel | 类似 Raft | 主从切换 |
| Redis Cluster | 类似 Raft（局部） | 槽位故障转移 |

## 八、Java 实现 Raft（简化版）

```java
public class RaftNode {
    enum State { FOLLOWER, CANDIDATE, LEADER }

    private State state = State.FOLLOWER;
    private long currentTerm = 0;
    private String votedFor = null;       // 本 term 投给了谁
    private final List<LogEntry> log = new ArrayList<>();
    private long commitIndex = 0;

    private final Random random = new Random();

    // 选举超时（150~300ms 随机）
    private long electionTimeout() {
        return 150 + random.nextInt(150);
    }

    /**
     * Follower 选举超时 → 变成 Candidate 开始选举
     */
    public void startElection() {
        state = State.CANDIDATE;
        currentTerm++;
        votedFor = selfId;
        long votes = 1;  // 投自己
        long deadline = System.currentTimeMillis() + electionTimeout();

        // 向所有 peer 发 RequestVote
        for (RaftNode peer : peers) {
            RequestVoteResponse resp = peer.requestVote(
                new RequestVote(currentTerm, log.size(), lastLogTerm()));
            if (resp.voteGranted) votes++;
        }

        // 收到多数派 → 成为 Leader
        if (votes > peers.size() / 2) {
            becomeLeader();
        } else if (System.currentTimeMillis() >= deadline) {
            // 超时 → 下一轮选举（term +1）
            startElection();
        }
    }

    private void becomeLeader() {
        state = State.LEADER;
        // 立即发空 AppendEntries（防止新一轮选举）
        sendHeartbeats();
    }

    /**
     * 处理投票请求
     */
    public RequestVoteResponse requestVote(RequestVote req) {
        // 拒绝任期小的请求
        if (req.term < currentTerm) {
            return new RequestVoteResponse(currentTerm, false);
        }
        // 候选人的日志至少和自己一样新才能投票
        boolean logUpToDate = req.lastLogTerm > lastLogTerm()
            || (req.lastLogTerm == lastLogTerm() && req.lastLogIndex >= log.size());

        if (req.term > currentTerm) {
            currentTerm = req.term;
            state = State.FOLLOWER;
            votedFor = null;
        }

        boolean voteGranted = (votedFor == null || votedFor.equals(req.candidateId))
            && logUpToDate;
        if (voteGranted) votedFor = req.candidateId;

        return new RequestVoteResponse(currentTerm, voteGranted);
    }

    /**
     * 心跳 + 日志复制（AppendEntries）
     */
    public AppendEntriesResponse appendEntries(AppendEntries req) {
        if (req.term < currentTerm) {
            return new AppendEntriesResponse(currentTerm, false);
        }
        // 收到合法 Leader 的心跳 → 退回 Follower
        if (req.term > currentTerm || state == State.CANDIDATE) {
            currentTerm = req.term;
            state = State.FOLLOWER;
            votedFor = null;
        }

        // 日志一致性检查 + 追加
        if (req.prevLogIndex < log.size()
            && log.get(req.prevLogIndex).term != req.prevLogTerm) {
            return new AppendEntriesResponse(currentTerm, false);
        }
        // 删除冲突日志，追加新条目
        log.subList(req.prevLogIndex, log.size()).clear();
        log.addAll(req.entries);

        // 更新 commitIndex
        if (req.leaderCommit > commitIndex) {
            commitIndex = Math.min(req.leaderCommit, log.size());
        }
        return new AppendEntriesResponse(currentTerm, true);
    }
}

class LogEntry {
    long term;
    String command;
}

class RequestVote {
    long term;
    long lastLogIndex;
    long lastLogTerm;
    String candidateId;
    RequestVote(long t, long i, long lt) {
        term = t; lastLogIndex = i; lastLogTerm = lt;
    }
}

class RequestVoteResponse {
    long term;
    boolean voteGranted;
    RequestVoteResponse(long t, boolean v) {
        term = t; voteGranted = v;
    }
}

class AppendEntries {
    long term;
    long prevLogIndex;
    long prevLogTerm;
    List<LogEntry> entries;
    long leaderCommit;
}

class AppendEntriesResponse {
    long term;
    boolean success;
    AppendEntriesResponse(long t, boolean s) {
        term = t; success = s;
    }
}
```

## 九、面试追问清单

| 追问 | 答案 |
|------|------|
| 为什么 Redis 不用强一致共识算法？ | 性能考虑，Redis 主从异步复制延迟低，强一致会拖累写入 |
| Paxos 为什么难实现？ | 提案号管理、活锁、活性的权衡，工程化困难 |
| Raft 怎么保证选举安全？ | 多数派投票 + 投票限制（候选人日志必须足够新） |
| Sentinel / Cluster 与 Raft 的区别？ | 局部 epoch，配置简单，不做完整日志复制 |
| 强一致 vs 最终一致怎么选？ | 业务决定：金融用 ZK（日志不能丢），社交用 Redis（最终可接受） |

## 十、下一步

到这里 8 篇 Redis 面试专题全部完成。建议按顺序阅读，形成完整的 Redis 知识体系：

1. [📝 高频面试题（上）](/08-interview/basic) — 20 道基础题
2. [📝 高频面试题（下）](/08-interview/advanced) — 20 道进阶题
3. [🔒 分布式锁手撕](/08-interview/lock-coding) — 含 Redisson 看门狗
4. [📚 LRU 算法手撕](/08-interview/lru) — 字节原题
5. [🦘 跳表手撕](/08-interview/skiplist-coding) — Redis ZSet 核心
6. [❄️ 缓存三大问题](/08-interview/avalanche) — 穿透/击穿/雪崩
7. [🎯 一致性 Hash](/08-interview/consistent-hash) — 含完整代码
8. [📜 Paxos/Raft 概述](/08-interview/consensus) — 共识算法与 Redis 高可用

后续可以回到首页继续其他章节的系统学习：[🏠 Redis 知识图谱首页](/)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [mysql](https://java-px.bot.cd/mysql/):MySQL 主存
- [kafka](https://java-px.bot.cd/kafka/):Kafka 异步队列
- [java](https://java-px.bot.cd/java-web-manual/):Java 客户端（Redisson / Jedis）
