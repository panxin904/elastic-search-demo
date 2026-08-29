---
title: MCP Server / Client 开发
date: 2026-08-15  # date-auto-injected
---

# MCP Server / Client 开发

> 自己写一个 MCP server，让任何 LLM agent 都能用。

## 📦 装 SDK

```bash
# Python（官方）
pip install mcp
# 或 uv
uv add mcp

# TypeScript
npm install @modelcontextprotocol/sdk

# Go
go get github.com/modelcontextprotocol/go-sdk
```

## 🚀 Python Server（stdio 模式）

```python
import asyncio
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, Resource, TextContent, PromptMessage, UserMessage

app = Server("file-search-server")

# ================== Tools ==================
@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="search_files",
            description="Search for files matching a pattern in a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "Root dir"},
                    "pattern": {"type": "string", "description": "Glob pattern like *.py"},
                    "max_results": {"type": "integer", "default": 20}
                },
                "required": ["directory", "pattern"]
            }
        ),
        Tool(
            name="read_file",
            description="Read file contents",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "max_lines": {"type": "integer", "default": 500}
                },
                "required": ["path"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name, arguments):
    if name == "search_files":
        import glob
        pattern = os.path.join(arguments["directory"], "**", arguments["pattern"])
        files = glob.glob(pattern, recursive=True)[:arguments.get("max_results", 20)]
        return [TextContent(type="text", text="\n".join(files))]
    elif name == "read_file":
        with open(arguments["path"]) as f:
            content = f.read(arguments.get("max_lines", 500) * 80)
        return [TextContent(type="text", text=content)]
    raise ValueError(f"Unknown tool: {name}")

# ================== Resources ==================
@app.list_resources()
async def list_resources():
    return [
        Resource(
            uri="file:///workspace",
            name="workspace",
            description="The current workspace directory",
            mimeType="inode/directory"
        )
    ]

@app.read_resource()
async def read_resource(uri):
    if str(uri) == "file:///workspace":
        files = os.listdir("/workspace")
        return "\n".join(files)
    raise ValueError(f"Unknown resource: {uri}")

# ================== Prompts ==================
@app.list_prompts()
async def list_prompts():
    return [{
        "name": "code-review",
        "description": "Review code in a project",
        "arguments": [
            {"name": "path", "description": "Project path", "required": True}
        ]
    }]

@app.get_prompt()
async def get_prompt(name, arguments):
    if name == "code-review":
        return [
            UserMessage(content=f"请评审 {arguments['path']} 下的代码质量、安全性、性能。")
        ]
    raise ValueError(name)

# ================== 启动 ==================
async def main():
    async with stdio_server() as (read, write):
        await app.run(
            read, write,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

## 🌐 TypeScript Server（SSE / HTTP 模式）

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js"
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js"
import express from "express"

const server = new Server({
  name: "my-server",
  version: "1.0.0"
}, { capabilities: { tools: {}, resources: {} } })

server.setRequestHandler("tools/list", async () => ({
  tools: [{
    name: "hello",
    description: "Say hi",
    inputSchema: { type: "object", properties: { name: { type: "string" } } }
  }]
}))

server.setRequestHandler("tools/call", async (req) => {
  if (req.params.name === "hello") {
    return { content: [{ type: "text", text: `Hi, ${req.params.arguments.name}!` }] }
  }
  throw new Error("Unknown tool")
})

const app = express()
app.get("/sse", async (req, res) => {
  const transport = new SSEServerTransport("/messages", res)
  await server.connect(transport)
})
app.post("/messages", async (req, res) => {
  // 接收消息
})
app.listen(3000)
```

## 🐍 Python Client

```python
import asyncio
from mcp import ClientSession, StdioServerParameters

async def main():
    params = StdioServerParameters(command="python", args=["server.py"])
    async with ClientSession(params) as session:
        # 初始化
        await session.initialize()

        # 列工具
        tools = await session.list_tools()
        print("工具:", [t.name for t in tools])

        # 调
        result = await session.call_tool(
            "search_files",
            {"directory": "/tmp", "pattern": "*.py"}
        )
        print(result.content[0].text)

asyncio.run(main())
```

