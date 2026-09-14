---
title: DeepSeek Harness 学习文档
date: 2026-09-14  # date-auto-injected
---

# 🎓 DeepSeek Harness 学习文档

> **DeepSeek Harness** 是 DeepSeek-AI 于 2026 年 8 月 13 日开源发布的 **AI Agent 运行时框架**，对标 Anthropic 的 Claude Code、Cursor Agent。本章系统学习它的设计理念、架构、4 种内置模式，以及和同类工具的对比。

## 🧭 它是什么

```
┌─────────────────────────────────────────────────┐
│              DeepSeek Harness 是什么？           │
├─────────────────────────────────────────────────┤
│                                                  │
│  ❌ 不是模型（V3 / R1 才是模型）                  │
│  ❌ 不是推理框架（vLLM / SGLang 才是）            │
│  ✅ 是 Agent 运行时（类似 Claude Code / Gemini CLI）│
│                                                  │
│  - 本地运行的 AI Agent                          │
│  - 内置工具集（文件、Shell、搜索、Skills、子代理）│
│  - 插件化架构（Everything is a Plugin）         │
│  - 4 种内置模式 + 多 Profile 并行                │
│  - 开源 MIT / TypeScript / Node.js 22+         │
│  - 一行启动：npx @deepseek-ai/dsh web           │
│                                                  │
└─────────────────────────────────────────────────┘
```

## 📊 关键事实

| 维度 | 数据 |
|---|---|
| GitHub | github.com/deepseek-ai/deepseek-harness |
| Star 数 | 21 万+（发布首周） |
| 当前版本 | v0.1.2-rc.1（Developer Preview） |
| License | MIT |
| 发布日期 | 2026-08-13 |
| 主语言 | TypeScript (99.8%) |
| 运行时 | Node.js ^22.19.0 |
| 包管理 | pnpm (workspaces) |
| 构建 | esbuild |
| 文档站 | VitePress |
| 测试 | Vitest + Playwright |
| CLI 命令 | `dsh` |
| npm 包 | `@deepseek-ai/dsh` |
| 默认 Web UI 端口 | 3080 |

## 🏛️ 核心理念：Everything is a Plugin

