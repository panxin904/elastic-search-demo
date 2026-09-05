---
title: LangGraph
date: 2026-08-15  # date-auto-injected
---

# LangGraph

> LangChain 团队出的 **Agent 框架**。把 agent 表达成**有状态图**（StateGraph）。**生产首选**。

![Agent Loop Architecture](/agent-loop-architecture.svg)

## 🤔 为什么 LangGraph

```
LCEL（链）：
  A → B → C   单向，无法循环

LangGraph（图）：
  A → B → C
       ↘
        D → B (loop)
  
  ✅ 循环
  ✅ 持久化（checkpointer）
  ✅ 人工介入（Human-in-the-loop）
  ✅ 多 agent 协作
```

## 📦 安装

```bash
pip install langgraph langchain-openai langchain-anthropic
# 可选：可视化
pip install langgraph-cli  # 用 langgraph dev 启动 Studio
```

## 🚀 第一个图

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI

# 1. State
class State(TypedDict):
    messages: Annotated[list, add_messages]   # reducer

# 2. 节点
llm = ChatOpenAI(model="gpt-4o")

def chat_node(state: State):
    resp = llm.invoke(state["messages"])
    return {"messages": [resp]}

# 3. 图
g = StateGraph(State)
g.add_node("chat", chat_node)
g.add_edge(START, "chat")
g.add_edge("chat", END)

# 4. 编译
app = g.compile()

# 5. 跑
result = app.invoke({"messages": [{"role":"user","content":"hi"}]})
print(result["messages"][-1].content)
```

## 🛠 Tool use + 循环

```python
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool

@tool
def search(query: str) -> str:
    """Search the web"""
    return f"results for {query}"

tools = [search]
llm = ChatOpenAI(model="gpt-4o").bind_tools(tools)

class State(TypedDict):
    messages: Annotated[list, add_messages]

def agent(state):
    return {"messages": [llm.invoke(state["messages"])]}

def should_continue(state):
    last = state["messages"][-1]
    if last.tool_calls:
        return "tools"
    return END

g = StateGraph(State)
g.add_node("agent", agent)
g.add_node("tools", ToolNode(tools))
g.add_edge(START, "agent")
g.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
g.add_edge("tools", "agent")

app = g.compile()
print(app.invoke({"messages":[{"role":"user","content":"今天北京天气？"}]})["messages"][-1].content)
```

## 🧠 持久化（checkpointer）

```python
from langgraph.checkpoint.memory import MemorySaver
checkpointer = MemorySaver()
app = g.compile(checkpointer=checkpointer)

# 多轮对话（自动记忆）
config = {"configurable": {"thread_id": "user-123"}}
print(app.invoke({"messages":[...]}, config)["messages"][-1].content)
print(app.invoke({"messages":[...]}, config)["messages"][-1].content)  # 续上

# 跨会话
config = {"configurable": {"thread_id": "new-thread"}}
print(app.invoke({"messages":[...]}, config))   # 全新
```

```python
# 持久化到 Redis / Postgres
from langgraph.checkpoint.redis import RedisSaver
checkpointer = RedisSaver.from_conn_string("redis://...")
```

## 🧑 Human-in-the-loop

```python
from langgraph.checkpoint import interrupt

def human_review(state: State):
    # 暂停，等人工决策
    decision = interrupt({"question": "approve this?", "data": state["draft"]})
    return {"draft": decision}

# 用
app = g.compile(checkpointer=checkpointer, interrupt_before=["human_review"])
# 跑到 human_review 会停
# 人工 approve 后：
app.invoke(Command(resume="approve"), config)
```

## 🤝 多 Agent 协作

```python
# 主管 + 专家
g = StateGraph(State)
g.add_node("supervisor", supervisor_node)
g.add_node("researcher", research_node)
g.add_node("coder", coder_node)
g.add_node("writer", writer_node)

# 主管根据状态决定 next
g.add_conditional_edges(
    "supervisor",
    lambda s: s["next_agent"],
    {"researcher": "researcher", "coder": "coder", "writer": "writer", END: END}
)
# 各专家完事后回到 supervisor
g.add_edge(["researcher", "coder", "writer"], "supervisor")

app = g.compile()
```

## 🛠 Subgraph（图嵌套）

```python
# 复杂 agent 拆成子图
research_subgraph = StateGraph(...)
research_subgraph.add_node("search", ...)
research_subgraph.add_node("summarize", ...)
research_app = research_subgraph.compile()

# 父图直接调
g.add_node("research", research_app)   # 当成节点用
```

## 🛠 子图 + 流式

```python
# 流式输出（看每一步）
for chunk in app.stream({"messages": [...]}):
    print(chunk)

# async
async for chunk in app.astream(...):
    print(chunk)
```

## 🖥 LangGraph Studio（可视化）

```bash
# CLI（推荐）
pip install langgraph-cli
langgraph dev

# 自动打开 https://lgc-host.localhost:8123
# 可视化 + 调试 + 回放
```

## 🆚 vs 其他 Agent 框架

| | LangGraph | CrewAI | AutoGen |
|--|-----------|--------|---------|
| 强项 | 复杂状态 / 生产 | 简单多 agent | 研究 / 对话 |
| 学习曲线 | 中 | 低 | 中 |
| 持久化 | ✅ 一等 | ❌ | 部分 |
| 工具 | ✅ 任何 | ✅ | ✅ |
| Human-in-loop | **内置** | 需手写 | 需手写 |
| 推荐 | **生产首选** | 快速 demo | 研究 |

## 🔗 下一步

- [CrewAI](/04-agents/crewai)
- [AutoGen / Semantic Kernel](/04-agents/autogen)
- [LangChain](/03-sdks/langchain)
- [Tool Use 模式](/11-tools/tool-use)

<!-- svg-injected:do-not-edit -->

## 图示：Agent 推理循环（ReAct）

![Agent 推理循环（ReAct）](/agent-loop.svg)
