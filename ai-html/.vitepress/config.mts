import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

export default withMermaid(defineConfig({
  mermaid: {
    theme: 'default'
  },
  base: '/ai/',
  title: 'AI 工具 / 大模型 / Agent 知识图谱',
  description: '系统化学习 AI 工具、主流大模型、SDK 与 Agent 框架 - 14 大类 · 80+ 节点 · 60+ 内容页',
  lang: 'zh-CN',
  lastUpdated: true,
  srcDir: 'docs',
  cleanUrls: true,
  head: [
    ['link', { rel: 'apple-touch-icon', href: '/apple-touch-icon.png', sizes: '180x180' }],
    ['link', { rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' }],
    ['link', { rel: 'icon', href: '/favicon.ico', type: 'image/x-icon' }],
    ['meta', { name: 'theme-color', content: '#8b5cf6' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:locale', content: 'zh_CN' }]  ],
  themeConfig: {
    siteTitle: 'AI 工程全栈',
    nav: [

      { text: '🏠 门户', link: 'https://java-px.bot.cd/', target: '_blank' },
{ text: '首页', link: '/' },
      { text: '知识图谱', link: '/graph' },
      { text: '思维导图', link: '/mindmap' },
      { text: '命令速查', link: '/cheatsheet' },
      { text: '学习路径', link: '/path' },
      {
        text: '更多站点',
        items: [
        { text: '企业级架构', link: 'https://java-px.bot.cd/architecture/' },
        { text: '大数据', link: 'https://java-px.bot.cd/bigdata/' },
        { text: '云原生 / Docker / K8s', link: 'https://java-px.bot.cd/cloud-native/' },
        { text: 'ElasticSearch', link: 'https://java-px.bot.cd/es/' },
        { text: '前端 & Node', link: 'https://java-px.bot.cd/frontend/' },
        { text: 'Java 语言', link: 'https://java-px.bot.cd/java-language/' },
        { text: 'Java Web 开发', link: 'https://java-px.bot.cd/java/' },
        { text: 'Kafka', link: 'https://java-px.bot.cd/kafka/' },
        { text: 'Linux 服务器', link: 'https://java-px.bot.cd/linux/' },
        { text: 'MySQL', link: 'https://java-px.bot.cd/mysql/' },
        { text: 'Python', link: 'https://java-px.bot.cd/python/' },
        { text: 'Redis', link: 'https://java-px.bot.cd/redis/' },
        { text: '微服务 / Spring Cloud', link: 'https://java-px.bot.cd/cloud/' },
        { text: '计算机网络', link: 'https://java-px.bot.cd/network/' },
        { text: '文件系统与存储', link: 'https://java-px.bot.cd/filesystem/' },
        { text: '在线工具', link: 'https://java-px.bot.cd/tools/' },
        { text: '视频处理', link: 'https://java-px.bot.cd/video/' }
      ]
      }
    ],
    sidebar: {
      '/': [
        { text: '🎯 开始', items: [{ text: '📖 学习路径', link: '/path' }] },
        {
          text: '🧠 大模型与推理', items: [
            { text: 'Claude 模型家族', link: '/01-models/claude' },
            { text: 'GPT / OpenAI', link: '/01-models/gpt' },
            { text: 'Gemini', link: '/01-models/gemini' },
            { text: 'DeepSeek', link: '/01-models/deepseek' },
            { text: '开源模型 Llama / Mistral', link: '/01-models/open-source' },
            { text: '模型对比与选型', link: '/01-models/compare' }
          ]
        },
        {
          text: '🔧 AI 编程工具', items: [
            { text: 'Claude Code / OpenCode', link: '/02-coding-tools/claude-code' },
            { text: 'Cursor IDE', link: '/02-coding-tools/cursor' },
            { text: 'GitHub Copilot', link: '/02-coding-tools/copilot' },
            { text: 'Continue / Cody', link: '/02-coding-tools/continue-cody' },
            { text: 'Aider', link: '/02-coding-tools/aider' },
            { text: '命令行速查', link: '/02-coding-tools/commands' }
          ]
        },
        {
          text: '📦 SDK 接入', items: [
            { text: 'Claude SDK / Anthropic', link: '/03-sdks/claude-sdk' },
            { text: 'OpenAI SDK', link: '/03-sdks/openai-sdk' },
            { text: 'Gemini / Vertex AI SDK', link: '/03-sdks/gemini-sdk' },
            { text: 'LangChain', link: '/03-sdks/langchain' },
            { text: 'LlamaIndex', link: '/03-sdks/llamaindex' }
          ]
        },
        {
          text: '🏗️ Agent 框架', items: [
            { text: 'LangGraph', link: '/04-agents/langgraph' },
            { text: 'CrewAI', link: '/04-agents/crewai' },
            { text: 'AutoGen / Semantic Kernel', link: '/04-agents/autogen' },
            { text: 'Dify / Coze', link: '/04-agents/dify-coze' }
          ]
        },
        {
          text: '🔍 RAG 架构', items: [
            { text: 'RAG 模式详解', link: '/05-rag/patterns' },
            { text: '向量数据库', link: '/05-rag/vector-db' },
            { text: '嵌入模型 Embedding', link: '/05-rag/embedding' }
          ]
        },
        {
          text: '🔌 MCP 协议', items: [
            { text: 'MCP 核心概念', link: '/06-mcp/core' },
            { text: 'MCP Server / Client 开发', link: '/06-mcp/dev' },
            { text: 'Codex MCP 集成', link: '/06-mcp/codex-integration' }
          ]
        },
        {
          text: '📝 Prompt 工程', items: [
            { text: 'Chain-of-Thought', link: '/07-prompt/cot' },
            { text: '结构化 Prompt', link: '/07-prompt/structured' },
            { text: 'Few-shot / Multi-shot', link: '/07-prompt/few-shot' }
          ]
        },
        {
          text: '🎯 微调与训练', items: [
            { text: 'LoRA / QLoRA', link: '/08-finetuning/lora' },
            { text: '全量微调', link: '/08-finetuning/full' },
            { text: '数据准备', link: '/08-finetuning/data' },
            { text: '量化 GGUF / GPTQ', link: '/08-finetuning/quantization' }
          ]
        },
        {
          text: '📊 评测与质量', items: [
            { text: 'Eval 框架', link: '/09-eval/frameworks' },
            { text: 'Benchmark 与指标', link: '/09-eval/benchmark' },
            { text: 'RLHF / DPO', link: '/09-eval/alignment' }
          ]
        },
        {
          text: '🏗️ 部署与推理', items: [
            { text: 'Ollama 本地推理', link: '/10-deploy/ollama' },
            { text: 'vLLM / TGI 服务', link: '/10-deploy/vllm-tgi' },
            { text: 'API 托管', link: '/10-deploy/hosted' }
          ]
        },
        {
          text: '📡 工具调用', items: [
            { text: 'Function Calling', link: '/11-tools/function-calling' },
            { text: 'Tool Use 模式', link: '/11-tools/tool-use' },
            { text: 'Structured Output', link: '/11-tools/structured-output' }
          ]
        },
        {
          text: '🛠️ 安装与环境', items: [
            { text: 'pip / brew / npm 安装', link: '/12-install/package-managers' },
            { text: 'Docker 一键部署', link: '/12-install/docker' },
            { text: 'CUDA / GPU 环境', link: '/12-install/cuda-gpu' }
          ]
        },
        {
          text: '🔒 安全与治理', items: [
            { text: 'API Key 管理', link: '/13-security/api-keys' },
            { text: 'Guardrails / Content Safety', link: '/13-security/guardrails' },
            { text: '成本控制 / Token', link: '/13-security/cost' }
          ]
        },
        {
          text: '🎯 面试与学习', items: [
            { text: '高频面试题', link: '/14-interview/questions' },
            { text: '项目案例', link: '/14-interview/cases' },
            { text: '学习路径', link: '/14-interview/path' }
          ]
        }
      ],
      '/graph': [{ text: '🌐 知识图谱', items: [{ text: '全局知识图谱', link: '/graph' }] }],
      '/mindmap': [{ text: '🧭 思维导图', items: [{ text: 'AI 思维导图', link: '/mindmap' }] }],
      '/cheatsheet': [{ text: '📋 命令速查', items: [{ text: 'AI 工具命令速查', link: '/cheatsheet' }] }],
      '/path': [{ text: '🎯 学习路径', items: [{ text: 'AI 工程学习路径', link: '/path' }] }]
    },
    socialLinks: [{ icon: 'github', link: 'https://github.com' }],
    footer: {
      message: 'AI 工程全栈 - 工具 / 大模型 / SDK / Agent · 🏠 <a href="https://java-px.bot.cd/" target="_blank">门户首页</a>',
      copyright: 'MIT License'
    },
    outline: { level: [2, 3], label: '页面大纲' },
    docFooter: { prev: '上一篇', next: '下一篇' },

    search: { provider: 'local' },
  }
}))
