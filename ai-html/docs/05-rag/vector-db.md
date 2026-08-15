---
title: 向量数据库
---

# 向量数据库（Vector DB）

> 存 **embedding 向量** + 快速 **相似度检索**（ANN）。RAG 的核心存储。

## 🤔 为什么需要专用向量库

```
传统数据库：精确匹配（= / > / <）
向量库：    相似度检索（找最近邻）

数据：1024 维浮点数 × 百万条
查询：给一个向量，返回 top-k 最相似
```

## 🏆 主流对比

| 库 | 类型 | 性能 | 特点 |
|----|------|------|------|
| **Pinecone** | 托管 SaaS | 极强 | 不用运维 / 贵 |
| **Chroma** | 嵌入式 | 中 | 轻量 / 适合 demo / 本地 |
| **Weaviate** | 开源 / 自托管 | 强 | 多模态 / GraphQL |
| **Qdrant** | 开源 | 强 | Rust 实现 / 性能 |
| **Milvus** | 开源 / 自托管 | 极强 | 大规模 / 分布式 |
| **Qdrant Cloud** | 托管 | 强 | Qdrant 官方 |
| **pgvector** | Postgres 扩展 | 中 | 一库多用 / 简单 |
| **Pinecone Serverless** | 托管 | 强 | 按查询付费 |

## 🌲 选型指南

| 场景 | 推荐 |
|------|------|
| 个人 / 小项目 / demo | **Chroma**（最简） |
| 生产 / 中等规模 | **Qdrant** / **Weaviate** / **pgvector** |
| 大规模 / 千万级 | **Milvus** / **Pinecone** |
| 不想运维 | **Pinecone** / **Qdrant Cloud** |
| 已有 Postgres | **pgvector** |
| 多模态（图 / 视频） | **Weaviate** / **Milvus** |

## 🚀 各库速用

### Chroma（最简）

```bash
pip install chromadb
```

```python
import chromadb
client = chromadb.PersistentClient(path="./chroma")

# 自动用 sentence-transformers/all-MiniLM-L6-v2 embedding
collection = client.get_or_create_collection("my-docs")

# 加文档（自动 embed）
collection.add(documents=["hello world", "bye"], ids=["1", "2"])

# 检索
results = collection.query(query_texts=["hi"], n_results=2)
for doc, dist in zip(results["documents"][0], results["distances"][0]):
    print(dist, doc)
```

### Qdrant（推荐 / Rust 强）

```bash
docker run -d -p 6333:6333 qdrant/qdrant
pip install qdrant-client
```

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

client = QdrantClient("localhost", port=6333)

# 建 collection
client.recreate_collection(
    collection_name="my_docs",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
)

# 加（自己 embed 后传）
client.upsert(
    collection_name="my_docs",
    points=[PointStruct(id=1, vector=[...], payload={"text": "..."})]
)

# 检索
hits = client.search(
    collection_name="my_docs",
    query_vector=[...],
    limit=5
)
for h in hits:
    print(h.payload["text"], h.score)
```

### pgvector（Postgres 一体化）

```sql
-- 装扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 表
CREATE TABLE docs (
    id BIGSERIAL PRIMARY KEY,
    content TEXT,
    embedding VECTOR(1536)
);

-- 加
INSERT INTO docs (content, embedding) VALUES ('hello', '[...]');

-- 检索（余弦相似度）
SELECT content, embedding <=> '[...]' AS distance
FROM docs
ORDER BY distance LIMIT 5;
```

```python
# Python 客户端
import psycopg
conn = psycopg.connect("postgresql://user:pass@localhost/db")
cur = conn.execute("SELECT content FROM docs ORDER BY embedding <=> %s LIMIT 5", (query_vec,))
for row in cur: print(row[0])
```

### Pinecone（托管）

```python
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="...")
pc.create_index(
    name="my-index",
    dimension=1536,
    metric="cosine",
    spec=ServerlessSpec(cloud="aws", region="us-east-1")
)
index = pc.Index("my-index")

index.upsert(vectors=[("id1", [0.1, 0.2, ...], {"text": "..."})])
results = index.query(vector=[...], top_k=5, include_metadata=True)
```

### Milvus（大规模生产）

```python
from pymilvus import MilvusClient

client = MilvusClient(uri="http://localhost:19530")
client.create_collection(collection_name="my", dimension=1536)

data = [{"id": 1, "vector": [...], "text": "..."}]
client.insert(collection_name="my", data=data)

results = client.search(
    collection_name="my",
    data=[[...]],      # query vector
    limit=5,
    output_fields=["text"]
)
```

## 🔍 检索参数

```python
# 相似度
distance = "cosine"     # 余弦（最常用，归一化向量）
# distance = "euclidean"  # 欧氏
# distance = "dot"         # 点积

# 检索
k = 5                # 返回 top-5

# 过滤（pgvector / Qdrant 支持）
filter = {"category": "tech", "date": {"$gt": "2024-01-01"}}
```

## 🆚 自建 vs 托管

| | 自建 | 托管 |
|--|------|------|
| 成本 | 服务器（$50-2000/月） | 按向量数（$0.05-0.40/M 向量） |
| 运维 | 自己 | 厂商 |
| 弹性 | 固定 | 自动 |
| 起步 | 复杂 | 简单 |
| 大规模 | 自建费劲 | 弹性好 |

## 🔗 下一步

- [RAG 模式详解](/05-rag/patterns)
- [嵌入模型 Embedding](/05-rag/embedding)
- [LangChain](/03-sdks/langchain)
- [LlamaIndex](/03-sdks/llamaindex)