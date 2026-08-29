---
title: 声明式分区
description: PostgreSQL 表分区策略与实战
---

# 声明式分区

> **TL;DR**：PG 10+ 支持**声明式分区**（PARTITION BY），单表亿级行→按时间/范围分区后查询性能提升 10x、维护成本降低 90%（老分区 DROP/ATTACH 即可）。**90% 的"大表慢"问题靠分区解决**。

## 一句话定义

```
声明式分区 = 一张大表（父表）拆成多个小表（分区），对应用透明
           = 按 RANGE / LIST / HASH 自动路由数据
```

## 三种分区类型

| 类型 | 适用场景 | 例子 |
|---|---|---|
| **RANGE** | 连续区间（时间、数值） | 按 created_at 月分区 |
| **LIST** | 离散值（地区、类型） | 按 region 分区 |
| **HASH** | 均匀分布 | 按 user_id hash 8 分区 |

## 实战：RANGE 分区（最常用）

### 创建分区表

```sql
-- 1. 父表（仅 schema，无数据）
CREATE TABLE orders (
  id BIGSERIAL,
  created_at TIMESTAMPTZ NOT NULL,
  user_id BIGINT,
  amount NUMERIC,
  status TEXT,
  PRIMARY KEY (id, created_at)         -- 分区键必须包含在主键
) PARTITION BY RANGE (created_at);

-- 2. 创建分区
CREATE TABLE orders_2026_q1 PARTITION OF orders
  FOR VALUES FROM ('2026-01-01') TO ('2026-04-01');

CREATE TABLE orders_2026_q2 PARTITION OF orders
  FOR VALUES FROM ('2026-04-01') TO ('2026-07-01');

CREATE TABLE orders_2026_q3 PARTITION OF orders
  FOR VALUES FROM ('2026-07-01') TO ('2026-10-01');

CREATE TABLE orders_2026_q4 PARTITION OF orders
  FOR VALUES FROM ('2026-10-01') TO ('2027-01-01');

-- 3. 默认分区（兜底，没匹配分区时落这里）
CREATE TABLE orders_default PARTITION OF orders DEFAULT;

-- 4. 插入数据
INSERT INTO orders (created_at, user_id, amount, status)
VALUES ('2026-08-09 10:00', 123, 99.50, 'paid');

-- 数据自动路由到 orders_2026_q3
```

### 自动创建分区

```sql
-- PG 14+：PG_PARTMAN 扩展（推荐）
CREATE EXTENSION pg_partman;

SELECT partman.create_parent(
  p_parent_table := 'public.orders',
  p_control := 'created_at',
  p_type := 'range',
  p_interval := '1 month',
  p_premake := 12  -- 提前创建 12 个月
);
```

### 查询（应用透明）

```sql
-- 应用 SQL 不变
SELECT * FROM orders WHERE user_id = 123 AND created_at >= '2026-08-01';

-- PG 优化器自动裁剪（partition pruning）
-- 只扫描 orders_2026_q3 分区，不扫全表
```

**EXPLAIN 看裁剪**：

```sql
EXPLAIN SELECT * FROM orders WHERE created_at >= '2026-08-01';

-- Append  (cost=... rows=...)
--   ->  Index Scan using idx_orders_2026_q3_user_id on orders_2026_q3
--   ->  ...
-- 只扫了 q3 分区！
```

## 实战：LIST 分区

```sql
-- 按地区分区
CREATE TABLE logs (
  id BIGSERIAL,
  region TEXT NOT NULL,
  message TEXT,
  created_at TIMESTAMPTZ,
  PRIMARY KEY (id, region)
) PARTITION BY LIST (region);

CREATE TABLE logs_us PARTITION OF logs FOR VALUES IN ('us-east', 'us-west');
CREATE TABLE logs_eu PARTITION OF logs FOR VALUES IN ('eu-west', 'eu-central');
CREATE TABLE logs_asia PARTITION OF logs FOR VALUES IN ('cn-east', 'cn-west', 'jp');
CREATE TABLE logs_default PARTITION OF logs DEFAULT;
```

## 实战：HASH 分区

```sql
-- 按 user_id hash 分 8 个分区
CREATE TABLE user_sessions (
  id BIGSERIAL,
  user_id BIGINT NOT NULL,
  session_data JSONB,
  PRIMARY KEY (id, user_id)
) PARTITION BY HASH (user_id);

CREATE TABLE user_sessions_0 PARTITION OF user_sessions
  FOR VALUES WITH (MODULUS 8, REMAINDER 0);
CREATE TABLE user_sessions_1 PARTITION OF user_sessions
  FOR VALUES WITH (MODULUS 8, REMAINDER 1);
-- ... 8 个分区
```

> **HASH 分区适用**：均匀分布的大表（如 session），避免热点分区。

## 分区维护

### 添加新分区

```sql
-- 加 2027 年 Q1 分区
CREATE TABLE orders_2027_q1 PARTITION OF orders
  FOR VALUES FROM ('2027-01-01') TO ('2027-04-01');
```

### 删除老分区（秒级）

