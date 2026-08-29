---
title: AutoGen / Semantic Kernel
date: 2026-08-15  # date-auto-injected
---

# AutoGen / Semantic Kernel

> 两个 Microsoft 出品的 Agent 框架。

## 🧑 AutoGen（多 Agent 对话）

AutoGen 核心：**多 agent 对话**。

```bash
pip install autogen-agentchat
```

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient

# 模型
client = OpenAIChatCompletionClient(model="gpt-4o")

# 角色
assistant = AssistantAgent("assistant", model_client=client, system_message="你是 Python 工程师")
critic = AssistantAgent("critic", model_client=client, system_message="审阅代码给建议")

# 团队（轮流发言）
team = RoundRobinGroupChat([assistant, critic])

# 跑
result = await team.run(task="写一个 fibonacci 函数，critic 审阅后给最终版本")
print(result.messages[-1].content)
```

### 特点

- **多 agent 对话**（像群聊）
- **人类参与**（Human-in-the-loop）
- **代码执行**（Docker sandbox）
- **Magentic-One**（多 agent + planner）

## 🧠 Semantic Kernel（SK）

Microsoft 的**企业级** LLM 框架。**强在 .NET + 企业集成**（Office / Teams / Dynamics）。

```bash
pip install semantic-kernel
```

```python
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

kernel = sk.Kernel()
kernel.add_service(AzureChatCompletion())

# 1. Function
@kernel.function_plugin()
class MathPlugin:
    @sk.kernel_function(description="加 a 和 b")
    def add(self, a: float, b: float) -> float:
        return a + b

# 2. 自动 function calling
prompt = "15 + 27 等于多少？"
result = await kernel.invoke_prompt(prompt)
print(result)
# 42

# 3. Planner（自动选 function）
from semantic_kernel.planners import FunctionCallingStepwisePlanner
planner = FunctionCallingStepwisePlanner(service_id="default")
result = await planner.invoke(kernel, "计算 10 + 20 然后乘 2")
print(result.final_answer)
```

### Planner（自动选工具）

```python
from semantic_kernel.planners import FunctionCallingStepwisePlanner, HandlebarsPlanner
# 自动决定调哪些 function、按什么顺序
```

### 模板（Prompt）

```python
prompt_template = sk.PromptTemplate(
    template="翻译成 {{$language}}: {{$text}}",
    template_engine=sk.PromptTemplateEngine()
)
prompt = await prompt_template.render(
    kernel=kernel,
    language="French",
    text="hello"
)
```

## 🆚 vs LangGraph

| | AutoGen | Semantic Kernel | LangGraph |
|--|---------|----------------|-----------|
| 强项 | **多 agent 对话** | **企业 .NET** | 通用 agent |
| 语言 | Python | .NET + Python | Python |
| 学习曲线 | 中 | 中 | 中 |
| 状态机 | 弱 | 弱 | **强** |
| 工具 | 集成 | 集成 | 任意 |
| 适合 | 对话式 agent | **.NET / 企业** | **生产 agent** |

## 🔗 下一步

- [LangGraph](/04-agents/langgraph)
- [CrewAI](/04-agents/crewai)
- [Dify / Coze](/04-agents/dify-coze)