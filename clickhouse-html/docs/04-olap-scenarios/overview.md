---
title: OLAP 实战场景
date: 2026-08-15  # date-auto-injected
---

# OLAP 实战场景

**ClickHouse 的核心价值在 6 大实战场景**——用户行为 / 日志 / 指标 / 实时数仓 / Bitmap 去重。

## 一句话总结

> **ClickHouse 6 大场景 = 埋点 + 日志 + 指标 + 实时数仓 + Bitmap 去重 + 业务 OLAP**。**每个场景都有大厂真实案例可参考**。

---

## 一、用户行为埋点

**场景**：电商 / 短视频 / 社交 App 每天 10 亿+ 埋点事件。

**表设计**：

```sql
CREATE TABLE user_events (
    event_time DateTime64(3),         -- 毫秒精度
    user_id UInt64,
    session_id UUID,
    event_type LowCardinality(String),  -- click/view/purchase
    page LowCardinality(String),
    element LowCardinality(String),   -- 元素
    amount Decimal(10, 2),
    properties Map(String, String),    -- 动态属性
    device_model LowCardinality(String),
    os_version LowCardinality(String),
    app_version LowCardinality(String),
    country LowCardinality(FixedString(2))
)
ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (event_time, user_id, event_type)
TTL event_time + INTERVAL 90 DAY;  -- 90 天后自动删除

-- 1. 漏斗分析
SELECT
    -- 步骤 1: 浏览
    countIf(event_type = 'view') AS view_count,
    -- 步骤 2: 加购
    countIf(event_type = 'add_to_cart') AS add_to_cart_count,
    -- 步骤 3: 结算
    countIf(event_type = 'checkout') AS checkout_count,
    -- 步骤 4: 支付
    countIf(event_type = 'purchase') AS purchase_count,
    -- 转化率
    round(100.0 * purchase_count / view_count, 2) AS conversion_rate
FROM user_events
WHERE event_time >= now() - INTERVAL 1 DAY
  AND country = 'CN';

-- 2. 用户留存（次日 / 7 日 / 30 日）
WITH
    -- 第一天活跃用户
    d1_users AS (
        SELECT DISTINCT user_id
        FROM user_events
        WHERE toDate(event_time) = '2026-08-01'
    ),
    -- 次日活跃
    d2_users AS (
        SELECT DISTINCT user_id
        FROM user_events
        WHERE toDate(event_time) = '2026-08-02'
          AND user_id IN (SELECT user_id FROM d1_users)
    )
SELECT
    (SELECT count() FROM d1_users) AS d1_total,
    (SELECT count() FROM d2_users) AS d2_retained,
    round(100.0 * (SELECT count() FROM d2_users) / (SELECT count() FROM d1_users), 2) AS d2_retention_pct;

-- 3. 路径分析
SELECT
    path,
    count() AS user_count
FROM (
    SELECT
        user_id,
        arrayStringConcat(
            arrayMap(x -> event_type, groupArray(event_type)),
            ' → '
        ) AS path
    FROM user_events
    WHERE event_time >= now() - INTERVAL 1 DAY
    GROUP BY user_id
)
GROUP BY path
ORDER BY user_count DESC
LIMIT 20;
```

**案例**：
- 字节跳动：抖音埋点 100 亿/天，ClickHouse 集群 1000+ 节点
- B 站：用户行为分析，500+ 节点 ClickHouse
- 知乎：问答浏览链路，ClickHouse + Druid 双写

## 二、日志分析

**场景**：服务器日志 / 应用日志聚合分析。

