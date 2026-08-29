---
title: Data Vault
date: 2026-08-15  # date-auto-injected
---
# Data Vault 建模

## 1. 是什么

Data Vault = 3NF + Kimball 混合方法，专为数据仓库设计。

```
Hub（核心实体，3NF）
  - 业务键（自然键 / 业务标识）
  - 少量属性
  - 不变 + 少量变化

Link（关系）
  - 多对多关联
  - 描述 Hub 之间的关系
  - 时间戳

Satellite（属性，Kimball 风格）
  - 大量属性（经常变）
  - 时效性（生效时间 / 失效时间）
  - 历史记录
```

## 2. 三大组件

### Hub（核心）

```sql
CREATE TABLE hub_user (
  hub_user_hk CHAR(32) PRIMARY KEY,  -- hash key (MD5/SHA-256)
  user_id BIGINT NOT NULL,           -- 业务键
  load_date TIMESTAMP NOT NULL,     -- 入仓时间
  record_source STRING NOT NULL,
  UNIQUE (user_id)
);
```

**特点**：只存业务键（稳定）+ 入仓时间 + 来源。

### Link（关系）

```sql
CREATE TABLE link_user_order (
  link_user_order_hk CHAR(32) PRIMARY KEY,
  hub_user_hk CHAR(32) NOT NULL,
  hub_order_hk CHAR(32) NOT NULL,
  load_date TIMESTAMP NOT NULL,
  record_source STRING NOT NULL,
  FOREIGN KEY (hub_user_hk) REFERENCES hub_user(hub_user_hk)
);
```

**特点**：多对多关联，独立表。

### Satellite（属性）

```sql
CREATE TABLE sat_user_profile (
  hub_user_hk CHAR(32) NOT NULL,
  load_date TIMESTAMP NOT NULL,
  load_end_date TIMESTAMP,  -- NULL = 当前
  user_name STRING,
  user_age INT,
  user_city STRING,
  user_vip_level STRING,
  hash_diff CHAR(32),  -- 变化检测
  PRIMARY KEY (hub_user_hk, load_date)
);
```

**特点**：所有历史 + 当前，Kimball 风格的缓慢变化维。

## 3. 完整例子

```sql
-- 1. Hub（核心实体）
hub_user (hub_user_hk, user_id, load_date, record_source)
hub_order (hub_order_hk, order_id, load_date, record_source)
hub_product (hub_product_hk, product_id, ...)

-- 2. Link（关系）
link_user_order (link_user_order_hk, hub_user_hk, hub_order_hk, ...)

-- 3. Satellite（属性）
sat_user_profile (hub_user_hk, load_date, load_end_date, user_name, user_age, user_city, ...)
sat_order_detail (hub_order_hk, load_date, ..., amount, quantity, ...)

-- 4. 查询（join 3 类）
SELECT
  u.user_id,
  u.user_name,
  u.user_city,
  o.amount,
  o.quantity,
  d.year,
  d.month
FROM hub_user h
JOIN sat_user_profile u ON h.hub_user_hk = u.hub_user_hk AND u.load_end_date IS NULL
JOIN link_user_order l ON h.hub_user_hk = l.hub_user_hk
JOIN hub_order ho ON l.hub_order_hk = ho.hub_order_hk
JOIN sat_order_detail o ON ho.hub_order_hk = o.hub_order_hk AND o.load_end_date IS NULL
JOIN dim_date d ON DATE(o.create_time) = d.date_value
WHERE d.year = 2024 AND d.month = 1;
```

## 4. 实战特性

| | Inmon | Kimball | Data Vault |
|--|-------|---------|-------------|
| 范式 | 3NF | 星型 / 雪花 | 3NF + 卫星 |
| 整合 | 早 | 晚 | 随时（增量） |
| 历史 | 弱 | 弱（SCD） | 强（时序） |
| 实施 | 长 | 短 | 中 |
| 适用 | 大型金融 | 互联网 | 中大型 / 敏捷 |

## 5. 实战选型

| 场景 | 选 |
|------|-----|
| 大型 / 金融 / 强合规 | Inmon 或 Data Vault |
| 互联网 / 快速迭代 | Kimball |
| 中大型 / 敏捷 + 合规 | Data Vault |
| 历史追溯要求高 | Data Vault |

## 6. 实战案例

### 案例 1：银行数仓

```
源系统（核心 + 信贷 + 财务）
   ↓
Hub（核心实体）
  - 客户 hub / 账户 hub / 交易 hub
   ↓
Link
  - 客户-账户 / 账户-交易
   ↓
Satellite（属性）
  - 客户画像（时效性）
  - 账户余额历史
  - 交易明细
   ↓
集市（Kimball 风格）
  - 风控集市 / 监管集市
```

### 案例 2：互联网电商

```
Kimball 为主：
  fact_orders（订单）
  dim_user（用户）
  dim_product（商品）

少数 Hub：
  hub_user（核心用户）
  hub_order（核心订单）
```

混合：99% Kimball + 1% Data Vault（关键主数据）。

## 7. 实战工具

| 工具 | 特点 |
|------|------|
| dbtvault | dbt + Data Vault |
| VaultSpeed | 商业 |
| DataVault Builder | 商业 |
| dbt | Kimball + 自定义 |

## 8. 实战 checklist

- [ ] Hub 设计（业务键 + 哈希）
- [ ] Link 设计（多对多）
- [ ] Satellite 设计（时序 + 历史）
- [ ] ETL / ELT 加载（增量）
- [ ] 查询 join 3 类
- [ ] 性能调优（哈希 join）

## 9. 实战建议

1. **不要过度 DV 化**：Hub 太多 join 也慢
2. **混合 Kimball + DV**：集市用 Kimball，中央用 DV
3. **哈希键 vs 业务键**：哈希 key（性能）+ 业务 key（人类可读）
4. **时间戳必带**：所有 Satellite 必带 load_date / load_end_date
5. **审计日志**：单独 Satellite（sat_audit）

## 10. 实战案例：完整 DV 模型

```sql
-- 客户域
hub_customer (hub_customer_hk, customer_id, load_date, source)
hub_account (hub_account_hk, account_id, load_date, source)
hub_address (hub_address_hk, address_id, load_date, source)

link_customer_account (link_customer_account_hk, hub_customer_hk, hub_account_hk, ...)

sat_customer_profile (hub_customer_hk, load_date, load_end_date, name, age, ...)
sat_account_balance (hub_account_hk, load_date, load_end_date, balance, type, ...)
sat_address_detail (hub_address_hk, load_date, load_end_date, country, city, ...)

-- 交易域
hub_transaction (hub_transaction_hk, transaction_id, load_date, source)
link_account_transaction (...)
sat_transaction_detail (...)

-- 集市层（Kimball 风格）
report_customer_balance AS
SELECT c.customer_id, a.account_id, ab.balance
FROM hub_customer c
JOIN link_customer_account ca ...
JOIN sat_account_balance ab ...
WHERE ab.load_end_date IS NULL;
```

## 🔗 下一步
- [Inmon vs Kimball](/08-modeling/inmon-kimball)
- [星型 / 雪花](/08-modeling/star-snowflake)
- [数据湖 三剑客](/10-data-lake/three-pillars)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [kafka](https://java-px.bot.cd/kafka/):Kafka 流处理
- [es](https://java-px.bot.cd/es/):Elasticsearch
- [clickhouse](https://java-px.bot.cd/clickhouse/):ClickHouse OLAP
