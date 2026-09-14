---
title: DeepSeek Harness 经典架构
date: 2026-09-14  # date-auto-injected
---

# 🏛️ DeepSeek Harness 经典架构

> 8 种典型 Harness 部署/集成架构：从单用户 CLI 到企业级 AI 中台。本章聚焦 **Agent 运行时**层（不是模型推理层）。

## 🏗️ 架构 1：单用户 CLI

```
┌─────────┐  stdin/stdout  ┌──────┐  HTTPS  ┌──────────┐
│ 用户终端 │ ─────────────►│ dsh │ ──────► │ DeepSeek │
│         │ ◄───────────── │      │ ◄────── │   API    │
└─────────┘    streaming   └──────┘         └──────────┘
```

**适用**：个人项目、临时任务、单机开发

**配置**：
```yaml
# ~/.config/dsh/config.yaml
provider: deepseek
api_key: sk-xxx
default_model: deepseek-chat
mode: standard
```

**启动**：
```bash
dsh
```

## 🖥️ 架构 2：本地 Web UI

```
┌─────────┐  HTTPS  ┌──────────┐  HTTP   ┌──────┐  HTTPS  ┌──────────┐
│ 浏览器  │ ──────► │ Web UI   │ ──────► │ dsh  │ ──────► │ DeepSeek │
│ (3080)  │ ◄────── │ (Vite)   │ ◄────── │      │ ◄────── │   API    │
└─────────┘  WSS   └──────────┘  SSE    └──────┘         └──────────┘
```

**适用**：个人开发 + 浏览器交互体验

**组件**：
- `@harness/server`（Fastify + WebSocket）
- `@harness/web`（Vite + Vue 3）
- 流式响应（SSE / WebSocket）

**启动**：
```bash
dsh web --port 3080
```

## 👥 架构 3：团队共享 Profile

```
┌──────┐
│ 团队 │ ──── 共享 ~/.config/dsh/profiles/team.yaml
└──────┘
         │
         ├─ 成员 A: dsh --profile team
         ├─ 成员 B: dsh --profile team
         └─ 成员 C: dsh --profile team

配置源（Git 仓库）：
my-team-config/
├─ profiles/
│  ├─ team.yaml          # 共享配置
│  └─ team-private.yaml.example  # 模板（每人填 Key）
└─ skills/               # 团队专属 Skills
   ├─ release.md
   └─ oncall.md
```

**适用**：小团队（5-20 人）统一配置

**部署**：
```bash
git clone git@github.com:my-org/dsh-team-config ~/.config/dsh-team
ln -s ~/.config/dsh-team/profiles ~/.config/dsh/profiles/team
ln -s ~/.config/dsh-team/skills ~/.config/dsh/skills/team
```

## 🏢 架构 4：自部署中心（企业级）

```
                   ┌────────────────────────────┐
                   │ Harness 中心化服务         │
                   │ （自部署 Fastify + UI）    │
                   │                            │
                   │  - 用户管理 + SSO         │
                   │  - Profile / Skill 仓库    │
                   │  - 计费审计               │
                   │  - 会话历史               │
                   └────────┬───────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
   ┌─────────┐          ┌─────────┐         ┌─────────┐
   │ 开发者 A│          │ 开发者 B│         │ 开发者 C│
   │ dsh web │          │ dsh web │         │ dsh cli │
   └────┬────┘          └────┬────┘         └────┬────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │ 模型代理        │
                   │ - DeepSeek API  │
                   │ - 自部署 vLLM   │
                   │ - 多模型路由    │
                   └─────────────────┘
```

**适用**：中大型企业（100+ 开发者）

**关键模块**：
- 用户管理：LDAP / SSO 接入
- 权限分级：Admin / Developer / Viewer
- 审计日志：所有操作可追溯
- 成本归集：按团队/项目分摊
- 模型路由：按任务路由到最合适的模型

## 🤖 架构 5：多 Profile 并行（不同项目）

```
       项目 A（个人）
       dsh web --profile=personal
       cwd: ~/projects/side-project
       model: deepseek-chat

       项目 B（公司）
       dsh web --profile=work
       cwd: ~/work/main-app
       model: claude-sonnet-4.5

       项目 C（评测）
       dsh web --profile=eval
       cwd: ~/eval/llm-bench
       model: qwen-long-context
```

**适用**：多项目开发者，避免上下文污染

