---
title: Raft 共识算法
date: 2026-08-15  # date-auto-injected
---

# Raft 共识算法


![Raft 协议流程 — Leader 选举 + 日志复制](/raft-flow.svg)

> Diego Ongaro & John Ousterhout 2014 年提出。"一种易于理解的共识算法"。

## 1. 为什么 Raft？

```
Paxos 的问题：
  - Lamport 1998 年提出
  - 难懂（Lamport 自己也写了简化版）
  - 实现复杂，边界情况多
  - 工程师需要花 1+ 年才能正确实现

Raft 的目标：
  - 和 Paxos 一样的容错能力
  - 更容易理解
  - 实现标准化
  → 工程界的"标准共识算法"
```

## 2. Raft 的两个核心

```
Raft 把共识拆成三个子问题：

1. Leader Election（领导者选举）
   - 集群中始终有一个 Leader
   - 其他节点是 Follower
   - Leader 挂了 → 选举新 Leader

2. Log Replication（日志复制）
   - Leader 接收客户端请求
   - 复制日志到所有 Follower
   - 多数派确认后 apply

3. Safety（安全性）
   - 选举安全：每个 term 最多一个 Leader
   - 日志匹配：Leader 的日志必须包含所有已提交的条目
   - 状态机安全：所有节点 apply 相同日志得到相同状态
```

## 3. 角色与状态

```
�─────────────────────────────────────────────────┐
│                                                 │
│   Follower（默认）                              │
│      ↓                                          │
│   Candidate（选举中）                           │
│      ↓                                          │
│   Leader（当选）                                │
│                                                 │
└─────────────────────────────────────────────────┘

所有节点初始为 Follower
选举超时 → 变 Candidate
获得多数票 → 变 Leader
发现更高 term → 退回 Follower
```

## 4. Term（任期）

```
Term = 一个 Leader 的执政期间

特点：
  - 全局单调递增
  - 每个 term 最多一个 Leader
  - 如果选举分裂 → 下个 term 重新选

类比：美国总统大选
  - 每个 term 4 年
  - 每 term 一个总统
  - 选举失败 → 下个 term 重新选
```

## 5. Leader Election

### 5.1 选举触发

```
Follower 在 election timeout（150-300ms 随机）内：
  - 没收到 Leader 心跳
  → 自己变 Candidate
  → term + 1
  → 投自己一票
  → 发 RequestVote RPC 给其他节点
```

### 5.2 投票规则

```
Follower 收到 RequestVote 时：
  1. term 比自己旧？ → 拒绝
  2. 这个 term 内已投过别人？ → 拒绝
  3. 候选人的日志比自己的还旧？ → 拒绝
  4. 否则 → 同意

"日志不旧于自己"：
  - 比较最后一条日志的 term
  - term 相同比 index
  - 候选人的必须 ≥ 自己的
```

### 5.3 选举结果

```
Candidate 收到多数票 → 变 Leader
  - 立即发心跳，宣告权威
  - 阻止新一轮选举

超时仍未多数 → 选举失败
  - election timeout 重新计时
  - 重新发起选举（term + 1）

📌 选举失败原因：选票分裂
   - 两个 Candidate 各得一半
   - 解决：随机超时让下次选举错开
```

## 6. Log Replication

### 6.1 流程

```
1. Client 发送命令给 Leader
2. Leader 把命令追加到本地日志
3. Leader 发 AppendEntries RPC 给所有 Follower
4. Follower 收到后追加日志，返回成功
5. Leader 收到多数派成功 → commit
6. Leader apply 命令到状态机
7. Leader 返回成功给 Client
8. 下次心跳通知 Follower 也 commit + apply
```

### 6.2 日志结构

```
日志条目：
  ┌─────────────────────────────────┐
  │ term: 5                         │
  │ index: 12                       │
  │ command: SET x = 1              │
  └─────────────────────────────────┘

日志整体：
  index:  1   2   3   4   5   6   7   8   9  10  11  12
  term:   1   1   2   2   3   3   3   4   4   4   4   5
  cmd:   A   B   C   D   E   F   G   H   I   J   K   L

committed：1-11（多数派已持久化）
applied：1-11（已 apply 到状态机）
```

### 6.3 日志一致性检查

```
AppendEntries 携带：
  - prevLogIndex：要追加位置的前一条
  - prevLogTerm：前一条的 term

Follower 检查：
  - prevLogIndex 位置的 term 与 prevLogTerm 匹配？
  - 不匹配 → 拒绝（prevLogIndex 递减重试）
  - 匹配 → 追加

📌 这一步保证 Leader 和 Follower 的日志从某个点开始完全一致
```

