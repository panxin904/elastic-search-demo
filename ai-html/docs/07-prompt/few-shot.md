---
title: Few-shot / Multi-shot
---

# Few-shot / Multi-shot

> 在 prompt 里给几个**示例**，让模型"照葫芦画瓢"。

## 🧬 Few-shot 基础

```python
# Zero-shot（无示例）
prompt = "把以下句子翻译成法语：'Hello, how are you?'"

# One-shot（1 个示例）
prompt = """
英文：Hello, how are you?
法语：Bonjour, comment ça va?

英文：Good morning.
法语："""

# Few-shot（多个示例）
prompt = """
英文：Hello, how are you?
法语：Bonjour, comment ça va?

英文：Good morning.
法语：Bonjour.

英文：Thank you very much.
法语："""
```

## 🛠 Few-shot 设计原则

### 1. 多样性（不要重复同结构）

```python
# ❌ 不好（结构都一样）
# Q: X
# A: A
# Q: Y
# A: A  ← 重复

# ✅ 好
# Q: x = 1, y = 2
# A: 3
# Q: "Hello" 重复 3 次
# A: "HelloHelloHello"
# Q: [1, 2, 3] 求和
# A: 6
```

### 2. 覆盖边界 case

```python
few_shots = [
    # 正常
    {"user": "正向", "assistant": "正向回答"},
    # 边界
    {"user": "空字符串", "assistant": "无内容"},
    # 错误情况
    {"user": "无效输入", "assistant": "无法处理，请提供 X"},
    # 复杂
    {"user": "复杂问题", "assistant": "完整详细回答"}
]
```

### 3. 顺序：最相关的放最后

LLM **对最后示例的注意最强**（recency bias）。

```python
few_shots = [
    # 一般示例
    {...},
    # 跟 query 最像的示例放最后
    {...}
]
```

## 🛠 格式 Few-shot

```python
# 1. JSON 输出
few_shots = [
    {"user": "提取 'Alice is 30' 的人物信息",
     "assistant": '{"name":"Alice","age":30}'},
    {"user": "提取 'Bob is 25' 的人物信息",
     "assistant": '{"name":"Bob","age":25}'}
]
# 然后：
user = "提取 'Carol is 40' 的人物信息"

# 2. 工具调用
few_shots = [
    {"user": "北京天气？",
     "assistant": """Action: get_weather(city="北京")
Observation: 北京 25°C 晴
Answer: 北京今天 25°C 晴。"""},
    {"user": "纽约天气？",
     "assistant": """Action: get_weather(city="纽约")
Observation: 纽约 18°C 阴
Answer: 纽约今天 18°C 阴。"""}
]
```

## 🧠 Multi-shot + 多模态

```python
# 图文混合 few-shot
few_shots = [
    {
        "user": [
            {"type":"text","text":"这图有什么？"},
            {"type":"image_url","image_url":{"url":"https://..."}}
        ],
        "assistant": "图里是一只狗在玩球"
    }
]
```

## 📊 数量

| 任务 | 推荐示例数 |
|------|----------|
| 简单分类 | 1-3 |
| 输出格式约束 | 3-5 |
| 复杂推理 | 5-10（含 CoT） |
| 边缘 case | 覆盖所有典型 edge |

**不要太多**：token 成本高 + 稀释注意力。

## 🆚 Zero-shot vs One-shot vs Few-shot

| | Zero-shot | One-shot | Few-shot |
|--|-----------|----------|----------|
| 示例 | 0 | 1 | 3-10 |
| 适合 | 简单任务 | 格式示范 | 复杂 / 特殊输出 |
| 成本 | 低 | 中 | 高 |
| 效果 | 取决于模型 | 稳定 | **最稳** |

## 🛠 实战

```python
# Claude 完整 few-shot
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    system="你是 SQL 翻译器：将中文转成 SQL",
    messages=[
        {
            "role": "user",
            "content": [
                {"type":"text","text":"示例：\nQ: 找出所有员工\nA: SELECT * FROM employees;\n\nQ: 找出工资超过 1 万的\nA: SELECT * FROM employees WHERE salary > 10000;\n\nQ: 找出北京的客户\nA:"}
            ]
        }
    ]
)
print(response.content[0].text)
# SELECT * FROM customers WHERE city = '北京';
```

## 🆚 vs System Prompt

| | Few-shot | System Prompt |
|--|----------|----------------|
| 作用 | **演示输出** | 角色 / 规则 |
| 适合 | 输出格式复杂 | 通用行为约束 |
| 配合 | 几乎都要 | 几乎都要 |

**最佳实践：few-shot + system**。

## 🔗 下一步

- [Chain-of-Thought](/07-prompt/cot)
- [结构化 Prompt](/07-prompt/structured)
- [Tool Use 模式](/11-tools/tool-use)