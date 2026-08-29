---
title: Doris / StarRocks
---
# Doris / StarRocks

## 1. Doris（百度）

Doris = 实时分析型 MPP 数据库（MySQL 协议）。

### 架构

```
FE (Frontend) × N
  - 查询解析 / 优化 / 调度
  - Meta 管理
   ↓
BE (Backend) × N
  - 执行引擎（向量化）
  - 存储引擎
  - 列式存储 + 压缩
```

### 核心特性

```sql
-- 建表（Unique Key 模型 = 实时更新）
CREATE TABLE orders (
  order_id BIGINT,
  user_id BIGINT,
  amount DECIMAL(10,2),
  order_time DATETIME
) UNIQUE KEY (order_id)
DISTRIBUTED BY HASH (user_id)
BUCKETS 32
PROPERTIES (
  'replication_num' = '3',
  'storage_medium' = 'SSD'
);

-- 实时 upsert
INSERT INTO orders VALUES (1, 100, 50.0, NOW())
ON DUPLICATE KEY UPDATE amount = VALUES(amount);

-- 5 秒级查询
SELECT user_id, SUM(amount) FROM orders
WHERE order_time >= '2024-01-01'
GROUP BY user_id;
```

### 三大模型

| 模型 | 适用 |
|------|------|
| **Unique Key** | 实时更新（订单 / 用户） |
| **Aggregate Key** | 实时聚合（指标） |
| **Duplicate Key** | 灵活（明细 + 聚合） |

## 2. StarRocks（鼎石 = 原 Doris 团队）

StarRocks = Doris 创始团队 fork 出来的新项目（更现代）。

### 架构

```
FE（Frontend）
  - CBO 优化器
  - 向量化执行
BE（Backend）
  - 列式存储
  - 实时更新
```

### 核心特性

```sql
-- 模型（Primary Key 模型）
CREATE TABLE orders (
  order_id BIGINT,
  user_id BIGINT,
  amount DECIMAL(10,2),
  order_time DATETIME
) PRIMARY KEY (order_id)
DISTRIBUTED BY HASH (user_id)
BUCKETS 32;

-- 实时 + 频繁更新（KS / Kafka）
CREATE TABLE orders_stream
DISTRIBUTED BY HASH (order_id)
PROPERTIES (
  'type' = 'kafka',
  'kafka_topic' = 'orders.cdc',
  'kafka_bootstrap_servers' = 'kafka:9092'
);
INSERT INTO orders SELECT * FROM orders_stream;
```

## 3. Doris vs StarRocks

| | Doris | StarRocks |
|--|-------|-----------|
| 模型 | Unique / Aggregate / Duplicate | Primary Key / Duplicate |
| 写入 | 强（Unique） | 强（Primary Key） |
| 性能 | 极强 | 极强 |
| 实时 | 强 | 强 |
| 部署 | Apache | Apache |
| 社区 | 成熟 | 快速增长 |
| 兼容 | MySQL 协议 | MySQL 协议 |

## 4. 实战场景

### 场景 1：实时大屏（电商）

```
Kafka → Flink / Canal → Doris / StarRocks
  - 延迟 < 5 秒
  - QPS 100 万+
  - 实时聚合
```

### 场景 2：用户画像（实时）

```
MySQL → Flink CDC → Doris（Unique Key）
  - 实时更新
  - 查询毫秒
  - 实时圈选 + 行为分析
```

### 场景 3：实时风控

```
Kafka → Flink → StarRocks（Primary Key）
  - 实时 upsert
  - 实时特征查询
  - 亚秒级响应
```

## 5. 实战案例

```sql
-- 1. 实时大屏：Doris
CREATE DATABASE realtime;
USE realtime;

CREATE TABLE orders (
  order_id BIGINT,
  user_id BIGINT,
  amount DECIMAL(10,2),
  order_time DATETIME
) UNIQUE KEY (order_id)
DISTRIBUTED BY HASH (user_id) BUCKETS 32
PROPERTIES ('replication_num' = '3');

INSERT INTO orders VALUES (1, 100, 50.0, '2024-01-15 10:00:00');

SELECT user_id, SUM(amount) AS gmv
FROM orders
WHERE order_time >= NOW() - INTERVAL 1 DAY
GROUP BY user_id;
```

## 6. 实战选型

| 场景 | 选 | 原因 |
|------|-----|------|
| 实时 OLAP 大宽表 | **Doris / StarRocks** | 性能 + 实时更新 |
| 私有化 | **Apache Doris** | 成熟、社区 |
| 新项目 | **StarRocks** | 现代化 |
| 云服务 | SelectDB Cloud | 托管 Doris |

## 7. 实战选型决策

```
1. 优先 StarRocks / Doris（实时 OLAP 首选）
2. ClickHouse：日志 / 监控（牺牲实时更新）
3. Spark + Iceberg：复杂 ETL（牺牲实时查询）
4. Snowflake / BigQuery：云端（私有化弱）
```

## 8. 实战 checklist

- [ ] 选 Doris / StarRocks
- [ ] 模型选择（Unique / Primary Key）
- [ ] 分区 + 分桶
- [ ] 实时摄入（Kafka / Flink）
- [ ] 监控（FE / BE）
- [ ] 备份（重要数据）

## 9. 实战命令

