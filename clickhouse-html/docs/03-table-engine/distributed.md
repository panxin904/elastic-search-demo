---
title: Distributed 表引擎
date: 2026-08-15  # date-auto-injected
description: 多分片集群查询 / 写入的核心：本地表 + 分布式表 scatter-gather 模型
---

# Distributed 表引擎

Distributed 表是 ClickHouse 集群查询的入口，本身不存储数据，是「本地表的代理」。

## 基础模型

```text
┌─────────────────────────┐
│  Distributed 表         │  不存数据，只路由
│  events_distributed     │
└─────────────────────────┘
         │
         │ SELECT → scatter 到所有分片
         │ INSERT → hash 到目标分片
         │
   ┌─────┴─────┬─────┴─────┬─────┴─────┐
   ▼           ▼           ▼           ▼
┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐
│本地表 │  │本地表 │  │本地表 │  │本地表 │
│shard1 │  │shard2 │  │shard3 │  │shard4 │
└───────┘  └───────┘  └───────┘  └───────┘
   A,B副本    A,B副本    A,B副本    A,B副本
```

## 创建 Distributed 表

### 1. 集群配置

在 `/etc/clickhouse-server/config.xml` 中定义：

```xml
<remote_servers>
    <my_cluster>
        <shard>
            <internal_replication>true</internal_replication>
            <replica>
                <host>shard1-replica1</host>
                <port>9000</port>
            </replica>
            <replica>
                <host>shard1-replica2</host>
                <port>9000</port>
            </replica>
        </shard>
        <shard>
            <replica>
                <host>shard2-replica1</host>
                <port>9000</port>
            </replica>
            <replica>
                <host>shard2-replica2</host>
                <port>9000</port>
            </replica>
        </shard>
    </my_cluster>
</remote_servers>
```

### 2. 在每台机器创建本地表

```sql
-- 在每个节点都执行
CREATE TABLE events_local (
  event_time DateTime,
  user_id UInt64,
  event_type LowCardinality(String)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (user_id, event_time)
```

### 3. 创建 Distributed 表（在每个节点）

```sql
-- 在每个节点都执行
CREATE TABLE events_distributed (
  event_time DateTime,
  user_id UInt64,
  event_type LowCardinality(String)
)
ENGINE = Distributed(my_cluster, default, events_local, rand())
```

**参数说明**：
- `my_cluster`：集群名（对应 config.xml）
- `default`：数据库名
- `events_local`：本地表名
- `rand()`：分片键（决定数据落到哪个分片）

## 分片键选择

```sql
-- 1. 随机（最简单）
ENGINE = Distributed(cluster, db, local, rand())

-- 2. 按用户 ID hash（同一用户始终在同一分片）
ENGINE = Distributed(cluster, db, local, cityHash64(user_id))

-- 3. 按月分片
ENGINE = Distributed(cluster, db, local, toYYYYMM(event_time))

-- 4. 自定义表达式
ENGINE = Distributed(cluster, db, local, intHash32(user_id) % 4)
```

**分片键决策**：

| 场景 | 推荐分片键 |
|---|---|
| 写入均匀 + 无 JOIN | `rand()` |
| 按用户聚合查询 | `cityHash64(user_id)` |
| 按时间范围查询 | `toYYYYMM(event_time)` |
| 多租户 | `cityHash64(tenant_id)` |

## 查询流程（SELECT）

```sql
-- 在任意节点查询，自动 scatter-gather
SELECT count() FROM events_distributed

-- 实际执行：
-- 1. 协调节点收到查询
-- 2. 同时发往所有分片
-- 3. 每个分片本地查询
-- 4. 协调节点 merge 结果
-- 5. 返回给客户端
```

## 写入流程（INSERT）

```sql
-- 通过 Distributed 表写入
INSERT INTO events_distributed VALUES (now(), 1, 'click')

-- 实际执行：
-- 1. 客户端连接节点 A
-- 2. 节点 A 根据分片键计算目标分片
-- 3. 转发到目标分片
-- 4. 目标分片写入本地表（同步副本）
-- 5. 返回成功
```

**性能提示**：
- Distributed 表写入有转发开销，**生产推荐直接写入本地表**
- 用 `insert_distributed_sync = 1` 等待所有副本确认

## 实战：本地表写入（推荐）

```bash
# 应用按 user_id mod 分片，写入对应节点
# 例如 user_id=12345, hash=12345 % 4 = 1, 写入 shard1

# 在 shard1 上执行
INSERT INTO events_local (event_time, user_id, event_type)
VALUES (now(), 12345, 'click')
```

```python
# Python 端：按 user_id 路由
import hashlib

def get_shard(user_id, num_shards=4):
    return hashlib.md5(str(user_id).encode()).hexdigest()[0] % num_shards

# 维护节点列表
SHARD_HOSTS = ['shard1:9000', 'shard2:9000', 'shard3:9000', 'shard4:9000']

# 写入对应节点
shard = get_shard(user_id)
client = clickhouse_connect.get_client(host=SHARD_HOSTS[shard])
client.insert('events_local', data)
```

## 实战：跨分片 JOIN

```sql
-- Distributed 表 + JOIN（本地表 JOIN）
SELECT
  e.event_id,
  u.user_name,
  u.country
FROM events_distributed e
JOIN users_distributed u ON e.user_id = u.id
WHERE e.event_date = '2024-01-01'

-- ⚠️ 跨分片 JOIN 性能差（需要在所有分片上 JOIN 后 merge）
-- 推荐：所有 JOIN 表用相同的分片键
```

## GLOBAL JOIN 优化

```sql
-- GLOBAL JOIN（每个分片都获取全量右表）
SELECT
  e.event_id,
  u.user_name
FROM events_distributed e
GLOBAL JOIN users_local u ON e.user_id = u.id
```

**注意**：`users_local` 必须复制到每个分片（如用 Distributed 表）。

## 副本与高可用

```sql
-- internal_replication = true 时
-- 写入第一个副本，自动同步到第二个副本
-- 任何副本故障时，从另一个副本读
```

## 监控

```sql
-- 查看集群拓扑
SELECT * FROM system.clusters FORMAT Vertical

-- 查看副本状态
SELECT * FROM system.replicas FORMAT Vertical

-- 查看分片数据分布
SELECT shard_num, count() FROM distributed_events
GROUP BY shard_num
```

## 常见问题

### Q1：Distributed 表能存数据吗？

不能。Distributed 表只是「逻辑视图」，必须指向本地表。

### Q2：写入 Distributed 表会丢数据吗？

如果 `internal_replication=true` 且第一个副本写入成功，会同步副本，不会丢。
如果 `internal_replication=false`，写入第一个副本后立即返回（不等副本），可能丢。

### Q3：如何扩容？

1. 添加新分片（config.xml）
2. 在新分片创建本地表
3. **手动 rebalance 数据**（用 `clickhouse-copier` 或迁移工具）

### Q4：副本同步延迟

```sql
-- 查看延迟
SELECT
  database,
  table,
  absolute_delay,
  last_queue_update
FROM system.replicas
ORDER BY absolute_delay DESC
```

## 下一步

- 学习物化视图：见 [materialized-view.md](./materialized-view.md)
