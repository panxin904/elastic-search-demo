---
title: 数据清洗
---

# 🔍 数据清洗

> **数据清洗**是数据分析中最**耗时**的环节（占 60-80%）。本章介绍常见的数据质量问题及解决方案。

## 🎯 数据质量问题

```
1. 缺失值（Missing）
2. 重复值（Duplicates）
3. 异常值（Outliers）
4. 不一致（Inconsistency）
5. 格式错误（Format Errors）
6. 数据类型错误（Wrong Types）
7. 噪声（Noise）
```

## 📊 缺失值处理

### 检测缺失值

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "A": [1, 2, np.nan, 4],
    "B": [5, np.nan, np.nan, 8],
    "C": [9, 10, 11, 12]
})

# 检测
print(df.isnull())
print(df.isnull().sum())        # 每列缺失数
print(df.isnull().sum().sum())  # 总缺失数

# 可视化
import matplotlib.pyplot as plt
df.isnull().sum().plot(kind="bar")
plt.title("Missing Values per Column")
plt.show()
```

### 缺失值填充

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "A": [1, 2, np.nan, 4, 5],
    "B": [5, np.nan, np.nan, 8, 9]
})

# 1. 固定值填充
df.fillna(0)

# 2. 统计值填充
df["A"].fillna(df["A"].mean())     # 均值
df["A"].fillna(df["A"].median())   # 中位数
df["A"].fillna(df["A"].mode()[0])  # 众数

# 3. 前向/后向填充
df.fillna(method="ffill")  # 前向
df.fillna(method="bfill")  # 后向

# 4. 插值
df["A"].interpolate(method="linear")   # 线性
df["A"].interpolate(method="polynomial", order=2)  # 多项式
df["A"].interpolate(method="spline", order=2)      # 样条

# 5. 按组填充
df["A"] = df.groupby("category")["A"].transform(
    lambda x: x.fillna(x.mean())
)

# 6. 模型预测填充（KNN）
from sklearn.impute import KNNImputer
imputer = KNNImputer(n_neighbors=3)
df_imputed = pd.DataFrame(
    imputer.fit_transform(df),
    columns=df.columns
)
```

### 删除缺失值

```python
# 删除任何缺失的行
df.dropna()

# 全部缺失才删
df.dropna(how="all")

# 指定列
df.dropna(subset=["A"])

# 阈值（保留至少 N 个非空）
df.dropna(thresh=2)
```

## 🔍 重复值处理

```python
import pandas as pd

df = pd.DataFrame({
    "name": ["Alice", "Bob", "Alice", "Carol", "Bob"],
    "age": [30, 25, 30, 28, 25]
})

# 检测
print(df.duplicated())              # 全部列
print(df.duplicated(subset=["name"]))  # 指定列

# 删除
df.drop_duplicates()                # 全部列
df.drop_duplicates(subset=["name"])
df.drop_duplicates(subset=["name"], keep="last")
df.drop_duplicates(subset=["name"], keep=False)  # 全部删
```

## 🔍 异常值处理

### 检测异常值

```python
import pandas as pd
import numpy as np

np.random.seed(42)
df = pd.DataFrame({
    "A": np.random.normal(100, 10, 100)
})
# 添加异常值
df.loc[5, "A"] = 1000
df.loc[20, "A"] = -100

# 1. Z-score 方法
from scipy import stats
df["z_score"] = np.abs(stats.zscore(df["A"]))
outliers_z = df[df["z_score"] > 3]
print("Z-score 异常：", len(outliers_z))

# 2. IQR 方法
Q1 = df["A"].quantile(0.25)
Q3 = df["A"].quantile(0.75)
IQR = Q3 - Q1
outliers_iqr = df[(df["A"] < Q1 - 1.5 * IQR) | (df["A"] > Q3 + 1.5 * IQR)]
print("IQR 异常：", len(outliers_iqr))

# 3. 分位数
outliers_quantile = df[(df["A"] < df["A"].quantile(0.01)) | 
                        (df["A"] > df["A"].quantile(0.99))]

# 4. 箱线图可视化
import matplotlib.pyplot as plt
df["A"].plot(kind="box")
plt.show()
```

### 处理异常值

```python
import numpy as np

# 1. 删除
df_clean = df[(df["A"] >= lower_bound) & (df["A"] <= upper_bound)]

# 2. 替换为分位数
df["A"] = df["A"].clip(lower=0.01, upper=0.99)

# 3. 替换为均值
df.loc[df["A"] > threshold, "A"] = df["A"].mean()

# 4. Winsorize
from scipy.stats.mstats import winsorize
df["A"] = winsorize(df["A"], limits=[0.05, 0.05])

# 5. Log 变换
df["A_log"] = np.log1p(df["A"])
```

## 🔍 数据类型转换

```python
import pandas as pd

df = pd.DataFrame({
    "id": ["1", "2", "3"],
    "price": ["10.5", "20.0", "30.5"],
    "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
    "category": ["A", "B", "A"]
})

# 转换
df["id"] = df["id"].astype(int)
df["price"] = df["price"].astype(float)
df["date"] = pd.to_datetime(df["date"])
df["category"] = df["category"].astype("category")

# 处理转换错误
df["price"] = pd.to_numeric(df["price"], errors="coerce")  # 错误转 NaN
df["date"] = pd.to_datetime(df["date"], errors="coerce")
```

## 🔍 字符串清洗

