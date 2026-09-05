---
title: threading 多线程
date: 2026-08-15  # date-auto-injected
---

# 🧵 threading 多线程
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600">Python GIL 与多线程真相</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">CPython 全局解释器锁 · 单进程仅 1 线程执行字节码</text>

  <!-- 进程框 -->
  <rect x="30" y="90" width="540" height="280" rx="10" fill="#f8fafc" stroke="#94a3b8" stroke-width="2" stroke-dasharray="6,3"/>
  <text x="300" y="115" text-anchor="middle" font-size="13" font-weight="700" fill="#1e293b">Python 进程（单进程）</text>

  <!-- GIL 锁 -->
  <rect class="at-hover-card" x="230" y="135" width="140" height="40" rx="6" fill="#fee2e2" stroke="#dc2626" stroke-width="2"/>
  <text x="300" y="160" text-anchor="middle" font-size="12" font-weight="700" fill="#991b1b">🔒 GIL Mutex</text>

  <!-- 线程 1..4 -->
  <rect class="at-hover-card" x="50" y="200" width="115" height="55" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="107" y="223" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">Thread-1</text>
  <text x="107" y="240" text-anchor="middle" font-size="9" fill="#334155">持有 GIL ✓</text>

  <rect class="at-hover-card" x="180" y="200" width="115" height="55" rx="6" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="237" y="223" text-anchor="middle" font-size="11" font-weight="700" fill="#475569">Thread-2</text>
  <text x="237" y="240" text-anchor="middle" font-size="9" fill="#64748b">等待 GIL</text>

  <rect class="at-hover-card" x="310" y="200" width="115" height="55" rx="6" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="367" y="223" text-anchor="middle" font-size="11" font-weight="700" fill="#475569">Thread-3</text>
  <text x="367" y="240" text-anchor="middle" font-size="9" fill="#64748b">等待 GIL</text>

  <rect class="at-hover-card" x="440" y="200" width="115" height="55" rx="6" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="497" y="223" text-anchor="middle" font-size="11" font-weight="700" fill="#475569">Thread-4</text>
  <text x="497" y="240" text-anchor="middle" font-size="9" fill="#64748b">等待 GIL</text>

  <!-- GIL → 持有线程箭头 -->
  <line x1="270" y1="175" x2="107" y2="200" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arr)"/>
  <line x1="290" y1="175" x2="237" y2="200" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3,3"/>
  <line x1="310" y1="175" x2="367" y2="200" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3,3"/>
  <line x1="330" y1="175" x2="497" y2="200" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3,3"/>

  <!-- 时间轴 -->
  <rect x="50" y="280" width="500" height="60" rx="6" fill="#f1f5f9" stroke="#cbd5e1"/>
  <text x="65" y="298" font-size="10" font-weight="700" fill="#1e293b">时间线（5ms tick）</text>
  <line x1="65" y1="320" x2="540" y2="320" stroke="#64748b" stroke-width="1"/>
  <rect x="100" y="305" width="80" height="22" fill="#dbeafe" stroke="#3b82f6"/>
  <text x="140" y="320" text-anchor="middle" font-size="9" fill="#1e40af">T1</text>
  <rect x="180" y="305" width="80" height="22" fill="#f1f5f9" stroke="#94a3b8"/>
  <text x="220" y="320" text-anchor="middle" font-size="9" fill="#475569">T2</text>
  <rect x="260" y="305" width="80" height="22" fill="#dbeafe" stroke="#3b82f6"/>
  <text x="300" y="320" text-anchor="middle" font-size="9" fill="#1e40af">T3</text>
  <rect x="340" y="305" width="80" height="22" fill="#f1f5f9" stroke="#94a3b8"/>
  <text x="380" y="320" text-anchor="middle" font-size="9" fill="#475569">T4</text>
  <rect x="420" y="305" width="80" height="22" fill="#dbeafe" stroke="#3b82f6"/>
  <text x="460" y="320" text-anchor="middle" font-size="9" fill="#1e40af">T1</text>
  <text x="540" y="335" text-anchor="end" font-size="9" fill="#64748b" font-style="italic">tick 切换（条件变量 + timeout）</text>

  <!-- 关键结论 -->
  <rect x="30" y="385" width="540" height="80" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="300" y="408" text-anchor="middle" font-size="12" font-weight="700" fill="#92400e">关键结论</text>
  <text x="50" y="428" font-size="11" fill="#334155">· CPU 密集：多线程 ≈ 单线程（GIL 串行化字节码执行）</text>
  <text x="50" y="446" font-size="11" fill="#334155">· IO 密集：多线程有效（GIL 在 IO 系统调用时释放）</text>
  <text x="320" y="428" font-size="11" fill="#334155">· CPU 密集替代：multiprocessing / C 扩展 / Cython</text>
  <text x="320" y="446" font-size="11" fill="#334155">· Python 3.13+ free-threaded mode（PEP 703，无 GIL）</text>
</svg>


> Python **threading** 模块支持**多线程**编程。但因为 **GIL** 的存在，多线程只适合 **IO 密集型任务**。

## 🎯 多线程基础

```python
import threading
import time

# 创建线程
def worker(name, delay):
    print(f"Worker {name} starting")
    time.sleep(delay)
    print(f"Worker {name} done")

# 创建并启动
t = threading.Thread(target=worker, args=("A", 2), name="Thread-A")
t.start()
t.join()  # 等待线程结束

print("Main done")
```

## 📊 Thread 类

### 创建线程

