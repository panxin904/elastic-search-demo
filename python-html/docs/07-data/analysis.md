---
title: 数据分析实战
---

# 📊 数据分析实战

> 本章用**真实案例**演示完整的数据分析流程：从数据加载、清洗、探索、可视化到建模。

## 🎯 分析流程

```
1. 提出问题
2. 数据获取
3. 数据清洗
4. 探索性分析（EDA）
5. 特征工程
6. 建模分析
7. 结果可视化
8. 报告与决策
```

## 📊 案例 1：Titanic 生存预测

### 1. 加载数据

```python
import pandas as pd
import numpy as np

# 加载 Titanic 数据
df = pd.read_csv("titanic.csv")
print(df.shape)  # (891, 12)
print(df.head())
print(df.info())
```

### 2. 数据清洗

```python
# 查看缺失值
print(df.isnull().sum())

# 处理缺失值
df["Age"].fillna(df["Age"].median(), inplace=True)
df["Embarked"].fillna(df["Embarked"].mode()[0], inplace=True)
df.drop("Cabin", axis=1, inplace=True)  # 太多缺失

# 数据类型转换
df["Sex"] = df["Sex"].map({"male": 0, "female": 1})
df["Embarked"] = df["Embarked"].map({"S": 0, "C": 1, "Q": 2})
```

### 3. 探索性分析（EDA）

```python
import matplotlib.pyplot as plt
import seaborn as sns

# 生存率
print(df["Survived"].value_counts())
# 0    549（死亡）
# 1    342（生存）

# 按性别生存率
print(df.groupby("Sex")["Survived"].mean())
# Sex
# 0    0.18（男性）
# 1    0.74（女性）

# 按舱位
print(df.groupby("Pclass")["Survived"].mean())
# Pclass
# 1    0.63（一等舱）
# 2    0.47（二等舱）
# 3    0.24（三等舱）

# 可视化
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

df.groupby("Sex")["Survived"].mean().plot(kind="bar", ax=axes[0])
axes[0].set_title("Survival Rate by Sex")

df.groupby("Pclass")["Survived"].mean().plot(kind="bar", ax=axes[1], color="green")
axes[1].set_title("Survival Rate by Pclass")

df.groupby("Age")["Survived"].mean().plot(ax=axes[2], color="red")
axes[2].set_title("Survival Rate by Age")
plt.tight_layout()
plt.show()
```

### 4. 特征工程

```python
# 家庭规模
df["FamilySize"] = df["SibSp"] + df["Parch"] + 1

# 是否独自一人
df["IsAlone"] = (df["FamilySize"] == 1).astype(int)

# 年龄分组
df["AgeGroup"] = pd.cut(df["Age"], bins=[0, 12, 18, 35, 60, 100],
                         labels=["child", "teen", "young", "middle", "old"])

# 名字中的称谓
df["Title"] = df["Name"].str.extract(r"([A-Za-z]+)\.")
print(df["Title"].value_counts())
```

### 5. 建模

```python
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# 准备数据
features = ["Pclass", "Sex", "Age", "Fare", "FamilySize", "IsAlone"]
X = df[features]
y = df["Survived"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 训练
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 评估
y_pred = model.predict(X_test)
print(f"准确率: {accuracy_score(y_test, y_pred):.2f}")
print(classification_report(y_test, y_pred))

# 特征重要性
importance = pd.DataFrame({
    "feature": features,
    "importance": model.feature_importances_
}).sort_values("importance", ascending=False)
print(importance)
```

## 📊 案例 2：销售数据分析

### 1. 加载数据

```python
import pandas as pd

# 模拟销售数据
df = pd.DataFrame({
    "date": pd.date_range("2024-01-01", periods=365),
    "product": (["A"] * 100 + ["B"] * 100 + ["C"] * 100 + ["D"] * 65)[:365],
    "region": (["North"] * 90 + ["South"] * 90 + ["East"] * 90 + ["West"] * 95)[:365],
    "sales": range(100, 465)
})
```

