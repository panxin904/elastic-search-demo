---
title: HDFS NameNode HA
date: 2026-08-15  # date-auto-injected
---
# HDFS NameNode HA

## 1. 为什么需要 HA

NameNode 单点故障 = 整个集群挂（无元数据 = 不可用）

## 2. QJM 方案（推荐）

```
  NameNode (Active)         NameNode (Standby)
       │                          │
       └──────────┬───────────────┘
                  ↓
        JournalNode 集群（奇数个，通常 3 个）
        - edit log 共享
        - 多数写成功 = 提交
```

**原理**：Active NN 写 edit log 到 JournalNode（多数副本成功才返回）。Standby NN 从 JournalNode 拉 edit log → 内存中重建元数据。

故障切换：
1. ZKFC 监控两个 NN 健康
2. Active NN 挂 → ZKFC 锁住旧 Active
3. 选 Standby NN → 升级为 Active
4. 从 JournalNode 拉最新 edit log
5. 接管服务（< 30 秒）

## 3. 关键配置

```xml
<property>
  <name>dfs.nameservices</name>
  <value>mycluster</value>
</property>
<property>
  <name>dfs.ha.namenodes.mycluster</name>
  <value>nn1,nn2</value>
</property>
<property>
  <name>dfs.namenode.rpc-address.mycluster.nn1</name>
  <value>nn1.example.com:8020</value>
</property>
<property>
  <name>dfs.namenode.shared.edits.dir</name>
  <value>qjournal://nn1.example.com:8485;nn2.example.com:8485;jn1.example.com:8485/mycluster</value>
</property>
<property>
  <name>dfs.client.failover.proxy.provider.mycluster</name>
  <value>org.apache.hadoop.hdfs.server.namenode.ha.ConfiguredFailoverProxyProvider</value>
</property>
```

## 4. 故障切换流程

```
1. ZKFC 周期发送 RPC 给两个 NN
2. NN 挂 → 30 秒内无响应
3. ZKFC 对 Active NN 发起 fencing
   (fence NN：隔离，防止脑裂)
4. ZKFC 在 ZooKeeper 选主（ZK 临时节点）
5. Standby NN 升级为 Active
6. 新 Active NN 从 JournalNode 拉 edit log
7. 接管服务（< 1 分钟）
```

## 5. 实战：状态查询

```bash
hdfs haadmin -getServiceState nn1
# active 或 standby
hdfs haadmin -getServiceState nn2

# 强制切换（测试用）
hdfs haadmin -transitionToActive nn2 --forcemanual
hdfs haadmin -transitionToStandby nn1
```

## 6. 监控指标

| 指标 | 阈值 |
|------|------|
| NameNode GC 时间 | < 10% |
| 文件数 | < 1 亿（内存限制） |
| 块数 | < 2 亿 |
| JournalNode 同步延迟 | < 1 秒 |
| 故障切换时间 | < 30 秒 |

## 7. HDFS Federation（多集群）

```
/cluster1 (NameNode 1)
/cluster2 (NameNode 2)
/cluster3 (NameNode 3)
```

每 NameNode 管独立命名空间，Router 路由。
**适用**：超大数据量（10 亿+ 文件）。

## 8. 现代 HDFS 趋势

```
HDFS → 仍是大数据本地存储
但被挑战：
  - 对象存储（S3 / OSS）成本低 + 无限扩展
  - 云原生：S3A + HDFS 联邦
  - Lakehouse：Iceberg / Delta 直接对 S3

HDFS 仍占：
  - 本地部署
  - 大数据生态核心（Hive / Spark 默认）
  - 强一致场景
```

## 9. 实战 checklist

- [ ] NameNode HA 已配置（QJM + ZKFC）
- [ ] Standby NN 至少 1 个（建议 2 个）
- [ ] JournalNode ≥ 3 个（奇数）
- [ ] ZooKeeper 集群（≥ 3 个）
- [ ] 监控：故障切换时间、JournalNode 同步、NN GC
- [ ] 定期演练切换

## 🔗 下一步
- [HDFS 架构](/02-hdfs/architecture)
- [副本机制](/02-hdfs/replication)
