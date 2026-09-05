---
title: asyncio 协程
date: 2026-08-15  # date-auto-injected
---

# ⚡ asyncio 协程
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600">Python asyncio 事件循环</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">单线程协作式调度 · await 让出执行权</text>

  <!-- 事件循环 -->
  <ellipse cx="300" cy="250" rx="160" ry="55" fill="#dcfce7" stroke="#10b981" stroke-width="2"/>
  <text x="300" y="245" text-anchor="middle" font-size="13" font-weight="700" fill="#047857">Event Loop</text>
  <text x="300" y="263" text-anchor="middle" font-size="11" fill="#475569">asyncio.run()</text>

  <!-- 协程 1 -->
  <rect class="at-hover-card" x="40" y="115" width="120" height="50" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="100" y="138" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">Coroutine A</text>
  <text x="100" y="155" text-anchor="middle" font-size="9" fill="#475569">await fetch()</text>

  <!-- 协程 2 -->
  <rect class="at-hover-card" x="40" y="335" width="120" height="50" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="100" y="358" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">Coroutine B</text>
  <text x="100" y="375" text-anchor="middle" font-size="9" fill="#475569">await db()</text>

  <!-- 协程 3 -->
  <rect class="at-hover-card" x="440" y="115" width="120" height="50" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="500" y="138" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">Coroutine C</text>
  <text x="500" y="155" text-anchor="middle" font-size="9" fill="#475569">await sleep()</text>

  <!-- 协程 4 -->
  <rect class="at-hover-card" x="440" y="335" width="120" height="50" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="500" y="358" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">Coroutine D</text>
  <text x="500" y="375" text-anchor="middle" font-size="9" fill="#475569">await queue.get()</text>

  <!-- 双向箭头 -->
  <line x1="160" y1="140" x2="200" y2="220" stroke="#64748b" stroke-width="1.5" marker-end="url(#arr)" marker-start="url(#arr)"/>
  <line x1="160" y1="360" x2="200" y2="280" stroke="#64748b" stroke-width="1.5" marker-end="url(#arr)" marker-start="url(#arr)"/>
  <line x1="440" y1="140" x2="400" y2="220" stroke="#64748b" stroke-width="1.5" marker-end="url(#arr)" marker-start="url(#arr)"/>
  <line x1="440" y1="360" x2="400" y2="280" stroke="#64748b" stroke-width="1.5" marker-end="url(#arr)" marker-start="url(#arr)"/>

  <!-- Ready queue -->
  <rect x="195" y="115" width="210" height="50" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="4,2"/>
  <text x="300" y="138" text-anchor="middle" font-size="11" font-weight="700" fill="#92400e">Ready Queue</text>
  <text x="300" y="155" text-anchor="middle" font-size="9" fill="#475569">asyncio.Queue / Task</text>

  <!-- IO 多路复用 -->
  <rect x="195" y="335" width="210" height="50" rx="6" fill="#ede9fe" stroke="#8b5cf6" stroke-width="1.5" stroke-dasharray="4,2"/>
  <text x="300" y="358" text-anchor="middle" font-size="11" font-weight="700" fill="#5b21b6">Selector (epoll/kqueue)</text>
  <text x="300" y="375" text-anchor="middle" font-size="9" fill="#475569">监听 fd 就绪事件</text>

  <!-- 步骤说明 -->
  <rect x="30" y="400" width="540" height="65" rx="6" fill="#f1f5f9" stroke="#cbd5e1"/>
  <text x="300" y="422" text-anchor="middle" font-size="12" font-weight="700" fill="#1e293b">执行流程</text>
  <text x="50" y="442" font-size="10" fill="#334155">① 调度协程 → ② 遇到 await 让出 → ③ 注册到 Selector</text>
  <text x="50" y="458" font-size="10" fill="#334155">④ 阻塞等待 fd 就绪 → ⑤ 唤醒协程 → 回到 Ready → 继续</text>
</svg>


> **asyncio** 是 Python 3.4+ 引入的**异步 I/O 框架**。用**协程（coroutine）**实现高并发，是 IO 密集型任务的**最佳选择**。

