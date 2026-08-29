---
title: LangChain
date: 2026-08-15  # date-auto-injected
---

# LangChain

> 主流 LLM 应用框架。**LCEL（LangChain Expression Language）** 把链 / agent / RAG 用 `|` 串起来。

## 📦 安装

```bash
# 核心
pip install langchain

# 模型 / Embedding / 社区
pip install langchain-openai          # OpenAI
pip install langchain-anthropic       # Claude
pip install langchain-google-genai     # Gemini
pip install langchain-ollama          # 本地
pip install langchain-community        # 集成
pip install langchain-text-splitters
pip install langgraph                  # agent
```

## 🚀 LCEL 基础

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. 模型
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

# 2. 提示
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是资深 Python 工程师"),
    ("human", "{question}")
])

# 3. 解析
parser = StrOutputParser()

# 4. 链：prompt | llm | parser（管道）
chain = prompt | llm | parser
print(chain.invoke({"question": "什么是 async/await？"}))
```

## 🛠 ChatModel 统一接口

```python
# 任意模型同一调用方式
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

llm_openai = ChatOpenAI(model="gpt-4o")
llm_claude = ChatAnthropic(model="claude-sonnet-4-5")
llm_gemini = ChatGoogleGenerativeAI(model="gemini-2.5-pro")

# 全部 .invoke(messages)
resp = llm_claude.invoke([{"role":"user","content":"hi"}])
print(resp.content)
```

## 🧠 PromptTemplate

```python
# 简单
prompt = ChatPromptTemplate.from_template("回答: {q}")

# 多变量 + 系统消息
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是 {role}"),
    ("human", "{q}")
])
print(prompt.format(role="Python 工程师", q="..."))

# 消息占位
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是助手"),
    ("placeholder", "{history}"),  # 整段历史
    ("human", "{q}")
])
```

## 📚 RAG 全流程

```python
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

# 1. 加载
docs = WebBaseLoader("https://example.com").load()

# 2. 切片
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(docs)

# 3. embedding + 存
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vs = FAISS.from_documents(chunks, embeddings)

# 4. 检索 + 生成
retriever = vs.as_retriever(search_kwargs={"k": 3})
prompt = ChatPromptTemplate.from_template("根据上下文回答：{context}\n问题：{input}")
qa_chain = create_stuff_documents_chain(ChatOpenAI(model="gpt-4o"), prompt)
rag_chain = create_retrieval_chain(retriever, qa_chain)
print(rag_chain.invoke({"input": "..."})["answer"])
```

## 🛠 Tool use

```python
from langchain.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor

@tool
def search_docs(query: str) -> str:
    """Search internal knowledge base"""
    return "..."

llm = ChatOpenAI(model="gpt-4o")
tools = [search_docs]

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
print(executor.invoke({"input": "查找最新报销政策"})["output"])
```

## 🛠 Output parser

```python
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

class Joke(BaseModel):
    setup: str = Field(..., description="The setup of the joke")
    punchline: str = Field(..., description="The punchline")

parser = PydanticOutputParser(pydantic_object=Joke)
prompt = ChatPromptTemplate.from_template("讲个笑话\n{format_instructions}")
.format_instructions").partial(
    format_instructions=parser.get_format_instructions()
)
chain = prompt | llm | parser
joke: Joke = chain.invoke({})
print(joke.setup, joke.punchline)
```

## 🆚 vs LangGraph

| | LangChain LCEL | LangGraph |
|--|-----------------|-----------|
| 适合 | 简单链 / RAG | **复杂 agent / 循环 / 状态** |
| 风格 | 函数式 `\|` | 图（StateGraph） |
| 能力 | 链 + 简单 agent | 多步 / 并行 / 子图 / 持久化 |

**RAG 用 LangChain，Agent 用 LangGraph**。

## 🔗 下一步

- [Claude SDK / Anthropic](/03-sdks/claude-sdk)
- [OpenAI SDK](/03-sdks/openai-sdk)
- [LangGraph](/04-agents/langgraph)
- [RAG 模式详解](/05-rag/patterns)