```python
import pandas as pd

df = pd.DataFrame({
    "name": ["  Alice  ", "BOB", "carol", "Dave@123", "Eve\n"]
})

# 去除空白
df["name_clean"] = df["name"].str.strip()

# 大小写
df["name_upper"] = df["name_clean"].str.upper()
df["name_lower"] = df["name_clean"].str.lower()
df["name_title"] = df["name_clean"].str.title()

# 替换
df["name_clean"] = df["name_clean"].str.replace(r"[^a-zA-Z\s]", "", regex=True)

# 分割
df = pd.DataFrame({"full_name": ["Alice Smith", "Bob Jones"]})
df[["first", "last"]] = df["full_name"].str.split(" ", expand=True)

# 提取
df = pd.DataFrame({"email": ["alice@example.com", "bob@test.org"]})
df["username"] = df["email"].str.extract(r"(\w+)@")
df["domain"] = df["email"].str.extract(r"@(\w+\.\w+)")

# 包含检测
df["is_alice"] = df["name"].str.contains("Alice", case=False)
```

## 🔍 类别特征编码

```python
import pandas as pd

df = pd.DataFrame({
    "category": ["A", "B", "A", "C", "B", "A"]
})

# 1. 标签编码
df["category_le"] = df["category"].map({"A": 0, "B": 1, "C": 2})

# 2. 因子化
df["category_codes"] = pd.factorize(df["category"])[0]

# 3. 独热编码
df_encoded = pd.get_dummies(df, columns=["category"])

# 4. 频率编码
freq = df["category"].value_counts(normalize=True)
df["category_freq"] = df["category"].map(freq)
```

## 🔍 日期时间处理

```python
import pandas as pd

df = pd.DataFrame({"date": ["2024-01-01", "2024-01-02", "2024-01-03"]})
df["date"] = pd.to_datetime(df["date"])

# 提取组件
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["day"] = df["date"].dt.day
df["weekday"] = df["date"].dt.dayofweek
df["quarter"] = df["date"].dt.quarter

# 时间差
df["date_diff"] = df["date"] - df["date"].min()

# 重采样
ts = pd.Series([1, 2, 3, 4, 5], 
              index=pd.date_range("2024-01-01", periods=5))
print(ts.resample("D").sum())
print(ts.resample("2D").sum())  # 2 天
```

## 🔍 实战：完整数据清洗流程

```python
import pandas as pd
import numpy as np

# 1. 加载数据
df = pd.read_csv("raw_data.csv")

# 2. 查看数据概况
print(f"形状: {df.shape}")
print(f"列: {df.columns.tolist()}")
print(f"缺失值: {df.isnull().sum().to_dict()}")
print(f"重复: {df.duplicated().sum()}")

# 3. 删除重复
df = df.drop_duplicates()

# 4. 处理缺失值
for col in df.columns:
    if df[col].dtype in ["int64", "float64"]:
        df[col] = df[col].fillna(df[col].median())
    else:
        df[col] = df[col].fillna(df[col].mode()[0])

# 5. 数据类型转换
df["id"] = df["id"].astype(str)
df["date"] = pd.to_datetime(df["date"])
df["category"] = df["category"].astype("category")

# 6. 处理异常值
for col in df.select_dtypes(include=[np.number]).columns:
    Q1, Q3 = df[col].quantile([0.25, 0.75])
    IQR = Q3 - Q1
    df = df[(df[col] >= Q1 - 1.5 * IQR) & (df[col] <= Q3 + 1.5 * IQR)]

# 7. 字符串清洗
for col in df.select_dtypes(include=["object"]).columns:
    df[col] = df[col].str.strip().str.lower()

# 8. 特征工程（示例）
df["age_group"] = pd.cut(df["age"], bins=[0, 18, 35, 60, 100], 
                          labels=["child", "young", "middle", "old"])

# 9. 保存
df.to_csv("cleaned_data.csv", index=False)

# 10. 验证
print(f"\n清洗后: {df.shape}")
print(f"缺失值: {df.isnull().sum().sum()}")
print(f"重复: {df.duplicated().sum()}")
```

## 🔍 异常检测进阶

```python
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

# 数据
np.random.seed(42)
X = np.random.randn(200, 2)
X[:5] = X[:5] + 5  # 异常

# 1. Isolation Forest
clf = IsolationForest(contamination=0.05, random_state=42)
outliers = clf.fit_predict(X)
print(f"Isolation Forest 异常: {(outliers == -1).sum()}")

# 2. Local Outlier Factor
clf = LocalOutlierFactor(contamination=0.05)
outliers = clf.fit_predict(X)
print(f"LOF 异常: {(outliers == -1).sum()}")

# 3. DBSCAN
from sklearn.cluster import DBSCAN
db = DBSCAN(eps=0.3, min_samples=5).fit(X)
outliers = (db.labels_ == -1).sum()
print(f"DBSCAN 异常: {outliers}")
```

## 🎯 总结

**数据清洗核心要点**：
- ✅ 检测缺失值（isnull）
- ✅ 处理缺失值（fillna / dropna / 插值）
- ✅ 检测重复值（duplicated）
- ✅ 检测异常值（Z-score / IQR / 箱线图）
- ✅ 数据类型转换（astype / to_numeric）
- ✅ 字符串清洗（strip / lower / 正则）
- ✅ 类别编码（LabelEncoder / get_dummies）
- ✅ 异常检测（Isolation Forest / LOF）
- ⚠️ 数据清洗占 60-80% 工作量
- ⚠️ 谨慎处理异常值（可能是真实数据）

**下一步：** [📊 数据分析实战](/07-data/analysis) — 真实案例分析
