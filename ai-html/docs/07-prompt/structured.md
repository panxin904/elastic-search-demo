---
title: 结构化 Prompt
date: 2026-08-15  # date-auto-injected
---

# 结构化 Prompt

> 写好 prompt 是 LLM 应用的第一步。**结构化、明确、可控**。

## 🧱 Prompt 三段式

```python
# 1. System prompt（角色 / 规则 / 输出格式）
system = """
你是资深 Python 工程师。
- 用 Python 3.12+ 类型提示
- 遵循 PEP 8
- 输出格式：JSON {answer, code, explanation}
"""

# 2. Few-shot（示范）
few_shots = [
    {"user": "如何反转字符串？", "assistant": '{answer: "切片", code: "s[::-1]", explanation: "..."}'}
]

# 3. User query
user = "如何读 CSV？"
```

## 📐 模板骨架

```python
prompt = f"""
# 角色
你是 {role}。

# 任务
{task_description}

# 规则
- {rule_1}
- {rule_2}

# 输出格式
{output_format}

# Few-shot
{few_shot_examples}

# 任务
{user_input}
"""
```

## 🛠 System Prompt 最佳实践

```python
# 明确角色 + 范围 + 输出格式
SYSTEM = """
你是"代码审查助手"，只看 PR diff，给出：

## 输出格式
- **严重问题**：必须修（安全 / 数据丢失）
- **建议**：可改可不改
- **可忽略**：风格问题

每条用 1-2 句说明 + 改法（代码片段）。

## 严格
- 不啰嗦、不给"总结"、不复述问题
- 不确定就标 [需要人类判断]
- 不输出非技术内容
"""
```

## 🎯 输出格式控制

### 1. JSON 强约束（OpenAI）

```python
from pydantic import BaseModel, Field
from openai import OpenAI

class CodeReview(BaseModel):
    issues: list[dict]
    summary: str

client = OpenAI()
resp = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system", "content": "你是代码审查助手"},
        {"role": "user", "content": "审查这段代码：..."}
    ],
    response_format=CodeReview
)
review = resp.choices[0].message.parsed
print(review.summary, review.issues)
```

### 2. Claude 系统提示 + JSON

```python
SYSTEM = """严格输出 JSON：
{
  "summary": "...",
  "issues": [{"severity": "...", "message": "...", "fix": "..."}],
  "suggestion": "..."
}
不要任何额外文字，不要 markdown 代码块标记。"""
```

### 3. XML 标签（容易解析）

```python
SYSTEM = """
输出格式：
<answer>你的回答</answer>
<confidence>0-1 的数字</confidence>
<reasoning>简短理由</reasoning>
"""
```

## 🧠 上下文管理（重要！）

```python
# 1. 长 system / few-shot 用 cache（成本降 90%）
msg = client.messages.create(
    model="claude-sonnet-4-5",
    system=[
        {"type":"text","text":"你是...","cache_control":{"type":"ephemeral"}},
        {"type":"text","text":"<50KB 文档>","cache_control":{"type":"ephemeral"}}
    ],
    messages=[...]
)

# 2. 多轮：放最近的 + 摘要老的
messages = [
    {"role":"system","content":"你是..."},
    {"role":"user","content":"最早的对话..."},
    {"role":"assistant","content":"..."},
    # 太多轮？摘要掉中间
    {"role":"system","content":"[对话摘要]"},
    {"role":"user","content":"最近的问题"},
    {"role":"assistant","content":"..."}
]

# 3. 控制总 token 数（避免超 context window）
# tiktoken / anthropic token counter
```

## 🔥 实战模式

### 1. 输出代码 + 解释

```python
SYSTEM = """你是资深 Python 工程师。
- 回答简洁（不啰嗦）
- 给完整可运行代码
- 末尾简短说下复杂度
- 不要客套话"""
```

### 2. 多步任务（分解）

```python
SYSTEM = """你分两步：
1. 简短计划（1-3 句）
2. 完整答案"""
```

### 3. 自洽（self-consistency）

```python
# 让模型从多个角度验证
SYSTEM = """回答后，再用 1-2 句检查你的逻辑是否有漏洞。
如有漏洞就修正。"""
```

### 4. Few-shot 反例

```python
# 不仅给正例，给反例 / 错误示范
few_shots = [
    {"user":"什么是 Python？",
     "assistant": "Python 是一种高级编程语言，以简洁著称。"},
    {"user":"什么是 Python？",
     "assistant": "Python 是一种编程语言。"},  # ❌ 错误示范
    {"user":"什么是 Python？",
     "assistant": "Python 是一种高级编程语言，由 Guido 创建，强调代码可读性。"}  # ✅ 正确
]
```

## 🆚 vs Few-shot

| | 系统 prompt | Few-shot |
|--|-------------|-----------|
| 作用 | 角色 / 规则 | 演示输出格式 |
| 长度 | 短到长 | 短（2-5 示例） |
| 优化 | Claude 缓存 | token 成本高 |
| 适合 | 几乎所有任务 | 输出格式复杂时 |

## 🔗 下一步

- [Chain-of-Thought](/07-prompt/cot)
- [Few-shot / Multi-shot](/07-prompt/few-shot)
- [Tool Use 模式](/11-tools/tool-use)