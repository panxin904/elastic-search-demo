---
title: 垃圾回收
date: 2026-08-15  # date-auto-injected
---

# 🔍 垃圾回收

> Python 的**垃圾回收（GC）**机制主要解决**循环引用**问题。理解 GC 是**避免内存泄漏**的关键。

## 🎯 引用计数的局限

```python
# 循环引用：引用计数无法处理
a = []
b = []
a.append(b)  # b 引用 +1
b.append(a)  # a 引用 +1
del a          # a 引用 -1（但 b 还引用 a）
del b          # b 引用 -1（但 a 还引用 b）
# 引用计数都不为 0，对象无法释放！
# → 内存泄漏
```

## 🛠️ CPython 的 GC 机制

### 分代收集（Generational GC）

```
核心思想：分代假说
  - 大多数对象生命周期很短（朝生夕死）
  - 存活越久的对象，越可能继续存活

三个代：
  - 0 代（新对象）
  - 1 代（经历 1 次 GC）
  - 2 代（长期存活对象）
```

### GC 阈值

```python
import gc

# 获取 GC 阈值
print(gc.get_threshold())
# (700, 10, 10)
# - 0 代阈值 700：每 700 次分配触发 0 代 GC
# - 1 代阈值 10：0 代 GC 10 次后触发 1 代 GC
# - 2 代阈值 10：1 代 GC 10 次后触发 2 代 GC
```

### GC 触发流程

```
分配新对象
   ↓
0 代对象数量 +1
   ↓
0 代对象数量 > 700（阈值）？
   ├─ 否 → 继续
   └─ 是 → 触发 0 代 GC
          ↓
       扫描 0 代对象
          ↓
       0 代 GC 次数 +1
          ↓
       0 代 GC 次数 > 10（阈值）？
          ├─ 否 → 继续
          └─ 是 → 触发 1 代 GC
                 ↓
              1 代 GC 次数 +1
                 ↓
              1 代 GC 次数 > 10（阈值）？
                 ├─ 否 → 继续
                 └─ 是 → 触发 2 代 GC
                        ↓
                     扫描所有代
```

## 🔍 GC 实现细节

### 循环引用的检测

```
CPython 维护一个链表（PyObject）：
  - 每个对象都有 ob_next 和 ob_prev
  - 可达对象在链表中
  - 不可达对象形成"环"

GC 扫描：
  1. 标记所有可达对象
  2. 找出不可达对象（环）
  3. 释放不可达对象
```

### 三色标记算法

```
GC 扫描用三色标记：
  - 白色：未访问（可能是垃圾）
  - 灰色：已访问，子对象未访问
  - 黑色：已访问，子对象都已访问

步骤：
  1. 所有对象初始为白色
  2. 从根对象（GC roots）出发，标记为灰色
  3. 处理灰色对象，标记子对象为灰色
  4. 标记完成后仍是白色的对象 = 垃圾
```

## 🛠️ gc 模块 API

### 基本操作

```python
import gc

# 启用 / 禁用 GC
gc.enable()
gc.disable()

# 强制 GC
gc.collect()         # 回收所有代
gc.collect(0)        # 只回收 0 代
gc.collect(1)        # 回收 0 代 + 1 代
gc.collect(2)        # 回收所有代

# 阈值
print(gc.get_threshold())  # (700, 10, 10)
gc.set_threshold(1000, 15, 15)

# 统计
print(gc.get_stats())
# [
#   {'collected': 0, 'uncollectable': 0, 'collections': 0},  # 0代
#   {'collected': 0, 'uncollectable': 0, 'collections': 0},  # 1代
#   {'collected': 0, 'uncollectable': 0, 'collections': 0}   # 2代
# ]

# 调试
gc.set_debug(gc.DEBUG_LEAK)
```

### 调试标志

```python
import gc

gc.set_debug(gc.DEBUG_COLLECTABLE)  # 打印可回收对象
gc.set_debug(gc.DEBUG_UNCOLLECTABLE) # 打印不可回收对象
gc.set_debug(gc.DEBUG_INSTANCES)    # 打印实例
gc.set_debug(gc.DEBUG_OBJECTS)       # 打印对象
gc.set_debug(gc.DEBUG_SAVEALL)       # 保存所有对象
gc.set_debug(gc.DEBUG_LEAK)          # 内存泄漏调试

# 关闭调试
gc.set_debug(0)
```

### 获取引用

