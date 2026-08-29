---
title: Flink CDC 实时同步
date: 2026-08-15  # date-auto-injected
---
# Flink CDC

## 1. 什么是 CDC

CDC（Change Data Capture）= 捕获数据库的变更（insert / update / delete），实时同步到下游。

## 2. Flink CDC 架构

```
源数据库 (MySQL/PG/MongoDB)
  ↓
  Debezium / Flink CDC Source
  读取 binlog / redo log
  ↓
  Flink 流处理（可选：join / aggregate / filter）
  ↓
  目标系统（Kafka / Iceberg / Hudi / ES）
```

## 3. 实战：MySQL → Kafka

```sql
-- 1. 开启 MySQL binlog
SET GLOBAL binlog_format = 'ROW';
SET GLOBAL binlog_row_image = 'FULL';
FLUSH PRIVILEGES;
```

```java
DataStream<String> source = env
  .fromSource(
    MySqlSource.<String>builder()
      .hostname("mysql-host")
      .port(3306)
      .databaseList("mydb")
      .tableList("mydb.orders")
      .username("cdc")
      .password("xxx")
      .serverTimeZone("Asia/Shanghai")
      .deserializer(new JsonDebeziumDeserializationSchema())
      .build(),
    WatermarkStrategy.<String>forBoundedOutOfOrderness(Duration.ofSeconds(5))
      .withTimestampAssigner((e, ts) -> extractTs(e)),
    SourceFunction.SourceOutputType.ALL
  );

// 1. 直接发到 Kafka
source.sinkTo(KafkaSink.<String>builder()
  .setBootstrapServers("kafka:9092")
  .setRecordSerializer(...).build());

// 2. 写入 Iceberg（数据湖）
source.map(s -> parseOrder(s))
  .sinkTo(IcebergSink.forInput(...));

env.execute("MySQL CDC");
```

## 4. CDC 模式

### 4.1 基于 binlog / redo log

```
MySQL binlog → Debezium → Kafka → Flink → 下游
PG WAL    → Debezium → Kafka → Flink → 下游
MongoDB oplog → Debezium → Kafka → Flink → 下游
```

**优点**：不侵入应用（直接读 log）
**缺点**：侵入数据库（需要 binlog）

### 4.2 基于 trigger

```sql
CREATE TRIGGER orders_cdc
AFTER INSERT OR UPDATE OR DELETE ON orders
FOR EACH ROW
BEGIN
  INSERT INTO cdc_log (...) VALUES (...);
END;
```

**优点**：不侵入数据库
**缺点**：影响写性能

## 5. 实战场景

| 场景 | 方案 |
|------|------|
| MySQL → Kafka | Flink CDC + Debezium |
| MySQL → 数据湖 | Flink CDC → Iceberg / Hudi |
| MySQL → ES 搜索 | Flink CDC → ES |
| MySQL → ClickHouse | Flink CDC → CH |
| 多源 → ODS → DWD | Flink CDC + Kafka + Flink SQL |
| PG → 多目标 | Debezium + Kafka Connect |

## 6. 实战案例：MySQL → 数据湖

```java
// Source: MySQL CDC
DataStream<SourceRecord> source = env
  .fromSource(MySqlSource.<SourceRecord>builder()...build(), ...)
  .filter(s -> s.table().equals("orders"));

// Map → DWD model
DataStream<Orders> orders = source
  .map(s -> Orders.fromBytes(s.value()))
  .filter(o -> o.amount > 0);

// Sink: Iceberg
orders.addSink(IcebergSink.builder()
  .forInput(new SimpleVersionedSerializer<Orders>(Orders.class))
  .to("hdfs:///data/iceberg/orders")
  .build());

env.execute("MySQL → Iceberg");
```

## 7. 实战：MySQL → ES（搜索 + 宽表）

```java
// CDC → Kafka → Flink → ES
DataStream<Order> orders = env
  .addSource(new FlinkKafkaConsumer<>("orders", deser))
  .keyBy(Order::getId)
  .process(new OrderIndexBuilder());

orders.sinkTo(new ElasticsearchSink.Builder<>()
  .setHosts(new HttpHost("es", 9200, "http"))
  .setEmitter(new OrderEmitter())
  .build());
```

## 8. CDC 延迟 vs 准确性

| 模式 | 延迟 | 准确性 | 适用 |
|------|------|--------|------|
| 实时 CDC | 秒级 | 高 | 实时数仓 / 搜索 |
| 准实时（5min） | 分钟 | 高 | 通用 |
| 批处理 | 小时 | 高 | T+1 |

## 9. 实战踩坑

### 9.1 全量同步 vs 增量同步

```
全量：首次启动 → 全表 select
增量：CDC binlog（位点）
  → 记录 binlog 位点（Kafka offset / Redis）
  → 重启从位点继续
```

### 9.2 Schema 变更

```
字段增加 / 减少 / 重命名 → 实时处理
解决方法：
  1. 固定 schema（保留所有字段为 string，动态解析）
  2. Avro schema 演进
  3. DDL 事件捕获（schema 变更触发重建）
```

## 10. 实战：Debezium 替代方案

| 工具 | 特点 |
|------|------|
| **Flink CDC** | 集成 Flink，exactly-once |
| **Debezium** | 独立 CDC 框架，写 Kafka |
| **Kafka Connect JDBC Source** | 定期轮询，慢 |
| **DataX** | 阿里，离线批量 |
| **SeaTunnel** | 国产，CDC + 实时 |

## 11. 实战 checklist

- [ ] MySQL binlog 开启（ROW 模式）
- [ ] CDC 用户权限（REPLICATION SLAVE / CLIENT）
- [ ] Flink Checkpoint 配置（10-60s）
- [ ] Sink 幂等或 2PC
- [ ] Schema 演进策略
- [ ] 监控（CDC 延迟 / 积压）

## 12. 实战案例：MySQL → Iceberg 实时入湖

```
架构：
  MySQL（业务库）
   ↓ Debezium
  Kafka（CDC topic）
   ↓ Flink CDC
  Flink（流处理）
   ↓
  Iceberg（数据湖，事务表）

效果：
  - 延迟 < 5 秒
  - exactly-once
  - 支持 schema 演进
  - 支持 time travel
```

## 🔗 下一步
- [Flink 架构](/05-flink/architecture)
- [状态与 Checkpoint](/05-flink/state)
- [Exactly-once](/05-flink/exactly-once)
- [数据湖 三剑客](/10-data-lake/three-pillars)
