---
title: 星型 / 雪花模型
---
# 星型 / 雪花模型

## 1. 星型模型（Star Schema）

```
              dim_date
                │
                │
dim_user ─── fact_sales ─── dim_product
                │
                │
              dim_store
```

**特点**：
- 事实表在中间
- 维度表直接连接（无中间层）
- 维度表反范式（冗余换性能）

**优势**：
- 简单直观
- 查询快（少 join）
- 适合 OLAP

**缺点**：
- 维度表冗余
- 更新成本（每行更新）

## 2. 雪花模型（Snowflake Schema）

```
            dim_date
              │
              │
            dim_month
              │
              │
dim_country ── dim_city ─── fact_sales
              │
              │
            dim_store
```

**特点**：
- 维度表进一步规范化
- 多层结构（dim_date → dim_month → dim_year）
- 节省存储

**优势**：
- 节省存储
- 数据一致

**缺点**：
- 多层 join（性能差）
- 复杂

## 3. 对比

| | 星型 | 雪花 |
|--|------|------|
| 性能 | 高（少 join）| 较低（多 join）|
| 存储 | 大（冗余）| 小（规范化）|
| 易理解 | 简单 | 复杂 |
| 适用 | OLAP 查询 | 维度数据稳定 |
| 推荐 | 90% 场景 | 维度频繁变 |

## 4. 何时选

```
选星型：
  - OLAP 查询频繁
  - 维度稳定（变化少）
  - 性能优先
  - 大多数场景

选雪花：
  - 维度频繁变（如产品类目调整）
  - 存储成本敏感
  - 维度层级深（省/市/区）
```

## 5. 实战：星型

```sql
-- 事实表
CREATE TABLE fact_orders (
  order_id BIGINT,
  user_id BIGINT,
  product_id BIGINT,
  date_id INT,
  amount DECIMAL(10,2),
  quantity INT
) PARTITIONED BY (dt STRING)
STORED AS PARQUET;

-- 维度表
CREATE TABLE dim_user (
  user_id BIGINT,
  user_name STRING,
  user_age INT,
  user_gender STRING,
  user_city STRING,
  user_vip_level STRING
);

CREATE TABLE dim_product (
  product_id BIGINT,
  product_name STRING,
  product_category STRING,
  product_price DECIMAL(10,2)
);

CREATE TABLE dim_date (
  date_id INT,
  date_value DATE,
  year INT,
  month INT,
  day INT,
  quarter INT,
  weekday STRING
);
```

## 6. 实战：雪花

```sql
-- 规范化维度
CREATE TABLE dim_country (
  country_id INT,
  country_name STRING
);

CREATE TABLE dim_city (
  city_id INT,
  country_id INT,
  city_name STRING
);

CREATE TABLE dim_user (
  user_id BIGINT,
  city_id INT,
  user_name STRING,
  user_age INT
);

-- 事实表 join 多次
SELECT
  c.country_name,
  ci.city_name,
  u.user_name,
  SUM(f.amount)
FROM fact_orders f
JOIN dim_user u ON f.user_id = u.user_id
JOIN dim_city ci ON u.city_id = ci.city_id
JOIN dim_country c ON ci.country_id = c.country_id
GROUP BY c.country_name, ci.city_name, u.user_name;
```

## 7. 实战混合

```
主表：星型（性能）
扩展表：雪花（维度稳定场景）
  - 比如地域（省/市/区）：雪花（变化少）
  - 比如商品类目：星型（变化频繁，平铺）
```

## 8. 数据仓库工具支持

| 工具 | 星型 | 雪花 |
|------|------|------|
| Hive | ✅ | ✅ |
| Spark SQL | ✅ | ✅ |
| Snowflake | ✅ 推荐 | ✅ |
| ClickHouse | ✅ 推荐 | 不推荐（join 弱） |
| Doris / StarRocks | ✅ 推荐 | 不推荐 |
| Druid | ✅（star） | 不推荐 |

**OLAP 引擎（ClickHouse / Doris）几乎都用星型**，因为 join 性能弱。

## 9. 选型决策

```
OLAP 引擎（ClickHouse / Doris / StarRocks）：
  → 星型（首选）

传统数仓（Hive / Snowflake）：
  → 星型 + 雪花（混合）

OLTP 场景：
  → 3NF（无事实表 / 维度表概念）
```

## 10. 实战 checklist

- [ ] 维度识别（不变 vs 变）
- [ ] 粒度确认（事实表一行代表什么）
- [ ] 星型（性能）vs 雪花（规范）
- [ ] 混合策略
- [ ] 工具支持（OLAP 引擎选型）
- [ ] 监控（查询延迟）

## 11. 实战案例

### 案例 1：互联网电商

```
星型：
  fact_orders（每日 100 亿）
  dim_user / dim_product / dim_channel

OLAP 引擎（Doris / ClickHouse）：
  星型（推荐）
  → 子表预聚合（rollup）
  → 查询毫秒级
```

### 案例 2：金融银行

```
雪花 + 星型：
  雪花（dim_region 省/市/区）
  星型（fact_transactions 交易）

Hive + Snowflake：
  3NF 整合层
  集市层用星型
```

## 🔗 下一步
- [OLAP vs OLTP](/08-modeling/olap-oltp)
- [Inmon vs Kimball](/08-modeling/inmon-kimball)
- [Data Vault](/08-modeling/data-vault)
