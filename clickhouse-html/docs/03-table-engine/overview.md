---
title: 表引擎总览
---

# ClickHouse 表引擎

**ClickHouse 表引擎 = 数据如何存储 + 索引 + 复制**——选错引擎性能差 100x。

## 一句话总结

> **表引擎 = 数据生命周期**。**MergeTree 家族是 99% 场景的选择**。**Kafka/Distributed/MaterializedView 是生态基础**。

---

## 一、表引擎选型决策树

```
需要写时合并？├─ 是 → ReplacingMergeTree（去重）
              ├─ 是 → AggregatingMergeTree（预聚合）
              ├─ 是 → CollapsingMergeTree（折叠相反状态）
              └─ 否 → MergeTree（基础）
                       │
需要分布式？├─ 是 → Distributed（本地表 + 分布式表）
              └─ 否 → MergeTree 系列
                       │
需要流式？├─ 是 → Kafka engine（直接消费）
              ├─ 是 → MaterializedView（自动维护）
              └─ 否 → 普通表
                       │
是临时/中间？├─ 是 → Memory（内存）/ Log（不索引）
              └─ 否 → MergeTree 系列
```

## 二、MergeTree 家族

### 1. MergeTree（基础）

```sql
CREATE TABLE events (
    date Date,
    event_type LowCardinality(String),
    user_id UInt64,
    amount Decimal(10, 2)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)              -- 按月分区
ORDER BY (date, event_type, user_id)     -- 排序键
PRIMARY KEY (date, event_type)           -- 主键（默认等于 ORDER BY 前缀）
SETTINGS index_granularity = 8192;       -- 索引粒度
```

**关键概念**：
- **PARTITION BY**：目录分区（`202608/`, `202609/`），删除时 DROP PARTITION 秒级
- **ORDER BY**：排序键，决定稀疏索引
- **PRIMARY KEY**：默认 ORDER BY 前缀，可不同（如 `PRIMARY KEY user_id, ORDER BY (date, user_id)`）
- **SETTINGS.index_granularity**：默认 8192，索引粒度

### 2. ReplacingMergeTree（去重）

```sql
CREATE TABLE events (
    date Date,
    user_id UInt64,
    event String,
    version UInt64
)
ENGINE = ReplacingMergeTree(version)
PARTITION BY date
ORDER BY (date, user_id);

-- 插入
INSERT INTO events VALUES
('2026-08-11', 1, 'click', 1),
('2026-08-11', 1, 'view', 2);  -- 同 (date, user_id) 不同 version
-- 后台合并：保留 version 最大的
```

**应用**：用户属性表、订单状态表、CDC 数据。

### 3. AggregatingMergeTree（预聚合）

```sql
CREATE TABLE daily_stats (
    date Date,
    event_type LowCardinality(String),
    -- 状态列
    uv AggregateFunction(uniq, UInt64),
    pv AggregateFunction(sum, UInt64),
    amount AggregateFunction(sum, Decimal(10, 2))
)
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (date, event_type);

-- 插入（用 -State 函数）
INSERT INTO daily_stats SELECT
    date,
    event_type,
    uniqState(user_id),
    sumState(1),
    sumState(amount)
FROM events
GROUP BY date, event_type;

-- 查询（用 -Merge 函数）
SELECT
    date,
    event_type,
    uniqMerge(uv) AS uv,
    sumMerge(pv) AS pv,
    sumMerge(amount) AS amount
FROM daily_stats
GROUP BY date, event_type;
```

**应用**：实时数仓指标层（UV / PV / GMV）。

### 4. CollapsingMergeTree（折叠相反状态）

```sql
CREATE TABLE orders (
    date Date,
    order_id UInt64,
    status Int8,    -- 1 = 正常, -1 = 取消
    amount Decimal(10, 2)
)
ENGINE = CollapsingMergeTree(status)
ORDER BY (date, order_id);

-- 正常下单
INSERT INTO orders VALUES ('2026-08-11', 100, 1, 99.00);
-- 取消订单（写 -1）
INSERT INTO orders VALUES ('2026-08-11', 100, -1, 99.00);
-- 后台合并：sum(status) = 0 → 折叠
```

**应用**：订单状态、状态机。

### 5. VersionedCollapsingMergeTree

```sql
CREATE TABLE orders_v (
    date Date,
    order_id UInt64,
    version UInt64,
    sign Int8,
    amount Decimal(10, 2)
)
ENGINE = VersionedCollapsingMergeTree(sign, version)
ORDER BY (date, order_id);
```

**比 CollapsingMergeTree 优势**：version 保证顺序，不依赖写入顺序。

## 三、Log 引擎族

### Memory（内存）

```sql
CREATE TABLE temp_metrics (
    ts DateTime,
    metric String,
    value Float64
) ENGINE = Memory;
```

