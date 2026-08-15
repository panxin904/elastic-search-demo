---
title: vs StarRocks
description: ClickHouse vs StarRocks：两大列存 OLAP 引擎的全面对比
---

# ClickHouse vs StarRocks

StarRocks 是从 Doris 0.13 fork 出来的开源 OLAP，专注 CBO 优化和向量化执行。本章对比 ClickHouse 与 StarRocks。

## 核心差异

| 维度 | ClickHouse | StarRocks |
|---|---|---|
| **出身** | Yandex（2009） | DorisDB fork（2020）→ StarRocks |
| **架构** | Shared-nothing + 本地存储 | FE + BE，可存算分离（v3.x） |
| **向量化** | 完整（SSE/AVX） | 完整（CBO + Adaptive） |
| **CBO** | 弱（无统计信息） | 强（统计 + CBO + Runtime Filter） |
| **JOIN 优化** | Hash Join 简单 | Adaptive Multi-Agg Join |
| **高并发** | 中（每查询 1-少线程） | 强（每 BE 数百并发） |
| **数据湖** | Iceberg/Hudi/Delta（v23+） | 原生 Iceberg/Hudi/Hive |
| **实时数仓** | Kafka 引擎 + MV | Routine Load + 主键模型 |
| **存算分离** | 部分（v22+ S3） | 完整（v3.x） |
| **运维** | 中（Keeper） | 简单（FE HA + BE 弹性） |
| **典型用户** | Cloudflare / Uber / 字节 | 滴滴 / 网易 / 米哈游 / 小红书 |

## 性能对比（基准测试 SSB）

```text
Star Schema Benchmark（100 GB 数据）

ClickHouse：     1.0x（基线）
StarRocks：      1.5-3x（CBO + Runtime Filter 优化）
```

**结论**：复杂查询场景，StarRocks 通常比 ClickHouse 快 1.5-3x。

## 单查询性能（CK 主场）

```sql
-- 单表列扫
SELECT
  event_date,
  uniq(user_id) AS uv,
  count() AS pv
FROM events
WHERE event_date BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY event_date

-- ClickHouse: 200ms（基于 10 亿行）
-- StarRocks: 400ms
```

**结论**：**单表聚合查询** ClickHouse 略胜（向量化和压缩）。

## 多表 JOIN（StarRocks 主场）

```sql
-- 4 表 JOIN
SELECT
  o.order_id,
  u.user_name,
  p.product_name,
  s.shop_name,
  o.amount
FROM orders o
JOIN users u ON o.user_id = u.id
JOIN products p ON o.product_id = p.id
JOIN shops s ON o.shop_id = s.id
WHERE o.order_date >= '2024-01-01'
LIMIT 1000

-- ClickHouse: 30s（4 表 JOIN 性能退化）
-- StarRocks: 1-3s（CBO 优化）
```

**结论**：**多表 JOIN** StarRocks 完胜（CBO + Runtime Filter + Adaptive）。

## 高并发查询

```sql
-- 100 个并发查询（简单聚合）
-- ClickHouse: 单查询 100ms，总耗时 30s（资源竞争）
-- StarRocks: 单查询 50ms，总耗时 8s（并发友好）
```

**结论**：**高并发** StarRocks 更适合（专为并发查询设计）。

## 实时数仓

### ClickHouse：Kafka 引擎 + MV

```sql
CREATE TABLE events_kafka (...)
ENGINE = Kafka()
SETTINGS kafka_broker_list = 'kafka-1:9092', kafka_topic_list = 'events', ...

CREATE MATERIALIZED VIEW events_mv TO events_local AS
SELECT ... FROM events_kafka
```

### StarRocks：Routine Load + 主键模型

```sql
CREATE TABLE events (
  event_time DATETIME,
  user_id BIGINT,
  event_type VARCHAR(20),
  PRIMARY KEY (event_time, user_id)
)
DUPLICATE KEY(event_time, user_id)
DISTRIBUTED BY HASH(user_id) BUCKETS 32

CREATE ROUTINE LOAD events_load ON events
COLUMNS (event_time, user_id, event_type)
FROM KAFKA (
  "kafka_broker_list" = "kafka-1:9092",
  "kafka_topic" = "events"
)
```

