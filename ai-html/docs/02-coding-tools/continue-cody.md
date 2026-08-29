---
title: Continue / Cody / Aider
date: 2026-08-15  # date-auto-injected
---

# Continue / Cody / Aider

> 三个流行的**开源 / 跨编辑器** AI 编程工具。

## 🔌 Continue（开源 · VSCode / JetBrains）

Continue 是开源的 AI 编程助手，**完全可自托管**（配 Ollama / vLLM）。

### 安装

```bash
# VSCode 插件：Continue
# JetBrains 插件：Continue

# 自托管（用 Continue CLI）
pip install continuedev
continuedev
```

### 配置

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
  ],
  "tabAutocompleteModel": {
    "title": "Tab",
    "provider": "ollama",
    "model": "deepseek-coder-v2"
  },
  "contextProviders": [
    {"name": "code", "params": {}},
    {"name": "docs", "params": {}},
    {"name": "web", "params": {}}
  ]
}
```

### 用法

```
Cmd+L  → 聊天
Cmd+I  →  编辑选中
Tab    →  补全
/cmd   →  自定义斜杠命令
```

## 🦊 Cody（Sourcegraph · 跨仓库上下文）

Cody = Sourcegraph 的 AI 助手，**强在跨仓库代码搜索**（Code Graph）。

```bash
# VSCode / JetBrains 插件：Cody
# 登录 Sourcegraph 账号（免费）
```

```json
// VSCode settings.json
{
  "cody.enabled": true,
  "cody.serverEndpoint": "https://sourcegraph.com",
  "cody.autocomplete.advanced.provider": "anthropic",
  "cody.autocomplete.advanced.model": "claude-sonnet-4-5"
}
```

Cody 能理解 monorepo 多仓库上下文，答"这个函数在哪些地方被调用"。

## 🛠 Aider（命令行 + git）

Aider = 终端里的 AI 结对编程 + **自动 git commit**。

```bash
pip install aider-chat

# 设置 API key
export ANTHROPIC_API_KEY=sk-ant-...

# 起 aider
aider --model claude-sonnet-4-5
# 在 prompt 输入
> 帮我重构 utils.ts 用 es-toolkit 替代 lodash

# 关键：aider 自动 git commit 每次改动
aider --auto-commits
aider --commit
```

### 实用功能

```bash
# 多文件
aider --file src/api/*.ts --model claude-sonnet-4-5

# 自动 lint
aider --auto-lint

# 语音
aider --voice

# 仓库映射（让 AI 理解结构）
aider --map-tokens 2048
```

## 🆚 对比

| | Continue | Cody | Aider |
|--|-----------|-------|--------|
| 形态 | 编辑器插件 | 编辑器插件 | CLI |
| 开源 | ✅（server 自托管） | ❌（闭源） | ✅ |
| 模型 | 任意 | 任意 | 任意 |
| 跨仓库 | 中 | **强** | 弱 |
| 自动 commit | ❌ | ❌ | ✅ |
| 适合 | 自由定制 | 大型 monorepo | 命令行党 |

## 🔗 下一步

- [Claude Code / OpenCode](/02-coding-tools/claude-code)
- [Cursor IDE](/02-coding-tools/cursor)
- [命令行速查](/02-coding-tools/commands)