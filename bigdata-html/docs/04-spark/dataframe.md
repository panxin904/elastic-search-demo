---
title: Spark SQL / DataFrame
date: 2026-08-15  # date-auto-injected
---
# Spark SQL 与 DataFrame

## 1. DataFrame 核心

DataFrame = 分布式表格 + Schema（RDD + Schema）。

```
+---+---+---+---+      row 1
| a | b | c | d |      row 2
+---+---+---+---+      row 3
  schema: a:int, b:string, c:double, d:long
```

## 2. DataFrame 创建

```python
# 从 RDD
rdd = sc.parallelize([(1, "Alice"), (2, "Bob")])
df = rdd.toDF(["id", "name"])

# 从文件
df = spark.read.csv("hdfs:///data/users.csv", header=True, inferSchema=True)
df = spark.read.parquet("hdfs:///data/events/")
df = spark.read.json("hdfs:///data/logs/")

# 从 JDBC
df = spark.read.jdbc(url, "users", properties={"user": "alice"})

# 从内存
df = spark.createDataFrame([(1, "Alice"), (2, "Bob")], ["id", "name"])
```

## 3. DataFrame 操作

```python
# 查
df.show()
df.printSchema()
df.select("name", "age").filter(df.age > 18).show()

# 增删改
df.withColumn("new_col", df.age * 2).show()
df.drop("col").show()
df.withColumnRenamed("old", "new").show()
df.na.fill(0).show()
df.na.drop().show()

# 聚合
df.groupBy("city").agg(
  F.count("*").alias("cnt"),
  F.avg("age").alias("avg_age"),
  F.max("salary")
).show()

# 关联
df1.join(df2, "id", "inner")
df1.join(df2, df1.id == df2.user_id, "left")

# 窗口
from pyspark.sql.window import Window
w = Window.partitionBy("user").orderBy("ts")
df.withColumn("rank", F.row_number().over(w)).show()
```

## 4. Spark SQL

```sql
-- 注册临时视图
df.createOrReplaceTempView("users")
spark.sql("SELECT city, count(*) FROM users WHERE age > 18 GROUP BY city").show()

-- CTE
WITH active_users AS (
  SELECT id, name FROM users WHERE last_login > '2024-01-01'
)
SELECT city, count(*) FROM active_users JOIN ...

-- 窗口函数
SELECT
  user_id,
  ts,
  SUM(amount) OVER (PARTITION BY user_id ORDER BY ts) AS cumulative
FROM events;
```

## 5. Catalyst 优化器

Spark SQL 自动优化（无需手动）：

```
逻辑计划 → Catalyst 优化 → 物理计划
  - 谓词下推（Predicate Pushdown）
  - 列裁剪（Column Pruning）
  - 常量折叠（Constant Folding）
  - Join 重排（Join Reorder）
  - 表达式简化
```

效果：写简单 SQL，跑出优化执行计划。

## 6. 数据源

```python
spark.read.csv("hdfs:///data.csv", header=True, inferSchema=True)
spark.read.json("s3a://bucket/path/")
spark.read.parquet("hdfs:///data/events/")
spark.read.text("hdfs:///data/logs/")

# 写入
df.write.mode("overwrite").parquet("hdfs:///data/out/")
df.write.mode("append").csv("s3a://bucket/path/")
df.write.partitionBy("dt").mode("overwrite").saveAsTable("dwd.events")

# 格式
df.write.format("iceberg").mode("overwrite").save("hdfs:///data/iceberg/")
```

## 7. UDF / 窗口函数

```python
# UDF
from pyspark.sql.functions import udf
from pyspark.sql.types import IntegerType

def len_udf(s):
    return len(s) if s else 0

spark.udf.register("str_len", len_udf, IntegerType())
spark.sql("SELECT str_len(name) FROM users").show()

# 窗口
from pyspark.sql.window import Window
w = Window.partitionBy("category").orderBy("price")
df.withColumn("rank", F.row_number().over(w)).show()
```

## 8. 实战案例

### 案例 1：用户订单分析

```python
orders = spark.read.parquet("hdfs:///data/orders/")
users = spark.read.parquet("hdfs:///data/users/")

result = orders.join(users, "user_id")   .filter(F.col("status") == "completed")   .groupBy("city", "category")   .agg(F.count("*").alias("orders"),
       F.sum("amount").alias("gmv"))   .orderBy(F.desc("gmv"))

result.write.parquet("hdfs:///data/dws/city_category/")
```

### 案例 2：实时排行

```python
from pyspark.sql.window import Window
events = spark.readStream.parquet("hdfs:///data/events/")

# 每 5 分钟窗口 + Top 10
windowed = (
  events
  .groupBy(
    F.window("ts", "5 minutes"),
    "category"
  )
  .agg(F.count("*").alias("cnt"))
  .withColumn("rank", F.row_number().over(
    Window.partitionBy("window").orderBy(F.desc("cnt"))
  ))
  .filter("rank <= 10")
)
```

## 9. 实战调优

```python
# 1. 谓词下推
df.filter("dt = '2024-01-15'")  # 自动下推

# 2. 列裁剪
df.select("id", "name")  # 只读 2 列

# 3. 分区裁剪
df.filter(F.col("dt") == "2024-01-15")  # 跳过分区

# 4. Bucket / 分桶
df.write.bucketBy(10, "id").saveAsTable("t")

# 5. 缓存复用
df.persist(StorageLevel.MEMORY_AND_DISK)
df.count()
df.show()
df.unpersist()
```

## 10. 与其他引擎对比

| | Spark | Hive | Presto/Trino | ClickHouse |
|--|-------|------|---------------|-------------|
| 执行引擎 | DAG | MapReduce | MPP | 向量化 |
| 延迟 | 秒 | 分钟 | 秒-分 | 毫秒-秒 |
| 适合 | ETL/ML | 批 | Ad-hoc | OLAP |
| 优化 | Catalyst | Rule-based | Cost-based | 向量化 |

## 🔗 下一步
- [Spark Core / RDD](/04-spark/rdd)
- [Spark Structured Streaming](/04-spark/streaming)
- [Spark 调优](/04-spark/tuning)
