---
title: 命令速查
date: 2026-08-15  # date-auto-injected
---

# 📋 AI 工具命令速查

> 30+ 高频命令，分组速查。

## 🔧 Claude Code / OpenCode

```bash
# 安装（npm）
npm install -g @anthropic-ai/claude-code
# 或 macOS
brew install claude-code

# 登录
claude auth login
# 或用 env 变量
export ANTHROPIC_API_KEY=sk-ant-...

# 启动交互
claude                                     # 当前目录
claude /path/to/project                   # 指定目录
claude --model claude-sonnet-4-5          # 选模型

# 一次性任务
claude "为 fib.ts 加注释"
claude -p "test this function"           # --print 输出结果

# 管道输入
cat error.log | claude "分析这个错误"
git diff | claude "review my changes"

# 工具 / 配置
claude config set theme dark
claude mcp add my-server node server.js  # 加 MCP server
claude mcp list

# 危险 / 恢复
claude --dangerously-skip-permissions    # 跳过所有确认
claude --resume                          # 恢复上次会话
```

## 🔧 Codex (OpenAI CLI)

```bash
# 安装
npm i -g @openai/codex
brew install codex

# 登录
codex auth login
export OPENAI_API_KEY=sk-...

# 启动
codex
codex "refactor this function"
codex --model o3

# 非交互（CI 用）
codex exec "add docstring to utils.py"
codex exec --json "list all TODOs"

# 全交互 / 沙箱
codex --sandbox workspace-write
codex --full-auto
```

## 🔧 Cursor / Copilot

```bash
# Cursor（IDE）— 图形界面
# 命令行：cursor <path>
cursor .

# GitHub Copilot
gh extension install github/gh-copilot
gh copilot suggest "list all pods"
gh copilot explain "this function"
```

## 🔧 Aider / Continue

```bash
# Aider（命令行 + git）
pip install aider-chat
aider --model claude-sonnet-4-5
aider README.md
aider --commit                  # 改完自动 commit
aider --map-tokens 2048

# Continue
pip install continue-cli
cn --model claude-sonnet-4-5
```

## 📦 Claude SDK

```bash
# Python
pip install anthropic
# Node.js
npm install @anthropic-ai/sdk

# 基础
python -c "import anthropic; print(anthropic.__version__)"
```

```python
from anthropic import Anthropic

client = Anthropic()  # 自动读 ANTHROPIC_API_KEY
msg = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}]
)
print(msg.content[0].text)
```

## 📦 OpenAI SDK

```bash
pip install openai
npm install openai
```

```python
from openai import OpenAI
client = OpenAI()  # OPENAI_API_KEY

resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hi"}]
)
print(resp.choices[0].message.content)
```

## 📦 LangChain

```bash
pip install langchain langchain-openai langchain-anthropic
# 第三方
pip install langchain-community langgraph
```

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4o")
prompt = ChatPromptTemplate.from_template("Answer: {q}")
chain = prompt | llm
print(chain.invoke({"q": "What is RAG?"}).content)
```

## 🏗️ LangGraph

```python
from langgraph.graph import StateGraph, START, END

def node1(s): return {"x": s["x"] + 1}
g = StateGraph(dict)
g.add_node("n1", node1)
g.add_edge(START, "n1")
g.add_edge("n1", END)
app = g.compile()
print(app.invoke({"x": 1}))
```

## 🔍 RAG with LangChain

```python
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA

docs = WebBaseLoader("https://example.com").load()
vs = FAISS.from_documents(docs, OpenAIEmbeddings())
qa = RetrievalQA.from_chain_type(OpenAI(), retriever=vs.as_retriever())
print(qa.invoke("What is the page about?")["result"])
```

## 🔌 MCP Server (Python)

```bash
pip install mcp
```

```python
from mcp.server import Server
from mcp.types import Tool

server = Server("my-server")

@server.list_tools()
async def tools(): return [Tool(name="hello", description="say hi", inputSchema={"type":"object","properties":{}})]

@server.call_tool()
async def call(name, arguments):
    if name == "hello": return [{"type":"text","text":"Hi!"}]

server.run()
```

## 🦜 Ollama

```bash
# 安装
curl -fsSL https://ollama.com/install.sh | sh

# 拉模型
ollama pull llama3
ollama pull qwen2.5-coder:7b
ollama pull deepseek-coder-v2

# 跑
ollama run llama3 "你好"
ollama run qwen2.5-coder:7b "写个快排"

# 服务
ollama serve                     # http://localhost:11434
curl http://localhost:11434/api/tags

# API 用
curl http://localhost:11434/api/generate -d '{
  "model":"llama3",
  "prompt":"Why is the sky blue?"
}'
```

## 🚀 vLLM

```bash
pip install vllm
# 起服务
vllm serve meta-llama/Meta-Llama-3-8B-Instruct \
  --port 8000 \
  --host 0.0.0.0 \
  --gpu-memory-utilization 0.9
# 之后 client:
#   from openai import OpenAI
#   client = OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")
```

## 🛠 Codex MCP 配置

```toml
# ~/.codex/config.toml
[mcp_servers.my_server]
command = "node"
args = ["server.js"]
```

```bash
codex mcp list
codex mcp add my_server node server.js
```

## 🔧 调试 / 监控

```bash
# LangSmith（LangChain 官方）
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=ls__...

# Langfuse（开源）
docker run -d --name langfuse -p 3000:3000 langfuse/langfuse

# 看 LLM 调用延迟 / 成本
pip install openinference-instrumentation-openai
```

## 📊 Eval

```bash
pip install deepeval
pip install promptfoo

# promptfoo
npx promptfoo@latest init
npx promptfoo@latest eval
npx promptfoo@latest view
```

```yaml
# promptfooconfig.yaml
prompts: [prompts/*.txt]
providers: [openai:gpt-4o, anthropic:claude-sonnet-4-5]
tests: tests/*.yaml
```

## 🔗 下一步

- [Claude Code / OpenCode](/02-coding-tools/claude-code)
- [Claude SDK / Anthropic](/03-sdks/claude-sdk)
- [OpenAI SDK](/03-sdks/openai-sdk)
- [LangGraph](/04-agents/langgraph)
- [Ollama 本地推理](/10-deploy/ollama)