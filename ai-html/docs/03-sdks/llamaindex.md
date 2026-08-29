---
title: LlamaIndex
date: 2026-08-15  # date-auto-injected
---

# LlamaIndex

> 专注 **RAG（检索增强生成）** 的框架。和 LangChain 互补 — LangChain 全能，LlamaIndex 在 RAG 做得更精。

## 📦 安装

```bash
pip install llama-index
# 模型集成
pip install llama-index-llms-openai
pip install llama-index-llms-anthropic
pip install llama-index-embeddings-openai
pip install llama-index-embeddings-huggingface

# 高级
pip install llama-index-agent-openai
pip install llama-index-packs-rag
```

## 🚀 基础 RAG

```python
from llama_index.core import (
    VectorStoreIndex, SimpleDirectoryReader, Settings
)
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

# 1. 全局配置
Settings.llm = OpenAI(model="gpt-4o")
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

# 2. 加载文档
documents = SimpleDirectoryReader("./data").load_data()

# 3. 建索引（自动切片 + embedding + 存）
index = VectorStoreIndex.from_documents(documents)

# 4. 查询
query_engine = index.as_query_engine()
resp = query_engine.query("公司的差旅政策是什么？")
print(resp.response)
print(resp.get_formatted_sources())
```

## 🛠 高级 RAG

### 多文件 / 多数据源

```python
# 多种 loader
from llama_index.core import (
    SimpleDirectoryReader,
    download_loader
)
from llama_index.readers.web import SimpleWebPageReader
from llama_index.readers.github import GitHubRepositoryReader

# GitHub 仓库
docs = GitHubRepositoryReader(...).load_data(branch="main")
```

### Re-ranking

```python
from llama_index.core.postprocessor import SentenceTransformerRerank

rerank = SentenceTransformerRerank(
    model="cross-encoder/ms-marco-MiniLM-L-2-v2",
    top_n=3
)
query_engine = index.as_query_engine(
    similarity_top_k=10,
    node_postprocessors=[rerank]
)
```

### 多步查询（Sub-question）

```python
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.core.tools import QueryEngineTool

tool1 = QueryEngineTool.from_defaults(query_engine=qe1, name="hr")
tool2 = QueryEngineTool.from_defaults(query_engine=qe2, name="finance")
sqqe = SubQuestionQueryEngine.from_defaults(
    query_engine_tools=[tool1, tool2]
)
resp = sqqe.query("差旅 + 财务 整体政策？")
```

### Router Query Engine

```python
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector

# 不同问题走不同索引
router = RouterQueryEngine(
    selector=LLMSingleSelector.from_defaults(),
    query_engine_tools=[
        QueryEngineTool.from_defaults(query_engine=hr_engine, name="hr"),
        QueryEngineTool.from_defaults(query_engine=tech_engine, name="tech")
    ]
)
resp = router.query("差旅政策")  # 自动走 hr
resp = router.query("Python 异步")  # 自动走 tech
```

## 🤖 Agent

```python
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.tools import FunctionTool

def get_weather(city: str) -> str:
    """Get current weather for a city"""
    return f"{city} 25°C 晴"

agent = OpenAIAgent.from_tools(
    tools=[FunctionTool.from_defaults(fn=get_weather)],
    llm=OpenAI(model="gpt-4o"),
    verbose=True
)
resp = agent.chat("北京天气？")
print(resp.response)
```

## 🛠 Function calling

```python
from llama_index.core.tools import FunctionTool

@llm
def search_internal(query: str) -> str:
    """Search internal knowledge base"""
    return "..."

# 自动从函数签名提取 schema
tool = FunctionTool.from_defaults(fn=search_internal)
```

## 🆚 vs LangChain

| | LangChain | LlamaIndex |
|--|-----------|------------|
| 强项 | 全能 / Agent | **RAG** |
| 上手 | 中 | 易（RAG 模板多） |
| 灵活性 | 高 | 高 |
| 数据连接器 | 多 | **极多**（数百种 loader） |
| Agent | LangGraph 强 | Function calling 够用 |
| 选型 | 综合应用 | **专注 RAG / 知识库** |

## 🛠 实战：完整 RAG 项目

```python
# 1. 加载 PDF
from llama_index.readers.file import PDFReader
docs = PDFReader().load_data("company-handbook.pdf")

# 2. 切片（自定义）
from llama_index.core.node_parser import SentenceSplitter
nodes = SentenceSplitter(chunk_size=512, chunk_overlap=50).get_nodes_from_documents(docs)

# 3. 索引
from llama_index.core import StorageContext, load_index_from_storage
import os
if not os.path.exists("./storage"):
    storage_context = StorageContext.from_defaults()
    storage_context.docstore.add_documents(nodes)
    index = VectorStoreIndex(nodes=nodes, storage_context=storage_context)
    index.storage_context.persist(persist_dir="./storage")
else:
    storage_context = StorageContext.from_defaults(persist_dir="./storage")
    index = load_index_from_storage(storage_context=storage_context)

# 4. 查询 + streaming
query_engine = index.as_query_engine(streaming=True)
resp = query_engine.query("差旅政策")
for token in resp.response_gen:
    print(token, end="", flush=True)
```

## 🔗 下一步

- [LangChain](/03-sdks/langchain)
- [RAG 模式详解](/05-rag/patterns)
- [向量数据库](/05-rag/vector-db)