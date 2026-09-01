---
title: 流复制 Streaming Replication
date: 2026-08-15  # date-auto-injected
description: PostgreSQL 主从复制核心机制
---

![PostgreSQL 复制架构](/postgresql-replication-flow.svg)

# 流复制 Streaming Replication

> **TL;DR**：PG 流复制 = **WAL 日志从主库实时传到从库**，从库 replay WAL 保持与主库一致。**生产高可用 / 读写分离 / 异地容灾**都靠它。**核心是 synchronous_commit 参数**决定数据安全与性能的取舍。

## 一句话定义

```
流复制 = 基于 WAL 的物理复制，主库产生的 WAL 实时（或异步）传送到从库
```

## 三种复制模式对比

| 模式 | 同步性 | 数据安全 | 性能影响 | 适用场景 |
|---|---|---|---|---|
| **异步** | 不等从库确认 | 可能丢数据 | 最快 | 95% 场景 |
| **同步** | 等至少 1 个从库确认 | 不丢数据 | 慢 1 个 RTT | 金融 |
| **同步优先** | 等同步从库，否则回滚 | 强一致 | 取决于延迟 | 数据一致性要求极高 |

```ini
# postgresql.conf
synchronous_commit = off       # 异步
synchronous_commit = local     # 仅本地 fsync
synchronous_commit = on        # 等同步从库
synchronous_commit = remote_write  # 等远程 write（不 fsync）
synchronous_commit = apply     # 等远程 apply（PG 13+，最安全）
```

## 异步复制架构

```
                     ┌──────────────┐
   写请求 ────────────→ │  Primary    │
                     │              │
                     │  生成 WAL    │
                     └──────┬───────┘
                            │ TCP 流式传送（默认异步）
                            ↓
                     ┌──────────────┐
                     │  Standby    │
                     │              │
                     │  replay WAL  │
                     └──────────────┘
```

**配置**：

```ini
# 主库
wal_level = replica
max_wal_senders = 5           # 最多 5 个从库
wal_keep_size = 1GB            # 保留 WAL 1GB（防从库断连）

# 从库
primary_conninfo = 'host=primary port=5432 user=replicator password=xxx'
hot_standby = on
```

```bash
# 从库：用 pg_basebackup 初始化
pg_basebackup -h primary -D /var/lib/postgresql/data -U replicator -P -Xs -c fast

# 然后创建 standby.signal 文件
touch /var/lib/postgresql/data/standby.signal

# 启动从库
pg_ctl start
```

## 同步复制架构

```
                     ┌──────────────┐
   写请求 ────────────→ │  Primary    │
                     │              │
                     │  生成 WAL    │
                     │  等待 ACK ←─┐│
                     └──────┬──────┘│
                            │      │
                            ↓      │
                     ┌──────────────┐
                     │  Standby 1  │ ── 同步从库（必须 ACK）
                     │              │
                     │  replay WAL  │
                     └──────────────┘

                     ┌──────────────┐
                     │  Standby 2  │ ── 异步从库（可选）
                     └──────────────┘
```

**配置**：

```ini
# 主库
synchronous_standby_names = 'standby1'  # 等 standby1 确认
# 或 PG 10+：优先级
synchronous_standby_names = 'FIRST 1 (standby1, standby2)'  # 1 个同步
synchronous_standby_names = 'ANY 2 (standby1, standby2, standby3)'  # 2 个同步
```

**同步复制的代价**：

```
RTT = 5ms（同城）
RTT = 30ms（同城跨机房）
RTT = 100ms+（跨城）

每个事务多等 1 个 RTT → 写入 p99 延迟 = RTT + 业务延迟
```

> **生产经验**：同步复制只在同城（同机房或同城双中心）用，跨城必须用异步。

## WAL 传送机制

### 三种传送方式

```ini
# 1. 异步流式（默认）
# 主库发送 WAL 后不等 ACK，性能最高

# 2. 同步流式
# 主库发送 WAL 后等 ACK

# 3. 异步 + archive
# 主库 archive 到 NFS/S3，从库定期取
# 适用于断网恢复场景
```

### WAL 保留策略

```ini
# 主库
wal_keep_size = 1GB         # 保留 1GB WAL（防从库落后太多）
max_wal_size = 2GB          # checkpoint 后最大 WAL

# 或用 archive（更可靠）
archive_mode = on
archive_command = 'cp %p /archive/%f'
```

### 监控复制延迟

```sql
-- 主库：看每个从库的延迟
SELECT
  client_addr,
  state,
  sync_state,                       -- async / sync / potential
  sent_lsn - replay_lsn AS byte_lag,
  EXTRACT(EPOCH FROM now() - reply_time) AS seconds_lag
FROM pg_stat_replication;

-- 从库：自己的 replay 进度
SELECT
  pg_last_wal_receive_lsn(),
  pg_last_wal_replay_lsn(),
  pg_last_xact_replay_timestamp();
```

