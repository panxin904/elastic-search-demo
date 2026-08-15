---
title: Leader 选举
---

# Leader 选举

> 集群选出一个"主"负责协调，其他节点 standby。**唯一性 + 高可用**。

## 1. 为什么需要 Leader？

```
场景：
  - 主备 MySQL：只有主能写
  - 任务调度集群：只有 1 个 worker 派发任务
  - 分布式锁服务：只有 1 个节点处理写

没有 Leader 的问题：
  - 多节点同时写 → 数据不一致（脑裂）
  - 任务重复派发 → 重复消费
  - 锁失效 → 并发问题
```

## 2. 核心要求

```
1. 唯一性：
   - 任意时刻只有 1 个 Leader
   - 多个 Leader = 脑裂 = 数据错乱

2. 高可用：
   - Leader 挂掉，新 Leader 30s 内选出
   - 不丢数据

3. 容错：
   - 多数节点存活就能选
   - 节点数 ≥ 3（容忍 1 挂）

4. 防止脑裂：
   - 网络分区时，旧 Leader 自动让位
   - quorum（多数派）原则
```

## 3. 选举算法

### 3.1 Raft

```
Raft 三角色：
  - Follower：跟随者，不主动发请求
  - Candidate：候选人，选举中
  - Leader：主，处理所有写请求

选举流程：
  1. 初始全 Follower
  2. Follower 选举超时（150-300ms 随机）
     → 变 Candidate
     → 自增 term，发起 RequestVote RPC
  3. 收到多数票 → 变 Leader
  4. Leader 定期发 AppendEntries（心跳）
  5. Follower 超时没收到心跳 → 重新选举

关键点：
  - 任期 term：单调递增，每个 Leader 一届
  - 投票规则：候选人日志 ≥ 自己的日志（防数据回退）
  - 随机超时：避免同时选举导致 split vote

📌 etcd / Consul / TiKV 都用 Raft
```

### 3.2 Paxos

```
Basic Paxos：
  - Proposer：发起提案
  - Acceptor：投票
  - Learner：学习结果

两阶段：
  Phase 1（Prepare）：
    Proposer 选提案号 n，发给多数派 Acceptor
    Acceptor 承诺不再接受 < n 的提案

  Phase 2（Accept）：
    Proposer 发 (n, value) 给多数派
    Acceptor 接受（无冲突）

  多数派接受 → value 被选定

📌 理论正确，但实现复杂
   工业界更多用 Multi-Paxos / Raft
```

### 3.3 Zab（ZooKeeper Atomic Broadcast）

```
ZAB 模式：
  - 选举（Election）：选 Leader
  - 发现（Discovery）：同步最新数据
  - 同步（Sync）：Leader 把提案广播给 Follower
  - 广播（Broadcast）：处理客户端请求

选举：
  - 基于 ZXID（事务 ID）
  - ZXID 最大的节点优先成为 Leader
  - 保证 Leader 有最新数据

📌 ZK 内部用 ZAB，比 Raft 早
```

## 4. 选举实战方案

### 4.1 基于 ZooKeeper

```java
// Curator LeaderLatch
LeaderLatch latch = new LeaderLatch(client, "/election/leader");
latch.start();
if (latch.hasLeadership()) {
    // 我是 Leader
    doSomething();
}

// LeaderLatchListener
latch.addListener(new LeaderLatchListener() {
    public void isLeader() { /* 拿到领导权 */ }
    public void notLeader() { /* 失去领导权 */ }
});
```

特点：
```
- 临时节点：session 断开自动删除
- 强一致：ZK 集群保证
- 适合：中等规模集群（< 100 节点）
- 缺点：ZK 维护成本
```

### 4.2 基于 Redis

```
方案 1：SETNX + expire
  SET leader:job myid EX 30 NX
  - 拿到 → 是 Leader
  - 没拿到 → 是 Follower
  - 每 10s 续期（看门狗）

方案 2：Redisson RLock
  RLock lock = redisson.getLock("leader:job");
  if (lock.tryLock(0, 30, TimeUnit.SECONDS)) {
      // 我是 Leader
  }

📌 性能高，但 Redis 主从切换可能短暂双 Leader
   适合：可容忍短暂脑裂的场景
```

### 4.3 基于 etcd

```go
// etcd lease + election
cli, _ := clientv3.New(clientv3.Config{Endpoints: []string{"localhost:2379"}})
lease, _ := cli.Grant(ctx, 10)  // 10s TTL
election := concurrency.NewElection(cli, "/election/")

// 参与竞选
go election.Campaign(ctx, "myvalue")

// 监听变化
ch := election.Observe(ctx)
for resp := range ch {
    // resp.Kvs 包含所有候选人
}

// 主动让位
election.Resign(ctx)
```

特点：
```
- Lease：自动过期
- Revision：全局版本号
- 强一致：基于 Raft
- K8s 默认使用
```

### 4.4 基于数据库

