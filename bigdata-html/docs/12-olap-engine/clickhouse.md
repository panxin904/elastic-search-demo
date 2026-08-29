---
title: ClickHouse
date: 2026-08-15  # date-auto-injected
---
# ClickHouse 架构

## 1. 是什么

ClickHouse = Yandex 开源的**列式 OLAP 数据库**（C++）。

性能特点：
  - 单机 100 亿行 / 秒级查询
  - 向量化执行（SIMD）
  - 列式压缩（10-20x）
  - 实时写入（不卡数据导入）

## 2. 架构

```
Query
  ↓
  Parser（生成 AST）
  ↓
  Optimizer（谓词下推 / 列裁剪）
  ↓
  Plan（合并多个 partition）
  ↓
  Executor（向量化 SIMD）
  ↓
  Storage（MergeTree 引擎）
  - 数据按主键排序
  - 稀疏索引（每 8192 行）
  - 列式压缩
```

## 3. 核心特性

### 3.1 MergeTree 引擎

```sql
CREATE TABLE events (
  ts DateTime,
  user_id UInt64,
  event_type LowCardinality(String),
  amount Float64
) ENGINE = MergeTree()
ORDER BY (user_id, ts)
PARTITION BY toYYYYMM(ts);

-- 写入
INSERT INTO events VALUES (now(), 123, 'click', 0.99);

-- 查询（毫秒级）
SELECT count(), uniq(user_id), avg(amount)
FROM events
WHERE ts > now() - INTERVAL 1 DAY
GROUP BY event_type;
```

### 3.2 索引

```sql
-- 主键索引（ORDER BY）
ORDER BY user_id

-- 跳数索引（每 8192 行）
-- 自动创建

-- 数据跳过（minmax）
INDEX idx_event_type event_type TYPE set(4) GRANULARITY 4
```

### 3.3 表引擎

| 引擎 | 特点 |
|------|------|
| MergeTree | 默认，insert 不可变 |
| ReplacingMergeTree | 保留最新版本 |
| SummingMergeTree | 累加（指标） |
| AggregatingMergeTree | 聚合预计算 |
| CollapsingMergeTree | 折叠小状态 |
| Log | 临时表 |
| Distributed | 分布式（自动） |

## 4. 实战 Schema 设计

```sql
-- 1. 事件表
CREATE TABLE events (
  ts DateTime,
  user_id UInt64,
  event_type LowCardinality(String),
  amount Float64,
  country LowCardinality(String)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(ts)
ORDER BY (user_id, ts)
SETTINGS index_granularity = 8192;

-- 2. 物化视图（自动聚合）
CREATE MATERIALIZED VIEW user_daily
ENGINE = SummingMergeTree
ORDER BY (user_id, dt)
POPULATE AS
SELECT
  user_id,
  toDate(ts) AS dt,
  sum(amount) AS gmv,
  count() AS cnt
FROM events
GROUP BY user_id, dt;

-- 3. 实时查询
SELECT dt, sum(gmv) FROM user_daily
WHERE dt >= today() - 7
GROUP BY dt;
```

## 5. 实战优化

### 5.1 索引

```sql
-- 跳数索引（默认）
-- ORDER BY 列自动建索引

-- 跳数 + minmax 索引
ALTER TABLE events ADD INDEX idx_ts ts TYPE minmax GRANULARITY 3;

-- 布隆过滤器索引（适合点查）
ALTER TABLE events ADD INDEX idx_user user_id TYPE bloom_filter(0.01) GRANULARITY 4;
```

### 5.2 分区

```sql
-- 建议：分区大小 1-10 GB
PARTITION BY toYYYYMM(ts)  -- 月分区
PARTITION BY toDate(ts)     -- 日分区（大量数据）

-- 删除旧分区（高效）
ALTER TABLE events DROP PARTITION 202312;
```

### 5.3 写入

```sql
-- 批量插入（推荐）
INSERT INTO events SELECT * FROM input_table;

-- 小批量（10 万级 / 秒）
INSERT INTO events VALUES (...);

-- 实时（Kafka 消费）
CREATE TABLE events_kafka (...)
  ENGINE = Kafka()
  SETTINGS kafka_broker_list = 'kafka:9092',
           kafka_topic = 'events',
           kafka_format = 'JSONEachRow';

CREATE TABLE events_local AS events_kafka;
INSERT INTO events_local SELECT * FROM events_kafka;
```

### 5.4 查询优化

```sql
-- 1. 谓词下推
WHERE ts >= '2024-01-01' AND event_type = 'click'

-- 2. 避免 SELECT *
SELECT user_id, sum(amount) FROM ...

-- 3. 用近似（快 10x）
SELECT uniqHLL12(user_id) FROM events;  -- 近似去重

-- 4. 优化 JOIN
SETTINGS join_algorithm = 'direct'

-- 5. 预聚合
SELECT user_id, sum(amount) FROM user_daily GROUP BY user_id;
```

