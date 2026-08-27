---
title: RAG 模式详解
---

# RAG - 检索增强生成

> **R**etrieval-**A**ugmented **G**eneration。**让 LLM 回答自己不知道的（私有 / 实时）数据**。

## 🤔 为什么需要 RAG

```
LLM 局限：
  ❌ 知识截止（GPT-4 截止 2023-10）
  ❌ 不知道公司私有文档
  ❌ 不知道今天新闻
  ❌ 容易编（hallucination）

RAG = LLM + 外部知识库：
  ✅ 实时（拉最新数据）
  ✅ 私有（企业 KB / 内部 wiki）
  ✅ 可控（来源可追溯）
  ✅ 减少 hallucination
```

## 🏗 RAG 三步

```
[Documents] → 切片 + Embedding → [Vector DB]
                                    ↑
                              query 也走同样流程
                                    ↓
                                检索 top-k
                                    ↓
                         [LLM + query + retrieved docs] → Answer
```

## 📜 完整代码（最小版）

```python
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

# 1. 加载
docs = WebBaseLoader("https://example.com/docs").load()

# 2. 切片
chunks = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200
).split_documents(docs)

# 3. Embedding + 存
vectorstore = FAISS.from_documents(chunks, OpenAIEmbeddings())

# 4. 检索 + 生成
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
qa = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-4o"),
    retriever=retriever,
    return_source_documents=True
)
result = qa.invoke("公司的差旅政策？")
print(result["result"])
print(result["source_documents"][0].metadata)
```

## 🎯 高级 RAG 模式

### 1. HyDE（Hypothetical Document Embeddings）

```python
# 问题：query 短，文档长 → embedding 距离不靠谱
# HyDE：先让 LLM 想象一个"假想答案"，再 embed 这个假想答案
from langchain.chains import HypotheticalDocumentEmbedder
hyde = HypotheticalDocumentEmbedder.from_llm(
    llm=ChatOpenAI(model="gpt-4o"),
    base_embeddings=OpenAIEmbeddings()
)
```

### 2. Self-Query Retriever

```python
# LLM 自动把 query 解析成 metadata filter
from langchain.retrievers import SelfQueryRetriever
retriever = SelfQueryRetriever.from_llm(
    llm=ChatOpenAI(model="gpt-4o"),
    vectorstore=vs,
    document_content_description="技术文档",
    metadata_field_info=[
        AttributeInfo(name="date", type="date", description="发布日期"),
        AttributeInfo(name="author", type="string", description="作者")
    ]
)
```

### 3. Multi-Query

```python
# 把一个问题变成多个角度
from langchain.retrievers import MultiQueryRetriever
retriever = MultiQueryRetriever.from_llm(
    llm=ChatOpenAI(model="gpt-4o"),
    retriever=vectorstore.as_retriever()
)
```

### 4. Parent Document Retriever

```python
# 检索小 chunk，返回大 block（让 LLM 看到完整上下文）
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore

store = InMemoryStore()
retriever = ParentDocumentRetriever(
    vectorstore=vs,
    docstore=store,
    child_splitter=RecursiveCharacterTextSplitter(chunk_size=200),
    parent_splitter=RecursiveCharacterTextSplitter(chunk_size=2000)
)
```

### 5. Self-RAG（自评估检索）

```python
# LLM 自己判断"这个文档要不要用" / "答案对不对"
from langchain.retrievers import SelfQueryRetriever  # 简化版
# 或 LangGraph 编排更精细
```

## 🔧 Reranking（二次精排）

```python
# 1. Embedding 检索 top-50（快但粗）
# 2. Cross-encoder rerank 取 top-5（慢但准）
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder

reranker = CrossEncoderReranker(
    model=HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-v2-m3"),
    top_n=5
)
retriever = ContextualCompressionRetriever(
    base_compressor=reranker,
    base_retriever=vectorstore.as_retriever(search_kwargs={"k": 50})
)
```

## 📊 评估

```python
# Ragas（推荐）
pip install ragas
from ragas import evaluate
from datasets import Dataset

results = evaluate(
    dataset=Dataset.from_dict({
        "question": [...],
        "contexts": [...],   # 检索到的
        "answer": [...],
        "ground_truth": [...]
    }),
    metrics=[
        "context_precision",
        "context_recall",
        "faithfulness",
        "answer_relevancy"
    ]
)
print(results)
# {'context_precision': 0.85, 'faithfulness': 0.92, ...}
```

## 🆚 vs Fine-tuning

| | RAG | Fine-tuning |
|--|-----|-------------|
| 适合 | 知识更新 / 私有 | 学模型"风格" / 任务 |
| 数据量 | 文档 | 问答对 |
| 成本 | 低（仅 embedding + LLM） | 高（GPU + 数据） |
| 灵活 | 改文档即可 | 改模型难 |
| 时效 | 即时 | 重新训练 |

## 🔗 下一步

- [向量数据库](/05-rag/vector-db)
- [嵌入模型 Embedding](/05-rag/embedding)
- [LangChain](/03-sdks/langchain)
- [LlamaIndex](/03-sdks/llamaindex)

<!-- svg-injected:do-not-edit -->

## 图示：RAG 离线索引 + 在线查询

![RAG 离线索引 + 在线查询](/rag-architecture.svg)
