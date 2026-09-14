---
title: DeepSeek Harness 使用教程
date: 2026-09-14  # date-auto-injected
---

# 📘 DeepSeek Harness 使用教程

> 9 节系统化教程：从首次启动到高级定制。配合演示项目可一次跑通。

## 🛠️ 第 1 课：环境准备

### 系统要求

```
┌──────────────────────────────────────────┐
│  最低要求                                │
│  - Node.js ^22.19.0（必须）             │
│  - 4GB RAM（仅 Web UI）                 │
│  - 500MB 磁盘                           │
│                                          │
│  推荐配置                                │
│  - Node.js ^22.19.0                     │
│  - 8GB RAM（同时跑 Web + 后端）         │
│  - 2GB 磁盘（含会话历史）               │
│  - 支持平台：macOS / Linux / WSL2       │
└──────────────────────────────────────────┘
```

### 安装 Node.js（macOS）

```bash
# 用 nvm（推荐）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
nvm install 22.19
nvm use 22.19
node --version    # v22.19.0
```

### 安装 Node.js（Linux / WSL2）

```bash
# 用 n
curl -fsSL https://raw.githubusercontent.com/tj/n/master/bin/n -o n && \
    chmod +x n && sudo ./n 22.19

# 或用 NodeSource
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 安装 pnpm（仅源码安装需要）

```bash
npm install -g pnpm@10
pnpm --version     # 10.x.x
```

### 验证环境

```bash
dsh doctor

# 第一次运行会自动检测所有依赖
```

## 🎯 第 2 课：第一次启动 Web UI

### 启动

```bash
mkdir ~/my-project && cd ~/my-project
npx @deepseek-ai/dsh web
```

### 浏览器操作

```
1. 打开 http://localhost:3080
2. 输入 API Key（首次）
3. 选模型 deepseek-chat
4. 工作目录 = ~/my-project
5. 看到左侧"会话区"+ 中间"对话区"+ 右侧"工具面板"
```

### 第一次对话

```
用户："在当前目录创建一个 README.md，写一段 Hello World 介绍"
Harness：{
  tools_used: [write_file, shell],
  diff: "+  # Hello World Project\n+  This is my first project.\n",
  files_modified: ["README.md"],
  commands_executed: ["ls -la"]
}
```

## 🔧 第 3 课：理解工作目录

### 概念

```
工作目录（CWD）= Harness 操作的根目录
所有文件编辑、Shell 命令都在这个范围内执行。

默认 = 当前 shell 目录
可手动指定：--cwd /path/to/project
```

### 项目结构建议

```
my-project/
├─ .dsh/                 # Harness 项目级配置
│  ├─ config.yaml       # 覆盖 ~/.config/dsh/config.yaml
│  ├─ skills/           # 项目专属 Skills
│  └─ plugins.json      # 项目依赖的插件
├─ src/                  # 源码
├─ tests/
├─ docs/
├─ package.json
└─ README.md
```

### .dsh/config.yaml 示例

```yaml
# 项目级配置（覆盖全局）
profile: project-default
provider: anthropic
model: claude-sonnet-4.5
tools:
  enabled:
    - file_edit
    - shell
    - web_search
    - code_search
  disabled:
    - email_send
    - deploy
permissions:
  shell:
    allow: ["npm test", "npm run build", "git status", "git diff"]
```

## 🧰 第 4 课：内置工具详解

### 工具清单

```
Harness 内置 7 大类工具：

1. file_edit    文件读写（read/write/edit/multi_edit）
2. shell        Shell 命令（受权限控制）
3. file_search  按文件名/glob/内容搜
4. code_search  按符号（函数/类/变量）搜
5. web_search   联网检索
6. web_fetch    抓取 URL 内容
7. todo         任务清单
```

### file_edit 工具

```yaml
# Harness 调用示例
{
  "tool": "file_edit",
  "params": {
    "file": "src/api/users.ts",
    "operations": [
      {"op": "replace", "old": "function getUser", "new": "async function getUser"},
      {"op": "insert_after", "anchor": "export const", "text": "\n\nexport const newFn = ..."}
    ]
  }
}
```

### shell 工具

```bash
# 默认受权限控制（见第 5 课）
# 用户确认流程：
#   1. Harness 准备执行 "npm test"
#   2. 弹出确认框（Web UI）或 CLI 等待 y/n
#   3. 用户同意 → 执行
#   4. 执行结果回传到对话
```

### file_search 工具

```yaml
# glob 模式
{
  "tool": "file_search",
  "params": {
    "pattern": "**/*.{ts,tsx}",
    "exclude": ["**/node_modules/**", "**/dist/**"]
  }
}

