---
title: Hive 优化
date: 2026-08-15  # date-auto-injected
---
# Hive 性能优化

## 1. 优化金字塔

```
        ┌─ 表设计（分区 / 分桶 / 格式）
     ┌─┴─┐
   ┌─┴─┐ └─ SQL 改写（谓词下推 / 列裁剪）
 ┌─┴─┐ └─ 配置调优（内存 / 并行）
 ┌─┴─┐ └─ 执行引擎（Tez / Spark / LLAP）
```

## 2. 表设计

### 分区（Partition）

```sql
CREATE TABLE orders (
  id BIGINT,
  user_id BIGINT,
  amount DECIMAL(10,2),
  created_at TIMESTAMP
) PARTITIONED BY (dt STRING)
STORED AS PARQUET;

-- 分区裁剪（关键）
SELECT * FROM orders WHERE dt = '2024-01-15';  -- 只读一个分区
```

**规则**：
- 高频过滤字段（时间 / 地域）
- 分区大小 1-10 GB
- 分区数 < 10000（避免小文件）

### 分桶（Bucket / Clustered）

```sql
-- 分桶（join 优化）
CREATE TABLE orders_bucketed (
  id BIGINT,
  user_id BIGINT,
  amount DECIMAL(10,2)
) CLUSTERED BY (user_id) INTO 32 BUCKETS;

-- 分桶表 join 优化（避免 shuffle）
SELECT /*+ MAPJOIN(o) */ *
FROM orders_bucketed o JOIN users_bucketed u
  ON o.user_id = u.id;
```

### 存储格式

| 格式 | 压缩比 | 列裁剪 | 谓词下推 |
|------|--------|--------|----------|
| TextFile | 无 | 无 | 无 |
| SequenceFile | 中 | 无 | 无 |
| RCFile | 中 | 有 | 有 |
| ORC | 高 | 有 | 有（推荐） |
| Parquet | 高 | 有 | 有（推荐） |

**推荐 ORC / Parquet**（列式 + 压缩 + 谓词下推）。

## 3. SQL 改写优化

```sql
-- 1. 谓词下推（最常用）
SET hive.optimize.ppd=true;
SELECT * FROM orders WHERE dt = '2024-01-15' AND user_id = 123;
-- 自动推到 Parquet row group 列扫描

-- 2. 列裁剪
SELECT id, amount FROM orders;  -- 只读 2 列

-- 3. 避免 SELECT *
SELECT user_id, sum(amount) FROM orders GROUP BY user_id;

-- 4. Map Join（小表）
SET hive.auto.convert.join=true;
SELECT /*+ MAPJOIN(small) */ * FROM big JOIN small ON ...;
-- 小表 < 25 MB 自动广播

-- 5. 谓词下推到分区
WHERE dt BETWEEN '2024-01-01' AND '2024-01-31'  -- 31 个分区

-- 6. 避免全表 count(*)
SELECT count(*) FROM orders WHERE dt = '2024-01-15';  -- 分区裁剪
```

## 4. 统计信息

```sql
-- 1. 收集列统计
ANALYZE TABLE orders COMPUTE STATISTICS FOR COLUMNS user_id, dt;

-- 2. 收集表统计
ANALYZE TABLE orders COMPUTE STATISTICS;

-- 3. 自动收集
SET hive.stats.autogather=true;
SET hive.stats.column.autogather=true;
```

## 5. 关键参数

```sql
-- 执行引擎
SET hive.execution.engine=tez;
-- 或 spark

-- 内存
SET hive.tez.container.size=8192;  -- 8 GB
SET hive.tez.java.opts=-Xmx6g;

-- 并行
SET hive.exec.parallel=true;
SET hive.exec.reducers.bytes.per.reducer=67108864;  -- 64MB per reducer

-- CBO
SET hive.cbo.enable=true;
SET hive.compute.query.using.stats=true;

-- 谓词下推
SET hive.optimize.ppd=true;
SET hive.optimize.ppd.storage=true;

-- 向量化
SET hive.vectorized.execution.enabled=true;
SET hive.vectorized.execution.reduce.enabled=true;

-- 小表 join
SET hive.auto.convert.join=true;
SET hive.auto.convert.join.noconditionaltask.size=20000;
```

## 6. 实战调优案例

### 案例 1：慢查询

```
原始：SELECT * FROM orders WHERE user_id = 123 AND dt BETWEEN '2024-01-01' AND '2024-01-31';
耗时：30 分钟

优化：
  1. 添加 PARTITION (dt) → 分区裁剪 → 30 天数据
  2. ORC 格式 + SNAPPY 压缩 → 减少 IO
  3. 列裁剪：只读 5 列
  4. Map Join 关联小表
耗时：5 秒
```

### 案例 2：数据倾斜

```
现象：GROUP BY user_id → 1 个 reducer 处理 50% 数据 → 30 分钟

优化：
  1. SET hive.groupby.skewindata=true;  -- 自动处理倾斜
  2. 加盐：打散到多个 reducer 再合并
  3. 启用 CBO：自动选择 join 策略
```

## 7. 实战 checklist

- [ ] 表用 ORC / Parquet + Snappy
- [ ] 分区按 dt 每天
- [ ] 大表分桶（user_id 32 buckets）
- [ ] 启用 CBO
- [ ] 启用谓词下推
- [ ] 启用向量化执行
- [ ] 启用 Map Join
- [ ] 定期 ANALYZE TABLE 收集统计

## 8. 监控

```
HiveServer2 JVM 堆 / GC
MetaStore 慢查询
LLAP daemon 数量
Tez / Spark 任务并发度
磁盘 IO
网络 IO
```

## 🔗 下一步
- [Hive 架构](/06-hive/architecture)
- [Hive on Spark / Tez](/06-hive/engine)
- [数据湖 三剑客](/10-data-lake/three-pillars)
