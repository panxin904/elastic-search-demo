---
title: Benchmark 与指标
date: 2026-08-15  # date-auto-injected
---

# Benchmark 与指标

> 模型对比看 benchmark 排行榜。**不要只看一个，要看多个**。

## 🏆 综合排行

| Benchmark | 测什么 | 看什么 |
|-----------|--------|--------|
| **MMLU** | 57 个学科 | 综合知识 |
| **MMLU-Pro** | MMLU 增强版（推理） | 复杂知识 |
| **HumanEval / HumanEval+** | 编程题 | 代码能力 |
| **GSM8K** | 小学数学（文字题） | 数学推理 |
| **MATH** | 高中竞赛 | 高级数学 |
| **MT-Bench** | 多轮对话 | 真实对话 |
| **Chatbot Arena (LMSYS)** | 用户盲评 | 真实偏好 |
| **TruthfulQA** | 真实性 | 抗幻觉 |
| **HellaSwag** | 常识推理 | 通用 |
| **IFEval** | 指令遵循 | 复杂指令 |
| **GPQA** | 研究生级问答 | 推理 |
| **MGSM** | 多语言数学 | 多语言 |
| **BBH** | BIG-Bench Hard | 综合推理 |

## 🏆 RAG / Agent 评测

| Benchmark | 测什么 |
|-----------|--------|
| **Natural Questions** | 开放域 QA |
| **TriviaQA** | 琐事 QA |
| **HotpotQA** | 多跳推理 QA |
| **BEIR** | 检索评测套件 |
| **RAGAS** | RAG 三件套（faithfulness / relevance / recall） |
| **WebArena** | Web Agent |
| **SWE-bench** | 真实软件工程问题 |

## 📊 当前闭源旗舰对比（2025 年）

| Benchmark | Claude Sonnet 4.5 | GPT-5 | Gemini 2.5 Pro | DeepSeek V3 |
|-----------|------------------|-------|---------------|---------------|
| MMLU | 88.0 | 87.5 | 86.0 | 88.5 |
| HumanEval+ | 92.0 | 90.5 | 88.0 | 85.0 |
| GSM8K | 97.0 | 96.0 | 94.0 | 90.0 |
| MATH | 75.0 | 78.0 | 72.0 | 68.0 |
| MT-Bench | 9.0 | 8.9 | 8.8 | 8.6 |
| SWE-bench | 65.0 | 60.0 | 55.0 | 42.0 |
| LiveCodeBench | 70.0 | 65.0 | 60.0 | 50.0 |

（数字为示例，会随版本变化）

## 📊 开源模型

| Benchmark | Qwen2.5-72B | Llama 3.3 70B | Mistral Large 2 | DeepSeek V3 |
|-----------|------------|---------------|------------------|--------------|
| MMLU | 86.1 | 86.0 | 84.0 | 88.5 |
| HumanEval | 86.6 | 88.4 | 92.0 | 82.6 |
| GSM8K | 95.2 | 95.1 | 93.0 | 89.3 |
| MATH | 80.2 | 77.3 | 69.0 | 67.6 |

## 📏 选 benchmark 原则

```
1. 测你的实际任务，不是泛泛指标
2. 多个 benchmark 一起看（避免 benchmark overfit）
3. 真实场景 > 标准化测试集
4. 自己的 eval set 比公开 benchmark 更准
```

## 🎯 实战：自己建 benchmark

```python
# 1. 收集真实用户 query
queries = collect_recent_questions(n=500)

# 2. 专家标注 answer（100-500 条高质量）
labels = {}
for q in sample(queries, 200):
    labels[q] = human_label(q)

# 3. 跑模型 A / B
def eval_model(model_name):
    correct = 0
    for q, ref in labels.items():
        pred = model.complete(q)
        if judge(q, ref, pred) >= 7:   # LLM-as-judge ≥ 7 分
            correct += 1
    return correct / len(labels)

print(f"Model A: {eval_model('gpt-4o'):.0%}")
print(f"Model B: {eval_model('claude-sonnet-4-5'):.0%}")
```

## 📈 看真实对话排名

[Chatbot Arena Leaderboard](https://lmsys.org/chatbot-arena-leaderboard/)：
- 真实用户盲评
- 投票 → Elo 评分
- 当前 top：Claude / GPT / Gemini / DeepSeek

## 🛠 跑 benchmark 套件

```bash
# HuggingFace evaluate
pip install evaluate

# HumanEval
python -m eval --benchmark humaneval --model gpt-4o

# MMLU
python -m eval --benchmark mmlu --model gpt-4o

# Ragas
ragas evaluate --metrics faithfulness context_precision
```

## 🔬 指标详解

### Faithfulness（事实性 / 抗幻觉）

```python
# 答案有多少可被 context 支持
# 1.0 = 完全忠于 context
# 0.0 = 完全编造
score = evaluate(
    answer, context,
    metric="faithfulness"
)
```

### Answer Relevancy

```python
# 答案与问题的相关度
# 答非所问 → 低
# 直接切题 → 高
```

### Context Precision / Recall

```python
# Precision：top-k 检索里相关文档的比例
# Recall：相关文档被检索到的比例
```

### BLEU / ROUGE

```python
# BLEU：n-gram 精确匹配（机器翻译）
# ROUGE：n-gram 召回匹配（摘要）
# 问题：跟人类判断相关性差
```

## 🔗 下一步

- [Eval 框架](/09-eval/frameworks)
- [RLHF / DPO](/09-eval/alignment)
- [RAG 模式详解](/05-rag/patterns)