Harness 基于 [Cordis](https://github.com/cordiverse/cordis) 框架（Cordis 团队与 Harness 团队深度合作）。所有能力（模型、工具、技能、UI、服务）都是**插件**：

```
┌─────────────────────────────────────────────────┐
│  Harness Core（Cordis 容器）                     │
│  - 插件加载 / 依赖注入 / 事件总线                │
├─────────────────────────────────────────────────┤
│  官方插件（内置）                                │
│  ├ @harness/model-*    模型适配器（OpenAI/Anthropic）│
│  ├ @harness/tool-*     工具（文件编辑/Shell/搜索）   │
│  ├ @harness/skill-*    Skills（Git/Review/Refactor） │
│  ├ @harness/server     Web UI 后端                │
│  ├ @harness/web        Web UI 前端                │
│  └ @harness/cli        命令行入口                 │
├─────────────────────────────────────────────────┤
│  社区插件（npm tag: dsh-plugin）                │
│  - 用户 / 第三方贡献                              │
└─────────────────────────────────────────────────┘
```

**好处**：
- ✅ 任何能力都可插拔（不需要的功能直接禁用）
- ✅ 第三方可发布 npm 包即装即用
- ✅ 升级核心不影响业务插件
- ✅ 测试友好（每个插件独立可测）

## 🎯 4 种内置模式

| 模式 | 触发 | 适用 |
|---|---|---|
| **标准模式 (Standard)** | `dsh` 不带参数 或 `--mode standard` | 日常开发任务（默认） |
| **PTC 模式 (Programmatic Tool Calling)** | `--mode ptc` | 用 TypeScript 代码编排多步工具调用 |
| **极简模式 (Minimal)** | `--mode minimal` | 只需 bash + str_replace_editor，类似 Claude Code early version |
| **创造模式 (Creative)** | `--mode creative` | 探索性编程、自动尝试多种方案 |

### 模式对比示例：实现一个 HTTP 客户端

```
标准模式：
  用户："写一个 HTTP 客户端处理 JSON"
  Agent → 自动调用 read_file/write_file/edit 工具 → 完成

PTC 模式：
  用户："用 PTC 模式写 HTTP 客户端"
  Agent → 生成 TypeScript 编排代码：
    ```typescript
    await writeFile('client.ts', generateClient())
    await runCmd('npm install axios')
    await runCmd('npm run build')
    ```
  一次性产出完整流程

极简模式：
  用户："写 HTTP 客户端"
  Agent → 直接用 bash + edit 工具 → 完成
  （无 Skills / Subagent）

创造模式：
  用户："写 HTTP 客户端，多试几种方案选最优"
  Agent → 自动生成 axios/fetch/ky 三种实现 → 跑基准测试 → 推荐最快
```

## 🔄 与同类工具对比

| 维度 | DeepSeek Harness | Claude Code | Cursor Agent | Gemini CLI | Codex CLI |
|---|---|---|---|---|---|
| 厂商 | DeepSeek-AI | Anthropic | Anysphere | Google | OpenAI |
| 开源 | ✅ MIT | ❌ 闭源 | ❌ 闭源 | ✅ Apache | ❌ 闭源 |
| 本地运行 | ✅ | ✅ | ❌ | ✅ | ✅ |
| 模型选择 | 任意 OpenAI 兼容 | 仅 Claude | 自家 + 接入 | Gemini | OpenAI |
| 插件架构 | ✅ Cordis | ❌ | ❌ | ✅ | ❌ |
| Skills 系统 | ✅ | ✅ | ❌ | ✅ | ✅ |
| 子代理 | ✅ | ✅ | ✅ | ✅ | ✅ |
| Web UI | ✅ 内置 | ❌ | ✅ | ❌ | ❌ |
| MCP 支持 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 工作目录 | 当前项目 | 当前项目 | 项目根 | 当前项目 | 当前项目 |

## 📦 仓库结构（重要）

```
deepseek-harness/
├─ packages/
│   ├─ core/             # @harness/core（Cordis 容器 + 插件加载）
│   ├─ server/           # @harness/server（Web UI 后端，Fastify）
│   ├─ web/              # @harness/web（Web UI 前端，Vite + Vue）
│   ├─ cli/              # @harness/cli（dsh 命令）
│   ├─ config/           # @harness/config（配置文件 schema）
│   ├─ utils/            # @harness/utils
│   ├─ tools/            # @harness/tool-*（文件/Shell/搜索工具）
│   ├─ skills/           # @harness/skill-*（Git/Review/Refactor Skills）
│   └─ models/           # @harness/model-*（OpenAI/Anthropic 适配）
├─ docs/                 # VitePress 文档站
├─ tests/                # Vitest 单元 + Playwright e2e
├─ presets/              # 内置模式预设（standard/ptc/minimal/creative）
├─ examples/             # 示例插件
├─ package.json          # pnpm workspaces 根
├─ pnpm-workspace.yaml
└─ README.md
```

## 🧠 学习路径推荐

```
🟢 第 1 阶段：上手（1 小时）
   1. npx @deepseek-ai/dsh web → 看 Web UI
   2. 让 Harness 改一个 README.md
   3. 试试不同模型（V3 / R1 / Qwen / Claude）

🟡 第 2 阶段：配置（半天）
   4. 读 ~/.config/dsh/config.yaml
   5. 切 Profile（不同项目用不同模型）
   6. 装一个官方 Skills 试试

🟠 第 3 阶段：定制（1-2 天）
   7. 写第一个自定义 Skill
   8. 调权限/沙箱策略
   9. 用 PTC 模式自动化工作流

🔴 第 4 阶段：插件开发（3-5 天）
   10. 看 packages/core 源码（理解 Cordis）
   11. 写一个 @harness/plugin-* 发布到 npm
   12. 提交 PR 到 deepseek-ai/deepseek-harness
```

## 🔍 设计哲学

```
┌────────────────────────────────────────────┐
│  "Harness 不是一个 chatbot，               │
│   而是 Agent 在本地开发环境的运行时"          │
│   ── DeepSeek 官方 README                  │
└────────────────────────────────────────────┘

设计原则（来自 deepseek-harness CONTRIBUTING.md）：

1. Everything is a Plugin
   → 任何能力都可拔插，方便扩展和裁剪

2. Local-first
   → 所有状态本地保存，零云端依赖
   → ~/.config/dsh/ + ~/.local/share/dsh/

3. OpenAI-compatible by default
   → 默认适配 OpenAI 协议（DeepSeek/Moonshot/Qwen/Grok 都用这个）
   → Anthropic / Gemini 走独立适配器

4. Sandbox-by-default, Permission-by-explicit
   → 默认所有操作进沙箱
   → 危险操作需用户显式确认

5. Test-driven Plugins
   → 每个插件必须带 Vitest 测试 + Playwright e2e
```

## 🚧 当前限制（v0.1.2-rc.1）

```
⚠️ Developer Preview 阶段，以下能力尚未完整：

- [ ] Windows 原生支持（当前依赖 WSL2）
- [ ] 多语言模型微调接入
- [ ] 团队协作 / 共享会话
- [ ] 移动端 UI（只有 Web + CLI）
- [ ] 完整的离线模式（部分功能仍需联网）
- [ ] 国际化（当前 UI 仅中英双语）
```

## 📚 关键资源

| 资源 | 链接 |
|---|---|
| 官方仓库 | github.com/deepseek-ai/deepseek-harness |
| 官方文档 | harness.directory（待上线） |
| DeepSeek 主页 | deepseek.com/harness |
| npm 包 | npmjs.com/package/@deepseek-ai/dsh |
| 插件索引 | github.com/topics/dsh-plugin |
| Discord | discord.gg/deepseek |
| 路线图 | github.com/deepseek-ai/deepseek-harness/issues?q=roadmap |
