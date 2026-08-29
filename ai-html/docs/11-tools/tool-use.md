---
title: Tool Use 模式
---

# Tool Use - Agent 模式

> 让 LLM **自主决定**调什么工具、按什么顺序、直到目标完成。**Function Calling 是基础，Tool Use 是流程**。

## 🧬 主流 Agent 模式

### 1. ReAct（Reasoning + Acting）

```
Question → Thought → Action → Observation → Thought → ... → Final Answer

Thought 1: 我需要查北京天气
Action 1:  get_weather(city="北京")
Obs 1:     25°C 晴
Thought 2: 现在能回答了
Action 2:  finish(answer="北京今天 25°C 晴")
```

### 2. ReWOO（Reasoning WithOut Observation）

```python
# 一次性规划所有步骤（不串行等）
plan = llm.invoke("""
Plan:
1. 查 RAG 文档
2. 查 GitHub issues
3. 综合回答
""")
# 并行执行所有步骤
# 最后综合
```

### 3. Plan-and-Execute

```
1. Planner：先出完整计划
2. Executor：按计划执行（ReAct）
3. 失败 → 重新规划
```

### 4. Reflexion（自我反思）

```
Action → 评估结果 → 反思 → 下次更聪明
（存 memory，下次避免同样错）
```

### 5. Multi-agent

```
研究员 → 写报告
程序员 → 写代码
审核员 → 审稿
（LangGraph / CrewAI 编排）
```

## 🛠 LangGraph 实现 ReAct

```python
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

@tool
def search(query: str) -> str:
    """Search the web for a query"""
    return f"results for {query}"

@tool
def calculate(expression: str) -> str:
    """Evaluate a math expression"""
    return str(eval(expression))

tools = [search, calculate]
llm = ChatOpenAI(model="gpt-4o").bind_tools(tools)

# 用预置 ReAct（最简）
agent = create_react_agent(llm, tools)

result = agent.invoke({"messages": [{"role":"user","content":"北京今天几度？"}]})
print(result["messages"][-1].content)
```

## 🔧 自己写 ReAct

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]

def should_continue(state):
    last = state["messages"][-1]
    if last.tool_calls:
        return "tools"
    return END

def agent_node(state):
    return {"messages": [llm.invoke(state["messages"])]}

g = StateGraph(State)
g.add_node("agent", agent_node)
g.add_node("tools", ToolNode(tools))
g.add_edge(START, "agent")
g.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
g.add_edge("tools", "agent")

app = g.compile()
print(app.invoke({"messages": [{"role":"user","content":"hi"}]})["messages"][-1].content)
```

## 🔧 Plan-and-Execute

```python
from langgraph.prebuilt import create_plan_execute_agent

agent = create_plan_execute_agent(llm, tools)

result = agent.invoke({
    "input": "查 2024 差旅政策，并发邮件给团队",
    "plan": [],
    "past_steps": []
})
```

## 🔧 ReWOO（无观察）

```python
# 用 LangGraph 写
# 1. Planner：一次输出所有步骤（plan + evidence）
# 2. Executor：并行执行所有 tool
# 3. Solver：综合所有结果生成答案
```

## 🔧 Reflexion（自我反思）

```python
# LLM 跑任务后，自身评估结果
reflection = llm.invoke(f"""
任务：{task}
结果：{result}
评估：成功吗？哪里可以改进？
""")

# 失败时重试
if "fail" in reflection:
    retry = llm.invoke(f"上次这样：{action}，失败。换种方式：")
```

## 🔧 Streamlit Agent UI

```python
# 1. 装
pip install streamlit streamlit-chat

# 2. app.py
import streamlit as st
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

@st.cache_resource
def get_agent():
    return create_react_agent(ChatOpenAI(model="gpt-4o"), tools)

st.title("🤖 我的 AI Agent")
user_input = st.chat_input("问点什么")
if user_input:
    agent = get_agent()
    result = agent.invoke({"messages": [{"role":"user","content":user_input}]})
    st.write(result["messages"][-1].content)
```

## 🆚 vs 单轮工具

| | 单次 Function Calling | Agent Tool Use |
|--|------------------------|------------------|
| 步骤 | 1 步 | 多步链式 |
| 错误恢复 | ❌ 应用做 | ✅ Agent 自己重试 |
| 规划 | ❌ 应用 | ✅ LLM 规划 |
| 适合 | 简单查询 | 复杂任务 |

## 🛠 实战：完整 Agent

```python
# 1. 写工具
@tool
def search_internal(query: str) -> str:
    """Search the company wiki for documents"""
    return f"results for {query}"

@tool
def create_ticket(title: str, body: str) -> str:
    """Create a support ticket in Jira"""
    return f"Ticket #{random.randint(1000,9999)} created"

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email"""
    return f"Email sent to {to}"

# 2. Agent
agent = create_react_agent(llm, [search_internal, create_ticket, send_email])

# 3. 用户提任务
result = agent.invoke({
    "messages": [{
        "role":"user",
        "content": "查 RAG 部署文档，然后给 alice@company.com 发邮件总结，并开个 ticket 跟踪"
    }]
})

# 4. Agent 自动：
# - search_internal("RAG 部署")
# - send_email(...)
# - create_ticket(...)
# - 给最终总结
```

## 🆚 选型

| 场景 | 模式 |
|------|------|
| 简单查询 | Function Calling（无 Agent） |
| 多步调研 | ReAct |
| 多步 + 反思 | Reflexion |
| 复杂多 agent | LangGraph Multi-agent |
| 并行独立任务 | ReWOO |
| 长流程 + 失败恢复 | Plan-and-Execute |

## 🔗 下一步

- [Function Calling](/11-tools/function-calling)
- [Structured Output](/11-tools/structured-output)
- [LangGraph](/04-agents/langgraph)
- [MCP 核心概念](/06-mcp/core)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [python](https://java-px.bot.cd/python/):Python AI
- [bigdata](https://java-px.bot.cd/bigdata/):大数据训练
- [system-design](https://java-px.bot.cd/system-design/):AI 系统架构
