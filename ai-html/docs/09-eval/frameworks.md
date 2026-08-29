---
title: Eval 框架
date: 2026-08-15  # date-auto-injected
---

# LLM Eval - 评测框架

> LLM 输出**不唯一**——你怎么知道新模型比旧的好？需要**评测**。

## 🤔 为什么需要 Eval

```
❌ 凭感觉："看着不错"
❌ 看几个例子：bias
✅ 系统性评测：定量、可复现
```

## 🏆 主流框架

| 框架 | 适合 | 特点 |
|------|------|------|
| **promptfoo** | prompt 对比 | YAML 配置 / 简单 |
| **deepeval** | G-Eval / 各种指标 | 综合 |
| **Ragas** | RAG | 检索 / 答案质量 |
| **OpenAI Evals** | OpenAI 模型 | 官方 |
| **MLflow LLM Evaluate** | Mlflow 生态 | 集成 |
| **LangSmith** | LangChain 生态 | tracing + eval |
| **Braintrust** | SaaS | 商业 |
| **MTEB** | Embedding | 检索评测 |

## 🚀 promptfoo（最易上手）

```bash
npm i -g promptfoo
promptfoo init
promptfoo eval
promptfoo view    # 打开浏览器看结果
```

```yaml
# promptfooconfig.yaml
prompts:
  - '你是一个翻译助手。把 {{text}} 翻译成 {{language}}。'
  - |
    请将以下文本翻译成 {{language}}：
    {{text}}

providers:
  - openai:gpt-4o
  - openai:gpt-4o-mini
  - anthropic:claude-sonnet-4-5
  - openai:o1-mini

tests:
  - vars:
      text: "Hello, world"
      language: "法语"
    assert:
      - type: contains
        value: "Bonjour"
      - type: llm-rubric
        value: "翻译准确自然"
        provider: openai:gpt-4o

  - vars:
      text: "Good morning"
      language: "日语"
    assert:
      - type: contains
        value: "おはよう"
```

## 🛠 deepeval（Python 深度评测）

```bash
pip install deepeval
```

```python
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    HallucinationMetric
)
from deepeval import evaluate

# 1. 定义指标
metrics = [
    AnswerRelevancyMetric(threshold=0.7),
    FaithfulnessMetric(threshold=0.8),
    HallucinationMetric(threshold=0.9)
]

# 2. 跑评测
test_cases = [
    LLMTestCase(
        input="What is RAG?",
        actual_output="RAG is Retrieval-Augmented Generation...",
        expected_output="...",
        context=["RAG combines retrieval with LLM generation..."]
    )
]
evaluate(test_cases, metrics)
```

## 🛠 Ragas（RAG 专用）

```bash
pip install ragas
```

```python
from ragas import evaluate
from datasets import Dataset

# 1. 准备数据
dataset = Dataset.from_dict({
    "question": ["Q1", "Q2"],
    "contexts": [["..."], ["..."]],
    "answer": ["A1", "A2"],
    "ground_truth": ["ref1", "ref2"]
})

# 2. 评测
result = evaluate(
    dataset,
    metrics=[
        "context_precision",
        "context_recall",
        "faithfulness",
        "answer_relevancy"
    ]
)
print(result)
# {'context_precision': 0.85, 'faithfulness': 0.92, ...}
```

## 🛠 OpenAI Evals

```bash
pip install openai evals
```

```python
from evals.elsuite.algebra.algebra import Algebra
# 或自己写
```

## 🛠 LangSmith（LangChain 生态）

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "ls__..."

from langchain_openai import ChatOpenAI
from langchain.evaluation import load_evaluator, EvaluatorType

llm = ChatOpenAI(model="gpt-4o")
evaluator = load_evaluator(EvaluatorType.QA, llm=llm)

result = evaluator.evaluate_strings(
    prediction="...",
    reference="...",
    input="..."
)
print(result)
```

## 📊 评测指标速查

| 指标 | 含义 | 适合 |
|------|------|------|
| **Faithfulness** | 答案是否忠于 context | RAG |
| **Answer Relevancy** | 答案是否切题 | 通用 |
| **Context Precision** | 检索 top-k 中相关比例 | RAG |
| **Context Recall** | 答案用了多少相关 context | RAG |
| **Hallucination** | 答案是否编造 | 通用 |
| **Toxicity** | 是否含毒 | 内容生成 |
| **BLEU / ROUGE** | n-gram 重叠 | 翻译 / 摘要 |
| **LLM-as-Judge** | LLM 评分（GPT-4 打分） | 难量化任务 |
| **HumanEval / MBPP** | 代码正确率 | 代码生成 |
| **MMLU** | 多任务知识 | 综合 |
| **HumanEval+** | 真实编程 | 代码 |

## 🛠 LLM-as-Judge 实战

```python
judge_prompt = """
你是一个严格的评估员。给下面的回答打分（0-10）。

问题：{question}
参考答案：{reference}
AI 回答：{prediction}

评估维度：
- 准确性（vs 参考）
- 完整性
- 清晰度

输出 JSON：{"score": 0-10, "reason": "..."}
"""

def judge(question, reference, prediction):
    resp = client.messages.create(
        model="gpt-4o",
        messages=[{"role":"user","content":judge_prompt.format(...)}]
    )
    import json
    return json.loads(resp.content[0].text)
```

## 📈 Benchmark（模型对比）

| Benchmark | 测什么 |
|-----------|--------|
| MMLU | 多任务知识 |
| HumanEval / HumanEval+ | 代码 |
| GSM8K | 数学 |
| MATH | 高难数学 |
| MT-Bench / Chatbot Arena | 对话 |
| MTEB | Embedding |
| TruthfulQA | 真实性 |
| HellaSwag | 常识推理 |
| BIG-bench | 综合 |

看 [lmsys.org/chatbot-arena](https://lmsys.org/chatbot-arena-leaderboard/) 看实时排行。

## 🔗 下一步

- [Benchmark 与指标](/09-eval/benchmark)
- [RLHF / DPO](/09-eval/alignment)
- [RAG 模式详解](/05-rag/patterns)