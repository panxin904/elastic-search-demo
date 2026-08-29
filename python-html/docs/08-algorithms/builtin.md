---
title: 内置数据结构
date: 2026-08-15  # date-auto-injected
---

# 📚 内置数据结构

> Python 内置数据结构是**所有算法的基础**。理解它们的时间和空间复杂度是写出高效代码的前提。

## 🎯 列表（list）

```python
# 1. 创建
lst = [1, 2, 3, 4, 5]
lst = list(range(10))
lst = [0] * 100  # 100 个 0
lst = list("hello")  # ['h', 'e', 'l', 'l', 'o']

# 2. 基本操作
lst.append(6)       # O(1) 摊销
lst.insert(0, 0)    # O(n)
lst.pop()           # O(1)
lst.pop(0)          # O(n)

# 3. 访问
first = lst[0]      # O(1)
last = lst[-1]       # O(1)
sub = lst[1:4]       # O(k) k=切片长度

# 4. 查找
index = lst.index(3)  # O(n)
count = lst.count(3)  # O(n)
exists = 3 in lst      # O(n)

# 5. 排序
lst.sort()           # O(n log n) - 原地
new_lst = sorted(lst) # O(n log n) - 新列表
lst.reverse()        # O(n)
```

### 列表实现原理

```python
# CPython 列表是动态数组
# - 维护一个指针数组（PyObject **ob_item）
# - 容量不足时扩容（通常是 1.125 倍）
# - append 平均 O(1)，偶尔 O(n)
# - insert/pop 中间 O(n)

import sys

lst = []
sizes = []
for i in range(20):
    lst.append(i)
    sizes.append(sys.getsizeof(lst))

# 观察容量增长
for i, s in enumerate(sizes):
    print(f"len={i+1}: size={s} bytes")
```

### 列表推导式（高效）

```python
# 慢：循环 + append
result = []
for x in range(10):
    result.append(x ** 2)

# 快：列表推导式
result = [x ** 2 for x in range(10)]

# 含条件
result = [x for x in range(10) if x % 2 == 0]

# 嵌套
matrix = [[i*3 + j for j in range(3)] for i in range(3)]
```

## 🔒 元组（tuple）

```python
# 不可变序列
t = (1, 2, 3)
t = 1, 2, 3  # 不带括号也行
t = (1,)      # 单元素必须带逗号

# 不可变
t[0] = 10  # TypeError

# 操作
len(t)          # O(1)
t[0]            # O(1)
t[1:3]          # O(k)
t + (4, 5)     # O(n)
t * 3           # O(n)
1 in t          # O(n)

# 命名元组
from collections import namedtuple
Point = namedtuple("Point", ["x", "y"])
p = Point(1, 2)
print(p.x, p.y)
print(p[0], p[1])
```

## 📖 字典（dict）

```python
# 1. 创建
d = {"name": "Alice", "age": 30}
d = dict(name="Alice", age=30)
d = {k: v for k, v in [("a", 1), ("b", 2)]}

# 2. 操作（平均 O(1)）
d["key"] = "value"          # O(1) 摊销
del d["key"]                # O(1)
d.get("key", default=None)  # O(1)

# 3. 访问
keys = d.keys()        # 视图
values = d.values()    # 视图
items = d.items()      # 视图

# 4. 遍历
for k, v in d.items():
    print(k, v)

# 5. 合并
d1 = {"a": 1}
d2 = {"b": 2}
d1.update(d2)  # {'a': 1, 'b': 2}
{**d1, **d2}  # 同上
```

### dict 实现原理

```python
# CPython dict 是开放寻址哈希表
# - 初始大小 8
# - 元素 > 2/3 时扩容（2 倍）
# - 平均 O(1) 操作

import sys

d = {}
sizes = []
for i in range(20):
    d[i] = i
    sizes.append(sys.getsizeof(d))

# 观察 dict 大小变化
for i, s in enumerate(sizes):
    print(f"len={i+1}: size={s} bytes")
```

### defaultdict

```python
from collections import defaultdict

# 默认值字典
dd = defaultdict(int)        # 默认 0
dd["a"] += 1                # 第一次返回 0，加 1 = 1
print(dd)                    # {'a': 1}

dd = defaultdict(list)       # 默认 []
dd["fruits"].append("apple")
print(dd)                    # {'fruits': ['apple']}
```

## 🎯 集合（set）

```python
# 1. 创建
s = {1, 2, 3}
s = set([1, 2, 3])
s = {x for x in range(10)}

# 2. 操作（平均 O(1)）
s.add(4)            # O(1)
s.remove(3)         # O(1) - 不存在报错
s.discard(3)       # O(1) - 不存在不报错
s.pop()             # O(1)

# 3. 集合运算
a = {1, 2, 3}
b = {3, 4, 5}
print(a | b)   # {1, 2, 3, 4, 5} 并集
print(a & b)   # {3} 交集
print(a - b)   # {1, 2} 差集
print(a ^ b)   # {1, 2, 4, 5} 对称差

# 4. 关系
print(a.issubset(b))      # False
print(a.isdisjoint(b))    # False
print(a.issuperset(b))    # False

# 5. 不可变集合（可作为 dict key / set 元素）
fs = frozenset([1, 2, 3])
```

## 📚 collections 模块

