---
title: Spark Core / RDD
date: 2026-08-15  # date-auto-injected
---
# Spark Core / RDD

## 1. Spark 架构

```
        Driver (driver program)
        - SparkContext / SparkSession
        - DAG 调度器
        - Task 调度

        Cluster Manager
        - YARN / Mesos / K8s / Standalone

        Executors (Worker)
        - 运行 Task
        - 内存 + 磁盘存储
```

## 2. RDD 核心概念

RDD（Resilient Distributed Dataset）= 不可变 + 分区 + 弹性 + 可并行。

```
五大属性：
  1. Partitions: 数据分片（并行度）
  2. Dependencies: 血统（lineage）
  3. Compute function: 计算函数
  4. Partitioner: 分区器（可选）
  5. PreferredLocations: 优先位置（HDFS block）
```

## 3. RDD 创建

```scala
// 1. parallelize (集合)
val rdd1 = sc.parallelize(1 to 1000)

// 2. textFile (HDFS / 本地)
val rdd2 = sc.textFile("hdfs:///data/file.txt")

// 3. Hadoop InputFormat
val rdd3 = sc.hadoopFile[Text, Text, TextInputFormat]("hdfs:///data")

// 4. transformation（懒执行）
val rdd4 = rdd2.flatMap(_.split(" ")).map((_, 1)).reduceByKey(_ + _)

// 5. PairRDD（key-value）
val pairs = rdd.map((_, 1))
```

## 4. 算子分类

### Transformation（懒）

```
map / filter / flatMap
mapValues / flatMapValues
groupByKey / reduceByKey
sortByKey
join / leftOuterJoin / cogroup
union / intersection / subtract
distinct
sample
coalesce / repartition
```

### Action（触发计算）

```
collect / count / first / take
reduce / fold / aggregate
countByKey / collectAsMap
saveAsTextFile / saveAsHadoopFile
foreach
```

## 5. RDD 持久化

```scala
// 缓存
rdd.persist(StorageLevel.MEMORY_AND_DISK)
val count1 = rdd.count()  // 触发计算 + 缓存
val count2 = rdd.count()  // 命中缓存

// 缓存级别
MEMORY_ONLY     // 仅内存（快，OOM 风险）
MEMORY_AND_DISK  // 内存 + 磁盘（推荐）
DISK_ONLY        // 仅磁盘
OFF_HEAP         // 堆外内存

// 释放
rdd.unpersist()
```

## 6. RDD 算子示例

```scala
// 词频统计
val textFile = sc.textFile("hdfs:///data/input")
val counts = textFile
  .flatMap(_.split(" "))
  .filter(_.nonEmpty)
  .map((_, 1))
  .reduceByKey(_ + _)
counts.saveAsTextFile("hdfs:///data/output")

// Top 10
val top10 = counts.sortBy(-_._2).take(10)
top10.foreach(println)

// join
val users = sc.parallelize(Seq(("u1", "Alice"), ("u2", "Bob")))
val orders = sc.parallelize(Seq(("u1", 100), ("u2", 200)))
val joined = users.join(orders)
// ((u1, (Alice, 100)), (u2, (Bob, 200)))
```

## 7. Shuffle 与宽依赖

| 类型 | 算子 | 影响 |
|------|------|------|
| **窄依赖** | map / filter / union | 不需 Shuffle，pipeline |
| **宽依赖** | groupByKey / join / sortByKey | 触发 Shuffle |

宽依赖是 Spark 性能瓶颈，**避免不必要的 Shuffle**。

## 8. RDD vs DataFrame vs Dataset

| | RDD | DataFrame | Dataset |
|--|-----|-----------|---------|
| 类型 | 通用对象 | Row | 强类型 |
| API | 函数式（RDD API） | SQL + DSL | 类型安全 + SQL |
| 性能 | 一般 | Catalyst 优化 | Catalyst 优化 |
| 适用 | 底层 / 复杂 | **首选（90%） | 强类型业务 |

**实践**：99% 用 DataFrame（Catalyst 自动优化），RDD 仅底层用。

## 9. Spark 性能调优

| 调优 | 描述 |
|------|------|
| `spark.sql.shuffle.partitions` | 200（默认），按数据量调 |
| `spark.sql.adaptive.enabled` | AQE 自适应执行（3.x） |
| `spark.executor.memory` | 4-8 GB |
| `spark.executor.cores` | 4-5 |
| `spark.memory.fraction` | 0.6（默认） |
| `spark.serializer` | KryoSerializer（比 Java 默认快 10 倍） |
| `spark.sql.adaptive.coalescePartitions.enabled` | 自动合并小 partition |

```python
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.shuffle.partitions", "200")
```

## 10. Spark 3.x 新特性

- AQE（Adaptive Query Execution）：运行时自适应
- Dynamic Coalesce：自动合并小 partition
- Dynamic Join Reorder：自动选择 join 策略
- Bloom Filter Join：减少大表 join 的 IO
- Pandas API on Spark：兼容 pandas
- Structured Streaming 改进

## 11. 实战例子

```python
# Word Count
text = spark.read.text("hdfs:///data/input")
counts = (
    text.selectExpr("split(value, ' ')[*] as word")
    .filter("word != ''")
    .groupBy("word").count()
    .orderBy("count", ascending=False)
)
counts.write.csv("hdfs:///data/output")

# Top 10
counts.limit(10).show()
```

## 12. 选型

| 场景 | 选 |
|------|-----|
| 离线 ETL | Spark SQL + DataFrame |
| 机器学习 | Spark MLlib + DataFrame |
| 图计算 | Spark GraphX（已不推荐，用 GraphFrames） |
| 实时流 | Spark Structured Streaming（弱于 Flink） |
| SQL 交互查询 | Spark SQL + Thrift Server |

## 🔗 下一步
- [Spark SQL / DataFrame](/04-spark/dataframe)
- [Spark Structured Streaming](/04-spark/streaming)
- [Spark 调优](/04-spark/tuning)

<!-- svg-injected:do-not-edit -->

## 图示：Spark Driver/Executor 与 RDD DAG

![Spark Driver/Executor 与 RDD DAG](/spark-architecture.svg)