```sql
-- DROP 分区 = 删除所有行（不触发 DELETE，慢日志，无锁）
DROP TABLE orders_2026_q1;
-- 或者
ALTER TABLE orders DETACH PARTITION orders_2026_q1;
DROP TABLE orders_2026_q1;

-- 实战：每月定时清理 12 个月前的分区
```

### 移动分区（detach + attach）

```sql
-- 1. 离线老分区
ALTER TABLE orders DETACH PARTITION orders_2026_q1;

-- 2. 压缩归档（可选）
-- 3. 重新挂载
ALTER orders ATTACH PARTITION orders_2026_q1 FOR VALUES FROM ('2026-01-01') TO ('2026-04-01');
```

## 分区索引

**两种索引策略**：

```sql
-- 1. 父表建索引（PG 11+ 自动传播到所有分区）
CREATE INDEX idx_orders_user_id ON orders (user_id);
-- 自动在 orders_2026_q1, q2, q3, q4 上都建索引

-- 2. 单个分区建索引（更灵活）
CREATE INDEX idx_orders_2026_q3_user_id ON orders_2026_q3 (user_id);
```

> **推荐**：**用父表索引（PG 11+）**，简单且自动传播。

## 实战案例

### 案例 1：订单表按月分区

```sql
CREATE TABLE orders (
  id BIGSERIAL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  user_id BIGINT,
  amount NUMERIC(10,2),
  status TEXT,
  PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- 创建当年 12 个月分区
DO $$
DECLARE
  month_start DATE;
  month_end DATE;
  tbl_name TEXT;
BEGIN
  FOR i IN 0..11 LOOP
    month_start := date_trunc('month', now())::date + (i || ' months')::interval;
    month_end := month_start + interval '1 month';
    tbl_name := 'orders_' || to_char(month_start, 'YYYYMM');
    
    EXECUTE format(
      'CREATE TABLE IF NOT EXISTS %I PARTITION OF orders
       FOR VALUES FROM (%L) TO (%L)',
      tbl_name, month_start, month_end
    );
  END LOOP;
END $$;

-- 索引
CREATE INDEX idx_orders_user_id ON orders (user_id);
CREATE INDEX idx_orders_status ON orders (status) WHERE status != 'paid';
```

### 案例 2：定时清理 12 个月前的数据

```sql
-- 用 pg_cron 扩展
CREATE EXTENSION pg_cron;

-- 每月 1 号删除 12 个月前的分区
SELECT cron.schedule(
  'cleanup-old-orders',
  '0 0 1 * *',  -- cron 表达式
  $$DO $$
  DECLARE
    cutoff DATE := date_trunc('month', now() - interval '12 months')::date;
    part_name TEXT;
  BEGIN
    FOR part_name IN
      SELECT relname FROM pg_inherits
      JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
      JOIN pg_class child ON pg_inherits.inhrelid = child.oid
      WHERE parent.relname = 'orders'
    LOOP
      IF part_name ~ '^orders_\d{6}$' THEN
        EXECUTE format('DROP TABLE IF EXISTS %I', part_name);
      END IF;
    END LOOP;
  END $$;
  $$);
```

### 案例 3：复合分区（按时间 + 区域）

```sql
CREATE TABLE logs (
  id BIGSERIAL,
  region TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  message TEXT,
  PRIMARY KEY (id, region, created_at)
) PARTITION BY LIST (region);

-- 每个区域一个时间子分区
CREATE TABLE logs_us PARTITION OF logs FOR VALUES IN ('us-east', 'us-west')
  PARTITION BY RANGE (created_at);

CREATE TABLE logs_us_2026_q3 PARTITION OF logs_us
  FOR VALUES FROM ('2026-07-01') TO ('2026-10-01');

-- 查询自动路由到两层
SELECT * FROM logs 
WHERE region = 'us-east' AND created_at >= '2026-08-01';
```

## 性能对比

| 操作 | 单表（1 亿行） | RANGE 分区（10 分区） |
|---|---|---|
| 时间范围查询 | 5000ms（全扫） | 500ms（只扫 1-2 分区） |
| 插入 | 10000/s | 15000/s（每分区并发 insert） |
| 删 1 个月老数据 | DELETE 1 小时 | DROP TABLE 1 秒 |
| VACUUM | 全表慢 | 单分区快 |

## 何时不用分区

```
❌ 表 < 1000 万行（没必要）
❌ 已有合适的索引（PG 一般能搞定）
❌ OLTP 高频跨分区查询（如按 user_id 全表聚合）

✓ 单表 > 1 亿行
✓ 时间序列数据（日志、订单、事件）
✓ 按时间清理老数据
✓ 单分区适合冷热分层（老分区压缩归档）
```

## 一句话总结

> **声明式分区 = 大表的性能与维护两难解药**：查询快 10x、清理老数据 1 秒（DROP）、PG 11+ 父表索引自动传播。**RANGE 时间分区是 90% 场景的默认选择**。**子表必须把分区键加到主键**。

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

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [mysql](https://java-px.bot.cd/mysql/):MySQL 对比
- [clickhouse](https://java-px.bot.cd/clickhouse/):ClickHouse OLAP
- [system-design](https://java-px.bot.cd/system-design/):数据库选型
