---
title: 线程池与进程池
---

# 🏊 线程池与进程池

> **concurrent.futures** 是 Python **统一的并发任务执行框架**，提供 **ThreadPoolExecutor**（线程池）和 **ProcessPoolExecutor**（进程池），简化并发编程。

## 🎯 为什么用线程池？

```
直接用 Thread 的问题：
  ❌ 频繁创建/销毁线程（开销大）
  ❌ 线程数量无控制（可能 OOM）
  ❌ 没有返回值收集
  ❌ 没有异常处理

线程池的优势：
  ✅ 线程复用（提高性能）
  ✅ 限制并发数
  ✅ 自动管理任务队列
  ✅ 统一的 API（ThreadPoolExecutor / ProcessPoolExecutor）
```

## 🚀 ThreadPoolExecutor（线程池）

### 基本使用

```python
from concurrent.futures import ThreadPoolExecutor
import time

def task(n):
    time.sleep(1)
    return n * 2

# 创建线程池
with ThreadPoolExecutor(max_workers=5) as executor:
    # 提交单个任务
    future = executor.submit(task, 10)
    result = future.result()  # 阻塞等待结果
    print(result)  # 20
    
    # 批量提交
    futures = [executor.submit(task, i) for i in range(10)]
    for f in futures:
        print(f.result())  # 0 2 4 6 8 10 12 14 16 18
```

### map 方法

```python
from concurrent.futures import ThreadPoolExecutor

def square(x):
    return x ** 2

with ThreadPoolExecutor(max_workers=3) as executor:
    # 类似 map，按顺序返回结果
    results = executor.map(square, [1, 2, 3, 4, 5])
    print(list(results))  # [1, 4, 9, 16, 25]
    
    # 带超时
    try:
        results = executor.map(square, [1, 2, 3], timeout=2)
        print(list(results))
    except TimeoutError:
        print("Timeout")
```

### as_completed（按完成顺序）

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random

def task(n):
    time.sleep(random.random())
    return n

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(task, i) for i in range(10)]
    
    # 按完成顺序处理（不按提交顺序）
    for future in as_completed(futures):
        result = future.result()
        print(f"Got: {result}")
```

## 🔧 Future 对象

```python
from concurrent.futures import ThreadPoolExecutor
import time

def task(n):
    time.sleep(2)
    return n * 2

with ThreadPoolExecutor(max_workers=2) as executor:
    future = executor.submit(task, 10)
    
    # 检查状态
    print(future.running())  # True
    print(future.done())     # False
    
    # 阻塞等待（带超时）
    try:
        result = future.result(timeout=5)
        print(result)  # 20
    except TimeoutError:
        print("超时")
    
    # 获取异常
    try:
        result = future.result()
    except Exception as e:
        print(f"异常: {e}")
    
    # 取消任务（如果还没开始）
    if future.cancel():
        print("已取消")
    else:
        print("无法取消（已开始）")
    
    # 添加回调
    future.add_done_callback(lambda f: print(f"Done: {f.result()}"))
```

## 🏊 ProcessPoolExecutor（进程池）

### 基本使用

```python
from concurrent.futures import ProcessPoolExecutor
import time

def cpu_task(n):
    total = 0
    for i in range(n):
        total += i ** 2
    return total

if __name__ == "__main__":
    # 创建进程池
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(cpu_task, 1_000_000) for _ in range(4)]
        results = [f.result() for f in futures]
        print(results)

# 4 进程比 4 线程快 3-4 倍（CPU 密集）
```

### map 风格

```python
from concurrent.futures import ProcessPoolExecutor

def square(x):
    return x ** 2

if __name__ == "__main__":
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(square, range(10)))
        print(results)
```

## 🛠️ 实战：批量下载（线程池）

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import time

def download(url):
    r = requests.get(url, timeout=10)
    return url, len(r.content), r.status_code

def batch_download(urls, max_workers=10):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(download, url): url for url in urls}
        
        for future in as_completed(futures):
            url, size, status = future.result()
            print(f"{url}: {status} {size} bytes")
            results.append((url, size, status))
    
    return results

# 使用
urls = [
    "https://httpbin.org/get",
    "https://httpbin.org/headers",
    "https://httpbin.org/ip",
] * 10

start = time.time()
results = batch_download(urls, max_workers=5)
print(f"Total: {time.time() - start:.2f}s")
```

## 🛠️ 实战：CPU 密集型计算（进程池）

```python
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import time

def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def find_primes(start, end):
    return [n for n in range(start, end) if is_prime(n)]

if __name__ == "__main__":
    # 准备数据
    ranges = [(i * 100000, (i + 1) * 100000) for i in range(8)]
    
    # 单进程
    start = time.time()
    all_primes = []
    for r in ranges:
        all_primes.extend(find_primes(*r))
    print(f"单进程: {time.time() - start:.2f}s, {len(all_primes)} primes")
    
    # 多进程
    start = time.time()
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = executor.map(find_primes, *zip(*ranges))
        all_primes = []
        for result in results:
            all_primes.extend(result)
    print(f"4 进程: {time.time() - start:.2f}s, {len(all_primes)} primes")
```

## 🔧 异常处理

```python
from concurrent.futures import ThreadPoolExecutor

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

with ThreadPoolExecutor() as executor:
    futures = [executor.submit(divide, 10, b) for b in [1, 2, 0, 4, 0]]
    
    for i, future in enumerate(futures):
        try:
            result = future.result()
            print(f"Task {i}: {result}")
        except Exception as e:
            print(f"Task {i}: error - {e}")
```

### wait（控制等待）

```python
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED, ALL_COMPLETED

with ThreadPoolExecutor() as executor:
    futures = [executor.submit(slow_task, i) for i in range(5)]
    
    # 等待所有完成
    done, not_done = wait(futures, return_when=ALL_COMPLETED)
    for f in done:
        print(f.result())
    
    # 等待第一个完成
    done, not_done = wait(futures, return_when=FIRST_COMPLETED)
    print(f"First done: {done.pop().result()}")
    # 取消其他未完成的任务
    for f in not_done:
        f.cancel()
```

## 📊 线程池 vs 进程池

| 维度 | ThreadPoolExecutor | ProcessPoolExecutor |
|------|---------------------|------------------------|
| 适合 | IO 密集 | CPU 密集 |
| 共享内存 | ✅ | ❌ |
| 创建开销 | 小 | 大 |
| 通信 | 简单（共享变量） | 复杂（IPC） |
| 适用规模 | 数十~数百并发 | 进程数 ≤ CPU 核数 |

## 🎯 总结

**线程池与进程池核心要点**：
- ✅ ThreadPoolExecutor 适合 IO 密集
- ✅ ProcessPoolExecutor 适合 CPU 密集
- ✅ submit / map / as_completed 三种用法
- ✅ Future 对象管理异步结果
- ✅ 异常处理（future.result() 抛异常）
- ✅ wait 控制等待策略
- ⚠️ 进程池必须 `if __name__ == "__main__":`
- ⚠️ max_workers 不要超过 CPU 核数（进程池）
- ⚠️ 大量任务用 map（避免 submit 开销）

**下一步：** [🎯 并发模式](/04-concurrency/patterns) — 经典并发设计模式
