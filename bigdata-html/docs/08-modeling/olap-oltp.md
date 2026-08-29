---
title: OLAP vs OLTP
date: 2026-08-15  # date-auto-injected
---
# OLAP vs OLTP

## 1. 两种系统

| | OLTP | OLAP |
|--|-------|------|
| 用途 | 业务交易 | 业务分析 |
| 操作 | 增删改查（短事务） | 复杂查询（聚合 / 扫描） |
| 延迟 | 毫秒 | 秒-分钟 |
| 数据量 | GB-TB | TB-PB |
| 用户数 | 大量（万+） | 少量（百+） |
| 典型场景 | 下单 / 支付 | 报表 / 数据分析 / BI |
| 数据特点 | 实时 / 最新 | 历史 / 大量 |
| 代表 | MySQL / Oracle | Hive / ClickHouse / Doris |
| 一致性 | 强（ACID） | 最终一致 |

## 2. OLTP 系统特点

```
关系型数据库（MySQL / Oracle / PG）：
  - 行式存储（适合按行查询）
  - 二级索引（B+Tree）
  - ACID 事务
  - 主键 / 外键约束
  - 单机 / 集群（小规模）
  - 优化：行级锁、索引、SQL 调优
```

## 3. OLAP 系统特点

```
列式数据库（ClickHouse / Doris / StarRocks / Parquet / ORC）：
  - 列式存储（适合按列聚合）
  - 向量化执行（SIMD）
  - 物化视图
  - 分布式计算（MPP）
  - 大规模（PB 级）
  - 优化：分区裁剪、列裁剪、压缩、谓词下推
```

## 4. 大数据场景选型

| 场景 | 选 | 原因 |
|------|-----|------|
| 实时业务交易 | OLTP（MySQL） | 强一致、低延迟 |
| 实时分析（亚秒） | OLAP 实时引擎（Doris / StarRocks） | 强 OLAP 性能 |
| 离线报表（小时） | Hive / Spark SQL | 批处理 |
| 日志分析 | ClickHouse / ES | 海量数据 |
| 实时数仓 | Flink + OLAP | 流 + OLAP |
| 数据湖分析 | Iceberg + Spark / Trino | 灵活查询 |

## 5. 经典场景：OLAP 选型

| 规模 | 选 |
|------|-----|
| GB-TB / 日 | ClickHouse / Doris / StarRocks |
| TB-PB / 日 | Doris / StarRocks / Hive + Spark |
| 实时 + 高并发 | Doris / StarRocks（强） |
| 简单查询 | ClickHouse（写入快） |
| 海量日志 | ClickHouse（首选） |

## 6. 实战案例

### 案例 1：电商订单 OLTP + OLAP 分离

```
OLTP（业务库）：
  MySQL → 订单 / 用户 / 库存（实时事务）
  
  ↓ CDC（binlog）

OLAP（数据仓库）：
  Hive / ClickHouse → 订单分析 / 用户画像 / 报表
```

### 案例 2：实时大屏

```
OLTP MySQL → Flink CDC → Kafka → Flink SQL 聚合
  → ClickHouse / Doris（OLAP 引擎，毫秒级查询）
  → 实时大屏
```

## 7. 一致性 vs 性能

OLTP 强一致（ACID 事务） vs  OLAP 最终一致（性能优先）。

OLTP：
  - 实时一致性
  - 单行操作
  - 锁开销

OLAP：
  - 高吞吐（PB 级扫描）
  - 不修改原始数据
  - 批量插入（ETL）

## 8. 实战误区

- ❌ 用 OLTP 跑 OLAP：MySQL 跑全表扫描 = 慢死
- ❌ 用 OLAP 跑 OLTP：ClickHouse 跑事务 = 强一致差
- ❌ 单库两用：性能 / 维护都差
- ✅ 分离：OLTP 业务库 + OLAP 数据仓

## 9. 实战 checklist

- [ ] OLTP / OLAP 分离
- [ ] CDC 实时同步（Flink CDC / Canal）
- [ ] 数据仓库分层（ODS / DWD / DWS / ADS）
- [ ] OLAP 引擎选型（ClickHouse / Doris / StarRocks）
- [ ] 监控（ETP 延迟 / OLAP 查询延迟）

## 10. 选型决策

```
业务交易 → MySQL / Oracle（强一致）
实时分析 → Doris / StarRocks / ClickHouse
离线分析 → Hive / Spark SQL
日志分析 → ClickHouse / ES
数据湖 → Iceberg + Trino / Spark / Flink
```

## 🔗 下一步
- [Inmon vs Kimball](/08-modeling/inmon-kimball)
- [数仓架构](/09-dw-architecture/snowflake)
- [OLAP 引擎 ClickHouse](/12-olap-engine/clickhouse)
