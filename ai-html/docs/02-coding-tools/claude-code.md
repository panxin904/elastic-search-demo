---
title: Claude Code / OpenCode
date: 2026-08-15  # date-auto-injected
---

# Claude Code / OpenCode

> Anthropic 官方的 **CLI Agent**。在终端里直接配 Claude 改代码 / 跑命令 / 看文件。是**最值得装**的 AI 编程工具之一。

## 📦 安装

```bash
# 方式 1：npm（推荐）
npm install -g @anthropic-ai/claude-code

# 方式 2：macOS brew
brew install claude-code

# 方式 3：脚本
curl -fsSL https://claude.ai/install.sh | sh

# 验证
claude --version
```

## 🔐 认证

```bash
# 1. 浏览器登录（推荐）
claude auth login

# 2. 环境变量（CI 用）
export ANTHROPIC_API_KEY=sk-ant-...

# 3. Bedrock / Vertex AI（企业）
export CLAUDE_CODE_USE_BEDROCK=1
export CLAUDE_CODE_USE_VERTEX=1
```

## 🚀 用法

```bash
# 启动（当前目录）
claude

# 指定项目
claude /path/to/project

# 选模型
claude --model claude-sonnet-4-5
claude --model claude-opus-4-5   # 最强

# 一次性任务
claude "为 fib.py 加详细注释"
claude -p "分析这个 bug"          # --print 输出结果
claude "refactor this function" --model opus

# 管道（极强）
git diff | claude "review my changes"
cat error.log | claude "分析"
find . -name '*.py' | xargs claude "docstring these"

# 文件 / 目录作为上下文
claude src/
claude README.md

# 持续对话
claude --resume                       # 恢复上次
claude --continue                    # 同上
```

## 🛠 关键能力

| 命令 | 作用 |
|------|------|
| Edit files | 多文件编辑 |
| Run commands | bash / 装包 / 跑测试 |
| Search | ripgrep 风格搜索 |
| Web fetch | 抓网页 |
| Bash | 完整 shell 访问 |
| Memory | 跨会话记忆 |

## ⚙️ 配置

```bash
# 全局
claude config set theme dark
claude config set model claude-sonnet-4-5

# 项目级（CLAUDE.md）
cat > CLAUDE.md <<'EOF'
# Project Rules
- 用 TypeScript strict mode
- 测试必须写在 __tests__ 目录
- 不用 lodash，用 es-toolkit
- 任何 PR 都要更新 CHANGELOG.md
EOF
# Claude Code 自动读这文件

# Hooks（pre/post 工具调用）
# ~/.claude/hooks.json
```

## 🔌 MCP（强烈推荐）

```bash
# 加 MCP server
claude mcp add github \
  -e GITHUB_TOKEN=ghp_... \
  -- npx -y @modelcontextprotocol/server-github

# 装到项目（推荐）
claude mcp add-json my-server '{"command":"node","args":["server.js"]}'

# 列出 / 删除
claude mcp list
claude mcp remove github
```

## 🚀 高级

```bash
# Hook 例子（自动 lint）
cat > .claude/hooks.json <<'EOF'
{
  "PostToolUse": [{
    "matcher": "Write|Edit",
    "hooks": [{"type":"command","command":"npx eslint --fix $FILE"}]
  }]
}
EOF

# 自定义斜杠命令
cat > .claude/commands/review.md <<'EOF'
请评审当前 PR 的代码质量、安全性、性能。
EOF
# /review

# 跳过权限（不推荐生产）
claude --dangerously-skip-permissions
```

## 🆚 vs OpenCode

| | Claude Code | OpenCode（开源替代） |
|--|--------------|---------------------|
| 出品 | Anthropic 官方 | 社区开源 |
| 模型 | Claude | 任意（OpenAI / Claude / Ollama） |
| 风格 | Anthropic 体验 | 类 Claude Code |
| 适合 | Claude 用户 / 生产 | 多模型 / 本地 / 自托管 |

## 🔗 下一步

- [OpenAI SDK](/03-sdks/openai-sdk)
- [Claude SDK / Anthropic](/03-sdks/claude-sdk)
- [MCP 核心概念](/06-mcp/core)
- [命令行速查](/02-coding-tools/commands)