```python
import gc
import weakref

class Node:
    def __init__(self, name):
        self.name = name
        self.next = None

a = Node("A")
b = Node("B")
a.next = b
b.next = a  # 循环引用

# 获取对象的所有引用
print(gc.get_referrers(a))  # 返回引用 a 的对象列表
print(gc.get_referents(a))  # 返回 a 引用的对象列表
```

## 📊 循环引用实例

### 创建循环引用

```python
import gc

class Node:
    def __init__(self, name):
        self.name = name
        self.refs = []

# 创建循环
a = Node("A")
b = Node("B")
a.refs.append(b)
b.refs.append(a)
del a, b

# 触发 GC
collected = gc.collect()
print(f"回收了 {collected} 个对象")
```

### 避免循环引用

```python
# 1. 使用 weakref（弱引用）
import weakref

class Node:
    def __init__(self, name):
        self.name = name
        self.refs = []  # 普通引用

class NodeWeak:
    def __init__(self, name):
        self.name = name
        self.refs = []  # 弱引用

# 强引用（会循环引用）
a = Node("A")
b = Node("B")
a.refs.append(b)
b.refs.append(a)
del a, b  # 循环引用，需 GC 回收

# 弱引用（不增加 refcount）
a = NodeWeak("A")
b = NodeWeak("B")
a.refs.append(weakref.ref(b))
b.refs.append(weakref.ref(a))
del a, b  # 立即释放

# 2. 避免容器持有其他容器的强引用
class Tree:
    def __init__(self):
        self.parent = None  # 用 weakref 替代
        self.children = []
```

## 📊 监控内存

### 启用 GC 调试

```python
import gc

# 检测内存泄漏
gc.set_debug(gc.DEBUG_LEAK)

# 运行代码
for i in range(1000):
    obj = SomeObject()
    # del obj（应该被 GC）

# GC 会打印泄漏的对象
collected = gc.collect()
print(f"回收: {collected}")
```

### tracemalloc 追踪

```python
import tracemalloc

tracemalloc.start()

# 业务代码
data = []
for i in range(10000):
    data.append([i] * 100)

# 快照
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

for stat in top_stats[:10]:
    print(stat)
# 输出占用内存最多的代码位置
```

### objgraph 第三方

```python
import objgraph

# 显示前 N 个对象类型
objgraph.show_most_common_types(limit=10)

# 查找内存泄漏
objgraph.show_growth()

# 显示对象引用关系
objgraph.show_refs([an_object], filename='refs.png')
```

## 📊 调优 GC

### 调整阈值

```python
import gc

# 默认阈值（可调整）
gc.set_threshold(700, 10, 10)

# 大对象多 → 调高（减少 GC 频率）
gc.set_threshold(1000, 15, 15)

# 小对象多 → 调低（更频繁 GC）
gc.set_threshold(500, 5, 5)
```

### 手动触发 GC

```python
import gc

# 大量对象释放后手动触发
gc.collect()

# 定时 GC（如游戏循环）
import time
while True:
    do_work()
    if time.time() % 60 < 1:  # 每分钟
        gc.collect()
```

### 禁用 GC（特殊场景）

```python
import gc

# 长时间运行的科学计算（可禁用 GC）
gc.disable()
# ... 计算 ...
gc.enable()
gc.collect()  # 显式回收
```

## 🛠️ 实战：排查内存泄漏

### 1. 监控内存增长

```python
import psutil
import os
import time

def monitor_memory(interval=5):
    process = psutil.Process(os.getpid())
    while True:
        mem = process.memory_info().rss / 1024 / 1024  # MB
        print(f"内存: {mem:.1f} MB")
        time.sleep(interval)
```

### 2. 强制 GC 找泄漏

```python
import gc
import objgraph

gc.set_debug(gc.DEBUG_LEAK)

# 业务代码

# 强制 GC
collected = gc.collect()
uncollectable = gc.garbage  # 不可回收对象
print(f"不可回收: {len(uncollectable)}")
for obj in uncollectable[:5]:
    print(objgraph.describe(obj))
```

## 🎯 总结

**Python GC 核心要点**：
- ✅ 引用计数不能处理循环引用
- ✅ 分代 GC 解决循环引用（0/1/2 代）
- ✅ 三色标记算法扫描可达性
- ✅ 调整 GC 阈值（trade-off）
- ✅ 弱引用避免循环引用
- ✅ tracemalloc 追踪内存分配
- ✅ 调试模式 DEBUG_LEAK 找泄漏
- ⚠️ 大量循环引用会影响 GC 性能
- ⚠️ 长时间运行需关注内存泄漏

**下一步：** [📊 性能剖析](/02-principles/profiling) — cProfile 与 line_profiler


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
