---
title: Log / TinyLog / StripeLog 引擎
date: 2026-08-15  # date-auto-injected
description: 小数据量场景的简单日志引擎，性能差但写入极简
---

# Log / TinyLog / StripeLog 引擎

Log 引擎家族适用于**小数据量**场景（百万级以内），它们：
- 没有 MergeTree 的后台合并
- 没有索引
- 没有并发读
- 写入是 append-only

## TinyLog（最简单）

```sql
CREATE TABLE simple_logs (
  log_time DateTime,
  message String
)
ENGINE = TinyLog()

INSERT INTO simple_logs VALUES (now(), 'hello')

SELECT * FROM simple_logs
```

**特点**：
- 每列一个文件（`<column>.bin`）
- 无索引，无压缩（除了 LZ4）
- 适合一次性写入 + 全表扫描
- **不能 ALTER**（只能 DROP + CREATE）

## Log（略强于 TinyLog）

```sql
CREATE TABLE simple_logs (
  log_time DateTime,
  message String
)
ENGINE = Log()
```

**区别**：
- Log 在每个数据文件结尾有「marks」标记，支持范围查询
- 比 TinyLog 略快

## StripeLog（合并存储）

```sql
CREATE TABLE simple_logs (
  log_time DateTime,
  message String
)
ENGINE = StripeLog()
```

**特点**：
- 所有列存储在同一个 `.data` 文件中
- 写入极快（小数据量）
- 读取也很简单
- 适合「一次性导入 + 偶尔查询」

## 何时使用 Log 引擎？

| 场景 | 推荐 |
|---|---|
| 小数据量（< 百万行） + 简单写入 | Log / TinyLog |
| 一次性导入 + 全表扫描 | StripeLog |
| 大数据量 | ❌ 用 MergeTree |
| 需要并发读 | ❌ 用 MergeTree |
| 需要修改数据 | ❌ 用 MergeTree |
| 需要物化视图 | ❌ 用 MergeTree |

## 实战：临时表（ETL 中间结果）

```sql
-- ETL 第一步：导入原始数据
CREATE TABLE raw_events_tmp (
  raw_line String
)
ENGINE = TinyLog()

INSERT INTO raw_events_tmp FROM INFILE '/tmp/raw_logs.csv' FORMAT CSVWithNames

-- 第二步：解析 + 写入 MergeTree 表
INSERT INTO events
SELECT
  parseDateTimeBestEffort(JSONExtractString(raw_line, 'event_time')) AS event_time,
  toUInt64(JSONExtractString(raw_line, 'user_id')) AS user_id,
  JSONExtractString(raw_line, 'event_type') AS event_type
FROM raw_events_tmp

-- 清理
DROP TABLE raw_events_tmp
```

## 与 MergeTree 的对比

| 维度 | Log 家族 | MergeTree |
|---|---|---|
| **数据量** | < 百万行 | 任意（PB 级） |
| **后台合并** | ❌ | ✅ |
| **主键索引** | ❌ | ✅ |
| **并发读** | ❌ | ✅ |
| **修改数据** | ❌ | ✅（弱） |
| **分区** | ❌ | ✅ |
| **TTL** | ❌ | ✅ |
| **写入性能** | 高（小数据） | 中 |
| **查询性能** | 低（全表扫） | 高 |

## 实战：ClickHouse 内部表

ClickHouse 自身大量使用 Log 引擎（如 `system.query_log`、`system.trace_log` 等）：

```sql
SELECT * FROM system.tables
WHERE engine LIKE '%Log%'
```

## 实战：调试中临时存储

```sql
-- 调试某条 SQL 时，临时存结果
CREATE TABLE debug_tmp
ENGINE = TinyLog()
AS SELECT * FROM events WHERE user_id = 12345 LIMIT 1000

-- 查看调试结果
SELECT * FROM debug_tmp

-- 调试完成清理
DROP TABLE debug_tmp
```

## 实战：ClickHouse 自带的系统表

ClickHouse 自身用 Log 家族存储大量系统表：

| 系统表 | 引擎 | 用途 |
|---|---|---|
| `system.query_log` | MergeTree（不是 Log） | 查询历史 |
| `system.zookeeper_log` | Log | ZK 操作日志 |
| `system.trace_log` | MergeTree | Trace span |
| `system.part_log` | MergeTree | 分片操作日志 |

**注意**，ClickHouse v22+ 的系统表主要用 MergeTree（不是 Log），但日志型元信息（ZK log / metric log）仍可用 Log 引擎。

## 实战：ETL Pipeline 中间数据

```sql
-- Pipeline 第一阶段：原始数据导入
CREATE TABLE etl_step1_raw ENGINE = TinyLog()
AS SELECT * FROM url('https://example.com/data.csv', CSVWithNames)

-- Pipeline 第二阶段：清洗
CREATE TABLE etl_step2_clean ENGINE = TinyLog()
AS SELECT
  toUInt64(JSONExtractString(raw_line, 'user_id')) AS user_id,
  parseDateTimeBestEffort(JSONExtractString(raw_line, 'event_time')) AS event_time,
  JSONExtractString(raw_line, 'event_type') AS event_type
FROM etl_step1_raw

-- Pipeline 第三阶段：写入 MergeTree 目标表
INSERT INTO events SELECT * FROM etl_step2_clean

-- 清理临时表
DROP TABLE etl_step1_raw
DROP TABLE etl_step2_clean
```

## 性能与限制

### 性能特征

```text
- 写入速度（百万行内）：极快（无后台合并）
- 读取速度：取决于全表扫（无索引）
- 并发读：❌ 不支持
- 修改数据：❌ 不支持
- 数据量：建议 ≤ 百万行
```

### 何时不用 Log 引擎

| 场景 | 不推荐 Log |
|---|---|
| 数据量 > 千万行 | 改用 MergeTree |
| 需要并发查询 | 改用 MergeTree |
| 需要修改/删除 | 改用 MergeTree |
| 需要分区 | 改用 MergeTree |
| 需要 TTL | 改用 MergeTree |

## 下一步

- 学习 MergeTree 家族：见 [mergetree-family.md](./mergetree-family.md)
- 学习 Kafka 引擎：见 [kafka-engine.md](./kafka-engine.md)
