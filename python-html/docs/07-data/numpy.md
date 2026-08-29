---
title: NumPy 数值计算
date: 2026-08-15  # date-auto-injected
---

# 🔢 NumPy 数值计算

> **NumPy** 是 Python **数值计算的基础库**。pandas、scikit-learn、TensorFlow 等都依赖 NumPy。

## 🎯 NumPy 核心：ndarray

```python
import numpy as np

# 创建数组
arr = np.array([1, 2, 3, 4, 5])
print(arr)
print(type(arr))  # <class 'numpy.ndarray'>
print(arr.shape)  # (5,)
print(arr.dtype)  # int64
```

### 数组 vs Python 列表

```python
import numpy as np
import time

# Python 列表
lst = list(range(1_000_000))
start = time.time()
lst2 = [x * 2 for x in lst]
print(f"列表: {time.time() - start:.4f}s")

# NumPy 数组
arr = np.arange(1_000_000)
start = time.time()
arr2 = arr * 2
print(f"NumPy: {time.time() - start:.4f}s")
# NumPy 快 50-100 倍
```

## 📊 创建数组

```python
import numpy as np

# 1. 从列表
arr = np.array([1, 2, 3])

# 2. 特殊数组
np.zeros(5)           # [0, 0, 0, 0, 0]
np.ones((2, 3))       # 2x3 全 1
np.full((2, 2), 7)    # 2x2 全 7
np.empty((2, 3))      # 未初始化（值随机）

# 3. 范围
np.arange(0, 10, 2)   # [0, 2, 4, 6, 8]
np.linspace(0, 1, 5)  # [0, 0.25, 0.5, 0.75, 1.0]

# 4. 随机
np.random.rand(3, 4)        # 0-1 均匀分布
np.random.randn(3, 4)       # 标准正态分布
np.random.randint(0, 10, 5) # 0-10 整数

# 5. 特殊矩阵
np.eye(3)              # 3x3 单位矩阵
np.diag([1, 2, 3])    # 对角矩阵
```

## 🔢 数组属性

```python
import numpy as np

arr = np.array([[1, 2, 3], [4, 5, 6]])

print(arr.shape)    # (2, 3)
print(arr.ndim)     # 2
print(arr.size)     # 6
print(arr.dtype)    # int64
print(arr.itemsize) # 8 字节
print(arr.nbytes)   # 48 字节（8*6）

# 改变形状
arr.reshape(3, 2)   # 3x2
arr.flatten()        # 1D
arr.T               # 转置
```

## 📊 数组索引

```python
import numpy as np

arr = np.array([10, 20, 30, 40, 50])

# 基本索引
print(arr[0])      # 10
print(arr[-1])     # 50

# 切片
print(arr[1:4])    # [20, 30, 40]
print(arr[::2])    # [10, 30, 50]

# 布尔索引
mask = arr > 25
print(arr[mask])    # [30, 40, 50]

# 花式索引
indices = [0, 2, 4]
print(arr[indices]) # [10, 30, 50]

# 二维数组
arr2d = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
print(arr2d[0])         # 第一行 [1, 2, 3]
print(arr2d[0, 1])      # 第一行第二列 2
print(arr2d[0:2, 1:3]) # 子矩阵 [[2, 3], [5, 6]]
```

## 🔢 数组运算

```python
import numpy as np

a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

# 算术（向量化）
print(a + b)      # [5, 7, 9]
print(a * b)      # [4, 10, 18]
print(a ** 2)     # [1, 4, 9]
print(np.sqrt(a)) # [1, 1.41, 1.73]

# 比较
print(a > 2)      # [False, False, True]
print((a > 1) & (a < 4))  # [False, True, True]

# 聚合
arr = np.array([1, 2, 3, 4, 5])
print(arr.sum())       # 15
print(arr.mean())      # 3.0
print(arr.std())       # 1.41
print(arr.min(), arr.max())  # 1, 5
print(arr.argmin(), arr.argmax())  # 0, 4
```

## 📊 矩阵运算

```python
import numpy as np

a = np.array([[1, 2], [3, 4]])
b = np.array([[5, 6], [7, 8]])

# 矩阵乘法
print(a @ b)        # [[19, 22], [43, 50]]
print(np.dot(a, b)) # 同上

# 元素乘
print(a * b)        # [[5, 12], [21, 32]]

# 转置
print(a.T)          # [[1, 3], [2, 4]]

# 求逆
print(np.linalg.inv(a))

# 行列式
print(np.linalg.det(a))

# 特征值
print(np.linalg.eigvals(a))
```

## 🔢 广播（Broadcasting）

```python
import numpy as np

# 不同形状数组的运算（自动扩展）
a = np.array([[1], [2], [3]])  # (3, 1)
b = np.array([10, 20, 30])    # (3,)

# 自动广播为 (3, 3)
print(a + b)
# [[11, 21, 31],
#  [12, 22, 32],
#  [13, 23, 33]]

# 规则：维度对齐，从右向左
# - 如果维度数不同，在左边补 1
# - 如果某维度为 1，扩展为匹配对方
# - 其他维度必须相同
```

## 📊 数组操作

### reshape