### 2. 时间趋势

```python
import matplotlib.pyplot as plt

# 月度销售
df["month"] = df["date"].dt.to_period("M")
monthly = df.groupby("month")["sales"].sum()

plt.figure(figsize=(12, 5))
monthly.plot(kind="line", marker="o")
plt.title("Monthly Sales")
plt.ylabel("Sales")
plt.grid(True)
plt.show()

# 7 日移动平均
df["sales_ma7"] = df["sales"].rolling(7).mean()
df[["sales", "sales_ma7"]].plot(figsize=(12, 5))
plt.title("Sales with 7-day Moving Average")
plt.show()
```

### 3. 同环比

```python
# 同比（YoY）
df["year"] = df["date"].dt.year
df["month_of_year"] = df["date"].dt.month

monthly_2023 = df[df["year"] == 2023].groupby("month_of_year")["sales"].sum()
monthly_2024 = df[df["year"] == 2024].groupby("month_of_year")["sales"].sum()

yoy = (monthly_2024 - monthly_2023) / monthly_2023 * 100
yoy.plot(kind="bar", figsize=(10, 5))
plt.title("Year-over-Year Growth (%)")
plt.show()
```

### 4. 区域 / 产品分析

```python
# 各产品月度销售（堆叠柱状图）
pivot = df.pivot_table(
    index=df["date"].dt.to_period("M"),
    columns="product",
    values="sales",
    aggfunc="sum"
)

pivot.plot(kind="bar", stacked=True, figsize=(12, 5))
plt.title("Monthly Sales by Product")
plt.legend(title="Product")
plt.show()
```

### 5. RFM 分析

```python
import pandas as pd
import numpy as np

np.random.seed(42)
customers = pd.DataFrame({
    "customer_id": range(1, 101),
    "recency": np.random.randint(1, 365, 100),      # 距上次购买天数
    "frequency": np.random.randint(1, 20, 100),    # 购买次数
    "monetary": np.random.randint(100, 10000, 100)  # 总消费
})

# RFM 分层
customers["R_score"] = pd.qcut(customers["recency"], 4, labels=[4, 3, 2, 1])
customers["F_score"] = pd.qcut(customers["frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4])
customers["M_score"] = pd.qcut(customers["monetary"], 4, labels=[1, 2, 3, 4])
customers["RFM_score"] = customers["R_score"].astype(str) + customers["F_score"].astype(str) + customers["M_score"].astype(str)

# 高价值客户
high_value = customers[customers["RFM_score"] == "444"]
print(f"高价值客户: {len(high_value)}")
```

## 📊 案例 3：金融时间序列

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 模拟股价
np.random.seed(42)
n_days = 252
returns = np.random.normal(0.0005, 0.02, n_days)
prices = 100 * (1 + returns).cumprod()
dates = pd.date_range("2024-01-01", periods=n_days)
stock = pd.DataFrame({"date": dates, "price": prices, "return": returns})

# 1. 趋势图
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# 价格
axes[0].plot(stock["date"], stock["price"])
axes[0].set_title("Stock Price")
axes[0].set_ylabel("Price")
axes[0].grid(True)

# 收益率
axes[1].plot(stock["date"], stock["return"], "g-", alpha=0.6)
axes[1].axhline(0, color="r", linestyle="--")
axes[1].set_title("Daily Return")
axes[1].set_ylabel("Return")
axes[1].grid(True)

# 累计收益
cumulative = (1 + stock["return"]).cumprod() - 1
axes[2].plot(stock["date"], cumulative * 100, "b-")
axes[2].fill_between(stock["date"], 0, cumulative * 100, alpha=0.3)
axes[2].set_title("Cumulative Return (%)")
axes[2].set_ylabel("Return (%)")
axes[2].grid(True)

plt.tight_layout()
plt.show()

# 2. 移动平均
for window in [5, 20, 50]:
    stock[f"MA{window}"] = stock["price"].rolling(window).mean()