```python
from collections import (
    Counter, defaultdict, OrderedDict,
    deque, namedtuple, ChainMap
)

# 1. Counter：计数器
c = Counter(["apple", "banana", "apple", "cherry", "apple"])
print(c)
# Counter({'apple': 3, 'banana': 1, 'cherry': 1})
print(c.most_common(2))  # [('apple', 3), ('banana', 1)]

# 2. defaultdict：默认值字典
dd = defaultdict(int)
dd["x"] += 1

# 3. OrderedDict：有序字典（Python 3.7+ 普通 dict 也保序）
od = OrderedDict()
od["a"] = 1
od["b"] = 2
od.move_to_end("a")  # 移到末尾

# 4. deque：双端队列
dq = deque([1, 2, 3])
dq.append(4)        # O(1) 右侧
dq.appendleft(0)    # O(1) 左侧
dq.pop()            # O(1)
dq.popleft()        # O(1)
dq.rotate(1)        # 旋转
dq.maxlen = 100     # 限制长度

# 5. namedtuple：命名元组
Point = namedtuple("Point", ["x", "y"])
p = Point(1, 2)

# 6. ChainMap：多个字典
d1 = {"a": 1}
d2 = {"b": 2}
cm = ChainMap(d1, d2)  # 优先 d1
print(cm["a"], cm["b"])
```

## 📊 性能对比

```python
import time
import random

n = 100_000
data = [random.randint(0, n) for _ in range(n)]

# 1. list vs set vs dict 查找
lst = list(data)
st = set(data)
d = {x: True for x in data}

target = data[n // 2]

# list 查找 O(n)
start = time.time()
for _ in range(1000):
    target in lst
print(f"list: {(time.time() - start):.4f}s")

# set 查找 O(1)
start = time.time()
for _ in range(1000):
    target in st
print(f"set: {(time.time() - start):.4f}s")

# dict 查找 O(1)
start = time.time()
for _ in range(1000):
    target in d
print(f"dict: {(time.time() - start):.4f}s")
# dict 和 set 快 list 数十倍
```

## 📊 实战：选择正确的数据结构

```python
# 场景 1：去重
items = [1, 2, 2, 3, 3, 3]
unique = list(set(items))  # O(n)，快
unique = list(dict.fromkeys(items))  # 保持顺序
# Python 3.7+ dict 保序

# 场景 2：统计频次
words = ["apple", "banana", "apple", "cherry", "apple"]
from collections import Counter
freq = Counter(words)  # O(n)

# 场景 3：查找
# ❌ list 查找 O(n)
# ✅ set/dict 查找 O(1)
needles = [1, 5, 10]
haystack = set(data)  # 转 set
for n in needles:
    if n in haystack:  # O(1)
        print("Found")

# 场景 4：最近使用的项
from collections import OrderedDict
cache = OrderedDict()
def get(key):
    if key in cache:
        cache.move_to_end(key)
    cache[key] = value
    return cache[key]

# 场景 5：队列（生产者-消费者）
from collections import deque
queue = deque()
queue.append(item)   # 右侧入队
item = queue.popleft()  # 左侧出队
```

## 📊 不可变数据结构

```python
# tuple, frozenset 是不可变的
# 可作为 dict key / set 元素

# 1. 嵌套元组（可哈希）
key = (("user", 1), ("order", 100))  # OK

# 2. 列表不可哈希
# {(1, 2, [3, 4])}  # TypeError: unhashable type: 'list'

# 3. 自定义 __hash__
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

p = Point(1, 2)
print(hash(p))  # 可哈希
d = {p: "origin"}  # 可作为 dict key
```

## 📊 堆（heapq）

```python
import heapq

# 堆是特殊队列（最小/最大优先）
heap = [3, 1, 4, 1, 5, 9, 2, 6]

# 堆化（O(n)）
heapq.heapify(heap)
print(heap)  # [1, 1, 2, 3, 5, 9, 4, 6]

# 弹出最小（O(log n)）
smallest = heapq.heappop(heap)
print(smallest)  # 1

# 推入（O(log n)）
heapq.heappush(heap, 0)

# 最大 k 个
nums = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
print(heapq.nlargest(3, nums))  # [9, 6, 5]
print(heapq.nsmallest(3, nums))  # [1, 1, 2]

# 优先队列
class Task:
    def __init__(self, priority, name):
        self.priority = priority
        self.name = name
    def __lt__(self, other):
        return self.priority < other.priority

pq = []
heapq.heappush(pq, Task(3, "low"))
heapq.heappush(pq, Task(1, "high"))
heapq.heappush(pq, Task(2, "medium"))

while pq:
    t = heapq.heappop(pq)
    print(f"{t.priority}: {t.name}")
```

## 🎯 总结

**内置数据结构核心要点**：
- ✅ list：动态数组，O(1) append，O(n) 中间插入
- ✅ tuple：不可变序列，可哈希
- ✅ dict：哈希表实现，O(1) 平均操作
- ✅ set：哈希表实现，O(1) 平均操作
- ✅ Counter：计数器
- ✅ defaultdict：默认值字典
- ✅ deque：双端队列
- ✅ heapq：堆排序
- ⚠️ list 中间插入是 O(n)
- ⚠️ 选择合适数据结构（O(1) vs O(n) 性能差 100x）

**下一步：** [🔍 排序算法](/08-algorithms/sort) — 算法可视化


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
