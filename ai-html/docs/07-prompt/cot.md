---
title: Chain-of-Thought
date: 2026-08-15  # date-auto-injected
---

# Chain-of-Thought (CoT)

> 让 LLM **一步一步想**，而不是直接出答案。显著提升推理 / 数学 / 代码。

## 🤔 为什么有效

```
直接答：
  Q: 一个房间 3 个灯，2 关 1 开。开关几次能让所有都开？
  A: 1 次（错）

CoT：
  Q: ... 一步一步想
  Step 1: 当前 1 开 2 关
  Step 2: 关一个开着的 = 0 开 3 关？不对，应该让一个关变开
  Step 3: 扳那个开着的 → 全开？需要再开 2 个
  ...
  Step N: 答案是 3 次
```

CoT 强迫模型"展示过程"，避免跳到错误结论。

## 🎯 主流技巧

### 1. Zero-shot CoT

```python
prompt = "Q: 9.11 和 9.9 哪个大？\nA: 让我们一步一步想。"
# "Let's think step by step."
```

加上 "Let's think step by step" 即可，比不加大幅提升。

### 2. Few-shot CoT

```python
prompt = """
Q: 一个停车场有 3 辆车，又来了 2 辆，现在几辆？
A: 让我数一下。最初 3 辆，又来 2 辆，3 + 2 = 5。所以 5 辆。

Q: 鸡兔同笼 35 头 94 足，几鸡几兔？
A: 让我想一想。设鸡 x，兔 y。x + y = 35, 2x + 4y = 94。第二式 - 第一式 × 2：2y = 24，y = 12，x = 23。所以 23 鸡 12 兔。

Q: <你的问题>
A: 让我一步一步想。
"""
```

给几个示例，让模型学会"想"。

### 3. Self-consistency

```python
# 同一个问题，sample 多条（高 temperature），投票选最一致的答案
import anthropic
from collections import Counter

client = anthropic.Anthropic()
question = "9.11 和 9.9 哪个大？"

answers = []
for _ in range(7):  # sample 7 次
    msg = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=512,
        temperature=0.7,
        messages=[{"role":"user","content":f"{question}\nLet's think step by step."}]
    )
    # 提取最后一行数字
    ans = msg.content[0].text.strip().split("\n")[-1]
    answers.append(ans)

final = Counter(answers).most_common(1)[0][0]
```

**多次采样 + 投票**，消除单次 CoT 的随机性。

### 4. Tree of Thoughts (ToT)

```python
# 多个思维路径并行探索
# 1. 生成 3 条思考路径
# 2. 评估每条
# 3. 选最好的
# 4. 继续展开
# 适合：复杂规划 / 24 点 / 数独
```

LangGraph 实现：

```python
from langgraph.graph import StateGraph, END

# 节点 1: generate_thoughts
# 节点 2: evaluate
# 节点 3: select_best
# 循环到最佳评估 → END
```

### 5. ReAct（Reasoning + Acting）

```python
# Thought → Action → Observation → Thought ...
prompt = """
Q: 当前巴黎时间几点了？

Thought: 我需要查实时时间
Action: get_time(timezone="Europe/Paris")
Observation: 14:30

Thought: 我现在知道答案了
Action: finish("巴黎时间 14:30")
"""
```

ReAct = CoT + Tool use。**Agent 的基础**。

## 📊 效果对比

| 方法 | GSM8K | MATH | 复杂代码 |
|------|-------|------|----------|
| Direct | 30% | 5% | 20% |
| Zero-shot CoT | 50% | 15% | 35% |
| Few-shot CoT | 70% | 40% | 55% |
| Self-consistency | 80% | 55% | 60% |
| Tree of Thoughts | 85% | 60% | — |
| ToT + Self-consistency | **90%** | **70%** | — |

（数字为示例，不同任务差异大）

## 🛠 实战

```python
# 复杂推理：用 o1 / Claude Opus
from openai import OpenAI
client = OpenAI()
resp = client.chat.completions.create(
    model="o3",
    messages=[{
        "role": "user",
        "content": "9.11 和 9.9 哪个大？"
    }]
)
# o1 / o3 内置 CoT，不用手动加

# Claude：opus + "think" 关键词
from anthropic import Anthropic
client = Anthropic()
resp = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=4096,
    thinking={"type": "enabled", "budget_tokens": 2000},  # extended thinking
    messages=[{"role":"user","content":"鸡兔同笼 35 头 94 足"}]
)
print(resp.content)   # 含 thinking 块
```

## 🆚 vs CoT vs ReAct vs Reflection

| 方法 | 思维 | 行动 | 自评 |
|------|------|------|------|
| CoT | ✅ | ❌ | ❌ |
| ReAct | ✅ | ✅ | ❌ |
| Reflexion | ✅ | ✅ | ✅ |
| ToT | 多路径 | ❌ | ✅ |

## 🔗 下一步

- [结构化 Prompt](/07-prompt/structured)
- [Few-shot / Multi-shot](/07-prompt/few-shot)
- [Tool Use 模式](/11-tools/tool-use)