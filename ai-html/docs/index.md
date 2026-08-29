---

date: 2026-08-15  # date-auto-injected
layout: home

hero:
  name: AI 工程全栈 知识图谱
  text: 系统化学习
  tagline: 主流 AI 工具 · 大模型 · SDK · Agent 框架
  actions:
    - theme: brand
      text: 🧭 学习路径
      link: /path
    - theme: alt
      text: 🌐 知识图谱
      link: /graph
    - theme: alt
      text: 🧠 思维导图
      link: /mindmap
    - theme: alt
      text: 📋 命令速查
      link: /cheatsheet

features:
  - icon: 🧠
    title: 大模型与推理
    details: Claude / GPT / Gemini / DeepSeek / Llama / Mistral / 选型
    link: /01-models/claude
    linkText: 开始看模型 →
  - icon: 🔧
    title: AI 编程工具
    details: Claude Code / Cursor / Copilot / Continue / Aider / 命令速查
    link: /02-coding-tools/claude-code
    linkText: 看 AI 工具 →
  - icon: 📦
    title: SDK 接入
    details: Claude / OpenAI / Gemini SDK · LangChain · LlamaIndex
    link: /03-sdks/claude-sdk
    linkText: 看 SDK →
  - icon: 🏗️
    title: Agent 框架
    details: LangGraph · CrewAI · AutoGen · Dify · Coze
    link: /04-agents/langgraph
    linkText: 看 Agent →
  - icon: 🔍
    title: RAG 架构
    details: RAG 模式 · 向量库 · Embedding · 召回 / 重排
    link: /05-rag/patterns
    linkText: 看 RAG →
  - icon: 🔌
    title: MCP 协议
    details: Model Context Protocol · Server / Client 开发 · Codex MCP
    link: /06-mcp/core
    linkText: 看 MCP →
  - icon: 📝
    title: Prompt 工程
    details: CoT · ToT · 结构化 Prompt · Few-shot
    link: /07-prompt/cot
    linkText: 看 Prompt →
  - icon: 🎯
    title: 微调与训练
    details: LoRA · QLoRA · 全量微调 · 数据准备 · 量化
    link: /08-finetuning/lora
    linkText: 看微调 →
  - icon: 📊
    title: 评测与质量
    details: Eval 框架 · Benchmark · RLHF · DPO
    link: /09-eval/frameworks
    linkText: 看评测 →
  - icon: 🏗️
    title: 部署与推理
    details: Ollama / vLLM / TGI / Together / Replicate
    link: /10-deploy/ollama
    linkText: 看部署 →
  - icon: 📡
    title: 工具调用
    details: Function Calling · Tool use · Structured Output
    link: /11-tools/function-calling
    linkText: 看 Tools →
  - icon: 🛠️
    title: 安装与环境
    details: pip / brew / npm / Docker / CUDA / GPU
    link: /12-install/package-managers
    linkText: 看安装 →
  - icon: 🔒
    title: 安全与治理
    details: API Key · Guardrails · 成本控制 · 内容安全
    link: /13-security/api-keys
    linkText: 看安全 →
  - icon: 🎯
    title: 面试与学习
    details: 高频题 · 项目案例 · 学习路径
    link: /14-interview/questions
    linkText: 看面试 →


---


<script setup>
// WhyThisGraph 数据：原写在 :prop="..." 里会触发 Vue 编译错误（多行 YAML 数组），
// 改为 script setup 形式。
const painPoints = [
      "Claude / GPT / Gemini / DeepSeek 到底选哪个？",
      "Claude Code / Codex / Cursor / Copilot / Aider 怎么用？",
      "Claude SDK / OpenAI SDK / LangChain / LangGraph 关系？",
      "Agent / RAG / MCP / Function Calling 是什么关系？",
      "LoRA / QLoRA / GGUF 怎么微调 / 量化？"
    ]
const goals = [
      "主流大模型横向对比 + 选型",
      "AI 编程工具安装 + 命令速查",
      "SDK / Agent 框架生态",
      "RAG / MCP / Tool use 原理",
      "微调 / 部署 / 评测",
      "工程化（API Key / 成本 / 容器化）"
    ]
const relatedSites = [
      { site: "architecture", path: "/01-distributed/cap", label: "分布式 CAP" },
      { site: "bigdata", path: "/06-warehouse/overview", label: "数仓架构" },
      { site: "cloud-native", path: "/05-observability/prometheus", label: "AI 部署监控" },
      { site: "observability", path: "/03-otel/overview", label: "AI 可观测性" }
    ]
</script>

<ClientOnly>
  <WhyThisGraph
    :pain-points="painPoints"
    :goals="goals"
    :related-sites="relatedSites"
    title="🎯 为什么写这个图谱？"
  />
</ClientOnly>
## 🎯 学习路径

```
🧠 模型    →  Claude / GPT / Gemini / 开源模型 横向对比
🔧 工具    →  Claude Code / Cursor / Copilot 安装与命令
📦 SDK     →  Claude SDK / OpenAI / LangChain 快速接入
🏗️ Agent  →  LangGraph / CrewAI / AutoGen 选型
🔍 RAG    →  模式 + 向量库 + Embedding
🔌 MCP    →  协议 + 服务端开发
🎯 实战    →  微调 / 部署 / 评测 / 成本 / 面试
```

完整路径请看 [📖 学习路径](/path)。


## 💡 学习建议

```
1. 应用开发者  →  模型对比 + AI 编程工具 + SDK 快速接入
2. Agent 开发  →  SDK + Agent 框架 + RAG + MCP
3. 算法工程师  →  微调 + 数据准备 + RLHF
4. 平台 / 部署  →  vLLM / Ollama / 成本 / 监控
5. 求职 / 跳槽  →  高频面试题 + 项目案例
```

<!-- ====== C6 Giscus 评论（PILOT） ======
     部署前请编辑 components/GiscusComment.vue 填入真实 giscus ID。
     验证评论后删除此块，或保留作为永久启用。 -->
<ClientOnly>
  <GiscusComment />
</ClientOnly>

## 📚 相关阅读（跨站导航）

<!-- xlink-injected:do-not-edit -->

按主题跨站推荐：

- [python](https://java-px.bot.cd/python/)：Python AI
- [bigdata](https://java-px.bot.cd/bigdata/)：大数据训练
- [system-design](https://java-px.bot.cd/system-design/)：AI 系统架构
- [observability](https://java-px.bot.cd/observability/)：模型监控
- [python-html](https://java-px.bot.cd/python-html/)：Python 工具链
