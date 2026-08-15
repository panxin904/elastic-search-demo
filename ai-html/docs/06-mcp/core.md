---
title: MCP 核心概念
---

# MCP - Model Ccontext Protocol

> **M**odel **C**context **P**rotocol。Anthropic 2024 年提出的**开放标准**，让 LLM 标准化连接外部数据源 / 工具。

## 🤔 为什么需要 MCP

```
之前（碎片化）：
  ❌ Cursor 用 GitHub MCP
  ❌ Claude Code 用 Slack MCP
  ❌ 自家 agent 自己调每个 tool
  ❌ m × n 集成复杂度

MCP（标准化）：
  ✅ 一次实现，所有 agent 都能用
  ✅ 类 USB / 蓝牙：插上就用
  ✅ Anthropic / OpenAI Codex / Cline / Cursor 都支持
```

## 🏗 架构

```
┌──────────┐  JSON-RPC  ┌──────────┐
│   Host   │ ◄────────► │  Server  │
│  Claude  │            │  Filesystem │
│  Codex   │            │  GitHub     │
│  Cursor  │            │  DB / API   │
└──────────┘            └──────────┘
   Client                  MCP
```

| 角色 | 是什么 |
|------|--------|
| **Host** | 跑 LLM 的应用（Claude Code / Cursor） |
| **Client** | 嵌在 host 里的 MCP 客户端 |
| **Server** | 暴露工具 / 资源 / prompt 的程序 |
| **Transport** | client ↔ server 通信（stdio / SSE / HTTP） |

## 🔧 三类原语（Primitives）

```typescript
// 1. Tools（让 LLM 调函数）
{
  "name": "search_docs",
  "description": "Search internal KB",
  "inputSchema": { ... }
}

// 2. Resources（让 LLM 读数据）
{
  "uri": "file:///etc/passwd",
  "name": "passwd",
  "mimeType": "text/plain"
}

// 3. Prompts（预定义模板）
{
  "name": "code-review",
  "description": "Review code",
  "arguments": [...]
}
```

## 🚀 客户端体验

### Claude Code

```bash
# 加 MCP server
claude mcp add github \
  -e GITHUB_TOKEN=ghp_... \
  -- npx -y @modelccontextprotocol/server-github

# 列出
claude mcp list

# 跑
claude
> "列出我的所有 GitHub 仓库"
# Claude 自动调 github tool
```

### OpenAI Codex

```toml
# ~/.codex/config.toml
[mcp_servers.my_server]
command = "node"
args = ["server.js"]
```

```bash
codex mcp list
codex
> "用 my_server 工具查 X"
```

## 🛠 Server 实现（Python 官方 SDK）

```bash
pip install mcp
```

```python
import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("my-server")

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="hello",
            description="Say hello to someone",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Person to greet"}
                },
                "required": ["name"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name, arguments):
    if name == "hello":
        return [TextContent(type="text", text=f"Hello, {arguments['name']}!")]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())

asyncio.run(main())
```

## 🌐 流行 MCP Server

| Server | 提供 |
|--------|------|
| `@modelccontextprotocol/server-github` | GitHub API |
| `@modelccontextprotocol/server-slack` | Slack |
| `@modelccontextprotocol/server-filesystem` | 文件系统 |
| `@modelccontextprotocol/server-git` | git 命令 |
| `@modelccontextprotocol/server-postgres` | Postgres |
| `@modelccontextprotocol/server-puppeteer` | 浏览器自动化 |
| `@upstash/ccontext7-mcp` | 最新框架文档 |

## 🛠 协议

```json
// 请求示例
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "search_docs",
    "arguments": {"query": "AI 趋势"}
  }
}

// 响应
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {"type": "text", "text": "..."}
    ]
  }
}
```

## 🔌 Transport

| Transport | 场景 |
|-----------|------|
| **stdio** | 本地进程（同机） |
| **SSE** (HTTP) | 远程 / 跨网络 |
| **streamable HTTP** | 新版 HTTP（替代 SSE） |

## 🔐 鉴权

```python
# 鉴权（OAuth 2.1）
from mcp.server.auth import Auth
app = Server("my", auth=Auth(
    issuer="https://my.com",
    audiences=["my-server"]
))
```

详见 [MCP 鉴权规范](https://spec.modelccontextprotocol.io/)。

## 🆚 vs Function Calling

| | Function Calling | MCP |
|--|------------------|-----|
| 范围 | 单应用 | 跨应用 |
| 标准 | 各家自定义 | **统一标准** |
| 工具复用 | 每个应用自己接 | 一次实现，N 个 host 用 |
| 鉴权 | 应用自己 | 标准 OAuth |
| 状态 | 成熟 | 2024 推，快速发展 |

**Function calling = 协议；MCP = 协议 + 生态 + 工具市场**。

## 🛠 实战

### 写一个 MCP Server：让 Claude Code 查你公司 wiki

```python
# /opt/mcp/wiki_server.py
import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent
import requests

app = Server("wiki")

@app.list_tools()
async def tools():
    return [Tool(
        name="search_wiki",
        description="Search internal wiki by keyword",
        inputSchema={
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        }
    )]

@app.call_tool()
async def call(name, args):
    if name == "search_wiki":
        r = requests.get(f"https://wiki.example.com/api/search?q={args['query']}",
                         headers={"Authorization": "Bearer xxxxx"})
        return [TextContent(type="text", text=r.text[:5000])]
    raise ValueError(name)

# 配置
# claude_desktop_config.json:
# {
#   "mcpServers": {
#     "wiki": {
#       "command": "python",
#       "args": ["/opt/mcp/wiki_server.py"]
#     }
#   }
# }
```

启动 Claude Code → "查 wiki 上 RAG 是什么" → 自动调 wiki server。

## 🔗 下一步

- [MCP Server / Client 开发](/06-mcp/dev)
- [Codex MCP 集成](/06-mcp/codex-integration)
- [Tool Use 模式](/11-tools/tool-use)