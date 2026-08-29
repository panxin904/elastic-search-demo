---
title: 常用函数与 CTE
date: 2026-08-15  # date-auto-injected
---

# 📚 常用函数与 CTE

> SQL 函数速查 + CTE（Common Table Expressions，公共表表达式）让复杂查询更优雅。

## 📊 聚合函数

```sql
-- 基础聚合
SELECT
  COUNT(*) AS total_count,           -- 总行数（含 NULL）
  COUNT(col) AS non_null_count,       -- 非 NULL 行数
  COUNT(DISTINCT col) AS unique_count, -- 不重复值数

  SUM(amount) AS total,
  AVG(amount) AS average,
  MAX(amount) AS maximum,
  MIN(amount) AS minimum,

  -- 统计聚合
  STDDEV(amount) AS std_dev,           -- 标准差
  VARIANCE(amount) AS variance,         -- 方差

  -- 分位数（8.0+）
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) AS median, -- 中位数
  PERCENTILE_DISC(0.5) WITHIN GROUP (ORDER BY amount) AS median_disc
FROM orders;
```

**GROUP_CONCAT：行转列神器**

```sql
-- 默认逗号分隔
SELECT user_id, GROUP_CONCAT(order_no) AS all_orders
FROM orders
GROUP BY user_id;

-- 自定义分隔符和排序
SELECT user_id,
  GROUP_CONCAT(
    DISTINCT order_no
    ORDER BY order_no DESC
    SEPARATOR ' | '
  ) AS all_orders
FROM orders
GROUP BY user_id;
```

## 📅 日期时间函数

```sql
-- 获取当前时间
SELECT NOW(), CURDATE(), CURTIME(), UTC_TIMESTAMP();

-- 提取部分
SELECT
  YEAR(NOW())        AS year,
  QUARTER(NOW())     AS quarter,
  MONTH(NOW())       AS month,
  WEEK(NOW())        AS week_of_year,
  DAY(NOW())         AS day,
  HOUR(NOW())        AS hour,
  MINUTE(NOW())      AS minute,
  SECOND(NOW())      AS second,
  DAYOFWEEK(NOW())   AS day_of_week,    -- 1=周日
  DAYOFYEAR(NOW())   AS day_of_year,
  WEEKDAY(NOW())     AS weekday_mon0;   -- 0=周一

-- 日期格式化
SELECT DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s');  -- 2025-07-18 14:30:00
SELECT DATE_FORMAT(NOW(), '%Y年%m月%d日');        -- 2025年07月18日

-- 字符串转日期
SELECT STR_TO_DATE('2025-07-18', '%Y-%m-%d');     -- 2025-07-18 00:00:00
SELECT STR_TO_DATE('18/07/2025', '%d/%m/%Y');     -- 2025-07-18 00:00:00

-- 日期加减
SELECT
  DATE_ADD(NOW(), INTERVAL 1 DAY)     AS tomorrow,
  DATE_ADD(NOW(), INTERVAL -1 MONTH)  AS last_month,
  DATE_SUB(NOW(), INTERVAL 1 HOUR)     AS last_hour,
  ADDDATE(NOW(), 7)                   AS next_week;

-- 日期差
SELECT
  DATEDIFF('2025-12-31', '2025-01-01')  AS days_diff,        -- 364
  TIMESTAMPDIFF(DAY, '2025-01-01', NOW()) AS days_since,    -- 198
  TIMESTAMPDIFF(MONTH, '2024-01-01', '2025-01-01') AS months;  -- 12

-- 日期截断
SELECT DATE_FORMAT(NOW(), '%Y-%m-01') AS month_start;
SELECT DATE_FORMAT(NOW(), '%Y-01-01') AS year_start;
SELECT LAST_DAY(NOW()) AS month_end;

-- Unix 时间戳
SELECT UNIX_TIMESTAMP();                    -- 当前时间戳
SELECT UNIX_TIMESTAMP('2025-01-01 12:00:00'); -- 1735713600
SELECT FROM_UNIXTIME(1735713600);            -- 转回时间
```

## 📝 字符串函数

