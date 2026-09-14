---
title: DeepSeek Harness 使用文档
date: 2026-09-14  # date-auto-injected
---

# 🚀 DeepSeek Harness 使用文档

> 5 分钟跑通 Harness。从一行启动 Web UI、源码安装、到 profile 配置，覆盖所有上手场景。

## 1️⃣ 一行启动（最快，推荐先体验）

### 前置条件

```
- Node.js ^22.19.0（必须，旧版会报错）
- pnpm 10+（仅源码安装需要）
- 任意 DeepSeek API Key（或 OpenAI / Anthropic Key）
```

### 启动命令

```bash
# 一行启动 Web UI（默认端口 3080）
npx @deepseek-ai/dsh web

# 首次运行会问 3 件事：
#   1. 配置 API Key（或选已有 profile）
#   2. 选模型（默认 deepseek-chat / deepseek-reasoner）
#   3. 工作目录（默认当前路径）

# 打开浏览器访问
open http://localhost:3080
```

### 启动参数

```bash
# 指定端口
npx @deepseek-ai/dsh web --port 9090

# 指定工作目录
npx @deepseek-ai/dsh web --cwd /Users/me/projects/my-app

# 指定 profile（见 §3）
npx @deepseek-ai/dsh web --profile work

# 禁用 Web UI（纯 CLI）
npx @deepseek-ai/dsh --no-web

# 后台运行 + 日志
npx @deepseek-ai/dsh web --daemon --log ~/.local/share/dsh/daemon.log
```

### 首次配置向导

```
┌──────────────────────────────────────────┐
│  Welcome to DeepSeek Harness v0.1.2-rc.1│
│                                          │
│  Step 1/3: Select API Provider           │
│  > DeepSeek                              │
│    OpenAI                                 │
│    Anthropic                              │
│    Custom (OpenAI-compatible)             │
│                                          │
│  Step 2/3: API Key                       │
│  > sk-********************************** │
│                                          │
│  Step 3/3: Default Model                 │
│  > deepseek-chat (V3.2)                  │
│    deepseek-reasoner (R1)                │
│    deepseek-coder                        │
└──────────────────────────────────────────┘

Config saved to ~/.config/dsh/config.yaml
Starting Web UI on http://localhost:3080
```

## 2️⃣ 源码安装（开发者推荐）

### 克隆仓库

```bash
git clone https://github.com/deepseek-ai/deepseek-harness.git
cd deepseek-harness
```

### 安装依赖

```bash
# 必须用 pnpm（项目用 pnpm workspaces）
npm i -g pnpm@10

pnpm install              # 安装所有 packages 的依赖
```

### 构建

```bash
pnpm run build            # esbuild 构建所有包
```

### 启动

```bash
# 方式 1：用 CLI 包启动
pnpm dsh web

# 方式 2：单独启动 server + web
pnpm --filter @harness/server dev       # 后端（端口默认 3000）
pnpm --filter @harness/web dev          # 前端（端口默认 5173）
```

### 开发模式（hot reload）

```bash
# 终端 1：core + server 监听
pnpm run dev:server

# 终端 2：前端 hot reload
pnpm run dev:web

# 浏览器自动打开 http://localhost:5173
```

### 运行测试

```bash
pnpm test                  # 所有单元测试（Vitest）
pnpm test:e2e              # Playwright 端到端
pnpm test --filter @harness/server   # 单包测试
```

## 3️⃣ Profile 管理（多环境必备）

### 概念

```
Profile = 一套独立的 API Key + 模型 + 配置
~/.config/dsh/
├─ config.yaml         # 默认配置
├─ profiles/
│  ├─ personal.yaml    # 个人项目（用 DeepSeek 个人 Key）
│  ├─ work.yaml        # 公司项目（用公司 Anthropic Key）
│  └─ eval.yaml        # 评测任务（用 Qwen 长上下文模型）
└─ sessions/           # 会话历史
```

### 创建 profile

```bash
# 交互式创建
dsh profile new work

# 或直接写 YAML
mkdir -p ~/.config/dsh/profiles
cat > ~/.config/dsh/profiles/work.yaml << 'YAML'
name: work
provider: anthropic
api_key: sk-ant-xxx
base_url: https://api.anthropic.com
model: claude-sonnet-4.5
fallback_model: claude-haiku-4
max_context: 200000
tools:
  enabled:
    - file_edit
    - shell
    - web_search
    - code_search
  disabled:
    - email_send
permissions:
  shell:
    allow: ["npm", "pnpm", "git", "ls", "cat"]
    deny:  ["rm -rf", "sudo", "curl | sh"]
YAML
```

### 切换 profile

```bash
# 命令行参数
dsh web --profile work

# 环境变量
export DSH_PROFILE=work
dsh web

# 当前 shell 一次性
DSH_PROFILE=work dsh web
```

### 查看所有 profile

```bash
dsh profile list

# Output:
# NAME       PROVIDER    MODEL              DEFAULT
# personal   deepseek    deepseek-chat      ✓
# work       anthropic   claude-sonnet-4.5
# eval       openai      qwen-long-context
```

### 删除 / 重命名

```bash
dsh profile rm work
dsh profile rename personal dev
```

## 4️⃣ 模型配置

### 内置 Provider

