---
title: 同步原语
---

# 🔁 同步原语

> 多线程/多进程编程中，**同步原语**用于**协调并发任务**、保护共享资源。本章详解 Python 中的同步原语。

## 🎯 为什么需要同步原语？

```
并发编程的问题：
  - 竞态条件（多个线程同时修改共享数据）
  - 死锁（线程互相等待）
  - 资源竞争（多个任务争抢同一资源）

同步原语的作用：
  - 保护共享数据（互斥）
  - 控制执行顺序（等待/通知）
  - 限制并发数（信号量）
```

## 🔒 Lock（互斥锁）

### 基本使用

```python
import threading

counter = 0
lock = threading.Lock()

def increment():
    global counter
    for _ in range(100000):
        with lock:  # 自动获取和释放
            counter += 1

threads = [threading.Thread(target=increment) for _ in range(4)]
for t in threads: t.start()
for t in threads: t.join()
print(counter)  # 400000（正确）
```

### 不加锁的问题

```python
import threading

counter = 0

def increment():
    global counter
    for _ in range(100000):
        counter += 1  # 不是原子操作

threads = [threading.Thread(target=increment) for _ in range(4)]
for t in threads: t.start()
for t in threads: t.join()
print(counter)  # 通常 < 400000（数据竞争）
```

### 手动加锁

```python
lock = threading.Lock()
counter = 0

def increment():
    global counter
    for _ in range(100000):
        lock.acquire()
        try:
            counter += 1
        finally:
            lock.release()
```

## 🔁 RLock（可重入锁）

```python
import threading

rlock = threading.RLock()

def func(level):
    with rlock:  # 同一线程可多次获取
        if level > 0:
            func(level - 1)
        # 如果是 Lock 会死锁

func(5)  # 不会死锁（可重入 5 次）
```

## 🚦 Condition（条件变量）

```python
import threading

condition = threading.Condition()
items = []

def consumer():
    with condition:
        while not items:
            print("Consumer waiting...")
            condition.wait()  # 释放锁并阻塞
        item = items.pop()
        print(f"Consumed: {item}")

def producer():
    with condition:
        time.sleep(1)
        items.append("data")
        print("Produced: data")
        condition.notify()  # 唤醒等待的线程

t1 = threading.Thread(target=consumer)
t2 = threading.Thread(target=producer)
t1.start()
t2.start()
t1.join()
t2.join()
```

### notify vs notify_all

```python
# notify：唤醒一个等待的线程
condition.notify()

# notify_all：唤醒所有等待的线程
condition.notify_all()
```

## 🚧 Semaphore（信号量）

```python
import threading

# 限制并发数（最多 3 个）
sem = threading.Semaphore(3)

def access_resource(i):
    with sem:
        print(f"Task {i} acquired")
        time.sleep(1)
        print(f"Task {i} released")

threads = [threading.Thread(target=access_resource, args=(i,)) for i in range(10)]
for t in threads: t.start()
for t in threads: t.join()

# 输出：3 个任务同时进行，其余等待
```

### BoundedSemaphore

```python
# 有界信号量（防止 acquire 超过初始值）
bsem = threading.BoundedSemaphore(3)

# release 超过初始值会抛 ValueError
```

## 🚪 Event（事件）

```python
import threading

event = threading.Event()

def waiter():
    print("Waiting...")
    event.wait()  # 阻塞直到 set()
    print("Woke up!")

def setter():
    time.sleep(2)
    print("Setting event")
    event.set()

threading.Thread(target=waiter).start()
threading.Thread(target=setter).start()
```

### 多事件协调

```python
import threading

event_a = threading.Event()
event_b = threading.Event()

def step_a():
    print("Step A")
    event_a.set()

def step_b():
    event_a.wait()  # 等待 A
    print("Step B")
    event_b.set()

def step_c():
    event_b.wait()  # 等待 B
    print("Step C")

threading.Thread(target=step_a).start()
threading.Thread(target=step_b).start()
threading.Thread(target=step_c).start()
# 输出顺序：A → B → C
```

## 🚦 Barrier（屏障）

