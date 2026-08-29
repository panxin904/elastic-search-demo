---
title: LLM 应用开发
date: 2026-08-15  # date-auto-injected
---

# 💬 LLM 应用开发

> **LLM（大语言模型）**应用开发是当前 AI 领域最热门的方向。本章讲解 **Prompt Engineering、RAG、Agent、Fine-tuning** 等核心概念和实战。

## 🎯 LLM 应用核心概念

```
Prompt Engineering（提示工程）：
  - 提示词设计
  - Few-shot Learning
  - Chain of Thought

RAG（检索增强生成）：
  - 外部知识补充
  - 解决幻觉
  - 数据更新

Agent（智能体）：
  - 调用工具
  - 多步推理
  - 自主决策

Fine-tuning（微调）：
  - LoRA / PEFT
  - 定制化模型
```

## 🚀 Prompt Engineering

### 基本原则

```
1. 清晰具体
   ❌ "写篇文章"
   ✅ "写一篇 800 字的科技文章，主题是 Python AI 库，风格通俗易懂"

2. 提供上下文
   ❌ "翻译这段话"
   ✅ "将以下英文翻译成中文，保持专业术语准确：[英文]"

3. 指定格式
   ❌ "列出关键点"
   ✅ "用 JSON 格式输出：{key_points: [...], summary: '...'}"

4. 角色设定
   "你是一位资深的 Python 工程师，擅长异步编程"

5. Few-shot（提供示例）
```

### Chain of Thought（思维链）

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": """
        一个水果店周一卖了 15 个苹果，周二卖了 23 个，周三卖的是周二的 2 倍。
        这三天一共卖了多少个苹果？
        
        让我们一步步思考：
        """}
    ]
)
print(response.choices[0].message.content)
```

### Few-shot Learning

```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": """
        将情感分类为 正面/负面：

        评论：这个产品太棒了！ -> 正面
        评论：质量很差，失望。 -> 负面
        评论：服务态度很好，下次还会来。 -> 
        """}
    ]
)
```

## 🛠️ LangChain 入门

### 安装

```bash
pip install langchain langchain-openai chromadb tiktoken
```

### Hello World

```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

# 1. LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# 2. Prompt 模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的{role}"),
    ("user", "{input}")
])

# 3. Chain
chain = LLMChain(llm=llm, prompt=prompt)

# 4. 调用
result = chain.invoke({"role": "Python 老师", "input": "什么是装饰器？"})
print(result["text"])
```

### 输出解析

```python
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

# 定义输出结构
class Person(BaseModel):
    name: str = Field(description="姓名")
    age: int = Field(description="年龄")

# 创建解析器
parser = PydanticOutputParser(pydantic_object=Person)

# 创建 Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "提取人物信息。\n{format_instructions}"),
    ("user", "{text}")
]).partial(format_instructions=parser.get_format_instructions())

# Chain
chain = prompt | llm | parser

# 调用
result = chain.invoke({"text": "Alice 今年 30 岁"})
print(result)  # Person(name='Alice', age=30)
```

## 🛠️ RAG（检索增强生成）

### 核心思想

```
传统 LLM：
  - 知识截止于训练时间
  - 容易产生幻觉
  - 无法访问私有数据

RAG（检索增强生成）：
  - 检索相关文档
  - 将文档作为上下文
  - LLM 基于真实数据回答
```

### 基础 RAG 实现

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# 1. 加载文档
loader = DirectoryLoader("./docs/", glob="**/*.txt")
documents = loader.load()
print(f"加载文档: {len(documents)} 个")

# 2. 文档分块
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents)
print(f"分块后: {len(texts)} 个")

# 3. 向量化（使用 OpenAI Embeddings）
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(texts, embeddings)

# 4. 保存到本地
vectorstore.save_local("vectorstore")

# 5. 加载
vectorstore = FAISS.load_local("vectorstore", embeddings, allow_dangerous_deserialization=True)

# 6. 创建检索器
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 7. 自定义 Prompt
prompt_template = """基于以下上下文回答问题。如果不知道答案，请说"我不知道"。

上下文：
{context}

问题：{question}