```sql
CREATE TABLE app_logs (
    ts DateTime,
    level Enum8('DEBUG' = 1, 'INFO' = 2, 'WARN' = 3, 'ERROR' = 4, 'FATAL' = 5),
    service LowCardinality(String),
    host LowCardinality(String),
    trace_id String,
    message String,
    error_type String,
    stack_trace String,
    duration_ms UInt32
)
ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(ts)
ORDER BY (service, level, ts)
TTL ts + INTERVAL 30 DAY;

-- 1. 错误率（按服务）
SELECT
    service,
    countIf(level IN ('ERROR', 'FATAL')) AS error_count,
    count() AS total,
    round(100.0 * error_count / total, 3) AS error_rate_pct
FROM app_logs
WHERE ts >= now() - INTERVAL 1 HOUR
GROUP BY service
ORDER BY error_rate_pct DESC;

-- 2. P99 延迟
SELECT
    service,
    quantile(0.5)(duration_ms) AS p50,
    quantile(0.95)(duration_ms) AS p95,
    quantile(0.99)(duration_ms) AS p99
FROM app_logs
WHERE ts >= now() - INTERVAL 1 HOUR
  AND level = 'INFO'
GROUP BY service
ORDER BY p99 DESC;

-- 3. 错误堆栈聚合
SELECT
    service,
    error_type,
    count() AS occurrences,
    min(ts) AS first_seen,
    max(ts) AS last_seen
FROM app_logs
WHERE level IN ('ERROR', 'FATAL')
  AND ts >= now() - INTERVAL 1 HOUR
GROUP BY service, error_type
ORDER BY occurrences DESC
LIMIT 50;

-- 4. 慢查询（duration > 1s）
SELECT
    service,
    message,
    duration_ms,
    ts
FROM app_logs
WHERE duration_ms > 1000
  AND ts >= now() - INTERVAL 1 HOUR
ORDER BY duration_ms DESC
LIMIT 100;
```

**案例**：
- Cloudflare：DNS 日志 + HTTP 日志，每天万亿级，ClickHouse 集群处理
- Uber：应用日志 + RIDER 日志，ClickHouse + ELK
- GitHub：所有 webhooks / events，ClickHouse

## 三、指标存储（TSDB）

**场景**：业务指标（DAU / GMV / 注册数）+ 服务器指标（CPU / Mem / 流量）。

```sql
CREATE TABLE metrics (
    ts DateTime,
    metric_name LowCardinality(String),   -- 'dau', 'gmv', 'cpu_usage'
    tags Map(LowCardinality(String), String),  -- {app: 'web', region: 'us'}
    value Float64
)
ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(ts)
ORDER BY (metric_name, ts)
TTL ts + INTERVAL 365 DAY;

-- 1. 查 DAU 趋势（按天）
SELECT
    toDate(ts) AS day,
    uniqExact(user_id) AS dau
FROM events
WHERE event_type = 'launch'
  AND ts >= now() - INTERVAL 30 DAY
GROUP BY day
ORDER BY day;

-- 2. GMV 同比
SELECT
    toDate(ts) AS day,
    sum(amount) AS gmv
FROM orders
WHERE status = 'paid'
  AND ts >= now() - INTERVAL 30 DAY
GROUP BY day
ORDER BY day;

-- 3. 服务器 CPU 99 分位（按 host）
SELECT
    host,
    quantile(0.99)(value) AS cpu_p99
FROM metrics
WHERE metric_name = 'cpu_usage'
  AND ts >= now() - INTERVAL 1 HOUR
GROUP BY host
ORDER BY cpu_p99 DESC;

-- 4. Prometheus remote_write 目标
-- Prometheus 配置：
-- remote_write:
--   - url: http://clickhouse:8123/api/v1/prom/write
--     headers: {X-ClickHouse-User: prometheus, X-ClickHouse-Database: metrics}
```

**案例**：
- Uber：所有业务指标（DAU / Rides / Eats）
- Cloudflare：网络流量指标
- GitHub：所有监控数据

## 四、实时数仓（核心）

**场景**：替代 Hive / Druid 的实时数仓。

```sql
-- 1. ODS（原始层）
CREATE TABLE ods_events (
    ts DateTime,
    user_id UInt64,
    event_type LowCardinality(String),
    properties String
) ENGINE = Kafka()
SETTINGS
    kafka_broker_list = 'kafka:9092',
    kafka_topic_list = 'raw_events',
    kafka_format = 'JSONEachRow',
    kafka_group_name = 'ods_consumer';

-- 2. DWD（明细层）
CREATE TABLE dwd_events (
    date Date,
    user_id UInt64,
    event_type LowCardinality(String),
    -- 解析后的 properties
    page String,
    amount Decimal(10, 2)
) ENGINE = MergeTree()
PARTITION BY date
ORDER BY (date, user_id, event_type);

CREATE MATERIALIZED VIEW ods_to_dwd TO dwd_events AS
SELECT
    toDate(ts) AS date,
    user_id,
    event_type,
    JSONExtractString(properties, 'page') AS page,
    toDecimal64(JSONExtractFloat(properties, 'amount'), 2) AS amount
FROM ods_events;

-- 3. DWS（汇总层）
CREATE TABLE dws_user_daily (
    date Date,
    user_id UInt64,
    pv UInt64,
    uv UInt8,  -- 0 或 1，用作 unique
    amount AggregateFunction(sum, Decimal(10, 2))
) ENGINE = AggregatingMergeTree()
PARTITION BY date
ORDER BY (date, user_id);

CREATE MATERIALIZED VIEW dwd_to_dws TO dws_user_daily AS
SELECT
    date,
    user_id,
    count() AS pv,
    1 AS uv,
    sumState(amount) AS amount
FROM dwd_events
GROUP BY date, user_id;

-- 4. ADS（应用层）
SELECT
    date,
    sum(pv) AS total_pv,
    sum(uv) AS total_uv,
    sumMerge(amount) AS total_amount
FROM dws_user_daily
WHERE date >= today() - 30
GROUP BY date
ORDER BY date;
```

