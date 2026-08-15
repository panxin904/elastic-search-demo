---
title: 内存管理
---

# 🗑️ 内存管理

> Python 的**内存管理**由**引用计数**和**垃圾回收（GC）**共同完成。理解内存管理是**避免内存泄漏、优化内存占用**的关键。

## 🎯 Python 内存管理三件套

```
1. 引用计数（Reference Counting）
   - 每个对象记录被引用次数
   - 计数为 0 时立即释放内存
   - 简单高效

2. 垃圾回收（GC，Generational）
   - 处理循环引用（引用计数无解）
   - 分代收集（减少扫描开销）

3. 内存池（Memory Pool / Arena）
   - 小对象预分配池
   - 减少系统调用
```

## 📊 引用计数（核心机制）

### 原理

```
每个 Python 对象内部维护一个计数器（ob_refcnt）：
  - 引用 +1（如赋值、传参）
  - 引用 -1（如变量超出作用域、del）
  - 计数归 0 → 立即释放内存

优点：实时、精确
缺点：不能处理循环引用
```

### 示例

```python
import sys

a = [1, 2, 3]     # refcount = 1
b = a              # refcount = 2
c = a              # refcount = 3
print(sys.getrefcount(a))  # 4（getrefcount 本身也引用）

del b              # refcount = 2
del c              # refcount = 1
del a              # refcount = 0 → 释放内存
```

### 引用计数变化

```python
# 增加引用
x = [1, 2, 3]      # +1
y = x               # +1
func(x)             # +1（函数参数），返回后 -1
lst.append(x)       # +1（容器持有）
# 共 4 个引用

# 减少引用
del y               # -1
x = None            # -1
# 对象释放（refcount = 0）
```

### sys.getrefcount

```python
import sys

a = "hello"
print(sys.getrefcount(a))  # 2（a + getrefcount 参数）

# 小整数（缓存）
n = 100
print(sys.getrefcount(n))  # 多个（缓存共享）

# 短字符串（intern）
s = "python"
print(sys.getrefcount(s))  # 多个（intern）
```

## 🗑️ 垃圾回收（GC）

### 为什么需要 GC？

```python
# 循环引用（引用计数无解）
a = []
b = []
a.append(b)  # b 引用 +1
b.append(a)  # a 引用 +1
del a          # a 引用 -1（但 b 还引用 a）
del b          # b 引用 -1（但 a 还引用 b）
# 引用计数都不为 0，但实际已无法访问
# 引用计数无法回收！
```

### CPython 的 GC 解决方案

```c
// CPython 的分代 GC
typedef struct _gc_generation {
    PyObject_HEAD
    PyObject *gc_list;        // 对象链表
    int threshold;             // 触发阈值
    int count;                 // 上次扫描后新增数
} gc_generation[NUM_GENERATIONS];
```

### 三个代（Generations）

```python
import gc

# 获取分代信息
print(gc.get_threshold())
# (700, 10, 10)  # 0代阈值700，1代阈值10，0代10次触发1代扫描
# - 0代（新对象）
# - 1代（经历1次GC的对象）
# - 2代（长期存活对象）
```

### 手动 GC

```python
import gc

# 启用 / 禁用 GC
gc.enable()
gc.disable()

# 强制 GC
gc.collect()           # 回收所有代
gc.collect(0)          # 只回收 0代
gc.collect(1)          # 回收 0代 + 1代
gc.collect(2)          # 回收所有代

# 统计
print(gc.get_stats())
# [{'collected': 0, 'uncollectable': 0, 'collections': 0}, ...]
```

### 查看循环引用

```python
import gc

class Node:
    def __init__(self, name):
        self.name = name
        self.next = None

# 创建循环引用
a = Node("A")
b = Node("B")
a.next = b
b.next = a

# 触发 GC
del a, b
collected = gc.collect()
print(f"回收了 {collected} 个对象")
```

## 📦 内存池（Memory Pool）

### 小对象池

```
CPython 对小对象（≤ 512 字节）使用内存池：
  - 减少系统调用（malloc/free）
  - 提高分配速度
  - 减少内存碎片

大对象（> 512 字节）：直接 malloc
```

### 内存管理层次

