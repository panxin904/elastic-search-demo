---
title: Spark 调优
date: 2026-08-15  # date-auto-injected
---
# Spark 性能调优

## 1. 调优金字塔

```
        ┌─ 数据倾斜
     ┌─┴─┐
   ┌─┴─┐ └─ 序列化 / 压缩
 ┌─┴─┐ └─ 内存 / GC
 ┌─┴─┐ └─ shuffle / 分区
 ┌─┴─┐ └─ 配置
```

## 2. 配置调优

```python
spark = SparkSession.builder   .appName("MyApp")   .config("spark.executor.memory", "8g")   .config("spark.executor.cores", "4")   .config("spark.sql.shuffle.partitions", "200")   .config("spark.sql.adaptive.enabled", "true")   .getOrCreate()
```

## 3. 内存调优

```
Executor 内存划分（默认 8g）：
  - 60% Execution (task 计算)
  - 20% Storage (cache)
  - 20% Reserved (对象创建等)

调优：
  spark.memory.fraction = 0.6     # Execution 比例
  spark.memory.storageFraction = 0.5  # Storage 占 Execution 比例
```

## 4. 序列化与压缩

```python
spark.conf.set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
spark.conf.set("spark.kryo.registrationRequired", "true")
spark.conf.registerKryoClasses([MyClass1, MyClass2])

# 压缩（Shuffle 中间数据）
spark.conf.set("spark.sql.shuffle.spill.numElementsForceSpillThreshold", "2000")
```

## 5. Shuffle 调优

```python
# 1. 分区数
spark.conf.set("spark.sql.shuffle.partitions", "200")
# 经验：分区数 = 总数据量 / 200MB

# 2. AQE（Spark 3.x 自适应）
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")

# 3. Broadcast Join（小表 < 10MB）
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", 10485760)
```

## 6. 数据倾斜

### 现象
- 个别 Task 极慢，整体被拖
- Stage 长时间不结束

### 解决

```python
# 1. 加盐（打散 key）
df.withColumn("salted_key", F.concat(F.col("key"), F.lit(F.rand() * 100).cast("int")))   .groupBy("salted_key").agg(F.sum("value"))   .groupBy(F.split("salted_key", "_")[0]).agg(F.sum("value"))

# 2. Broadcast Join（小表）
df_large.join(F.broadcast(df_small), "key")

# 3. 自定义 Partitioner
def my_partitioner(key):
  return hash(key) % num_partitions

# 4. 过滤异常 key
df.filter("key != 'HOT_KEY'").union(hot_key_df)
```

## 7. 内存 / GC 调优

```python
# GC 选择（G1 默认）
spark.conf.set("spark.executor.extraJavaOptions", "-XX:+UseG1GC -XX:MaxGCPauseMillis=200")

# 大堆 + G1GC
spark.conf.set("spark.executor.memory", "16g")
spark.conf.set("spark.executor.memoryOverhead", "4g")  # 堆外

# Kryo 序列化（减少内存）
spark.conf.set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
```

## 8. Executor 调优

```python
# 1. CPU 和内存
spark.conf.set("spark.executor.cores", 4)        # 每 executor 4 核
spark.conf.set("spark.executor.memory", "8g")   # 每 executor 8g

# 2. 动态分配（推荐）
spark.conf.set("spark.dynamicAllocation.enabled", "true")
spark.conf.set("spark.dynamicAllocation.minExecutors", "2")
spark.conf.set("spark.dynamicAllocation.maxExecutors", "100")

# 3. K8s / YARN
spark.conf.set("spark.executor.instances", "50")
```

## 9. Spark UI 调优

Web UI: http://driver:4040

| 指标 | 调优方向 |
|------|---------|
| Stage Duration | 优化慢 stage |
| Shuffle Read/Write | 加 partition + 调 IO |
| GC Time | 调内存 / GC 算法 |
| Spill | 加内存 / 减少 partition |
| Task Skew | 处理数据倾斜 |

## 10. 实战调优案例

### 案例 1：join 慢

```
10 亿 user × 10 亿 order
user 100 MB（小）→ broadcast
order 100 GB（大）→ 普通 join

df.join(F.broadcast(user), "user_id")  # 1 分钟
df.join(user, "user_id")                # 30 分钟
```

### 案例 2：数据倾斜

```
10 亿订单，1 个 vip 用户占 1 亿
→ 1 个 Task 处理 1 亿，其他 Task 几秒 → 整体 1 亿

解决：
  1. 加盐：salt = 0..99 → 100 个 reduce
  2. 二阶段聚合
  → 时间从 30 min 减到 5 min
```

## 11. SQL 调优

```python
# 1. 列裁剪
df.select("id", "name")  # 只读 2 列

# 2. 谓词下推
df.filter("dt = '2024-01-15'")  # 分区裁剪

# 3. 避免 shuffle
df.sortWithinPartitions("id")

# 4. 缓存复用
df.persist(StorageLevel.MEMORY_AND_DISK)
df.count()
df.show()
df.unpersist()
```

## 12. 实战调优清单

- [ ] Executor 内存（一般 8-16 GB）
- [ ] Executor cores（一般 4-5）
- [ ] Shuffle partitions（数据量 / 200 MB）
- [ ] 启用 AQE（Spark 3.x）
- [ ] Kryo 序列化
- [ ] 数据倾斜（加盐 / broadcast）
- [ ] Checkpoint（流处理）
- [ ] 监控（Spark UI / History Server）

## 🔗 下一步
- [Spark Core / RDD](/04-spark/rdd)
- [Spark SQL / DataFrame](/04-spark/dataframe)
- [Flink 架构](/05-flink/architecture)