**对比**：
- CK Kafka 引擎简洁（一行 SQL）
- StarRocks Routine Load 可查询状态 + 自动重试
- 两者性能相近

## 数据湖集成

### ClickHouse

```sql
-- v23+ 支持 Iceberg
CREATE TABLE iceberg_table (...)
ENGINE = IcebergS3('http://minio:9000/warehouse/', 'table')

SELECT * FROM iceberg_table
```

### StarRocks

```sql
-- 原生 Iceberg Catalog
CREATE EXTERNAL CATALOG iceberg_catalog
PROPERTIES (
  "type" = "iceberg",
  "iceberg.catalog.type" = "hive",
  "hive.metastore.uris" = "thrift://hive-metastore:9083"
)

SELECT * FROM iceberg_catalog.db.table
```

**对比**：StarRocks 数据湖集成更成熟（多年迭代），CK 正在追赶。

## 存算分离

### ClickHouse

v22.x 引入 S3 存算分离（实验性）：

```sql
CREATE TABLE events (...)
ENGINE = MergeTree()
SETTINGS storage_policy = 's3_main'
```

### StarRocks

v3.x 完整支持存算分离（CN + BN 分离）：

```text
├── FE（前端）
├── CN（计算节点，无状态）
└── BN（存储节点，BE）
```

**对比**：StarRocks v3.x 存算分离生产可用，CK 还在实验阶段。

## 生态对比

| 维度 | ClickHouse | StarRocks |
|---|---|---|
| **官方云** | ClickHouse Cloud | StarRocks Cloud（阿里云） |
| **运维工具** | clickhouse-keeper / clickhouse-backup | StarRocks Manager |
| **监控** | system.metrics | audit log + 系统表 |
| **BI 集成** | Grafana / Superset / Metabase | Apache Superset / SmartBI |
| **客户端** | ch-go / JDBC / Python | mysql-jdbc / Go / Python |
| **版本发布** | 每月一个版本 | 每月一个版本 |

## 选型决策

### 选 ClickHouse

✅ **单表列扫 + 高吞吐写入**（埋点 / 日志）
✅ **极致性能优化**（自研 ch-go 客户端）
✅ **存算分离不是必须**（本地 SSD 即可）
✅ **团队有 ClickHouse 运维经验**

### 选 StarRocks

✅ **复杂 JOIN + 高并发查询**（BI 报表）
✅ **存算分离 + 弹性扩缩容**
✅ **数据湖联邦查询**（Iceberg / Hudi）
✅ **团队倾向 CBO 优化器 + 自动化运维**

## 实战对比

### 场景 1：BI 实时看板（StarRocks 赢面）

```text
数据量：10 亿订单
查询：多维度聚合（地区 + 品类 + 时间）
并发：100+ QPS
表数：5+ JOIN

StarRocks 优势：CBO + Runtime Filter + 高并发
```

### 场景 2：埋点日志分析（CK 赢面）

```text
数据量：PB 级
查询：单表按时间聚合
写入：百万 events/s
表数：1（事件宽表）

CK 优势：写入吞吐 + 单表聚合
```

### 场景 3：电商实时分析（都适合）

```text
数据量：10 亿订单
查询：订单 + 用户 + 商品 JOIN
并发：50 QPS
更新：订单状态实时更新

CK：Doris-style 宽表预 JOIN
SR：直接多表 JOIN（CBO 自动优化）
```

## 大厂案例

| 公司 | 引擎 | 场景 |
|---|---|---|
| 滴滴 | StarRocks | 行程数据（与 CK 共存） |
| 网易 | StarRocks | 游戏分析 |
| 米哈游 | StarRocks | 游戏数据 |
| 小红书 | StarRocks | 内容分析 |
| Cloudflare | ClickHouse | DNS 日志 |
| Uber | ClickHouse | 业务日志 |
| 字节跳动 | ClickHouse | 抖音埋点 |

详见 [../case-study.md](../case-study.md) 案例 1、2、9。

## 结论

- **场景偏聚合 + 写入密集** → ClickHouse
- **场景偏 JOIN + 高并发 + 数据湖** → StarRocks
- **场景都涵盖** → 双引擎共存（滴滴案例）

## 下一步

- 学习 vs TiDB：见 [vs-tidb.md](./vs-tidb.md)
