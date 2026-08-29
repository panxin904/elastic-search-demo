---
title: Spark Structured Streaming
date: 2026-08-15  # date-auto-injected
---
# Spark Structured Streaming

## 1. 是什么

基于 Spark SQL 的流处理引擎：把流当作无限增长的表（unbounded table）。

## 2. 核心概念

```
流 = 持续 append 的 InputTable
  ↓ trigger
  处理（micro-batch 或 continuous）
  ↓
结果表（OutputTable）
  多种 output mode:
    - append: 只追加新行
    - update: 更新结果（聚合）
    - complete: 整个结果重写
```

## 3. Source

```python
# Kafka
df = spark.readStream   .format("kafka")   .option("kafka.bootstrap.servers", "host:9092")   .option("subscribe", "events")   .load()

# 解析 value
events = df.selectExpr(
  "CAST(value AS STRING) as json",
  "timestamp"
)
parsed = events.select(F.from_json("json", schema).alias("data"), "timestamp")

# File source（监控目录）
df = spark.readStream.schema(schema).csv("hdfs:///data/landing/")

# Rate source（测试）
df = spark.readStream.format("rate").option("rowsPerSecond", 10).load()
```

## 4. Sink

```python
# Kafka
query = df.writeStream   .format("kafka")   .option("kafka.bootstrap.servers", "host:9092")   .option("topic", "output")   .option("checkpointLocation", "hdfs:///ck/output/")   .start()

# File sink
df.writeStream   .format("parquet")   .option("path", "hdfs:///data/out/")   .option("checkpointLocation", "hdfs:///ck/")   .outputMode("append")   .start()

# ForeachBatch（自定义）
df.writeStream.foreachBatch(lambda df, epoch: df.write.parquet(f"hdfs:///out/{epoch}")).start()
```

## 5. Trigger

```python
# Micro-batch（默认）
df.writeStream.trigger(processingTime="10 seconds").start()

# Once（一次性批）
df.writeStream.trigger(once=True).start()

# Continuous（实验性，低延迟 ~1ms）
df.writeStream.trigger(continuous="10 milliseconds").start()
```

## 6. 窗口与水印

```python
# 滚动窗口（10 分钟）
windowed = df.groupBy(
  F.window("ts", "10 minutes"),
  "user_id"
).count()

# 水印（处理乱序事件）
df.withWatermark("ts", "5 minutes")   .groupBy(F.window("ts", "10 minutes"), "user_id")   .count()
```

## 7. Output Mode

```python
# Append：只追加新结果（无聚合）
# Update：更新结果（聚合后变化）
# Complete：每次完整输出

# 示例
df.groupBy("user").count()   .writeStream   .outputMode("complete") \  # 完整输出
  .format("console")   .start()
```

## 8. 实战案例：实时统计

```python
from pyspark.sql import functions as F

# 1. 从 Kafka 读
stream = spark.readStream   .format("kafka")   .option("kafka.bootstrap.servers", "host:9092")   .option("subscribe", "user_events")   .load()   .selectExpr("CAST(value AS STRING) as json", "timestamp")   .select(F.from_json("json", "user_id INT, event STRING").alias("data"), "timestamp")

# 2. 每分钟统计
counts = stream.groupBy(
  F.window("timestamp", "1 minute"),
  "data.user_id",
  "data.event"
).count()

# 3. 输出到 Kafka
query = counts.writeStream   .format("kafka")   .option("kafka.bootstrap.servers", "host:9092")   .option("topic", "user_event_count")   .option("checkpointLocation", "hdfs:///ck/event_count/")   .outputMode("update")   .start()

query.awaitTermination()
```

## 9. 容错

| 机制 | 说明 |
|------|------|
| Checkpoint | 状态 / offset 持久化（HDFS / S3） |
| Write Ahead Log | 计算前先写日志 |
| Idempotent Sink | 多次写结果相同 |
| Exactly-once | checkpoint + WAL + idempotent sink |

## 10. Spark Structured Streaming vs Flink

| | Spark SS | Flink |
|--|-----------|--------|
| 处理模型 | Micro-batch（默认）/ Continuous | True streaming |
| 延迟 | 秒级（默认）/ 毫秒（continuous） | 毫秒级（核心） |
| 状态 | 内置 + 自定义 | 内置 + RocksDB |
| Exactly-once | ✅ | ✅（核心优势） |
| 流批一体 | ✅ 同一套 API | ✅ |
| SQL 支持 | ✅ Spark SQL | ✅ Flink SQL |
| 生态 | Spark 生态（强） | Flink 生态（独立） |
| 适合 | ETL / 离线 + 流 | 实时计算（强） |

## 11. 实战调优

```python
# 1. 并行度
spark.conf.set("spark.sql.shuffle.partitions", "200")

# 2. Watermark
df.withWatermark("ts", "10 minutes")  # 乱序容忍

# 3. Trigger
.trigger(processingTime="5 seconds")  # 控制延迟

# 4. State Store（生产推荐 RocksDB）
spark.conf.set(
  "spark.sql.streaming.stateStore.providerClass",
  "org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider"
)

# 5. Checkpoint 周期
.option("checkpointLocation", "hdfs:///ck/") .trigger(processingTime="1 minute")
```

## 12. 实战 checklist

- [ ] Checkpoint 路径（生产必须）
- [ ] Output mode 选对（append / update / complete）
- [ ] Watermark 处理乱序
- [ ] Schema 演进（additive / allow）
- [ ] State Store（生产 RocksDB）
- [ ] Trigger 调优（延迟 vs 吞吐）
- [ ] 监控（输入 lag / 处理延迟 / 输出 lag）

## 🔗 下一步
- [Spark Core / RDD](/04-spark/rdd)
- [Spark SQL / DataFrame](/04-spark/dataframe)
- [Spark 调优](/04-spark/tuning)
- [Flink 架构](/05-flink/architecture)
