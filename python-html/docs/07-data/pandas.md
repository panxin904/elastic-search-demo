---
title: pandas 入门
---

# 🐼 pandas 入门

> **pandas** 是 Python **数据分析的基石**。本章从基础开始讲解 pandas 核心数据结构 DataFrame 的使用。

## 🎯 核心数据结构

```python
import pandas as pd

# Series：一维带标签数组
s = pd.Series([1, 3, 5, 7, 9], index=["a", "b", "c", "d", "e"])
print(s)
# a    1
# b    3
# c    5
# d    7
# e    9

# DataFrame：二维表格
df = pd.DataFrame({
    "name": ["Alice", "Bob", "Carol"],
    "age": [30, 25, 28],
    "city": ["Beijing", "Shanghai", "Guangzhou"]
})
print(df)
#     name  age       city
# 0  Alice   30    Beijing
# 1    Bob   25  Shanghai
# 2  Carol   28 Guangzhou
```

## 📊 创建 DataFrame

```python
import pandas as pd

# 从字典
df = pd.DataFrame({
    "name": ["Alice", "Bob"],
    "age": [30, 25]
})

# 从列表
df = pd.DataFrame([
    ["Alice", 30],
    ["Bob", 25]
], columns=["name", "age"])

# 从 NumPy 数组
import numpy as np
df = pd.DataFrame(
    np.random.rand(3, 4),
    columns=["A", "B", "C", "D"]
)

# 从文件
df = pd.read_csv("data.csv")
df = pd.read_excel("data.xlsx")
df = pd.read_json("data.json")

# 从 SQL
import sqlalchemy
engine = sqlalchemy.create_engine("sqlite:///db.db")
df = pd.read_sql("SELECT * FROM users", engine)
```

## 🔍 数据查看

```python
import pandas as pd
import numpy as np

df = pd.DataFrame(np.random.rand(5, 4), columns=list("ABCD"))

# 基本信息
df.head()        # 前 5 行
df.head(3)       # 前 3 行
df.tail(2)       # 后 2 行
df.shape         # (5, 4)
df.columns       # Index(['A', 'B', 'C', 'D'])
df.dtypes        # 每列数据类型
df.info()        # 详细摘要

# 统计信息
df.describe()    # 数值列统计（count, mean, std, min, max...）

# 唯一值
df["A"].unique()
df["A"].nunique()    # 唯一值数量
df["A"].value_counts()  # 频次

# 唯一索引
df.index
df.set_index("A", inplace=True)
df.reset_index(drop=True, inplace=True)
```

## 📈 数据选择

### 选择列

```python
# 单列
df["name"]

# 多列
df[["name", "age"]]

# 按类型
df.select_dtypes(include=["int64", "float64"])
df.select_dtypes(exclude=["object"])

# 按列名模式
df.filter(like="name")  # 列名包含 "name"
df.filter(regex="^a")    # 列名以 a 开头
```

### 选择行

```python
# 按位置
df.iloc[0]      # 第 0 行
df.iloc[0:3]    # 前 3 行

# 按标签
df.loc[0]       # 索引为 0 的行
df.loc[0:2]     # 索引 0-2

# 条件筛选
df[df["age"] > 25]
df[(df["age"] > 20) & (df["city"] == "Beijing")]
df.query("age > 25 and city == 'Beijing'")  # query 方法

# isin
df[df["city"].isin(["Beijing", "Shanghai"])]
```

### 同时选择行和列

```python
# loc
df.loc[0:2, "name"]
df.loc[0:2, ["name", "age"]]

# iloc
df.iloc[0:2, 0:2]

# 快速取值
df.at[0, "name"]    # 单个值（loc 快版）
df.iat[0, 0]        # 单个值（iloc 快版）
```

## 🔧 数据修改

### 修改值

```python
# 单值
df.loc[0, "age"] = 31

# 条件修改
df.loc[df["age"] > 30, "category"] = "senior"
df.loc[df["age"] <= 30, "category"] = "junior"

# 添加新列
df["salary"] = [50000, 60000, 70000]

# 计算列
df["age_next_year"] = df["age"] + 1
df["is_adult"] = df["age"] >= 18

# apply 函数
df["name_upper"] = df["name"].apply(str.upper)
df["age_group"] = df["age"].apply(lambda x: "young" if x < 30 else "old")
```

