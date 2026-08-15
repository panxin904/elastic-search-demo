---
title: 排序算法
---

# 🔍 排序算法

> 排序是**最经典的算法问题**。本章用可视化详解 6 种主流排序算法。

## 🎯 排序算法对比

| 算法 | 平均 | 最坏 | 空间 | 稳定 | 适用 |
|------|------|------|------|------|------|
| 冒泡排序 | O(n²) | O(n²) | O(1) | ✅ | 教学 |
| 选择排序 | O(n²) | O(n²) | O(1) | ❌ | 教学 |
| 插入排序 | O(n²) | O(n²) | O(1) | ✅ | 小数据 |
| 希尔排序 | O(n log²n) | O(n²) | O(1) | ❌ | 中等数据 |
| 快速排序 | O(n log n) | O(n²) | O(log n) | ❌ | 通用 |
| 归并排序 | O(n log n) | O(n log n) | O(n) | ✅ | 大数据 |
| 堆排序 | O(n log n) | O(n log n) | O(1) | ❌ | 大数据 |
| 计数排序 | O(n + k) | O(n + k) | O(k) | ✅ | 整数 |

## 🔍 冒泡排序

<ClientOnly>
  <SortVisualizer algorithm="bubble" />
</ClientOnly>

### 算法

```python
def bubble_sort(arr):
    """O(n²) 时间，O(1) 空间，稳定"""
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:  # 优化：没有交换说明已排序
            break
    return arr

# 使用
arr = [64, 34, 25, 12, 22, 11, 90]
print(bubble_sort(arr))
```

### 优化

```python
def bubble_sort_optimized(arr):
    """O(n²) 最坏，O(n) 最好（已排序）"""
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr
```

## 🔍 选择排序

<ClientOnly>
  <SortVisualizer algorithm="selection" />
</ClientOnly>

### 算法

```python
def selection_sort(arr):
    """O(n²) 时间，O(1) 空间，不稳定"""
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr
```

## 🔍 插入排序

<ClientOnly>
  <SortVisualizer algorithm="insertion" />
</ClientOnly>

### 算法

```python
def insertion_sort(arr):
    """O(n²) 时间，O(1) 空间，稳定"""
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr
```

### 优势

- ✅ 对**近乎有序**的数据是 O(n)
- ✅ 稳定排序
- ✅ 在线算法（可边接收边排序）

## 🔍 希尔排序

### 算法

```python
def shell_sort(arr):
    """O(n log²n) 平均"""
    n = len(arr)
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = arr[i]
            j = i
            while j >= gap and arr[j - gap] > temp:
                arr[j] = arr[j - gap]
                j -= gap
            arr[j] = temp
        gap //= 2
    return arr
```

## 🔍 快速排序

<ClientOnly>
  <SortVisualizer algorithm="quick" />
</ClientOnly>

### 算法（标准）

```python
def quick_sort(arr, lo=0, hi=None):
    """O(n log n) 平均，O(n²) 最坏"""
    if hi is None:
        hi = len(arr) - 1
    if lo < hi:
        p = partition(arr, lo, hi)
        quick_sort(arr, lo, p - 1)
        quick_sort(arr, p + 1, hi)
    return arr

def partition(arr, lo, hi):
    """Lomuto 分区"""
    pivot = arr[hi]
    i = lo - 1
    for j in range(lo, hi):
        if arr[j] < pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
    return i + 1
```

### 三路快排

```python
def quick_sort_3way(arr, lo=0, hi=None):
    """处理大量重复元素"""
    if hi is None:
        hi = len(arr) - 1
    if lo >= hi:
        return
    
    lt, gt = lo, hi
    pivot = arr[lo]
    i = lo
    while i <= gt:
        if arr[i] < pivot:
            arr[lt], arr[i] = arr[i], arr[lt]
            lt += 1
            i += 1
        elif arr[i] > pivot:
            arr[gt], arr[i] = arr[i], arr[gt]
            gt -= 1
        else:
            i += 1
    
    quick_sort_3way(arr, lo, lt - 1)
    quick_sort_3way(arr, gt + 1, hi)
```

## 🔍 归并排序

<ClientOnly>
  <SortVisualizer algorithm="merge" />
</ClientOnly>

### 算法