**告警阈值**：
```
字节延迟 > 100MB → 黄色
字节延迟 > 1GB → 红色
时间延迟 > 60s → 黄色
时间延迟 > 600s → 红色
```

## 实战部署

### 1. 同城主从（异步）

```bash
# 主库 postgresql.conf
wal_level = replica
max_wal_senders = 10
wal_keep_size = '2GB'
hot_standby = on
archive_mode = on
archive_command = '/bin/cp %p /archive/%f'

# 主库 pg_hba.conf
host replication replicator 10.0.0.0/24 scram-sha-256

# 创建复制用户
psql -c "CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'xxx';"

# 从库初始化
pg_basebackup -h primary.db -D /data -U replicator -P -Xs -c fast

# 从库 standby.signal
echo "" > /data/standby.signal
cat >> /data/postgresql.conf <<EOF
primary_conninfo = 'host=primary.db port=5432 user=replicator password=xxx'
hot_standby = on
EOF

# 启动
pg_ctl start -D /data
```

### 2. 同城双活（同步复制）

```ini
# 主库
synchronous_standby_names = 'FIRST 1 (standby_dr)'
synchronous_commit = on

# 从库（DC2）
primary_conninfo = 'host=primary-dc1.db ...'
hot_standby = on
```

### 3. 异地异步（容灾）

```ini
# 异地从库（DC3，RTT=50ms）
primary_conninfo = 'host=primary-dc1.db ...'
hot_standby = on
# 不用同步
```

## 复制与故障切换

### 手动切换

```bash
# 1. 主库降级
psql -c "SELECT pg_promote();"
# 或 pg_ctl promote -D /data

# 2. 老主库变从库（重新指向新主）
# 修改 primary_conninfo，重启

# 3. 应用切流（修改连接串或 DNS / VIP 漂移）
```

### 自动切换：Patroni

**Patroni** = PG 集群管理工具，集成流复制 + 自动故障切换 + etcd 协调。

```yaml
# patroni.yml
scope: mycluster
name: pg-node1

restapi:
  listen: 0.0.0.0:8008

etcd:
  host: 10.0.0.1:2379

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    maximum_lag_on_failover: 1048576  # 1MB
    postgresql:
      use_pg_rewind: true
      parameters:
        wal_level: replica
        max_wal_senders: 10
        wal_keep_size: 1GB

postgresql:
  listen: 0.0.0.0:5432
  data_dir: /var/lib/postgresql/data
  authentication:
    superuser:
      username: postgres
      password: xxx
    replication:
      username: replicator
      password: xxx
```

**Patroni 故障切换流程**：

```
主库故障
   ↓
Patroni 检测（10s loop_wait）
   ↓
通过 etcd 选主
   ↓
pg_ctl promote 新主
   ↓
老主库自动 pg_rewind，重新加入集群作从库
   ↓
应用层通过 HAProxy / VIP 感知新主
```

## 读写分离

### 应用层分流

```
写请求 → PgBouncer (6432) → 主库
读请求 → PgBouncer (6432) → 从库（多个）
```

**Java 配置**：

```yaml
spring:
  datasource:
    write:
      url: jdbc:postgresql://primary.db:6432/mydb
    read:
      url: jdbc:postgresql://standby.db:6432/mydb
```

### 中间件分流

```
应用 → ShardingSphere / MaxScale → 主库 / 从库
```

**ShardingSphere 配置**：

```yaml
rules:
- !READWRITE_SPLITTING
  dataSources:
    write_ds:
      writeDataSourceName: write_ds
      readDataSourceNames:
        - read_ds_1
        - read_ds_2
      loadBalancerName: random
  loadBalancers:
    random:
      type: RANDOM
```

## 常见错误

### 错误 1：主从数据不一致

**现象**：从库查询结果与主库不一致。

**原因**：
- 从库 replay 滞后
- 主库有 long-running 事务（影响 vacuum）
- synchronous_commit = off 导致主库"提前"返回，从库还没收到

### 错误 2：WAL 撑爆磁盘

**现象**：主库磁盘满。

**修复**：
```ini
# 控制 WAL 增长
max_wal_size = 2GB              # checkpoint 后最大
wal_keep_size = '1GB'           # 保留
wal_compression = on            # 压缩
```

### 错误 3：从库延迟过大

**监控**：
```sql
SELECT sent_lsn - replay_lsn FROM pg_stat_replication;
```

**修复**：
- 增加网络带宽
- 拆分大事务（避免单事务 10GB WAL）
- 从库加大 `wal_receiver_timeout`

## 一句话总结

> **流复制 = PG HA 的基石**：异步覆盖 95% 场景，同步用于金融级数据安全，异地用异步容灾。**Patroni + etcd + HAProxy = 生产级自动故障切换**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [mysql](https://java-px.bot.cd/mysql/):MySQL 对比
- [clickhouse](https://java-px.bot.cd/clickhouse/):ClickHouse OLAP
- [system-design](https://java-px.bot.cd/system-design/):数据库选型