答案："""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)

# 8. 创建 RAG Chain
llm = ChatOpenAI(model="gpt-4", temperature=0)
qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt}
)

# 9. 问答
result = qa.invoke({"query": "文档中讲了什么？"})
print(f"答案: {result['result']}")
print(f"来源: {[doc.metadata['source'] for doc in result['source_documents']]}")
```

## 🤖 Agent（智能体）

### ReAct Agent

```python
from langchain_openai import ChatOpenAI
from langchain.agents import load_tools, initialize_agent, AgentType

# 1. LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# 2. 加载工具
tools = load_tools(["serpapi", "llm-math"], llm=llm)

# 3. 创建 Agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 4. 调用
result = agent.invoke({
    "input": "2024 年巴黎奥运会金牌榜前 3 名是哪些国家？它们各多少金牌？"
})
print(result)
```

### 自定义工具

```python
from langchain.agents import tool, Tool
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

# 自定义工具
@tool
def search_database(query: str) -> str:
    """在数据库中搜索商品"""
    # 实际实现：连接数据库，查询商品
    return f"找到 {query} 的搜索结果：3 条"

# 列表形式
def get_weather(city: str) -> str:
    """获取城市的天气"""
    return f"{city} 天气晴朗，25°C"

tools = [
    Tool(
        name="search_database",
        func=search_database,
        description="在数据库中搜索商品"
    ),
    Tool(
        name="get_weather",
        func=get_weather,
        description="获取城市的天气"
    )
]

# 创建 Agent
llm = ChatOpenAI(model="gpt-4", temperature=0)
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

result = agent.invoke({"input": "上海今天天气怎么样？"})
```

## 🛠️ LlamaIndex（RAG 框架）

```bash
pip install llama-index
```

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.settings import Settings
from llama_index.llms.openai import OpenAI

# 1. 配置
Settings.llm = OpenAI(model="gpt-4")

# 2. 加载文档
documents = SimpleDirectoryReader("./docs").load_data()

# 3. 构建索引
index = VectorStoreIndex.from_documents(documents)

# 4. 查询引擎
query_engine = index.as_query_engine()

# 5. 查询
response = query_engine.query("文档讲了什么？")
print(response)
```

## 🛠️ Prompt 模板高级用法

```python
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

# 1. 简单模板
template = ChatPromptTemplate.from_messages([
    ("system", "你是{role}"),
    ("user", "{input}")
])

# 2. 多消息模板
template = ChatPromptTemplate.from_messages([
    ("system", "你是一个翻译专家"),
    ("user", "请将以下文本翻译成{lang}：{text}"),
    ("assistant", "好的，我将翻译。"),
    ("user", "请提供更多上下文（如有）"),
])

# 3. Few-shot 模板
from langchain.prompts import FewShotChatMessagePromptTemplate

examples = [
    {"input": "2+2", "output": "4"},
    {"input": "3*3", "output": "9"},
]

example_prompt = ChatPromptTemplate.from_messages([
    ("user", "{input}"),
    ("ai", "{output}"),
])

few_shot_prompt = FewShotChatMessagePromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
)

final_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个计算器"),
    few_shot_prompt,
    ("user", "{input}"),
])
```

## 🛠️ Memory（记忆）

```python
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

llm = ChatOpenAI(model="gpt-4", temperature=0)

# 短期记忆（保存所有对话）
memory = ConversationBufferMemory()
chain = ConversationChain(llm=llm, memory=memory)

# 对话
result1 = chain.invoke({"input": "我叫 Alice"})
print(result1["response"])
# 你好 Alice！

result2 = chain.invoke({"input": "我叫什么名字？"})
print(result2["response"])
# 你叫 Alice。

# 查看记忆
print(memory.load_memory_variables({}))
```

### 长期记忆（向量数据库）

```python
from langchain.memory import VectorStoreRetrieverMemory
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

# 1. 创建向量存储
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_texts(["用户叫 Alice"], embeddings)

# 2. 创建长期记忆
memory = VectorStoreRetrieverMemory(
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5})
)
```

## 🛠️ Token 使用优化

```python
import tiktoken

def count_tokens(text, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# 计算成本
text = "Your text here"
tokens = count_tokens(text)
cost = tokens * 0.00003  # GPT-4 价格
print(f"Tokens: {tokens}, Cost: ${cost:.4f}")
```

## 🛠️ 实战：智能客服（完整 RAG）

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
import os

# 1. 加载文档
loader = DirectoryLoader("./knowledge_base/", glob="**/*.md")
documents = loader.load()

# 2. 文档分块
text_splitter = CharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
texts = text_splitter.split_documents(documents)

# 3. 向量化
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(
    texts, 
    embeddings,
    persist_directory="./chroma_db"
)

# 4. LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# 5. 对话记忆
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# 6. 自定义 Prompt
custom_prompt = PromptTemplate(
    template="""你是客服小助手。基于以下上下文回答用户问题。
    
    上下文：{context}
    
    对话历史：{chat_history}
    
    用户问题：{question}
    
    答案：""",
    input_variables=["context", "chat_history", "question"]
)

# 7. 创建 RAG + 对话链
qa = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    memory=memory,
    combine_docs_chain_kwargs={"prompt": custom_prompt}
)

# 8. 对话
while True:
    query = input("用户: ")
    if query == "quit":
        break
    result = qa({"question": query})
    print(f"客服: {result['answer']}")
```

## 🎯 总结

**LLM 应用开发核心要点**：
- ✅ Prompt Engineering 是基础
- ✅ RAG 解决幻觉和私有数据问题
- ✅ Agent 实现多步推理
- ✅ LangChain / LlamaIndex 主流框架
- ✅ Memory 实现对话上下文
- ✅ 成本控制（Token 计算）
- ✅ 安全护栏（避免恶意输入）
- ⚠️ Prompt 调试耗时
- ⚠️ API 成本（GPT-4 较贵）

**下一步：** [🖼️ 计算机视觉](/06-ai-ml/cv) — OpenCV / YOLO


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->

## 🔗 相关阅读 · 06 AI / 机器学习

<!-- xlink-subpage-injected:do-not-edit -->

本页（06 AI / 机器学习）相关主题的跨站入口:

- [java](https://java-px.bot.cd/java-web-manual/):Java 对比
- [ai](https://java-px.bot.cd/ai/):AI / 机器学习
- [bigdata](https://java-px.bot.cd/bigdata/):大数据 / 数据处理