```python
def merge_sort(arr):
    """O(n log n) 时间，O(n) 空间，稳定"""
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```

### 自底向上（迭代版）

```python
def merge_sort_iterative(arr):
    n = len(arr)
    size = 1
    while size < n:
        for lo in range(0, n - size, 2 * size):
            mid = lo + size
            hi = min(lo + 2 * size, n)
            arr[lo:hi] = merge(arr[lo:mid], arr[mid:hi])
        size *= 2
    return arr
```

## 🔍 堆排序

### 算法

```python
import heapq

def heap_sort(arr):
    """O(n log n) 时间，O(1) 空间，不稳定"""
    n = len(arr)
    # 1. 构建大顶堆
    for i in range(n // 2 - 1, -1, -1):
        sift_down(arr, i, n)
    
    # 2. 逐个取出
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        sift_down(arr, 0, i)
    return arr

def sift_down(arr, start, end):
    root = start
    while True:
        child = 2 * root + 1
        if child >= end:
            break
        if child + 1 < end and arr[child] < arr[child + 1]:
            child += 1
        if arr[root] < arr[child]:
            arr[root], arr[child] = arr[child], arr[root]
            root = child
        else:
            break
```

## 🔍 计数排序（O(n) 极限）

```python
def counting_sort(arr):
    """O(n + k) 时间，O(k) 空间，稳定"""
    if not arr:
        return arr
    
    # 找范围
    min_val, max_val = min(arr), max(arr)
    k = max_val - min_val + 1
    
    # 计数
    count = [0] * k
    for x in arr:
        count[x - min_val] += 1
    
    # 累加
    for i in range(1, k):
        count[i] += count[i - 1]
    
    # 输出
    output = [0] * len(arr)
    for x in reversed(arr):
        output[count[x - min_val] - 1] = x
        count[x - min_val] -= 1
    
    return output
```

## 📊 Python 内置排序

```python
# Python list.sort() 和 sorted() 是 Timsort
# - 时间：O(n log n) 最坏，O(n) 最好
# - 空间：O(n)
# - 稳定

# 使用
arr = [3, 1, 4, 1, 5, 9, 2, 6]
arr.sort()                # 原地排序
sorted_arr = sorted(arr)  # 返回新列表

# 自定义排序
students = [
    {"name": "Alice", "age": 30, "score": 85},
    {"name": "Bob", "age": 25, "score": 92},
    {"name": "Carol", "age": 28, "score": 78}
]
students.sort(key=lambda s: s["score"], reverse=True)

# 多键排序
students.sort(key=lambda s: (-s["score"], s["age"]))

# 稳定排序
arr = [(1, "a"), (1, "b"), (0, "c")]
arr.sort(key=lambda x: x[0])  # 按第一键排序，相同保持原顺序
```

## 📊 性能测试

```python
import random
import time

def benchmark(sort_func, n=10000):
    arr = [random.randint(0, n) for _ in range(n)]
    arr_copy = arr.copy()
    
    start = time.time()
    sort_func(arr_copy)
    return time.time() - start

n = 10000
print(f"n = {n}")
print(f"冒泡排序: {benchmark(bubble_sort, n):.4f}s")      # 慢
print(f"选择排序: {benchmark(selection_sort, n):.4f}s")
print(f"插入排序: {benchmark(insertion_sort, n):.4f}s")
print(f"快速排序: {benchmark(quick_sort, n):.4f}s")        # 快
print(f"归并排序: {benchmark(merge_sort, n):.4f}s")
print(f"Python sort: {benchmark(lambda a: a.sort(), n):.4f}s")  # 最快
```

## 🎯 总结

**排序算法核心要点**：
- ✅ 冒泡 / 选择 / 插入：O(n²)，教学用
- ✅ 快速排序：O(n log n) 平均，通用
- ✅ 归并排序：O(n log n)，稳定
- ✅ 堆排序：O(n log n)，原地
- ✅ 计数排序：O(n + k)，整数数据
- ✅ Python sort：Timsort，O(n log n)
- ⚠️ 快速排序最坏 O(n²)（已排序数据）
- ⚠️ 选排序看数据特征（小数据用插入，大数据用快排/归并）

**下一步：** [🔎 搜索算法](/08-algorithms/search) — 二分 / DFS / BFS
