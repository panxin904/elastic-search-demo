---
title: Inmon vs Kimball
---
# Inmon vs Kimball 建模

## 1. 两大流派

| | Inmon | Kimball |
|--|-------|---------|
| 出品 | Bill Inmon（"数据仓库之父"） | Ralph Kimball |
| 架构 | 企业级总线（EDW） | 数据集市（DM） |
| 范式 | 第三范式（3NF） | 星型 / 雪花（维度建模） |
| 起点 | 企业级中央数据仓库 | 部门级数据集市 |
| 整合 | 一次（中央） | 各部门自建后整合 |
| 周期 | 长（年） | 短（周） |

## 2. Inmon 架构

```
源系统 1, 2, 3 ... 源系统 n
   ↓
  ┌────────────────────────┐
  │   企业级中央数据仓库（EDW） │  ← 第三范式（3NF）
  │   整合 + 主数据           │
  └────────────────────────┘
   ↓ 数据集市（按部门）
  财务集市  /  销售集市  /  运营集市
```

**特点**：
- 数据完整、一致（EDW 是 single source of truth）
- 3NF 减少冗余
- 实施周期长（先建 EDW → 再建集市）
- 适合大型企业

## 3. Kimball 架构

```
源系统 1, 2, 3 ... 源系统 n
   ↓
  各部门数据集市（DM）
  财务集市 + 销售集市 + 运营集市
   ↓
  一致性维度（Conformed Dimension）整合
```

**特点**：
- 部门自建（快速响应）
- 星型 / 雪花（维度建模）
- 维度统一（共享维度）
- 实施快（先集市后整合）

## 4. 核心区别

| | Inmon | Kimball |
|--|-------|---------|
| 起点 | 全局 | 部门 |
| 整合 | 早（中央仓） | 晚（集市） |
| 范式 | 3NF | 星型 / 雪花 |
| 周期 | 长 | 短 |
| 适用 | 大型 / 金融 | 互联网 / 快速迭代 |

## 5. Kimball 维度建模

### 事实表

```
fact_sales
- order_id (FK → dim_order)
- user_id (FK → dim_user)
- product_id (FK → dim_product)
- date_id (FK → dim_date)
- store_id (FK → dim_store)
- amount, quantity
- created_at
```

**特点**：只存度量（数值），不含描述。

### 维度表

```
dim_user
- user_id (PK)
- name
- age
- gender
- city
- register_date
- vip_level
```

**特点**：描述性属性。

### 星型 vs 雪花

星型（Star Schema）：
- 事实表居中
- 维度表直接连事实表
- 反范式（性能优先）

雪花（Snowflake）：
- 维度表进一步规范化
- 节省存储
- 多 join（性能略差）

## 6. 实战案例：电商销售分析

```sql
-- Kimball 星型 schema
CREATE TABLE fact_orders (
  order_id BIGINT,
  user_id BIGINT,
  product_id BIGINT,
  date_id INT,
  order_amount DECIMAL(10,2),
  order_quantity INT
) PARTITIONED BY (dt STRING);

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
  product_brand STRING,
  product_price DECIMAL(10,2)
);

CREATE TABLE dim_date (
  date_id INT,
  date DATE,
  year INT,
  month INT,
  day INT,
  weekday STRING
);

-- 典型查询
SELECT
  d.year,
  d.month,
  p.product_category,
  u.user_vip_level,
  COUNT(*) AS order_cnt,
  SUM(f.order_amount) AS gmv
FROM fact_orders f
JOIN dim_user u ON f.user_id = u.user_id
JOIN dim_product p ON f.product_id = p.product_id
JOIN dim_date d ON f.date_id = d.date_id
WHERE f.dt BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY d.year, d.month, p.product_category, u.user_vip_level;
```

## 7. 缓慢变化维（SCD）

维度表会变（如用户改地址、商品换类目），怎么处理？

| 类型 | 描述 |
|------|------|
| SCD Type 1 | 直接覆盖（无历史） |
| SCD Type 2 | 保留历史（新增一行 + 生效时间） |
| SCD Type 3 | 当前 + 前一值（增加列） |
| SCD Type 4 | 历史表（独立表） |

**推荐 Type 2**（最常用）：

```sql
-- dim_user 增加列
user_id, name, city, valid_from, valid_to, is_current
1, Alice, Beijing, 2020-01-01, 2023-06-30, false
1, Alice, Shanghai, 2023-07-01, 9999-12-31, true
```

事实表 join 维度表时取 `is_current=true` 的最新行。

## 8. 实战选型

| 场景 | 选 |
|------|-----|
| 大型 / 金融 / 强治理 | Inmon（3NF 中央仓） |
| 互联网 / 快速迭代 / 多部门 | Kimball（维度集市） |
| 中型 / 混合 | Kimball 为主 + Inmon 思想 |

**实践**：互联网公司 90% 用 Kimball 思想 + Data Vault（3NF 中央层）变体。

## 9. Data Vault（3NF + Kimball 混合）

```
Hub（核心实体，3NF）
  - 用户 hub
  - 订单 hub
  - 商品 hub
Link（关系）
  - 用户-订单 link
  - 用户-地址 link
Satellite（属性，Kimball 风格）
  - 用户画像 satellite
  - 订单明细 satellite
```

**特点**：
- 3NF 但只存 hub + link（无冗余）
- Satellite 灵活扩展
- 适合敏捷数据建模

**现代实践**：Hub + Link 是 3NF；Satellite 是 Kimball 风格。

## 10. 实战 checklist

- [ ] 业务过程识别（销售 / 库存 / 营销 ...）
- [ ] 粒度（事实表一行代表什么？）
- [ ] 维度识别（用户 / 商品 / 时间 / 地区 ...）
- [ ] 星型 vs 雪花
- [ ] SCD 策略（Type 2 推荐）
- [ ] 周期快照（拉链表 / 累加表）

## 11. 实战案例

### 案例 1：互联网电商

```
Kimball：
  fact_orders / fact_payments / fact_clicks
  dim_user / dim_product / dim_date / dim_channel
  周期：每天 snapshot 维度表
  加载：CDC → Kafka → Spark / Flink → Iceberg → Doris

Inmon：
  EDW（中央仓）
  按主题域：销售域 / 库存域 / 财务域
  3NF 整合
  
实践：Inmon 中央层 + Kimball 应用层
```

## 🔗 下一步
- [OLAP vs OLTP](/08-modeling/olap-oltp)
- [星型 / 雪花模型](/08-modeling/star-snowflake)
- [Data Vault](/08-modeling/data-vault)
- [数仓架构 Snowflake](/09-dw-architecture/snowflake)