## 7. Safety 规则

### 7.1 选举限制

```
被选举的 Leader 必须包含所有已提交的日志条目
  - 候选人的日志必须 ≥ 多数派的日志
  - 投票规则保证这一点
  → 新 Leader 不会"丢失"已提交的数据
```

### 7.2 提交限制

```
Leader 只提交**当前 term** 的日志条目
  - 不能用旧 term 的多数派计数来提交新日志
  → 避免图灵奖论文的"幽灵提交"问题
```

### 7.3 状态机安全

```
所有节点 apply 日志的顺序必须一致
  - 日志是顺序的
  - Leader 只提交连续的多数派前缀
  - Follower 只 apply 已 commit 的前缀
  → 状态机收敛
```

## 8. 成员变更（Membership Change）

### 8.1 直接配置切换的问题

```
老配置 [A, B, C] 切到新配置 [A, B, C, D, E]

可能出现：
  - 老多数派 [A, B, C] 选出老 Leader
  - 新多数派 [A, B, D] 选出新 Leader
  - 两个 Leader 同时存在 → 脑裂

📌 单步切换在分布式下不可行
```

### 8.2 Joint Consensus（联合共识）

```
两阶段切换：
  阶段 1：Joint Consensus（old ∪ new）
    - 旧 + 新 配置都参与决策
    - 多数派 = 旧多数派 ∩ 新多数派
    - 提交到 joint 日志

  阶段 2：Commit New Configuration
    - 只用新配置
    - 多数派 = 新配置多数派

📌 etcd / Consul 的成员变更就是 Joint Consensus
```

## 9. 日志压缩（Snapshot）

### 9.1 问题

```
日志不断增长：
  - 占用磁盘
  - 启动时重放慢
  - 新节点加入需要全量同步
```

### 9.2 解决：Snapshot

```
定期把已应用的日志生成 snapshot：
  - 删除旧的日志条目
  - 保存状态机当前状态
  - 元数据：lastIncludedIndex, lastIncludedTerm

新节点加入：
  - Leader 发 InstallSnapshot RPC
  - 新节点直接接收 snapshot
  - 不需要重放所有历史日志
```

## 10. Raft vs Paxos

```
┌─────────────────┬──────────────────┬─────────────────�
│                 │ Raft             │ Paxos           │
├─────────────────┼──────────────────┼─────────────────�
│ 易懂度          │ ★★★★★            │ ★★              │
│ Leader          │ 必有             │ 可选            │
│ 日志顺序        │ 严格连续         │ 灵活            │
│ 实现复杂度      │ 低               │ 高              │
│ 工程成熟度      │ 高（etcd/Consul）│ 高（Chubby）    │
│ 性能            │ 高               │ 高              │
│ 学术贡献        │ "可理解性"       │ "正确性"        │
└─────────────────┴──────────────────┴─────────────────┘
```

## 11. Raft 工程实现

### 11.1 etcd

```
应用场景：
  - Kubernetes 的配置存储
  - 分布式锁
  - 服务发现

特点：
  - 强一致 + 高可用
  - 用 Raft + WAL
  - watch 机制监听 key 变更
```

### 11.2 Consul

```
应用场景：
  - 服务发现
  - 健康检查
  - KV 存储

特点：
  - 多数据中心 Raft
  - 内置服务注册
  - 支持 ACL
```

### 11.3 TiKV

```
应用场景：
  - 分布式 NewSQL 存储
  - TiDB 的存储层

特点：
  - Raft + RocksDB
  - Multi-Raft（按 region 分片）
  - 工业级实现
```

## 12. 一句话总结

```
📌 Raft = 易懂版 Paxos，是当代分布式协调的事实标准
📌 三个核心：Leader Election + Log Replication + Safety
📌 Term 单调递增，每个 Term 最多一个 Leader
📌 日志复制走多数派，多数派确认才 commit
📌 成员变更用 Joint Consensus，避免脑裂
📌 学习 Raft 是理解分布式共识的最佳路径
📌 工程实现：etcd（K8s）、Consul（服务发现）、TiKV（NewSQL）
```

## 13. 参考资料

- In Search of an Understandable Consensus Algorithm (Ongaro & Ousterhout, USENIX 2014)
- raft.github.io （动画演示）
- Consensus: Bridging Theory and Practice (Ongaro PhD Thesis, 2014)
- etcd Internals（GitHub）
- DDIA 第 9 章


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [architecture](https://java-px.bot.cd/architecture/):企业架构
- [java](https://java-px.bot.cd/java-web-manual/):Java 实现
- [kafka](https://java-px.bot.cd/kafka/):消息
