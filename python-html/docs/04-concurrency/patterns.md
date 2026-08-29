---
title: 并发模式
---

# 🎯 并发模式

> 掌握**经典并发设计模式**能让你写出**高质量、高性能**的并发代码。本章介绍 8 种最常用的并发模式。

## 🎯 模式 1：Future 模式

```python
from concurrent.futures import ThreadPoolExecutor
import time

def task(n):
    time.sleep(1)
    return n * 2

# 提交任务，立即返回 Future
with ThreadPoolExecutor() as executor:
    future1 = executor.submit(task, 10)
    future2 = executor.submit(task, 20)
    
    # 主线程继续做其他事
    print("Main thread doing other work")
    
    # 稍后获取结果
    r1 = future1.result()
    r2 = future2.result()
    print(f"Results: {r1}, {r2}")
```

## 🎯 模式 2：Producer-Consumer（生产者-消费者）

```python
import asyncio
from asyncio import Queue

async def producer(queue):
    for i in range(10):
        await queue.put(f"item-{i}")
        print(f"Produced: item-{i}")
        await asyncio.sleep(0.1)

async def consumer(queue, name):
    while True:
        try:
            item = await asyncio.wait_for(queue.get(), timeout=1)
            print(f"Consumer {name} got: {item}")
            await asyncio.sleep(0.2)
        except asyncio.TimeoutError:
            break

async def main():
    queue = Queue(maxsize=5)
    await asyncio.gather(
        producer(queue),
        consumer(queue, "A"),
        consumer(queue, "B")
    )

asyncio.run(main())
```

## 🎯 模式 3：Worker Pool（工作池）

```python
from concurrent.futures import ThreadPoolExecutor
import queue
import threading
import time

def worker_pool(tasks_queue, results_queue, n_workers=3):
    """工作池模式"""
    def worker():
        while True:
            try:
                task = tasks_queue.get(timeout=1)
            except queue.Empty:
                break
            
            # 处理任务
            result = f"Processed: {task}"
            results_queue.put(result)
            tasks_queue.task_done()
    
    threads = [threading.Thread(target=worker) for _ in range(n_workers)]
    for t in threads: t.start()
    for t in threads: t.join()

# 使用
tasks_queue = queue.Queue()
results_queue = queue.Queue()

for i in range(10):
    tasks_queue.put(f"task-{i}")

worker_pool(tasks_queue, results_queue, n_workers=3)

# 收集结果
while not results_queue.empty():
    print(results_queue.get())
```

## 🎯 模式 4：Pipeline（流水线）

```python
import asyncio

async def stage1(queue_in, queue_out):
    """阶段 1：接收原始数据"""
    for i in range(10):
        data = f"raw-{i}"
        await queue_in.put(data)
    await queue_in.put(None)  # 结束标记

async def stage2(queue_in, queue_out):
    """阶段 2：处理数据"""
    while True:
        data = await queue_in.get()
        if data is None:
            await queue_out.put(None)
            break
        processed = f"processed({data})"
        await queue_out.put(processed)

async def stage3(queue_in):
    """阶段 3：最终处理"""
    while True:
        data = await queue_in.get()
        if data is None:
            break
        print(f"Final: {data}")

async def main():
    q1, q2, q3 = asyncio.Queue(), asyncio.Queue(), asyncio.Queue()
    await asyncio.gather(
        stage1(q1, q2),
        stage2(q2, q3),
        stage3(q3)
    )

asyncio.run(main())
```

## 🎯 模式 5：Pub-Sub（发布订阅）

```python
import asyncio

class EventBus:
    def __init__(self):
        self.subscribers = {}
    
    def subscribe(self, event_type, callback):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    async def publish(self, event_type, data):
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)

bus = EventBus()

# 订阅
async def on_user_created(user):
    print(f"Email service: Sending welcome to {user}")

bus.subscribe("user_created", on_user_created)

# 发布
async def main():
    await bus.publish("user_created", {"name": "Alice", "email": "alice@example.com"})

asyncio.run(main())
```

## 🎯 模式 6：Promise 模式

```python
import asyncio

class Promise:
    def __init__(self):
        self.future = asyncio.Future()
    
    def resolve(self, value):
        self.future.set_result(value)
    
    def reject(self, error):
        self.future.set_exception(error)
    
    async def then(self, callback):
        try:
            result = await self.future
            return callback(result)
        except Exception as e:
            print(f"Error: {e}")

# 使用
async def main():
    promise = Promise()
    
    async def consume():
        result = await promise.then(lambda x: x * 2)
        print(f"Result: {result}")
    
    asyncio.create_task(consume())
    await asyncio.sleep(0.1)
    promise.resolve(21)

asyncio.run(main())
# Result: 42
```

## 🎯 模式 7：Semaphore 控制并发

```python
import asyncio
import time

sem = asyncio.Semaphore(3)  # 最多 3 个并发

async def access(i):
    async with sem:
        print(f"Task {i} acquired")
        await asyncio.sleep(1)
        print(f"Task {i} released")

async def main():
    # 100 个任务，最多 3 个并发
    await asyncio.gather(*[access(i) for i in range(100)])

asyncio.run(main())
# 3 个并发处理，约 33 秒完成（vs ~100 秒无信号量）
```

