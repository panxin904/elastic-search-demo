---
title: GitHub Copilot
---

# GitHub Copilot

> GitHub + OpenAI 出品的 AI 编程助手。生态最大，VSCode / JetBrains / Neovim 全部支持。

## 📦 安装

```bash
# 1. 在编辑器装插件
# - VSCode: GitHub Copilot + Copilot Chat
# - JetBrains: Marketplace 装 GitHub Copilot
# - Neovim: github/copilot.vim

# 2. 登录
gh auth login --with-copilot

# 命令行（Copilot CLI，beta）
gh extension install github/gh-copilot
gh copilot suggest "list all pods"
gh copilot explain "this function"
```

## 🔑 核心功能

### 1. 行内补全

键入时灰字提示，按 `Tab` 接受。

```python
# 写 "def fibonacci(n):" 后 Copilot 自动建议
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

### 2. Copilot Chat

`Ctrl+I`（VSCode）：自然语言交互

```
# 解释代码
> 解释这个函数做什么

# 改代码
> 给这函数加 type hints

# 写测试
> 给 fibonacci 写 pytest
```

### 3. Copilot Workspace（Agent 模式 beta）

多文件改：让 Copilot 跨多个文件重构 / 加功能。

### 4. CLI

```bash
gh copilot suggest "list all docker containers"
# 建议：docker ps -a

gh copilot suggest -t shell "find large files"
# 建议：find / -size +100M

gh copilot explain "awk -F: '{print $1}' /etc/passwd"
# 解释：按 : 分割，打印第 1 列
```

## ⚙️ 配置

```json
// VSCode settings.json
{
  "github.copilot.enable": {
    "*": true,
    "yaml": false,
    "plaintext": false
  },
  "github.copilot.advanced": {
    "inlineSuggestCount": 5,
    "listCount": 10
  }
}
```

## 🆚 vs Cursor

| | Copilot | Cursor |
|--|---------|--------|
| 出品 | GitHub / OpenAI | Cursor 团队 |
| 模型 | OpenAI / Anthropic | 多家 |
| 编辑器 | VSCode / JetBrains / Neovim | 自己（VSCode 兼容） |
| 上下文 | 当前文件 + 引用 | 多文件 + Agent 模式 |
| 适合 | 补全 + Chat | 全流程 IDE |

## 🔗 下一步

- [Cursor IDE](/02-coding-tools/cursor)
- [Claude Code / OpenCode](/02-coding-tools/claude-code)
- [命令行速查](/02-coding-tools/commands)