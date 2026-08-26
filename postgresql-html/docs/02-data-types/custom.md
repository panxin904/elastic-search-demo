---
title: 自定义类型
description: CREATE TYPE 实战
---

# 自定义类型

> **TL;DR**：`CREATE TYPE` 让 PG 支持**复合类型、枚举、范围**自定义。**复合类型**把多个字段绑成一行，**枚举**限定值集合，**范围**封装"区间"语义。

## 一句话定义

```
PG 自定义类型 = 复合类型（行）/ 枚举（固定集合）/ 范围（区间）/ 基类型（C 扩展）
```

## 复合类型（Composite Type）

**类似"行类型"**：把多个字段绑成一个类型。

```sql
-- 1. 定义复合类型
CREATE TYPE address AS (
  street TEXT,
  city TEXT,
  zip TEXT,
  country TEXT
);

-- 2. 用作表字段
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  name TEXT,
  home_address address
);

-- 3. 插入
INSERT INTO users (name, home_address) VALUES
  ('Alice', ROW('长安街 1 号', '北京', '100000', '中国'));

-- 4. 查询
SELECT (home_address).city FROM users WHERE id = 1;
-- '北京'

-- 5. 修改
UPDATE users 
SET home_address.city = '上海'    -- 注意语法
WHERE id = 1;
```

**作为函数参数 / 返回值**：

```sql
-- 返回复合类型
CREATE FUNCTION get_user(id INT) RETURNS users AS $$
  SELECT * FROM users WHERE id = $1;
$$ LANGUAGE SQL;

-- 调用
SELECT * FROM get_user(123);
```

## 枚举类型（ENUM）

**固定值集合**：状态字段、类型字段。

```sql
-- 1. 定义枚举
CREATE TYPE order_status AS ENUM (
  'pending', 'paid', 'shipped', 'delivered', 'cancelled'
);

-- 2. 用作表字段
CREATE TABLE orders (
  id BIGSERIAL PRIMARY KEY,
  status order_status DEFAULT 'pending'
);

-- 3. 插入
INSERT INTO orders (status) VALUES ('paid');
-- 自动校验：无效值报错
INSERT INTO orders (status) VALUES ('invalid');
-- ERROR: invalid input value for enum order_status: 'invalid'

-- 4. 查询
SELECT * FROM orders WHERE status = 'paid';

-- 5. 排序（按定义顺序）
SELECT * FROM orders ORDER BY status;
-- pending → paid → shipped → ...
```

### 添加新枚举值

```sql
-- 在末尾追加
ALTER TYPE order_status ADD VALUE 'returned';

-- 在指定位置插入（PG 9.6+）
ALTER TYPE order_status ADD VALUE 'refunded' BEFORE 'cancelled';
```

### 枚举 vs CHECK 约束

```sql
-- 用 CHECK（灵活但性能差）
CREATE TABLE orders (
  status TEXT CHECK (status IN ('pending', 'paid', 'shipped'))
);

-- 用 ENUM（严格且高效）
CREATE TABLE orders (
  status order_status
);
```

> **枚举优势**：**类型安全、存储紧凑、排序自然**。**CHECK 优势**：**灵活、可以随时改**。

## 范围类型（Range）

PG 内置 6 种范围类型（int4range / numrange / daterange / tsrange / tstzrange），也可自定义：

```sql
-- 自定义 float 范围类型
CREATE TYPE floatrange AS RANGE (
  subtype = float8,
  subtype_diff = float8mi
);

-- 用法
SELECT floatrange(1.0, 9.5, '[]');
```

详见 [range.md](/02-data-types/range)。

## 基类型（Base Type）

**用 C 语言扩展**，是 PG 扩展开发的核心。

```c
// 示例：实现一个复数类型
#include "fmgr.h"

PG_MODULE_MAGIC;

PG_FUNCTION_INFO_V1(complex_in);
PG_FUNCTION_INFO_V1(complex_out);

Datum complex_in(PG_FUNCTION_ARGS) {
  // 解析字符串 "1,2" → complex
}

Datum complex_out(PG_FUNCTION_ARGS) {
  // complex → 字符串 "1,2"
}
```

```sql
-- 注册
CREATE TYPE complex (
  input = complex_in,
  output = complex_out,
  internallength = 16,
  alignment = double
);
```

> **基类型开发门槛高**，**90% 场景用复合 / 枚举 / 范围足够**。

## 实战案例

### 案例 1：电商订单状态枚举

```sql
CREATE TYPE order_status AS ENUM (
  'created', 'paid', 'packed', 'shipped', 'delivered', 'refunded', 'cancelled'
);

CREATE TABLE orders (
  id BIGSERIAL PRIMARY KEY,
  status order_status DEFAULT 'created',
  amount NUMERIC(10,2)
);

-- 历史状态迁移（添加 'returned'）
ALTER TYPE order_status ADD VALUE 'returned' AFTER 'delivered';
```

### 案例 2：地址复合类型

```sql
CREATE TYPE address AS (
  street TEXT,
  city TEXT,
  state TEXT,
  zip TEXT,
  country TEXT
);

CREATE TABLE customers (
  id BIGSERIAL PRIMARY KEY,
  name TEXT,
  shipping_address address,
  billing_address address
);

-- 查北京客户
SELECT * FROM customers 
WHERE (shipping_address).city = '北京';
```

### 案例 3：自定义 IP 段类型

```sql
CREATE TABLE ip_allocations (
  range cidr,
  owner TEXT
);

CREATE INDEX idx_ip_range ON ip_allocations USING SPGIST (range);

-- 查 192.168.1.100 在哪个段
SELECT * FROM ip_allocations 
WHERE range >> '192.168.1.100'::inet;
```

## 一句话总结

> **CREATE TYPE 让 PG 类型系统可扩展**：**复合类型（行）**、**ENUM（枚举）**、**范围（区间）**是 3 大常用自定义类型。**枚举限定值集合** + **复合类型封装结构**，**避免散落的字典表**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
