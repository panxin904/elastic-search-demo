---
title: DeepSeek Harness 实战教程
date: 2026-09-14  # date-auto-injected
---

# 🎯 DeepSeek 实战教程

> 7 个生产级实战场景：RAG、Agent、Code Review、批量处理、监控、流式输出优化、跨服务调用。每个都附可运行代码。

## 🍜 实战 1：构建 RAG 知识库问答

### 完整代码

```python
"""
RAG 客服助手：基于 DeepSeek-V3 + ChromaDB
"""
import os
from openai import OpenAI
import chromadb

# 1. 初始化 DeepSeek
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

# 2. 初始化向量库
chroma = chromadb.PersistentClient(path="./chroma_data")
collection = chroma.get_or_create_collection("knowledge")

# 3. 文档切片 → embedding → 入库
def embed(texts):
    # 用 DeepSeek API 也支持 embedding
    # 或用本地 bge-m3 / m3e
    resp = client.embeddings.create(
        model="text-embedding-v3",     # DeepSeek embedding 模型
        input=texts
    )
    return [e.embedding for e in resp.data]

documents = [
    "退款政策：购买 7 天内可全额退款",
    "配送时效：江浙沪 24 小时，其他地区 3-5 天",
    "会员等级：银牌 9 折，金牌 8 折，钻石 7 折",
]
collection.add(
    documents=documents,
    embeddings=embed(documents),
    ids=[f"doc-{i}" for i in range(len(documents))]
)

# 4. RAG 查询
def rag_query(question: str) -> str:
    # 4.1 检索
    results = collection.query(
        query_embeddings=embed([question]),
        n_results=3
    )
    context = "\n".join(results["documents"][0])

    # 4.2 拼 prompt（缓存 system，节省成本）
    system_prompt = f"""你是客服助手，仅基于以下资料回答：
{context}

规则：
1. 资料外的问题直接说"暂不了解"
2. 引用处用 [1][2] 标记
3. 简洁友好"""

    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        temperature=0.3
    )
    return resp.choices[0].message.content

# 5. 测试
print(rag_query("金牌会员打几折？"))
# 输出："金牌会员享受 8 折优惠 [3]。"

print(rag_query("能不能开发票？"))
# 输出："暂不了解。"
```

## 🤖 实战 2：构建 Multi-Agent 编程助手

```python
"""
Multi-Agent：架构师 + 程序员 + 测试员
"""
from openai import OpenAI
import json

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

def call_agent(role, messages, tools=None):
    return client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "system", "content": role}] + messages,
        tools=tools
    )

ARCHITECT = """你是架构师，负责把需求拆解成技术方案。
输出 JSON：{"plan": [...], "tech_stack": [...]}"""

CODER = """你是程序员，按架构师方案写代码。
输出 Python 代码块。"""

TESTER = """你是测试员，写 5 个测试用例覆盖边界条件。
输出 pytest 代码块。"""

def multi_agent_pipeline(requirement):
    # Step 1: 架构师出方案
    plan_resp = call_agent(ARCHITECT, [
        {"role": "user", "content": requirement}
    ])
    plan = plan_resp.choices[0].message.content

    # Step 2: 程序员写代码
    code_resp = call_agent(CODER, [
        {"role": "user", "content": f"需求：{requirement}\n方案：{plan}"}
    ])
    code = code_resp.choices[0].message.content

    # Step 3: 测试员补测试
    test_resp = call_agent(TESTER, [
        {"role": "user", "content": f"代码：{code}"}
    ])
    tests = test_resp.choices[0].message.content

    return {"plan": plan, "code": code, "tests": tests}

result = multi_agent_pipeline("写一个分布式限流器")
print(json.dumps(result, indent=2, ensure_ascii=False))
```

## 🔍 实战 3：Code Review 自动化

```python
"""
Git diff → DeepSeek-V3 → PR 评论
"""
import subprocess

def get_diff(file_path):
    result = subprocess.run(
        ["git", "diff", "HEAD~1", "--", file_path],
        capture_output=True, text=True
    )
    return result.stdout

def review_code(diff):
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": """你是高级 Python 工程师，审查代码 diff。
输出格式：
- 🔴 严重问题（必须修）
- 🟡 建议优化
- 🟢 不错
每条带行号引用。"""},
            {"role": "user", "content": f"```diff\n{diff}\n```"}
        ],
        temperature=0.2
    )
    return resp.choices[0].message.content

# 集成到 GitHub Actions
review = review_code(get_diff("src/main.py"))
print(review)
# 提交到 PR 评论
```

## 📦 实战 4：批量并发处理

```python
"""
asyncio 并发 50 个请求
"""
import asyncio
from openai import AsyncOpenAI

async_client = AsyncOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

async def process_one(text):
    resp = await async_client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": f"翻译成英文：{text}"}]
    )
    return resp.choices[0].message.content

async def batch_translate(texts, concurrency=50):
    semaphore = asyncio.Semaphore(concurrency)

    async def limited(text):
        async with semaphore:
            return await process_one(text)

    return await asyncio.gather(*[limited(t) for t in texts])

# 跑批
texts = ["你好", "世界", "再见"] * 100
results = asyncio.run(batch_translate(texts))
print(f"完成 {len(results)} 个翻译")
```

## 📊 实战 5：成本监控

