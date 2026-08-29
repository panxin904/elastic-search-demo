---
title: Hive 架构
date: 2026-08-15  # date-auto-injected
---
# Hive 架构

## 1. 整体架构

```
        Client (Beeline / JDBC)
          ↓
        HiveServer2 (Thrift Server)
          ↓
        Compiler (SQL → DAG)
          ↓
        Execution Engine
          ├── MapReduce / Tez / Spark
          └── LLAP (Long Lived Process)
          ↓
        MetaStore (metadata)
          ├── MySQL / PostgreSQL
          └── Thrift API
          ↓
        Storage
          ├── HDFS
          ├── S3 / OSS
          └── Iceberg / Hudi
```

## 2. 核心组件

### MetaStore

```
存放元数据：
  - Database / Table / Partition 定义
  - 列类型 / 存储格式
  - 文件位置 / 分区信息
  - SerDe 信息
  - Statistics（行数 / 大小）

部署模式：
  1. Embedded（单 JVM，默认）
  2. Remote（独立服务，多 HiveServer2 共享）
     └── MySQL / PostgreSQL 存储元数据
```

### HiveServer2

```
Thrift Server：处理客户端请求
  - 接收 SQL
  - 解析 / 优化
  - 调度执行
  - 返回结果

支持多客户端：
  - Beeline（CLI）
  - JDBC / ODBC（BI 工具）
  - Python（PyHive / spark-hive）
```

### Compiler / Optimizer

```
SQL → AST → Logical Plan → Optimized Plan → Physical Plan → DAG

CBO（Cost-Based Optimizer）：
  - 谓词下推
  - 列裁剪
  - Join 重排
  - 统计信息
```

## 3. 数据模型

```sql
-- 内部表（managed）
CREATE TABLE orders (
  id BIGINT,
  user_id BIGINT,
  amount DECIMAL(10,2),
  created_at TIMESTAMP
) PARTITIONED BY (dt STRING)
STORED AS PARQUET
LOCATION '/data/warehouse/orders';

-- 外部表（external）
CREATE EXTERNAL TABLE logs (
  ts TIMESTAMP,
  level STRING,
  msg STRING
) STORED AS TEXTFILE
LOCATION '/data/logs/';

-- 分区
ALTER TABLE orders ADD PARTITION (dt='2024-01-15');
```

## 4. 存储格式

| 格式 | 特点 |
|------|------|
| TextFile | 默认，文本 |
| SequenceFile | 二进制 |
| RCFile / ORC | 列式（推荐） |
| Parquet | 列式（推荐） |
| Avro | 模式演进 |
| JSON | 半结构化 |

**生产推荐 ORC / Parquet**（列式 + 压缩 + 谓词下推）。

## 5. 执行引擎

```
MR（MapReduce）：原始
Tez：基于 DAG，比 MR 快
Spark：内存迭代
LLAP（Long Lived Process）：
  - 常驻 daemon
  - 缓存容器
  - 列式 cache
  - 推荐
```

```sql
SET hive.execution.engine=tez;
SET hive.execution.engine=spark;
SET hive.execution.engine=mr;
```

## 6. 实战命令

```sql
-- 数据库
CREATE DATABASE dw;
USE dw;

-- 内部表（Parquet + 分区）
CREATE TABLE orders (
  id BIGINT,
  user_id BIGINT,
  amount DECIMAL(10,2),
  created_at TIMESTAMP
) PARTITIONED BY (dt STRING)
STORED AS PARQUET
TBLPROPERTIES ('parquet.compression'='SNAPPY');

-- 加载（分区）
LOAD DATA INPATH '/data/raw/orders/2024-01-15/'
INTO TABLE orders PARTITION (dt='2024-01-15');

-- 查询
SELECT user_id, sum(amount), count(*)
FROM orders
WHERE dt BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY user_id
ORDER BY sum(amount) DESC
LIMIT 100;

-- 动态分区
SET hive.exec.dynamic.partition.mode=nonstrict;
INSERT OVERWRITE TABLE orders PARTITION (dt)
SELECT id, user_id, amount, created_at, dt FROM raw_orders;

-- 导出
INSERT OVERWRITE DIRECTORY '/data/export/orders'
SELECT * FROM orders WHERE dt = '2024-01-15';
```

## 7. 实战调优

```sql
-- 1. 谓词下推
SET hive.optimize.ppd=true;
SELECT * FROM orders WHERE user_id = 123;  -- 推到 Parquet 列裁剪

-- 2. 列裁剪
SELECT id, amount FROM orders;  -- 只读 2 列

-- 3. Map Join（小表）
SET hive.auto.convert.join=true;
SELECT /*+ MAPJOIN(small_table) */ * FROM big JOIN small ON ...;

-- 4. Cost-Based Optimization
ANALYZE TABLE orders COMPUTE STATISTICS;
SET hive.cbo.enable=true;

-- 5. 向量化
SET hive.vectorized.execution.enabled=true;
SET hive.vectorized.execution.reduce.enabled=true;

-- 6. Tez 容器重用
SET hive.execution.engine=tez;
SET tez.am.resource.dedicated=true;
```

## 8. 实战：ETL Pipeline

```sql
-- ODS
CREATE TABLE ods.orders (
  id BIGINT, user_id BIGINT, amount DECIMAL(10,2), dt STRING
) PARTITIONED BY (dt) STORED AS PARQUET;

-- DWD（清洗）
CREATE TABLE dwd.orders AS
SELECT
  id,
  user_id,
  amount,
  CASE WHEN amount > 0 THEN 'valid' ELSE 'invalid' END AS status,
  dt
FROM ods.orders
WHERE dt = '${hiveconf:dt}';

-- DWS（聚合）
CREATE TABLE dws.user_order_daily AS
SELECT
  user_id,
  dt,
  count(*) AS order_cnt,
  sum(amount) AS gmv
FROM dwd.orders
GROUP BY user_id, dt;
```

## 9. Hive 3.x 新特性

- LLAP 默认
- 物化视图（Materialized View）
- CBO 优化器（Calcite）
- 支持 INSERT INTO ... VALUES
- 支持 Lambda 表达式（部分）
- 与 Iceberg / Hudi 集成

## 10. 实战 checklist

- [ ] MetaStore 独立部署（多 HS2 共享）
- [ ] MetaStore 选 MySQL / PostgreSQL（不用 Derby）
- [ ] 执行引擎选 Tez（比 MR 快 10x）
- [ ] 启用 Cost-Based Optimization
- [ ] 启用向量化执行
- [ ] 表用 ORC / Parquet（压缩 + 列裁剪）
- [ ] 分区设计（按 dt 每天）
- [ ] 监控：HiveServer2 / MetaStore 指标

## 🔗 下一步
- [Hive 优化](/06-hive/optimize)
- [Hive on Spark / Tez](/06-hive/engine)
