---
title: Matplotlib 可视化
date: 2026-08-15  # date-auto-injected
---

# 📈 Matplotlib 可视化

> **Matplotlib** 是 Python 最基础的**数据可视化库**。所有高级可视化库（Seaborn、Plotly）都构建在它之上。

## 🎯 安装

```bash
pip install matplotlib
```

## 🚀 快速开始

```python
import matplotlib.pyplot as plt
import numpy as np

# 准备数据
x = np.linspace(0, 10, 100)
y = np.sin(x)

# 绘图
plt.plot(x, y)
plt.xlabel("x")
plt.ylabel("sin(x)")
plt.title("Sine Wave")
plt.grid(True)
plt.show()
```

## 📊 基础图表

### 折线图

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)

# 多条线
plt.plot(x, y1, label="sin(x)", color="blue", linestyle="-")
plt.plot(x, y2, label="cos(x)", color="red", linestyle="--")
plt.xlabel("x")
plt.ylabel("y")
plt.title("Trig Functions")
plt.legend()
plt.grid(True)
plt.show()

# 保存
plt.savefig("plot.png", dpi=300, bbox_inches="tight")
```

### 散点图

```python
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(42)
x = np.random.randn(200)
y = 2 * x + np.random.randn(200) * 0.5
colors = np.random.rand(200)
sizes = np.random.rand(200) * 100

plt.scatter(x, y, c=colors, s=sizes, alpha=0.6, cmap="viridis")
plt.colorbar(label="Value")
plt.xlabel("X")
plt.ylabel("Y")
plt.title("Scatter Plot")
plt.show()
```

### 柱状图

```python
import matplotlib.pyplot as plt

# 普通柱状图
categories = ["A", "B", "C", "D", "E"]
values = [23, 45, 56, 78, 33]

plt.figure(figsize=(8, 5))
plt.bar(categories, values, color="skyblue")
plt.xlabel("Category")
plt.ylabel("Value")
plt.title("Bar Chart")
plt.show()

# 水平柱状图
plt.barh(categories, values, color="lightgreen")
plt.xlabel("Value")
plt.ylabel("Category")
plt.title("Horizontal Bar Chart")
plt.show()

# 分组柱状图
import numpy as np
x = np.arange(5)
width = 0.35
plt.bar(x - width/2, [23, 45, 56, 78, 33], width, label="Group A")
plt.bar(x + width/2, [33, 38, 49, 60, 25], width, label="Group B")
plt.xticks(x, ["A", "B", "C", "D", "E"])
plt.legend()
plt.title("Grouped Bar Chart")
plt.show()
```

### 直方图

```python
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(42)
data = np.random.normal(100, 15, 1000)

plt.hist(data, bins=30, color="skyblue", edgecolor="black", alpha=0.7)
plt.xlabel("Value")
plt.ylabel("Frequency")
plt.title("Histogram")
plt.axvline(data.mean(), color="red", linestyle="--", label="Mean")
plt.legend()
plt.show()
```

### 饼图

```python
import matplotlib.pyplot as plt

labels = ["A", "B", "C", "D"]
sizes = [25, 30, 20, 25]
colors = ["gold", "yellowgreen", "lightcoral", "lightskyblue"]
explode = (0.1, 0, 0, 0)

plt.figure(figsize=(8, 8))
plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct="%1.1f%%", shadow=True, startangle=90)
plt.axis("equal")
plt.title("Pie Chart")
plt.show()
```

### 箱线图

```python
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(42)
data = [np.random.normal(0, std, 100) for std in [1, 2, 3]]

plt.boxplot(data, labels=["A", "B", "C"])
plt.ylabel("Value")
plt.title("Box Plot")
plt.grid(True)
plt.show()
```

## 📊 子图（Subplots）

### 等分网格

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)

# 2x2 子图
fig, axes = plt.subplots(2, 2, figsize=(10, 8))

axes[0, 0].plot(x, np.sin(x))
axes[0, 0].set_title("sin")

axes[0, 1].plot(x, np.cos(x), "r")
axes[0, 1].set_title("cos")

axes[1, 0].plot(x, np.tan(x), "g")
axes[1, 0].set_title("tan")
axes[1, 0].set_ylim(-5, 5)

axes[1, 1].plot(x, np.exp(x), "m")
axes[1, 1].set_title("exp")

plt.tight_layout()
plt.show()
```

### 不规则布局

```python
import matplotlib.pyplot as plt
import numpy as np

fig = plt.figure(figsize=(10, 6))

ax1 = fig.add_subplot(2, 2, 1)
ax1.plot(np.sin(np.linspace(0, 10, 100)))
ax1.set_title("1")

ax2 = fig.add_subplot(2, 2, 2)
ax2.plot(np.cos(np.linspace(0, 10, 100)))
ax2.set_title("2")

ax3 = fig.add_subplot(2, 1, 2)
ax3.plot(np.tan(np.linspace(0, 10, 100)))
ax3.set_title("3 (span 2 cols)")

plt.tight_layout()
plt.show()
```

## 📊 样式美化

### 主题

```python
import matplotlib.pyplot as plt

# 可用主题
print(plt.style.available)
# ['Solarize_Light2', '_classic_test_patch', 'bmh', 'classic', ...

# 使用主题
plt.style.use("ggplot")

x = range(10)
y = [i**2 for i in x]
plt.plot(x, y)
plt.title("With ggplot style")
plt.show()

# 恢复默认
plt.style.use("default")
```

### 颜色

