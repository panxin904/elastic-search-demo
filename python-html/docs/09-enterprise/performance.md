---
title: 性能优化
date: 2026-08-15  # date-auto-injected
---

# 🚀 性能优化

> **性能优化**是 Python 后端开发的重要课题。本章从**测量、原则、技术**三个层面讲解。

## 🎯 性能优化原则

### 1. 不要过早优化

```
✅ 先写清晰的代码
✅ 测量瓶颈（profiling）
✅ 优化瓶颈（不是全部）
✅ 验证改进有效

❌ 凭直觉优化
❌ 过早优化
❌ 优化非热点代码
```

### 2. 测量优先

```
工具：
  - timeit：微基准
  - cProfile：函数级
  - line_profiler：行级
  - memory_profiler：内存
  - py-spy：生产采样
```

### 3. 复杂度优先

```
优化层次：
  1. 算法复杂度（O(n²) → O(n log n)）
  2. 数据结构（list 查找 → set/dict 查找）
  3. 库选择（Python → NumPy/Pandas）
  4. 并行（多线程、多进程、异步）
  5. 缓存（Redis、本地缓存）
  6. C 扩展（Cython、C 扩展）
```

## 🔧 代码层优化

### 选择合适的数据结构

```python
# ❌ 慢：list 查找 O(n)
items = [1, 2, 3, 4, 5, ..., 1000000]
if 999999 in items:  # 100 万次比较
    pass

# ✅ 快：set 查找 O(1)
items_set = set(items)
if 999999 in items_set:  # 1 次哈希
    pass
```

### 列表推导式 vs 循环

```python
import timeit

# ❌ 慢：循环 + append
def slow():
    result = []
    for i in range(1000):
        result.append(i ** 2)
    return result

# ✅ 快：列表推导式
def fast():
    return [i ** 2 for i in range(1000)]

# 性能差异
t1 = timeit.timeit(slow, number=1000)
t2 = timeit.timeit(fast, number=1000)
print(f"循环: {t1:.4f}s, 推导: {t2:.4f}s")
# 推导式快 2-3 倍
```

### 字符串拼接

```python
import timeit

# ❌ 慢：+ 拼接
def slow():
    s = ""
    for i in range(10000):
        s += str(i)
    return s

# ✅ 快：join
def fast():
    return "".join(str(i) for i in range(10000))

t1 = timeit.timeit(slow, number=10)
t2 = timeit.timeit(fast, number=10)
# join 快 10 倍+
```

### 生成器 vs 列表

```python
import sys

# ❌ 占内存：列表
def list_sum(n):
    nums = [i ** 2 for i in range(n)]  # 占用 O(n) 内存
    return sum(nums)

# ✅ 省内存：生成器
def gen_sum(n):
    return sum(i ** 2 for i in range(n))  # 占用 O(1) 内存

# 1 亿数据
print(sys.getsizeof(list_sum(100_000_000)))  # 巨大
print(sys.getsizeof(gen_sum(100_000_000)))   # 很小
```

### 局部变量 vs 全局变量

```python
import math

# ❌ 慢：全局变量
def slow_func():
    result = 0
    for i in range(100000):
        result += math.sin(i)  # 每次查找全局

# ✅ 快：局部变量
def fast_func():
    sin = math.sin  # 局部变量（快 10-20%）
    result = 0
    for i in range(100000):
        result += sin(i)
```

### 字典合并

```python
# ❌ 慢：多次 update
d = {}
d.update({"a": 1})
d.update({"b": 2})
d.update({"c": 3})

# ✅ 快：一次性构造
d = {**{"a": 1}, **{"b": 2}, **{"c": 3}}
# 或 Python 3.9+
d = {"a": 1} | {"b": 2} | {"c": 3}
```

## 🔧 并发优化

### 多线程（IO 密集）

```python
from concurrent.futures import ThreadPoolExecutor
import requests

def fetch(url):
    return requests.get(url).text

# 串行
urls = [f"https://api.example.com/data/{i}" for i in range(100)]
results = [fetch(url) for url in urls]  # 慢

# 并发
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(fetch, urls))  # 快 5-10 倍
```

### 多进程（CPU 密集）

```python
from concurrent.futures import ProcessPoolExecutor

def cpu_task(n):
    return sum(i * i for i in range(n))

# 多进程
if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(cpu_task, [10_000_000] * 4))
    # 4 核 CPU 接近 4 倍加速
```

### 异步（高并发 IO）

```python
import asyncio
import aiohttp

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def main():
    urls = [f"https://api.example.com/{i}" for i in range(1000)]
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
    # 单线程支持 1000+ 并发
```

## 🔧 缓存优化

### 本地缓存（functools.lru_cache）

```python
from functools import lru_cache
import time

# ❌ 慢：每次都计算
def fib_slow(n):
    if n < 2: return n
    return fib_slow(n-1) + fib_slow(n-2)
# fib_slow(35) 耗时 ~1.5 秒

# ✅ 快：缓存结果
@lru_cache(maxsize=128)
def fib_fast(n):
    if n < 2: return n
    return fib_fast(n-1) + fib_fast(n-2)
# fib_fast(35) 耗时 < 0.001 秒
```

