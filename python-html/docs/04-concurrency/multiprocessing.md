---
title: multiprocessing
date: 2026-08-15  # date-auto-injected
---

# 🔀 multiprocessing

> Python **multiprocessing** 模块通过**多进程**绕过 GIL，适合 **CPU 密集型**任务并行化。

## 🎯 为什么用 multiprocessing？

```
GIL 限制多线程并行：
  - CPU 密集型任务：多线程无法利用多核
  - 解决：多进程（每个进程独立 GIL）

multiprocessing 特点：
  ✅ 每个进程有独立 Python 解释器
  ✅ 真正并行（利用多核）
  ✅ 独立内存（无需锁）
  ⚠️ 进程间通信复杂
  ⚠️ 创建开销大（不如线程）
```

## 🚀 快速开始

### 基本使用

```python
import multiprocessing
import time

def cpu_task(n):
    total = 0
    for i in range(n):
        total += i ** 2
    return total

if __name__ == "__main__":
    # 单进程
    start = time.time()
    result = cpu_task(10_000_000)
    print(f"单进程: {time.time() - start:.2f}s")
    
    # 多进程
    start = time.time()
    with multiprocessing.Pool(4) as pool:
        results = pool.map(cpu_task, [10_000_000] * 4)
    print(f"4 进程: {time.time() - start:.2f}s")
    # 4 进程约快 3-4x（4 核 CPU）
```

### 进程类

```python
import multiprocessing

class Worker(multiprocessing.Process):
    def __init__(self, name):
        super().__init__()
        self.worker_name = name
    
    def run(self):
        print(f"Worker {self.worker_name} started, pid={self.pid}")
        # 业务逻辑
        print(f"Worker {self.worker_name} done")

workers = [Worker(f"W{i}") for i in range(3)]
for w in workers: w.start()
for w in workers: w.join()
```

## 🔄 进程间通信

### Queue（队列）

```python
import multiprocessing

def producer(q):
    for i in range(5):
        q.put(i)
        print(f"Produced: {i}")

def consumer(q):
    while True:
        item = q.get()
        if item is None:
            break
        print(f"Consumed: {item}")

q = multiprocessing.Queue()
p1 = multiprocessing.Process(target=producer, args=(q,))
p2 = multiprocessing.Process(target=consumer, args=(q,))
p1.start()
p2.start()
p1.join()
q.put(None)  # 通知 consumer 结束
p2.join()
```

### Pipe（管道）

```python
import multiprocessing

def sender(conn):
    conn.send("Hello from sender")
    conn.send([1, 2, 3])
    conn.close()

def receiver(conn):
    while True:
        try:
            msg = conn.recv()
            print(f"Received: {msg}")
        except EOFError:
            break

parent_conn, child_conn = multiprocessing.Pipe()
p = multiprocessing.Process(target=sender, args=(child_conn,))
p.start()
receiver(parent_conn)  # 主进程接收
p.join()
```

### Shared Memory（共享内存）

```python
import multiprocessing
import time

def worker(shared_list):
    shared_list.append("worker_data")
    print(f"Worker: {shared_list}")

if __name__ == "__main__":
    # 共享列表
    with multiprocessing.Manager() as manager:
        shared_list = manager.list()
        shared_list.append("main_data")
        
        p = multiprocessing.Process(target=worker, args=(shared_list,))
        p.start()
        p.join()
        
        print(f"Main: {shared_list}")
        # ['main_data', 'worker_data']
```

## 🏊 进程池

### Pool

```python
import multiprocessing

def square(x):
    return x * x

if __name__ == "__main__":
    with multiprocessing.Pool(4) as pool:
        # map：单参数
        results = pool.map(square, [1, 2, 3, 4, 5])
        print(results)  # [1, 4, 9, 16, 25]
        
        # map_async：异步
        async_result = pool.map_async(square, [1, 2, 3, 4, 5])
        results = async_result.get(timeout=10)
        
        # imap：迭代器
        for r in pool.imap(square, [1, 2, 3, 4, 5]):
            print(r)
        
        # imap_unordered：乱序
        for r in pool.imap_unordered(square, [1, 2, 3, 4, 5]):
            print(r)
        
        # apply：单任务
        result = pool.apply(square, (5,))
        print(result)
        
        # apply_async：异步
        async_result = pool.apply_async(square, (5,))
        result = async_result.get()
```

### concurrent.futures.ProcessPoolExecutor

```python
from concurrent.futures import ProcessPoolExecutor
import time

def cpu_task(n):
    return sum(i**2 for i in range(n))

if __name__ == "__main__":
    start = time.time()
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(cpu_task, 5_000_000) for _ in range(4)]
        results = [f.result() for f in futures]
    print(f"4 进程: {time.time() - start:.2f}s")
```

## 🔒 进程同步

### Lock（互斥锁）

```python
import multiprocessing

def worker(lock, counter):
    for _ in range(100000):
        with lock:
            counter.value += 1

if __name__ == "__main__":
    counter = multiprocessing.Value("i", 0)
    lock = multiprocessing.Lock()
    
    processes = [multiprocessing.Process(target=worker, args=(lock, counter)) for _ in range(4)]
    for p in processes: p.start()
    for p in processes: p.join()
    print(counter.value)  # 400000
```

### Event（事件）

```python
import multiprocessing
import time

def waiter(event):
    print("Waiting...")
    event.wait()
    print("Done!")

def setter(event):
    time.sleep(2)
    event.set()

if __name__ == "__main__":
    event = multiprocessing.Event()
    multiprocessing.Process(target=waiter, args=(event,)).start()
    multiprocessing.Process(target=setter, args=(event,)).start()
```

## 🛠️ 实战：CPU 密集型任务

```python
import multiprocessing
import time

def heavy_computation(data):
    """CPU 密集型任务"""
    result = 0
    for x in data:
        for _ in range(1000):
            result += x ** 0.5
    return result

if __name__ == "__main__":
    # 准备数据
    data_chunks = [list(range(i * 10000, (i + 1) * 10000)) for i in range(8)]
    
    # 单进程
    start = time.time()
    results = [heavy_computation(chunk) for chunk in data_chunks]
    print(f"单进程: {time.time() - start:.2f}s")
    
    # 多进程
    start = time.time()
    with multiprocessing.Pool(4) as pool:
        results = pool.map(heavy_computation, data_chunks)
    print(f"4 进程: {time.time() - start:.2f}s")
    # 接近 4 倍加速（4 核 CPU）
```

## 📊 进程 vs 线程

| 维度 | 多线程（threading） | 多进程（multiprocessing） |
|------|---------------------|----------------------------|
| 内存 | 共享 | 独立 |
| 创建开销 | 小 | 大 |
| 通信 | 简单（共享变量） | 复杂（IPC） |
| CPU 密集 | ❌ GIL 限制 | ✅ 真正并行 |
| IO 密集 | ✅ 适合 | ⚠️ 适合但重 |
| 扩展性 | 同一进程 | 多机器 |

## 🎯 总结

**multiprocessing 核心要点**：
- ✅ 多进程绕过 GIL（CPU 密集并行）
- ✅ Process 类创建进程
- ✅ Pool 进程池（推荐）
- ✅ Queue / Pipe 进程间通信
- ✅ Lock / Event 进程同步
- ✅ Manager 共享复杂对象
- ✅ ProcessPoolExecutor 高级接口
- ⚠️ 进程创建开销大（不如线程）
- ⚠️ 进程间通信复杂（用 Manager）
- ⚠️ 必须在 `if __name__ == "__main__":` 下

**下一步：** [⚡ asyncio 协程](/04-concurrency/asyncio) — 异步编程
