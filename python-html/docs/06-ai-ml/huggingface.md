---
title: Hugging Face
---

# 🤗 Hugging Face

> **Hugging Face** 是 **AI 社区的 GitHub**，提供 **Transformers、Datasets、Tokenizers** 等工具，是预训练模型时代的**事实标准**。

## 🎯 Hugging Face 生态

```
Hub（模型中心）：
  - 100万+ 预训练模型
  - 20万+ 数据集
  - 30万+ 演示应用（Spaces）

库（Python SDK）：
  - transformers：预训练模型
  - datasets：数据集加载
  - tokenizers：分词器
  - accelerate：训练加速
  - diffusers：图像生成
  - safetensors：模型序列化
```

## 🚀 快速开始

### 安装

```bash
pip install transformers datasets tokenizers
# torch / tensorflow（按需）
pip install torch
```

### 第一个任务：情感分析

```python
from transformers import pipeline

# 一行代码完成情感分析
classifier = pipeline("sentiment-analysis")
result = classifier("I love this movie!")
print(result)
# [{'label': 'POSITIVE', 'score': 0.9998}]

# 多条文本
texts = ["I love Python", "This is terrible"]
results = classifier(texts)
for text, result in zip(texts, results):
    print(f"{text}: {result['label']} ({result['score']:.2f})")
```

## 🛠️ Pipeline 任务

```python
from transformers import pipeline

# 文本分类
classifier = pipeline("sentiment-analysis")

# 文本生成
generator = pipeline("text-generation", model="gpt2")
result = generator("Once upon a time", max_length=50, num_return_sequences=2)

# 问答
qa = pipeline("question-answering")
result = qa(question="What is Python?", 
            context="Python is a popular programming language.")

# 命名实体识别
ner = pipeline("ner")
result = ner("Apple was founded by Steve Jobs in California.")

# 文本摘要
summarizer = pipeline("summarization")
result = summarizer("Long article text here...")

# 翻译
translator = pipeline("translation_en_to_zh", model="Helsinki-NLP/opus-mt-en-zh")
result = translator("Hello, how are you?")

# 图像分类
classifier = pipeline("image-classification")
result = classifier("image.jpg")

# 目标检测
detector = pipeline("object-detection")
result = detector("image.jpg")

# 语音识别
asr = pipeline("automatic-speech-recognition")
result = asr("audio.wav")

# 文本生成（对话）
chat = pipeline("text-generation", model="microsoft/DialoGPT-medium")
result = chat("Hello,", max_length=100)
```

## 🛠️ 使用预训练模型

### AutoModel（自动选择模型）

```python
from transformers import AutoTokenizer, AutoModel

# 加载 tokenizer 和模型
model_name = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# 文本编码
inputs = tokenizer("Hello, world!", return_tensors="pt")
print(inputs)
# {'input_ids': tensor([[  101,  7592,  1010,  2088,   999,   102]]), ...}

# 模型推理
outputs = model(**inputs)
print(outputs.last_hidden_state.shape)
# torch.Size([1, 6, 768])
```

### 文本分类

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# 加载预训练模型
model_name = "distilbert-base-uncased-finetuned-sst-2-english"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# 推理
text = "I love this movie!"
inputs = tokenizer(text, return_tensors="pt")

with torch.no_grad():
    outputs = model(**inputs)

# 获取预测
logits = outputs.logits
probs = torch.softmax(logits, dim=-1)
predicted_class = torch.argmax(probs).item()
labels = ["NEGATIVE", "POSITIVE"]
print(f"预测: {labels[predicted_class]} ({probs[0][predicted_class].item():.2%})")
```

### 文本生成

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# 生成
input_text = "The future of AI is"
inputs = tokenizer(input_text, return_tensors="pt")
outputs = model.generate(
    **inputs,
    max_length=50,
    num_return_sequences=2,
    temperature=0.7,
    do_sample=True,
    top_p=0.9
)

for i, output in enumerate(outputs):
    text = tokenizer.decode(output, skip_special_tokens=True)
    print(f"生成 {i+1}: {text}")
```

## 📊 文本嵌入（Embeddings）

### Sentence Transformers

```bash
pip install sentence-transformers
```

```python
from sentence_transformers import SentenceTransformer

# 加载模型
model = SentenceTransformer('all-MiniLM-L6-v2')

# 编码句子
sentences = [
    "Python is a programming language",
    "Java is also a programming language",
    "I love eating pizza"
]
embeddings = model.encode(sentences)
print(embeddings.shape)  # (3, 384)

# 计算相似度
from sentence_transformers import util
similarity = util.cos_sim(embeddings, embeddings)
print(similarity)
# tensor([[1.0000, 0.7234, 0.1234],
#         [0.7234, 1.0000, 0.0987],
#         [0.1234, 0.0987, 1.0000]])
```

