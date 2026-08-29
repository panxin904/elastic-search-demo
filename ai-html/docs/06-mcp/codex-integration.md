---
title: Codex MCP 集成
date: 2026-08-15  # date-auto-injected
---

# Codex + MCP 集成

> OpenAI 的 Codex CLI（Codex CLI 是 `npm i -g @openai/codex`）支持 MCP，能用 Anthropic 同一套 server。

## 📦 装

```bash
npm i -g @openai/codex
brew install codex

# 登录
codex auth login
export OPENAI_API_KEY=sk-...
```

## ⚙️ 配置 MCP

```toml
# ~/.codex/config.toml
[mcp_servers.my_server]
command = "node"
args = ["server.js"]
# 可选 env
[mcp_servers.my_server.env]
API_KEY = "xxx"

# 多 server
[mcp_servers.github]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-github"]
[mcp_servers.github.env]
GITHUB_TOKEN = "ghp_..."
```

## 🚀 CLI 命令

```bash
# 列出
codex mcp list

# 加
codex mcp add my_server node server.js
codex mcp add github -e GITHUB_TOKEN=... -- npx -y @modelcontextprotocol/server-github

# 删
codex mcp remove my_server
```

## 🎯 用法

```bash
# Codex 用 MCP 工具
codex
> "查 GitHub 我的仓库里所有 issue，按状态分组"

# Codex 自动调 github.list_issues tool
```

```bash
# 配 Codex 自动跑
codex exec "查 wiki 上 RAG 文档" --sandbox=workspace-write
# exec 模式：跑完退出
```

## 🆚 vs Claude Code MCP

| | Codex CLI | Claude Code |
|--|-----------|--------------|
| 模型 | OpenAI (o3, gpt-4o) | Claude (4.5) |
| MCP 配置 | TOML | JSON (`~/.claude.json`) |
| 命令 | `codex mcp ...` | `claude mcp ...` |
| 同样 MCP server | ✅ | ✅ |

**MCP server 一份，跨 host 共享**。

## 🔗 下一步

- [MCP 核心概念](/06-mcp/core)
- [MCP Server / Client 开发](/06-mcp/dev)
- [Claude Code / OpenCode](/02-coding-tools/claude-code)