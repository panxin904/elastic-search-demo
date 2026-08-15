---
title: 数据类型
---

# 📊 MySQL 数据类型

> 数据类型选错了，性能会差 **10 倍甚至 100 倍**。理解每个类型的存储方式和适用场景，是 MySQL 优化的基础。

## 🎯 选型原则

```
更小的通常更好 → 占用更少磁盘、内存、CPU
简单就好 → 整数比字符串操作代价低
避免 NULL → 难以优化，索引不存储 NULL（除非特别需要）
```

## 🔢 整数类型

| 类型 | 字节 | 范围（无符号） | 范围（有符号） | 用途 |
|---|---|---|---|---|
| `TINYINT` | 1 | 0~255 | -128~127 | 状态、布尔 (0/1) |
| `SMALLINT` | 2 | 0~65535 | -32768~32767 | 小范围计数 |
| `MEDIUMINT` | 3 | 0~1677万 | -838万~838万 | 中等范围 |
| `INT` | 4 | 0~42亿 | -21亿~21亿 | **最常用** |
| `BIGINT` | 8 | 0~1844京 | -922京~922京 | 自增 ID / 大数据量 |

```sql
CREATE TABLE demo (
  status TINYINT UNSIGNED NOT NULL DEFAULT 0,    -- 0-255 状态
  age    TINYINT UNSIGNED,                        -- 0-255 年龄
  view_count INT UNSIGNED DEFAULT 0,              -- 浏览量
  -- ⚠️ 自增 ID 必须用 UNSIGNED，范围翻倍
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY
) ENGINE=InnoDB;

-- 显示宽度（已过时，仅做了解）
-- INT(11) 中的 11 不限制存储范围，只是显示宽度，建议省略
```

**关键点：**
- ✅ **自增主键必须 `UNSIGNED`**，范围翻倍
- ✅ 状态字段用 `TINYINT`，省 3 倍空间
- ❌ 不要为了"未来扩展"用 BIGINT，浪费 50% 空间

## 💰 精确小数（金融首选）

| 类型 | 字节 | 范围 | 用途 |
|---|---|---|---|
| `DECIMAL(M,D)` | 变长 | 精确 | **金额、汇率** |
| `NUMERIC` | 同上 | 同上 | DECIMAL 的同义词 |

```sql
-- DECIMAL(M, D): M=总位数, D=小数位数
price DECIMAL(10, 2),    -- 总共 10 位，小数 2 位：最大 99999999.99
amount DECIMAL(18, 4),  -- 更高精度（4 位小数）

-- ⚠️ 浮点数（FLOAT / DOUBLE）不能用于金额！
-- 它们是近似值，可能出现 0.1 + 0.2 ≠ 0.3
```

**为什么不用 FLOAT/DOUBLE 存金额？**

```sql
CREATE TABLE wrong_money (
  amount FLOAT
);
INSERT INTO wrong_money VALUES (0.1), (0.2);
SELECT SUM(amount) FROM wrong_money;
-- 结果：0.30000000000000004 ❌
```

## 🔬 浮点数

| 类型 | 字节 | 精度 |
|---|---|---|
| `FLOAT` | 4 | 单精度，约 7 位有效数字 |
| `DOUBLE` | 8 | 双精度，约 15 位有效数字 |

```sql
-- 适用：科学计算、地理坐标等允许误差的场景
latitude DOUBLE,         -- GPS 坐标
sensor_value FLOAT,      -- 传感器读数
```

## 📝 字符串类型

| 类型 | 最大长度 | 字符集影响 | 用途 |
|---|---|---|---|
| `CHAR(N)` | 255 | 是 | 定长字符串（MD5、UUID、手机号） |
| `VARCHAR(N)` | 65535 | 是 | **变长字符串（最常用）** |
| `TINYTEXT` | 255 | 是 | 短文本 |
| `TEXT` | 65535 | 是 | 长文本（文章、评论） |
| `MEDIUMTEXT` | 16MB | 是 | 大文本 |
| `LONGTEXT` | 4GB | 是 | 超大文本 |
| `BINARY(N)` | 255 | 否 | 定长二进制 |
| `VARBINARY(N)` | 65535 | 否 | 变长二进制 |
| `BLOB` | 65535 | 否 | 二进制大对象 |

```sql
-- CHAR vs VARCHAR 选择
md5 CHAR(32),            -- MD5 固定 32 位
phone CHAR(11),           -- 手机号固定 11 位
name VARCHAR(100),        -- 姓名变长
bio TEXT,                 -- 个人简介
article MEDIUMTEXT,       -- 文章正文
avatar VARBINARY(200),    -- 头像二进制
```

**关键点：**
- ✅ CHAR 性能稍好（定长，无需长度字节）
- ❌ VARCHAR(255) 不一定省空间：超过 255 字节会占用 2 字节长度
- ⚠️ 频繁更新的字段用 VARCHAR，长度变化会导致页分裂

### VARCHAR(N) 的 N 是字符数还是字节数？

**字符数**。但总字节数受字符集影响：
- utf8mb4：每个字符最多 4 字节
- utf8：每个字符最多 3 字节
- latin1：每个字符 1 字节

```sql
-- 查看行的最大字节数
SHOW VARIABLES LIKE 'innodb_large_prefix';  -- 8.0 默认 ON
-- 行总大小（所有字段 + 头部）不能超过 65535 字节

-- 例如 VARCHAR(21845) 用 utf8mb4 会超过单行限制
-- 实际：21845 × 4 = 87380 > 65535 ❌
```

## ⏰ 时间日期类型

