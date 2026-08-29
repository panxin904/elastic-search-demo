---
title: 限流与重试
date: 2026-08-29  # date-auto-injected
---

# 🚧 限流、重试与错误码

> API 调用不可避免会遇到限流、超时、5xx 错误。掌握正确的重试策略是生产环境稳定性的关键。

## 🚦 限流机制

### 三种限流维度

| 维度 | 说明 | 典型值（GPT-4o） |
|------|------|------------------|
| **RPM** (Requests Per Minute) | 每分钟请求数 | 500 / 5000（按 tier） |
| **TPM** (Tokens Per Minute) | 每分钟 token 数 | 30K / 250K |
| **并发数** | 同时进行的请求数 | 50-200 |

## 📥 限流响应

### HTTP 状态码

| 状态码 | 含义 | 处理 |
|--------|------|------|
| `200` | 成功 | - |
| `400` | 请求格式错误 | 修复请求 |
| `401` | API Key 无效 | 检查 key |
| `403` | 权限不足 | 检查 scope |
| `404` | 模型不存在 | 检查 model 名称 |
| `429` | **限流** | 重试（带退避） |
| `500` | 服务端错误 | 重试 |
| `502/503/504` | 网关/上游错误 | 重试 |
| `529` | Anthropic 过载 | 重试 |

### 响应头（关键）

```http
HTTP/1.1 429 Too Many Requests
retry-after: 23
x-ratelimit-limit-requests: 500
x-ratelimit-remaining-requests: 0
x-ratelimit-reset-requests: 23s
```

| Header | 含义 |
|--------|------|
| `retry-after` | 多少秒后重试（OpenAI / Anthropic 都支持） |
| `x-ratelimit-limit-requests` | RPM 上限 |
| `x-ratelimit-remaining-requests` | 剩余请求数 |
| `x-ratelimit-reset-requests` | 限额重置时间 |
| `x-request-id` | 请求 ID（工单排查用） |

## 🔄 重试策略

### 1. 指数退避（Exponential Backoff）

```python
import time
import random
import httpx

def call_with_retry(func, max_retry=5, base_delay=1.0, max_delay=60.0):
    for attempt in range(max_retry):
        try:
            return func()
        except (httpx.ReadError, httpx.ConnectError) as e:
            if attempt == max_retry - 1:
                raise
            # 指数退避 + 抖动
            delay = min(base_delay * (2 ** attempt), max_delay)
            delay *= (0.5 + random.random())  # 0.5-1.5x 抖动
            print(f"Retry {attempt+1}/{max_retry} after {delay:.1f}s: {e}")
            time.sleep(delay)
        except Exception as e:
            # 检查是否是可重试错误
            if hasattr(e, "status_code"):
                if e.status_code in (429, 500, 502, 503, 504, 529):
                    retry_after = float(e.headers.get("retry-after", 1))
                    if attempt == max_retry - 1:
                        raise
                    delay = retry_after + random.uniform(0, 1)
                    print(f"Retry {attempt+1}/{max_retry} after {delay:.1f}s (retry-after)")
                    time.sleep(delay)
                    continue
            raise
```

### 2. OpenAI SDK 内置重试

```python
from openai import OpenAI

client = OpenAI(
    max_retries=5,  # 默认 2
    timeout=60.0,   # 默认 60s
)
```

### 3. Anthropic SDK 内置重试

```python
import anthropic

client = anthropic.Anthropic(
    max_retries=5,
    timeout=60.0,
)
```

## 🛑 限流应对（生产级）

### 1. 客户端并发控制

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()
semaphore = asyncio.Semaphore(10)  # 最多 10 并发

async def bounded_call(prompt):
    async with semaphore:
        return await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )

# 即使发起 1000 个任务，最多 10 个同时执行
tasks = [bounded_call(f"question {i}") for i in range(1000)]
results = await asyncio.gather(*tasks)
```

### 2. 令牌桶限流

```python
import time

