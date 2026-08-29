---
title: 成本控制 / Token 管理
---

# 成本控制 / Token 管理

> LLM 应用烧钱的方式："一个 prompt 没限制 size 给我打了一个 8000 token 的 conversation → 调一次 5 美元 → 一天 100 万次 = 500 万美元"。

## 🤔 钱在哪烧的

```
LLM 调用成本 = 单价 × 输入 token × 输出 token × 调用次数

输入 1M token 看似很多，输出 1M token 更贵（3-5x）
```

## 🔍 看成本

### OpenAI

```python
import openai
resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[...]
)
print("input:", resp.usage.prompt_tokens)
print("output:", resp.usage.completion_tokens)
print("total:", resp.usage.total_tokens)
# $ = input * (2.5/1M) + output * (10/1M)
```

### Anthropic

```python
print(resp.usage)
# Usage(input_tokens=123, output_tokens=45)
# Anthropic 端也算 = 3 / MTok in
```

## 💡 优化策略

### 1. 模型选型

| 任务 | 选 |
|------|-----|
| 简单分类 / 提取 | gpt-4o-mini ($0.15/Mtok) |
| 日常 Chat | gpt-4o ($2.5) / Sonnet 4.5 ($3) |
| 复杂推理 | o1 / Opus 4.5（贵 $15+） |

**默认走小模型**，不行再升级。

```python
def ask(prompt):
    if is_simple(prompt):
        return client_gpt4o_mini.invoke(prompt)        # 0.15/Mtok
    return client_gpt4o.invoke(prompt)                  # 2.5/Mtok
```

### 2. Prompt 优化

```python
# ❌ 长 system
system = "你是专家..."  # 8000 tokens

# ✅ 精简
system = "你是助手。回答简洁。"  # 12 tokens

# ✅ 用 prompt cache（重复前缀）
# Claude: cache_control={"type": "ephemeral"}
# 重复前缀 → 命中 cache → 90% 折扣
```

### 3. 控制 max_tokens

```python
resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    max_tokens=256        # 限制最大输出
)
```

### 4. 截断长输入

```python
def truncate(text, max_tokens=2000):
    # 用 tiktoken 估 token 数
    import tiktoken
    enc = tiktoken.encoding_for_model("gpt-4o")
    tokens = enc.encode(text)
    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
    return enc.decode(tokens)
```

### 5. 缓存（减少重复调用）

```python
# Redis / 内存缓存
import hashlib, json, redis
r = redis.Redis()

def cached_llm(prompt):
    key = hashlib.md5(prompt.encode()).hexdigest()
    hit = r.get(key)
    if hit: return json.loads(hit)
    resp = client.chat.completions.create(...)
    r.setex(key, 3600, json.dumps(resp.choices[0].message))
    return resp
```

### 6. 批量

```python
# 把多个 query 合并成一次调用
resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "Q1: 1+1=?\nQ2: 2+2=?\nQ3: 3+3=?"}
    ]
)
# 输出再 split
```

## 🛡 限速 + 告警

```python
import time
from functools import wraps

# 1. 单用户限速
USER_LIMIT = 100  # req/hour
def rate_limit(user_id):
    count = r.incr(f"rl:{user_id}:{int(time.time()/3600)}")
    if count > USER_LIMIT:
        raise Exception("rate limited")
    return count

# 2. 月度预算
class BudgetChecker:
    def __init__(self, limit_usd):
        self.used = 0
        self.limit = limit_usd

    def charge(self, cost):
        self.used += cost
        if self.used > self.limit:
            raise Exception("over budget")

# 3. 实时告警
# 配合 Prometheus + Alertmanager
# - token 用量超 80% 预算 → Slack / PagerDuty
```

## 📊 监控工具

| 工具 | 特点 |
|------|------|
| **OpenAI Usage API** | 官方 |
| **Anthropic Console** | 看月度账单 |
| **Langfuse**（开源） | 完整 observability + 成本 |
| **Helicone**（开源） | LLM 专用网关 + 缓存 + 限速 |
| **Portkey** | 多 provider 路由 + 成本 |
| **LiteLLM** | 统一 API + 成本追踪 |

## 🚀 LiteLLM + Budget

```yaml
# config.yaml
model_list:
  - model_name: claude
    litellm_params:
      model: anthropic/claude-sonnet-4-5
      api_key: sk-ant-...
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: sk-...

litellm_settings:
  drop_params: true
  set_verbose: False
  # 预算限制
  max_budget: 1000            # USD / month
  budget_duration: 30d
```

```bash
litellm --config config.yaml
# :4000 → 监控 /metrics 看用量
```

## 🚀 Helicone 缓存

```python
# pip install helicone
import openai

client = openai.OpenAI(
    api_key="sk-...",
    base_url="https://oai.hconeai.com/v1",
    default_headers={
        "Helicone-Auth": "Bearer sk-helicone-...",
        "Helicone-Cache-Enabled": "true",        # 自动缓存
        "Helicone-User-Id": "alice"
    }
)
# 重复请求自动命中 cache（0 成本）
```

## 🪜 估算公式

```python
def estimate_cost(model, input_tokens, output_tokens):
    PRICES = {
        "gpt-4o": (2.5, 10),        # (in, out) $/MTok
        "gpt-4o-mini": (0.15, 0.6),
        "claude-sonnet-4-5": (3, 15),
        "deepseek-chat": (0.14, 0.28),
    }
    in_p, out_p = PRICES[model]
    cost = input_tokens * in_p / 1_000_000 + output_tokens * out_p / 1_000_000
    return cost

# 月度预估
calls_per_day = 10_000
avg_input, avg_output = 500, 200
cost_per_call = estimate_cost("gpt-4o", avg_input, avg_output)  # 0.00325
monthly = calls_per_day * cost_per_call * 30
# ~$975
```

## 🛠 实战

```python
import tiktoken

# 1. 控制单次成本
def safe_ask(prompt, model="gpt-4o", max_cost=0.05):
    enc = tiktoken.encoding_for_model(model)
    in_tokens = len(enc.encode(prompt))
    est = estimate_cost(model, in_tokens, 500)
    if est > max_cost:
        raise Exception(f"预估 ${est:.4f} 超 ${max_cost}")

    resp = client.chat.completions.create(
        model=model,
        messages=[{"role":"user","content":prompt}],
        max_tokens=500
    )
    return resp.choices[0].message.content

# 2. 月度预算 + 告警
# cron 每日跑
# python -c "
# import requests
# today = sum(usage['tokens'])
# if today > 0.8 * MONTHLY_BUDGET:
#     send_slack_alert('80% budget used')
# "
```

## 🔗 下一步

- [API Key 管理](/13-security/api-keys)
- [Guardrails / Content Safety](/13-security/guardrails)
- [Eval 框架](/09-eval/frameworks)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [python](https://java-px.bot.cd/python/):Python AI
- [bigdata](https://java-px.bot.cd/bigdata/):大数据训练
- [system-design](https://java-px.bot.cd/system-design/):AI 系统架构
