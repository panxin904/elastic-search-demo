---
title: 上下文窗口与 Token
date: 2026-08-29  # date-auto-injected
---

# 🧮 上下文窗口与 Token 计算

> 理解 Token 是控制 API 成本、优化 Prompt、避免超限的基础。

## 🤔 Token 是什么

Token 是模型处理的最小文本单位，介于字符和词之间。

```
英文: "Hello, world!" → ["Hello", ",", " world", "!"] → 4 tokens
中文: "你好，世界" → ["你", "好", "，", "世", "界"] → 5 tokens
代码: "function() { return 42; }" → ~7 tokens
```

## 🆚 不同分词器

| 模型 | 分词器 | 1 token ≈ |
|------|--------|-----------|
| GPT-4 / GPT-4o | o200k_base | 0.75 英文单词 / 1.5 中文字 |
| GPT-3.5 / GPT-4 旧 | cl100k_base | 类似上 |
| Claude | Claude tokenizer | 略多于 GPT |
| Gemini | SentencePiece | 中英都偏多 |
| DeepSeek | BPE | 与 GPT 类似 |

## 📊 主流模型上下文窗口（2026）

| 模型 | 上下文窗口 | 输出上限 |
|------|----------|---------|
| **Claude Sonnet 4.5** | 200K | 8K / 64K（beta） |
| **GPT-4o** | 128K | 16K |
| **GPT-4o mini** | 128K | 16K |
| **o1-preview** | 128K | 32K |
| **Gemini 2.0 Flash** | 1M | 8K |
| **Gemini 2.5 Pro** | 2M | 64K |
| **DeepSeek V3** | 64K | 8K |
| **Qwen 2.5 72B** | 128K | 8K |
| **Llama 3.1 405B** | 128K | 8K |

## 💻 Token 计算工具

### OpenAI 官方

```bash
pip install tiktoken
```

```python
import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")
text = "你好，世界！Hello world!"
tokens = enc.encode(text)
print(f"Token count: {len(tokens)}")
# 中文 + 英文混合，约 8-10 tokens
```

### Anthropic（需要 API）

```python
import anthropic
client = anthropic.Anthropic()

# 方式 1：在 API 响应里看 usage.input_tokens
response = client.messages.create(...)
print(response.usage.input_tokens)

# 方式 2：使用 count_tokens 端点
count = client.messages.count_tokens(
    model="claude-sonnet-4-5",
    messages=[{"role": "user", "content": "hello"}],
)
print(count.input_tokens)
```

### 在线工具

- **OpenAI Tokenizer**：https://platform.openai.com/tokenizer
- **Anthropic Console**：https://console.anthropic.com（显示 token 数）

## 📐 中英文 token 估算

| 内容 | Token 数（粗估） |
|------|------------------|
| 1 个英文字符 | 0.25 token |
| 1 个英文单词 | 1.3 tokens |
| 1 个中文字符 | 0.7-1.5 tokens |
| 1 行代码 | 10-30 tokens |
| 1 页 Markdown | ~500 tokens |
| 1 本书 | 100K-200K tokens |

## 🎯 Token 优化技巧

### 1. 提示工程压缩

```python
# ❌ 啰嗦
prompt = """
请帮我仔细地、认真地、深入地分析下面这段文本，然后告诉我这段文本主要表达了什么核心思想。
"""

# ✅ 简洁
prompt = "分析下文核心思想："
```

### 2. 消息历史管理

```python
# 超过上下文窗口时，截断最早消息
def trim_messages(messages, max_tokens=100_000):
    enc = tiktoken.encoding_for_model("gpt-4o")
    total = 0
    trimmed = []
    for msg in reversed(messages):
        tokens = len(enc.encode(msg["content"]))
        if total + tokens > max_tokens:
            break
        total += tokens
        trimmed.insert(0, msg)
    return trimmed
```

### 3. 缓存命中（Anthropic Prompt Caching）

Anthropic 支持把 system + 长上下文标记为 cache，写入 1.25x、读取 0.1x 价格。

```python
response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": "你是一个法律顾问...",  # 长 system
            "cache_control": {"type": "ephemeral"}
        }
    ],
    messages=[...],
)
```

### 4. 滑动窗口摘要

```python
def summarize_old_messages(messages, llm):
    """把最早 N 条消息总结成 1 条"""
    if len(messages) < 10:
        return messages
    old = messages[:8]
    summary_prompt = f"用 100 字总结以下对话：\n\n{old}"
    summary = llm.invoke(summary_prompt).content
    return [{"role": "system", "content": f"对话历史摘要：{summary}"}] + messages[8:]
```

## 💰 价格参考（2026 年 8 月）

| 模型 | Input (per 1M) | Output (per 1M) |
|------|---------------|-----------------|
| GPT-4o | $2.50 | $10.00 |
| GPT-4o mini | $0.15 | $0.60 |
| o1-preview | $15.00 | $60.00 |
| Claude Sonnet 4.5 | $3.00 | $15.00 |
| Claude Haiku 4.5 | $0.80 | $4.00 |
| Gemini 2.0 Flash | $0.075 | $0.30 |
| DeepSeek V3 | $0.27 | $1.10 |

**示例计算**：
- GPT-4o 处理 100K token 输入 + 10K 输出 = (100K × $2.50 + 10K × $10.00) / 1M = $0.35
- Claude Sonnet 处理同样 = (100K × $3 + 10K × $15) / 1M = $0.45
- Gemini Flash = (100K × $0.075 + 10K × $0.30) / 1M = $0.011

## ⚠️ 上下文窗口填满的征兆

1. **响应开始截断**：`finish_reason: length`
2. **模型"忘记"早消息**：超过窗口前的对话被截断
3. **Token 计数返回错误**：`400 invalid_request_error: too many tokens`
4. **成本失控**：循环调用导致 token 累积

## 🔧 实战：监控 Token 使用

```python
class TokenTracker:
    def __init__(self):
        self.total_input = 0
        self.total_output = 0
        self.calls = 0

    def record(self, response):
        if hasattr(response, "usage"):
            self.total_input += response.usage.prompt_tokens
            self.total_output += response.usage.completion_tokens
            self.calls += 1

    def cost_estimate(self, model="gpt-4o"):
        prices = {
            "gpt-4o": (2.50, 10.00),
            "gpt-4o-mini": (0.15, 0.60),
            "claude-sonnet-4-5": (3.00, 15.00),
        }
        in_p, out_p = prices[model]
        return (self.total_input * in_p + self.total_output * out_p) / 1_000_000

tracker = TokenTracker()
# ... 每次调用 response = client.chat.completions.create(...); tracker.record(response)
print(f"Cost so far: ${tracker.cost_estimate():.4f}")
```

## 🔗 关联章节

- [rate-limit-retry](./rate-limit-retry) - 超 token 限流处理
- [multimodal-input](./multimodal-input) - 图片如何折算 token
- [13-security/cost](../13-security/cost) - 成本控制策略
