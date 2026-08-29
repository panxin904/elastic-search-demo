---
title: Flink CDC 实时同步
date: 2026-08-15  # date-auto-injected
---
# Flink CDC 与实时数据同步

## 1. CDC 三种方式

| 方式 | 原理 | 延迟 | 影响 |
|------|------|------|------|
| **基于 trigger** | 数据库 trigger | 秒 | 影响写 |
| **基于 binlog / WAL** | 读数据库 log | 毫秒-秒 | 不影响（只读）|
| **基于时间戳** | 定期轮询 | 分钟-小时 | 不影响 |

**生产首选**：binlog（不侵入应用，延迟低）。

## 2. Flink CDC 架构

```
MySQL binlog
   ↓
  Debezium / Flink CDC Source
   ↓
  Flink 算子（transform / filter / join）
   ↓
  Sink：
    - Kafka（后续处理）
    - 数据湖（Iceberg / Hudi / Delta）
    - OLAP（ClickHouse / Doris / ES）
    - DB（MySQL / PG）
```

## 3. Flink CDC Connector

```xml
<dependency>
  <groupId>com.ververica</groupId>
  <artifactId>flink-connector-debezium</artifactId>
  <version>2.5.0</version>
</dependency>
<dependency>
  <groupId>com.ververica</groupId>
  <artifactId>flink-sql-connector-mysql-cdc</artifactId>
  <version>2.5.0</version>
</dependency>
```

```sql
-- Flink SQL CDC（推荐）
CREATE TABLE orders_cdc (
  id BIGINT,
  user_id BIGINT,
  amount DECIMAL(10,2),
  ts TIMESTAMP(3),
  WATERMARK FOR ts AS ts - INTERVAL '5' SECOND
) WITH (
  'connector' = 'mysql-cdc',
  'hostname' = 'mysql-host',
  'port' = '3306',
  'username' = 'cdc',
  'password' = 'xxx',
  'database-name' = 'mydb',
  'table-name' = 'orders',
  'debezium.snapshot.mode' = 'initial'
);
```

## 4. 实战：MySQL → Iceberg 实时入湖

```sql
-- 1. CDC source
CREATE TABLE orders_cdc (...) WITH ('connector' = 'mysql-cdc', ...);

-- 2. 数据湖 sink
CREATE TABLE orders_iceberg (
  id BIGINT,
  user_id BIGINT,
  amount DECIMAL(10,2),
  ts TIMESTAMP(3)
) WITH (
  'connector' = 'iceberg',
  'catalog-name' = 'my_catalog',
  'database-name' = 'dw',
  'table-name' = 'orders'
);

-- 3. 实时 ETL
INSERT INTO orders_iceberg
SELECT id, user_id, amount, ts FROM orders_cdc;
```

## 5. 实战：MySQL → Kafka → Flink → ClickHouse

```sql
-- Kafka 中转
CREATE TABLE orders_kafka (
  id BIGINT,
  user_id BIGINT,
  amount DECIMAL(10,2),
  ts TIMESTAMP(3),
  WATERMARK FOR ts AS ts - INTERVAL '5' SECOND
) WITH (
  'connector' = 'kafka',
  'topic' = 'orders.cdc',
  'format' = 'debezium-json',
  'scan.startup.mode' = 'earliest-offset'
);

-- 写入 ClickHouse
INSERT INTO clickhouse_sink
SELECT id, user_id, amount, ts FROM orders_kafka;
```

## 6. 实战踩坑

### 6.1 binlog 开启

```sql
-- MySQL 必开
SET GLOBAL binlog_format = 'ROW';
SET GLOBAL binlog_row_image = 'FULL';
FLUSH PRIVILEGES;
```

### 6.2 CDC 用户权限

```sql
-- 需要 SELECT / RELOAD / LOCK TABLES / REPLICATION SLAVE / REPLICATION CLIENT
GRANT SELECT, RELOAD, LOCK TABLES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'cdc'@'%';
```

### 6.3 全量 + 增量

```
首次：全表快照（snapshot.mode = initial）
之后：仅增量（binlog）
重启：从 binlog 位点继续
```

## 7. Flink CDC vs DataX vs Canal

| 工具 | 特点 |
|------|------|
| **Flink CDC** | 集成 Flink（exactly-once / 流批一体） |
| **DataX** | 阿里，离线批量同步 |
| **Canal** | 阿里，MySQL binlog → MQ |
| **Debezium** | 独立 CDC，写 Kafka |
| **SeaTunnel** | 国产，CDC + 实时 |

## 8. 实战案例：MySQL → 数据湖（Iceberg）

```
架构：
  MySQL（业务库）
   ↓ Flink CDC（binlog）
  Flink SQL（transform）
   ↓
  Iceberg（数据湖，事务表）
  
效果：
  - 延迟 < 5 秒
  - exactly-once
  - 支持 schema 演进
  - 支持 time travel
```

## 9. 实战选型

| 场景 | 选 |
|------|-----|
| MySQL → 数据湖 | Flink CDC + Iceberg |
| MySQL → Kafka | Flink CDC / Debezium |
| MySQL → ES / ClickHouse | Flink CDC / Canal |
| 多源汇聚 | Flink CDC |
| 一次性全量 | DataX / sqoop |

## 10. 实战 checklist

- [ ] MySQL binlog ROW 模式
- [ ] CDC 用户权限
- [ ] Flink CDC connector
- [ ] Checkpoint（10-60s）
- [ ] Sink 幂等（Iceberg / Kafka）
- [ ] Schema 演进策略
- [ ] 监控（CDC 延迟 / 积压）

## 11. 实战代码

```java
// Flink CDC 启动（Java）
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
env.enableCheckpointing(60_000L);

MySqlSource<String> source = MySqlSource.<String>builder()
  .hostname("mysql-host")
  .port(3306)
  .databaseList("mydb")
  .tableList("mydb.orders")
  .username("cdc")
  .password("xxx")
  .deserializer(new JsonDebeziumDeserializationSchema())
  .startupOptions(StartupOptions.initial())
  .build();

DataStream<String> stream = env.fromSource(source,
  WatermarkStrategy.noWatermarks(),
  "MySQL CDC Source");

stream.map(s -> parse(s))
  .sinkTo(...);
env.execute("MySQL CDC");
```

## 🔗 下一步
- [Flink 架构](/05-flink/architecture)
- [Kafka Streams](/07-kafka-streaming/streams)
- [数据湖 三剑客](/10-data-lake/three-pillars)