```sql
-- 选举表
CREATE TABLE leader_election (
  job_name VARCHAR(64) PRIMARY KEY,
  leader_id VARCHAR(64),
  elected_at TIMESTAMP,
  expire_at TIMESTAMP
);

-- 竞争
INSERT INTO leader_election (job_name, leader_id, expire_at)
VALUES ('job-A', 'host-1', NOW() + INTERVAL 30 SECOND)
ON DUPLICATE KEY UPDATE
  leader_id = IF(expire_at < NOW(), VALUES(leader_id), leader_id),
  expire_at = IF(expire_at < NOW(), VALUES(expire_at), expire_at);

-- 续期
UPDATE leader_election
SET expire_at = NOW() + INTERVAL 30 SECOND
WHERE job_name = 'job-A' AND leader_id = 'host-1';

📌 简单可靠，但有 DB 性能瓶颈
   适合：低频选举（分钟级）
```

## 5. 关键问题

### 5.1 脑裂（Split Brain）

```
场景：
  1. Leader A 和 Follower B C 网络分区
  2. A 以为自己是 Leader，继续写
  3. B C 选新 Leader D
  4. A 和 D 同时写 → 数据不一致

防脑裂：
  1. Quorum 原则：写需要多数派确认
     - 5 节点需要 3 个 ACK
     - 分区后少数派自动放弃领导权

  2. Fencing token：
     - Leader 选举时拿单调递增 ID
     - 写资源时检查 token，旧 token 拒绝
     - 即使双 Leader，旧 Leader 写不进去

  3. STONITH（Shoot The Other Node In The Head）：
     - 检测到脑裂，强制关闭旧 Leader
     - Pacemaker 集群用此方案
```

### 5.2 选举风暴

```
场景：
  - 集群规模大，频繁 Leader 切换
  - 每次选举广播给所有节点
  - 网络压力 + 业务暂停

优化：
  1. 预选举（Pre-Vote）：
     - 先试投票，不自增 term
     - 避免无效 term 增长

  2. 优先级选举：
     - 资源充足的节点优先（CPU/内存/网络）
     - 减少无效选举

  3. Leader 租约：
     - Leader 续租期内不发起新选举
     - 减少 split vote
```

### 5.3 Leader 负载

```
Leader 瓶颈：
  - 写请求全经过 Leader（顺序写）
  - 单点性能受限

优化：
  1. 分片（Sharding）：
     - 多个 Leader，各管一片
     - Kafka Partition Leader

  2. Follower 读：
     - 读可以走 Follower（线性一致性除外）
     - etcd readIndex / lease read

  3. 状态机外置：
     - Leader 只负责协调
     - 数据存共享存储
```

## 6. 典型应用

### 6.1 HDFS NameNode HA

```
架构：
  - Active NameNode（主）
  - Standby NameNode（备）
  - ZKFC（ZKFailoverController）

切换：
  1. Active 挂掉
  2. ZKFC 检测心跳丢失
  3. ZK 选举 Standby 为新 Active
  4. 共享存储同步 edit log
  5. 新 Active 上线

📌 防脑裂：Fencing 强制 kill 旧 Active
```

### 6.2 Kafka Controller

```
Kafka 集群：
  - 1 个 Controller（ZK 中选举）
  - 管理 partition leader 选举
  - KRaft 模式（Kafka 2.8+）已去 ZK

选举：
  - ZK 中第一个注册成功的 broker
  - KRaft：基于 Raft
```

### 6.3 Elasticsearch Master

```
ES 集群：
  - 多个 master-eligible 节点
  - 选举 1 个 active master
  - 维护集群状态

选举：
  - 基于最小集群状态版本
  - 多数派原则
  - 脑裂时通过 publish_timeout 检测
```

## 7. 经典面试题

### 7.1 设计 Leader 选举

```
Q：3 节点集群选 Leader
A：
  1. 基于 Raft 算法
  2. 节点启动都是 Follower
  3. 选举超时（随机 150-300ms）变 Candidate
  4. 自增 term，发 RequestVote
  5. 拿到多数票（2/3）→ Leader
  6. Leader 发心跳维持权威

追问：脑裂怎么防？
  - quorum：写需要多数派
  - 少数派自动让位
  - fencing token

追问：选举风暴？
  - 随机超时
  - 预选举
  - Leader 租约
```

### 7.2 选主 vs 选主+数据

```
Q：分布式存储选主
A：
  1. 基于 Raft
  2. 选主时同步日志
  3. 日志最新者优先（term 优先，相同时 index 优先）
  4. 新 Leader 把未提交的日志补完

追问：选主期间能不能服务？
  - 只读可以
  - 写必须等新 Leader 选出
  - 一般 1s 内完成
```

## 8. 一句话总结

```
📌 Leader 选举 = 唯一性 + 高可用 + 防脑裂
📌 算法：Raft（最主流） / Paxos（理论） / Zab（ZK）
📌 实现：ZK 临时节点 / etcd Lease / Redis SETNX / DB 唯一索引
📌 脑裂防护：Quorum + Fencing token + STONITH
📌 选举风暴优化：随机超时 + 预选举 + 租约
📌 Leader 负载优化：分片 + Follower 读 + 状态机外置
📌 典型应用：HDFS HA / Kafka Controller / ES Master
```

## 9. 参考资料

- Raft 论文 (Diego Ongaro, 2014)
- Paxos Made Simple (Lamport, 2001)
- ZAB 协议论文
- etcd Raft 实现
- Curator LeaderLatch 文档
- "Consensus: Bridging Theory and Practice" (Diego Ongaro PhD)