stock[["price", "MA5", "MA20", "MA50"]].plot(figsize=(12, 5))
plt.title("Stock Price with Moving Averages")
plt.show()

# 3. 波动率（年化）
stock["volatility"] = stock["return"].rolling(20).std() * np.sqrt(252)
stock["volatility"].plot(figsize=(12, 5), color="red")
plt.title("20-day Rolling Volatility (Annualized)")
plt.show()
```

## 📊 案例 4：用户行为漏斗

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 模拟用户行为数据
np.random.seed(42)
n_users = 10000
events = pd.DataFrame({
    "user_id": np.random.randint(1, n_users + 1, n_users * 3),
    "event": (["visit"] * n_users + 
             ["view_product"] * int(n_users * 0.6) + 
             ["add_to_cart"] * int(n_users * 0.3))[:n_users * 3],
    "timestamp": pd.date_range("2024-01-01", periods=n_users * 3, freq="T")
})

# 漏斗分析
funnel = events.groupby("event")["user_id"].nunique().reset_index()
funnel.columns = ["event", "users"]
funnel = funnel.sort_values("users", ascending=False)
print(funnel)

# 计算转化率
funnel["conversion_rate"] = funnel["users"] / funnel["users"].iloc[0] * 100
funnel["step_conversion"] = funnel["users"] / funnel["users"].shift(1) * 100
print(funnel)

# 漏斗图
fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.barh(funnel["event"], funnel["users"], color="skyblue")
for i, (bar, val) in enumerate(zip(bars, funnel["users"])):
    ax.text(val + 50, bar.get_y() + bar.get_height() / 2, 
            f"{val:,}", va="center")
ax.set_xlabel("Users")
ax.set_title("Conversion Funnel")
plt.show()
```

## 📊 案例 5：A/B 测试分析

```python
import numpy as np
import pandas as pd
from scipy import stats

# 模拟 A/B 测试数据
np.random.seed(42)
n = 5000

df = pd.DataFrame({
    "user_id": range(n),
    "group": np.random.choice(["A", "B"], n),
    "converted": np.random.binomial(1, p=0.10, n=n)  # baseline 10%
})

# 根据分组调整转化率
df.loc[df["group"] == "B", "converted"] = np.random.binomial(
    1, p=0.12, n=(df["group"] == "B").sum()  # B 组 12%
)

# 各组转化率
conv_rate = df.groupby("group")["converted"].mean()
print(conv_rate)

# 假设检验（双比例 Z 检验）
a_conv = df[df["group"] == "A"]["converted"]
b_conv = df[df["group"] == "B"]["converted"]

# 方法 1：scipy
z_stat, p_value = stats.proportions_ztest(
    [b_conv.sum(), a_conv.sum()],
    [len(b_conv), len(a_conv)]
)
print(f"Z 统计量: {z_stat:.3f}, p 值: {p_value:.4f}")

# 方法 2：卡方检验
contingency = pd.crosstab(df["group"], df["converted"])
chi2, p_chi, dof, expected = stats.chi2_contingency(contingency)
print(f"卡方: {chi2:.3f}, p 值: {p_chi:.4f}")

# 结论
if p_value < 0.05:
    print("结论：B 组转化率显著高于 A 组（p < 0.05）")
else:
    print("结论：无显著差异")
```

## 🎯 总结

**数据分析实战核心要点**：
- ✅ 完整流程：加载 → 清洗 → EDA → 建模 → 可视化
- ✅ 案例 1：Titanic 生存预测（分类）
- ✅ 案例 2：销售数据分析（业务分析）
- ✅ 案例 3：金融时间序列
- ✅ 案例 4：用户行为漏斗
- ✅ 案例 5：A/B 测试
- ⚠️ 数据清洗占 60-80% 工作量
- ⚠️ 业务理解比技术更重要

**下一步：** [💾 大数据处理](/07-data/big-data) — Dask / PySpark


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
