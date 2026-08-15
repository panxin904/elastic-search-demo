---
title: CDC 同步
---
# CDC 数据同步

## 1. 概述

CDC = Change Data Capture = 实时同步数据库变更到下游。

详见 [Flink CDC](/05-flink/cdc)。

## 2. CDC 工具选型

| 工具 | 特点 | 适用 |
|------|------|------|
| **Flink CDC** | Flink 集成，exactly-once | 大数据 + 流处理 |
| **Debezium** | 独立框架，写 Kafka | 通用 CDC |
| **Canal** | 阿里，MySQL binlog | Java 生态 |
| **DataX** | 阿里，离线批量 | 一次性全量 |
| **Maxwell** | 轻量级，MySQL | 简单场景 |
| **Debezium UI** | 可视化 | 运维 |

## 3. 实战：Debezium + Kafka

```bash
# 1. 启动 Debezium
docker run -d --name debezium   -p 8083:8083   -e CONFIG_STORAGE_TOPIC=my_cdc_configs   -e CONFIG_STORAGE_REPLICATION_FACTOR=1   -e CONFIG_STORAGE_CLEANUP_POLICY=compact   -e OFFSET_STORAGE_TOPIC=my_cdc_offsets   debezium/connect:1.9

# 2. 注册 MySQL connector
curl -X POST -H "Content-Type: application/json"   http://localhost:8083/connectors   -d '{
    "name": "mysql-orders",
    "config": {
      "connector.class": "io.debezium.connector.mysql.MySqlConnector",
      "database.hostname": "mysql",
      "database.port": "3306",
      "database.user": "cdc",
      "database.password": "xxx",
      "database.server.id": "1",
      "table.include.list": "mydb.orders",
      "topic.prefix": "cdc"
    }
  }'
```

## 4. 实战：Flink CDC

详见 [Flink CDC](/05-flink/cdc)。

## 5. 实战：阿里 Canal

```bash
# Canal Server（解析 binlog）
canal.deployer-1.1.6.tar.gz

# 启动
bin/startup.sh
# 默认端口 11111

# 客户端订阅
canal.client-1.1.6
```

## 6. 实战：DataX 批量同步

```json
{
  "job": {
    "content": [{
      "reader": {
        "name": "mysqlreader",
        "parameter": {
          "username": "root",
          "password": "xxx",
          "column": ["id", "name", "amount"],
          "connection": [{"table": ["orders"]}]
        }
      },
      "writer": {
        "name": "hdfswriter",
        "parameter": {
          "path": "/data/ods/orders",
          "defaultFS": "hdfs://nn:9000",
          "fileType": "parquet"
        }
      }
    }],
    "setting": {"speed": {"channel": 4}}
  }
}
```

## 7. 实战选型

| 场景 | 选 |
|------|-----|
| 实时 + Flink 集成 | Flink CDC |
| 通用 CDC + Kafka | Debezium |
| MySQL 大量 binlog | Canal |
| 一次性全量迁移 | DataX / sqoop |
| 简单 CDC + 队列 | Maxwell / Debezium |

## 8. 实战技巧

### 8.1 冲突解决

```
主库 → binlog → CDC → Kafka → 多个消费者
  - 顺序保证（按主键分区到固定 partition）
  - 幂等写入（按主键去重）
  - 版本号（用于冲突检测）
```

### 8.2 全量 + 增量

```
首次：全表快照（snapshot.mode = initial）
之后：仅增量（binlog）
重启：从 binlog 位点继续
```

## 9. 实战案例：MySQL → Iceberg 实时入湖

详见 [Flink CDC](/05-flink/cdc)。

## 10. 实战建议

- 选 Flink CDC（如果用 Flink）或 Debezium
- 增量 + 全量结合（首次 snapshot + 后续 binlog）
- 幂等写入（按主键去重）
- 监控（延迟 / 积压）

## 🔗 下一步
- [Flink CDC](/05-flink/cdc)
- [数据血缘](/07-kafka-streaming/lineage)
