---
title: ClickHouse 独有函数
description: ClickHouse 独有 + 高频函数全集：array / map / tuple / JSON / URL / 时间 / 字符串
---

# ClickHouse 独有函数

ClickHouse 有大量「独有」函数，特别是数组、Map、JSON、URL、时间、地理位置、机器学习相关函数。

## 数组函数

```sql
-- 基础
SELECT
  arrayConcat([1,2], [3,4]),           -- [1,2,3,4]
  arrayElement([1,2,3], 1),            -- 2（索引从 1 开始！）
  arrayPushBack([1,2], 3),             -- [1,2,3]
  arrayPushFront([1,2], 0),            -- [0,1,2]
  arraySlice([1,2,3,4], 2, 2),         -- [2,3]
  arrayReverse([1,2,3]),               -- [3,2,1]
  arraySort([3,1,2]),                  -- [1,2,3]
  arrayDistinct([1,1,2,3])             -- [1,2,3]

-- 聚合
SELECT
  arrayReduce('sum', [1,2,3]),         -- 6
  arrayReduce('avg', [1,2,3]),         -- 2
  arrayReduce('max', [1,2,3])          -- 3

-- 过滤
SELECT
  arrayFilter(x -> x > 1, [1,2,3]),    -- [2,3]
  arrayMap(x -> x * 2, [1,2,3]),       -- [2,4,6]
  arrayExists(x -> x > 2, [1,2,3])     -- 1（存在）

-- 查询
SELECT
  has([1,2,3], 2),                    -- 1（包含）
  has([1,2,3], 5),                    -- 0
  indexOf([1,2,3], 2),                 -- 2
  arrayContains([1,2,3], 2)            -- true
```

## Map 函数

```sql
SELECT
  map('a', 1, 'b', 2, 'c', 3),         -- {'a':1,'b':2,'c':3}
  mapKeys({'a':1,'b':2}),              -- ['a','b']
  mapValues({'a':1,'b':2})             -- [1,2]

-- 嵌套类型转换
SELECT CAST([1,2,3], 'Array(UInt8)') AS arr
```

## JSON 函数

```sql
-- 解析 JSON 字符串
SELECT
  JSONExtractString('{"name": "Alice"}', 'name'),  -- 'Alice'
  JSONExtractInt('{"age": 25}', 'age'),            -- 25
  JSONExtractFloat('{"score": 9.5}', 'score'),     -- 9.5
  JSONExtractBool('{"active": true}', 'active'),   -- 1
  JSONExtractArrayRaw('{"tags": ["a","b"]}', 'tags')  -- '["a","b"]'

-- 类型安全的提取
SELECT JSONExtract('{"name": "Alice", "age": 25}', 'Tuple(name String, age UInt8)')
```

## URL 函数

ClickHouse 内置 URL 解析函数（无需正则）：

```sql
SELECT
  protocol('https://example.com/path?q=1'),  -- 'https'
  domain('https://example.com/path'),         -- 'example.com'
  domainWithoutWWW('https://www.example.com'),-- 'example.com'
  topLevelDomain('https://example.com'),      -- 'com'
  path('https://example.com/path/to'),        -- '/path/to'
  pathFull('https://example.com/path?q=1'),   -- '/path?q=1'
  queryStringAndFragment('https://example.com/path?q=1#h'),  -- 'q=1#h'
  extractURLParameters('https://example.com/?a=1&b=2')['a']  -- '1'
```

## 时间函数

```sql
SELECT
  toYear(now()),                       -- 2024
  toMonth(now()),                      -- 1
  toDayOfMonth(now()),
  toHour(now()),
  toMinute(now()),
  toSecond(now()),

  toDate('2024-01-01 12:00:00'),
  toDateTime('2024-01-01 12:00:00'),
  toDateTime64('2024-01-01 12:00:00.123', 3),  -- 毫秒精度
  toUnixTimestamp(now()),

  formatDateTime(now(), '%Y-%m-%d %H:%M:%S'),
  parseDateTimeBestEffort('2024-01-01')

-- 时间窗口
SELECT
  toStartOfInterval(now(), INTERVAL 5 MINUTE),  -- 5 分钟窗口
  toStartOfHour(now()),
  toStartOfDay(now()),
  toStartOfWeek(now()),
  toStartOfMonth(now())
```