**Profile 切换**：
```bash
# 自动切换（基于目录）
dsh watch ~/projects --profile=personal
dsh watch ~/work --profile=work

# 手动
dsh --cwd /path --profile X
```

## 🔧 架构 6：CI/CD 中的 Harness

```
┌──────────────┐  git push    ┌──────────────────┐
│  开发者 push │ ──────────► │ GitHub Actions    │
└──────────────┘             └────────┬─────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │ dsh --mode ptc   │
                              │ /review /test    │
                              └────────┬─────────┘
                                       │
              ┌────────────────────────┼────────────────────┐
              ▼                        ▼                    ▼
        ┌──────────┐            ┌──────────┐          ┌──────────┐
        │ 评论 PR  │            │ 自动修复 │          │ 跑测试   │
        │ (AI review)│          │ (commit) │          │ 覆盖率   │
        └──────────┘            └──────────┘          └──────────┘
```

**示例 workflow**：

```yaml
# .github/workflows/harness-ci.yml
name: Harness CI
on: [pull_request]

jobs:
  harness-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-node@v4
        with:
          node-version: 22.19

      - name: Install Harness
        run: npm install -g @deepseek-ai/dsh

      - name: AI Code Review
        env:
          DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
        run: |
          dsh --no-web --mode standard <<'EOF'
          /review ${{ github.event.pull_request.base.sha }} ${{ github.event.pull_request.head.sha }}
          输出 Markdown 格式评论到 PR
          EOF

      - name: Post Review Comment
        uses: marocchino/sticky-pull-request-comment@v2
        with:
          message: ${{ steps.review.outputs.comment }}
```

## 🌐 架构 7：Harness 中台化（多团队多模型）

```
                         ┌────────────────────────────┐
                         │     Harness Gateway        │
                         │  - 统一认证 / 计费         │
                         │  - Profile 仓库            │
                         │  - 插件市场                │
                         │  - 会话审计                │
                         │  - 模型路由                │
                         │  - 缓存代理                │
                         └─────────┬──────────────────┘
                                   │
       ┌──────────┬───────────────┼───────────────┬──────────┐
       ▼          ▼               ▼               ▼          ▼
   ┌────────┐ ┌────────┐      ┌────────┐    ┌────────┐  ┌────────┐
   │ 团队 A │ │ 团队 B │      │ 团队 C │    │ 团队 D │  │ 团队 E │
   │前端组  │ │后端组  │      │数据组  │    │运维组  │  │产品组  │
   └────────┘ └────────┘      └────────┘    └────────┘  └────────┘
       │          │               │               │          │
       └──────────┴───────────────┼───────────────┴──────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
        ┌──────────┐         ┌──────────┐         ┌──────────┐
        │ DeepSeek │         │ 自部署   │         │ 第三方   │
        │   API    │         │ vLLM     │         │ Claude   │
        └──────────┘         └──────────┘         └──────────┘
```

**适用**：500+ 开发者、跨 BU、多模型

**核心组件**：

```yaml
# Harness Gateway（自实现 + @harness/server 改造）
gateway:
  port: 443
  auth:
    sso: oidc
    roles: [admin, lead, dev, viewer]
  models:
    pool:
      - id: deepseek-v3
        provider: deepseek
        routing_weight: 0.5
      - id: claude-sonnet
        provider: anthropic
        routing_weight: 0.3
      - id: self-hosted-qwen
        provider: vllm
        endpoint: http://gpu-cluster:8000/v1
        routing_weight: 0.2
  cache:
    type: redis
    ttl: 3600
  billing:
    cost_per_token:
      deepseek-v3: { input: 0.27, output: 1.10 }
      claude-sonnet: { input: 3, output: 15 }
  audit:
    log_path: s3://audit-bucket/dsh/
    retention_days: 365
```

## 🧠 架构 8：Cordis 插件系统核心架构（源码级）