### 文本搜索

```python
# 构建语义搜索
corpus_embeddings = model.encode(corpus)

# 查询
query = "What is a programming language?"
query_embedding = model.encode(query)

# 找最相似的
hits = util.semantic_search(query_embedding, corpus_embeddings, top_k=3)
for hit in hits[0]:
    print(f"Score: {hit['score']:.3f} | {corpus[hit['corpus_id']]}")
```

## 📊 数据集（datasets）

```python
from datasets import load_dataset

# 加载内置数据集
dataset = load_dataset("imdb")
print(dataset)
# DatasetDict({
#     train: Dataset({
#         features: ['text', 'label'],
#         num_rows: 25000
#     }),
#     test: Dataset(...)
# })

# 访问数据
print(dataset["train"][0])
# {'text': 'I rented...', 'label': 0}

# 数据切片
train_data = dataset["train"].select(range(100))

# 数据处理
def tokenize(example):
    return tokenizer(example["text"], truncation=True, max_length=512)

tokenized = dataset["train"].map(tokenize, batched=True)

# 数据划分
train_test = dataset["train"].train_test_split(test_size=0.2)
```

### 加载自定义数据集

```python
from datasets import load_dataset

# 从 CSV
dataset = load_dataset("csv", data_files="data.csv")

# 从 JSON
dataset = load_dataset("json", data_files="data.json")

# 从 Hugging Face Hub
dataset = load_dataset("squad", split="train")
```

## 🛠️ 微调预训练模型

### 准备数据

```python
from datasets import load_dataset
from transformers import AutoTokenizer

# 加载数据
dataset = load_dataset("imdb", split="train[:1000]")

# 分词
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

def tokenize(batch):
    return tokenizer(batch["text"], padding=True, truncation=True, max_length=512)

tokenized_dataset = dataset.map(tokenize, batched=True)
tokenized_dataset = tokenized_dataset.rename_column("label", "labels")
tokenized_dataset.set_format("torch", columns=["input_ids", "attention_mask", "labels"])
```

### 训练

```python
from transformers import (
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)
import numpy as np
from datasets import load_metric

# 加载模型
model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    num_labels=2
)

# 评估函数
def compute_metrics(eval_pred):
    metric = load_metric("accuracy")
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)

# 训练参数
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=64,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    logging_dir="./logs",
    learning_rate=2e-5
)

# 创建 Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    compute_metrics=compute_metrics
)

# 训练
trainer.train()

# 保存
model.save_pretrained("./my-model")
tokenizer.save_pretrained("./my-model")
```

## 🤖 Hugging Face Hub

### 浏览模型

```python
from huggingface_hub import HfApi, list_models

# 列出模型
models = list_models(filter="text-classification", limit=10)
for model in models:
    print(f"{model.modelId}: {model.downloads} downloads")
```

### 下载模型

```python
from huggingface_hub import snapshot_download

# 下载整个模型
snapshot_download(
    repo_id="bert-base-uncased",
    local_dir="./models/bert"
)

# 下载特定文件
from huggingface_hub import hf_hub_download
hf_hub_download(
    repo_id="bert-base-uncased",
    filename="config.json",
    local_dir="./models/bert"
)
```

### 推送模型到 Hub

```python
# 登录
huggingface-cli login

# 推送
model.push_to_hub("my-awesome-model")
tokenizer.push_to_hub("my-awesome-model")
```

## 🛠️ 实战：构建问答系统

```python
from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering

# 1. 加载 QA 模型
model_name = "distilbert-base-cased-distilled-squad"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForQuestionAnswering.from_pretrained(model_name)
qa = pipeline("question-answering", model=model, tokenizer=tokenizer)

# 2. 文档
context = """
Kafka is a distributed event streaming platform. 
It was originally developed by LinkedIn and donated to the Apache Software Foundation.
Kafka is written in Scala and Java. It provides high throughput, low latency.
"""

# 3. 问答
questions = [
    "What is Kafka?",
    "Who developed Kafka?",
    "What language is Kafka written in?"
]

for q in questions:
    result = qa(question=q, context=context)
    print(f"Q: {q}")
    print(f"A: {result['answer']} (score: {result['score']:.2f})\n")
```

## 🎯 总结

**Hugging Face 核心要点**：
- ✅ 最大的 AI 社区和模型中心
- ✅ transformers 库一键加载预训练模型
- ✅ pipeline 任务抽象（情感分析、问答、生成）
- ✅ Datasets 库加载数据集
- ✅ Tokenizers 高效分词
- ✅ 微调预训练模型（Trainer API）
- ✅ Hub 浏览、下载、上传模型
- ⚠️ 大模型需要 GPU 推理
- ⚠️ 微调需要合理超参数

**下一步：** [💬 LLM 应用开发](/06-ai-ml/llm-apps) — LangChain / RAG / Agent