| 类型 | 字节 | 范围 | 用途 |
|---|---|---|---|
| `YEAR` | 1 | 1901~2155 | 年份 |
| `DATE` | 3 | 1000-01-01 ~ 9999-12-31 | 日期 |
| `TIME` | 3 | -838:59:59 ~ 838:59:59 | 时间 |
| `DATETIME` | 8 | 1000-01-01 ~ 9999-12-31 | **日期+时间（推荐）** |
| `TIMESTAMP` | 4 | 1970-01-01 ~ 2038-01-19 | 时间戳 |

```sql
-- DATETIME vs TIMESTAMP
CREATE TABLE events (
  id INT PRIMARY KEY AUTO_INCREMENT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  -- DATETIME 不受时区影响，存储什么显示什么
  -- 范围大：1000-9999 年
  
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  -- 自动更新为最后修改时间
  
  logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  -- TIMESTAMP 受时区影响，存储为 UTC
  -- 范围小：1970-2038 年
  -- 4 字节，节省空间
);

-- ❌ 不要用字符串存日期
-- '2025-01-15' 占 10 字节，且无法用日期函数
```

**DATETIME vs TIMESTAMP 选择：**
- 需要跨时区 → TIMESTAMP
- 范围大、简单稳定 → DATETIME（**推荐**）

## 🎲 JSON 类型（MySQL 5.7+）

```sql
CREATE TABLE products (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100),
  -- 灵活的扩展字段
  attrs JSON,           -- {"color": "red", "size": "XL", "tags": [...]}
  meta JSON
);

-- 插入 JSON
INSERT INTO products (name, attrs) VALUES
('iPhone', '{"color": "red", "storage": 256}'),
('MacBook', '{"color": "silver", "storage": 512, "touchbar": true}');

-- JSON 查询函数
SELECT name,
       JSON_EXTRACT(attrs, '$.color') AS color,           -- 取字段
       JSON_UNQUOTE(JSON_EXTRACT(attrs, '$.color')) AS color_unq,
       attrs->>'$.color' AS color_shorthand,             -- 简写
       JSON_EXTRACT(attrs, '$.tags[*]') AS all_tags,      -- 取数组
       attrs->'$.price' AS price
FROM products;

-- JSON 索引（8.0+）
ALTER TABLE products ADD INDEX idx_color ((CAST(attrs->>'$.color' AS CHAR(20))));
```

## 🎯 枚举与集合（谨慎使用）

```sql
CREATE TABLE orders (
  status ENUM('pending', 'paid', 'shipped', 'completed', 'cancelled'),
  tags SET('urgent', 'vip', 'fragile', 'gift')
);
```

**缺点：**
- 修改枚举值需要 ALTER TABLE（重写全表）
- 排序按定义顺序而非字母

**建议：** 优先用 `TINYINT` + 注释或查表方式。

## 📊 类型选择速查表

| 业务字段 | 推荐类型 | 说明 |
|---|---|---|
| 主键 ID | `BIGINT UNSIGNED AUTO_INCREMENT` | 范围最大 |
| 状态 (0-10) | `TINYINT UNSIGNED` | 节省 3 倍空间 |
| 状态 (0-100) | `SMALLINT UNSIGNED` | 节省 2 倍空间 |
| 年龄 | `TINYINT UNSIGNED` | 0-255 足够 |
| 价格 | `DECIMAL(10, 2)` | 避免浮点误差 |
| 名称 / 标题 | `VARCHAR(100-255)` | 按实际调整 |
| 描述 / 简介 | `VARCHAR(500)` 或 `TEXT` | 视长度定 |
| 文章正文 | `MEDIUMTEXT` | 最长 16MB |
| 手机号 | `CHAR(11)` | 定长 |
| 邮箱 | `VARCHAR(100)` | 变长 |
| 时间戳 | `DATETIME` | 推荐；TIMESTAMP 受 2038 年限制 |
| 布尔 | `TINYINT(1)` | 0=false, 1=true |
| IP 地址 | `INT UNSIGNED` + `INET_ATON()` | 比 VARCHAR 省 75% |
| 地理坐标 | `DECIMAL(10,7)` 或 `DOUBLE` | 视精度定 |
| UUID | `CHAR(32)` 或 `BINARY(16)` | 去掉 `-` 后 32 字符 |
| 扩展字段 | `JSON` | MySQL 5.7+ |

## ⚠️ 常见陷阱

### 1. 字符串排序的字符集问题

```sql
-- 不同字符集的 VARCHAR 比较结果可能不同
utf8mb4: VARCHAR(10) 最大 40 字节
utf8:    VARCHAR(10) 最大 30 字节
latin1: VARCHAR(10) 最大 10 字节
```

### 2. 隐式类型转换

```sql
-- ❌ WHERE 字段类型与值不匹配，导致索引失效
SELECT * FROM users WHERE phone = 13800138000;  -- phone 是 VARCHAR
-- 实际执行：CAST(phone AS SIGNED) = 13800138000

-- ✅ 保持类型一致
SELECT * FROM users WHERE phone = '13800138000';
```

### 3. INT 显示宽度已过时

```sql
-- ❌ MySQL 8.0 已废弃 INT(N) 中的 N
id INT(11) NOT NULL AUTO_INCREMENT,

-- ✅ 直接写 INT
id INT NOT NULL AUTO_INCREMENT,
```

## 🎯 总结

**设计原则：**
- ✅ 主键用 `BIGINT UNSIGNED`
- ✅ 状态用 `TINYINT`
- ✅ 金额用 `DECIMAL`
- ✅ 时间用 `DATETIME`
- ✅ 字符串按实际长度选 `VARCHAR(N)`
- ✅ 灵活扩展用 `JSON`
- ❌ 避免 `NULL`（设默认值）
- ❌ 避免过大字段（TEXT 慎用）

**下一步：** [🌐 字符集与排序规则](../01-foundation/charset) — 详解 utf8mb4 与 collation