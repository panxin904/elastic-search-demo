---
title: 复杂度分析
date: 2026-08-15  # date-auto-injected
---

# 📐 复杂度分析

> **算法复杂度**是衡量算法**时间和空间**效率的标尺。本章讲解 **Big O 记号**和常见复杂度。

## 🎯 Big O 记号

```
Big O 记号表示算法的**上界**，即最坏情况下的复杂度。
忽略常数项和低阶项，只关注最高阶的增长率。
```

### 常见复杂度（从优到劣）

| 复杂度 | 名称 | 描述 | 示例 |
|--------|------|------|------|
| O(1) | 常数 | 与输入无关 | 数组索引 |
| O(log n) | 对数 | 每次减半 | 二分查找 |
| O(n) | 线性 | 与输入成正比 | 遍历数组 |
| O(n log n) | 线性对数 | 主流高效排序 | 快速排序 |
| O(n²) | 平方 | 嵌套循环 | 冒泡排序 |
| O(n³) | 立方 | 三层循环 | 矩阵乘法（朴素） |
| O(2ⁿ) | 指数 | 每次翻倍 | 斐波那契（递归） |
| O(n!) | 阶乘 | 排列枚举 | 旅行商（暴力） |

### 复杂度增长趋势

```python
import matplotlib.pyplot as plt
import numpy as np

n = np.arange(1, 11)

complexities = {
    "O(1)":        np.ones_like(n),
    "O(log n)":     np.log2(n),
    "O(n)":        n,
    "O(n log n)":  n * np.log2(n),
    "O(n²)":       n ** 2,
    "O(n³)":       n ** 3,
    "O(2ⁿ)":       2 ** n,
}

plt.figure(figsize=(10, 6))
for label, values in complexities.items():
    plt.plot(n, values, marker='o', label=label)
plt.yscale('log')
plt.xlabel("n (输入规模)")
plt.ylabel("操作数（对数）")
plt.title("算法复杂度对比")
plt.legend()
plt.grid(True)
plt.show()
```

## 📊 时间复杂度分析

### 循环

```python
# O(1) - 常数
def get_first(arr):
    return arr[0]

# O(n) - 线性
def find_max(arr):
    max_val = arr[0]
    for x in arr:        # n 次
        if x > max_val:
            max_val = x
    return max_val

# O(n²) - 平方
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):       # n 次
        for j in range(n-i-1):  # n 次
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]

# O(log n) - 对数
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:           # log n 次
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

### 递归

```python
# O(log n) - 二分查找
def binary_search_recursive(arr, target, lo, hi):
    if lo > hi:
        return -1
    mid = (lo + hi) // 2
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid+1, hi)
    else:
        return binary_search_recursive(arr, target, lo, mid-1)

# O(2ⁿ) - 斐波那契（朴素递归）
def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)

# O(n) - 斐波那契（记忆化）
def fib_memo(n, memo={}):
    if n < 2:
        return n
    if n not in memo:
        memo[n] = fib_memo(n-1, memo) + fib_memo(n-2, memo)
    return memo[n]

# O(n) - 斐波那契（迭代）
def fib_iter(n):
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(n-1):
        a, b = b, a + b
    return b
```

## 📊 空间复杂度分析

```python
# O(1) - 常数空间
def swap(a, b):
    a, b = b, a  # 只用两个变量

# O(n) - 线性空间
def copy_list(lst):
    return lst.copy()  # 新列表长度 n

# O(n) - 递归调用栈
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)  # 递归 n 层

# O(n) - 哈希表
def two_sum(nums, target):
    seen = {}  # 哈希表最多 n 个
    for i, n in enumerate(nums):
        if target - n in seen:
            return [seen[target - n], i]
        seen[n] = i
```

## 📊 摊销分析

```python
# 动态数组（list）
# 添加元素：偶尔 O(n)，平时 O(1)
# 摊销 O(1)

# Python list 实现
import sys

# 初始空列表
lst = []
print(f"初始大小: {sys.getsizeof(lst)} 字节")

# 不断 append
for i in range(100):
    lst.append(i)
