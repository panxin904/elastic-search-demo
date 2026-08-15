---
title: Kafka Connect
---

# 🔌 Kafka Connect

> **Kafka Connect** 是 Kafka 官方的**数据集成框架**，用于在 Kafka 与外部系统（如 MySQL、Elasticsearch）之间可靠地传输数据。

## 🎯 Kafka Connect 是什么？

```
Kafka Connect = 数据导入导出框架

两种模式：
  - Source Connector：从外部系统读取数据到 Kafka
  - Sink Connector：从 Kafka 写数据到外部系统

特点：
  ✅ 分布式（可扩展）
  ✅ 容错（自动恢复）
  ✅ REST API 管理
  ✅ 插件化（丰富的 Connector 生态）
```

## 🏗️ Kafka Connect 架构

```
┌────────────────────────────────────────────────────┐
│                Kafka Connect Cluster                 │
│                                                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐    │
│  │  Worker 1  │  │  Worker 2  │  │  Worker 3  │    │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘    │
│        │               │               │            │
│  ┌─────┴───────────────┴───────────────┴──────┐    │
│  │   Source Connector   │   Sink Connector       │    │
│  │  - Debezium MySQL   │   - Elasticsearch       │    │
│  │  - JDBC             │   - S3                  │    │
│  │  - MongoDB          │   - HDFS                │    │
│  └────────────────────┴──────────────────────────┘    │
└────────────────────────────────────────────────────┘
```

## 🔧 部署 Kafka Connect

### 1. Standalone 模式（单机）

```bash
# 启动
bin/connect-standalone.sh config/connect-standalone.properties \
    config/connector1.properties config/connector2.properties
```

```properties
# connect-standalone.properties
bootstrap.servers=localhost:9092
key.converter=org.apache.kafka.connect.json.JsonConverter
value.converter=org.apache.kafka.connect.json.JsonConverter
key.converter.schemas.enable=true
value.converter.schemas.enable=true
offset.storage.file.filename=/tmp/connect.offsets
```

### 2. Distributed 模式（推荐）

```bash
# 启动
bin/connect-distributed.sh config/connect-distributed.properties
```

```properties
# connect-distributed.properties
bootstrap.servers=localhost:9092
group.id=connect-cluster
key.converter=org.apache.kafka.connect.json.JsonConverter
value.converter=org.apache.kafka.connect.json.JsonConverter
config.storage.topic=connect-configs
offset.storage.topic=connect-offsets
status.storage.topic=connect-status
config.storage.replication.factor=3
offset.storage.replication.factor=3
status.storage.replication.factor=3
```

## 📝 Source Connector：从 MySQL 同步到 Kafka

### Debezium MySQL Connector

```json
{
  "name": "mysql-source-connector",
  "config": {
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "tasks.max": "1",
    "database.hostname": "mysql-host",
    "database.port": "3306",
    "database.user": "debezium",
    "database.password": "dbz_password",
    "database.server.id": "184054",
    "database.server.name": "mysql-server",
    "database.include.list": "inventory",
    "table.include.list": "inventory.orders,inventory.customers",
    "database.history.kafka.bootstrap.servers": "localhost:9092",
    "database.history.kafka.topic": "schema-changes.inventory",
    "snapshot.mode": "initial",
    "transforms": "route",
    "transforms.route.type": "org.apache.kafka.connect.transforms.RegexRouter",
    "transforms.route.regex": "([^.]+)\\.([^.]+)\\.([^.]+)",
    "transforms.route.replacement": "$3"
  }
}
```

**生成 Topic**：
- `mysql-server.inventory.orders`
- `mysql-server.inventory.customers`
- `schema-changes.inventory`（DDL 记录）

### 数据格式

```json
{
  "before": null,
  "after": {
    "id": 1001,
    "user_id": "user123",
    "amount": 99.9,
    "status": "CREATED",
    "created_at": "2024-07-15T10:00:00Z"
  },
  "source": {
    "version": "1.9.0",
    "connector": "mysql",
    "name": "mysql-server",
    "ts_ms": 1721037600000,
    "snapshot": "false",
    "db": "inventory",
    "table": "orders",
    "server_id": 12345,
    "gtid": null,
    "file": "mysql-bin.000003",
    "pos": 154,
    "row": 0
  },
  "op": "c",
  "ts_ms": 1721037600000,
  "transaction": null
}
```

## 📝 Sink Connector：从 Kafka 同步到 Elasticsearch

```json
{
  "name": "elasticsearch-sink-connector",
  "config": {
    "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
    "tasks.max": "3",
    "topics": "orders,payments,users",
    "connection.url": "http://elasticsearch:9200",
    "connection.username": "elastic",
    "connection.password": "password",
    "type.name": "_doc",
    "key.ignore": "true",
    "schema.ignore": "true",
    "batch.size": "1000",
    "linger.ms": "100",
    "max.in.flight.requests": "5"
  }
}
```

## 📝 管理 Connector

### REST API

```bash
# 列出所有 Connector
curl http://localhost:8083/connectors

# 查看 Connector 状态
curl http://localhost:8083/connectors/{name}/status

# 查看 Connector 配置
curl http://localhost:8083/connectors/{name}/config

# 启动 Connector
curl -X POST http://localhost:8083/connectors \
    -H "Content-Type: application/json" \
    -d @connector-config.json

# 暂停 Connector
curl -X PUT http://localhost:8083/connectors/{name}/pause

# 恢复 Connector
curl -X PUT http://localhost:8083/connectors/{name}/resume

# 重启 Connector
curl -X POST http://localhost:8083/connectors/{name}/restart

# 删除 Connector
curl -X DELETE http://localhost:8083/connectors/{name}
```

