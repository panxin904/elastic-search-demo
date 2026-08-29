---
title: 嵌入模型 Embedding
date: 2026-08-15  # date-auto-injected
---

# 嵌入模型（Embedding）

> 把文本 / 图 / 音 / 视频 → 数值向量（dense vector）。**语义检索的基础**。

## 🧬 主流 Embedding 模型

| 模型 | 维度 | 上下文 | 价格 ($/MTok) | 特点 |
|------|------|--------|---------------|------|
| **OpenAI text-embedding-3-small** | 1536 | 8K | 0.02 | 性价比首选 |
| OpenAI text-embedding-3-large | 3072 | 8K | 0.13 | 质量高 |
| **OpenAI text-embedding-ada-002** | 1536 | 8K | 0.10 | 上一代 |
| **Voyage-3** | 1024 | 32K | 0.06 | 检索质量 SOTA |
| **Cohere embed-v3** | 1024 | 8K | 0.10 | 多语言强 |
| **BGE-M3** | 1024 | 8K | 免费 | 中文 SOTA / BAAI |
| **M3E** | 1024 | 8K | 免费 | 中文 |
| **Nomic Embed v1.5** | 768 | 8K | 免费 | 英文强 |
| **all-MiniLM-L6-v2** | 384 | 256 | 免费 | Sentence-Transformers 经典 |
| **Cohere embed-multilingual-v3** | 1024 | 8K | 0.10 | 多语言 |
| **Jina v3** | 1024 | 8K | 免费 | 1024 维 / 多语言 |

## 🚀 使用

### OpenAI

```python
from openai import OpenAI
client = OpenAI()

resp = client.embeddings.create(
    model="text-embedding-3-small",
    input="你好世界"
)
vec = resp.data[0].embedding   # list of 1536 floats
print(len(vec), vec[:3])
```

### 本地（Sentence-Transformers）

```bash
pip install sentence-transformers
```

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-m3")   # 自动下载
vec = model.encode("你好世界", normalize_embeddings=True)
print(len(vec), vec[:3])
```

### Ollama（任何 LLM 提供 embedding 也行）

```bash
ollama pull nomic-embed-text
ollama serve
```

```python
import requests
def embed(text):
    r = requests.post("http://localhost:11434/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": text})
    return r.json()["embedding"]
```

### LangChain 统一接口

```python
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings, OllamaEmbeddings

# OpenAI
emb = OpenAIEmbeddings(model="text-embedding-3-small")
vec = emb.embed_query("hi")

# 本地
emb = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
vec = emb.embed_query("hi")

# Ollama
emb = OllamaEmbeddings(model="nomic-embed-text")
vec = emb.embed_query("hi")
```

## 🔍 选型指南

| 场景 | 选 |
|------|-----|
| 通用 / 英文 | text-embedding-3-small（便宜够用） |
| **质量优先** | Voyage-3（检索 SOTA） |
| **中文** | BGE-M3（开源）/ text-embedding-3-large |
| 多语言 | Cohere embed-multilingual-v3 |
| 离线 / 隐私 | BGE-M3 / all-MiniLM（本地） |
| 大量文档 / 便宜 | text-embedding-3-small + 量化（matryoshka） |
| 图像 / 多模态 | CLIP / SigLIP / BGE-VL |

## 📐 维度（Dimensions）

```python
# 维度 = 检索质量 vs 存储 / 速度
# 维度越高 → 检索越准，但存更多 + 算更慢

# OpenAI text-embedding-3 支持 matryoshka（多维度）
# 训练时把 3072 维套娃成 1536 / 768 / 256
resp = client.embeddings.create(
    model="text-embedding-3-large",
    input="hi",
    dimensions=512   # 只用 512 维，省 6 倍存储
)
```

## 🛠 实战：批量 Embedding + 存入向量库

```python
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

client = OpenAI()
qdrant = QdrantClient("localhost", port=6333)

texts = ["doc1", "doc2", "doc3"]
resp = client.embeddings.create(
    model="text-embedding-3-small",
    input=texts
)
vectors = [d.embedding for d in resp.data]

qdrant.upsert(
    collection_name="docs",
    points=[
        PointStruct(id=i, vector=v, payload={"text": t})
        for i, (v, t) in enumerate(zip(vectors, texts))
    ]
)
```

## 🔬 评估

```python
# MTEB（Massive Text Embedding Benchmark）
# https://huggingface.co/spaces/mteb/leaderboard
# 评估：检索 / 分类 / 聚类 / STS 等

# 自己用 Ragas 评估
from ragas.metrics import context_recall, context_precision
...
```

## 🆚 vs Sparse（BM25 / Splade）

| | Dense（向量） | Sparse（关键词） |
|--|---------------|---------------------|
| 语义匹配 | **强** | 弱 |
| 关键词精确 | 弱 | **强** |
| 多语言 | 强 | 弱（需每语言） |
| 速度 | 中 | 快 |
| 适合 | 复杂查询 | 短查询 / 精确词 |

**混合检索（hybrid）**：dense + sparse + rerank = 工业级标准做法。

```python
from langchain.retrievers import EnsembleRetriever
retriever = EnsembleRetriever(
    retrievers=[dense_retriever, bm25_retriever],
    weights=[0.7, 0.3]
)
```

## 🔗 下一步

- [RAG 模式详解](/05-rag/patterns)
- [向量数据库](/05-rag/vector-db)
- [LangChain](/03-sdks/langchain)
- [LlamaIndex](/03-sdks/llamaindex)