![Python Asyncio Event Loop](/python-asyncio-event-loop.svg)

## 🎯 为什么用 asyncio？

```
单线程异步的革命性优势：
  ✅ 极高的并发（单线程支持数千连接）
  ✅ 极低的资源占用（无线程切换开销）
  ✅ 避免 GIL 限制（IO 等待时让出）
  ✅ 优雅的语法（async/await）

对比：
  - threading：100 并发需要 100 线程
  - asyncio：100 并发只需要 1 线程
  - asyncio + aiohttp：单机可处理 10K+ 连接
```

## 🚀 快速开始

### Hello World

```python
import asyncio

async def hello():
    print("Hello")
    await asyncio.sleep(1)
    print("World")

# 运行
asyncio.run(hello())
# Hello
# World（1 秒后）
```

### 串行 vs 并发

```python
import asyncio
import time

async def task(n):
    print(f"Task {n} starting")
    await asyncio.sleep(1)
    print(f"Task {n} done")
    return n

async def main():
    # 串行：~3 秒
    start = time.time()
    await task(1)
    await task(2)
    await task(3)
    print(f"串行: {time.time() - start:.2f}s")
    
    # 并发：~1 秒
    start = time.time()
    await asyncio.gather(task(1), task(2), task(3))
    print(f"并发: {time.time() - start:.2f}s")

asyncio.run(main())
```

## 📝 async / await 语法

### async def

```python
import asyncio

# 定义协程函数
async def fetch_data(url):
    print(f"Fetching {url}")
    await asyncio.sleep(1)  # 模拟 IO
    return {"url": url, "data": "..."}

# 调用协程（必须 await）
async def main():
    result = await fetch_data("https://api.example.com")
    print(result)

asyncio.run(main())
```

### await

```python
import asyncio

# await 后必须是 awaitable 对象
# - coroutine
# - Future
# - Task

async def main():
    # await 协程
    result = await fetch_data("url")
    
    # await Task
    task = asyncio.create_task(fetch_data("url"))
    result = await task
```

## 🚀 Task（任务）

### 创建 Task

```python
import asyncio

async def task(name, delay):
    print(f"Task {name} starting")
    await asyncio.sleep(delay)
    print(f"Task {name} done")
    return name

async def main():
    # 创建 Task（不等待）
    t1 = asyncio.create_task(task("A", 1))
    t2 = asyncio.create_task(task("B", 2))
    t3 = asyncio.create_task(task("C", 3))
    
    # 等待所有完成
    await asyncio.gather(t1, t2, t3)
    
    # 或单独等待
    # await t1
    # await t2
    # await t3
    
    print("All done")

asyncio.run(main())
```

### asyncio.gather

```python
import asyncio

async def fetch(url):
    await asyncio.sleep(1)
    return f"data from {url}"

async def main():
    # 并发执行多个协程
    urls = ["url1", "url2", "url3", "url4", "url5"]
    results = await asyncio.gather(*[fetch(u) for u in urls])
    print(results)
    
    # return_exceptions=True：异常不中断
    results = await asyncio.gather(
        *[fetch(u) for u in urls],
        return_exceptions=True
    )
    for url, r in zip(urls, results):
        if isinstance(r, Exception):
            print(f"{url}: error {r}")
        else:
            print(f"{url}: {r}")
```

### asyncio.create_task

```python
import asyncio

async def background_task():
    while True:
        await asyncio.sleep(1)
        print("Background tick")

async def main():
    # 启动后台任务
    task = asyncio.create_task(background_task())
    
    # 主任务
    await asyncio.sleep(3)
    print("Main done")
    
    # 取消后台任务
    task.cancel()

asyncio.run(main())
```

## ⏱️ 超时

```python
import asyncio

async def slow_task():
    await asyncio.sleep(10)
    return "done"

async def main():
    try:
        result = await asyncio.wait_for(slow_task(), timeout=2.0)
        print(result)
    except asyncio.TimeoutError:
        print("Timeout!")

asyncio.run(main())
```

