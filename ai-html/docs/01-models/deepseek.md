---
title: DeepSeek
date: 2026-08-15  # date-auto-injected
---

# DeepSeek

> 中国最火的**开源 MoE（Mixture of Experts）大模型**。性能对齐 GPT-4 / Claude，**价格只要 1/50**。

## 🧬 模型族

| 模型 | 类型 | 上下文 | 何时用 |
|------|------|--------|--------|
| **DeepSeek-V3.2** | MoE 671B (37B active) | 128K | 推理 / 通用对话 |
| **DeepSeek-R1** | 推理（对标 o1） | 64K | 数学 / 代码 / 复杂推理 |
| **DeepSeek-V2.5** | MoE 236B | 128K | 性价比主力 |
| **DeepSeek-Coder-V2** | 代码 236B MoE | 128K | 代码补全 / 审查 |

## 🆚 价格（API vs 国外）

| 模型 | 输入 ($/MTok) | 输出 ($/MTok) |
|------|--------------|---------------|
| DeepSeek-V3 | 0.14 | 0.28 |
| DeepSeek-R1 | 0.55 | 2.19 |
| GPT-4o | 2.5 | 10 |
| Claude Sonnet 4.5 | 3 | 15 |

→ **便宜 10-50 倍**，中文能力强。

## 🚀 调用

```python
# OpenAI 兼容 API（推荐）
from openai import OpenAI

client = OpenAI(
    api_key="sk-...",
    base_url="https://api.deepseek.com"
)

resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "你好"}]
)
print(resp.choices[0].message.content)

# 流式
stream = client.chat.completions.create(
    model="deepseek-reasoner",  # R1 推理
    messages=[{"role":"user","content":"9.11 和 9.9 哪个大？"}],
    stream=True
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## 🌐 国内访问

```python
# 国内加速
client = OpenAI(
    api_key="sk-...",
    base_url="https://api.deepseek.com"   # 直连
)

# 高并发：async
import asyncio
from openai import AsyncOpenAI
async def main():
    client = AsyncOpenAI(api_key="...", base_url="https://api.deepseek.com")
    resp = await client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role":"user","content":"hi"}]
    )
    print(resp.choices[0].message.content)
asyncio.run(main())
```

## 🧠 思考链

DeepSeek-R1 在输出前会生成详细的思考过程：

```python
# 看思考过程（reasoning_content）
resp = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=[{"role":"user","content":"鸡兔同笼 35 头 94 足"}]
)
msg = resp.choices[0].message
print("思考:", msg.reasoning_content)   # CoT 推理
print("答案:", msg.content)
```

## 🆚 vs 国外模型

| | DeepSeek V3 | GPT-4o | Claude 4.5 |
|--|--------------|--------|-----------|
| 推理 | 强 | 强 | 极强 |
| 中文 | **极强** | 中 | 强 |
| 代码 | 强（Coder 极强） | 强 | 极强 |
| 价格 | **极低** | 中 | 中 |
| 长上下文 | 128K | 128K | 200K |
| 国内 | **直连** | 需代理 | 需代理 |

## 🛠 实战

```python
# 接入 RAG
from langchain.chat_models import ChatOpenAI  # 用 OpenAI 兼容
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS

llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key="...",
    openai_api_base="https://api.deepseek.com"
)
qa = RetrievalQA.from_chain_type(llm, retriever=vs.as_retriever())
print(qa.invoke("...")["result"])
```

## 🔗 下一步

- [模型对比与选型](/01-models/compare)
- [开源模型 Llama / Mistral](/01-models/open-source)
- [Ollama 本地推理](/10-deploy/ollama)