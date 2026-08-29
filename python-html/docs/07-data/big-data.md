---
title: 大数据处理
date: 2026-08-15  # date-auto-injected
---

# 💾 大数据处理

> 当数据量**超出单机内存**时（GB → TB → PB），pandas 就力不从心了。本章介绍 **Dask、PySpark、Polars** 等分布式数据处理框架。

## 🎯 大数据处理工具

```
Dask：
  - pandas 兼容（DataFrame API）
  - 任务调度（out-of-core 处理）
  - 集群支持

Polars：
  - 基于 Rust，极快（10-100x pandas）
  - 内存高效
  - 单机大数据

PySpark：
  - Spark 的 Python API
  - 成熟稳定
  - 集群支持（YARN / Kubernetes）

Modin：
  - pandas 替代品
  - 多核加速
  - 简单替换
```

## 🚀 Dask 入门

### 安装

```bash
pip install dask[complete]
```

### Hello World

```python
import dask.dataframe as dd
import pandas as pd

# 1. 从 pandas 创建
pdf = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
ddf = dd.from_pandas(pdf, npartitions=2)
print(ddf)
print(ddf.compute())  # 触发计算，返回 pandas

# 2. 从 CSV 读取（分块）
ddf = dd.read_csv("big_data.csv")

# 3. 类似 pandas 的 API
result = ddf[ddf["value"] > 100].groupby("category")["value"].mean().compute()
```

### Dask DataFrame

```python
import dask.dataframe as dd

# 读取大文件
ddf = dd.read_csv(
    "huge_data.csv",
    blocksize="64MB"  # 每个分块 64MB
)

# pandas 兼容的 API
filtered = ddf[ddf["age"] > 30]
grouped = filtered.groupby("city")["salary"].mean()
result = grouped.compute()  # 触发计算

# 自定义函数
ddf["full_name"] = ddf["first_name"] + " " + ddf["last_name"]
result = ddf.compute()
```

### Dask 集群

```python
from dask.distributed import Client

# 启动本地集群
client = Client(n_workers=4, threads_per_worker=2)
print(client)

# 提交任务
def square(x):
    return x ** 2

futures = client.map(square, range(1000))
results = client.gather(futures)
```

## 🚀 Polars 入门

### 安装

```bash
pip install polars
```

### 基础使用

```python
import polars as pl
import pandas as pd

# 1. 创建 DataFrame
df = pl.DataFrame({
    "name": ["Alice", "Bob", "Carol"],
    "age": [30, 25, 28]
})
print(df)

# 2. 读取 CSV
df = pl.read_csv("data.csv")

# 3. 写 Parquet（比 CSV 快）
df.write_parquet("data.parquet")
df = pl.read_parquet("data.parquet")

# 4. pandas 兼容
pdf = df.to_pandas()
df_from_pd = pl.from_pandas(pdf)
```

### Polars 表达式（LazyFrame）

```python
import polars as pl

# 1. 惰性求值
df = (
    pl.scan_csv("big_data.csv")  # LazyFrame
    .filter(pl.col("age") > 18)
    .with_columns(
        (pl.col("salary") * 12).alias("annual_salary")
    )
    .group_by("city")
    .agg(pl.col("salary").mean())
    .sort("salary", descending=True)
    .collect()  # 触发计算
)
```

### Polars vs pandas 性能

```python
import polars as pl
import pandas as pd
import numpy as np
import time

# 创建大数据
n = 10_000_000
pdf = pd.DataFrame({
    "A": np.random.rand(n),
    "B": np.random.rand(n)
})

# pandas
start = time.time()
result_pdf = pdf[pdf["A"] > 0.5]["B"].mean()
print(f"pandas: {time.time() - start:.3f}s")

# Polars
pl_df = pl.from_pandas(pdf)
start = time.time()
result_pl = pl_df.filter(pl.col("A") > 0.5).select(pl.col("B").mean()).collect()
print(f"Polars: {time.time() - start:.3f}s")
# Polars 快 5-20x
```

## 🚀 PySpark 入门

### 安装

```bash
pip install pyspark
# 需要 Java 8+ 环境
```

### 创建 SparkSession

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("MyApp") \
    .master("local[*]") \
    .getOrCreate()

# 读取数据
df = spark.read.csv("data.csv", header=True, inferSchema=True)

# 查看
df.show(5)
df.printSchema()
df.describe().show()
```

### 基本操作

```python
# 1. 选择
df.select("name", "age").show()
df.select(df["name"], df["age"] + 1).show()

# 2. 过滤
df.filter(df["age"] > 18).show()
df.where(df["city"] == "Beijing").show()

# 3. 聚合
df.groupBy("city").agg({"age": "avg", "salary": "sum"}).show()