```python
import matplotlib.pyplot as plt
import numpy as np

# 命名颜色
plt.plot([1, 2, 3], [1, 4, 9], color="coral")

# HEX
plt.plot([1, 2, 3], [1, 4, 9], color="#FF5733")

# RGB
plt.plot([1, 2, 3], [1, 4, 9], color=(0.1, 0.5, 0.8))

# Colormap
cmap = plt.cm.viridis
x = np.linspace(0, 10, 100)
y = np.sin(x)
plt.scatter(x, y, c=y, cmap=cmap)
plt.colorbar()
plt.show()
```

### 标注

```python
import matplotlib.pyplot as plt

x = [1, 2, 3, 4, 5]
y = [2, 4, 6, 8, 10]

plt.plot(x, y, "o-", markersize=10)
plt.xlabel("X")
plt.ylabel("Y")
plt.title("With Annotations")

# 标注点
plt.annotate("重要点", xy=(3, 6), xytext=(4, 8),
            arrowprops=dict(arrowstyle="->", color="red"))

# 文字
plt.text(2, 9, "文本注释", fontsize=12, color="blue")

# 网格
plt.grid(True, alpha=0.3)
plt.show()
```

## 📊 实战：完整数据可视化

```python
import matplotlib.pyplot as plt
import numpy as np

# 模拟数据
np.random.seed(42)
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
product_a = np.random.randint(80, 150, 12)
product_b = np.random.randint(60, 130, 12)
product_c = np.random.randint(40, 110, 12)

# 创建图表
fig, ax1 = plt.subplots(figsize=(12, 6))

# 柱状图（产品销量）
x = np.arange(len(months))
width = 0.25

ax1.bar(x - width, product_a, width, label="Product A", color="skyblue")
ax1.bar(x, product_b, width, label="Product B", color="lightgreen")
ax1.bar(x + width, product_c, width, label="Product C", color="salmon")
ax1.set_xlabel("Month")
ax1.set_ylabel("Sales", color="black")
ax1.set_xticks(x)
ax1.set_xticklabels(months)
ax1.legend(loc="upper left")

# 折线图（趋势）
ax2 = ax1.twinx()
total = product_a + product_b + product_c
ax2.plot(x, total, "k--o", label="Total", linewidth=2)
ax2.set_ylabel("Total Sales", color="black")
ax2.legend(loc="upper right")

# 标题
fig.suptitle("Monthly Sales Report", fontsize=14, fontweight="bold")
fig.tight_layout()
plt.show()
```

## 📊 3D 图表

```python
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

# 曲面图
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection="3d")

x = np.linspace(-5, 5, 100)
y = np.linspace(-5, 5, 100)
X, Y = np.meshgrid(x, y)
Z = np.sin(np.sqrt(X**2 + Y**2))

ax.plot_surface(X, Y, Z, cmap="viridis")
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.set_title("3D Surface")
plt.show()

# 散点图
ax = fig.add_subplot(111, projection="3d")
ax.scatter(X, Y, Z, c=Z, cmap="viridis")
plt.show()
```

## 📊 实战：销售数据仪表板

```python
import matplotlib.pyplot as plt
import numpy as np

# 模拟数据
np.random.seed(42)
months = np.arange(1, 13)
sales = np.cumsum(np.random.randn(12) * 50 + 200)
profit_margin = np.random.uniform(0.1, 0.3, 12)

# 创建 2x2 子图
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle("Sales Dashboard 2024", fontsize=14, fontweight="bold")

# 1. 销售趋势（折线图）
axes[0, 0].plot(months, sales, "b-o", linewidth=2)
axes[0, 0].set_title("Monthly Sales")
axes[0, 0].set_xlabel("Month")
axes[0, 0].set_ylabel("Sales ($)")
axes[0, 0].grid(True, alpha=0.3)

# 2. 利润率（柱状图）
axes[0, 1].bar(months, profit_margin * 100, color="green", alpha=0.7)
axes[0, 1].set_title("Profit Margin")
axes[0, 1].set_xlabel("Month")
axes[0, 1].set_ylabel("Margin (%)")
axes[0, 1].axhline(profit_margin.mean() * 100, color="red", 
                   linestyle="--", label="Avg")
axes[0, 1].legend()

# 3. 销售分布（直方图）
axes[1, 0].hist(sales, bins=10, color="skyblue", edgecolor="black")
axes[1, 0].set_title("Sales Distribution")
axes[1, 0].set_xlabel("Sales ($)")
axes[1, 0].set_ylabel("Frequency")
axes[1, 0].axvline(sales.mean(), color="red", linestyle="--", label="Mean")
axes[1, 0].legend()

# 4. 散点图（销售 vs 利润率）
axes[1, 1].scatter(sales, profit_margin * 100, s=100, alpha=0.6)
axes[1, 1].set_title("Sales vs Margin")
axes[1, 1].set_xlabel("Sales ($)")
axes[1, 1].set_ylabel("Margin (%)")
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

## 🎯 总结

**Matplotlib 核心要点**：
- ✅ 基础图表：折线、柱状、散点、直方图、饼图
- ✅ 子图（subplots）
- ✅ 主题美化（ggplot / seaborn）
- ✅ 标注（annotate / text）
- ✅ 3D 图表
- ✅ 与 NumPy / pandas 集成
- ✅ 保存为 PNG / PDF / SVG
- ✅ 交互式（widget 后端）
- ⚠️ 静态图（不如 Plotly 交互）
- ⚠️ 大量数据性能差

**下一步：** [🔍 数据清洗](/07-data/cleaning) — 数据预处理


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

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [java](https://java-px.bot.cd/java-web-manual/):Java 对比
- [ai](https://java-px.bot.cd/ai/):AI / 机器学习
- [bigdata](https://java-px.bot.cd/bigdata/):大数据 / 数据处理
