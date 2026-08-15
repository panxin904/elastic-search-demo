---
title: 数据准备
---

# 微调数据准备

> **数据质量 > 数据量**。10 万条高质量 > 100 万条低质量。

## 📊 数据集类型

| 类型 | 用途 | 例子 |
|------|------|------|
| **Instruct（指令）** | SFT / 对齐 | "问题 → 回答" |
| **Preference（偏好）** | DPO / PPO | "回答 A > 回答 B" |
| **CPT（继续预训练）** | 领域适配 | 大段无标注文本 |
| **多模态** | 图文对齐 | 图 → 文 / 文 → 图 |

## 📚 数据来源

### 开源数据集

```python
from datasets import load_dataset

# Hugging Face Hub（10 万 + 数据集）
ds = load_dataset("Anthropic/hh-rlhf")              # RLHF
ds = load_dataset("argilla/distilabel-intel-orca-dpo-pairs")  # DPO
ds = load_dataset("yahma/alpaca-cleaned")            # 52K Alpaca
ds = load_dataset("OpenAssistant/oasst1")             # 多语言对话
ds = load_dataset("BAAI/COIG-PC-Lite")               # 中文
ds = load_dataset("garage-bAInd/Open-Platypus")      # 推理
ds = load_dataset("Open-Orca/SlimOrca")               # 高质量
```

### 自建

```python
# 1. 内部文档
docs = SimpleDirectoryReader("./company-docs").load_data()

# 2. 用户对话
def export_user_chats():
    chats = db.query("SELECT role, content FROM messages WHERE created_at > NOW() - INTERVAL '90 days'")
    return [{"messages": [{"role": r.role, "content": r.content} for r in c]} for c in chats]

# 3. GitHub Issues
import requests
issues = requests.get("https://api.github.com/repos/owner/repo/issues").json()
```

## 📝 数据格式

### 1. Instruct（Alpaca 风格）

```json
{
  "instruction": "用 Python 写一个快排",
  "input": "",
  "output": "def quicksort(arr):\n  if len(arr) <= 1: return arr\n  ..."
}
```

```python
def to_alpaca(ex):
    return {
        "instruction": ex["q"],
        "input": ex.get("ctx", ""),
        "output": ex["a"]
    }
```

### 2. ChatML（多轮）

```json
{
  "messages": [
    {"role":"system","content":"你是助手"},
    {"role":"user","content":"什么是 RAG？"},
    {"role":"assistant","content":"RAG 是..."},
    {"role":"user","content":"怎么用 LangChain 做？"},
    {"role":"assistant","content":"参考以下代码..."}
  ]
}
```

### 3. 偏好（DPO）

```json
{
  "prompt": "Python 怎么反转字符串？",
  "chosen": "s[::-1]",
  "rejected": "for i in reversed(s): ..."
}
```

### 4. ShareGPT / OpenAI

```json
{
  "conversations": [
    {"from":"human","value":"hi"},
    {"from":"gpt","value":"hello"}
  ]
}
```

## 🧹 数据清洗

```python
# 1. 基础清洗
def clean(text):
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)         # 多空格合一
    text = re.sub(r'<\|.*?\|>', '', text)   # 移除特殊 token
    return text

# 2. 去重
seen = set()
unique = []
for ex in dataset:
    key = (ex['q'], ex['a'][:50])
    if key in seen: continue
    seen.add(key)
    unique.append(ex)

# 3. 长度过滤
def length_ok(ex):
    return 10 <= len(ex["q"]) <= 2000 and 10 <= len(ex["a"]) <= 4000
filtered = [ex for ex in unique if length_ok(ex)]

# 4. 质量过滤
import re
def has_garbage(text):
    return bool(re.search(r'http\S+|@\S+', text))  # 留邮箱 / URL 给专门的
clean = [ex for ex in filtered if not has_garbage(ex["a"])]
```

## 🔍 数据增强

```python
# 1. 反向翻译（en -> zh -> en）
from transformers import pipeline
translator = pipeline("translation", model="Helsinki-NLP/opus-mt-en-zh")
def back_translate(text):
    zh = translator(text)[0]["translation_text"]
    return translator(zh)[0]["translation_text"]

# 2. 同义改写（用 LLM）
def rewrite_variants(text):
    prompt = f"重写下面文本为 3 种不同说法：\n{text}"
    # ...

# 3. 对话角色转换
def flip_roles(ex):
    return {
        "messages": [
            {"role":"user","content":ex["a"]},
            {"role":"assistant","content":ex["q"]}
        ]
    }
```

## 🧪 质量评估

```python
# 1. LLM-as-a-judge
def judge_quality(ex):
    prompt = f"""
    评估下面 (Q, A) 对的质量（0-10）：
    Q: {ex['q']}
    A: {ex['a']}
    评分维度：准确性 / 有用性 / 清晰度
    输出 JSON：{{"score": x, "reason": "..."}}
    """
    # 用 Claude / GPT 打分
    return llm.complete(prompt)

# 2. 简单启发式
def heuristic_score(ex):
    score = 1.0
    if len(ex["a"]) < 50: score *= 0.5
    if "I don't know" in ex["a"]: score *= 0.3
    if re.search(r'\\b(error|undefined|null)\\b', ex["a"]): score *= 0.7
    return score

# 3. Embedding 一致性
def semantic_score(ex):
    qv = embed(ex["q"])
    av = embed(ex["a"])
    return cosine(qv, av)
```

## 📊 数据量参考

| 任务 | 数据量 | 训练时间（1xA100） |
|------|--------|---------------------|
| 风格微调 | 1k-10k | 几十分钟 |
| 任务适应 | 10k-100k | 几小时 |
| 行业大模型 | 1M+ | 几周 |
| 继续预训练 | 1B+ tokens | 几月 |

## 🛠 实战

```python
# 数据流水线
import json
from datasets import load_dataset, Dataset

# 1. 加载
raw = []
for source in ["your-internal-kb.jsonl", "github-issues.jsonl"]:
    with open(source) as f:
        raw.extend(json.loads(line) for line in f)

# 2. 清洗
cleaned = []
for ex in raw:
    if not 10 <= len(ex["q"]) <= 2000: continue
    if not 10 <= len(ex["a"]) <= 4000: continue
    if ex["q"] in ex["a"]: continue   # 太短或答非所问
    cleaned.append({"messages":[
        {"role":"user","content":ex["q"]},
        {"role":"assistant","content":ex["a"]}
    ]})

# 3. 去重
seen = set()
unique = []
for ex in cleaned:
    key = ex["messages"][0]["content"]
    if key in seen: continue
    seen.add(key)
    unique.append(ex)

# 4. 划分
ds = Dataset.from_list(unique)
split = ds.train_test_split(test_size=0.05)
split["train"].to_jsonl("train.jsonl")
split["test"].to_jsonl("test.jsonl")
```

## 🔗 下一步

- [LoRA / QLoRA](/08-finetuning/lora)
- [全量微调](/08-finetuning/full)
- [量化 GGUF / GPTQ](/08-finetuning/quantization)