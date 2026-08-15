---
title: BRIN 索引
description: Block Range 索引（适合时序数据）
---

# BRIN 索引

> **TL;DR**：BRIN（Block Range Index）= **块范围索引**，索引大小只有 B-tree 的 **1/100**。**适合自然有序的大表（时序、日志）**，**查询范围扫描性能接近 B-tree**。

## 一句话定义

```
BRIN = 把表按块（默认 128 个 page = 1MB）分组
     = 每个块记录一组元数据（min/max/sum）
     = 查询时先看元数据，命中范围才深入扫描
```

## 适用场景

```
✓ 时间戳 / 序号单调递增的大表（> 1 亿行）
✓ 日志、事件、监控数据
✓ 数据按物理顺序写入（INSERT 顺序）
✓ 查询多按时间范围扫描

✗ 数据随机分布（不适用）
✗ 需要等值查询 + 大量更新
✗ 小表（< 1000 万行）
```

## 基本使用

```sql
-- 1. 创建 BRIN 索引
CREATE TABLE events (
  id BIGSERIAL,
  occurred_at TIMESTAMPTZ NOT NULL,
  data JSONB
);

CREATE INDEX idx_events_time ON events USING BRIN (occurred_at);

-- 2. 范围查询（用 BRIN）
SELECT * FROM events 
WHERE occurred_at >= '2026-08-01' AND occurred_at < '2026-08-09';

-- EXPLAIN 看
EXPLAIN SELECT * FROM events 
WHERE occurred_at >= '2026-08-01' AND occurred_at < '2026-08-09';

-- Bitmap Heap Scan on events
--   Recheck Cond: ...
--   ->  Bitmap Index Scan on idx_events_time
```

## 关键参数

### pages_per_range

```sql
-- 默认 128 (1MB)
CREATE INDEX idx_events_time ON events USING BRIN (occurred_at) WITH (pages_per_range = 32);
```

**调优**：
- **更小**（如 16）= 更精细，但索引更大、扫描稍慢
- **更大**（如 256）= 更粗，索引更小，但可能漏过滤（需要 recheck）

### autosummarize

```sql
-- PG 11+ 自动总结
ALTER INDEX idx_events_time SET (autosummarize = on);
```

## BRIN vs B-tree

| 维度 | B-tree | BRIN |
|---|---|---|
| 索引大小 | 100% | **1-5%** |
| 查询速度 | 极快 | 快（有 recheck 开销） |
| 等值查询 | ✓ | ✗（不适用） |
| 范围查询 | ✓ | ✓ |
| 排序 | ✓ | ✗ |
| 适用数据 | 任意 | 自然有序 |

## 实战案例

### 案例 1：百亿行日志

```sql
CREATE TABLE app_logs (
  id BIGSERIAL,
  ts TIMESTAMPTZ NOT NULL DEFAULT now(),
  level TEXT,
  message TEXT
);

-- 1. 按月分区
CREATE TABLE app_logs_2026_08 PARTITION OF app_logs
  FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');

-- 2. 每个分区建 BRIN 索引
CREATE INDEX idx_logs_2026_08_ts ON app_logs_2026_08 USING BRIN (ts);

-- 索引大小对比：
-- B-tree: 500 MB
-- BRIN:   5 MB (1%)
```

### 案例 2：监控指标数据

```sql
CREATE TABLE metrics (
  id BIGSERIAL,
  ts TIMESTAMPTZ NOT NULL DEFAULT now(),
  host TEXT,
  cpu NUMERIC(5,2)
);

-- 查某个时间段的 CPU 数据
CREATE INDEX idx_metrics_ts ON metrics USING BRIN (ts);

SELECT host, avg(cpu) FROM metrics
WHERE ts >= now() - interval '1 hour'
GROUP BY host;
-- BRIN 索引快速定位 1MB 范围，再 GROUP BY
```

### 案例 3：传感器时序

```sql
CREATE TABLE sensor_data (
  sensor_id INT,
  recorded_at TIMESTAMPTZ NOT NULL,
  value NUMERIC
);

-- 按时间建 BRIN
CREATE INDEX idx_sensor_time ON sensor_data USING BRIN (recorded_at);

-- 查最近 1 小时
SELECT * FROM sensor_data
WHERE recorded_at >= now() - interval '1 hour'
  AND sensor_id = 123;

-- 复合查询 = BRIN 粗筛 + 索引细筛
```

## 与分区表配合

**BRIN + RANGE 分区 = 大表最佳组合**：

```sql
-- 1. 按月分区
CREATE TABLE events (...) PARTITION BY RANGE (occurred_at);
CREATE TABLE events_2026_08 PARTITION OF events
  FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');

-- 2. 每分区建 BRIN
CREATE INDEX idx_events_2026_08_brin 
  ON events_2026_08 USING BRIN (occurred_at);

-- 3. 查询：PG 自动 partition pruning + BRIN 块过滤
SELECT * FROM events
WHERE occurred_at >= '2026-08-01' AND occurred_at < '2026-08-02';
-- 只扫 events_2026_08 分区 → BRIN 进一步过滤
```

## 注意事项

### 1. 大量 UPDATE 会失效

```
BRIN 记录每块的 min/max → UPDATE 后可能不再准确
PG 自动 recheck，但性能下降
解决：定期 REINDEX
```

### 2. 顺序写入很重要

```sql
-- ✓ 按时间顺序 INSERT
INSERT INTO events (ts) VALUES 
  ('2026-08-01'), ('2026-08-02'), ('2026-08-03');

-- ✗ 乱序 INSERT（多个 worker 并行写入）
-- BRIN 索引效果差
```

## 一句话总结

> **BRIN = 时序数据的最佳索引**：索引大小只有 B-tree 的 1-5%，**查询范围扫描性能接近 B-tree**。**前提：数据按物理顺序写入**（典型场景：日志、事件、监控）。**配合 RANGE 分区 = 大表最佳方案**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