**特点**：
- 数据在内存，重启丢失
- 极快（10x MergeTree）
- 用于临时 / 中间结果

### Log

```sql
CREATE TABLE logs (
    ts DateTime,
    level String,
    message String
) ENGINE = Log;
```

**特点**：
- 不支持索引 / ALTER
- 仅顺序写
- 适合只写不查的小表

### TinyLog / StripeLog

更小型的 Log，仅用于最简场景。

## 四、Kafka 引擎

```sql
CREATE TABLE kafka_events (
    date Date,
    user_id UInt64,
    event String
) ENGINE = Kafka()
SETTINGS
    kafka_broker_list = 'kafka:9092',
    kafka_topic_list = 'user_events',
    kafka_group_name = 'clickhouse_consumer',
    kafka_format = 'JSONEachRow',
    kafka_num_consumers = 1;

-- 查询（直接消费 Kafka 临时表）
SELECT * FROM kafka_events LIMIT 10;
```

**通常配合 MaterializedView**：

```sql
CREATE TABLE events (
    date Date,
    user_id UInt64,
    event String
) ENGINE = MergeTree()
ORDER BY (date, user_id);

CREATE MATERIALIZED VIEW kafka_mv TO events AS
SELECT
    toDate(parseDateTimeBestEffort(ts)) AS date,
    user_id,
    event
FROM kafka_events;
```

**应用**：实时数仓（Kafka → CH 秒级延迟）。

## 五、Distributed 表

```sql
-- 1. 在每个分片创建本地表
CREATE TABLE events_local ON CLUSTER cluster_3shards (
    date Date,
    user_id UInt64,
    event String
) ENGINE = MergeTree()
ORDER BY (date, user_id);

-- 2. 创建分布式表
CREATE TABLE events_distributed ON CLUSTER cluster_3shards (
    date Date,
    user_id UInt64,
    event String
) ENGINE = Distributed(cluster_3shards, db, events_local, rand());

-- 3. 写入分布式表
INSERT INTO events_distributed VALUES
('2026-08-11', 1, 'click'),
('2026-08-11', 2, 'view');

-- 4. 查询（自动 scatter-gather）
SELECT count() FROM events_distributed;
```

**关键概念**：
- **本地表**：实际存储，每个分片一份
- **分布式表**：路由层，不存数据
- **sharding_key**：rand() / hash(user_id) / cityHash64(...)

## 六、MaterializedView（物化视图）

```sql
-- 1. 基础表
CREATE TABLE events (...);

-- 2. 目标聚合表
CREATE TABLE hourly_stats (
    hour DateTime,
    event_type LowCardinality(String),
    uv AggregateFunction(uniq, UInt64),
    pv UInt64
) ENGINE = AggregatingMergeTree()
ORDER BY (hour, event_type);

-- 3. 物化视图（自动维护）
CREATE MATERIALIZED VIEW hourly_mv TO hourly_stats AS
SELECT
    toStartOfHour(ts) AS hour,
    event_type,
    uniqState(user_id) AS uv,
    count() AS pv
FROM events
GROUP BY hour, event_type;

-- 4. 查询（自动反映）
SELECT
    hour,
    event_type,
    uniqMerge(uv) AS uv,
    sum(pv) AS pv
FROM hourly_stats
GROUP BY hour, event_type;
```

**应用**：实时数仓核心，自动增量更新。

## 七、其他引擎

| 引擎 | 用途 |
|---|---|
| **File** | 直接读文件（CSV/TSV/Parquet）|
| **URL** | 读远程文件 |
| **JDBC** | 桥接 MySQL/PG（用 jdbc-bridge）|
| **ODBC** | 桥接（用 odbc-bridge）|
| **MySQL** | 远程 MySQL 表（用 ClickHouse 看 MySQL）|
| **PostgreSQL** | 远程 PG 表 |
| **Dictionary** | 内存键值查（外部数据源）|
| **MaterializedPostgreSQL** | PG → CH 实时同步（24.x）|
| **EmbeddedRocksDB** | RocksDB 集成（24.x）|
| **S3** | S3 对象存储 |
| **HDFS** | HDFS 文件 |
| **Redis** | Redis 数据 |
| **MongoDB** | MongoDB 数据 |

## 关联章节

- **02-sql/overview**：SQL 基础
- **03-table-engine/mergetree-family**：MergeTree 深入
- **03-table-engine/kafka-engine**：Kafka 集成
- **04-olap-scenarios/realtime-warehouse**：实时数仓

## 一句话总结

> **表引擎 = 数据如何存储 + 索引 + 复制**。**99% 场景用 MergeTree 家族 + Kafka + Distributed + MaterializedView**。


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
