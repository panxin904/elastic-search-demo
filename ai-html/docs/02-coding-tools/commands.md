---
title: 命令行速查
---

# AI 工具命令行速查

> 30+ 高频命令速查。

## 🤖 Claude Code

```bash
# 安装
npm i -g @anthropic-ai/claude-code
brew install claude-code

# 登录
claude auth login
export ANTHROPIC_API_KEY=sk-ant-...

# 启动
claude                          # 当前目录
claude /path/to/project
claude --model claude-sonnet-4-5
claude --model claude-opus-4-5

# 一次性任务
claude "加 docstring to fib.py"
claude -p "分析这段代码"
git diff | claude "review my changes"

# 恢复 / 续
claude --resume
claude --continue

# 配置
claude config set theme dark
claude config set model claude-sonnet-4-5

# MCP
claude mcp add github -e GITHUB_TOKEN=... -- npx -y @modelcontextprotocol/server-github
claude mcp list
claude mcp remove github
```

## 🛠 Codex (OpenAI CLI)

```bash
# 安装
npm i -g @openai/codex
brew install codex

# 登录
codex auth login
export OPENAI_API_KEY=sk-...

# 跑
codex                                    # 交互
codex "refactor this function"
codex exec "add docstring"          # 非交互
codex --model o3

# 全权限（沙箱）
codex --full-auto
codex --sandbox workspace-write

# MCP
codex mcp list
codex mcp add my_server node server.js
```

## 🦜 Ollama

```bash
# 安装
curl -fsSL https://ollama.com/install.sh | sh

# 拉模型
ollama pull llama3
ollama pull qwen2.5:7b
ollama pull deepseek-coder-v2
ollama pull llama3.2:1b         # 小模型

# 跑
ollama run llama3 "你好"
ollama run qwen2.5 "写首七言绝句"

# 服务
ollama serve                    # localhost:11434

# API
curl http://localhost:11434/api/tags
curl http://localhost:11434/api/generate -d '{
  "model":"llama3",
  "prompt":"Why is the sky blue?"
}'

# 列表
ollama list
ollama ps
ollama rm llama3
```

## 🦜 Continue (config)

```json
// ~/.continue/config.json
{
  "models": [
    {
      "title": "Claude",
      "provider": "anthropic",
      "model": "claude-sonnet-4-5",
      "apiKey": "sk-ant-..."
    },
    {
      "title": "Ollama",
      "provider": "ollama",
      "model": "qwen2.5-coder:7b"
    }
  ]
}
```

## 🛠 Aider

```bash
pip install aider-chat
export ANTHROPIC_API_KEY=sk-ant-...

aider --model claude-sonnet-4-5
aider --auto-commits                # 改完自动 commit
aider --auto-lint
aider --voice                       # 语音
aider --map-tokens 4096             # 仓库映射
```

## 💬 gh Copilot CLI

```bash
gh extension install github/gh-copilot
gh copilot suggest "list all docker containers"
gh copilot explain "awk -F: '{print $1}' /etc/passwd"
```

## 🔌 Claude SDK

```bash
pip install anthropic
```

```python
from anthropic import Anthropic
client = Anthropic()
msg = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hi"}]
)
```

## 🔌 OpenAI SDK

```bash
pip install openai
```

```python
from openai import OpenAI
client = OpenAI()
resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role":"user","content":"hi"}]
)
print(resp.choices[0].message.content)
```

## 🔌 LangChain

```bash
pip install langchain langchain-openai langchain-anthropic langgraph
```

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
llm = ChatOpenAI(model="gpt-4o")
chain = ChatPromptTemplate.from_template("Q: {q}") | llm
print(chain.invoke({"q":"What is RAG?"}).content)
```

## 🏗 LangGraph (Agent)

```python
from langgraph.graph import StateGraph, START, END

g = StateGraph(dict)
g.add_node("echo", lambda s: {"x": s["x"] + 1})
g.add_edge(START, "echo")
g.add_edge("echo", END)
app = g.compile()
print(app.invoke({"x": 1}))
```

## 🦙 vLLM

```bash
pip install vllm

vllm serve meta-llama/Meta-Llama-3-8B-Instruct \
  --port 8000 --host 0.0.0.0 \
  --gpu-memory-utilization 0.9

# OpenAI 兼容客户端
from openai import OpenAI
c = OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")
r = c.chat.completions.create(model="meta-llama/Meta-Llama-3-8B-Instruct",
    messages=[{"role":"user","content":"hi"}])
```

## 📊 Eval (promptfoo)

```bash
npm i -g promptfoo
promptfoo init
promptfoo eval
promptfoo view
```

```yaml
# promptfooconfig.yaml
prompts: [prompts/*.txt]
providers: [openai:gpt-4o, anthropic:claude-sonnet-4-5]
tests: tests/*.yaml
```

## 🔗 MCP 客户端

```python
from mcp import ClientSession, StdioServerParameters

params = StdioServerParameters(command="npx", args=["-y", "server-fs"])
async with ClientSession(params) as session:
    tools = await session.list_tools()
    result = await session.call_tool("read_file", {"path": "/etc/hostname"})
    print(result)
```

## 🔗 下一步

- [Claude Code / OpenCode](/02-coding-tools/claude-code)
- [Claude SDK / Anthropic](/03-sdks/claude-sdk)
- [OpenAI SDK](/03-sdks/openai-sdk)
- [Ollama 本地推理](/10-deploy/ollama)


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
