---
title: 模型对比与选型
---

# 模型对比与选型

> 闭源旗舰 + 开源强模型，**按场景选**。

## 📊 闭源旗舰对比

| 维度 | Claude 4.5 Sonnet | GPT-5 / GPT-4o | Gemini 2.5 Pro | DeepSeek V3 |
|------|-------------------|------------------|----------------|---------------|
| 厂商 | Anthropic | OpenAI | Google | DeepSeek |
| 上下文 | 200K | 200K | 1M-2M | 128K |
| 推理 | **极强** | 强 | 极强 | 强 |
| 代码 | **极强** | 强 | 强 | 强（Coder 极强） |
| 中文 | 强 | 中 | 强 | **极强** |
| 视觉 | 图 / PDF | 图 | **图 / 音 / 视** | 图 |
| 速度 | 中 | 中快 | 中 | 中 |
| 价格 $/MTok (in) | 3 | 2.5 | 1.25 | **0.14** |
| 工具调用 | 强 | 强 | 强 | 强 |
| MCP 原生 | ✅ | ❌（Codex CLI 有） | ❌ | ❌ |

## 🎯 选型矩阵

| 场景 | 首选 | 次选 |
|------|------|------|
| **复杂代码 / Agent** | Claude 4.5 Sonnet | GPT-5 |
| **深度推理** | o3 / Claude Opus | DeepSeek R1 |
| **长上下文（>500K）** | Gemini 2.5 Pro | Claude 4.5 |
| **中文 + 性价比** | DeepSeek V3 | Qwen2.5 |
| **多模态（音/视）** | Gemini 2.5 Pro | GPT-4o |
| **本地 / 隐私** | Qwen 72B + Ollama | Llama 3.3 70B |
| **敏感数据** | Claude on AWS Bedrock | 本地 Llama |
| **小模型 / 边缘** | Llama 3.2 1B/3B | Qwen2.5 7B |
| **代码补全（IDE）** | Claude Code | Copilot |
| **RAG / 长文档** | Claude 4.5 (200K) | Gemini 2.5 (1M) |

## 💰 成本对比（每百万 token 输入）

| 模型 | 价格 | 排名 |
|------|------|------|
| DeepSeek V3 | $0.14 | 🥇 极便宜 |
| GPT-4o mini | $0.15 | 🥈 |
| Gemini 2.5 Flash | $0.30 | 🥉 |
| GPT-4o | $2.5 | 主流 |
| Claude Sonnet 4.5 | $3 | 略贵 |
| GPT-5 | $5 | 旗舰 |
| Claude Opus 4.5 | $15 | 💰 贵 |
| o1 | $15 | 贵 |

→ **日常开发 DeepSeek V3 或 GPT-4o mini 即可**，关键时刻切 Sonnet 4.5 / Opus 4.5。

## 🔄 实战：多模型路由

```python
# 用 LiteLLM 统一接口，自动选模型
from litellm import completion

def ask(prompt: str, task: str = "default"):
    models = {
        "simple": "gpt-4o-mini",
        "code": "claude-sonnet-4-5",
        "reason": "o3",
        "chinese": "deepseek-chat",
        "long": "gemini-2.5-pro",
        "default": "claude-sonnet-4-5",
    }
    return completion(
        model=models[task],
        messages=[{"role": "user", "content": prompt}]
    )

print(ask("9.11 9.9 哪个大", task="reason"))
print(ask("用 Python 写 quicksort", task="code"))
print(ask("你好", task="chinese"))
```

## 🛠 选型清单

回答 5 个问题：

1. **数据隐私敏感？** 是 → 自托管（Ollama / vLLM）
2. **预算？** 紧张 → DeepSeek / GPT-4o mini
3. **任务复杂？** 高 → Claude Opus / o3
4. **长上下文（>500K）？** 是 → Gemini 2.5 Pro
5. **需要中文？** 是 → DeepSeek / Qwen / 文心

## 🔗 下一步

- [Claude 模型家族](/01-models/claude)
- [GPT / OpenAI](/01-models/gpt)
- [Gemini](/01-models/gemini)
- [DeepSeek](/01-models/deepseek)

<!-- svg-injected:do-not-edit -->

## 图示：LLM 训练 6 阶段流水线

![LLM 训练 6 阶段流水线](/llm-training-pipeline.svg)