# 内容搜索
{
  "tool": " "file_search"",  # 实际用 grep 工具
  "params": {
    "type": "content",
    "query": "TODO",
    "files": "src/**/*.ts"
  }
}
```

## 🔐 第 5 课：权限与沙箱

### 默认权限策略

```
Harness 默认所有危险操作需要用户确认：

⚠️ 需要确认：
- 写文件（除 .dsh/cache/）
- 执行 shell 命令
- 网络请求（web_fetch）
- 装/卸插件

✅ 无需确认（只读）：
- 读文件
- 文件搜索
- 代码搜索
- 会话内查询
```

### 配置权限

```yaml
# ~/.config/dsh/config.yaml
permissions:
  # 文件系统
  filesystem:
    read:   ["**"]                    # 允许读所有
    write:  ["src/**", "tests/**", "docs/**", "*.md", "*.json"]
    deny:   [".env", "secrets/**", ".git/**", "node_modules/**"]

  # Shell 命令
  shell:
    allow: [
      "ls", "cat", "grep", "find",
      "git status", "git diff", "git log",
      "npm test", "npm run lint", "pnpm test"
    ]
    deny: [
      "rm -rf", "sudo", "curl | sh", "chmod 777",
      "git push --force", "git reset --hard"
    ]

  # 网络
  network:
    allow_domains: ["github.com", "npmjs.com", "api.deepseek.com"]
    deny_domains:  ["localhost:*"]      # 防止 SSRF
```

### 沙箱级别

```yaml
sandbox:
  level: standard       # relaxed / standard / strict / paranoid

# relaxed    → 大部分操作直接执行
# standard   → 默认，危险操作需确认
# strict     → 所有写操作需确认
# paranoid   → 所有操作需确认（含读）
```

### 一次性放行

```bash
# 在 CLI 中遇到权限弹窗时：
y        # 放行一次
n        # 拒绝
a        # 放行所有（当前会话）
!        # 永远放行（写入配置）
?        # 查看这条命令的危险度
```

## 🎨 第 6 课：Skills 系统

### 概念

```
Skill = 一组预设 prompt + 工具调用模式
让 Harness 在特定场景下"自动应用最佳实践"

例：
- /review       → 自动审查当前 PR
- /refactor     → 智能重构代码
- /git-commit   → 按规范生成 commit message
- /test         → 自动补单元测试
- /docs         → 自动生成/更新文档
```

### 调用 Skill

```bash
# CLI：
dsh /review

# Web UI：
# 输入框打 / 触发 skill 列表 → 选择
```

### 内置 Skills

```
/init         初始化项目（生成 .dsh/ + README）
/review       Code Review（基于 git diff）
/refactor     智能重构（保持行为不变）
/test         自动补单元测试
/docs         生成/同步文档
/commit       按 Conventional Commits 生成 commit
/fix          自动修复 lint/test 报错
/clean        清理无用代码（dead code）
/changelog    更新 CHANGELOG.md
```

### 自定义 Skill

```bash
# 创建 ~/.config/dsh/skills/my-skill.md
cat > ~/.config/dsh/skills/deploy.md << 'SKILL'
---
name: deploy
description: 一键部署当前项目
mode: standard
---

# /deploy Skill

## 流程
1. 检查 git status（必须 clean）
2. 跑测试（npm test）
3. 跑 lint
4. 询问部署目标（staging / prod）
5. 执行部署命令

## 输出
- 部署结果
- 部署日志
- 后续监控链接
SKILL
```

```bash
# 现在可用
dsh /deploy
```

## 🤖 第 7 课：子代理（Subagent）

### 概念

```
子代理 = Harness 内部启动另一个 Agent 实例
用于：
- 并行处理多个独立任务
- 隔离上下文（避免污染主对话）
- 用不同模型处理不同子任务
```

### 使用场景

```
用户："重构 src/auth/ 下所有文件，并写测试"

Harness 自动启动 3 个子代理：
├─ subagent-1: 重构 auth/login.ts
├─ subagent-2: 重构 auth/session.ts
└─ subagent-3: 重构 auth/permission.ts