print(f"100 元素后: {sys.getsizeof(lst)} 字节")
# 容量翻倍策略
```

## 📊 常见数据结构操作复杂度

| 数据结构 | 访问 | 查找 | 插入 | 删除 |
|---------|------|------|------|------|
| 数组 | O(1) | O(n) | O(n) | O(n) |
| 链表 | O(n) | O(n) | O(1) | O(1) |
| 栈 | O(n) | O(n) | O(1) | O(1) |
| 队列 | O(n) | O(n) | O(1) | O(1) |
| 哈希表 | - | O(1) | O(1) | O(1) |
| 二叉搜索树 | O(log n) | O(log n) | O(log n) | O(log n) |
| 平衡 BST | O(log n) | O(log n) | O(log n) | O(log n) |
| 堆 | O(1) | O(n) | O(log n) | O(log n) |
| 跳表 | O(log n) | O(log n) | O(log n) | O(log n) |
| 红黑树 | O(log n) | O(log n) | O(log n) | O(log n) |

## 📊 算法复杂度速查

| 算法 | 时间 | 空间 |
|------|------|------|
| 二分查找 | O(log n) | O(1) |
| 顺序查找 | O(n) | O(1) |
| 冒泡排序 | O(n²) | O(1) |
| 快速排序 | O(n log n) 平均 | O(log n) |
| 归并排序 | O(n log n) | O(n) |
| 堆排序 | O(n log n) | O(1) |
| 计数排序 | O(n + k) | O(k) |
| 基数排序 | O(n × k) | O(n + k) |
| 拓扑排序 | O(V + E) | O(V) |
| Dijkstra | O((V+E) log V) | O(V) |
| Bellman-Ford | O(V × E) | O(V) |
| Floyd | O(V³) | O(V²) |
| DFS / BFS | O(V + E) | O(V) |

## 🛠️ 实战：分析实际代码

### 示例 1：两数之和

```python
def two_sum_brute(nums, target):
    """O(n²) 时间，O(1) 空间"""
    n = len(nums)
    for i in range(n):
        for j in range(i+1, n):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []

def two_sum_hash(nums, target):
    """O(n) 时间，O(n) 空间"""
    seen = {}
    for i, n in enumerate(nums):
        if target - n in seen:
            return [seen[target - n], i]
        seen[n] = i
    return []
```

### 示例 2：斐波那契

```python
import time

def fib_recursive(n):
    """O(2ⁿ) 时间，O(n) 空间"""
    if n < 2: return n
    return fib_recursive(n-1) + fib_recursive(n-2)

def fib_memo(n, memo={}):
    """O(n) 时间，O(n) 空间"""
    if n < 2: return n
    if n not in memo:
        memo[n] = fib_memo(n-1, memo) + fib_memo(n-2, memo)
    return memo[n]

def fib_iter(n):
    """O(n) 时间，O(1) 空间"""
    if n < 2: return n
    a, b = 0, 1
    for _ in range(n-1):
        a, b = b, a + b
    return b

# 性能测试
for n in [20, 30, 40]:
    start = time.time()
    fib_iter(n)
    print(f"n={n}: {time.time() - start:.6f}s")
```

## 🛠️ 面试技巧

### 1. 先给出暴力解

```
✅ 总是先给最简单但可能慢的解（O(n²) 或 O(n³)）
✅ 证明正确性
✅ 分析时间/空间复杂度
✅ 优化到最优
```

### 2. 优化思路

```
优化方向：
  - 减少重复计算（记忆化 / 哈希表）
  - 改变数据结构（O(n²) → O(n)）
  - 改变算法（O(n²) → O(n log n)）
  - 分治 / 贪心 / 动态规划
```

### 3. 时间 vs 空间权衡

```
以空间换时间：哈希表、记忆化
以时间换空间：流式算法
```

## 🎯 总结

**复杂度分析核心要点**：
- ✅ Big O 表示最坏情况
- ✅ 忽略常数和低阶项
- ✅ 常见复杂度：O(1) / O(log n) / O(n) / O(n log n) / O(n²) / O(2ⁿ)
- ✅ 时间复杂度（执行步骤数）
- ✅ 空间复杂度（额外内存）
- ✅ 摊销分析（动态数组）
- ✅ 数据结构操作复杂度
- ✅ 面试先给暴力，再优化
- ⚠️ Big O 是上界（不是平均值）

**下一步：** [📚 内置数据结构](/08-algorithms/builtin) — list/dict/set 复杂度