```yaml
# ~/.config/dsh/config.yaml
provider: deepseek          # 默认 provider
providers:
  deepseek:
    api_key: sk-xxx
    base_url: https://api.deepseek.com/v1
    default_model: deepseek-chat
    models:
      v3:    { id: deepseek-chat,     max_tokens: 8192 }
      r1:    { id: deepseek-reasoner, max_tokens: 16000 }
      coder: { id: deepseek-coder,    max_tokens: 8192 }

  openai:
    api_key: sk-xxx
    base_url: https://api.openai.com/v1
    models:
      gpt5:  { id: gpt-5,           max_tokens: 32000 }
      gpt5m: { id: gpt-5-mini,      max_tokens: 16000 }

  anthropic:
    api_key: sk-ant-xxx
    models:
      opus:   { id: claude-opus-4,    max_tokens: 32000 }
      sonnet: { id: claude-sonnet-4.5, max_tokens: 16000 }

  custom:
    api_key: sk-xxx
    base_url: http://localhost:8000/v1       # 自部署 vLLM
    default_model: deepseek-r1-distill-32b
```

### 用模型映射

```bash
# Web UI：顶栏下拉切换
# CLI 命令：
dsh --model r1        # 使用 deepseek-reasoner
dsh --model sonnet    # 使用 claude-sonnet-4.5
```

### 自动路由（按任务选模型）

```yaml
# 配置智能路由
routing:
  simple_qa:        gpt5m      # 短问答用 mini 模型
  complex_reason:   r1         # 复杂推理用 R1
  code_generation:  coder      # 代码生成用 coder
  default:          v3         # 默认 V3
```

## 5️⃣ 工作目录与会话

### 默认行为

```
Harness 启动时会在当前目录（或 --cwd 指定）寻找：
1. .dsh/ 目录（项目级配置）→ 优先
2. 当前 git 仓库根目录 → 作为工作区
3. 否则用当前目录

会话状态保存到：
~/.local/share/dsh/sessions/<session-id>/
├─ messages.json     # 完整对话
├─ edits.jsonl       # 所有文件修改（可回滚）
├─ commands.jsonl    # 所有 shell 命令
└─ checkpoints/      # 关键节点快照
```

### 查看历史会话

```bash
dsh session list

# ID                STARTED           TURNS  FILES  COST
# abc123def456      2026-09-14 10:23   42    8     $0.12
# xyz789ghi012      2026-09-13 18:45   18    3     $0.05
```

### 恢复会话

```bash
dsh session resume abc123def456
```

### 导出会话

```bash
dsh session export abc123def456 --format markdown > session.md
dsh session export abc123def456 --format json > session.json
```

## 6️⃣ 配置文件位置

```
~/.config/dsh/
├─ config.yaml          # 主配置（创建于首次启动）
├─ profiles/            # 多 profile 目录
├─ plugins/             # 已装插件清单
├─ skills/              # 用户自定义 Skills
└─ logs/                # 运行日志

~/.local/share/dsh/
├─ sessions/            # 会话历史
├─ cache/               # 模型响应缓存
└─ checkpoints/         # 文件快照（可回滚）
```

## 7️⃣ 常用命令速查

```bash
# 启动
dsh                       # 等同 dsh web，但只在 TTY 下
dsh web --port 9090       # Web UI
dsh --no-web              # 仅 CLI

# 模式
dsh --mode standard       # 默认
dsh --mode ptc            # PTC 模式
dsh --mode minimal        # 极简
dsh --mode creative       # 创造

# Profile
dsh profile new <name>
dsh profile list
dsh profile rm <name>
dsh --profile <name>

# 模型
dsh --model <alias>
dsh --model deepseek-chat
dsh --model claude-sonnet-4.5

# 会话
dsh session list
dsh session resume <id>
dsh session export <id>

# 插件
dsh plugin list
dsh plugin install <npm-name>
dsh plugin uninstall <npm-name>

# Skills
dsh skill list
dsh skill run <skill-name> [args...]

# 系统
dsh doctor                # 健康检查（Node 版本/依赖/Key 有效性）
dsh update                # 升级到最新版
dsh uninstall             # 卸载（保留配置）
dsh --help                # 完整帮助
dsh --version
```

## 8️⃣ 健康检查

```bash
dsh doctor

# Checks:
# ✓ Node.js v22.19.0 (要求 ^22.19.0)
# ✓ pnpm 10.12.0 (可选，源码安装需要)
# ✓ ~/.config/dsh/ 存在
# ✓ Profile "personal" 配置完整
# ✓ DeepSeek API Key 有效（余额 $5.42）
# ✓ 模型 deepseek-chat 可访问
# ✓ 模型 deepseek-reasoner 可访问
# ✓ 插件加载：12 个官方 + 0 个第三方
# ✓ 端口 3080 可用
# ✓ 工作目录可写
# 
# All checks passed!
```

## 9️⃣ 升级与卸载

```bash
# 升级（npx 用户）
npx @deepseek-ai/dsh@latest web

# 升级（源码用户）
cd deepseek-harness
git pull
pnpm install
pnpm run build

# 卸载
npm uninstall -g @deepseek-ai/dsh    # 如果全局装过
rm -rf ~/.config/dsh                 # 删除配置
rm -rf ~/.local/share/dsh            # 删除会话/缓存

# ⚠️ 注意：profiles/、skills/ 备份后再删
```
