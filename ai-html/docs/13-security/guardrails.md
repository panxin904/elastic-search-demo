---
title: Guardrails / Content Safety
---

# Guardrails - LLM 内容安全

> **G**uard**R**ails = LLM 输入 / 输出 **校验 + 过滤 + 重写**。**生产 LLM 应用必备**。

## 🤔 为什么需要 Guardrails

```
LLM 应用风险：
  ❌ 输出有害 / 歧视 / 暴力
  ❌ 泄露 PII（个人身份信息）
  ❌ Prompt Injection（恶意 prompt 突破 system）
  ❌ 输出错乱（JSON 不合规 / 偏离主题）
  ❌ 幻觉（编造事实）
  ❌ 版权 / 商标 / 隐私

Guardrails：
  ✅ 输入：检测恶意 / 越狱
  ✅ 输出：检测有害 / PII / 错乱
  ✅ 自动重写 / 屏蔽
  ✅ 审计日志
```

## 🏆 主流 Guardrails 工具

| 工具 | 类型 | 特点 |
|------|------|------|
| **NeMo Guardrails (NVIDIA)** | 框架 | Colang DSL，主流 |
| **Guardrails AI** | 框架 | Python，开源 |
| **LangChain Guardrails** | 集成 | LangChain 生态 |
| **Llama Guard** (Meta) | 输入 / 输出分类 | 安全 LLM |
| **OpenAI Moderation API** | 云服务 | 内容审核 |
| **Azure AI Content Safety** | 云服务 | 多模态审核 |
| **Perspective API** | Google | 评论毒性 |
| **NeMo Guardrails** + **Llama Guard** | 组合 | NVIDIA 推荐 |

## 🚀 NeMo Guardrails

```bash
pip install nemoguardrails
```

```python
from nemoguardrails import LLMRails, RailsConfig

# 1. 配置
config = RailsConfig.from_content("""
define user ask anything
define bot respond helpfully

define flow
  user ask about weather
  bot provide weather
""")

# 2. 装
rails = LLMRails(config)

# 3. 跑（带 guardrails）
response = rails.generate("北京天气？")
print(response)
```

### 编程式 guardrails（Colang）

```python
from nemoguardrails import RailsConfig

# config/rails/config.yml
# define jailbreak detection
#   if user says "ignore previous instructions"
#     bot refuse
```

## 🚀 Guardrails AI

```bash
pip install guardrails-ai
```

```python
from guardrails import Guard
from pydantic import BaseModel

class Pet(BaseModel):
    name: str
    age: int

guard = Guard.from_pydantic(Pet)
result = guard.parse("我的狗 3 岁，叫小黄")
print(result.validated_output)
# Pet(name='小黄', age=3)
```

## 🚀 Llama Guard（输入 / 输出分类）

```bash
ollama pull llama-guard3:8b
```

```python
import ollama

# 检查输入
def check_input_safe(text):
    resp = ollama.chat(
        model="llama-guard3:8b",
        messages=[{"role":"user","content":text}]
    )
    return resp["message"]["content"] == "safe"

# 检查输出
def check_output_safe(text):
    resp = ollama.chat(
        model="llama-guard3:8b",
        messages=[
            {"role":"user","content":""},
            {"role":"assistant","content":text}
        ]
    )
    return resp["message"]["content"] == "safe"

# 集成
def safe_chat(prompt, llm):
    if not check_input_safe(prompt):
        return "输入不安全，已拒绝"
    answer = llm.invoke(prompt)
    if not check_output_safe(answer):
        return "输出不安全，请换个问法"
    return answer
```

## 🚀 OpenAI Moderation

```python
from openai import OpenAI
client = OpenAI()

# 检测文本是否违规
resp = client.moderations.create(
    model="omni-moderation-latest",
    input=["我恨所有人", "hello"]
)
for r in resp.results:
    print(r.flagged, r.categories)
# True {hate: True, ...}
# False {}
```

返回的 categories：hate / harassment / self-harm / sexual / violence 等。

## 🛡 实战 Guardrails 流水线

```python
def safe_llm_call(user_input: str, context: str = "") -> str:
    # 1. 输入：检测 jailbreak
    if not check_input_safe(user_input):
        return "⚠️ 输入含可疑指令，已拒绝"

    # 2. 输入：检测 PII
    if contains_pii(user_input):
        user_input = redact_pii(user_input)

    # 3. 调 LLM
    answer = llm.invoke(user_input, context=context)

    # 4. 输出：检查有害
    if not check_output_safe(answer):
        return "⚠️ 输出被过滤"

    # 5. 输出：检查 PII
    answer = redact_pii(answer)

    # 6. 输出：检查合规（JSON schema）
    try:
        result = MySchema.model_validate_json(answer)
        return result
    except ValidationError:
        return "⚠️ 输出格式异常"

    return answer
```

## 🔐 PII 检测

```python
import re

def contains_pii(text: str) -> bool:
    patterns = {
        "email": r'[\w.]+@[\w.]+',
        "phone_cn": r'1[3-9]\d{9}',
        "id_card_cn": r'\d{17}[\dXx]',
        "credit_card": r'\d{16}',
    }
    for name, p in patterns.items():
        if re.search(p, text):
            return True
    return False

def redact_pii(text):
    text = re.sub(r'[\w.]+@[\w.]+', '[EMAIL]', text)
    text = re.sub(r'1[3-9]\d{9}', '[PHONE]', text)
    return text
```

## 🚨 Prompt Injection 检测

```python
INJECTION_PATTERNS = [
    r"ignore (all )?previous instructions",
    r"disregard (your|all) rules",
    r"system prompt",
    r"reveal your prompt",
    r"forget everything",
    r"act as [a-z]+",
]

def is_injection(text: str) -> bool:
    text_low = text.lower()
    return any(re.search(p, text_low) for p in INJECTION_PATTERNS)
```

更好的方式：用一个**专门分类的 LLM**（如 Llama Guard）。

## 🔧 LangChain 集成

```python
from langchain.chains import ConstitutionalChain
# Constitutional AI 风格：让 LLM 自己审查输出

from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o")

principles = [
    "回答不能含 PII",
    "回答不能有害 / 歧视",
    "回答不能编造事实"
]

chain = ConstitutionalChain.from_llm(
    llm=llm,
    chain=base_chain,
    constitutional_principles=principles
)
result = chain.invoke({"input": "..."})
```

## 🆚 vs 提示工程

| | Guardrails | 提示工程 |
|--|------------|----------|
| 防护 | 系统级 | 容易绕过 |
| 延迟 | 略高（额外模型） | 0 |
| 准确 | 高 | 中 |
| 适合 | 生产 | demo |

## 🔗 下一步

- [API Key 管理](/13-security/api-keys)
- [成本控制 / Token](/13-security/cost)
- [Eval 框架](/09-eval/frameworks)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [python](https://java-px.bot.cd/python/):Python AI
- [bigdata](https://java-px.bot.cd/bigdata/):大数据训练
- [system-design](https://java-px.bot.cd/system-design/):AI 系统架构
