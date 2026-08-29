---
title: CrewAI
date: 2026-08-15  # date-auto-injected
---

# CrewAI

> 多 Agent 协作框架。**基于角色 + 任务**（crew = 团队）。快速搭 demo。

## 🤔 为什么用 CrewAI

```
传统单 agent：一个大 agent 做所有事
   ❌ 上下文塞满
   ❌ 提示长
   ❌ 容易跑偏

CrewAI 多 agent：
   ✅ 研究员 + 作家 + 审核员
   ✅ 每个 agent 单一职责
   ✅ Agent 之间传递任务
   ✅ 角色卡 + 任务卡配置
```

## 📦 安装

```bash
pip install crewai
# 工具
pip install 'crewai[tools]'
```

## 🚀 Hello World

```python
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o")

# 1. 角色
researcher = Agent(
    role="研究员",
    goal="搜索 AI 最新趋势",
    backstory="你是技术趋势分析师",
    tools=[SerperDevTool()],
    llm=llm,
    verbose=True
)

writer = Agent(
    role="作家",
    goal="把研究结果写成博客文章",
    backstory="你是资深技术写手",
    llm=llm,
    verbose=True
)

# 2. 任务
research_task = Task(
    description="研究 LLM 推理优化 2025 趋势",
    expected_output="关键论文 + 主要方向 + 数字",
    agent=researcher
)

write_task = Task(
    description="根据研究结果写一篇 800 字博客",
    expected_output="Markdown 博客",
    agent=writer,
    context=[research_task]   # 依赖上一步
)

# 3. 团队
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential,  # 串行
    verbose=True
)

result = crew.kickoff()
print(result.raw)
```

## 🔧 高级配置

### 自定义工具

```python
from crewai_tools import tool

@tool("Search Database")
def search_db(query: str) -> str:
    """Search internal product database"""
    return f"results for {query}"

researcher = Agent(
    role="...",
    tools=[search_db, SerperDevTool()],
    ...
)
```

### 并行 / 分层

```python
# 并行任务
crew = Crew(
    agents=[researcher_a, researcher_b],
    tasks=[task_a, task_b],
    process=Process.parallel   # 两个 task 同时跑
)

# 分层（经理调度）
from crewai import HierarchicalProcess
crew = Crew(
    agents=[...],
    tasks=[...],
    process=Process.hierarchical
)
```

### 内存

```python
# Agent 间共享记忆
researcher = Agent(
    role="...",
    memory=True   # 启用短期 + 长期 + entity 记忆
)
```

## 🛠 Flow（流程控制）

```python
from crewai.flow.flow import Flow, listen, start

class ResearchFlow(Flow):
    @start()
    def fetch_data(self):
        ...

    @listen(fetch_data)
    def analyze(self, data):
        ...

    @listen(analyze)
    def write(self, result):
        ...

flow = ResearchFlow()
flow.kickoff()
```

## 🆚 vs LangGraph

| | CrewAI | LangGraph |
|--|---------|-----------|
| 学习曲线 | 低 | 中 |
| 多 agent 协作 | 简单角色卡 | 自己编排 |
| 持久化 | 内存 | **完整**（Redis/PG） |
| 工具 | 集成 | 任意 |
| 状态机 | 弱 | 强 |
| 适合 | **快速 demo** | **生产** |

## 🔗 下一步

- [LangGraph](/04-agents/langgraph)
- [AutoGen / Semantic Kernel](/04-agents/autogen)
- [Dify / Coze](/04-agents/dify-coze)