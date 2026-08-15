---
title: 逻辑复制
description: PG 10+ 行列级复制
---

# 逻辑复制

> **TL;DR**：逻辑复制 = **行列级复制**（vs 物理复制按 block 复制）。**适用**：跨大版本升级、PG → Kafka、PG → 数仓、读写分离（精确粒度）。

## 一句话定义

```
逻辑复制 = PUBLICATION（发布）+ SUBSCRIPTION（订阅）
        = 按表 / 按操作（INSERT/UPDATE/DELETE）复制
        = 不复制 DDL、不复制 TRUNCATE
        = 解耦复制
```

## 与物理复制的对比

| 维度 | 物理（流复制） | 逻辑 |
|---|---|---|
| 粒度 | 整个实例 | 单表 / 单操作 |
| 跨大版本 | ✗ | ✓ |
| 跨平台 | ✗ | ✓ |
| 不同 schema 名 | ✗ | ✓ |
| SELECT 过滤 | ✗ | ✓（WHERE） |
| 列过滤 | ✗ | ✓ |
| 双向复制 | 难 | ✓ |
| 性能 | 高 | 中 |

## 配置

```ini
# postgresql.conf（源库）
wal_level = logical                    # 必须 logical
max_replication_slots = 10             # 每个订阅 1 个 slot
max_wal_senders = 10                   # 流复制连接数
```

```sql
-- 1. PUBLICATION（源库）
CREATE PUBLICATION pub_orders FOR TABLE orders;
-- 或
CREATE PUBLICATION pub_all FOR ALL TABLES;
-- 或带 WHERE 过滤
CREATE PUBLICATION pub_paid FOR TABLE orders 
  WHERE (status = 'paid');

-- 2. SUBSCRIPTION（目标库）
CREATE SUBSCRIPTION sub_orders
  CONNECTION 'host=source.db port=5432 dbname=mydb user=replicator password=xxx'
  PUBLICATION pub_orders;
```

## 实战案例

### 案例 1：跨大版本升级（PG 13 → 16）

```sql
-- 源库（PG 13）
CREATE PUBLICATION pub_upgrade FOR ALL TABLES;

-- 目标库（PG 16）
CREATE SUBSCRIPTION sub_upgrade
  CONNECTION 'host=old-pg-13.db port=5432 dbname=mydb user=replicator'
  PUBLICATION pub_upgrade;

-- 等待同步
SELECT * FROM pg_stat_subscription;

-- 切换应用连接到新库
-- 删除 SUBSCRIPTION + 老库
```

### 案例 2：PG → Kafka（CDC）

```sql
-- PG 端
CREATE PUBLICATION pub_cdc FOR TABLE orders, users;

-- 用 debezium / kafka-connect-pgsql 订阅
-- 实时流式变更到 Kafka
```

### 案例 3：PG → ClickHouse / 数仓

```sql
-- PG 端
CREATE PUBLICATION pub_dw FOR TABLE orders;
CREATE PUBLICATION pub_dw FOR TABLE users;

-- ClickHouse 端用 MaterializedPostgreSQL 引擎
CREATE TABLE orders_dw (...)
ENGINE = MaterializedPostgreSQL('pg-host:5432', 'mydb', 'orders', 'user', 'password', 'pub_dw');
```

### 案例 4：读写分离（行级过滤）

```sql
-- 只复制已支付订单到分析库
CREATE PUBLICATION pub_paid FOR TABLE orders
  WHERE (status = 'paid');

CREATE SUBSCRIPTION sub_paid
  CONNECTION '...'
  PUBLICATION pub_paid;
```

## 监控

```sql
-- PUBLICATION 端
SELECT * FROM pg_stat_replication;

-- SUBSCRIPTION 端
SELECT
  subname,
  pid,
  received_lsn,
  last_msg_send_time,
  last_msg_replay_time,
  EXTRACT(EPOCH FROM now() - last_msg_replay_time) AS lag_seconds
FROM pg_stat_subscription;
```

## 限制

```sql
-- ❌ DDL 不自动复制
ALTER TABLE orders ADD COLUMN new_col INT;
-- 不会自动同步到订阅端，需要手动 ALTER

-- ❌ TRUNCATE 不自动复制
TRUNCATE orders;
-- 默认不复制（可以用 publish = 'truncate' 启用）

-- ❌ 大事务可能阻塞
-- 大量 INSERT 会阻塞 replication slot

-- ⚠️ Sequence 不自动同步
-- 需要单独处理
```

## 双向复制（multi-master）

```sql
-- A 库（pub_a）
CREATE PUBLICATION pub_a FOR TABLE users WHERE (id % 2 = 0);
-- B 库（pub_b）
CREATE PUBLICATION pub_b FOR TABLE users WHERE (id % 2 = 1);

-- A 订阅 B
CREATE SUBSCRIPTION sub_b
  CONNECTION 'host=B.db ...'
  PUBLICATION pub_b;

-- B 订阅 A
CREATE SUBSCRIPTION sub_a
  CONNECTION 'host=A.db ...'
  PUBLICATION pub_a;

-- ⚠️ 必须用 WHERE 切分，避免冲突
```

## 一句话总结

> **逻辑复制 = 行列级灵活复制**：**跨大版本、跨平台、按表/按列/按 WHERE 过滤**。**PG → Kafka / 数仓**的首选。**DDL 不自动复制**，**TRUNCATE 默认不复制**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