```
┌──────────────────────────────────┐
│  Arena（256 KB）                    │
│  ┌────────────────────────────┐  │
│  │ Pool（4 KB = 多个 Block）     │  │
│  │  ┌──────┬──────┬──────┐    │  │
│  │  │Block │Block │Block │    │  │
│  │  │ 16B  │ 32B  │ 64B  │    │  │
│  │  └──────┴──────┴──────┘    │  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘
```

## 📊 内存监控

### sys.getsizeof

```python
import sys

# 基本类型
print(sys.getsizeof(0))         # 24
print(sys.getsizeof("hello"))    # 54
print(sys.getsizeof([]))         # 56
print(sys.getsizeof({}))         # 64

# 容器大小（不含元素）
print(sys.getsizeof([1, 2, 3]))  # 88（不含元素 24 字节）
# 实际内存：88 + 3 * 28 = 172
```

### objgraph（第三方）

```bash
pip install objgraph
```

```python
import objgraph

# 显示前 N 个对象
objgraph.show_most_common_types(limit=10)

# 显示特定类型的对象
objgraph.by_type('dict')

# 显示引用链
objgraph.show_refs([an_object], filename='refs.png')

# 显示反向引用
objgraph.show_backrefs([an_object], filename='backrefs.png')

# 查找内存泄漏
objgraph.show_growth()
```

### tracemalloc（标准库）

```python
import tracemalloc

# 开始追踪
tracemalloc.start()

# 程序代码
data = [i for i in range(100000)]
d = {x: x for x in range(100000)}

# 拍摄快照
snapshot1 = tracemalloc.take_snapshot()

# 更多代码
data2 = [i for i in range(200000)]

# 第二张快照
snapshot2 = tracemalloc.take_snapshot()

# 比较快照
top_stats = snapshot2.compare_to(snapshot1, 'lineno')
for stat in top_stats[:10]:
    print(stat)
```

## 🛠️ 优化内存

### 1. 使用 __slots__

```python
# 默认情况：每个实例有 __dict__
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
print(sys.getsizeof(p))  # 56 + __dict__ 大小

# 使用 __slots__：节省内存
class Point:
    __slots__ = ('x', 'y')
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
print(sys.getsizeof(p))  # 56（无 __dict__）
```

### 2. 避免大对象

```python
# 慢：逐行读取
with open("big.txt") as f:
    lines = f.readlines()  # 一次性读入

# 快：迭代器
with open("big.txt") as f:
    for line in f:  # 逐行迭代
        process(line)
```

### 3. 使用生成器

```python
# 慢：列表推导式（一次性生成所有）
squares = [x**2 for x in range(1_000_000)]

# 快：生成器（惰性求值）
squares = (x**2 for x in range(1_000_000))
```

### 4. 弱引用

```python
import weakref

class BigObject:
    def __init__(self, data):
        self.data = data

# 普通引用
obj = BigObject("huge data")
ref = obj  # refcount +1

# 弱引用（不增加 refcount）
weak = weakref.ref(obj)
print(weak())  # <__main__.BigObject object>

del obj
print(weak())  # None（自动清理）
```

## 🚨 内存泄漏排查

### 常见内存泄漏场景

```python
# 1. 全局列表累积
cache = []
def process(data):
    cache.append(data)  # 永远不释放！

# 2. 闭包引用
def create_handler():
    big_data = load_huge_data()
    def handler():
        return big_data
    return handler  # big_data 永远不释放
```

### 排查方法

```python
import tracemalloc

tracemalloc.start()

# 业务代码
# ...

snapshot = tracemalloc.take_snapshot()
for stat in snapshot.statistics("lineno")[:10]:
    print(stat)
# 显示占用内存最多的代码位置
```

## 🎯 总结

**Python 内存管理核心要点**：
- ✅ 引用计数：实时、精确、不能处理循环引用
- ✅ 垃圾回收：处理循环引用、分代收集
- ✅ 内存池：小对象预分配，提高效率
- ✅ `__slots__` 节省内存
- ✅ 生成器避免一次性加载
- ✅ 弱引用避免循环引用
- ✅ tracemalloc 监控内存
- ⚠️ 循环引用需 GC 回收
- ⚠️ 大对象需手动管理

**下一步：** [⏱️ GIL 全局锁](/02-principles/gil) — Python 多线程的限制