### 使用 kafka-connect-cli

```bash
# 列出
kafka-connect-cli list

# 启动
kafka-connect-cli create mysql-source.json

# 查看状态
kafka-connect-cli status mysql-source-connector
```

## 🛠️ 实战：MySQL → Kafka → Elasticsearch

### 1. MySQL Source

```json
{
  "name": "mysql-cdc",
  "config": {
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "tasks.max": "1",
    "database.hostname": "mysql",
    "database.port": "3306",
    "database.user": "debezium",
    "database.password": "password",
    "database.server.id": "1",
    "database.server.name": "mysql-prod",
    "database.include.list": "shop",
    "table.include.list": "shop.orders,shop.products,shop.users",
    "database.history.kafka.bootstrap.servers": "kafka:9092",
    "database.history.kafka.topic": "schema-changes",
    "snapshot.mode": "initial",
    "transforms": "unwrap,route",
    "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
    "transforms.unwrap.drop.tombstones": "true",
    "transforms.route.type": "org.apache.kafka.connect.transforms.RegexRouter",
    "transforms.route.regex": "([^.]+)\\.([^.]+)\\.([^.]+)",
    "transforms.route.replacement": "cdc.$3"
  }
}
```

### 2. Elasticsearch Sink

```json
{
  "name": "es-sink",
  "config": {
    "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
    "tasks.max": "3",
    "topics": "cdc.orders,cdc.products,cdc.users",
    "connection.url": "http://elasticsearch:9200",
    "type.name": "_doc",
    "key.ignore": "true",
    "schema.ignore": "true",
    "batch.size": "500",
    "linger.ms": "100",
    "max.in.flight.requests": "10",
    "flush.timeout.ms": "10000",
    "transforms": "ts",
    "transforms.ts.type": "org.apache.kafka.connect.transforms.TimestampConverter",
    "transforms.ts.target.type": "string",
    "transforms.ts.field": "created_at"
  }
}
```

### 3. 监听 Kafka 做业务处理

```java
@KafkaListener(topics = "cdc.orders", groupId = "cdc-processor")
public void consume(ConsumerRecord<String, String> record) {
    JSONObject cdcEvent = JSON.parseObject(record.value());
    String op = cdcEvent.getString("op");  // c=create, u=update, d=delete
    
    switch (op) {
        case "c":
            // 新增
            handleCreate(cdcEvent.getJSONObject("after"));
            break;
        case "u":
            // 更新
            handleUpdate(cdcEvent.getJSONObject("before"), cdcEvent.getJSONObject("after"));
            break;
        case "d":
            // 删除
            handleDelete(cdcEvent.getJSONObject("before"));
            break;
    }
}
```

## 🔧 自定义 Connector

### 单消息转换（SMT）

```java
// SMT：Transform 消息字段
public class AddTimestampTransform implements Transformation<SourceRecord> {
    
    @Override
    public void configure(Map<String, ?> configs) {}
    
    @Override
    public SourceRecord apply(SourceRecord record) {
        // 添加时间戳字段
        Struct value = (Struct) record.value();
        Schema schema = value.schema();
        
        Schema updatedSchema = SchemaBuilder.struct()
            .field("id", schema.field("id"))
            .field("name", schema.field("name"))
            .field("timestamp", Schema.INT64_SCHEMA)
            .build();
        
        Struct updatedValue = new Struct(updatedSchema)
            .put("id", value.get("id"))
            .put("name", value.get("name"))
            .put("timestamp", System.currentTimeMillis());
        
        return new SourceRecord(
            record.sourcePartition(),
            record.sourceOffset(),
            record.topic(),
            record.kafkaPartition(),
            record.keySchema(),
            record.key(),
            updatedSchema,
            updatedValue
        );
    }
    
    @Override
    public ConfigDef config() {
        return new ConfigDef();
    }
    
    @Override
    public void close() {}
}
```

注册到 Connect：

```properties
# plugin.path 配置
plugin.path=/opt/kafka-connect-plugins

# 添加自定义 Connector JAR
cp my-connector.jar /opt/kafka-connect-plugins/
```

## 📊 监控 Connect

### Connect REST API 指标

```bash
# 查看所有 Connect 状态
curl http://localhost:8083/connectors | jq

# 查看 Connector 任务状态
curl http://localhost:8083/connectors/{name}/tasks | jq

# 查看 Connector 当前 Offset
curl http://localhost:8083/connectors/{name}/status | jq
```

### JMX 指标

```
connect.source-task-messages-produced.total
connect.sink-task-messages-consumed.total
connect.connector-task-error.total
```

## ⚠️ 常见问题

### 问题 1：Connector 启动失败

```
常见原因：
  1. Connector 类不存在（plugin.path 配置错误）
  2. 配置文件错误
  3. 网络问题

解决：
  1. 检查 logs/connect.log
  2. 验证插件路径
  3. 测试外部系统连接
```

### 问题 2：数据延迟

```
原因：Batch 设置过大
解决：减小 batch.size 和 linger.ms
```

### 问题 3：数据丢失

```
场景：Connect 重启时数据丢失
解决：
  1. 开启持久化（offset.storage.topic）
  2. 配置 replication.factor ≥ 3
  3. 监控 offset 提交
```

## 🎯 总结

**Kafka Connect 核心要点**：
- ✅ Source Connector 从外部系统读数据
- ✅ Sink Connector 写数据到外部系统
- ✅ Distributed 模式推荐
- ✅ Debezium 是 CDC 主流方案
- ✅ REST API 管理 Connector
- ⚠️ 自定义 Connector 需打包 JAR
- ⚠️ 监控 Connector 状态

**下一步：** [🌊 Kafka Streams](/08-enterprise/streams) — 流处理
