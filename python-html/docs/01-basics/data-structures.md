---
title: 数据结构
date: 2026-08-15  # date-auto-injected
---

# 📦 数据结构

> Python 内置 4 大数据结构：**list（列表）、tuple（元组）、dict（字典）、set（集合）**。理解它们的特性是 Python 编程的基础。

## 📋 List 列表

### 列表基础

```python
# 创建
fruits = ["apple", "banana", "cherry"]
nums = [1, 2, 3, 4, 5]
mixed = [1, "hello", 3.14, True]
empty = []
nested = [[1, 2], [3, 4]]

# 长度
print(len(fruits))  # 3

# 索引访问
print(fruits[0])     # 'apple'
print(fruits[-1])    # 'cherry'（最后一个）

# 切片
print(fruits[0:2])   # ['apple', 'banana']
print(fruits[::-1])  # 反转
```

### 列表方法

```python
fruits = ["apple", "banana"]

# 添加
fruits.append("cherry")        # 末尾添加
fruits.insert(0, "orange")     # 指定位置插入
fruits.extend(["grape", "kiwi"])  # 扩展

# 删除
fruits.remove("apple")         # 删除第一个匹配
popped = fruits.pop()          # 删除并返回最后一个
popped = fruits.pop(0)         # 删除并返回索引 0

# 查找
print(fruits.index("banana"))   # 1
print(fruits.count("apple"))    # 0

# 排序
fruits.sort()                  # 升序
fruits.sort(reverse=True)      # 降序
fruits.reverse()               # 反转

# 其他
fruits.clear()                 # 清空
copy = fruits.copy()           # 浅拷贝
```

### 列表推导式

```python
# 基本
squares = [x**2 for x in range(10)]

# 带条件
evens = [x for x in range(20) if x % 2 == 0]

# 嵌套循环
pairs = [(x, y) for x in [1, 2] for y in [3, 4]]
# [(1,3), (1,4), (2,3), (2,4)]

# 带函数
names = ['alice', 'bob']
upper = [n.upper() for n in names]
```

## 🔒 Tuple 元组

### 元组基础

```python
# 创建
point = (1, 2)
rgb = (255, 0, 0)
single = (1,)  # 单元素元组必须有逗号！
empty = ()

# 不可变（关键特性）
point[0] = 3  # TypeError: 'tuple' object does not support item assignment

# 解包
x, y = point
print(f"x={x}, y={y}")

# 多个返回值
def get_user():
    return ("Alice", 30, "alice@example.com")

name, age, email = get_user()
```

### 元组 vs 列表

| 特性 | list | tuple |
|------|------|-------|
| 可变 | ✅ | ❌ |
| 速度 | 较慢 | 较快 |
| 内存 | 较大 | 较小 |
| 用途 | 动态集合 | 不可变记录 |
| Hashable | ❌ | ✅ |

## 📖 Dict 字典

### 字典基础

```python
# 创建
user = {"name": "Alice", "age": 30, "city": "Beijing"}
empty = {}
from_dict = dict(name="Bob", age=25)

# 访问
print(user["name"])         # 'Alice'
print(user.get("age"))     # 30
print(user.get("email", "N/A"))  # 'N/A'（默认值）

# 修改
user["email"] = "alice@example.com"
user["age"] = 31

# 删除
del user["city"]
email = user.pop("email")
```

### 字典方法

```python
user = {"name": "Alice", "age": 30}

# 遍历
for key in user:
    print(key, user[key])

for key, value in user.items():
    print(f"{key}: {value}")

# 视图对象
keys = user.keys()      # dict_keys(['name', 'age'])
values = user.values()  # dict_values(['Alice', 30])
items = user.items()    # dict_items([...])

# 其他
user2 = user.copy()             # 浅拷贝
user.update({"city": "BJ", "age": 31})  # 合并
user.clear()                    # 清空
print("name" in user)           # True（成员检查）
print(len(user))                # 2
```

### 字典推导式

```python
# 基本
squares = {x: x**2 for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# 反转字典
user = {"name": "Alice", "age": 30}
inverted = {v: k for k, v in user.items()}
# {'Alice': 'name', 30: 'age'}

# 过滤
scores = {"Alice": 85, "Bob": 92, "Carol": 78}
passed = {k: v for k, v in scores.items() if v >= 80}
# {'Alice': 85, 'Bob': 92}
```

## 🎯 Set 集合

### 集合基础

```python
# 创建
fruits = {"apple", "banana", "cherry"}
nums = set([1, 2, 2, 3, 3])  # {1, 2, 3}（自动去重）
empty = set()

# 集合操作
fruits.add("date")
fruits.remove("apple")          # KeyError
fruits.discard("apple")        # 不存在不报错
fruits.pop()                   # 随机移除
fruits.clear()
```

### 集合运算

```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

# 并集
print(a | b)         # {1, 2, 3, 4, 5, 6}
print(a.union(b))

# 交集
print(a & b)         # {3, 4}
print(a.intersection(b))

# 差集
print(a - b)         # {1, 2}
print(a.difference(b))

# 对称差
print(a ^ b)         # {1, 2, 5, 6}
print(a.symmetric_difference(b))

# 子集 / 超集
print({1, 2} <= {1, 2, 3})   # True（子集）
print({1, 2, 3} >= {1, 2})  # True（超集）
```

## 🔄 嵌套结构

```python
# 列表套字典
users = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25}
]

# 字典套列表
groups = {
    "admins": ["alice", "bob"],
    "users": ["carol", "dave"]
}

# 复杂嵌套
data = {
    "users": [
        {"name": "Alice", "scores": [85, 92, 78]}
    ]
}
print(data["users"][0]["scores"][1])  # 92
```

## 📊 性能对比

```python
import time

n = 1_000_000

# list 查找
lst = list(range(n))
start = time.time()
999_999 in lst
print(f"list: {time.time() - start:.6f}s")  # 慢

# set 查找
s = set(range(n))
start = time.time()
999_999 in s
print(f"set: {time.time() - start:.6f}s")   # 极快

# dict 查找
d = {i: i for i in range(n)}
start = time.time()
999_999 in d
print(f"dict: {time.time() - start:.6f}s")  # 极快
```

| 操作 | list | tuple | set | dict |
|------|------|-------|-----|------|
| 索引访问 | O(1) | O(1) | ❌ | ❌ |
| 查找 | O(n) | O(n) | O(1) | O(1) |
| 添加 | O(1) | ❌ | O(1) | O(1) |
| 删除 | O(n) | ❌ | O(1) | O(1) |
| 内存 | 大 | 小 | 中 | 中 |

## 🛠️ 选择指南

```
✅ 需要可变序列 → list
✅ 不可变记录 → tuple
✅ 快速查找 / 去重 → set
✅ 键值对映射 → dict

✅ 复合结构：
  - 列表套字典（数据列表）
  - 字典套列表（分组）
```

## 🎯 总结

**数据结构核心要点**：
- ✅ list：可变有序序列
- ✅ tuple：不可变有序序列
- ✅ dict：键值对映射（O(1) 查找）
- ✅ set：无序不重复（O(1) 查找）
- ✅ 列表推导式、字典推导式
- ✅ 集合运算（并、交、差、对称差）
- ⚠️ 列表查找慢（大数据用 set/dict）
- ⚠️ tuple 是不可变的（Key 用 tuple）

**下一步：** [🔁 控制流](/01-basics/control-flow) — if/else/for/while
