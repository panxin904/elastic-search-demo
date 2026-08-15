---
title: Structured Output
---

# Structured Output（结构化输出）

> 让 LLM 输出**符合 JSON Schema** 的可靠数据，**不是** JSON 字符串。

## 🤔 为什么需要

```
LLM 默认输出：
  "这是 JSON 格式的回答：{\"name\": \"alice\", ...} 嗯就这样。"
  → 有时带 markdown 标记
  → 有时少字段
  → 有时类型错（"18" vs 18）

Structured output（OpenAI 叫 json_schema）：
  response_format: {schema: ...}
  → 直接返回合规 JSON
  → 100% 解析
  → 字段类型强约束
```

## 🚀 OpenAI json_schema（推荐）

```python
from pydantic import BaseModel
from openai import OpenAI

class Weather(BaseModel):
    city: str
    temperature: float
    unit: str = "celsius"
    condition: str
    humidity: int

client = OpenAI()
resp = client.beta.chat.completions.create(
    model="gpt-4o-2024-08-06",     # 支持 json_schema
    messages=[
        {"role": "system", "content": "提取天气信息。"},
        {"role": "user", "content": "北京今天 25 度，湿度 60%，晴。"}
    ],
    response_format=Weather        # pydantic
)
weather: Weather = resp.choices[0].message.parsed
print(weather.city, weather.temperature, weather.humidity)
# 北京 25.0 60
```

## 📐 Pydantic 字段约束

```python
from pydantic import BaseModel, Field
from typing import Literal

class Job(BaseModel):
    title: str
    seniority: Literal["junior", "mid", "senior"]    # 枚举
    salary_min: int = Field(ge=0)                     # >= 0
    salary_max: int = Field(ge=0, le=1_000_000)
    remote: bool = False
    skills: list[str] = Field(max_length=10)         # 数组限制

resp = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[{"role":"user","content":"招资深 RAG 工程师，3-5 年经验，远程，60-90k"}],
    response_format=Job
)
job = resp.choices[0].message.parsed
print(job.model_dump_json(indent=2))
# {
#   "title": "RAG 工程师",
#   "seniority": "senior",
#   ...
# }
```

## 🚀 Anthropic Tool Use + Schema

```python
# Claude 用 input_schema
import json
from anthropic import Anthropic

client = Anthropic()
tools = [{
    "name": "extract_job",
    "description": "Extract job info",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "seniority": {"type": "string", "enum": ["junior","mid","senior"]},
            "salary_min": {"type": "integer"},
            "skills": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["title", "seniority"]
    }
}]

# 调 tool
resp = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    tools=[tools],
    tool_choice={"type": "tool", "name": "extract_job"},
    messages=[{"role":"user","content":"招资深 RAG 工程师，3-5 年，远程，60-90k"}]
)
data = json.loads(resp.content[0].input)
# {"title": "...", "seniority": "senior", ...}
```

## 🚀 LangChain

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel

class Weather(BaseModel):
    city: str
    temperature: float

parser = PydanticOutputParser(pydantic_object=Weather)

prompt = ChatPromptTemplate.from_template("""
提取天气：
{format_instructions}
文本：{text}
""").partial(format_instructions=parser.get_format_instructions())

chain = prompt | llm | parser
weather: Weather = chain.invoke({"text": "北京 25 度"})
```

## 🆚 JSON Schema vs JSON mode vs function calling

| | json_schema | json mode | tool use |
|--|-------------|-----------|----------|
| 模式 | 严格 | 严格 | 调用函数 |
| 强制 schema | ✅ | ❌（仅 JSON） | ✅ |
| 用法 | 解析结果 | 解析 JSON | 执行函数 |
| 何时 | 抽数据 / 分类 | 通用 | 调工具 |

```python
# json_schema
response_format=Weather

# json mode
response_format={"type":"json_object"}

# tool use
tools=[...]
```

## 🧠 复杂 schema

```python
from pydantic import BaseModel
from typing import List, Dict, Optional, Union, Literal
from datetime import datetime

class Address(BaseModel):
    street: str
    city: str
    country: str = "China"

class Employee(BaseModel):
    name: str
    age: int
    skills: List[str]
    address: Optional[Address] = None
    role: Literal["intern", "full-time", "contractor"]
    joined: datetime

class Company(BaseModel):
    name: str
    employees: List[Employee]
    metadata: Dict[str, Union[str, int]]

# Claude / OpenAI 都能从这种 schema 生成
```

## 🔄 嵌套 + 引用

```python
class Comment(BaseModel):
    author: str
    text: str
    replies: list["Comment"] = []   # 自引用

Comment.model_rebuild()  # pydantic 2.x
```

## 🛠 流式

```python
# OpenAI 不直接支持流式 json_schema
# 变通：用 stream + 解析部分 JSON
from pydantic import TypeAdapter

stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    response_format=Weather,
    stream=True
)

# 收集
parts = []
for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta: parts.append(delta)
text = "".join(parts)
weather = Weather.model_validate_json(text)
```

## 🆚 vs Regex 提取

| | json_schema | Regex |
|--|-------------|-------|
| 准确 | 高 | 低（LLM 输出变化就坏） |
| 复杂 schema | ✅ | ❌ |
| 性能 | 略慢 | 快 |
| 适合 | 生产 | 简单抽取 |

## 🛠 实战

```python
# 1. 抽简历 → 结构化
class Resume(BaseModel):
    name: str
    email: str
    years_exp: int
    skills: list[str]
    educations: list[dict]

prompt = "抽这个简历：{text}"
chain = prompt | llm | PydanticOutputParser(pydantic_object=Resume)
resume = chain.invoke({"text": "..."})

# 2. 分类 + 抽取
class Sentiment(BaseModel):
    label: Literal["positive", "negative", "neutral"]
    confidence: float = Field(ge=0, le=1)
    reason: str

# 3. 多轮对话后最终抽
class LeadInfo(BaseModel):
    name: Optional[str]
    budget: Optional[int]
    timeline: Optional[str]
    pain_points: list[str]
    next_step: str
```

## 🔗 下一步

- [Function Calling](/11-tools/function-calling)
- [Tool Use 模式](/11-tools/tool-use)
- [LangChain](/03-sdks/langchain)