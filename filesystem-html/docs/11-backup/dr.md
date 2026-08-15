---
title: 容灾恢复
---

# 容灾与恢复 — 业务连续性核心

> <span class="kg-badge kg-badge--backup">备份快照</span>
> 同城双活 · 异地灾备 · RTO/RPO 决策树

容灾（Disaster Recovery）是业务在数据中心故障、自然灾害、人为错误下**持续运行**的能力。

## 1. 容灾分级

| 等级 | 描述 | RTO | RPO |
|------|------|-----|-----|
| Tier 0 | 单机房，无备份 | 不可恢复 | 全部丢 |
| Tier 1 | 异地冷备份（磁带） | 24h | 24h |
| Tier 2 | 异地温备份 | 4h | 1h |
| Tier 3 | 异地热备份 | 分钟级 | 秒级 |
| Tier 4 | 双活数据中心 | 0 | 0 |
| Tier 5 | 多活 + 自动化切换 | 0 | 0 |

## 2. RTO / RPO

- **RTO (Recovery Time Objective)**：灾难发生后多久恢复
- **RPO (Recovery Point Objective)**：允许丢失多少数据

```
RTO 0（业务不中断）
├── 多 AZ / 多活
├── 实时同步
└── 流量秒级切换

RTO 短（业务中断几分钟）
├── 异步复制
├── 自动化故障切换
└── 定期演练

RTO 长（业务可中断几小时）
├── 异地冷备份
├── 手动恢复
└── 季度演练
```

## 3. 容灾模式

### 3.1 主备模式（Active-Passive）

```
[主站]           [备站]
  - 在线业务       - 备份
  - 写入           - 待命
  
灾备切换：
  - 备站接管 IP
  - DNS 切流量
```

- RTO：分钟级（自动化）/ 小时级（手动）
- 资源浪费：备站空转

### 3.2 双活模式（Active-Active）

```
[站 A]  ◄────►  [站 B]
 在线业务         在线业务
（同时承担负载）

特点：
- 资源 100% 利用
- 一站挂 = 另一站扛全部
```

- RTO：秒级
- 资源浪费：0
- **复杂**：数据双向同步、流量调度

### 3.3 多活模式（Multi-Active）

```
[北京] ◄────► [上海] ◄────► [广州]
  - 分片 A        - 分片 B        - 分片 C
```

每个数据中心承担**部分用户**。灾备时其他机房接管。

## 4. 存储层容灾

### 4.1 同步复制（同步）

```
主写入 ─→ 备写入 ─→ 主确认
            │
            └─→ 备故障：主写入等待
```

- RPO = 0
- 延迟增加（双写距离）
- 不抗**同时**故障

### 4.2 异步复制（异步）

```
主写入 → 主确认 → 后台异步 → 备写入
```

- RPO = 秒级
- 性能不受异地距离影响
- 容**异地**故障

### 4.3 半同步复制

```
主写入 → 备写入确认 → 主确认
       ↘ 异步补充
```

- 至少一份备写入成功 → 主确认
- 平衡 RPO 与性能

## 5. 实战：数据库容灾

### 5.1 MySQL Group Replication / Galera

```ini
[mysqld]
wsrep_cluster_address="gcomm://node1,node2,node3"
wsrep_provider=/usr/lib/galera/libgalera_smm.so
wsrep_node_address=node1
wsrep_node_name=node1
wsrep_sst_method=rsync
wsrep_slave_threads=4
```

- 多主
- 同步复制
- 冲突检测

### 5.2 PostgreSQL Streaming Replication

```ini
# 主
wal_level = replica
archive_mode = on
archive_command = 'cp %p /backup/wal/%f'

# 备
primary_slot_name = 'replica_slot'
hot_standby = on
```

- 物理流复制
- 异步 / 同步可选
- 读写分离

### 5.3 Redis Sentinel / Cluster

```yaml
# Sentinel 模式
sentinel monitor mymaster 127.0.0.1 6379 2
sentinel down-after-milliseconds mymaster 5000
sentinel failover-timeout mymaster 60000
```

- 自动故障检测
- 主从切换

## 6. 实战：对象存储容灾

### 6.1 同城多 AZ

```bash
# 阿里云 OSS 北京
bucket: my-data
region: cn-beijing
多 AZ 副本（默认）
```

### 6.2 跨区域复制

```bash
# OSS CRR
ossutil set-bucket-crr oss://src-bucket crr-config.json
# 异步复制到上海
```

### 6.3 自建（Ceph / MinIO）

```bash
# MinIO
mc replicate add local/src remote/dst
mc replicate status local/src
```

## 7. 实战：K8s 容灾

### 7.1 多集群

```yaml
# ArgoCD Multi-cluster
clusters:
  - name: cluster-a
    server: https://a.example.com:6443
  - name: cluster-b
    server: https://b.example.com:6443
```

### 7.2 Velero 跨集群恢复

```bash
# 备份集群 A
velero backup create cluster-a-backup --include-namespaces=prod

# 在集群 B 恢复
velero restore create --from-backup cluster-a-backup
```

### 7.3 应用层 DR

```yaml
# PodDisruptionBudget
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: web
```

## 8. 流量切换

### 8.1 DNS 切流

```bash
# TTL 必须很短（如 60 秒）
www.example.com  A  1.2.3.4   # 主
                A  5.6.7.8   # 备
```

切换时改 DNS → 60 秒后生效。

### 8.2 Anycast IP

云厂商提供 Anycast IP，多机房共享 IP，路由自动故障切换。

### 8.3 Layer 4/7 LB

云厂商 LB（ALB / CLB）+ 健康检查 → 故障自动摘除。

## 9. 恢复演练

**这是关键**：

```text
[ ] 季度切换演练（主 → 备）
[ ] 半年异地切换演练
[ ] 一年全链路恢复演练
[ ] 恢复时间实测
[ ] 业务验证
[ ] 数据校验
[ ] 改进（缩短 RTO）
```

## 10. 监控容灾指标

```promql
# RTO 指标：故障 → 恢复时间
# RPO 指标：上次同步时间
backup_last_success_timestamp{cluster="prod"} > time() - 3600

# 副本延迟
replication_lag_seconds{cluster="prod-replica"} < 10

# 自动告警
- alert: ReplicaLagHigh
  expr: replication_lag_seconds > 60
- alert: BackupFailed
  expr: increase(backup_failures_total[1h]) > 0
```

## 11. 实战 checklist

```text
[ ] 业务 RTO / RPO 目标
[ ] 容灾等级（Tier）
[ ] 主备还是双活
[ ] 同步 vs 异步
[ ] 存储容灾策略
[ ] 数据库容灾策略
[ ] 应用多活策略
[ ] DNS / 流量切换
[ ] 监控告警
[ ] 文档化
[ ] 季度演练
```

## 12. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| RTO = 恢复时间 | "RTO=时" |
| RPO = 数据丢失 | "RPO=数" |
| 双活 0 / 0 | "双活=零丢失" |
| 异步异地 | "异步=异地" |
| 演练必做 | "演练=验证" |

## 参考

- NIST SP 800-34
- 《Site Reliability Engineering》 Google
- 云厂商容灾白皮书（AWS / Azure / 阿里云）