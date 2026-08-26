---
title: TimescaleDB 时序扩展
description: PG 时序数据库
---

# TimescaleDB 时序扩展

> **TL;DR**：TimescaleDB = PG 的**时序数据库扩展**。**自动分区 + 列式压缩 + 保留策略 + 连续聚合**，**单 PG 实例支持 100 亿行时序数据**。

## 一句话定义

```
TimescaleDB = PG 时序扩展
            = 超表（hypertable）+ chunk（按时间/空间分区）
            = 自动管理、查询语法不变
```

## 与原生分区的对比

| 维度 | 原生分区 | TimescaleDB |
|---|---|---|
| 自动创建分区 | ✗ | ✓ |
| 自动压缩 | ✗ | ✓ |
| 自动保留 | ✗ | ✓ |
| 连续聚合 | ✗ | ✓ |
| 分布式 | ✗ | ✓（多节点） |
| SQL 兼容 | ✓ | ✓ |

## 安装

```bash
# Ubuntu
apt install timescaledb-2-postgresql-15

# 配置
echo "shared_preload_libraries = 'timescaledb'" >> /etc/postgresql/15/main/postgresql.conf
```

```sql
CREATE EXTENSION timescaledb;
```

## 超表（Hypertable）

```sql
-- 1. 创普通表
CREATE TABLE metrics (
  ts TIMESTAMPTZ NOT NULL,
  sensor_id INT NOT NULL,
  cpu NUMERIC(5,2),
  mem NUMERIC(5,2)
);

-- 2. 转超表（按时间分区）
SELECT create_hypertable('metrics', 'ts');

-- 3. 插入数据（应用无感知）
INSERT INTO metrics (ts, sensor_id, cpu, mem) VALUES
  (now(), 1, 80.5, 60.2),
  (now() - interval '1 hour', 1, 75.3, 58.1);
```

## 自动分区

TimescaleDB 自动按时间创建 chunk：

```
metrics chunk:
  - chunk_2026_08_01 (1 天)
  - chunk_2026_08_02
  - chunk_2026_08_03
  ...
默认 chunk_time_interval = 7 days
```

**调整 chunk 大小**：

```sql
SELECT set_chunk_time_interval('metrics', INTERVAL '1 day');
-- 1 天一个 chunk（小数据量）
-- 1 周一个 chunk（大数据量）
```

## 压缩

```sql
-- 1. 启用压缩（按时间降序）
ALTER TABLE metrics SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'sensor_id',
  timescaledb.compress_orderby = 'ts DESC'
);

-- 2. 手动压缩
SELECT compress_chunk(c) FROM show_chunks('metrics') c;

-- 3. 自动压缩策略
SELECT add_compression_policy('metrics', INTERVAL '7 days');
-- 7 天前的 chunk 自动压缩
```

**压缩效果**：

```
压缩前：100 GB
压缩后：5-10 GB（10-20x 压缩）
查询性能：基本不变（列存）
```

## 保留策略

```sql
-- 自动删除 N 天前的数据
SELECT add_retention_policy('metrics', INTERVAL '90 days');
-- 90 天前的 chunk 自动删除
```

## 连续聚合（Continuous Aggregate）

```sql
-- 1. 创建连续聚合
CREATE MATERIALIZED VIEW metrics_hourly
WITH (timescaledb.continuous) AS
SELECT
  time_bucket('1 hour', ts) AS bucket,
  sensor_id,
  avg(cpu) AS avg_cpu,
  max(cpu) AS max_cpu,
  avg(mem) AS avg_mem
FROM metrics
GROUP BY bucket, sensor_id;

-- 2. 自动刷新策略
SELECT add_continuous_aggregate_policy('metrics_hourly',
  start_offset => INTERVAL '1 day',
  end_offset => INTERVAL '1 hour',
  schedule_interval => INTERVAL '1 hour');

-- 3. 查询（实时 + 历史）
SELECT * FROM metrics_hourly
WHERE bucket >= now() - interval '7 days'
ORDER BY bucket DESC;
```

**比 PG 原生物化视图**：

```
✓ 自动刷新（策略）
✓ 历史 chunk + 实时数据
✓ 支持 UPDATE 底层
```

## 实战案例

### 案例 1：监控指标存储

```sql
CREATE TABLE metrics (
  ts TIMESTAMPTZ NOT NULL,
  host TEXT NOT NULL,
  metric TEXT NOT NULL,
  value DOUBLE PRECISION
);

SELECT create_hypertable('metrics', 'ts');

-- 索引
CREATE INDEX idx_metrics_host ON metrics (host, ts DESC);
CREATE INDEX idx_metrics_metric ON metrics (metric, ts DESC);

-- 7 天后压缩
ALTER TABLE metrics SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'host, metric',
  timescaledb.compress_orderby = 'ts DESC'
);
SELECT add_compression_policy('metrics', INTERVAL '7 days');

-- 90 天后删除
SELECT add_retention_policy('metrics', INTERVAL '90 days');
```

### 案例 2：IoT 传感器数据

```sql
CREATE TABLE sensor_data (
  ts TIMESTAMPTZ NOT NULL,
  sensor_id INT NOT NULL,
  temperature NUMERIC(5,2),
  humidity NUMERIC(5,2)
);

-- 按时间和 sensor 分区
SELECT create_hypertable('sensor_data', 'ts', chunk_time_interval => INTERVAL '1 day');

-- 压缩 + 保留
ALTER TABLE sensor_data SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'sensor_id',
  timescaledb.compress_orderby = 'ts DESC'
);
SELECT add_compression_policy('sensor_data', INTERVAL '30 days');
SELECT add_retention_policy('sensor_data', INTERVAL '365 days');
```

### 案例 3：金融行情（K线）

```sql
CREATE TABLE stock_prices (
  ts TIMESTAMPTZ NOT NULL,
  symbol TEXT NOT NULL,
  open NUMERIC(10,4),
  high NUMERIC(10,4),
  low NUMERIC(10,4),
  close NUMERIC(10,4),
  volume BIGINT
);

SELECT create_hypertable('stock_prices', 'ts');

-- 连续聚合生成 K 线
CREATE MATERIALIZED VIEW stock_klines_1min
WITH (timescaledb.continuous) AS
SELECT
  time_bucket('1 minute', ts) AS bucket,
  symbol,
  first(open, ts) AS open,
  max(high) AS high,
  min(low) AS low,
  last(close, ts) AS close,
  sum(volume) AS volume
FROM stock_prices
GROUP BY bucket, symbol;
```

## 监控

```sql
-- 1. 超表信息
SELECT * FROM timescaledb_information.hypertables;

-- 2. chunk 列表
SELECT * FROM timescaledb_information.chunks
WHERE hypertable_name = 'metrics';

-- 3. 压缩统计
SELECT * FROM timescaledb_information.compressed_chunk_stats;

-- 4. 策略
SELECT * FROM timescaledb_information.jobs
WHERE application_name LIKE '%Compression%'
   OR application_name LIKE '%Retention%';
```

## 分布式（多节点）

```sql
-- 1. 添加 data node
SELECT add_data_node('tsdb1.db', chunk_time_interval => INTERVAL '1 day');
SELECT add_data_node('tsdb2.db', chunk_time_interval => INTERVAL '1 day');

-- 2. 分布式超表
SELECT create_distributed_hypertable('metrics', 'ts');
```

## 一句话总结

> **TimescaleDB = PG 时序数据库**：**自动分区 + 列式压缩 + 保留策略 + 连续聚合**。**100 亿行单实例可扛**。**应用 SQL 零修改**，**只 CREATE EXTENSION + create_hypertable**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>


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