## 6. ClickHouse vs Doris vs StarRocks

| | ClickHouse | Doris | StarRocks |
|---|---|---|---|
| 出品 | Yandex | 百度 | 鼎石 |
| 性能 | 极强 | 强 | 极强 |
| 写入 | 强 | 强 | 强 |
| 更新 | 弱 | 强（Unique Key）| 强 |
| 生态 | 独立 | Apache Doris | Apache |
| 部署 | 云 / 自建 | 自建 | 自建 |
| 适合 | 海量日志 | 实时 OLAP | 实时 OLAP |

## 7. 实战案例

### 案例 1：电商日志分析

```
Kafka → ClickHouse（Kafka 引擎）
  - 每天 10 亿条
  - 7 天保留（可调整）
  - 实时查询（亚秒）

表设计：
  events_local (Kafka 引擎)
  events (MergeTree)
  events_user_daily (SummingMergeTree，聚合)
  
查询：
  - 实时大屏
  - 业务报表
  - 用户行为分析
```

### 案例 2：金融交易分析

```
MySQL → Flink CDC → ClickHouse
  - 实时摄取
  - 实时风控
  - T+1 报表

表设计：
  transactions（明细）
  user_balance_history（快照）
  risk_metrics（聚合）
```

## 8. ClickHouse 命令

```sql
-- 查
SELECT * FROM events LIMIT 10;
SELECT count() FROM events;
SELECT uniq(user_id) FROM events
WHERE ts > now() - INTERVAL 1 HOUR;

-- 写入
INSERT INTO events VALUES (now(), 123, 'click', 0.99);

-- 集群
SELECT * FROM system.clusters;
SELECT * FROM system.replicas;

-- 慢查询
SELECT * FROM system.query_log
WHERE type > 1 AND query_start_time > now() - INTERVAL 1 DAY
ORDER BY query_duration_ms DESC LIMIT 10;
```

## 9. 实战选型

| 场景 | 选 |
|------|-----|
| 海量日志 / 监控 | **ClickHouse**（首选） |
| 实时 OLAP 大宽表 | **Doris / StarRocks** |
| 实时 + 频繁更新 | **Doris / StarRocks**（强） |
| 亚秒级查询 | **ClickHouse** |
| 大量历史 + 简单聚合 | **ClickHouse** |

## 10. 实战 checklist

- [ ] 表引擎选择（MergeTree / Summing / Distributed）
- [ ] 分区设计（按月 / 周 / 日）
- [ ] 排序键选择（高基数低基数）
- [ ] 索引（ORDER BY / minmax / bloom_filter）
- [ ] 写入方式（Kafka / insert / batch）
- [ ] 物化视图（自动聚合）
- [ ] 监控（query_log / merge_log）

## 11. 实战选型决策

```
做日志 / 监控统计 → ClickHouse
做实时 OLAP 大宽表 → Doris / StarRocks
做实时 + 频繁更新 → Doris / StarRocks
做 OLAP 私有化 → Doris（Apache）
做 ClickHouse 云服务 → ClickHouse Cloud
```

## 12. 实战注意事项

- 写入一旦提交，删除 / 修改用 ALTER TABLE（不能快速 DELETE）
- UPDATE 用 ReplacingMergeTree（按 ORDER BY 替换）
- 聚合查询用物化视图
- 监控 query_log（慢查询）

## 13. 实战选型对比

| 栈 | 适合 |
|------|------|
| ClickHouse + S3 | 海量日志 + 自建 |
| Doris + Hive | 实时 OLAP + 私有化 |
| StarRocks + Hive | 实时 OLAP + 实时数仓 |
| Doris + Iceberg | 湖仓 + 实时 OLAP |

## 14. 实战建议

1. 选 ClickHouse：日志 / 监控 / 海量
2. 选 Doris / StarRocks：实时 OLAP / 私有化
3. 分区设计：按时间（每天 / 每月）
4. 排序键：选高基数（user_id） + 时间
5. 预聚合：SummingMergeTree 或物化视图
6. 监控：query_log / 慢查询

## 15. 实战 checklist

- [ ] ClickHouse 安装（20.x）
- [ ] Zookeeper 集成（ReplicatedMergeTree）
- [ ] Kafka 消费（Kafka 引擎）
- [ ] 物化视图（聚合）
- [ ] 监控（query_log / merge_log）
- [ ] 备份（重要数据）

## 🔗 下一步
- [Doris / StarRocks](/12-olap-engine/doris-starrocks)
- [OLAP 选型](/12-olap-engine/selection)
- [Snowflake 架构](/09-dw-architecture/snowflake)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [kafka](https://java-px.bot.cd/kafka/):Kafka 流处理
- [es](https://java-px.bot.cd/es/):Elasticsearch
- [clickhouse](https://java-px.bot.cd/clickhouse/):ClickHouse OLAP