### 排序

```python
# 按值排序
df.sort_values("age", ascending=False)
df.sort_values(["age", "name"], ascending=[True, False])

# 按索引排序
df.sort_index(ascending=False)
```

## 📊 数据聚合

### groupby

```python
df = pd.DataFrame({
    "department": ["IT", "HR", "IT", "HR", "Finance"],
    "name": ["Alice", "Bob", "Carol", "Dave", "Eve"],
    "salary": [10000, 8000, 12000, 9000, 15000]
})

# 单聚合
print(df.groupby("department")["salary"].sum())
# IT        22000
# HR        17000
# Finance   15000

# 多聚合
print(df.groupby("department").agg({
    "salary": ["sum", "mean", "max", "min", "count"]
}))

# 命名聚合
print(df.groupby("department").agg(
    total=("salary", "sum"),
    avg=("salary", "mean"),
    count=("name", "count")
))

# 转换
df["dept_avg"] = df.groupby("department")["salary"].transform("mean")
```

### 透视表

```python
df = pd.DataFrame({
    "date": ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02"],
    "product": ["A", "B", "A", "B"],
    "sales": [100, 200, 150, 250]
})

pivot = df.pivot_table(
    index="date",
    columns="product",
    values="sales",
    aggfunc="sum",
    fill_value=0
)
print(pivot)
```

## 📊 数据合并

### concat

```python
df1 = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
df2 = pd.DataFrame({"A": [5, 6], "B": [7, 8]})

# 垂直拼接
pd.concat([df1, df2])

# 水平拼接
pd.concat([df1, df2], axis=1)

# 重置索引
pd.concat([df1, df2], ignore_index=True)
```

### merge

```python
users = pd.DataFrame({
    "id": [1, 2, 3],
    "name": ["Alice", "Bob", "Carol"]
})
orders = pd.DataFrame({
    "user_id": [1, 1, 2, 3],
    "amount": [100, 200, 150, 300]
})

# 内连接
pd.merge(users, orders, left_on="id", right_on="user_id")

# 左连接
pd.merge(users, orders, left_on="id", right_on="user_id", how="left")

# 外连接
pd.merge(users, orders, left_on="id", right_on="user_id", how="outer")
```

## 📊 数据清洗

### 缺失值

```python
import numpy as np

df = pd.DataFrame({
    "A": [1, 2, np.nan, 4],
    "B": [5, np.nan, np.nan, 8],
    "C": [9, 10, 11, 12]
})

# 检测
df.isnull()
df.isnull().sum()

# 删除
df.dropna()               # 任何缺失删除
df.dropna(how="all")     # 全部缺失才删
df.dropna(subset=["A"])  # 指定列

# 填充
df.fillna(0)
df.fillna(df.mean())
df.fillna(method="ffill")
```

### 重复值

```python
df = pd.DataFrame({
    "name": ["Alice", "Bob", "Alice", "Carol"],
    "age": [30, 25, 30, 28]
})

# 检测
df.duplicated()
df.duplicated(subset=["name"])

# 删除
df.drop_duplicates()
df.drop_duplicates(subset=["name"], keep="last")
```

## 📊 IO 操作

```python
# CSV
df.to_csv("output.csv", index=False)
df.to_csv("output.csv", index=False, encoding="utf-8-sig")  # Excel 友好

# Excel
df.to_excel("output.xlsx", index=False, sheet_name="Sheet1")

# JSON
df.to_json("output.json", orient="records", force_ascii=False)

# SQL
import sqlalchemy
engine = sqlalchemy.create_engine("sqlite:///db.db")
df.to_sql("users", engine, if_exists="replace", index=False)
```

## 🎯 总结

**pandas 核心要点**：
- ✅ DataFrame 是核心（二维表格）
- ✅ 数据选择（loc / iloc / query）
- ✅ 数据清洗（缺失值、重复）
- ✅ 数据聚合（groupby / 透视表）
- ✅ 数据合并（concat / merge）
- ✅ 强大的 IO（CSV / Excel / SQL / JSON）
- ✅ apply 函数式编程
- ✅ 时间序列分析
- ⚠️ 大数据用 Dask / Vaex
- ⚠️ 用 category 类型节省内存

**下一步：** [🔢 NumPy 数值计算](/07-data/numpy) — 数组运算基础


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
