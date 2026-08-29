---
title: Redshift / BigQuery
---
# Redshift / BigQuery 数仓

## 1. AWS Redshift

Redshift = AWS 的托管 MPP 列式数据仓库（PostgreSQL 协议）。

### 架构

```
Leader Node
  - 查询解析 / 优化
  - 协调 Compute Nodes
   ↓
Compute Nodes × N
  - 列式存储（块）
  - 并行执行
  - MPP（大规模并行）
```

### 实战

```sql
-- 创建表（指定排序键 + 压缩）
CREATE TABLE orders (
  order_id BIGINT,
  user_id BIGINT,
  amount DECIMAL(10,2),
  order_time TIMESTAMP
)
SORTKEY (order_time)
DISTKEY (user_id)
COMPRESS BYTEDELTA;

-- 加载（COPY 最快）
COPY orders FROM 's3://my-bucket/orders/2024/01/15/' 
  IAM_ROLE 'arn:aws:iam::123:role/RedshiftCopy'
  FORMAT AS PARQUET;

-- 查询
SELECT user_id, COUNT(*), SUM(amount)
FROM orders
WHERE order_time BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY user_id;
```

### Redshift Serverless

```
无服务器：按 RPU（Redshift Processing Unit）按量付费
  - 自动扩缩
  - 自动优化
  - 按查询秒级计费
  - 无需管理集群
```

## 2. GCP BigQuery

BigQuery = GCP 的托管数据仓库（无服务器）。

### 架构

```
Storage (Colossus)  ←  无限扩展的对象存储
  ↓
Compute（Dremel）  ←  无服务器，按查询秒级计费
  - 自动扩容
  - 自动优化
  - 柱式存储
```

### 实战

```sql
-- 创建表（分区 + 聚簇）
CREATE TABLE `mydataset.orders` (
  order_id INT64,
  user_id INT64,
  amount NUMERIC,
  order_time TIMESTAMP
)
PARTITION BY DATE(order_time)
CLUSTER BY user_id;

-- 加载
LOAD DATA OVERWRITE `mydataset.orders`
FROM FILES (
  format = 'PARQUET',
  uris = ['gs://my-bucket/orders/*.parquet']
);

-- 查询
SELECT user_id, COUNT(*) AS cnt, SUM(amount) AS gmv
FROM `mydataset.orders`
WHERE DATE(order_time) BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY user_id;
```

### BigQuery ML

```sql
-- BigQuery ML（SQL 内 ML）
CREATE MODEL `mydataset.user_churn_model`
OPTIONS(model_type='logistic_reg') AS
SELECT
  user_id, age, activity_score, churned
FROM `mydataset.user_features`;

-- 预测
SELECT * FROM ML.PREDICT(MODEL `mydataset.user_churn_model`,
  (SELECT * FROM `mydataset.new_user_features`));
```

## 3. Redshift vs BigQuery

| | Redshift | BigQuery |
|--|-----------|-----------|
| 部署 | AWS | GCP |
| 协议 | PostgreSQL | Standard SQL |
| 定价 | 按节点 / 按量 | 按量（按查询） |
| 存算分离 | 部分（Redshift Serverless） | ✅ |
| 实时 | Kinesis Data Streams | BigQuery Streaming |
| ML | Redshift ML | BigQuery ML |
| 优势 | AWS 集成 / 复杂 join | GCP 集成 / 无服务器 |
| 适用 | 大型 AWS 客户 | GCP 客户 |

## 4. 实战选型

```
业务 → 选型
  - AWS 客户 → Redshift
  - GCP 客户 → BigQuery
  - 多云 / 自建 → Snowflake / ClickHouse / Doris
  - 实时 + 离线 → BigQuery（streaming）
  - 大量历史 → Redshift（压缩存储）
```

## 5. 实战案例

### 案例 1：AWS 全栈数仓

```
S3 (数据湖)
   ↓
Glue（ETL）
   ↓
Redshift（OLAP）
   ↓
Quicksight（BI）

优势：全 AWS 生态，零运维
成本：按 Redshift 节点 + S3 存储
```

### 案例 2：GCP 全栈

```
GCS (数据湖)
   ↓
Dataflow（流批）
   ↓
BigQuery（OLAP）
   ↓
Looker（BI）

优势：流批一体，BigQuery 极强
成本：按 query bytes
```

## 6. 实战选型决策

```
阶段 1：< 10 TB → 单机 OLAP（ClickHouse / Doris）
阶段 2：10-100 TB → Snowflake / BigQuery
阶段 3：100+ TB → Snowflake + Iceberg / BigQuery
```

## 7. 实战技巧

### Redshift

```sql
-- 1. 选择排序键（高基数列不能选）
-- 范围查询的列（如时间）作 sortkey
-- 高基数列（如 user_id）作 distkey
-- 但要选低基数

-- 2. 压缩（自动）
-- COPY 时自动选压缩算法
ANALYZE COMPRESSION orders;

-- 3. 真空回收
VACUUM DELETE ONLY orders;

-- 4. 性能监控
SELECT * FROM STL_ALERT_EVENT_LOG
WHERE event_time > DATEADD(hour, -1, GETDATE());
```

### BigQuery

```sql
-- 1. 分区裁剪（避免全表扫描）
WHERE DATE(order_time) = '2024-01-15'

-- 2. 集群表（自动排序）
CLUSTER BY user_id

-- 3. 近似聚合（快）
SELECT APPROX_COUNT_DISTINCT(user_id) FROM events;

-- 4. BI Engine（在线服务）
CREATE MODEL `mydataset.user_ltv`
OPTIONS(model_type='linear_reg') AS ...
```

## 8. 实战性能对比

| 规模 | Redshift | BigQuery | ClickHouse |
|------|----------|----------|-------------|
| 1 TB | 快 | 极快 | 极快 |
| 100 TB | 快 | 快 | 极快 |
| 1 PB | 中（需 resize） | 快 | 快 |
| 10 PB | 慢 | 中 | 中 |

## 9. 实战成本对比

| | Redshift | BigQuery | Snowflake |
|--|----------|----------|-----------|
| 存储 | $0.024/GB/月 | $0.02/GB/月 | $0.04/GB/月 |
| 计算 | $0.25/h (dc2.large) | $6.25/TB 查询 | 按 warehouse |
| 实时 | Kinesis 收费 | BigQuery streaming | Snowpipe |

**经验**：BigQuery 最便宜（按查询字节）；Redshift 贵但稳定；Snowflake 中等。

## 10. 实战 checklist

- [ ] 数仓选型（按云生态）
- [ ] 表设计（星型 / 缓慢变化维）
- [ ] 加载方式（COPY / Snowpipe / Streams）
- [ ] 性能调优（聚簇 / 物化视图）
- [ ] 权限管理（RBAC）
- [ ] 成本控制（warehouse 启停）
- [ ] 监控（query 性能 / cost）

## 🔗 下一步
- [Snowflake 架构](/09-dw-architecture/snowflake)
- [OLAP vs OLTP](/08-modeling/olap-oltp)
- [数据湖 三剑客](/10-data-lake/three-pillars)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [kafka](https://java-px.bot.cd/kafka/):Kafka 流处理
- [es](https://java-px.bot.cd/es/):Elasticsearch
- [clickhouse](https://java-px.bot.cd/clickhouse/):ClickHouse OLAP
