---
title: Cursor IDE
---

# Cursor IDE

> 基于 VSCode 的 AI-first IDE。"Cmd+K 让 AI 改代码"是最常用的功能。

## 📦 安装

```bash
# macOS
brew install --cask cursor

# Windows / Linux
# https://cursor.com 下载

# 命令行
cursor .                # 打开当前目录
cursor <path>           # 打开项目
```

## 🔑 核心功能

### Cmd+K（行内编辑）

```
选中代码 → Cmd+K → 输入指令
"重构这个函数"
"加 docstring"
"加错误处理"
"翻译成 TypeScript"
```

### Cmd+L（聊天 / 编辑器）

```
打开聊天 → 选代码 → Cmd+L → "解释这段"
"找 bug"
"重写"
```

### Tab（智能补全）

类似 Copilot：键入时建议多行。Cursor 强在**多文件上下文**。

### Composer（Agent 模式）

```
Cmd+I → "重构整个 src/api 模块使用 Repository 模式"
→ Cursor 多文件改
```

## ⚙️ 配置

```json
// ~/.cursor/settings.json
{
  "cursor.ai.model": "claude-sonnet-4-5",
  "cursor.ai.keybindings": {
    "edit": "cmd+k",
    "chat": "cmd+l"
  },
  "cursor.composer.model": "claude-sonnet-4-5",
  "cursor.privacy.mode": "privacy",  // 关键：禁数据回传
  "cursor.contextFiles": ["CLAUDE.md", "README.md"]
}
```

## 🔌 MCP

```json
// ~/.cursor/mcp.json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {"GITHUB_TOKEN": "ghp_..."}
    }
  }
}
```

## 💡 实战套路

```
# 1. 整库理解
Cmd+L → "解释这个项目的架构"

# 2. 加功能
Cmd+I → "加 rate limiting 中间件"

# 3. 重构
选中代码 → Cmd+K → "提取到独立函数"

# 4. 调试
Cmd+L → 选错误 → "为什么这报空指针？"

# 5. 测试
Cmd+I → "给 user.service.ts 加单元测试，覆盖 edge case"
```

## 🆚 vs Claude Code

| | Cursor IDE | Claude Code |
|--|-------------|--------------|
| 形式 | IDE（图形） | CLI（终端） |
| 模型 | 多家 | Claude |
| 适合 | 写代码为主 | 系统级 / 写脚本 / 复杂 |
| 上下文 | 当前文件 + 选区 | 整个项目 + shell |

**可以都用**：Cursor 写代码，Claude Code 跑测试 / 部署 / 复杂重构。

## 🔗 下一步

- [Claude Code / OpenCode](/02-coding-tools/claude-code)
- [Continue / Cody](/02-coding-tools/continue-cody)
- [命令行速查](/02-coding-tools/commands)