```python
import numpy as np

arr = np.arange(12)

# reshape
print(arr.reshape(3, 4))
# [[ 0,  1,  2,  3],
#  [ 4,  5,  6,  7],
#  [ 8,  9, 10, 11]]

# -1 自动推断
print(arr.reshape(3, -1))   # 3x4
print(arr.reshape(-1, 4))   # 3x4

# 多维
print(arr.reshape(2, 3, 2)) # 2x3x2
```

### 拼接

```python
import numpy as np

a = np.array([[1, 2], [3, 4]])
b = np.array([[5, 6], [7, 8]])

# 垂直拼接
print(np.vstack([a, b]))

# 水平拼接
print(np.hstack([a, b]))

# 通用 concat
print(np.concatenate([a, b], axis=0))  # 垂直
print(np.concatenate([a, b], axis=1))  # 水平
```

### 分割

```python
import numpy as np

arr = np.arange(12).reshape(3, 4)

# 平均分割
print(np.split(arr, 3, axis=0))  # 3 块

# 指定位置
print(np.split(arr, [1, 2], axis=1))
```

## 📊 数学函数

```python
import numpy as np

arr = np.array([1, 2, 3, 4])

# 三角函数
print(np.sin(arr))
print(np.cos(arr))
print(np.tan(arr))

# 指数对数
print(np.exp(arr))
print(np.log(arr))

# 舍入
print(np.round([1.4, 2.5, 3.6]))
print(np.floor([1.4, 2.5, 3.6]))
print(np.ceil([1.4, 2.5, 3.6]))

# 统计
arr = np.array([1, 5, 3, 8, 2, 7])
print(np.median(arr))     # 4.0
print(np.percentile(arr, 75))  # 75% 分位数
print(np.var(arr))        # 方差
print(np.std(arr))        # 标准差
```

## 🔢 线性代数

```python
import numpy as np

# 矩阵
A = np.array([[1, 2], [3, 4]])

# 求逆
A_inv = np.linalg.inv(A)

# 验证
print(A @ A_inv)  # [[1, 0], [0, 1]]

# 行列式
print(np.linalg.det(A))

# 解线性方程组 Ax = b
b = np.array([5, 11])
x = np.linalg.solve(A, b)
print(x)  # [1, 2]

# 特征值和特征向量
eigenvalues, eigenvectors = np.linalg.eig(A)
print(eigenvalues)

# 奇异值分解（SVD）
U, S, V = np.linalg.svd(A)
print(S)
```

## 📊 随机数

```python
import numpy as np

# 1. 简单随机
print(np.random.rand(3))        # 均匀分布 [0, 1)
print(np.random.randn(3))       # 标准正态分布
print(np.random.randint(0, 10, 5))  # [0, 10) 整数

# 2. 设置种子（可复现）
np.random.seed(42)
print(np.random.rand(3))

# 3. 高级随机
print(np.random.choice(["A", "B", "C"], size=10))  # 抽样
print(np.random.shuffle([1, 2, 3, 4, 5]))         # 原地打乱
```

## 🔢 向量化计算

```python
import numpy as np

# 1. 向量化替代循环
arr = np.arange(1_000_000)

# 慢：循环
result = np.zeros_like(arr)
for i in range(len(arr)):
    result[i] = arr[i] ** 2

# 快：向量化
result = arr ** 2

# 2. 矩阵运算
A = np.random.rand(1000, 1000)
B = np.random.rand(1000, 1000)
C = A @ B  # 矩阵乘法（NumPy 优化）

# 3. 通用函数（ufunc）
arr = np.array([1, 2, 3])
print(np.add(arr, 1))  # [2, 3, 4]
print(np.multiply(arr, 2))  # [2, 4, 6]
```

## 📊 实战：数据分析

```python
import numpy as np

# 模拟股票数据
np.random.seed(42)
prices = 100 + np.cumsum(np.random.randn(252) * 0.5)

# 计算日收益率
returns = np.diff(prices) / prices[:-1]

# 统计
print(f"平均收益率: {returns.mean():.4%}")
print(f"波动率: {returns.std():.4%}")
print(f"最大涨幅: {returns.max():.2%}")
print(f"最大跌幅: {returns.min():.2%}")

# 移动平均
window = 20
ma = np.convolve(prices, np.ones(window) / window, mode='valid')

# 累计收益
total_return = (prices[-1] / prices[0]) - 1
print(f"累计收益: {total_return:.2%}")
```

## 📊 与 pandas 配合

```python
import numpy as np
import pandas as pd

# NumPy → pandas
arr = np.random.rand(5, 3)
df = pd.DataFrame(arr, columns=["A", "B", "C"])
print(df)

# pandas → NumPy
arr_back = df.values
print(type(arr_back))  # <class 'numpy.ndarray'>

# pandas 底层使用 NumPy
print(df["A"].values)  # Series.values → NumPy array
```

## 🎯 总结

**NumPy 核心要点**：
- ✅ ndarray 是核心数据结构
- ✅ 向量化计算（比 Python 列表快 50-100x）
- ✅ 广播机制（不同形状数组运算）
- ✅ 线性代数（矩阵乘法、求逆、特征值）
- ✅ 随机数生成
- ✅ 与 pandas 深度集成
- ✅ 内存视图（避免复制）
- ✅ 通用函数（ufunc）
- ⚠️ dtype 注意（int64 / float64）
- ⚠️ 大数据用 Dask

**下一步：** [📈 Matplotlib 可视化](/07-data/matplotlib) — 数据可视化


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
