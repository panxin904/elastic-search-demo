---
title: SQL 实战总览
---

# ClickHouse SQL 实战

**ClickHouse SQL = 标准 SQL + 向量化扩展**——MySQL/PG 工程师 30 分钟上手。

## 一句话总结

> **ClickHouse SQL ≈ SQL92 + 数组/map/JSON 复杂类型 + 强类型聚合 + Lambda 函数**。**与 MySQL 90% 兼容，10% 差异需注意**。

---

## 一、ClickHouse vs MySQL vs PG 语法差异

| 维度 | MySQL | PostgreSQL | ClickHouse |
|---|---|---|---|
| **类型** | 基础 | 丰富（JSONB / array） | 极丰富（Array / Map / Tuple / Enum / Decimal 76 位）|
| **JOIN 算法** | NL / Hash | Hash / Merge | Hash / Parallel Hash / 直接 |
| **子查询** | 不优化 | 优化 | **必须显式 JOIN**（`select subquery` 报错）|
| **UPDATE / DELETE** | 完整 | 完整 | **ALTER TABLE ... UPDATE/DELETE**（极慢，重写 part）|
| **事务** | 完整 | 完整 | **单 insert 原子，跨 insert 无事务** |
| **窗口函数** | 8.0+ | 完整 | **FROM 子句必须先有窗口定义**（不同 PG）|
| **函数命名** | 大写小写都行 | 小写 | 任意 |
| **LIMIT** | 末尾 | 末尾 | 末尾 + `LIMIT n BY` 高级 |

## 二、SELECT 语法

```sql
SELECT
    -- 字段
    user_id,
    -- 数组下标（PG 无）
    events[1] AS first_event,
    -- 嵌套字段
    profile.country,
    -- Lambda 函数
    arrayMap(x -> x * 2, [1, 2, 3]) AS doubled,
    -- 强类型转换
    toInt32(amount) AS amt
FROM events
WHERE date >= '2026-01-01'
  AND event_type IN ('click', 'view')
  -- 数组包含
  AND has(tags, 'mobile')
GROUP BY user_id, profile.country
HAVING count() > 10
ORDER BY count() DESC
LIMIT 100
```

## 三、聚合函数 TOP 20

```sql
-- 计数
count(), countDistinct(), uniq(), uniqExact(), uniqHLL12()

-- 数值
sum(), avg(), min(), max(), median(), quantile(0.95)(), quantiles(0.5, 0.9, 0.99)()

-- 数组
groupArray(x), groupUniqArray(x), arrayConcat(groupArray(x))

-- 字符串
groupConcat(x, ','), groupConcatDistinct(x, ',')

-- 状态聚合（与 AggregatingMergeTree 配合）
sumState(x), sumMerge(x), avgState(x), avgMerge(x)
uniqState(x), uniqMerge(x)

-- 参数化聚合
quantileState(0.95)(x), quantileMerge(x)
```

## 四、JOIN 类型

```sql
-- 1. INNER JOIN
SELECT *
FROM events AS e
INNER JOIN users AS u ON e.user_id = u.id

-- 2. LEFT JOIN（ClickHouse 必须显式 RIGHT 或 LEFT，不能简写）
SELECT *
FROM events AS e
LEFT JOIN users AS u ON e.user_id = u.id

-- 3. JOIN 多表
SELECT *
FROM events e
LEFT JOIN users u ON e.user_id = u.id
LEFT JOIN pages p ON e.page_id = p.id

-- 4. ASOF JOIN（ClickHouse 特色，模糊最近匹配）
-- 用于：股价/订单与报价的最近时间匹配
SELECT *
FROM trades t
ASOF JOIN quotes q ON t.symbol = q.symbol
                AND t.time >= q.time
```

## 五、窗口函数

```sql
-- 必须 FROM 子句先有窗口
SELECT
    user_id,
    event_time,
    amount,
    -- 累计求和
    sum(amount) OVER (PARTITION BY user_id ORDER BY event_time) AS running_total,
    -- 排名
    row_number() OVER (PARTITION BY user_id ORDER BY event_time) AS rn,
    -- 上一行
    lagInFrame(amount) OVER (PARTITION BY user_id ORDER BY event_time) AS prev_amount
FROM events
```

**与 PG 差异**：
- `OVER (PARTITION BY ...)` 必须配合 `ORDER BY`
- 函数名带 `InFrame` 后缀（`lagInFrame` 而非 `lag`）

## 六、JSON 处理

