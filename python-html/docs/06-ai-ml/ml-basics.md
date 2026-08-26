---
title: 机器学习基础
---

# 🧠 机器学习基础

> **机器学习（Machine Learning）**让计算机从**数据中学习规律**，做出预测或决策。本章使用 **scikit-learn** 入门机器学习核心概念。

## 🎯 机器学习分类

```
监督学习（有标签）：
  - 分类（Classification）：预测类别（垃圾邮件识别）
  - 回归（Regression）：预测连续值（房价预测）

无监督学习（无标签）：
  - 聚类（Clustering）：分组（用户分群）
  - 降维（Dimensionality Reduction）：特征压缩

强化学习：
  - 通过试错学习最优策略（AlphaGo）

半监督学习：
  - 少量标签 + 大量无标签

自监督学习：
  - 预训练 LLM 常用
```

## 🛠️ scikit-learn 入门

### 安装

```bash
pip install scikit-learn
```

### 第一个模型：鸢尾花分类

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# 1. 加载数据
iris = load_iris()
X, y = iris.data, iris.target
print(f"特征: {iris.feature_names}")  # 4 个特征
print(f"类别: {iris.target_names}")  # 3 个类别

# 2. 划分训练集 / 测试集
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 3. 创建模型
model = RandomForestClassifier(n_estimators=100, random_state=42)

# 4. 训练
model.fit(X_train, y_train)

# 5. 预测
y_pred = model.predict(X_test)

# 6. 评估
print(f"准确率: {accuracy_score(y_test, y_pred):.2f}")
print(classification_report(y_test, y_pred, target_names=iris.target_names))
```

## 📊 分类算法

### 常用分类器

```python
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB

# 逻辑回归（线性）
lr = LogisticRegression()

# 决策树（非线性）
dt = DecisionTreeClassifier()

# 随机森林（集成）
rf = RandomForestClassifier(n_estimators=100)

# GBDT（集成）
gb = GradientBoostingClassifier()

# SVM（核方法）
svm = SVC()

# KNN（基于距离）
knn = KNeighborsClassifier(n_neighbors=5)

# 朴素贝叶斯（概率）
nb = GaussianNB()

# 训练和预测
for name, model in [("LR", lr), ("DT", dt), ("RF", rf), ("SVM", svm), ("KNN", knn), ("NB", nb)]:
    model.fit(X_train, y_train)
    acc = model.score(X_test, y_test)
    print(f"{name}: {acc:.2f}")
```

## 📈 回归算法

```python
from sklearn.datasets import load_boston  # 注意：Boston 数据集在新版本已移除
from sklearn.datasets import fetch_california_housing
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score

# 加载数据
housing = fetch_california_housing()
X, y = housing.data, housing.target

# 划分
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 线性回归
lr = LinearRegression()
lr.fit(X_train, y_train)
y_pred = lr.predict(X_test)
print(f"MSE: {mean_squared_error(y_test, y_pred):.2f}")
print(f"R²: {r2_score(y_test, y_pred):.2f}")

# 岭回归（L2 正则化）
ridge = Ridge(alpha=1.0)
ridge.fit(X_train, y_train)
print(f"Ridge R²: {ridge.score(X_test, y_test):.2f}")

# 随机森林回归
rf = RandomForestRegressor(n_estimators=100)
rf.fit(X_train, y_train)
print(f"RF R²: {rf.score(X_test, y_test):.2f}")
```

## 🔄 模型选择与调优

### 交叉验证

```python
from sklearn.model_selection import cross_val_score, KFold

# 5 折交叉验证
scores = cross_val_score(model, X, y, cv=5, scoring="accuracy")
print(f"CV scores: {scores}")
print(f"Mean: {scores.mean():.2f} (+/- {scores.std():.2f})")
```

### 网格搜索

```python
from sklearn.model_selection import GridSearchCV

# 参数网格
param_grid = {
    "n_estimators": [50, 100, 200],
    "max_depth": [None, 5, 10, 20],
    "min_samples_split": [2, 5, 10]
}

# 网格搜索
grid_search = GridSearchCV(
    RandomForestClassifier(random_state=42),
    param_grid,
    cv=5,
    scoring="accuracy",
    n_jobs=-1  # 并行
)
grid_search.fit(X_train, y_train)

print(f"Best params: {grid_search.best_params_}")
print(f"Best score: {grid_search.best_score_:.2f}")
best_model = grid_search.best_estimator_
```

### 随机搜索

```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import randint

# 随机参数分布
param_dist = {
    "n_estimators": randint(50, 500),
    "max_depth": [None, 5, 10, 20, 30],
    "min_samples_split": randint(2, 20)
}

random_search = RandomizedSearchCV(
    RandomForestClassifier(random_state=42),
    param_dist,
    n_iter=50,  # 50 次随机采样
    cv=5,
    scoring="accuracy",
    n_jobs=-1,
    random_state=42
)
random_search.fit(X_train, y_train)
print(f"Best params: {random_search.best_params_}")
```

## 🛠️ 数据预处理

### 标准化

```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

# Z-score 标准化（均值为 0，标准差为 1）
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 最小-最大缩放（缩放到 0-1）
minmax = MinMaxScaler()
X_minmax = minmax.fit_transform(X)

# 鲁棒标准化（抗异常值）
robust = RobustScaler()
X_robust = robust.fit_transform(X)
```

### 编码类别特征

```python
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, OrdinalEncoder