## 🔒 同步原语

### Lock

```python
import asyncio

lock = asyncio.Lock()
counter = 0

async def worker():
    global counter
    for _ in range(1000):
        async with lock:
            counter += 1

async def main():
    tasks = [asyncio.create_task(worker()) for _ in range(10)]
    await asyncio.gather(*tasks)
    print(counter)  # 10000

asyncio.run(main())
```

### Semaphore

```python
import asyncio

sem = asyncio.Semaphore(3)

async def access(i):
    async with sem:
        print(f"Task {i} acquired")
        await asyncio.sleep(1)

async def main():
    tasks = [asyncio.create_task(access(i)) for i in range(10)]
    await asyncio.gather(*tasks)

asyncio.run(main())
# 3 个并发
```

### Event

```python
import asyncio

event = asyncio.Event()

async def waiter():
    print("Waiting...")
    await event.wait()
    print("Done!")

async def setter():
    await asyncio.sleep(2)
    event.set()

async def main():
    await asyncio.gather(waiter(), setter())

asyncio.run(main())
```

### Queue

```python
import asyncio

async def producer(queue):
    for i in range(5):
        await queue.put(i)
        await asyncio.sleep(0.1)

async def consumer(queue):
    while True:
        item = await queue.get()
        print(f"Consumed: {item}")
        if item == 4:
            break

async def main():
    queue = asyncio.Queue()
    await asyncio.gather(producer(queue), consumer(queue))

asyncio.run(main())
```

## 🛠️ 实战：异步 HTTP 客户端

```python
import asyncio
import aiohttp

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.json()

async def main():
    urls = [f"https://api.example.com/data/{i}" for i in range(100)]
    
    async with aiohttp.ClientSession() as session:
        # 并发 100 个请求
        tasks = [fetch(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        for url, data in zip(urls, results):
            print(f"{url}: {data}")

asyncio.run(main())
```

## 🛠️ 实战：异步文件 IO

```python
import asyncio
import aiofiles

async def read_file(path):
    async with aiofiles.open(path, "r") as f:
        content = await f.read()
    return content

async def write_file(path, content):
    async with aiofiles.open(path, "w") as f:
        await f.write(content)

async def main():
    # 异步读多个文件
    paths = ["file1.txt", "file2.txt", "file3.txt"]
    contents = await asyncio.gather(*[read_file(p) for p in paths])
    print(contents)

asyncio.run(main())
```

## 🛠️ 实战：异步生产者-消费者

```python
import asyncio

async def producer(queue):
    for i in range(10):
        await queue.put(f"item-{i}")
        await asyncio.sleep(0.1)
    await queue.put(None)  # 结束信号

async def consumer(queue):
    while True:
        item = await queue.get()
        if item is None:
            break
        print(f"Consumed: {item}")
        await asyncio.sleep(0.2)

async def main():
    queue = asyncio.Queue(maxsize=5)
    await asyncio.gather(producer(queue), consumer(queue))

asyncio.run(main())
```

## 📊 异步库推荐

```
✅ aiohttp - 异步 HTTP 客户端/服务器
✅ aiofiles - 异步文件 IO
✅ asyncpg - 异步 PostgreSQL
✅ aiomysql - 异步 MySQL
✅ aioredis - 异步 Redis
✅ motor - 异步 MongoDB
✅ httpx - 同步/异步 HTTP 客户端
```

## 🎯 总结

**asyncio 核心要点**：
- ✅ async def 定义协程，await 调用
- ✅ asyncio.gather 并发执行
- ✅ asyncio.create_task 创建任务
- ✅ asyncio.Queue 异步队列
- ✅ asyncio.Lock / Semaphore / Event 同步
- ✅ 适合 IO 密集型（HTTP、数据库、文件）
- ✅ 极高的并发（单线程数千连接）
- ⚠️ 不要在协程中调用阻塞 IO
- ⚠️ 异步库需要专门支持（aiohttp 等）

**下一步：** [🔁 同步原语](/04-concurrency/sync-primitives) — 多线程同步工具


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