```sql
-- 大小写
SELECT UPPER('hello'), LOWER('HELLO');

-- 截取
SELECT
  SUBSTRING('hello world', 1, 5),   -- 'hello' (从 1 开始)
  SUBSTRING('hello world', 7),       -- 'world' (到末尾)
  LEFT('hello', 3),                  -- 'hel'
  RIGHT('hello', 3),                 -- 'llo'

-- 拼接
SELECT CONCAT('a', '-', 'b');        -- 'a-b'
SELECT CONCAT_WS('-', 'a', 'b', 'c'); -- 'a-b-c' (带分隔符)

-- 长度
SELECT
  CHAR_LENGTH('你好'),               -- 2（字符数）
  LENGTH('你好'),                     -- 6（字节数，utf8mb4 = 3字节/字）

-- 查找替换
SELECT
  LOCATE('world', 'hello world'),     -- 7（位置，从 1 开始）
  REPLACE('hello', 'l', 'L'),         -- 'heLLo'
  REVERSE('hello');                    -- 'olleh'

-- 去除空格
SELECT
  TRIM('  hello  '),                  -- 'hello'
  LTRIM('  hello'),                    -- 'hello  '
  RTRIM('hello  ');                    -- '  hello'

-- 填充
SELECT
  LPAD('1', 3, '0'),                  -- '001'
  RPAD('1', 3, '0'),                  -- '100'

-- 重复
SELECT REPEAT('ab', 3);               -- 'ababab'

-- 反引号转义（防 SQL 注入）
SELECT QUOTE('hello');                 -- 'hello'
```

## 🔢 数学函数

```sql
-- 基本
SELECT
  ABS(-5),              -- 5
  CEIL(1.2),            -- 2
  CEILING(1.2),         -- 2（同 CEIL）
  FLOOR(1.8),           -- 1
  ROUND(1.456, 2),      -- 1.46
  TRUNCATE(1.456, 2),   -- 1.45（截断，不四舍五入）
  MOD(10, 3),           -- 1（取模）
  10 % 3;                -- 1

-- 幂、对数
SELECT
  POW(2, 10),           -- 1024
  POWER(2, 10),         -- 1024
  SQRT(16),              -- 4
  LOG(100),              -- 自然对数
  LOG10(100);            -- 以 10 为底

-- 三角函数
SELECT SIN(0), COS(0), TAN(0);  -- 0, 1, 0
SELECT PI();                     -- 3.141593

-- 随机
SELECT RAND();                    -- 0-1 之间的随机数
SELECT FLOOR(RAND() * 100);       -- 0-99 之间的整数

-- 符号
SELECT SIGN(-5), SIGN(0), SIGN(5);  -- -1, 0, 1
```

## 🔄 类型转换函数

```sql
-- CAST
SELECT CAST('123' AS SIGNED);       -- 123
SELECT CAST('2025-01-01' AS DATE); -- 2025-01-01
SELECT CAST(123.45 AS CHAR);       -- '123.45'

-- CONVERT
SELECT CONVERT('123', SIGNED);
SELECT CONVERT('abc' USING utf8mb4); -- 转换字符集

-- 实用场景
-- ❌ 字符串数字比较（索引失效）
SELECT * FROM t WHERE phone = 13800138000;
-- ✅ 转字符串
SELECT * FROM t WHERE phone = CAST(13800138000 AS CHAR);
```

## ❓ 条件函数

```sql
-- IF
SELECT IF(score >= 60, '及格', '不及格') FROM exam;

-- IFNULL / COALESCE
SELECT IFNULL(NULL, 'default');          -- 'default'
SELECT COALESCE(NULL, NULL, 'first');   -- 'first'

-- CASE WHEN
SELECT
  id,
  CASE
    WHEN score >= 90 THEN 'A'
    WHEN score >= 80 THEN 'B'
    WHEN score >= 60 THEN 'C'
    ELSE 'D'
  END AS grade
FROM exam;

-- 简化版：CASE value WHEN
SELECT
  CASE status
    WHEN 1 THEN '正常'
    WHEN 0 THEN '禁用'
    ELSE '未知'
  END AS status_text
FROM users;
```

## 🌳 CTE（公共表表达式）

### 基础 CTE

```sql
-- 普通 CTE：用 WITH 声明临时结果集
WITH
  active_users AS (
    SELECT id, name FROM users WHERE status = 1
  ),
  recent_orders AS (
    SELECT * FROM orders WHERE created_at >= '2025-01-01'
  )
SELECT
  au.name,
  COUNT(ro.id) AS order_count
FROM active_users au
LEFT JOIN recent_orders ro ON au.id = ro.user_id
GROUP BY au.id, au.name;

-- 等价于子查询（但更清晰）
SELECT
  au.name,
  COUNT(ro.id) AS order_count
FROM (SELECT id, name FROM users WHERE status = 1) au
LEFT JOIN (SELECT * FROM orders WHERE created_at >= '2025-01-01') ro
  ON au.id = ro.user_id
GROUP BY au.id, au.name;
```

### CTE 链式引用