```python
import threading

barrier = threading.Barrier(3)

def worker(i):
    print(f"Worker {i} waiting")
    barrier.wait()  # 等待所有线程到齐
    print(f"Worker {i} passed")

threads = [threading.Thread(target=worker, args=(i,)) for i in range(3)]
for t in threads: t.start()
for t in threads: t.join()
# 输出：所有线程"waiting"，然后所有线程"passed"
```

## 📊 多进程同步原语

```python
import multiprocessing

# 进程 Lock
lock = multiprocessing.Lock()
counter = multiprocessing.Value("i", 0)

def worker():
    global counter
    for _ in range(100000):
        with lock:
            counter.value += 1

if __name__ == "__main__":
    processes = [multiprocessing.Process(target=worker) for _ in range(4)]
    for p in processes: p.start()
    for p in processes: p.join()
    print(counter.value)  # 400000
```

### 进程同步原语

```python
import multiprocessing

# Lock / RLock / Semaphore / Event / Condition
# 用法与 threading 类似（注意参数传递）

# Queue 进程间通信
q = multiprocessing.Queue()

def producer(q):
    for i in range(5):
        q.put(i)

def consumer(q):
    while True:
        try:
            item = q.get(timeout=1)
            print(item)
        except:
            break

if __name__ == "__main__":
    p = multiprocessing.Process(target=producer, args=(q,))
    c = multiprocessing.Process(target=consumer, args=(q,))
    p.start()
    c.start()
    p.join()
    c.join()
```

## 🛠️ 实战：线程安全的 Singleton

```python
import threading

class Singleton:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # 双重检查
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.value = 0

# 测试
def worker():
    instance = Singleton()
    instance.value += 1

threads = [threading.Thread(target=worker) for _ in range(100)]
for t in threads: t.start()
for t in threads: t.join()

s = Singleton()
print(s.value)  # 100
```

## 🛠️ 实战：读写锁（threading 不支持，可自己实现）

```python
import threading

class ReadWriteLock:
    def __init__(self):
        self._readers = 0
        self._writers = 0
        self._read_lock = threading.Lock()
        self._write_lock = threading.Lock()
        self._no_writers = threading.Condition(self._read_lock)
    
    def acquire_read(self):
        with self._read_lock:
            while self._writers > 0:
                self._no_writers.wait()
            self._readers += 1
    
    def release_read(self):
        with self._read_lock:
            self._readers -= 1
            if self._readers == 0:
                self._no_writers.notify_all()
    
    def acquire_write(self):
        with self._write_lock:
            while self._writers > 0:
                # 等待
                pass
            self._writers = 1
        with self._read_lock:
            while self._readers > 0:
                self._no_writers.wait()
    
    def release_write(self):
        with self._read_lock:
            self._writers = 0
            self._no_writers.notify_all()
        with self._write_lock:
            pass
```

## ⚠️ 常见问题

### 死锁

```python
# 避免死锁原则：
# 1. 避免嵌套锁
# 2. 按固定顺序获取锁
# 3. 设置锁超时
# 4. 减少锁粒度

# 反例：死锁
lock_a = threading.Lock()
lock_b = threading.Lock()

def worker1():
    with lock_a:
        with lock_b:
            pass

def worker2():
    with lock_b:
        with lock_a:
            pass

# 解决：统一顺序
def worker1():
    with lock_a:  # 总是先 A 后 B
        with lock_b:
            pass

def worker2():
    with lock_a:  # 总是先 A 后 B
        with lock_b:
            pass
```

### 活锁

```python
# 活锁：两个线程互相让出资源，都无法继续
# 解决：引入随机退避
import random
import time

def worker():
    while True:
        if lock.acquire(timeout=1):
            try:
                # 业务
                return
            finally:
                lock.release()
        time.sleep(random.random())  # 随机退避
```

## 🎯 总结

**同步原语核心要点**：
- ✅ Lock：互斥（最常用）
- ✅ RLock：可重入锁（避免死锁）
- ✅ Condition：等待/通知（生产者-消费者）
- ✅ Semaphore：限制并发数
- ✅ Event：线程间通知
- ✅ Barrier：所有线程到齐才继续
- ✅ 进程同步原语（multiprocessing）
- ⚠️ 注意死锁（统一加锁顺序）
- ⚠️ 减少锁粒度（提高并发）

**下一步：** [🏊 线程池与进程池](/04-concurrency/pool) — concurrent.futures


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
