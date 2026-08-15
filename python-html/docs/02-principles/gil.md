---
title: GIL 全局锁
---

# ⏱️ GIL 全局锁

> **GIL（Global Interpreter Lock）**是 CPython 最具争议的设计。它**限制 Python 多线程**的并行能力，但对**IO 密集型**任务影响有限。

## 🎯 GIL 是什么？

```
GIL = Global Interpreter Lock（全局解释器锁）

作用：
  - 保证同一时刻只有一个线程执行 Python 字节码
  - 保护 CPython 的内存管理（引用计数）不是线程安全的

影响：
  - 多线程不能利用多核 CPU
  - CPU 密集型任务无法真正并行
  - IO 密集型任务影响较小（IO 等待时释放 GIL）
```

## 🔍 GIL 的工作原理

```
线程 A 获得 GIL
  ↓
执行字节码
  ↓
检查 GIL 锁
  ├─ 未持有 → 释放 GIL（每 100 字节码或 5ms）
  └─ 持有 → 继续执行
  ↓
线程 B 获得 GIL
  ↓
（重复）

GIL 切换触发条件：
  - 执行的字节码达到一定数量
  - 线程执行了 IO 操作（time.sleep、socket.recv）
  - 线程主动释放
```

## 📊 GIL 的影响

### CPU 密集型任务

```python
import threading
import time

# CPU 密集型：GIL 影响巨大
def cpu_task():
    n = 0
    for _ in range(10_000_000):
        n += 1

# 单线程
start = time.time()
cpu_task()
cpu_task()
print(f"单线程: {time.time() - start:.2f}s")  # ~1.0s

# 多线程（不会更快！）
start = time.time()
t1 = threading.Thread(target=cpu_task)
t2 = threading.Thread(target=cpu_task)
t1.start()
t2.start()
t1.join()
t2.join()
print(f"双线程: {time.time() - start:.2f}s")  # ~1.2s（甚至更慢）
```

### IO 密集型任务

```python
import threading
import time
import urllib.request

def io_task():
    urllib.request.urlopen("http://httpbin.org/delay/1").read()

# 单线程
start = time.time()
io_task()
io_task()
print(f"单线程: {time.time() - start:.2f}s")  # ~2.0s

# 多线程（明显加速！）
start = time.time()
t1 = threading.Thread(target=io_task)
t2 = threading.Thread(target=io_task)
t1.start()
t2.start()
t1.join()
t2.join()
print(f"双线程: {time.time() - start:.2f}s")  # ~1.0s
```

## 📊 GIL 历史

```
1989：Python 诞生，GIL 存在
2000：Python 2.0，多线程支持（但 GIL 限制）
2003：Python 2.3，引入 GIL 切换
2010：Python 2.7，GIL 仍是问题
2017：Python 3.6，GIL 优化（更快切换）
2021：Python 3.10，GIL 工作组
2023：Python 3.12，可选 no-GIL 实验（PEP 703）
```

## 🔧 GIL 的设计初衷

```
为什么 CPython 有 GIL？

1. 内存管理不是线程安全
   - 引用计数需要原子操作
   - 避免加锁的性能开销

2. CPython 大量 C 扩展
   - C 扩展大多不是线程安全
   - GIL 保护 C 扩展

3. 简单性
   - 单线程执行简化了内存模型
   - 避免复杂的锁和同步

权衡：
  - 多线程 CPU 密集型 → 受限
  - 多线程 IO 密集型 → 不受影响
  - 多进程 CPU 密集型 → 不受限（独立 GIL）
```

## 🚀 绕过 GIL 的方案

### 方案 1：多进程（multiprocessing）

```python
from multiprocessing import Process
import time

def cpu_task():
    n = 0
    for _ in range(10_000_000):
        n += 1

# 多进程：真正并行
start = time.time()
processes = [Process(target=cpu_task) for _ in range(4)]
for p in processes: p.start()
for p in processes: p.join()
print(f"4 进程: {time.time() - start:.2f}s")  # ~0.3s（4 核 CPU）

# vs 多线程（受限 GIL）
import threading
threads = [threading.Thread(target=cpu_task) for _ in range(4)]
start = time.time()
for t in threads: t.start()
for t in threads: t.join()
print(f"4 线程: {time.time() - start:.2f}s")  # ~1.0s
```

### 方案 2：多线程 + IO 密集

```python
import threading
import requests
import time

def fetch_url(url):
    return requests.get(url).text

urls = ["http://example.com"] * 100

# 单线程
start = time.time()
for url in urls:
    fetch_url(url)
print(f"单线程: {time.time() - start:.2f}s")  # 慢

# 多线程
start = time.time()
threads = []
for url in urls:
    t = threading.Thread(target=fetch_url, args=(url,))
    t.start()
    threads.append(t)
for t in threads:
    t.join()
print(f"多线程: {time.time() - start:.2f}s")  # 快
```

### 方案 3：异步（asyncio）

```python
import asyncio
import aiohttp

async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.text()

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)

asyncio.run(main())
# 单线程异步，性能接近多线程，无需 GIL 限制
```

### 方案 4：C 扩展

```python
# numpy / pandas 等 C 扩展在执行时释放 GIL

import numpy as np

# 大量计算在 C 层完成，绕过 GIL
arr = np.random.rand(1000, 1000)
result = np.linalg.inv(arr)  # numpy 内部多线程
```

### 方案 5：其他 Python 实现

```
- PyPy：单线程快，但仍有 GIL
- Jython：跑在 JVM 上，无 GIL（已不活跃）
- IronPython：跑在 .NET 上，无 GIL（已不活跃）
- Python 3.13+：可选 no-GIL 实验（PEP 703）
```

## 🛠️ GIL 调优

### 查看 GIL 争用

```python
import sys
print(sys.getswitchinterval())  # 默认 5ms

# 设置 GIL 切换间隔
sys.setswitchinterval(0.001)  # 1ms（更频繁切换）
sys.setswitchinterval(0.01)   # 10ms（更少切换）
```

### Python 3.13 新特性（PEP 703）

```python
# Python 3.13+ 实验性 no-GIL
# 编译时使用 --disable-gil 选项
# 运行时可启用 no-GIL 模式

# 配置文件
# pyproject.toml
[build]
option = "--disable-gil"
```

## 📊 GIL vs 多线程

| 场景 | threading | multiprocessing | asyncio |
|------|-----------|-----------------|---------|
| CPU 密集 | ❌ 慢 | ✅ 真正并行 | ❌ 慢 |
| IO 密集 | ✅ 适合 | ⚠️ 适合但重 | ✅ 最佳 |
| 实现难度 | 简单 | 较复杂 | 中等 |
| 内存占用 | 低 | 高（多进程） | 极低 |
| 适用 | 简单并发 | CPU 密集 | 高并发 IO |

## 🎯 总结

**GIL 核心要点**：
- ✅ GIL 保护 CPython 内存管理
- ✅ 多线程不能利用多核（CPU 密集）
- ✅ 多线程适合 IO 密集（不受 GIL 影响）
- ✅ 多进程绕过 GIL（multiprocessing）
- ✅ 异步（asyncio）是 IO 密集的最佳选择
- ✅ C 扩展（numpy）会释放 GIL
- ⚠️ Python 3.13+ 可选 no-GIL（实验性）
- ⚠️ 选对并发方案比纠结 GIL 更重要

**下一步：** [🔍 垃圾回收](/02-principles/gc) — GC 机制详解
