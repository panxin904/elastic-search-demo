---
title: Snowflake 数仓架构
---
# Snowflake 数仓架构

## 1. 是什么

Snowflake = 云原生数据仓库（SaaS），三层架构：存储 / 计算 / 服务完全分离。

```
                Services
          ┌─────┼─────┐
   Query  ETL  BI  ML
          │
    ┌─────┴─────┐
    │  Compute  │  ← 弹性伸缩（按查询秒级启停）
    │  Warehouse │
    └─────┬─────┘
          │
    ┌─────┴─────┐
    │  Storage  │  ← 共享 S3 / GCS / Azure Blob
    │   (S3)    │
    └───────────┘
```

## 2. 三大特色

### 2.1 存储计算分离

```
传统数仓（Snowflake / Redshift / Hive）：
  - 存算耦合
  - 扩容 = 加机器 + 迁数据
  - 慢

Snowflake：
  - 存算分离
  - 存储 S3（对象存储）
  - 计算按查询秒级启停
  - 弹性 + 按量付费
```

### 2.2 多计算集群共享数据

```
S3（共享存储）
  ↓
  ┌──────┐   ┌──────┐   ┌──────┐
  │ DW-1 │   │ DW-2 │   │ DW-3 │
  │ 1 XL │   │ 2 XL │   │ M    │
  └──────┘   └──────┘   └──────┘
  ETL        BI        数据科学
  全部读同一份 S3 数据
  互不影响
```

### 2.3 零运维

```
完全云服务：
  - 不用管集群
  - 不用调优
  - 按量付费（停机不收费）
  - 自动备份
  - 自动扩容
```

## 3. 核心功能

```sql
-- 创建 warehouse（计算集群）
CREATE WAREHOUSE etl_wh
  WITH WAREHOUSE_SIZE = 'XLARGE'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  MIN_CLUSTER_COUNT = 1
  MAX_CLUSTER_COUNT = 10;

-- 数据库 / Schema
CREATE DATABASE dw;
CREATE SCHEMA dw.dwd;
CREATE SCHEMA dw.dws;
CREATE SCHEMA dw.ads;

-- 表（自动压缩 + 微分区）
CREATE TABLE dwd.orders (
  order_id BIGINT,
  user_id BIGINT,
  amount DECIMAL(10,2),
  order_time TIMESTAMP_NTZ
)
CLUSTER BY (DATE_TRUNC('day', order_time))
PARTITION BY (DATE_TRUNC('day', order_time));

-- 加载（COPY = 批量最快）
COPY INTO dwd.orders
FROM @s3_stage/orders/2024/01/15/
FILE_FORMAT = (TYPE = PARQUET);

-- 查询
SELECT user_id, COUNT(*), SUM(amount)
FROM dwd.orders
WHERE order_time >= '2024-01-01'
GROUP BY user_id;
```

## 4. 实战案例

### 案例 1：金融风控实时数仓

```
源：Kafka（交易事件）
   ↓ Snowpipe（CDC，秒级入仓）
Snowflake：
  - 实时层（staging）
  - 整合层（dwd）
  - 应用层（dws 风控指标）
  - 服务层（ads 决策）
   ↓
  Snowflake 实时查询 → 风控决策
```

### 案例 2：电商 OLAP

```
源：Kafka（订单事件） + MySQL（用户 / 商品）
   ↓ Snowpipe + Streams
   ↓
  Snowflake：dwd / dws / ads
   ↓
  BI（Tableau / Looker）直接连 Snowflake
```

## 5. 性能优化

```sql
-- 1. 自动聚簇（micro-partition）
ALTER TABLE orders CLUSTER BY (DATE_TRUNC('day', order_time));
-- 手动重聚簇
ALTER TABLE orders RECLUSTER;

-- 2. 查询加速（物化视图）
CREATE MATERIALIZED VIEW daily_sales AS
SELECT DATE(order_time) AS dt, SUM(amount) AS gmv
FROM orders
GROUP BY DATE(order_time);

-- 3. 搜索优化（搜索优化服务）
ALTER TABLE products ADD SEARCH OPTIMIZATION ON (name, description);

-- 4. 物化视图自动刷新
CREATE MATERIALIZED VIEW daily_sales
  REFRESH FAST START AT '2024-01-01'
AS SELECT ...;
```

## 6. 实战选型

| 场景 | 选 |
|------|-----|
| 云原生 / 弹性 | **Snowflake**（首选） |
| AWS 生态 | **Redshift** |
| GCP 生态 | **BigQuery** |
| 私有化 | **Apache Doris** / ClickHouse |
| 大量数据 + 复杂查询 | **Snowflake** / BigQuery |

## 7. 实战选型对比

| | Snowflake | Redshift | BigQuery | ClickHouse |
|--|-----------|-----------|---------|------------|
| 部署 | 公有云 SaaS | AWS | GCP | 私有 / 云 |
| 存算分离 | ✅ | 部分 | ✅ | ❌ |
| 弹性 | 极强 | 中 | 强 | 中 |
| 定价 | 按量（贵）| 按量 | 按量 | 自建 |
| 实时 | Snowpipe | Kinesis | BigQuery Streaming | Kafka 集成 |
| 适用 | 通用 | AWS 用户 | GCP 用户 | 实时 + 大数据 |

## 8. 实战 checklist

- [ ] 数仓选型（按预算 + 生态）
- [ ] 表设计（Kimball 星型 + 缓慢变化维）
- [ ] 加载方式（COPY / Snowpipe / Streams）
- [ ] 性能调优（聚簇 / 物化视图）
- [ ] 权限管理（RBAC）
- [ ] 成本控制（按 warehouse 启停）
- [ ] 监控（query 性能 / cost）

## 9. 实战选型建议

| 业务 | 选 | 原因 |
|------|-----|------|
| 中小互联网 | Snowflake | 按量付费，零运维 |
| 大型互联网 | Doris / StarRocks | 私有化，性能好 |
| 金融 / 强合规 | Redshift | AWS 集成 |
| 全球化 | BigQuery | GCP 集成 |
| 自建数仓 | Hive / Doris | 成本敏感 |

## 🔗 下一步
- [Redshift / BigQuery](/09-dw-architecture/redshift-bigquery)
- [OLAP vs OLTP](/08-modeling/olap-oltp)
- [数据湖 三剑客](/10-data-lake/three-pillars)
