---
title: 性能剖析
---

# 📊 性能剖析

> **性能剖析（Profiling）**是定位 Python 性能瓶颈的关键手段。本章介绍常用工具和最佳实践。

## 🎯 性能剖析工具

```
标准库：
  - cProfile：函数级性能分析
  - profile：纯 Python 实现（慢）
  - timeit：基准测试
  - tracemalloc：内存追踪

第三方：
  - line_profiler：行级分析
  - memory_profiler：内存分析
  - py-spy：采样分析器（生产可用）
  - scalene：综合分析（CPU + GPU + 内存）
```

## 🔧 cProfile（推荐）

### 命令行使用

```bash
# 性能分析
python -m cProfile -o output.prof script.py

# 排序输出
python -m cProfile -s tottime script.py

# 输出到控制台
python -m cProfile script.py
```

### 程序内使用

```python
import cProfile
import pstats

# 启动分析
profiler = cProfile.Profile()
profiler.enable()

# 业务代码
def slow_function():
    total = 0
    for i in range(10_000_000):
        total += i
    return total

slow_function()
slow_function()

# 停止分析
profiler.disable()

# 输出报告
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # 前 10 个函数
stats.print_callers('slow_function')  # 调用者
stats.print_callees('slow_function')  # 被调用者
```

### 输出解读

```
   ncalls  tottime  percall  cumtime  percall  filename:lineno(function)
        1    0.000    0.000    0.456    0.456  script.py:1(<module>)
        2    0.225    0.113    0.225    0.113  script.py:5(slow_function)
        1    0.000    0.000    0.000    0.000  {built-in method builtins.exec}
```

字段说明：
- `ncalls`：调用次数
- `tottime`：函数自身耗时（不含子函数）
- `percall`：平均每次调用耗时
- `cumtime`：累计耗时（含子函数）
- `filename:lineno(function)`：函数位置

### 排序选项

```python
stats.sort_stats('cumulative')  # 按累计时间
stats.sort_stats('tottime')     # 按自身时间
stats.sort_stats('calls')       # 按调用次数
stats.sort_stats('name')        # 按函数名
```

### 可视化

```bash
# 用 snakeviz 可视化
pip install snakeviz
snakeviz output.prof

# 用 gprof2dot 生成调用图
pip install gprof2dot
gprof2dot -f pstats output.prof | dot -Tpng -o output.png
```

## ⏱️ timeit（基准测试）

### 命令行

```bash
# 测量 Python 语句执行时间
python -m timeit "sum(range(100))"

# 多行
python -m timeit "
for i in range(100):
    pass
"

# 设置次数
python -m timeit -n 1000 "x = 1 + 1"

# 设置时间（自动调整次数）
python -m timeit -t 1 "x = 1 + 1"
```

### 程序内使用

```python
import timeit

# 测量单个语句
t = timeit.timeit("sum(range(100))", number=1000)
print(f"1000 次 sum: {t:.4f}s")
print(f"平均每次: {t/1000*1e6:.2f}μs")

# 测量多行（用分号或三引号）
t = timeit.timeit("""
for i in range(100):
    if i % 2 == 0:
        x = i
    else:
        x = -i
""", number=10000)

# 多次测量取最佳
times = timeit.repeat("sum(range(100))", number=1000, repeat=5)
print(f"最佳: {min(times):.4f}s")
```

### 对比实现

```python
import timeit

# 对比两种实现
setup = """
import random
data = [random.randint(0, 1000) for _ in range(1000)]
"""

# 方式 1
t1 = timeit.timeit("sum(data)", setup=setup, number=1000)

# 方式 2
t2 = timeit.timeit("""
total = 0
for x in data:
    total += x
""", setup=setup, number=1000)

print(f"sum: {t1:.4f}s, 循环: {t2:.4f}s")
```

## 🔬 line_profiler（行级分析）

### 安装

```bash
pip install line_profiler
```

### 使用

```python
# 在函数前加 @profile 装饰器
@profile
def slow_function():
    total = 0
    for i in range(10_000_000):
        total += i ** 2
    return total

slow_function()
```

```bash
# 运行分析
kernprof -l -v script.py
```

输出：
```
Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
     1                                           @profile
     2                                           def slow_function():
     3         1        100.0    100.0      0.0      total = 0
     4  10000000      5000.0      0.0     50.0      for i in range(10_000_000):
     5  10000000      5000.0      0.0     50.0          total += i ** 2
     6         1          0.0      0.0      0.0      return total
```

## 💾 memory_profiler（内存分析）

### 安装

```bash
pip install memory_profiler
```

### 使用

