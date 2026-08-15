---
title: Aider
---

# Aider

> 终端里的 **AI 结对编程 + git**。每改完自动 commit，适合 CLI 党。

## 📦 安装

```bash
# pip（推荐）
pip install aider-chat

# uv
uv tool install aider-chat

# 验证
aider --version
```

## 🔐 认证

```bash
# OpenAI / Anthropic / DeepSeek / Ollama
export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...
export DEEPSEEK_API_KEY=sk-...

# 用 Ollama 本地
aider --model ollama_chat/qwen2.5-coder:7b
```

## 🚀 启动

```bash
# 当前目录
aider

# 指定文件（提前把文件加到 chat）
aider src/api.py src/utils.py

# 选模型
aider --model claude-sonnet-4-5
aider --model sonnet
aider --model deepseek-chat

# 高级
aider --model sonnet --auto-commits --auto-lint --voice
```

## 🎯 实战套路

```bash
# 加新功能
> 给 user 表加一列 deleted_at，加软删除接口

# 重构
> 把 utils.py 里 lodash 替换成 es-toolkit

# 写测试
> 给 user_service.py 加 pytest，覆盖成功/失败/边界

# 改 bug
> 这个 test 失败：# 输出。帮我修

# 改完自动 commit
> git diff 看下
> 提交吧，commit message 写"refactor: 替换 lodash 为 es-toolkit"

# 多文件
aider --file src/api/*.ts
```

## ⚙️ 配置

```yaml
# ~/.aider.conf.yml
model: claude-sonnet-4-5
auto-commits: true
auto-lint: true
auto-test: true
test-cmd: pytest
lint-cmd: ruff check
git-commit-args: --no-verify
```

## 🆚 vs Cursor / Claude Code

| | Aider | Cursor | Claude Code |
|--|-------|--------|--------------|
| 形态 | CLI | IDE | CLI |
| 自动 commit | **✅** | ❌ | ❌ |
| 自动 lint | **✅** | ❌ | ❌ |
| 适合 | CLI 党 + git | 写代码 | 系统级 |

## 🛠 进阶

```bash
# 多模型路由
aider --model sonnet src/*.py
aider --model o1-mini "complex refactor"

# 仓库映射
aider --map-tokens 4096
# AI 能理解整个 repo 结构

# 语音（边说边改）
aider --voice

# 排除文件
aider --exclude "*.test.js" --exclude "dist/"
```

## 🔗 下一步

- [Claude Code / OpenCode](/02-coding-tools/claude-code)
- [Continue / Cody](/02-coding-tools/continue-cody)
- [命令行速查](/02-coding-tools/commands)