3 个并行 → 主代理收集结果 → 写测试
```

### 配置子代理

```yaml
# ~/.config/dsh/config.yaml
subagent:
  enabled: true
  max_concurrent: 4
  default_model: gpt5m           # 子代理用便宜模型
  trigger:
    parallel_tasks: true          # 检测到独立任务时并行
    code_search_depth: 3          # 搜索深度 >3 时启用
```

### 手动触发子代理

```bash
# CLI
dsh spawn "写测试覆盖 auth/login.ts" --model gpt5m

# 在对话中
用户："用子代理分析 src/api/ 下的所有 controller 接口兼容性"
```

## 🌳 第 8 课：PTC 模式（Programmatic Tool Calling）

### 概念

```
PTC 模式 = 把"工具调用"提升为"程序执行"
Harness 写一段 TypeScript 代码来编排多个工具，而不是一次一个工具调用。

优势：
- 复杂的工具编排更可靠
- 可读性高（代码即文档）
- 可调试（TypeScript 类型检查）
```

### 示例：批量重命名文件

```
标准模式：
  1. list files
  2. read each file
  3. write each file
  4. delete old file
  （多次工具调用，容易出错）

PTC 模式：
  Harness 生成：
  ```typescript
  for (const path of await glob('src/*.old.ts')) {
    const content = await readFile(path)
    const newPath = path.replace('.old.ts', '.ts')
    await writeFile(newPath, content)
    await deleteFile(path)
  }
  ```
  一次性执行，类型安全
```

### 启用 PTC

```bash
# CLI
dsh --mode ptc

# Web UI：顶栏下拉选 "PTC"
```

### PTC 模式限制

```
⚠️ PTC 模式当前限制：
- 必须在能执行 Node.js 的环境（沙箱已支持）
- 不能直接调用 Harness 外部 API（如 web_fetch 在 PTC 内部是异步）
- 子代理不递归（PTC 子任务仍用标准模式）
```

## 🎯 第 9 课：创造模式（Creative）

### 概念

```
创造模式 = Harness 自动尝试多种方案 + 自我反思
用于没有明确最优解的探索性任务。
```

### 工作流程

```
1. 列出 3 种实现思路
2. 分别实现
3. 跑基准测试 / 静态分析
4. 对比结果
5. 推荐 + 说明理由
```

### 启用

```bash
dsh --mode creative
```

### 示例

```
用户："写一个 HTTP 客户端"
（创造模式下 Harness 会）：
  - axios 实现 → 跑测 → benchmark
  - fetch 实现 → 跑测 → benchmark
  - ky 实现 → 跑测 → benchmark
  - 给出推荐："对于你项目，fetch 更轻量；但如果需要拦截器，axios 更合适"
```

## 🩺 第 10 课：故障排查

### 启动失败

```bash
# 报错 "EADDRINUSE :::3080"
# → 端口占用
dsh web --port 9090
# 或杀掉占 3080 的进程
lsof -ti:3080 | xargs kill -9

# 报错 "Cannot find module '@harness/core'"
# → npx 缓存损坏
rm -rf ~/.npm/_npx
npx @deepseek-ai/dsh@latest web

# 报错 "Node version not supported"
# → Node 太旧
nvm install 22.19 && nvm use 22.19
```

### API 调用失败

```bash
# 报错 "401 Unauthorized"
dsh doctor                     # 检查 Key 是否过期
# → 在 ~/.config/dsh/profiles/personal.yaml 更新 API Key

# 报错 "429 Too Many Requests"
# → 限流。在 config.yaml 加：
rate_limit:
  rps: 5                       # 每秒请求数
  retry_after: 60              # 429 后等待秒数
```

### 工具调用失败

```bash
# 报错 "Permission denied"
# → 受权限策略限制
# 方案 A：临时放行（CLI 输入 y）
# 方案 B：编辑 config.yaml 加 allow 规则
# 方案 C：检查 .dsh/config.yaml 是否覆盖了全局配置

# 报错 "File not found"
# → 工作目录设置错误
dsh web --cwd /correct/path

# 报错 "Command not found in shell"
# → shell PATH 缺少工具
# 编辑 ~/.config/dsh/config.yaml:
shell:
  env:
    PATH: "$PATH:/usr/local/bin:/opt/homebrew/bin"
```

### 会话卡死

```bash
# Web UI 无响应
# 强制刷新：Cmd + Shift + R
# 或重启服务：
dsh web --port 3081           # 换个端口

# CLI 卡在 prompt
# Ctrl + C 中断当前 turn
# 输入 /exit 完全退出

# 恢复之前会话：
dsh session list
dsh session resume <id>
```
