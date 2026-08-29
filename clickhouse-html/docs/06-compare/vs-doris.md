---
title: vs Doris / StarRocks
date: 2026-08-15  # date-auto-injected
description: ClickHouse vs Doris vs StarRocks 三大 OLAP 引擎详细对比
---

# ClickHouse vs Doris

[Doris](https://doris.apache.org/) 和 [StarRocks](https://www.starrocks.io/) 是 MPP 架构的新一代 OLAP 引擎。本章对比 ClickHouse 和 Doris。

## 核心差异

| 维度 | ClickHouse | Doris |
|---|---|---|
| **出身** | Yandex（2009） | 百度（2017）→ Apache |
| **架构** | Shared-nothing | Frontend + Backend |
| **存储引擎** | MergeTree（LSM 风格） | 列存 + Segment |
| **JOIN 能力** | 弱（Hash Join 本地） | 强（CBO + Runtime Filter） |
| **数据更新** | ReplacingMergeTree（异步） | 默认支持 UPSERT |
| **实时写入** | Kafka 引擎 + MV | Stream Load / Routine Load |
| **运维** | 复杂（Keeper 集群） | 简单（FE + BE） |
| **SQL 完整度** | 中（无完整事务） | 高（CBO 强） |
| **生态** | 客户端 / Kafka / dbt | 自带生态 + SelectDB 商业版 |
| **典型用户** | Uber / Cloudflare / GitHub | 百度 / 美团 / 小米 / 京东 |

## 性能对比（10 亿行 JOIN）

```sql
-- 测试场景：星型模型 JOIN
-- 事实表 orders（10 亿）
-- 维度表 users（百万）、products（百万）、shops（万）

-- Doris SQL
SELECT
  u.country,
  p.category,
  s.shop_type,
  count() AS order_count,
  sum(o.amount) AS gmv
FROM orders o
JOIN users u ON o.user_id = u.id
JOIN products p ON o.product_id = p.id
JOIN shops s ON o.shop_id = s.id
WHERE o.order_date >= '2024-01-01'
GROUP BY u.country, p.category, s.shop_type

-- Doris: 5-8s
-- ClickHouse: 30-60s（JOIN 4 张大表性能退化）
```

**结论**：**多张大表 JOIN** Doris 完胜 ClickHouse。

## 单表聚合性能（CK 主场）

```sql
-- 单表聚合
SELECT
  event_date,
  uniq(user_id) AS uv,
  count() AS pv
FROM events
WHERE event_date BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY event_date

-- ClickHouse: 100ms
-- Doris: 200ms
```

**结论**：**单表列扫** ClickHouse 比 Doris 快 1.5-2x。

## 数据写入吞吐

```sql
-- 批量 INSERT
INSERT INTO events VALUES ... (1 million rows)

-- ClickHouse: 0.5s（100w rows/s）
-- Doris: 1-2s（50w rows/s）
```

**结论**：**批量写入** ClickHouse 仍占优。

## 实时数据接入

### ClickHouse：Kafka 引擎

```sql
CREATE TABLE events_kafka (...)
ENGINE = Kafka()
SETTINGS kafka_broker_list = 'kafka-1:9092', kafka_topic_list = 'events', kafka_format = 'JSONEachRow'

CREATE MATERIALIZED VIEW events_mv TO events_local AS SELECT * FROM events_kafka
```

### Doris：Routine Load

```sql
CREATE ROUTINE LOAD my_load_job ON events
COLUMNS (event_time, user_id, event_type)
PROPERTIES (
  "desired_concurrent_number" = "3",
  "max_error_number" = "1000"
)
FROM KAFKA (
  "kafka_broker_list" = "kafka-1:9092",
  "kafka_topic" = "events"
)
```

**对比**：
- CK Kafka 引擎更简洁（一行 SQL）
- Doris Routine Load 持续消费，状态可查询
- 两者都能达到 10w+ rows/s

## 数据更新

### ClickHouse：ReplacingMergeTree

```sql
CREATE TABLE users (
  id UInt64,
  name String,
  updated_at DateTime
)
ENGINE = ReplacingMergeTree(updated_at)
ORDER BY id

-- 去重是异步的（合并时执行）
SELECT * FROM users FINAL WHERE id = 1
```

### Doris：UPSERT（默认）

```sql
CREATE TABLE users (
  id BIGINT,
  name VARCHAR(100),
  UNIQUE KEY (id)
)
DISTRIBUTED BY HASH(id) BUCKETS 10

-- 默认 UPSERT（实时合并）
INSERT INTO users VALUES (1, 'Alice')  -- 替换之前的 id=1
```

**对比**：Doris UPSERT 是同步的（默认开启 Unique Key 表），CK ReplacingMergeTree 是异步的。

## 运维对比

| 维度 | ClickHouse | Doris |
|---|---|---|
| **依赖** | ClickHouse Keeper（或 Zookeeper） | 无（FE 自带 BDBJE） |
| **集群部署** | 复杂（多分片 + 副本） | 简单（FE 3 节点 + BE N 节点） |
| **扩容** | 手动 rebalance | 自动均衡 |
| **监控** | 自带 system.metrics | 自带 system.audit + audit log |
| **故障恢复** | 副本切换（秒级） | FE 高可用（秒级） |

**结论**：Doris 运维更简单，ClickHouse 运维更复杂但更可控。

## 生态对比

| 维度 | ClickHouse | Doris |
|---|---|---|
| **客户端** | ch-go / clickhouse-go / JDBC / Python | mysql-jdbc / Go / Python |
| **Kafka 集成** | 原生引擎 | Routine Load |
| **数据湖** | Iceberg / DeltaLake（v23+） | 原生 Iceberg / Hudi |
| **BI 工具** | Grafana / Superset / Metabase | Apache Superset / SmartBI |
| **云服务** | ClickHouse Cloud / Altinity | SelectDB Cloud |
| **商业支持** | Altinity / ClickHouse Inc | SelectDB（商业版） |

## 选型决策

### 选 ClickHouse

✅ **单表聚合 + 高吞吐写入**（日志 / 埋点 / 指标）
✅ **极致性能优化**（定制客户端 + LZ4 压缩）
✅ **生态丰富**（Kafka / dbt / Grafana / Prometheus）
✅ **团队有能力运维 Keeper 集群**

### 选 Doris

✅ **复杂 JOIN 场景**（星型 / 雪花模型）
✅ **实时 UPSERT**（订单状态机、用户更新）
✅ **运维团队精简**（不想维护 Zookeeper）
✅ **数据湖联邦查询**（原生 Iceberg）

## 实战对比

### 场景 1：日志分析（CK 赢面）

```text
数据量：100 亿 / 天
查询：按 status_code / path 聚合
写入：Kafka 流式

CK 优势：单表聚合快 1.5-2x，Kafka 引擎更简洁
```

### 场景 2：订单实时分析（Doris 赢面）

```text
数据量：10 亿订单 + 多维度关联
查询：订单 + 用户 + 商品 + 店铺 JOIN
更新：订单状态实时更新

Doris 优势：多表 JOIN 优化好，UPSERT 实时合并
```

### 场景 3：埋点实时大宽表（CK 赢面）

```text
数据量：PB 级
查询：单表按时间聚合
写入：百万 events/s

CK 优势：写入吞吐 + 单表聚合双优
```

## 大厂案例

| 公司 | 引擎 | 场景 |
|---|---|---|
| Uber | ClickHouse | 日志分析 |
| Cloudflare | ClickHouse | DNS / CDN |
| GitHub | ClickHouse | Events |
| 字节跳动 | ClickHouse | 抖音埋点 |
| 美团 | ClickHouse + Doris 双引擎 | 外卖（CK）+ 供应链（Doris） |
| 京东 | ClickHouse | 订单分析 |
| 百度 | Doris | 凤巢广告 |
| 小米 | Doris | 业务分析 |

## 与 StarRocks 对比

详见 [vs-starrocks.md](./vs-starrocks.md)。

**结论**：
- **Doris**：Apache 社区版 + SelectDB 商业版，国内接受度高
- **StarRocks**：从 Doris 0 fork，CBO 优化器更强，海外接受度高
- **二者形态相似，选哪个都合理**

## 下一步

- 学习 vs StarRocks：见 [vs-starrocks.md](./vs-starrocks.md)
- 学习 vs TiDB：见 [vs-tidb.md](./vs-tidb.md)