```python
"""
实时统计 DeepSeek 调用成本
"""
from datetime import datetime
import json

class DeepSeekCostMonitor:
    PRICING = {
        "deepseek-chat":     {"input": 0.27,  "output": 1.10, "cached": 0.028},
        "deepseek-reasoner": {"input": 0.55,  "output": 2.19, "cached": 0.14},
    }

    def __init__(self):
        self.total_cost = 0.0
        self.call_count = 0
        self.by_model = {}

    def record(self, model, usage):
        pricing = self.PRICING[model]
        cached = getattr(usage, "prompt_tokens_details", None)
        cached_tokens = cached.cached_tokens if cached else 0

        uncached_input = usage.prompt_tokens - cached_tokens
        cost = (
            uncached_input / 1e6 * pricing["input"]
            + cached_tokens / 1e6 * pricing["cached"]
            + usage.completion_tokens / 1e6 * pricing["output"]
        )

        self.total_cost += cost
        self.call_count += 1
        self.by_model.setdefault(model, {"cost": 0, "calls": 0, "tokens": 0})
        self.by_model[model]["cost"] += cost
        self.by_model[model]["calls"] += 1
        self.by_model[model]["tokens"] += usage.total_tokens

        return cost

    def summary(self):
        return {
            "total_cost_usd": round(self.total_cost, 4),
            "total_calls": self.call_count,
            "by_model": self.by_model,
            "generated_at": datetime.now().isoformat()
        }

monitor = DeepSeekCostMonitor()

# 包装调用
def tracked_chat(model, messages, **kwargs):
    resp = client.chat.completions.create(model=model, messages=messages, **kwargs)
    cost = monitor.record(model, resp.usage)
    print(f"[{model}] cost=${cost:.6f}, tokens={resp.usage.total_tokens}")
    return resp

# 使用
tracked_chat("deepseek-chat", [{"role": "user", "content": "hi"}])

# 输出汇总
print(json.dumps(monitor.summary(), indent=2))
```

## 🌊 实战 6：流式 + reasoning 完整 UI

```python
"""
FastAPI + SSE 流式 DeepSeek-R1 响应
"""
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import OpenAI
import json

app = FastAPI()
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com/v1")

@app.post("/chat/stream")
async def chat_stream(message: str):
    def generate():
        stream = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[{"role": "user", "content": message}],
            stream=True
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                yield f"event: thinking\ndata: {json.dumps({'text': delta.reasoning_content})}\n\n"
            elif delta.content:
                yield f"event: answer\ndata: {json.dumps({'text': delta.content})}\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

前端用 EventSource 接收：

```javascript
const evtSource = new EventSource("/chat/stream?message=...");
evtSource.addEventListener("thinking", e => appendThinking(JSON.parse(e.data).text));
evtSource.addEventListener("answer",   e => appendAnswer(JSON.parse(e.data).text));
evtSource.addEventListener("done",     () => evtSource.close());
```

## 🔗 实战 7：与 LangChain 集成

```python
"""
LangChain + DeepSeek 构建 Agent
"""
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

# DeepSeek 接入 LangChain
llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
    openai_api_base="https://api.deepseek.com/v1",
    temperature=0.3
)

# 定义工具
@tool
def get_weather(city: str) -> str:
    """查询天气"""
    return f"{city}今天晴，22°C"

@tool
def search_docs(query: str) -> str:
    """搜索内部文档"""
    # RAG 检索逻辑
    return "找到相关文档..."

tools = [get_weather, search_docs]

# 构建 Agent
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是智能助手，可用工具：{tool_names}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 运行
result = executor.invoke({"input": "查询北京天气并搜索相关文档"})
print(result["output"])
```

## 🚀 实战 8：本地推理服务 + Nginx 反代

```nginx
# /etc/nginx/sites-available/deepseek
upstream vllm_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name llm.example.com;

    location / {
        proxy_pass http://vllm_backend;
        proxy_set_header Host $host;

        # 流式响应关键配置
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header X-Accel-Buffering no;

        # 超时调长
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
    }
}
```

```bash
# 启动 vLLM
vllm serve deepseek-ai/DeepSeek-R1-Distill-Qwen-14B \
    --port 8000 --host 127.0.0.1 \
    --max-model-len 32768

# 启动 Nginx
nginx -s reload

# 外网调用
curl -X POST https://llm.example.com/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{"model":"...","messages":[...]}'
```

## 📚 实战 9：监控 + 日志

```python
"""
结构化日志 + 性能监控
"""
import logging
import time
from functools import wraps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("deepseek")

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        resp = func(*args, **kwargs)
        duration = time.perf_counter() - start

        usage = resp.usage
        logger.info(json.dumps({
            "event": "deepseek_call",
            "model": resp.model,
            "duration_ms": int(duration * 1000),
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens,
            "first_token_ms": int(resp._first_token_time * 1000) if hasattr(resp, "_first_token_time") else None,
        }))
        return resp
    return wrapper

@monitor_performance
def call_deepseek(messages):
    return client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )

# 输出（JSON 格式，方便 ELK / Loki 采集）
# {"event": "deepseek_call", "model": "deepseek-chat", "duration_ms": 1234, ...}
```

## 💼 实战 10：生产级重试 + 容错

```python
"""
指数退避 + 熔断器
"""
import time
from functools import wraps
import random

def retry_with_backoff(max_retries=5, base_delay=1, max_delay=60):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    delay = delay + random.uniform(0, 0.5)  # jitter
                    logger.warning(f"retry {attempt+1}/{max_retries} after {delay:.1f}s: {e}")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry_with_backoff()
def robust_chat(messages):
    return client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        timeout=30                  # 单次请求超时
    )
```
