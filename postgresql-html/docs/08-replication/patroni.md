---
title: Patroni 高可用
description: PostgreSQL 自动故障切换集群管理
---

# Patroni 高可用

> **TL;DR**：Patroni 是 PG 生态最成熟的**集群管理工具**，集成流复制 + etcd 分布式协调 + 自动故障切换。**生产级 PG HA 的标准方案**：Patroni + etcd + HAProxy 三件套。

## 一句话定义

```
Patroni = PG 集群的大脑
       = 流复制管理者 + 自动故障切换 + 配置管理 + REST API
```

## 为什么需要 Patroni

裸 PG 流复制只能手工切换，问题是：

```
❌ 主库挂了 → 人工介入 → 切从库 → 改应用连接 → 业务中断 5-30 分钟
✅ 主库挂了 → Patroni 30s 内自动切换 → 应用透明
```

**生产级 HA 三件套**：

```
Patroni   ←→  etcd 协调    ←→  HAProxy/VIP
(每个 PG 节点)        (3-5 节点)         (应用入口)
   │                       │                     │
   └─ 流复制主从 ─────────┘                     │
                                                │
                                         应用连接这里
```

## 架构组件

| 组件 | 角色 | 部署 |
|---|---|---|
| **PostgreSQL** | 数据存储 | 每节点 1 个 PG 实例 |
| **Patroni** | PG 集群管理 | 每节点 1 个 Patroni 守护进程 |
| **etcd / ZooKeeper / Consul** | 分布式协调 | 3-5 节点集群 |
| **HAProxy / VIP** | 流量入口 | 2 个 HAProxy（HA） |
| **PgBouncer** | 连接池（可选） | 每节点 1 个 |

## 部署实战

### 1. 准备 etcd 集群

```bash
# 3 节点 etcd
etcd --name etcd1 \
  --initial-advertise-peer-urls http://10.0.0.1:2380 \
  --listen-peer-urls http://10.0.0.1:2380 \
  --listen-client-urls http://10.0.0.1:2379 \
  --advertise-client-urls http://10.0.0.1:2379 \
  --initial-cluster etcd1=http://10.0.0.1:2380,etcd2=http://10.0.0.2:2380,etcd3=http://10.0.0.3:2380 \
  --initial-cluster-token my-etcd-cluster
```

### 2. Patroni 配置

```yaml
# /etc/patroni.yml
scope: pg-cluster-01
name: ${HOSTNAME}

restapi:
  listen: 0.0.0.0:8008
  connect_address: 10.0.0.1:8008

etcd:
  host: 10.0.0.1:2379,10.0.0.2:2379,10.0.0.3:2379

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576      # 1MB
    postgresql:
      use_pg_rewind: true
      use_slots: true
      parameters:
        wal_level: replica
        max_wal_senders: 10
        max_replication_slots: 10
        wal_keep_size: 1GB
        hot_standby: on

postgresql:
  listen: 0.0.0.0:5432
  connect_address: 10.0.0.1:5432
  data_dir: /var/lib/postgresql/15/main
  bin_dir: /usr/lib/postgresql/15/bin
  pgpass: /tmp/pgpass0
  authentication:
    superuser:
      username: postgres
      password: ${POSTGRES_PASSWORD}
    replication:
      username: replicator
      password: ${REPLICATOR_PASSWORD}
    rewind:
      username: postgres
      password: ${POSTGRES_PASSWORD}

tags:
  nofailover: false
  noloadbalance: false
  clonefrom: false
  nosync: false
```

### 3. 启动 Patroni

```bash
# 第一个节点初始化
patroni /etc/patroni.yml

# 其他节点（自动加入集群）
patroni /etc/patroni.yml
```

### 4. HAProxy 入口

```haproxy
# /etc/haproxy/haproxy.cfg
listen pg-primary
    bind *:5000
    option httpchk GET /primary
    http-check expect status 200
    default-server inter 3s fall 3 rise 2 on-marked-down shutdown-sessions
    server pg1 10.0.0.1:5432 check port 8008
    server pg2 10.0.0.2:5432 check port 8008
    server pg3 10.0.0.3:5432 check port 8008

listen pg-replica
    bind *:5001
    balance roundrobin
    option httpchk GET /replica
    http-check expect status 200
    default-server inter 3s fall 3 rise 2
    server pg1 10.0.0.1:5432 check port 8008
    server pg2 10.0.0.2:5432 check port 8008
    server pg3 10.0.0.3:5432 check port 8008

listen pg-api
    bind *:8008
    http-request use-service prometheus-exporter if { path /metrics }
```

**HAProxy 健康检查通过 Patroni REST API**：

```bash
# 检查当前主
curl http://10.0.0.1:8008/primary
# 返回 200 = 是主
# 返回 503 = 不是主

# 检查是否可作从库
curl http://10.0.0.1:8008/replica
# 返回 200 = 是从库或可提升的从库
```

### 5. 应用连接

```yaml
# 写流量
jdbc:postgresql://haproxy-vip:5000/mydb

# 读流量（负载均衡）
jdbc:postgresql://haproxy-vip:5001/mydb
```

## 故障切换流程

