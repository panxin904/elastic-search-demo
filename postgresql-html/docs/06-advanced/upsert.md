---
title: UPSERT
description: INSERT ON CONFLICT 实战
---

# UPSERT

> **TL;DR**：UPSERT = **不存在则插入，存在则更新**。**PG 用 `INSERT ON CONFLICT` 实现**，比 MySQL `INSERT ... ON DUPLICATE KEY UPDATE` 更标准、更安全。

## 一句话定义

```
UPSERT = INSERT + UPDATE
       = "如果不存在则 INSERT，否则 UPDATE"
       = 单条 SQL 原子操作
```

## 基本语法

```sql
INSERT INTO table (cols) VALUES (...)
ON CONFLICT (conflict_target) DO UPDATE SET ...
[RETURNING ...];
```

## 实战案例

### 案例 1：单条 upsert

```sql
CREATE TABLE users (
  id BIGINT PRIMARY KEY,
  name TEXT NOT NULL,
  last_login_at TIMESTAMPTZ,
  login_count INT DEFAULT 0
);

-- upsert
INSERT INTO users (id, name, last_login_at, login_count)
VALUES (123, 'Alice', now(), 1)
ON CONFLICT (id) DO UPDATE SET
  last_login_at = EXCLUDED.last_login_at,
  login_count = users.login_count + 1;
-- 如果 id=123 存在：更新 last_login_at 和 login_count
-- 如果不存在：插入
```

### 案例 2：库存扣减

```sql
CREATE TABLE products (
  id BIGINT PRIMARY KEY,
  stock INT NOT NULL
);

-- 原子扣减
UPDATE products 
SET stock = stock - 1 
WHERE id = 1 AND stock > 0;
-- 返回 1 行 = 成功扣减，0 行 = 库存不足
```

或者用 INSERT ON CONFLICT：

```sql
INSERT INTO products (id, stock) VALUES (1, 99)
ON CONFLICT (id) DO UPDATE SET stock = products.stock - 1
WHERE products.stock > 0
RETURNING stock;
-- 返回新库存；如果 -1 不存在则不操作
```

### 案例 3：计数器自增

```sql
CREATE TABLE counters (
  name TEXT PRIMARY KEY,
  value BIGINT DEFAULT 0
);

-- 计数器 +1
INSERT INTO counters (name, value) VALUES ('page_view', 1)
ON CONFLICT (name) DO UPDATE SET value = counters.value + 1
RETURNING value;
-- 返回新值
```

### 案例 4：批量 upsert

```sql
INSERT INTO products (id, name, price) VALUES
  (1, 'A', 100),
  (2, 'B', 200),
  (3, 'C', 300)
ON CONFLICT (id) DO UPDATE SET
  name = EXCLUDED.name,
  price = EXCLUDED.price;
-- 一次性 upsert 3 行
```

## EXCLUDED 关键字

```sql
-- EXCLUDED 引用 INSERT VALUES 中的值
INSERT INTO users (id, name) VALUES (1, 'Alice')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;
-- 等价于：
--   name = 'Alice'
```

## DO NOTHING 模式

```sql
-- 仅在不存在时插入
INSERT INTO users (id, name) VALUES (1, 'Alice')
ON CONFLICT (id) DO NOTHING;
-- 存在则什么都不做（不报错也不更新）
```

## RETURNING 返回值

```sql
INSERT INTO counters (name, value) VALUES ('click', 1)
ON CONFLICT (name) DO UPDATE SET value = counters.value + 1
RETURNING name, value;
-- 返回 {'click', 42}
```

## MERGE（PG 15+）

**PG 15+ 新增标准 SQL MERGE 语法**：

```sql
MERGE INTO products AS t
USING (VALUES (1, 100), (2, 200)) AS s(id, price)
ON t.id = s.id
WHEN MATCHED THEN
  UPDATE SET price = s.price
WHEN NOT MATCHED THEN
  INSERT (id, price) VALUES (s.id, s.price);
```

**vs INSERT ON CONFLICT**：

| 维度 | ON CONFLICT | MERGE |
|---|---|---|
| 标准 | PG 特有 | ANSI SQL |
| 灵活性 | 单表 | 多表 / 复杂条件 |
| 性能 | 优 | 略慢（解析复杂） |
| 推荐 | 简单 upsert | 复杂业务逻辑 |

## 实战案例

### 案例：用户最后登录时间

```sql
CREATE TABLE user_logins (
  user_id BIGINT PRIMARY KEY,
  last_login_at TIMESTAMPTZ NOT NULL,
  login_count INT NOT NULL DEFAULT 1
);

-- 每次登录调用
INSERT INTO user_logins (user_id, last_login_at, login_count)
VALUES (123, now(), 1)
ON CONFLICT (user_id) DO UPDATE SET
  last_login_at = EXCLUDED.last_login_at,
  login_count = user_logins.login_count + 1;
```

### 案例：幂等消息处理

```sql
-- Kafka 消息处理，message_id 幂等
INSERT INTO processed_messages (message_id, processed_at)
VALUES ('msg-12345', now())
ON CONFLICT (message_id) DO NOTHING
RETURNING message_id;
-- 如果 message_id 已处理，返回 0 行（消息被跳过）
-- 如果新消息，返回 1 行（处理）
```

## 一句话总结

> **UPSERT = INSERT ON CONFLICT**：**`ON CONFLICT (key) DO UPDATE SET ... = EXCLUDED.field`**。**EXCLUDED 引用 INSERT 值，DO NOTHING 跳过**。**PG 15+ 新增标准 MERGE**，复杂场景用 MERGE，简单场景用 ON CONFLICT。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