class TokenBucket:
    def __init__(self, rate_per_minute=500):
        self.capacity = rate_per_minute
        self.tokens = rate_per_minute
        self.refill_rate = rate_per_minute / 60  # tokens per second
        self.last_refill = time.time()

    def acquire(self, tokens=1):
        while True:
            now = time.time()
            elapsed = now - self.last_refill
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            self.last_refill = now
            if self.tokens >= tokens:
                self.tokens -= tokens
                return
            time.sleep((tokens - self.tokens) / self.refill_rate)

bucket = TokenBucket(rate_per_minute=500)

def call_with_bucket(prompt):
    bucket.acquire()
    return client.chat.completions.create(...)
```

### 3. 多 Key 轮询

```python
import random
from openai import OpenAI

keys = ["sk-key1", "sk-key2", "sk-key3"]
clients = [OpenAI(api_key=k) for k in keys]

def call_with_key_rotation(prompt):
    client = random.choice(clients)
    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
```

## 🚨 流式场景的特殊处理

### 1. 客户端断开检测

```python
async def stream_with_disconnect_check(stream, request):
    last_chunk_time = time.time()
    try:
        async for chunk in stream:
            last_chunk_time = time.time()
            yield chunk
    except (httpx.ReadError, asyncio.CancelledError):
        # 客户端断开
        return
```

### 2. 心跳超时

Anthropic SSE 每 5-15 秒会发 `ping` 事件。如果 60 秒没收到任何事件，应断开重连：

```python
PING_TIMEOUT = 60

async for event in stream:
    if time.time() - last_event_time > PING_TIMEOUT:
        log.warning("SSE timeout, reconnecting")
        break
```

## 🔍 错误码字典

### OpenAI

| Code | Message | 处理 |
|------|---------|------|
| `invalid_api_key` | Incorrect API key | 检查 key |
| `insufficient_quota` | You exceeded your current quota | 充值 |
| `model_not_found` | The model does not exist | 检查 model 名 |
| `context_length_exceeded` | max_tokens too large or messages too long | 减少 input 或 max_tokens |
| `rate_limit_exceeded` | Too many requests | 退避重试 |
| `server_error` | Internal server error | 退避重试 |
| `timeout` | Request timed out | 退避重试 |

### Anthropic

| Type | Message | 处理 |
|------|---------|------|
| `authentication_error` | invalid x-api-key | 检查 key |
| `permission_error` | API Key does not have required scope | 检查权限 |
| `not_found_error` | model not found | 检查 model 名 |
| `rate_limit_error` | Number of requests exceeded | 退避重试 |
| `api_error` | Internal server error | 退避重试 |
| `overloaded_error` | API is temporarily overloaded | 退避重试 |

## 📊 监控指标（生产必备）

```python
import time
from dataclasses import dataclass, field

@dataclass
class APIMetrics:
    total_calls: int = 0
    success_calls: int = 0
    retry_calls: int = 0
    failed_calls: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_latency_ms: float = 0
    error_breakdown: dict = field(default_factory=dict)

    def record(self, response, latency_ms, attempt):
        self.total_calls += 1
        self.total_latency_ms += latency_ms
        if attempt > 1:
            self.retry_calls += 1
        if response and hasattr(response, "usage"):
            self.success_calls += 1
            self.total_input_tokens += response.usage.prompt_tokens
            self.total_output_tokens += response.usage.completion_tokens
        else:
            self.failed_calls += 1
            # 按 status code 分类

    @property
    def success_rate(self):
        return self.success_calls / max(self.total_calls, 1)
```

## 🔧 LangChain 集成（高级）

```python
from langchain_openai import ChatOpenAI
from langchain_core.rate_limiters import InMemoryRateLimiter

rate_limiter = InMemoryRateLimiter(
    requests_per_second=10,  # 10 RPS
    check_every_n_seconds=0.1,
    max_bucket_size=10,
)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    rate_limiter=rate_limiter,
    max_retries=3,
)

# 自动限流 + 重试
response = llm.invoke("hello")
```

## 🔗 关联章节

- [context-tokens](./context-tokens) - TPM 限流
- [streaming-protocol](./streaming-protocol) - 流式断流处理
- [13-security/cost](../13-security/cost) - 成本监控
