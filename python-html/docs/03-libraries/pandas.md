---
title: pandas 数据分析
---

# 🐼 pandas 数据分析

> **pandas** 是 Python **数据分析的基石**。提供高性能、易用的**数据结构**和**数据分析工具**。

## 🎯 pandas 核心数据结构

```python
import pandas as pd

# Series：一维带标签数组
s = pd.Series([1, 3, 5, 7, 9], name="numbers")
print(s)
# 0    1
# 1    3
# 2    5
# 3    7
# 4    9

# DataFrame：二维表格（核心）
data = {
    "name": ["Alice", "Bob", "Carol"],
    "age": [30, 25, 28],
    "city": ["Beijing", "Shanghai", "Guangzhou"]
}
df = pd.DataFrame(data)
print(df)
#     name  age       city
# 0  Alice   30    Beijing
# 1    Bob   25  Shanghai
# 2  Carol   28 Guangzhou
```

## 📊 创建 DataFrame（库 API 视角）

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
df = pd.DataFrame(np.random.rand(3, 4), columns=["A", "B", "C", "D"])

# 从 CSV
df = pd.read_csv("data.csv")

# 从 Excel
df = pd.read_excel("data.xlsx", sheet_name="Sheet1")

# 从 SQL
import sqlalchemy
engine = sqlalchemy.create_engine("sqlite:///db.db")
df = pd.read_sql("SELECT * FROM users", engine)

# 从 JSON
df = pd.read_json("data.json")
```

## 🔍 数据查看

```python
import pandas as pd
import numpy as np

df = pd.DataFrame(np.random.rand(5, 4), columns=list("ABCD"))

# 基本信息
df.head()        # 前 5 行
df.head(3)       # 前 3 行
df.tail(3)       # 后 3 行
df.shape         # (行数, 列数)
df.columns       # 列名
df.index         # 行索引
df.dtypes        # 每列的数据类型
df.info()        # 详细信息

# 统计信息
df.describe()    # 数值列的统计
df.describe(include="all")  # 所有列

# 唯一值
df["A"].unique()
df["A"].nunique()
df["A"].value_counts()
```

## 📈 数据选择

### 选择列

```python
# 单列
df["name"]

# 多列
df[["name", "age"]]

# 按数据类型
df.select_dtypes(include=["int64", "float64"])
df.select_dtypes(exclude=["object"])
```

### 选择行

```python
# 按标签
df.loc[0]                 # 第 0 行
df.loc[0:3]               # 切片（包含端点）
df.loc[[0, 2, 4]]         # 多行

# 按位置
df.iloc[0]                # 第 0 行
df.iloc[0:3]              # 切片（不包含端点）
df.iloc[[0, 2, 4]]        # 多行

# 按条件（布尔索引）
df[df["age"] > 25]
df[(df["age"] > 20) & (df["city"] == "Beijing")]

# query 方法（推荐）
df.query("age > 25 and city == 'Beijing'")
```

### 选择行和列

```python
# loc: 标签
df.loc[0:2, "name"]
df.loc[0:2, ["name", "age"]]

# iloc: 位置
df.iloc[0:2, 0:2]

# 单个值
df.loc[0, "name"]
df.at[0, "name"]      # 更快
df.iat[0, 0]          # 更快
```

## 🔧 数据清洗

### 缺失值

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "A": [1, 2, np.nan, 4],
    "B": [5, np.nan, np.nan, 8],
    "C": [9, 10, 11, 12]
})

# 检测缺失值
df.isnull()
df.isnull().sum()       # 每列缺失值数量
df.notnull()

# 删除缺失值
df.dropna()             # 任何缺失值删除
df.dropna(how="all")    # 全部缺失才删
df.dropna(subset=["A"]) # 只看 A 列

# 填充缺失值
df.fillna(0)                     # 填充固定值
df.fillna(df.mean())             # 填充均值
df.fillna(df.mean()["A":"B"])   # 不同列用不同均值
df.fillna(method="ffill")        # 前向填充
df.fillna(method="bfill")        # 后向填充
```

### 重复值