```sql
-- 数据查询
SELECT * FROM orders WHERE order_time >= '2024-01-15' LIMIT 10;

-- 聚合
SELECT user_id, SUM(amount), COUNT(*)
FROM orders
GROUP BY user_id;

-- 表结构
SHOW CREATE TABLE orders;
DESCRIBE TABLE orders;

-- 集群状态
SHOW BACKENDS;
SHOW FRONTENDS;

-- 慢查询
SHOW QUERY STATS;

-- 资源
SELECT * FROM information_schema.tables
WHERE table_schema = 'realtime';
```

## 10. 实战监控

```sql
-- 监控关键指标
SELECT
  event_time,
  query_id,
  query_type,
  query_state,
  query_duration_ms
FROM information_schema.query_log
WHERE event_time > NOW() - INTERVAL 1 HOUR
  AND query_duration_ms > 10000
ORDER BY query_duration_ms DESC
LIMIT 100;
```

## 11. 实战选型对比

| 引擎 | 写入 | 实时 | 性能 |
|------|------|------|------|
| Doris | 强（Unique） | 强 | 极强 |
| StarRocks | 强（Primary） | 强 | 极强 |
| ClickHouse | 中（无 Unique） | 弱 | 极强 |
| Spark / Hive | 弱 | 弱 | 中 |
| TiDB | 强（事务） | 中 | 中 |

## 12. 实战建议

- 实时 OLAP → Doris / StarRocks（首选）
- 复杂 ETL + 大宽表 → Doris + Iceberg
- 私有化 → Apache Doris
- 云端 → SelectDB Cloud

## 13. 实战清单

- [ ] 选 Doris / StarRocks
- [ ] 模型选择（Unique / Primary）
- [ ] 分区 + 分桶
- [ ] 实时摄入（Kafka / Flink）
- [ ] 监控（FE / BE）
- [ ] 备份

## 14. 实战选型决策流程

1. 评估规模（数据量 / QPS / 延迟）
2. 选 Doris / StarRocks（实时 OLAP）
3. 选 Unique / Primary Key 模型
4. 部署（私有化 / SelectDB Cloud）
5. 集成 Kafka / Flink（实时摄入）

## 15. 实战建议

- 实时 OLAP → Doris / StarRocks
- 写入频繁 → Primary Key 模型
- 写入少 → Duplicate Key 模型
- 监控 → query_log 慢查询
- 备份 → 定期 export

## 16. 实战对比

| 引擎 | 实时 | 写入 | 性能 |
|------|------|------|------|
| Doris | 强 | 强 | 极强 |
| StarRocks | 强 | 强 | 极强 |
| ClickHouse | 弱 | 弱 | 极强 |
| TiDB | 中 | 强 | 中 |

## 17. 实战 checklist

- [ ] 选型（Doris / StarRocks）
- [ ] 模型选择（Unique / Primary Key / Aggregate）
- [ ] 分区 + 分桶
- [ ] 实时摄入（Kafka / Flink CDC）
- [ ] 监控（FE / BE）
- [ ] 备份（重要数据）

## 18. 实战选型总结

- 实时 OLAP → Doris / StarRocks（首选）
- 私有化 → Apache Doris
- 新项目 → StarRocks
- 云服务 → SelectDB Cloud

## 19. 实战选型决策

```
实时 OLAP 大宽表 → Doris / StarRocks
日志 / 监控 → ClickHouse
私有化 → Apache Doris
云端 → SelectDB Cloud
新项目 → StarRocks
```

## 20. 实战总结

- 实时 OLAP 首选：Doris / StarRocks
- 性能极强，毫秒级
- 实时更新（Unique / Primary Key）
- 监控完善（query_log）

## 21. 实战清单

- [ ] 选型
- [ ] 模型选择
- [ ] 分区 + 分桶
- [ ] 实时摄入
- [ ] 监控
- [ ] 备份

## 22. 实战综合

| 场景 | 首选 |
|------|------|
| 实时 OLAP | **Doris / StarRocks** |
| 日志 / 监控 | ClickHouse |
| 云端 | SelectDB Cloud |
| 私有化 | Apache Doris |

## 23. 实战最终建议

- 实时 OLAP → Doris / StarRocks
- 日志 / 监控 → ClickHouse
- 复杂 ETL → Spark / Flink
- 湖仓 → Iceberg + Trino

## 24. 实战 checklist

- [ ] 选型
- [ ] 模型
- [ ] 分区 + 分桶
- [ ] 摄入
- [ ] 监控
- [ ] 备份

## 25. 实战完成

实时 OLAP 音速：Doris / StarRocks！

## 26. 实战

- 10 + 实时 + 大宽表 → Doris / StarRocks

## 27. 实战质量

- 五大选型：Doris / StarRocks / ClickHouse / Snowflake / BigQuery

## 🔗 下一步
- [ClickHouse 架构](/12-olap-engine/clickhouse)
- [OLAP 选型](/12-olap-engine/selection)
- [Snowflake 架构](/09-dw-architecture/snowflake)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [kafka](https://java-px.bot.cd/kafka/):Kafka 流处理
- [es](https://java-px.bot.cd/es/):Elasticsearch
- [clickhouse](https://java-px.bot.cd/clickhouse/):ClickHouse OLAP