# 4. SQL
df.createOrReplaceTempView("people")
result = spark.sql("SELECT city, AVG(age) FROM people GROUP BY city")
result.show()
```

### Spark DataFrame vs pandas

```python
# pandas（单机器）
import pandas as pd
df = pd.read_csv("data.csv")
result = df.groupby("city")["age"].mean()

# PySpark（多机器/分布式）
df = spark.read.csv("data.csv", header=True, inferSchema=True)
result = df.groupBy("city").agg({"age": "avg"}).collect()
```

## 🚀 Modin（pandas 替代）

```bash
pip install modin[all]
```

```python
# 只需修改导入
import modin.pandas as pd  # 替代 import pandas as pd

# pandas API 完全兼容
df = pd.read_csv("big_data.csv")
result = df.groupby("category")["value"].mean()
# 多核并行处理
```

## 📊 实战：Dask 处理 TB 级数据

```python
import dask.dataframe as dd

# 读取 TB 级 CSV
ddf = dd.read_csv(
    "huge_data/*.csv",
    blocksize="128MB"
)

# pandas 兼容 API
result = (
    ddf
    .query("value > 100")
    .groupby("category")
    .agg({"value": ["mean", "sum", "count"]})
    .compute()  # 触发计算
)

# 保存
result.to_csv("output.csv")
```

## 📊 实战：Polars 高性能分析

```python
import polars as pl

# 1. 惰性查询（LazyFrame）
df = pl.scan_parquet("data/*.parquet")

result = (
    df
    .filter(pl.col("amount") > 100)
    .group_by("user_id")
    .agg([
        pl.col("amount").sum().alias("total_spent"),
        pl.col("amount").mean().alias("avg_spent"),
        pl.col("amount").count().alias("transactions")
    ])
    .filter(pl.col("transactions") > 5)  # 至少 5 次交易
    .sort("total_spent", descending=True)
    .limit(100)  # Top 100
    .collect()
)
```

## 📊 工具对比

| 工具 | 性能 | API 兼容性 | 集群 | 学习曲线 | 推荐场景 |
|------|------|-----------|------|---------|---------|
| **pandas** | 1x | 原生 | ❌ | 低 | < 1 GB |
| **Polars** | 5-20x | 类似 pandas | ❌ | 中 | < 内存 80% |
| **Dask** | 2-10x | pandas 兼容 | ✅ | 中 | < TB |
| **Modin** | 2-4x | pandas 兼容 | ❌ | 低 | 多核加速 |
| **PySpark** | 10-100x | 独立 API | ✅ | 高 | TB-PB |
| **Ray** | 10-100x | 灵活 | ✅ | 中 | ML/DL |

## 🛠️ 选型指南

```
数据量 < 1 GB？
  → pandas（首选，简单）

1-10 GB？
  → Polars（快 5-20 倍）
  → 或 Modin（多核加速）

10-100 GB？
  → Dask（单机能处理）
  → 或 Polars + 分块处理

100 GB - 1 TB？
  → Dask 集群
  → PySpark 集群

> 1 TB？
  → PySpark + 集群（Hive / Iceberg / Delta Lake）
```

## 🛠️ 实战：数据处理 pipeline

```python
import polars as pl
import dask.dataframe as dd

# 方案 1：Polars（推荐，单机）
def process_with_polars():
    df = (
        pl.scan_parquet("data/*.parquet")
        .filter(pl.col("value").is_not_null())
        .with_columns([
            pl.col("date").dt.year().alias("year"),
            pl.col("amount").fill_null(0)
        ])
        .group_by(["year", "category"])
        .agg(pl.col("amount").sum())
        .sort("year")
        .collect()
    )
    return df

# 方案 2：Dask（分布式）
def process_with_dask():
    ddf = dd.read_parquet("data/*.parquet")
    ddf = ddf[ddf["value"].notnull()]
    ddf = ddf.assign(year=ddf["date"].dt.year)
    result = ddf.groupby(["year", "category"])["amount"].sum().compute()
    return result

# 方案 3：PySpark（大数据）
def process_with_spark():
    df = spark.read.parquet("data/*.parquet")
    df.createOrReplaceTempView("data")
    result = spark.sql("""
        SELECT year(date) as year, category, SUM(amount) as total
        FROM data
        WHERE value IS NOT NULL
        GROUP BY year, category
        ORDER BY year
    """)
    return result
```

## 🎯 总结

**大数据处理核心要点**：
- ✅ Polars：单机大数据首选（10-20x 加速）
- ✅ Dask：分布式 + pandas 兼容
- ✅ PySpark：成熟稳定，大数据首选
- ✅ Modin：多核 pandas 替代
- ✅ 选型：数据量决定工具
- ✅ 惰性求值（LazyFrame）节省内存
- ✅ Parquet 列式存储（比 CSV 快 10x）
- ⚠️ 学习曲线（PySpark）
- ⚠️ 集群部署复杂

**下一步：** [📐 复杂度分析](/08-algorithms/complexity) — 算法基础
