---
title: vs MySQL / PostgreSQL
description: ClickHouse vs MySQL vs PostgreSQL 完整对比：数据模型 / 性能 / 适用场景
---

# ClickHouse vs MySQL / PostgreSQL

很多团队在「要不要上 ClickHouse」前会先问：「MySQL/PG 能不能扛？」本章给出可执行的对比。

## 核心差异

| 维度 | ClickHouse | MySQL | PostgreSQL |
|---|---|---|---|
| **数据模型** | 列存 | 行存 | 行存 |
| **写吞吐** | 100w+ rows/s | 1-5w rows/s | 5-10w rows/s |
| **单查询**（亿级聚合） | < 1s | 30s+ / OOM | 30s+ / OOM |
| **JOIN 能力** | 弱（≤ 8 表） | 强 | 极强 |
| **事务** | 无 | ACID | ACID |
| **UPDATE/DELETE** | 弱（异步 MUTATION） | 强 | 强 |
| **索引** | 主键稀疏 + Skip | B+Tree / 全文 | B+Tree / GIN / BRIN |
| **适用数据量** | PB 级 | TB 级 | TB 级 |

## 性能基准（10 亿行）

```sql
-- 测试表
CREATE TABLE test_table (
  id UInt64,
  user_id UInt64,
  event_time DateTime,
  event_type LowCardinality(String),
  amount Decimal(18, 2)
)
ENGINE = MergeTree() ORDER BY id

-- 插入 10 亿行（约 5 分钟）
INSERT INTO test_table SELECT
  number,
  number % 1000,
  now() - INTERVAL number SECOND,
  ['click', 'view', 'purchase'][number % 3 + 1],
  rand() % 1000
FROM numbers(1000000000)
```

| 查询 | ClickHouse | MySQL（带索引） | PostgreSQL（带索引） |
|---|---|---|---|
| `SELECT count()` | 100ms | 30s | 20s |
| `SELECT count() GROUP BY event_type` | 200ms | 60s | 40s |
| `SELECT uniq(user_id)` | 1s | 120s+ | 90s+ |
| `SELECT avg(amount) GROUP BY user_id`（Top 100） | 500ms | 90s+ | 60s+ |
| `SELECT * WHERE user_id = X` | 50ms | 10ms | 8ms |

**结论**：
- 聚合 / 统计查询 → ClickHouse 完胜（10-100x）
- 单行 / 主键查询 → MySQL/PG 更快（行存索引）

## 数据同步模式

### 模式 1：MySQL → ClickHouse 实时同步

```text
MySQL（OLTP） → Debezium/Kafka → ClickHouse（OLAP）
            │
            │  CDC 同步
            ▼
       实时分析
```

### 模式 2：双写（不推荐）

```text
应用 → MySQL（事务写入）
      → ClickHouse（分析写入）
      │
      └── 双写一致性难保证
```

### 模式 3：ClickHouse → MySQL 回写（少见）

CK 计算结果回写 MySQL 提供 OLTP 读取（如实时计数）。

## 何时 MySQL/PG 足够？

✅ **数据量 < 1 亿行 + 查询模式以单行为主** → MySQL/PG 就够
✅ **强事务 + 高并发点查** → MySQL/PG（TiDB 也行）
✅ **简单 COUNT/SUM** → MySQL/PG（CK 杀鸡用牛刀）

## 何时 ClickHouse 值得？

✅ **数据量 ≥ 1 亿行 + 聚合查询为主** → ClickHouse 必备
✅ **日志 / 埋点 / 指标** → ClickHouse 主战场
✅ **实时看板 / 报表** → ClickHouse 秒级延迟
✅ **PB 级长期存储** → ClickHouse 压缩 + 分布式

## 混合架构（推荐）

```text
MySQL/PG（OLTP）
    │
    ├── 主库：用户 / 订单 / 商品（强事务）
    └── 从库：备份 + 简单聚合

ClickHouse（OLAP）
    │
    ├── 实时看板
    ├── 用户行为分析
    └── 业务指标

Kafka（CDC）
    │
    └── MySQL → Kafka → ClickHouse
```

## 迁移路径

### Step 1：数据量评估

```sql
-- MySQL 评估
SELECT
  table_schema,
  table_name,
  table_rows,
  ROUND(data_length / 1024 / 1024, 2) AS data_mb
FROM information_schema.tables
WHERE table_schema NOT IN ('mysql', 'information_schema', 'performance_schema')
ORDER BY data_length DESC
```

### Step 2：建立 CDC 链路

```bash
# 用 Debezium 捕获 MySQL binlog
debezium-connector-mysql \
  --connector.class=io.debezium.connector.mysql.MySqlConnector \
  --database.hostname=mysql-1 \
  --database.port=3306 \
  --database.user=debezium \
  --database.password=xxx \
  --database.server.id=1 \
  --table.include.list=production.orders,production.users \
  --topic.prefix=cdc
```

### Step 3：ClickHouse 消费

```sql
CREATE TABLE orders_kafka (...)
ENGINE = Kafka()
SETTINGS
  kafka_broker_list = 'kafka-1:9092',
  kafka_topic_list = 'cdc.production.orders',
  kafka_format = 'JSONEachRow'

CREATE MATERIALIZED VIEW orders_cdc_mv TO orders_local AS
SELECT * FROM orders_kafka
```

### Step 4：业务查询迁移

| 原 MySQL 查询 | ClickHouse 查询 |
|---|---|
| `SELECT count(*) FROM orders` | `SELECT count() FROM orders` |
| `SELECT COUNT(DISTINCT user_id)` | `SELECT uniq(user_id)` |
| `SELECT * FROM orders WHERE id = X` | **保持 MySQL**（CK 慢） |

## 实战：电商平台

```text
MySQL 主库（写）：用户 / 订单 / 商品 / 库存
   │
   └── Binlog
       │
       └── Debezium → Kafka
           │
           └── ClickHouse Kafka 引擎
               │
               ├── MV：实时 UV / PV / GMV
               ├── MV：用户画像
               └── MV：商品分析

查询路由：
- 用户登录 / 下单 / 支付 → MySQL
- 商家后台 / 经营分析 → ClickHouse
- 实时大屏 → ClickHouse + Grafana
```

## 大厂案例

- **Uber**：订单数据走 ClickHouse
- **字节跳动**：电商分析
- **京东**：订单履约 + 商品分析（与 MySQL/PG 共存）

详见 [../case-study.md](../case-study.md) 案例 6。

## 工具对比

| 工具 | MySQL | PG | ClickHouse |
|---|---|---|---|
| **客户端** | MySQL Workbench | pgAdmin | DBeaver / DataGrip |
| **BI** | Metabase | Metabase | Grafana / Metabase / Superset |
| **ORM** | MyBatis / GORM | sqlx / GORM | 没有专门 ORM（直接写 SQL） |

## 下一步

- 学习 vs Doris：见 [vs-doris.md](./vs-doris.md)
