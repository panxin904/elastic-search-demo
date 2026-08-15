---
title: Generated 列
description: PG 12+ 计算列
---

# Generated 列

> **TL;DR**：PG 12+ 支持 **GENERATED 列**，自动从其他列计算。**类似 MySQL Generated Column + Oracle 虚列**，但 PG 是 STORED（物理存储）。

## 一句话定义

```
Generated 列 = 表内自动计算列
            = INSERT/UPDATE 时自动更新
            = 可建索引、可直接查
```

## 两种模式

| 模式 | 存储 | 性能 |
|---|---|---|
| `STORED` | 物理存储 | 读快，写稍慢 |
| `VIRTUAL` (PG 18+) | 不存储 | 写快，读时算 |

> **PG 12-17：只有 STORED**。**PG 18+：新增 VIRTUAL**。

## 基本使用

```sql
-- 创建表
CREATE TABLE orders (
  id BIGSERIAL PRIMARY KEY,
  quantity INT NOT NULL,
  unit_price NUMERIC(10,2) NOT NULL,
  -- Generated 列
  total NUMERIC(10,2) GENERATED ALWAYS AS (quantity * unit_price) STORED
);

-- 插入
INSERT INTO orders (quantity, unit_price) VALUES (3, 99.50);
-- total 自动 = 297.50

-- 查询
SELECT * FROM orders;
-- id | quantity | unit_price | total
-- 1  | 3        | 99.50      | 297.50
```

## 实战案例

### 案例 1：自动金额计算

```sql
CREATE TABLE order_items (
  id BIGSERIAL PRIMARY KEY,
  product_id BIGINT NOT NULL,
  quantity INT NOT NULL CHECK (quantity > 0),
  unit_price NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0),
  discount NUMERIC(3,2) DEFAULT 0,
  -- Generated：折后总价
  subtotal NUMERIC(10,2) GENERATED ALWAYS AS (
    quantity * unit_price * (1 - discount)
  ) STORED,
  -- Generated：完整字段
  full_label TEXT GENERATED ALWAYS AS (
    product_id::text || ' x ' || quantity::text
  ) STORED
);

-- 索引
CREATE INDEX idx_order_items_subtotal ON order_items (subtotal);
```

### 案例 2：自动拼接全名

```sql
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  first_name TEXT,
  middle_name TEXT,
  last_name TEXT,
  full_name TEXT GENERATED ALWAYS AS (
    trim(both ' ' from 
      coalesce(first_name, '') || ' ' || 
      coalesce(middle_name, '') || ' ' || 
      coalesce(last_name, '')
    )
  ) STORED
);

-- 插入
INSERT INTO users (first_name, middle_name, last_name) 
VALUES ('张', '三', '丰');
-- full_name 自动 = '张 三 丰'
```

### 案例 3：JSONB 自动字段

```sql
CREATE TABLE events (
  id BIGSERIAL PRIMARY KEY,
  data JSONB NOT NULL,
  -- 从 JSONB 提取
  event_type TEXT GENERATED ALWAYS AS (data->>'type') STORED,
  user_id BIGINT GENERATED ALWAYS AS ((data->>'user_id')::BIGINT) STORED,
  event_ts TIMESTAMPTZ GENERATED ALWAYS AS ((data->>'ts')::TIMESTAMPTZ) STORED
);

CREATE INDEX idx_events_type ON events (event_type);
CREATE INDEX idx_events_user ON events (user_id);
```

## 与视图 / 触发器的对比

```sql
-- 1. 视图（每次查询重算）
CREATE VIEW order_view AS
SELECT id, quantity * unit_price AS total FROM orders;
-- 性能差，不占存储

-- 2. 触发器（写入时算）
CREATE FUNCTION calc_total() RETURNS TRIGGER AS $$
BEGIN
  NEW.total := NEW.quantity * NEW.unit_price;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_orders_total
BEFORE INSERT OR UPDATE ON orders
FOR EACH ROW EXECUTE FUNCTION calc_total();
-- 灵活，但手写麻烦

-- 3. Generated 列（推荐）
total NUMERIC GENERATED ALWAYS AS (quantity * unit_price) STORED;
-- 自动、简单、有索引
```

## 限制

```sql
-- ❌ 不能引用其他 Generated 列
CREATE TABLE t (
  a INT,
  b INT GENERATED ALWAYS AS (a * 2) STORED,
  c INT GENERATED ALWAYS AS (b + 1) STORED  -- 报错
);

-- ✅ 必须直接引用基础列
CREATE TABLE t (
  a INT,
  b INT GENERATED ALWAYS AS (a * 2) STORED,
  c INT GENERATED ALWAYS AS (a * 2 + 1) STORED  -- OK
);

-- ❌ 不能用子查询
GENERATED ALWAYS AS ((SELECT max(id) FROM other_table)) STORED  -- 报错

-- ❌ 不能用 volatile 函数
GENERATED ALWAYS AS (random()) STORED  -- 报错
```

## 一句话总结

> **Generated 列 = 物理存储的计算列**：**自动维护、可建索引、读写都好**。**PG 12+ STORED / PG 18+ 新增 VIRTUAL**。**金额、拼接、JSONB 提取字段**都是典型场景。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