```python
df = pd.DataFrame({
    "name": ["Alice", "Bob", "Alice", "Carol"],
    "age": [30, 25, 30, 28]
})

# 检测重复
df.duplicated()              # 标记重复行
df.duplicated(subset=["name"])  # 按列检测

# 删除重复
df.drop_duplicates()              # 全部列都重复才删
df.drop_duplicates(subset=["name"])  # 指定列
df.drop_duplicates(keep="last")   # 保留最后
df.drop_duplicates(keep=False)    # 全部删除
```

### 数据类型转换

```python
df["age"] = df["age"].astype(int)
df["age"] = df["age"].astype(float)
df["date"] = df["date"].astype("datetime64[ns]")
df["category"] = df["category"].astype("category")

# 数值型 → 类别型（节省内存）
df["city"] = df["city"].astype("category")
```

## 📊 数据聚合

### groupby

```python
df = pd.DataFrame({
    "department": ["IT", "HR", "IT", "HR", "Finance"],
    "name": ["Alice", "Bob", "Carol", "Dave", "Eve"],
    "salary": [10000, 8000, 12000, 9000, 15000]
})

# 基本分组
print(df.groupby("department")["salary"].sum())
# IT        22000
# HR        17000
# Finance   15000

# 多聚合
print(df.groupby("department").agg({
    "salary": ["sum", "mean", "max", "min"]
}))

# 自定义聚合
print(df.groupby("department").agg(
    total=("salary", "sum"),
    avg=("salary", "mean"),
    count=("name", "count")
))
```

### 透视表

```python
df = pd.DataFrame({
    "date": ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02"],
    "category": ["A", "B", "A", "B"],
    "sales": [100, 200, 150, 250]
})

# 透视
pivot = df.pivot_table(
    index="date",
    columns="category",
    values="sales",
    aggfunc="sum"
)
print(pivot)
# category       A      B
# date
# 2024-01-01   100    200
# 2024-01-02   150    250
```

### 合并

```python
# 拼接
df1 = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
df2 = pd.DataFrame({"A": [5, 6], "B": [7, 8]})

# 垂直拼接
pd.concat([df1, df2])

# 水平拼接
pd.concat([df1, df2], axis=1)

# 合并（类似 SQL JOIN）
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

## 📊 数据分析实战

```python
import pandas as pd

# 加载数据
df = pd.read_csv("sales.csv", parse_dates=["date"])

# 探索
print(df.shape)
print(df.info())
print(df.describe())

# 时间序列分析
df.set_index("date", inplace=True)
monthly = df.resample("M")["sales"].sum()

# 滑动窗口
df["rolling_avg_7d"] = df["sales"].rolling(7).mean()
df["rolling_std_7d"] = df["sales"].rolling(7).std()

# 同比环比
df["yoy"] = df["sales"].pct_change(12)  # 同比 12 个月
df["mom"] = df["sales"].pct_change(1)   # 环比 1 个月

# 导出
df.to_csv("output.csv", index=False)
df.to_excel("output.xlsx", index=False)
```

## ⚡ 性能优化

```python
# 1. 选择合适的数据类型
df["id"] = df["id"].astype("int32")        # 默认是 int64
df["category"] = df["category"].astype("category")  # 类别型

# 2. 避免 apply + lambda（慢）
df["new"] = df["value"].apply(lambda x: x * 2)

# 推荐：向量化操作（快）
df["new"] = df["value"] * 2

# 3. 用 query 代替复杂布尔索引
df.query("age > 25 and city == 'Beijing'")

# 4. 用 isin 代替多个 OR
df[df["city"].isin(["Beijing", "Shanghai"])]

# 5. 用 category 节省内存
df["city"] = df["city"].astype("category")
```

## 🎯 总结

**pandas 核心要点**：
- ✅ DataFrame 是核心（二维表格）
- ✅ Series 是一维带标签数组
- ✅ 强大 IO（CSV/Excel/SQL/JSON）
- ✅ 数据清洗（缺失值、重复、类型）
- ✅ groupby / 透视表 / 合并
- ✅ 时间序列分析
- ✅ 矢量化操作提升性能
- ⚠️ 大数据用 Dask 或 Vaex（pandas 不适合）
- ⚠️ 内存敏感时用 category 类型

**下一步：** [🧪 pytest 测试](/03-libraries/pytest) — Python 测试框架


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