```
主库（pg1）故障
   ↓
Patroni 30s 内检测（loop_wait × 3）
   ↓
通过 etcd 选主（pg2 或 pg3）
   ↓
Patroni 在新主上跑 pg_ctl promote
   ↓
老主库 pg1 自动 pg_rewind，重新加入集群作从库
   ↓
HAProxy 5000 端口自动指向新主（通过 /primary 检查）
   ↓
应用连接恢复（30-60s 内）
```

**关键参数**：

```yaml
# 故障检测时间
loop_wait: 10                  # 每 10s 检查一次
retry_timeout: 10              # 重试 10s
ttl: 30                        # 30s 没心跳就认为挂

# 切换策略
maximum_lag_on_failover: 1048576  # 延迟 > 1MB 的从库不能作主
master_start_timeout: 300      # 提升等待 300s
```

## 手动运维

### 查看集群状态

```bash
# Patroni REST API
curl http://10.0.0.1:8008/cluster

# 返回 JSON：
{
  "members": [
    { "name": "pg1", "role": "primary", "state": "running", ... },
    { "name": "pg2", "role": "replica", "state": "running", ... },
    { "name": "pg3", "role": "replica", "state": "running", ... }
  ]
}

# Patroni CLI
patronictl -c /etc/patroni.yml list
```

### 手动切换主

```bash
# 1. 优雅切换（推荐）
patronictl -c /etc/patroni.yml switchover
# 选择目标主（pg2）

# 2. 强制切换（故障场景）
patronictl -c /etc/patroni.yml failover --master pg1 --candidate pg2
```

### 暂停 Patroni 维护

```bash
# 暂停自动 failover
patronictl -c /etc/patroni.yml pause

# 恢复
patronictl -c /etc/patroni.yml resume
```

## 监控

### Patroni 指标

```bash
# /metrics 端点（Prometheus）
curl http://10.0.0.1:8008/metrics

# 关键指标：
# patroni_cluster_members
# patroni_postgres_running
# patroni_postgres_replica_lag
# patroni_standby_leader_frequency
```

### 告警规则（Prometheus）

```yaml
groups:
- name: patroni
  rules:
  - alert: PatroniNoPrimary
    expr: patroni_cluster_members{role="primary"} == 0
    for: 30s
    labels:
      severity: page
    annotations:
      summary: "PG 集群无主节点"

  - alert: PatroniReplicaLag
    expr: patroni_postgres_replica_lag > 1048576  # 1MB
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "PG 从库延迟 > 1MB"

  - alert: PatroniClusterSplit
    expr: count(patroni_cluster_members{role="primary"}) > 1
    for: 0m
    labels:
      severity: page
    annotations:
      summary: "PG 集群脑裂！多个主节点"
```

## 实战案例

### 案例 1：电商 PG 集群

```
3 节点 PG（pg1, pg2, pg3）
3 节点 etcd
2 节点 HAProxy（VIP 漂移）
1 个 VIP（10.0.0.100）— 应用统一连接这里
```

**容量**：支撑 5000 QPS 写 + 20000 QPS 读。

### 案例 2：异地容灾

```
DC1 (同城)：Patroni 集群（3 节点 + 3 etcd）
DC2 (异地)：Patroni Standby Cluster（只读副本）
        │
   archive_mode + archive_command 传 WAL 到 DC2
```

## 常见错误

### 错误 1：etcd 集群脑裂

**症状**：两个主节点，集群分裂。

**原因**：etcd 节点少于 3 个时网络分区会导致。

**修复**：
- etcd 至少 3 节点（推荐 5 节点）
- Patroni 配置 `maximum_lag_on_failover` 防误判
- 监控 `patroni_cluster_split` 告警

### 错误 2：切换后老主无法加入

**症状**：老主 pg_rewind 失败。

**原因**：时间线分歧太大。

**修复**：
```bash
# 手工 pg_rewind
pg_rewind --target-pgdata=/var/lib/postgresql/15/main \
  --source-server="host=new-primary port=5432 user=postgres"

# 或者重新 basebackup
rm -rf /var/lib/postgresql/15/main
pg_basebackup -h new-primary -D /var/lib/postgresql/15/main -U replicator -P
```

### 错误 3：从库延迟爆炸

**症状**：`patroni_postgres_replica_lag` 飙到 GB 级。

**原因**：
- 主库大事务（单事务 100GB WAL）
- 主库 long-running 2PC 事务

**修复**：
```sql
-- 1. 找到慢查询
SELECT pid, query_start, state, query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY xact_start;

-- 2. 必要时 kill
SELECT pg_cancel_backend(pid);
-- 或强制终止
SELECT pg_terminate_backend(pid);
```

## 一句话总结

> **Patroni + etcd + HAProxy = PG 高可用标准方案**。30-60s 自动故障切换，应用无感知。**etcd 必须 ≥3 节点、Patroni 必须用 pg_rewind、HAProxy 必须 ≥2 节点**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>


<!-- auto-enrich:do-not-edit -->

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

- [mysql](https://java-px.bot.cd/mysql/):MySQL 对比
- [clickhouse](https://java-px.bot.cd/clickhouse/):ClickHouse OLAP
- [system-design](https://java-px.bot.cd/system-design/):数据库选型