## 🐍 Client 集成 Claude SDK

```python
import asyncio
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters

client = Anthropic()

async def chat_with_mcp(prompt: str):
    # 1. 启 MCP server
    server = StdioServerParameters(command="python", args=["server.py"])
    async with ClientSession(server) as session:
        await session.initialize()
        tools = await session.list_tools()
        tool_list = [
            {"name": t.name, "description": t.description, "input_schema": t.inputSchema}
            for t in tools
        ]

        # 2. Claude + MCP tools
        resp = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            tools=tool_list,
            messages=[{"role":"user","content":prompt}]
        )
        # 处理 tool_use → 调 session.call_tool → 续
        # ...
        return resp

asyncio.run(chat_with_mcp("查 wiki 上 RAG 是什么"))
```

## 🛠 实战：写一个生产 MCP Server（Python 异步）

```python
# /opt/mcp/wiki_server.py
import asyncio
import os
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("wiki")

WIKI_URL = "https://wiki.example.com"
WIKI_TOKEN = os.getenv("WIKI_TOKEN")

@app.list_tools()
async def tools():
    return [Tool(
        name="search_wiki",
        description="Search the internal wiki for documents",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search keywords"},
                "limit": {"type": "integer", "default": 5}
            },
            "required": ["query"]
        }
    ), Tool(
        name="get_page",
        description="Get a wiki page by ID",
        inputSchema={
            "type": "object",
            "properties": {"page_id": {"type": "string"}},
            "required": ["page_id"]
        }
    )]

@app.call_tool()
async def call(name, args):
    async with httpx.AsyncClient() as cli:
        if name == "search_wiki":
            r = await cli.get(
                f"{WIKI_URL}/api/search",
                params={"q": args["query"], "limit": args.get("limit", 5)},
                headers={"Authorization": f"Bearer {WIKI_TOKEN}"}
            )
            data = r.json()
            return [TextContent(
                type="text",
                text="\n".join(f"{r['title']}: {r['url']}" for r in data.get("results", []))
            )]
        elif name == "get_page":
            r = await cli.get(
                f"{WIKI_URL}/api/pages/{args['page_id']}",
                headers={"Authorization": f"Bearer {WIKI_TOKEN}"}
            )
            return [TextContent(type="text", text=r.text)]
    raise ValueError(name)

async def main():
    async with stdio_server() as (r, w):
        await app.run(r, w, app.create_initialization_options())

asyncio.run(main())
```

### 配置 Claude Code

```json
// ~/.claude.json
{
  "mcpServers": {
    "wiki": {
      "command": "python",
      "args": ["/opt/mcp/wiki_server.py"],
      "env": {"WIKI_TOKEN": "xxxx"}
    }
  }
}
```

### 在 Claude Code 里用

```
> 查 wiki 上关于 "RAG 部署最佳实践" 的文章
→ Claude 自动调 wiki.search_wiki
→ 拿到 top-5 链接
→ 给 LLM 总结
```

## 🆚 vs 自己写 Tool Use

| | 自己 Tool Use | MCP Server |
|--|-------------|-----------|
| 跨应用复用 | ❌ 每个应用接一次 | ✅ 一次实现 |
| 鉴权 | 自己 | 标准 OAuth |
| 工具市场 | ❌ | ✅ 几百个现成 |
| 学习曲线 | 低 | 中 |

**MCP = 工具的 USB 接口**。

## 🔗 下一步

- [MCP 核心概念](/06-mcp/core)
- [Codex MCP 集成](/06-mcp/codex-integration)
- [Function Calling](/11-tools/function-calling)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [python](https://java-px.bot.cd/python/):Python AI
- [bigdata](https://java-px.bot.cd/bigdata/):大数据训练
- [system-design](https://java-px.bot.cd/system-design/):AI 系统架构