# 标签编码（用于有序类别）
le = LabelEncoder()
y_encoded = le.fit_transform(["cat", "dog", "cat"])  # [0, 1, 0]

# 独热编码（用于无序类别）
ohe = OneHotEncoder(sparse_output=False)
X_onehot = ohe.fit_transform([["red"], ["blue"], ["red"]])
# [[1, 0], [0, 1], [1, 0]]
```

### 处理缺失值

```python
import numpy as np
from sklearn.impute import SimpleImputer

# 模拟缺失值
X = np.array([[1, 2], [np.nan, 3], [7, 6]])

# 均值填充
imputer = SimpleImputer(strategy="mean")
X_imputed = imputer.fit_transform(X)

# 中位数填充
imputer = SimpleImputer(strategy="median")
X_imputed = imputer.fit_transform(X)

# 0 填充
imputer = SimpleImputer(strategy="constant", fill_value=0)
X_imputed = imputer.fit_transform(X)
```

## 📊 模型评估

### 分类指标

```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve
)
import matplotlib.pyplot as plt

# 基础指标
y_true = [0, 1, 0, 1, 1, 0]
y_pred = [0, 1, 1, 1, 0, 0]
y_proba = [0.1, 0.9, 0.6, 0.8, 0.4, 0.2]

print(f"Accuracy:  {accuracy_score(y_true, y_pred):.2f}")
print(f"Precision: {precision_score(y_true, y_pred):.2f}")
print(f"Recall:    {recall_score(y_true, y_pred):.2f}")
print(f"F1:        {f1_score(y_true, y_pred):.2f}")
print(f"AUC:       {roc_auc_score(y_true, y_proba):.2f}")

# 混淆矩阵
cm = confusion_matrix(y_true, y_pred)
print(f"Confusion Matrix:\n{cm}")

# 完整报告
print(classification_report(y_true, y_pred))

# ROC 曲线
fpr, tpr, _ = roc_curve(y_true, y_proba)
plt.plot(fpr, tpr, label="ROC curve")
plt.plot([0, 1], [0, 1], "k--")
plt.xlabel("FPR")
plt.ylabel("TPR")
plt.title("ROC Curve")
plt.show()
```

### 回归指标

```python
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score
)
import numpy as np

y_true = np.array([3, -0.5, 2, 7])
y_pred = np.array([2.5, 0.0, 2, 8])

# MAE
print(f"MAE:  {mean_absolute_error(y_true, y_pred):.2f}")
# RMSE
print(f"RMSE: {np.sqrt(mean_squared_error(y_true, y_pred)):.2f}")
# R²
print(f"R²:   {r2_score(y_true, y_pred):.2f}")
```

## 📊 Pipeline（管道）

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier

# 创建 Pipeline
pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("pca", PCA(n_components=10)),
    ("clf", RandomForestClassifier())
])

# 训练
pipe.fit(X_train, y_train)

# 预测
y_pred = pipe.predict(X_test)

# 在 Pipeline 中调参
param_grid = {
    "pca__n_components": [5, 10, 20],
    "clf__n_estimators": [50, 100, 200]
}
grid = GridSearchCV(pipe, param_grid, cv=5)
grid.fit(X_train, y_train)
```

## 🛠️ 模型持久化

```python
import joblib

# 保存
joblib.dump(model, "model.pkl")

# 加载
loaded_model = joblib.load("model.pkl")

# 预测
y_pred = loaded_model.predict(X_test)
```

## 📊 实战：完整 ML 流程

```python
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

# 1. 加载数据
df = pd.read_csv("data.csv")
X = df.drop("target", axis=1)
y = df["target"]

# 2. 划分
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 3. 预处理（数值 + 类别）
numeric_features = X.select_dtypes(include=["int64", "float64"]).columns
categorical_features = X.select_dtypes(include=["object"]).columns

preprocessor = ColumnTransformer([
    ("num", StandardScaler(), numeric_features),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
])

# 4. Pipeline
pipe = Pipeline([
    ("preprocess", preprocessor),
    ("clf", RandomForestClassifier(random_state=42))
])

# 5. 网格搜索
param_grid = {
    "clf__n_estimators": [100, 200, 300],
    "clf__max_depth": [None, 10, 20, 30]
}
grid = GridSearchCV(pipe, param_grid, cv=5, scoring="f1", n_jobs=-1)
grid.fit(X_train, y_train)

# 6. 评估
y_pred = grid.predict(X_test)
print(classification_report(y_test, y_pred))

# 7. 保存
joblib.dump(grid.best_estimator_, "best_model.pkl")
```

## 🎯 总结

**机器学习基础核心要点**：
- ✅ 监督学习（分类、回归）
- ✅ 无监督学习（聚类、降维）
- ✅ scikit-learn 标准 API（fit/predict）
- ✅ 数据预处理（标准化、编码、缺失值）
- ✅ 模型选择（交叉验证、网格搜索）
- ✅ Pipeline（流程化）
- ✅ 模型评估（准确率、F1、AUC 等）
- ✅ 模型持久化（joblib）
- ⚠️ 避免过拟合（正则化、交叉验证）
- ⚠️ 特征工程至关重要

**下一步：** [🤗 Hugging Face](/06-ai-ml/huggingface) — 预训练模型生态


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
