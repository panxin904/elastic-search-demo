---
title: Quorum 多数派
---
# Quorum / 多数派

## 1. 核心公式

N 副本集群，写操作需 W 个节点确认，读操作需 R 个节点响应。

**强一致性要求：W + R > N**

```
N=3, W=2, R=2: 2+2=4 > 3 ✅ 强一致
N=5, W=3, R=3: 3+3=6 > 5 ✅ 强一致
N=3, W=2, R=1: 2+1=3 = 3 ❌ 可能读不到最新
```

## 2. 常见配置

| 配置 | W | R | 写可用 | 读可用 | 一致性 |
|------|---|---|--------|--------|---------|
| 多数写 | N/2+1 | 1 | N/2 | N | 强 |
| 多数读 | 1 | N/2+1 | N | N/2 | 强 |
| 全写全读 | N | N | 0（节点全活） | 0 | 强 |
| Quorum 写读 | N/2+1 | N/2+1 | N/2 | N/2 | 强 |

## 3. NWR 与可用性

```
N=3, W=R=2: 容忍 1 节点故障（N-W = 1）
N=5, W=R=3: 容忍 2 节点故障
N=5, W=R=2: 容忍 1 节点（更慢，弱一致）
```

**经典选型**：N=3, W=R=2 是分布式系统的"甜蜜点"。

## 4. CAP 与 NWR 关系

```
P (分区): N 节点分裂成两派
C (一致): W 写入要求多数派 → 少数派不可写
A (可用): R 读取要求多数派 → 少数派不可读

CP: 少数派不可写不可读（牺牲可用性）
AP: 少数派可写（last-write-wins）+ 可读
```

## 5. 实战：Cassandra / Dynamo

```
N=3, W=2, R=2: 强一致读
N=3, W=1, R=1: 高吞吐，最终一致（默认）
N=3, W=3, R=1: 写极慢，读快（适合分析查询）
N=3, W=1, R=3: 写快，读慢（适合 OLTP）
```

Dynamo 让客户端选择 W/R 配置，**调一致性 vs 性能**。

## 6. Quorum 故障

N=3 集群挂 2 个节点 → 无法形成 quorum → 整个集群不可写。

**解决**：
- 加节点到 5 个（容忍 2 节点故障）
- 异地多活 + Paxos / Raft
- 自动故障转移

## 7. 实战：Raft + Quorum

Raft 选举要求**多数派**投票通过：
- 5 节点：3 票通过 → 容忍 2 节点故障
- 3 节点：2 票通过 → 容忍 1 节点故障
- 1 节点：1 票通过 → 不能容错（仅适合开发）

## 8. 实战：etcd 配置

```bash
# 3 节点 etcd cluster
--initial-cluster=etcd1=https://etcd1:2380,etcd2=https://etcd2:2380,etcd3=https://etcd3:2380
--initial-cluster-token=etcd-cluster-1
--initial-cluster-state=new

# 写 quorum = 2，读 quorum = 2
# 容忍 1 节点故障
```

## 9. Quorum 在微服务中的角色

- **etcd**：k8s 集群状态 = Raft + Quorum
- **Kafka**：controller quorum（KRaft 模式）
- **Redis Sentinel / Cluster**：leader 选举 + failover
- **服务发现**：consul / etcd 集群

## 10. 实战建议

```yaml
# 副本数选择：
N=3:  小团队 / 内部系统（推荐起步）
N=5:  生产关键系统（容忍 2 节点故障）
N=7:  金融级（容忍 3 节点故障，但写延迟高）

# W/R 选择：
  OLTP（强一致）:  W=2 R=2 in N=3
  分析查询（弱一致）:  W=1 R=1
  混合:  quorum 写 + local 读
```

## 🔗 下一步
- [CAP 定理](/03-ha-theory/cap)
- [Raft 共识](/03-ha-theory/raft)
- [幂等性设计](/03-ha-theory/idempotency)