```sql
WITH
  -- 第 1 步：每用户的总消费
  user_totals AS (
    SELECT user_id, SUM(amount) AS total
    FROM orders
    WHERE created_at >= '2025-01-01'
    GROUP BY user_id
  ),
  -- 第 2 步：消费超过 1000 的高价值用户
  vip_users AS (
    SELECT user_id FROM user_totals WHERE total > 1000
  ),
  -- 第 3 步：高价值用户最近的订单
  vip_orders AS (
    SELECT o.*
    FROM orders o
    INNER JOIN vip_users v ON o.user_id = v.user_id
    WHERE o.created_at >= '2025-06-01'
  )
SELECT * FROM vip_orders;
```

### 递归 CTE

```sql
-- 递归查询：查组织架构的所有下属
WITH RECURSIVE org_tree AS (
  -- 基础情况：CEO（没有上级）
  SELECT id, name, manager_id, 1 AS level, CAST(name AS CHAR(500)) AS path
  FROM employees
  WHERE manager_id IS NULL
  
  UNION ALL
  
  -- 递归情况：每个员工的下属
  SELECT e.id, e.name, e.manager_id, t.level + 1,
         CONCAT(t.path, ' > ', e.name)
  FROM employees e
  INNER JOIN org_tree t ON e.manager_id = t.id
  WHERE t.level < 10  -- 防止无限递归
)
SELECT * FROM org_tree ORDER BY path;

-- 应用：递归生成数字序列
WITH RECURSIVE nums AS (
  SELECT 1 AS n
  UNION ALL
  SELECT n + 1 FROM nums WHERE n < 100
)
SELECT * FROM nums;

-- 应用：递归查分类树（含所有层级）
WITH RECURSIVE category_tree AS (
  SELECT id, name, parent_id, 0 AS depth
  FROM categories
  WHERE parent_id IS NULL
  
  UNION ALL
  
  SELECT c.id, c.name, c.parent_id, ct.depth + 1
  FROM categories c
  INNER JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT * FROM category_tree ORDER BY depth, name;
```

## 📋 JSON 函数（MySQL 5.7+）

```sql
-- 提取
SELECT
  JSON_EXTRACT(attrs, '$.name') AS name,
  attrs->>'$.name' AS name_shorthand,        -- 等价于 JSON_UNQUOTE(JSON_EXTRACT(...))
  JSON_EXTRACT(attrs, '$.tags[0]') AS first_tag,
  JSON_EXTRACT(attrs, '$.spec.color') AS color;

-- 修改
SELECT
  JSON_SET(attrs, '$.price', 100, '$.stock', 50),  -- 设置或新增
  JSON_INSERT(attrs, '$.new_field', 'x'),          -- 仅新增
  JSON_REPLACE(attrs, '$.price', 200),            -- 仅替换已有
  JSON_REMOVE(attrs, '$.obsolete'),                -- 删除字段
  JSON_ARRAY(1, 2, 'x'),                          -- 创建数组
  JSON_OBJECT('key', 'value');                     -- 创建对象

-- 查询
SELECT
  JSON_CONTAINS(attrs, '"red"', '$.color'),        -- 是否包含
  JSON_LENGTH(attrs, '$.tags'),                    -- 数组长度
  JSON_KEYS(attrs),                                 -- 所有键
  JSON_TYPE(JSON_EXTRACT(attrs, '$.age'));         -- 类型

-- 创建索引（8.0+）
ALTER TABLE products ADD INDEX idx_color ((CAST(attrs->>'$.color' AS CHAR(20))));
```

## 🎯 函数性能注意事项

```sql
-- ❌ 在 WHERE 中对字段使用函数（破坏索引）
SELECT * FROM users WHERE DATE(created_at) = '2025-01-01';
SELECT * FROM users WHERE UPPER(name) = 'ZHANGSAN';

-- ✅ 改写
SELECT * FROM users
WHERE created_at >= '2025-01-01' AND created_at < '2025-01-02';

-- 对于 UPPER，可以创建函数索引（8.0+）
CREATE INDEX idx_upper_name ON users((UPPER(name)));
```

## 🎯 总结

**常用函数：**
- 聚合：COUNT / SUM / AVG / GROUP_CONCAT
- 日期：DATE_FORMAT / DATE_ADD / DATEDIFF / UNIX_TIMESTAMP
- 字符串：CONCAT / SUBSTRING / REPLACE / GROUP_CONCAT
- 数学：ROUND / FLOOR / CEIL / RAND
- JSON：JSON_EXTRACT / JSON_SET / ->>

**CTE 优势：**
- ✅ 复杂查询更清晰
- ✅ 可链式引用（前一个 CTE 作为输入）
- ✅ 递归 CTE 处理树状数据
- ✅ 替代子查询，提升可读性

**下一步：** [⚖️ ACID 与隔离级别](../04-transaction/isolation) — 理解事务的本质


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