### Redis 缓存

```python
import redis
import json

r = redis.Redis()

def get_user(user_id):
    # 1. 查缓存
    cached = r.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)
    
    # 2. 查 DB
    user = db.query("SELECT * FROM users WHERE id = %s", user_id)
    
    # 3. 写缓存
    r.setex(f"user:{user_id}", 3600, json.dumps(user))
    
    return user
```

### 缓存更新模式

```python
# 模式 1：Cache-Aside（最常用）
def get_data(key):
    if cached := cache.get(key):
        return cached
    data = db.fetch(key)
    cache.setex(key, 3600, data)
    return data

# 模式 2：Write-Through
def set_data(key, value):
    db.save(key, value)
    cache.setex(key, 3600, value)

# 模式 3：Write-Behind（异步）
async def set_data(key, value):
    db.save(key, value)
    await cache.setex(key, 3600, value)
```

## 🔧 数据库优化

### 索引

```sql
-- 单列索引
CREATE INDEX idx_user_email ON users(email);

-- 复合索引（最左前缀）
CREATE INDEX idx_user_status_created ON users(status, created_at);

-- 覆盖索引
CREATE INDEX idx_user_covering ON users(email, name, status);

-- 部分索引
CREATE INDEX idx_active_users ON users(id) WHERE status = 'active';
```

### 批量操作

```python
# ❌ 慢：逐条插入
for user in users:
    db.execute("INSERT INTO users (name, email) VALUES (?, ?)", 
               (user.name, user.email))
db.commit()  # 1000 次往返

# ✅ 快：批量插入
db.executemany(
    "INSERT INTO users (name, email) VALUES (?, ?)",
    [(u.name, u.email) for u in users]
)
db.commit()  # 1 次往返
```

### 连接池

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    "postgresql://user:pass@localhost/db",
    pool_size=20,           # 连接池大小
    max_overflow=10,        # 最大溢出
    pool_pre_ping=True,     # 健康检查
    pool_recycle=3600,      # 回收时间
)
```

## 🔧 Web 优化

### Gzip 压缩

```python
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)
# 响应 > 1KB 自动压缩
```

### 缓存 HTTP 响应

```python
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

app = FastAPI()

@app.on_event("startup")
async def startup():
    FastAPICache.init(RedisBackend(), prefix="cache:")

@app.get("/users")
@cache(expire=60)  # 缓存 60 秒
async def get_users():
    # 业务逻辑
    return await db.fetch_all("SELECT * FROM users")
```

### 异步处理

```python
from fastapi import FastAPI, BackgroundTasks

app = FastAPI()

@app.post("/orders")
async def create_order(order: Order, background_tasks: BackgroundTasks):
    # 1. 立即处理（保存订单）
    order_id = await save_order(order)
    
    # 2. 异步处理（发送邮件、发短信等）
    background_tasks.add_task(send_confirmation_email, order_id)
    background_tasks.add_task(update_inventory, order_id)
    
    return {"order_id": order_id, "status": "created"}
```

## 🔧 性能监控

### APM 工具

```python
# New Relic
import newrelic.agent
newrelic.agent.initialize()

# Datadog
from ddtrace import tracer, patch
patch(flask=True)  # 自动埋点

# Prometheus + Grafana
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter("requests_total", "Total requests", ["method", "endpoint"])
REQUEST_LATENCY = Histogram("request_latency_seconds", "Request latency")

@app.middleware("http")
async def monitor(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_LATENCY.observe(duration)
    
    return response
```

## 🔧 性能优化清单

```markdown
✅ 算法和数据结构
  - 选择合适的数据结构
  - 优化算法复杂度

✅ 代码层
  - 使用局部变量
  - 避免重复计算
  - 列表推导式
  - 字符串 join

✅ 并发
  - IO 密集：多线程 / asyncio
  - CPU 密集：多进程
  - 高并发：asyncio

✅ 缓存
  - 内存缓存（lru_cache）
  - Redis 缓存
  - HTTP 缓存

✅ 数据库
  - 索引优化
  - 批量操作
  - 连接池
  - 读写分离

✅ Web
  - 压缩（Gzip）
  - 缓存（Redis）
  - 异步处理
  - CDN

✅ 监控
  - APM 工具
  - Prometheus
  - 性能分析
```

## 🎯 总结

**性能优化核心要点**：
- ✅ 先测量，后优化（cProfile）
- ✅ 算法复杂度优先（O(n²) → O(n log n)）
- ✅ 选择合适数据结构（O(1) vs O(n)）
- ✅ 并发利用多核（线程 / 进程 / 异步）
- ✅ 缓存减少计算
- ✅ 数据库索引和批量操作
- ✅ Web 压缩和缓存
- ⚠️ 不要过早优化
- ⚠️ 优化前先测量

**下一步：** [🌐 FastAPI Web 实战](/09-enterprise/fastapi) — 现代 Python Web 框架


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

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [java](https://java-px.bot.cd/java-web-manual/):Java 对比
- [ai](https://java-px.bot.cd/ai/):AI / 机器学习
- [bigdata](https://java-px.bot.cd/bigdata/):大数据 / 数据处理
