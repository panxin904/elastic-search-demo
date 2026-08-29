---
title: 批 / 流计算
date: 2026-08-15  # date-auto-injected
---
# 批 vs 流计算

## 1. 两种范式

### 批处理（Batch）

```
数据 → 攒一批 → 处理 → 写结果
  特点：吞吐高、延迟高（分钟-小时）
  适合：日终报表 / 离线分析 / 全量数据
  代表：Hadoop / Spark SQL / Hive
```

### 流处理（Stream）

```
数据 → 实时 → 处理 → 实时输出
  特点：延迟低（毫秒-秒）、吞吐受限于状态
  适合：实时监控 / 报警 / 实时推荐
  代表：Flink / Kafka Streams / Spark Streaming
```

## 2. 对比

| | 批处理 | 流处理 |
|--|--------|--------|
| 延迟 | 分钟-小时 | 毫秒-秒 |
| 吞吐 | 极高 | 中-高 |
| 数据量 | PB | GB-TB / 天 |
| 状态 | 无 / 简单 | 复杂（exactly-once） |
| 复杂度 | 低 | 高 |
| 成本 | 存储 / 算力 | 持续算力 |
| 适合 | 报表 / 训练 | 监控 / 报警 / 实时计算 |

## 3. 三大架构

### 3.1 Lambda 架构

```
Batch Layer   ──→  Serving Layer
  (全量重算)          (合并)
Speed Layer   ──→  
  (增量新数据)
```

**优点**：全量数据准确 + 实时数据新鲜
**缺点**：维护两套代码（批 + 流）

### 3.2 Kappa 架构

```
Stream  ──→  Serving
  (单一 Kafka 流)
```

**优点**：一套代码（都是流处理）
**缺点**：需要重算历史（replay Kafka）

### 3.3 Lakehouse 架构

```
Stream + Batch → 统一的 Lakehouse 表（Iceberg / Hudi）
                 Spark / Flink 读写同一张表
```

**优点**：流批一体 + 事务 + Time Travel
**代表**：Databricks Lakehouse / Apache Iceberg / Apache Hudi

## 4. 批处理实践：Spark SQL

```sql
-- 读 raw → 清洗 → 写 dwd
INSERT OVERWRITE TABLE dwd.events
SELECT
  user_id,
  event_type,
  FROM_UNIXTIME(ts / 1000) AS event_time,
  properties
FROM ods.events
WHERE dt = '2024-01-15'
  AND event_type IS NOT NULL;
```

## 5. 流处理实践：Flink

```java
DataStream<ClickEvent> clicks = env
  .addSource(new FlinkKafkaConsumer<>("clicks", schema, props))
  .filter(c -> c.userId != null)
  .keyBy(ClickEvent::getUserId)
  .window(TumblingEventTimeWindows.of(Time.minutes(5)))
  .aggregate(new CountAggregator(), new ClickWindow())
  .keyBy(...)
  .process(...);
```

## 6. 流批一体实践

```sql
-- Iceberg 流批一体表
CREATE TABLE events (
  ts TIMESTAMP,
  user_id BIGINT,
  cnt INT
) WITH (
  'connector' = 'iceberg',
  'format-version' = '2',
  'write.format.default' = 'parquet'
);

-- 流式写入（Kafka → Iceberg）
INSERT INTO events /*+ OPTIONS('sink-versioned' = 'true') */ 
SELECT * FROM kafka_events;

-- 批量覆写（每日 ETL）
INSERT OVERWRITE events PARTITION (dt='2024-01-15')
SELECT * FROM stage_events;
```

## 7. 实战选型

| 场景 | 推荐 |
|------|------|
| 日终报表 / 离线指标 | Spark SQL + Hive |
| 实时监控 / 报警 | Flink / Kafka Streams |
| 实时特征 / 推荐 | Flink + Redis |
| 实时 + 离线融合 | Flink + Iceberg |
| 复杂 ETL 编排 | Airflow + Spark / Flink |

## 8. 关键决策点

```
延迟需求：
  秒级以下 → Flink / Kafka Streams
  秒-分钟 → Spark Streaming / Flink
  分钟-小时 → Spark SQL / Hive
  小时+   → Hive / MR

数据量：
  < 1 TB / 天 → 单机 / 小集群
  1-100 TB → 大集群 / Spark / Flink
  > 100 TB → Lakehouse / 数据湖

一致性：
  at-most-once → 简单
  at-least-once → Kafka + 幂等
  exactly-once → Flink + Kafka 事务
```

## 9. Lambda vs Kappa vs Lakehouse

| 架构 | 数据处理 | 实时性 | 复杂度 | 适用 |
|------|---------|--------|--------|------|
| Lambda | 批 + 流双写 | 实时 | 高 | 强实时性 |
| Kappa | 单一 Kafka 流 | 实时 | 中 | 实时 + 全量重算 |
| Lakehouse | 统一表 | 实时 | 中 | 现代数据栈 |

## 10. 实战案例

**美团外卖实时配送调度**：
- Kafka → Flink → Redis → 派单系统
- 端到端 50ms 延迟
- 百万级订单 / 分钟

**阿里双11实时大屏**：
- Kafka → Blink → HBase → 大屏
- 全链路秒级

**抖音推荐实时特征**：
- Kafka → Flink → Redis → 在线推理
- 100ms 延迟

## 🔗 下一步
- [Spark Core / RDD](/04-spark/rdd)
- [Flink 架构](/05-flink/architecture)
- [Kafka Streams](/07-kafka-streaming/streams)