**案例**：
- 字节跳动：实时数仓 DWD/DWS/ADS 三层架构
- 美团：实时数仓替代 Hive，秒级延迟
- 滴滴：司机 / 乘客 / 订单全链路

## 五、Bitmap 去重

**场景**：亿级用户去重（DAU / MAU）。

```sql
-- 1. 表设计
CREATE TABLE dau_bitmap (
    date Date,
    event_type LowCardinality(String),
    -- Bitmap 列存用户
    users AggregateFunction(uniq, UInt64)
) ENGINE = AggregatingMergeTree()
PARTITION BY date
ORDER BY (date, event_type);

-- 2. 写入
INSERT INTO dau_bitmap
SELECT
    toDate(event_time) AS date,
    event_type,
    uniqState(user_id)
FROM events
GROUP BY date, event_type;

-- 3. DAU 查
SELECT uniqMerge(users) AS dau
FROM dau_bitmap
WHERE date = today()
  AND event_type = 'launch';

-- 4. 多日累计
SELECT uniqMerge(users) AS mau
FROM dau_bitmap
WHERE date >= today() - 30;

-- 5. Bitmap 操作（位运算）
-- RoaringBitmap：用于精确去重
-- ClickHouse 内置：groupBitmapState() / groupBitmapMerge()

CREATE TABLE user_bitmap_daily (
    date Date,
    users AggregateFunction(groupBitmap, UInt64)
) ENGINE = MergeTree()
ORDER BY date;

INSERT INTO user_bitmap_daily
SELECT
    date,
    groupBitmapState(user_id)
FROM events
GROUP BY date;

-- 交集（两日都活跃）
SELECT
    bitmapCardinality(
        bitmapAnd(
            (SELECT groupBitmapMerge(users) FROM user_bitmap_daily WHERE date = '2026-08-01'),
            (SELECT groupBitmapMerge(users) FROM user_bitmap_daily WHERE date = '2026-08-02')
        )
    ) AS both_active;
```

**应用**：DAU/MAU/留存/漏斗/画像标签。

## 六、业务 OLAP（自由查询）

**场景**：业务分析师自助 BI 查询。

```sql
-- 1. 订单分析
SELECT
    toStartOfHour(created_at) AS hour,
    count() AS orders,
    sum(amount) AS gmv,
    uniq(user_id) AS paying_users
FROM orders
WHERE created_at >= today() - 7
GROUP BY hour
ORDER BY hour;

-- 2. 商品排行
SELECT
    product_id,
    product_name,
    count() AS sales,
    sum(amount) AS revenue
FROM order_items
WHERE created_at >= today() - 30
GROUP BY product_id, product_name
ORDER BY revenue DESC
LIMIT 100;

-- 3. 用户画像
SELECT
    age_group,
    gender,
    count() AS user_count,
    sum(total_spend) AS total_spend
FROM user_profiles
GROUP BY age_group, gender
ORDER BY total_spend DESC;
```

**案例**：
- 京东：BI 自助查询（替换 Hive + Impala）
- 美团：业务分析团队 SQL 入口
- 网易：游戏用户行为分析

## 关联章节

- **03-table-engine/overview**：表引擎
- **03-table-engine/materialized-view**：物化视图
- **05-ecosystem/overview**：生态集成
- **06-compare/overview**：选型对比

## 一句话总结

> **ClickHouse 6 大场景 = 埋点 + 日志 + 指标 + 实时数仓 + Bitmap + 业务 OLAP**。**每个都有大厂背书**。


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

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

- [es](https://java-px.bot.cd/es/):ES 对比
- [bigdata](https://java-px.bot.cd/bigdata/):大数据生态
- [postgresql](https://java-px.bot.cd/postgresql/):PostgreSQL 对比