```
┌─────────────────────────────────────────────────────────────┐
│ Harness Process                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Cordis Context（核心容器）                             │ │
│  │  - 插件加载（PluginLoader）                             │ │
│  │  - 依赖注入（inject / registry）                        │ │
│  │  - 事件总线（emitter）                                 │ │
│  │  - 生命周期（start / stop）                            │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                  │
│            ┌───────────────┼────────────────┐                │
│            ▼               ▼                ▼                │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐          │
│  │ ModelPlugin  │ │  ToolPlugin  │ │  SkillPlugin │  ...     │
│  │ (ctx.model)  │ │ (ctx.tool.X) │ │ (ctx.skill.X)│          │
│  └──────────────┘ └──────────────┘ └──────────────┘          │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Agent Loop（主循环）                                  │ │
│  │  1. 接收用户消息                                       │ │
│  │  2. 调用 model 生成（含 tool_use）                     │ │
│  │  3. 派发 tool 到 ToolPlugin                           │ │
│  │  4. 把 tool 结果回传给 model                           │ │
│  │  5. 重复 2-4 直到 model 返回最终答案                   │ │
│  │  6. 保存会话、检查点                                   │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Sandbox（沙箱）                                       │ │
│  │  - 文件访问（path 安全过滤）                          │ │
│  │  - Shell 命令（白名单 + 用户确认）                    │ │
│  │  - 网络请求（domain 白名单）                          │ │
│  │  - 资源限制（CPU / 内存 / 磁盘）                      │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Cordis 插件加载流程

```typescript
// 简化的核心代码（实际在 packages/core/src/loader.ts）

export async function loadPlugins(ctx: Context, config: Config) {
  // 1. 解析 plugin 配置
  const pluginSpecs = parsePlugins(config.plugins)

  // 2. 按依赖拓扑排序
  const sorted = topoSort(pluginSpecs, p => p.dependencies)

  // 3. 实例化每个 plugin（注入依赖）
  for (const spec of sorted) {
    const deps = spec.dependencies.map(d => ctx[d])  // DI
    const instance = new spec.service(ctx, ...deps)
    ctx.registry.set(spec.name, instance)
  }

  // 4. 启动所有 plugin（start hook）
  await Promise.all(
    Array.from(ctx.registry.values()).map(p => p.start?.())
  )

  // 5. 事件总线建立连接
  ctx.emit('plugins:loaded')
}
```

### 工具调用生命周期

```
┌────────┐                 ┌────────┐                ┌────────┐
│ Model  │ tool_use(name=X)│  ctx   │ tool(X, args)  │ Tool   │
│ (LLM)  │ ──────────────► │(Cordis)│ ─────────────► │ Plugin │
│        │ ◄────────────── │        │ ◄───────────── │        │
└────────┘   tool_result   └────────┘     result     └────────┘
     │                                                     │
     │                                                     ▼
     │                                            ┌─────────────┐
     │                                            │ 沙箱检查     │
     │                                            │ 权限检查     │
     │                                            └─────────────┘
     │                                                     │
     │                                                     ▼
     │                                            ┌─────────────┐
     │                                            │ 执行工具    │
     │                                            │ (file/shell)│
     │                                            └─────────────┘
```

## 📐 架构对比表

| 架构 | 适用 | 复杂度 | 用户量 |
|---|---|---|---|
| 1. 单用户 CLI | 个人 | ⭐ | 1 |
| 2. 本地 Web UI | 个人 | ⭐ | 1 |
| 3. 团队共享 Profile | 小团队 | ⭐⭐ | 5-20 |
| 4. 自部署中心 | 企业 | ⭐⭐⭐ | 100+ |
| 5. 多 Profile 并行 | 多项目开发者 | ⭐ | 1 |
| 6. CI/CD 集成 | 自动化 | ⭐⭐ | 整个团队 |
| 7. Harness 中台 | 大型组织 | ⭐⭐⭐⭐ | 500+ |
| 8. Cordis 核心 | 源码研究者 | ⭐⭐⭐⭐⭐ | — |

## 🛣️ 演进路径

```
Phase 1: 架构 1（CLI）           → 5 分钟
Phase 2: 架构 2（Web UI）        → 5 分钟
Phase 3: 架构 5（多 Profile）    → 1 小时
Phase 4: 架构 3（团队共享）      → 1 天
Phase 5: 架构 6（CI 集成）       → 1 周
Phase 6: 架构 4（自部署中心）    → 1-2 月
Phase 7: 架构 7（中台化）        → 3-6 月
```

## 📚 关键参考

| 资源 | 链接 |
|---|---|
| 仓库 | github.com/deepseek-ai/deepseek-harness |
| 架构概览 | harness.directory/docs/architecture |
| Cordis 框架 | cordis.io |
| 插件开发指南 | harness.directory/docs/plugin-dev |
| 部署手册 | harness.directory/docs/self-host |
| Roadmap | github.com/deepseek-ai/deepseek-harness/issues?q=is%3Aissue+roadmap |