```sql
-- 1. JSON 字段（ClickHouse 24.x+）
CREATE TABLE events (
    id UInt64,
    data JSON
) ENGINE = MergeTree ORDER BY id;

-- 2. 插入
INSERT INTO events VALUES
(1, '{"user": "alice", "amount": 100, "tags": ["a", "b"]}'),
(2, '{"user": "bob", "amount": 200}');

-- 3. 查询
SELECT
    data.user AS user,           -- 字符串
    data.amount AS amount,        -- 数值
    data.tags[1] AS first_tag,    -- 数组下标
    data.optional::Nullable(Int32) AS opt
FROM events;

-- 4. JSON 函数
SELECT JSONExtractString(data, 'user') FROM events;
SELECT JSONExtractInt(data, 'amount') FROM events;
SELECT JSONExtractKeys(data) FROM events;
```

## 七、数组 / Map / Tuple

```sql
-- 数组
SELECT [1, 2, 3] AS arr;
SELECT arrayMap(x -> x * 2, [1, 2, 3]);  -- [2, 4, 6]
SELECT arrayFilter(x -> x > 1, [1, 2, 3]);  -- [2, 3]
SELECT arrayJoin([1, 2, 3]) AS x;  -- 展开为 3 行

-- Map
SELECT CAST((['a', 'b'], [1, 2]), 'Map(String, UInt8)') AS m;
-- {'a':1, 'b':2}
SELECT m['a'] FROM (SELECT CAST(...) AS m);

-- Tuple
SELECT tuple(1, 'a', [1, 2]) AS t;
-- (1, 'a', [1, 2])
SELECT t.1, t.2, t.3 FROM (SELECT tuple(1, 'a', [1, 2]) AS t);
```

## 八、子查询与 CTE

```sql
-- CTE（推荐）
WITH
    active_users AS (
        SELECT user_id
        FROM events
        WHERE event_type = 'login'
          AND date >= '2026-01-01'
        GROUP BY user_id
        HAVING count() > 5
    ),
    total_per_user AS (
        SELECT user_id, sum(amount) AS total
        FROM events
        WHERE user_id IN (SELECT user_id FROM active_users)
        GROUP BY user_id
    )
SELECT * FROM total_per_user WHERE total > 1000;
```

**注意**：ClickHouse 不支持不相关子查询（`SELECT (SELECT ...)` 必须相关）。

## 九、查询优化技巧

```sql
-- 1. 用 PREWHERE 提前过滤
SELECT count()
FROM events
PREWHERE date = '2026-08-01'  -- 提前过滤，先于主 WHERE
WHERE event_type = 'click';

-- 2. SAMPLE 抽样
SELECT count() FROM events SAMPLE 0.1;  -- 10% 抽样

-- 3. FINAL 强制去重（ReplacingMergeTree）
SELECT * FROM events FINAL WHERE user_id = 1;

-- 4. 用近似聚合
SELECT uniqHLL12(user_id) FROM events;  -- 比 uniqExact 快 10x

-- 5. 避免 SELECT *
SELECT user_id, sum(amount) FROM events GROUP BY user_id;
```

## 十、ClickHouse 独有函数 TOP 20

```sql
-- URL
URLHierarchy('https://example.com/a/b/c')
extractURLParameter(url, 'utm_source')

-- 数组
arrayJoin(), arrayMap(), arrayFilter(), arrayReduce()
arrayConcat(), arrayDistinct(), arraySort(), arrayReverse()

-- 字符串
extractAll(text, 'pattern')
splitByChar(',', str)
replaceOne(haystack, pattern, replacement)

-- 类型转换
toInt32OrZero(str), toFloat64OrNull(str)
accurateCast(value, 'UInt64')

-- 时间
toStartOfInterval(date, INTERVAL 1 minute)
dateDiff('minute', start, end)
formatDateTime(date, '%Y-%m-%d %H:%M:%S')

-- Hash
cityHash64(str), murmurHash3_64(str)
URLHash(url)

-- UUID
generateUUIDv4()
toUUID(str)
```

## 关联章节

- **02-sql/select-aggregate**：SELECT 与聚合
- **02-sql/functions**：函数速查
- **03-table-engine/overview**：表引擎
- **04-olap-scenarios/overview**：实战

## 一句话总结

> **ClickHouse SQL = 标准 SQL + 强类型 + 复杂类型 + 状态聚合**。**MySQL/PG 工程师 30 分钟上手**。


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