## 字符串函数

```sql
SELECT
  length('hello'),                     -- 5
  lower('HELLO'),                      -- 'hello'
  upper('hello'),                      -- 'HELLO'
  trim('  hello  '),                   -- 'hello'
  replace('hello world', 'world', 'CK'),  -- 'hello CK'
  extract('hello123world', '([0-9]+)'), -- '123'
  match('hello123', '[0-9]+'),         -- 1
  splitByChar(',', 'a,b,c'),           -- ['a','b','c']
  splitByRegex('\\s+', 'a b  c')       -- ['a','b','c']
```

## 地理位置函数

ClickHouse 支持 Geo 数据类型（点/多边形）：

```sql
-- 距离计算（地球半径 6371000 米）
SELECT
  geoDistance(116.4, 39.9, 121.5, 31.2),  -- 上海到北京约 1067 km
  greatCircleDistance(116.4, 39.9, 121.5, 31.2, 6371000)

-- 点是否在多边形内
SELECT pointInPolygon((39.9, 116.4), [(39.0, 115.0), (40.0, 115.0), (40.0, 117.0), (39.0, 117.0)])
```

## Hash 函数

```sql
SELECT
  cityHash64('hello'),                 -- 13253124476785557978
  murmurHash3_64('hello'),             -- 4236618289605128574
  farmHash64('hello'),                 -- 5527709461249098091
  xxHash64('hello'),                   -- 0xbea37d5e（如需可逆不推荐）
  MD5('hello'),                        -- '5d41402abc4b2a76b9719d911017c592'
  halfMD5('hello')                     -- MD5 前 8 字节
```

## UUID 函数

```sql
SELECT
  generateUUIDv4(),                    -- 随机 UUID
  UUIDNumToString(toUUIDOrNull('12345678-1234-1234-1234-123456789012'))
```

## 条件函数

```sql
-- 多分支
SELECT
  multiIf(x > 100, 'high', x > 50, 'mid', 'low'),
  if(x > 0, 'positive', 'non-positive'),

-- 异常处理
SELECT
  ifNull(x, 0),                        -- x 为 NULL 时返回 0
  ifNotFinite(x, 0),                   -- 浮点 NaN/Inf 时返回 0
  coalesce(x, y, z, 0),                -- 第一个非 NULL 值

-- 类型转换
SELECT
  toString(123),
  toInt64('123'),
  toFloat64('1.23'),
  toDate('2024-01-01'),
  CAST(x AS String)
```

## 窗口函数与 CTE

详见 [window-functions.md](./window-functions.md)。

## Lambda 函数

```sql
-- 数组映射
SELECT arrayMap(x -> x * 2, [1,2,3])   -- [2,4,6]

-- 数组过滤
SELECT arrayFilter(x -> x > 1, [1,2,3]) -- [2,3]

-- 多参数
SELECT arrayMap((x, y) -> x + y, [1,2,3], [10,20,30])  -- [11,22,33]

-- 聚合
SELECT arrayReduce((acc, x) -> acc + x, [1,2,3], 0)  -- 6
```

## 函数使用建议

| 场景 | 推荐函数 |
|---|---|
| 文本日志解析 | `extract`、`match`、`splitByRegex` |
| 时间字段处理 | `toStartOfInterval`、`toDateTime64` |
| 数组去重 | `arrayDistinct`、`groupUniqArray` |
| JSON 字段提取 | `JSONExtract` 家族 |
| URL 解析 | `protocol`、`domain`、`path` |
| 用户唯一标识 | `cityHash64` 或 `generateUUIDv4()` |
| 距离计算 | `geoDistance`、`greatCircleDistance` |
| 性能优化 | `LowCardinality`、`prewhere`、`SAMPLE` |

## 下一步

- 学习窗口函数：见 [window-functions.md](./window-functions.md)
- 学习聚合查询：见 [select-aggregate.md](./select-aggregate.md)