```python
from memory_profiler import profile

@profile
def memory_intensive():
    big_list = [i for i in range(1_000_000)]
    big_dict = {i: i for i in range(1_000_000)}
    del big_list
    big_str = "x" * 10_000_000
    return big_dict

memory_intensive()
```

```bash
python -m memory_profiler script.py
```

输出：
```
Line #    Mem usage    Increment  Occurrences   Line Contents
============================================================
     1   38.7 MiB      0.0 MiB       1           @profile
     2   38.7 MiB      0.0 MiB       1           def memory_intensive():
     3   98.2 MiB     59.5 MiB       1           big_list = [i for i in range(1_000_000)]
     4  150.7 MiB     52.5 MiB       1           big_dict = {i: i for i in range(1_000_000)}
     5  150.7 MiB      0.0 MiB       1           del big_list
     6  160.4 MiB      9.7 MiB       1           big_str = "x" * 10_000_000
     7  160.4 MiB      0.0 MiB       1           return big_dict
```

## 🔥 py-spy（生产采样分析）

### 安装

```bash
pip install py-spy
```

### 使用

```bash
# 附加到运行中的进程（生产可用）
py-spy dump --pid 12345
py-spy top --pid 12345

# 记录火焰图
py-spy record -o profile.svg --pid 12345

# 实时打印调用栈
py-spy dump --pid 12345 | head -50
```

### 优势

```
✅ 无需重启进程
✅ 低开销（< 1%）
✅ 生产环境可用
✅ 生成火焰图
```

## 💡 Scalene（综合分析）

```bash
pip install scalene
scalene script.py
```

输出（CPU + GPU + 内存）：
```
script.py:    87% |  150MB |  120ms | (100%/0%/0%)
   list_comp/append:  60% |   80MB |   80ms
   ...
```

## 🛠️ 优化建议

### 1. 字符串拼接

```python
import timeit

# 慢：字符串拼接创建新对象
t1 = timeit.timeit("""
s = ''
for i in range(1000):
    s += str(i)
""", number=100)

# 快：join
t2 = timeit.timeit("""
''.join(str(i) for i in range(1000))
""", number=100)

print(f"拼接: {t1:.4f}s, join: {t2:.4f}s")
# join 快 10x+
```

### 2. 列表添加

```python
# 慢：append 到列表（动态扩容）
t1 = timeit.timeit("""
result = []
for i in range(10000):
    result.append(i)
""", number=100)

# 快：列表推导式
t2 = timeit.timeit("""
result = [i for i in range(10000)]
""", number=100)

print(f"append: {t1:.4f}s, 推导: {t2:.4f}s")
```

### 3. 字典访问

```python
# 慢：try/except
t1 = timeit.timeit("""
d = {'a': 1, 'b': 2}
for i in range(1000):
    try:
        x = d['a']
    except KeyError:
        pass
""", number=100)

# 快：get
t2 = timeit.timeit("""
d = {'a': 1, 'b': 2}
for i in range(1000):
    x = d.get('a', 0)
""", number=100)

print(f"try: {t1:.4f}s, get: {t2:.4f}s")
```

### 4. 局部变量 vs 全局变量

```python
import math

def use_global():
    for _ in range(10000):
        math.sin(1)

def use_local():
    sin = math.sin  # 局部变量
    for _ in range(10000):
        sin(1)

import timeit
t1 = timeit.timeit(use_global, number=100)
t2 = timeit.timeit(use_local, number=100)
print(f"全局: {t1:.4f}s, 局部: {t2:.4f}s")
# 局部访问快 5-10%
```

## 📊 实战：定位慢查询

### 步骤

```python
# 1. cProfile 找慢函数
python -m cProfile -o output.prof script.py

# 2. 分析报告
python -c "
import pstats
p = pstats.Stats('output.prof')
p.sort_stats('cumulative').print_stats(20)
"

# 3. 找最慢的 10 个函数
python -c "
import pstats
p = pstats.Stats('output.prof')
p.sort_stats('tottime').print_stats(10)
"

# 4. 找被调用最多的函数
python -c "
import pstats
p = pstats.Stats('output.prof')
p.sort_stats('calls').print_stats(10)
"
```

## 🎯 总结

**Python 性能剖析核心要点**：
- ✅ cProfile 找慢函数（最常用）
- ✅ timeit 基准测试
- ✅ line_profiler 行级分析
- ✅ memory_profiler 内存分析
- ✅ py-spy 生产环境采样分析
- ✅ scalene 综合分析（CPU+GPU+内存）
- ✅ 优化字符串拼接（用 join）
- ✅ 优化列表添加（用推导式）
- ✅ 用 get 代替 try/except
- ⚠️ 不要过早优化（先 measure）
- ⚠️ 优化前先 profile

**下一步：** [📚 常用库](/03-libraries/stdlib) — Python 标准库精要