```python
import threading

# 方式 1：函数式
def task():
    print("Running")

t1 = threading.Thread(target=task)
t1.start()

# 方式 2：带参数
t2 = threading.Thread(target=task, args=("arg1",), kwargs={"key": "value"})
t2.start()

# 方式 3：继承 Thread
class MyThread(threading.Thread):
    def run(self):
        print("Running in thread")

t3 = MyThread()
t3.start()
```

### 线程方法

```python
import threading

t = threading.Thread(target=lambda: print("Hello"))

# 启动
t.start()

# 等待完成
t.join()             # 阻塞等待
t.join(timeout=5)    # 最多等 5 秒

# 检查状态
print(t.is_alive())   # 是否运行中
print(t.daemon)      # 是否守护线程
print(t.name)        # 线程名
print(t.ident)       # 线程 ID

# 守护线程（主线程退出时自动结束）
t.daemon = True
t.start()
```

## 🔒 线程同步

### Lock（互斥锁）

```python
import threading

# 共享资源
counter = 0
lock = threading.Lock()

def increment():
    global counter
    for _ in range(100000):
        with lock:  # 自动获取和释放
            counter += 1

# 不加锁：结果不确定
# 加锁：结果 = 200000
threads = [threading.Thread(target=increment) for _ in range(2)]
for t in threads: t.start()
for t in threads: t.join()
print(counter)  # 200000
```

### RLock（可重入锁）

```python
import threading

rlock = threading.RLock()

def recursive_func(n):
    with rlock:
        if n > 0:
            recursive_func(n - 1)
        # 同一线程可多次获取
```

### Condition（条件变量）

```python
import threading

condition = threading.Condition()
items = []

def consumer():
    with condition:
        while not items:
            condition.wait()
        item = items.pop()
        print(f"Consumed: {item}")

def producer():
    with condition:
        items.append("data")
        condition.notify()

t1 = threading.Thread(target=consumer)
t2 = threading.Thread(target=producer)
t1.start()
time.sleep(0.1)
t2.start()
t1.join()
t2.join()
```

### Semaphore（信号量）

```python
import threading

# 限制并发数
sem = threading.Semaphore(3)

def worker(i):
    with sem:  # 最多 3 个并发
        print(f"Worker {i} running")
        time.sleep(1)
        print(f"Worker {i} done")

threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
for t in threads: t.start()
for t in threads: t.join()
```

### Event（事件）

```python
import threading

event = threading.Event()

def waiter():
    print("Waiting...")
    event.wait()  # 阻塞直到 event.set()
    print("Done!")

def setter():
    time.sleep(2)
    event.set()  # 唤醒所有等待的线程

threading.Thread(target=waiter).start()
threading.Thread(target=setter).start()
```

## 📊 线程池

```python
from concurrent.futures import ThreadPoolExecutor
import time

def task(n):
    time.sleep(1)
    return n * 2

# 创建线程池
with ThreadPoolExecutor(max_workers=5) as executor:
    # 提交任务
    futures = [executor.submit(task, i) for i in range(10)]
    
    # 获取结果
    for f in futures:
        print(f.result())

# map 风格
with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(task, range(10)))
    print(results)
```

## 🛠️ 实战：生产者-消费者

```python
import threading
import queue
import time
import random

# 共享队列
q = queue.Queue(maxsize=5)

def producer():
    for i in range(10):
        item = f"item-{i}"
        q.put(item)
        print(f"Produced: {item}")
        time.sleep(random.random())

def consumer():
    while True:
        try:
            item = q.get(timeout=3)
            print(f"Consumed: {item}")
            q.task_done()
            time.sleep(random.random() * 0.5)
        except queue.Empty:
            break

# 启动线程
t1 = threading.Thread(target=producer)
t2 = threading.Thread(target=consumer)
t1.start()
t2.start()
t1.join()
t2.join()
print("Done")
```

## 🔧 线程局部数据

```python
import threading

# 线程局部变量（每个线程独立）
local_data = threading.local()

def worker(name):
    local_data.name = name
    print(f"Thread {name}: {local_data.name}")

t1 = threading.Thread(target=worker, args=("A",))
t2 = threading.Thread(target=worker, args=("B",))
t1.start()
t2.start()
```

## 🛠️ 实战：批量下载（IO 密集）

```python
import threading
import requests
import time

urls = [
    "https://api.example.com/data/1",
    "https://api.example.com/data/2",
    "https://api.example.com/data/3",
    "https://api.example.com/data/4",
    "https://api.example.com/data/5",
]

def download(url):
    print(f"Downloading {url}")
    r = requests.get(url, timeout=10)
    print(f"Done {url}: {len(r.content)} bytes")
    return r.content

# 单线程
start = time.time()
for url in urls:
    download(url)
print(f"单线程: {time.time() - start:.1f}s")

# 多线程
start = time.time()
threads = []
results = []
for url in urls:
    t = threading.Thread(target=lambda u=url: results.append(download(u)))
    t.start()
    threads.append(t)
for t in threads:
    t.join()
print(f"多线程: {time.time() - start:.1f}s")
# 多线程快 3-5x（IO 密集型）
```

## 🎯 总结

**Python threading 核心要点**：
- ✅ 适合 IO 密集型任务（HTTP、文件、数据库）
- ✅ 不适合 CPU 密集型（GIL 限制）
- ✅ Lock / RLock 保护共享资源
- ✅ Condition 实现等待/通知
- ✅ Semaphore 限制并发数
- ✅ Event 线程间通知
- ✅ ThreadPoolExecutor 线程池
- ✅ threading.local 线程局部数据
- ⚠️ GIL 限制多线程 CPU 性能
- ⚠️ 共享资源需加锁（避免死锁）

**下一步：** [🔀 multiprocessing](/04-concurrency/multiprocessing) — 多进程


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