## 🎯 模式 8：Map-Reduce

```python
from concurrent.futures import ThreadPoolExecutor
from functools import reduce

# Map：并行处理
def mapper(n):
    return n ** 2

# Reduce：聚合
def reducer(a, b):
    return a + b

with ThreadPoolExecutor() as executor:
    # Map 阶段
    mapped = list(executor.map(mapper, [1, 2, 3, 4, 5]))
    print(f"Mapped: {mapped}")  # [1, 4, 9, 16, 25]
    
    # Reduce 阶段
    result = reduce(reducer, mapped)
    print(f"Result: {result}")  # 55
```

## 🛠️ 实战：限流器

```python
import asyncio
import time

class RateLimiter:
    """令牌桶限流器"""
    def __init__(self, rate=10, per=1.0):
        self.rate = rate        # 令牌数
        self.per = per          # 时间窗口
        self.tokens = rate      # 当前令牌
        self.last_refill = time.time()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_refill
            # 补充令牌
            self.tokens = min(self.rate, self.tokens + elapsed * (self.rate / self.per))
            self.last_refill = now
            
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False
    
    async def wait_and_acquire(self):
        while not await self.acquire():
            await asyncio.sleep(0.1)

# 使用
limiter = RateLimiter(rate=5, per=1.0)

async def api_call(i):
    await limiter.wait_and_acquire()
    print(f"Request {i} at {time.time():.2f}")

async def main():
    await asyncio.gather(*[api_call(i) for i in range(20)])

asyncio.run(main())
# 每秒最多 5 个请求
```

## 🛠️ 实战：分布式锁（基于 Redis）

```python
import asyncio
import aioredis

class DistributedLock:
    def __init__(self, redis, key, timeout=10):
        self.redis = redis
        self.key = f"lock:{key}"
        self.timeout = timeout
        self.value = None
    
    async def __aenter__(self):
        # SET key value NX EX timeout
        self.value = f"{id(self)}"
        acquired = await self.redis.set(
            self.key, self.value, nx=True, ex=self.timeout
        )
        if not acquired:
            raise RuntimeError(f"Failed to acquire lock: {self.key}")
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        # Lua 脚本：只删除自己持有的锁
        lua = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        await self.redis.eval(lua, 1, self.key, self.value)

# 使用
async def main():
    redis = aioredis.from_url("redis://localhost")
    async with DistributedLock(redis, "order:1001") as lock:
        # 临界区
        print("Lock acquired")
        await asyncio.sleep(1)
        print("Lock released")

asyncio.run(main())
```

## 🛠️ 实战：批量处理（Batch）

```python
import asyncio
from collections import deque

class BatchProcessor:
    """批量处理器：累积 N 个任务后批量处理"""
    def __init__(self, batch_size=10, flush_interval=1.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.queue = asyncio.Queue()
        self.buffer = []
    
    async def add(self, item):
        await self.queue.put(item)
    
    async def process_loop(self, handler):
        while True:
            try:
                item = await asyncio.wait_for(
                    self.queue.get(), 
                    timeout=self.flush_interval
                )
                self.buffer.append(item)
                
                # 达到批大小就处理
                if len(self.buffer) >= self.batch_size:
                    await self._flush(handler)
            except asyncio.TimeoutError:
                # 超时也处理（避免数据堆积）
                if self.buffer:
                    await self._flush(handler)
    
    async def _flush(self, handler):
        if not self.buffer:
            return
        batch = self.buffer.copy()
        self.buffer.clear()
        await handler(batch)

# 使用
async def save_batch(items):
    print(f"Saving {len(items)} items to DB")

async def main():
    processor = BatchProcessor(batch_size=5, flush_interval=2.0)
    
    asyncio.create_task(processor.process_loop(save_batch))
    
    for i in range(20):
        await processor.add(f"item-{i}")
        await asyncio.sleep(0.3)
    
    await asyncio.sleep(3)

asyncio.run(main())
```

## 🎯 总结

**经典并发模式核心要点**：
- ✅ Future 模式：异步获取结果
- ✅ Producer-Consumer：解耦生产和消费
- ✅ Worker Pool：控制并发数
- ✅ Pipeline：多阶段流水线
- ✅ Pub-Sub：事件驱动
- ✅ Promise：链式异步操作
- ✅ Semaphore：限流
- ✅ Map-Reduce：分布式计算
- ⚠️ 死锁（统一加锁顺序）
- ⚠️ 活锁（随机退避）
- ⚠️ 资源耗尽（限流 + 监控）

**下一步：** [🎯 爬虫基础](/05-scraping/basics) — Python 爬虫入门


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

## 🔗 相关阅读 · 04 并发

<!-- xlink-subpage-injected:do-not-edit -->

本页（04 并发）相关主题的跨站入口:

- [java](https://java-px.bot.cd/java-web-manual/):Java 对比
- [ai](https://java-px.bot.cd/ai/):AI / 机器学习
- [bigdata](https://java-px.bot.cd/bigdata/):大数据 / 数据处理
