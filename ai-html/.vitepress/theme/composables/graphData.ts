// ai-html graph data
// 节点分类：models / coding / sdks / agents / rag / mcp / prompt / finetuning / eval / deploy / tools / install / security / interview

export const graphData = {
  nodes: [
    // 01 模型
    { name: 'Claude 模型家族', category: 'models', link: '/01-models/claude', value: 7 },
    { name: 'GPT / OpenAI', category: 'models', link: '/01-models/gpt', value: 6 },
    { name: 'Gemini', category: 'models', link: '/01-models/gemini', value: 5 },
    { name: 'DeepSeek', category: 'models', link: '/01-models/deepseek', value: 5 },
    { name: '开源模型 Llama / Mistral', category: 'models', link: '/01-models/open-source', value: 5 },
    { name: '模型对比与选型', category: 'models', link: '/01-models/compare', value: 5 },

    // 02 Coding 工具
    { name: 'Claude Code / OpenCode', category: 'coding', link: '/02-coding-tools/claude-code', value: 8 },
    { name: 'Cursor IDE', category: 'coding', link: '/02-coding-tools/cursor', value: 7 },
    { name: 'GitHub Copilot', category: 'coding', link: '/02-coding-tools/copilot', value: 7 },
    { name: 'Continue / Cody', category: 'coding', link: '/02-coding-tools/continue-cody', value: 5 },
    { name: 'Aider', category: 'coding', link: '/02-coding-tools/aider', value: 5 },
    { name: '命令行速查', category: 'coding', link: '/02-coding-tools/commands', value: 5 },

    // 03 SDK
    { name: 'Claude SDK / Anthropic', category: 'sdks', link: '/03-sdks/claude-sdk', value: 7 },
    { name: 'OpenAI SDK', category: 'sdks', link: '/03-sdks/openai-sdk', value: 7 },
    { name: 'Gemini / Vertex AI SDK', category: 'sdks', link: '/03-sdks/gemini-sdk', value: 5 },
    { name: 'LangChain', category: 'sdks', link: '/03-sdks/langchain', value: 6 },
    { name: 'LlamaIndex', category: 'sdks', link: '/03-sdks/llamaindex', value: 5 },

    // 04 Agent
    { name: 'LangGraph', category: 'agents', link: '/04-agents/langgraph', value: 7 },
    { name: 'CrewAI', category: 'agents', link: '/04-agents/crewai', value: 6 },
    { name: 'AutoGen / Semantic Kernel', category: 'agents', link: '/04-agents/autogen', value: 6 },
    { name: 'Dify / Coze', category: 'agents', link: '/04-agents/dify-coze', value: 5 },

    // 05 RAG
    { name: 'RAG 模式详解', category: 'rag', link: '/05-rag/patterns', value: 6 },
    { name: '向量数据库', category: 'rag', link: '/05-rag/vector-db', value: 6 },
    { name: '嵌入模型 Embedding', category: 'rag', link: '/05-rag/embedding', value: 5 },

    // 06 MCP
    { name: 'MCP 核心概念', category: 'mcp', link: '/06-mcp/core', value: 6 },
    { name: 'MCP Server / Client 开发', category: 'mcp', link: '/06-mcp/dev', value: 6 },
    { name: 'Codex MCP 集成', category: 'mcp', link: '/06-mcp/codex-integration', value: 5 },

    // 07 Prompt
    { name: 'Chain-of-Thought', category: 'prompt', link: '/07-prompt/cot', value: 6 },
    { name: '结构化 Prompt', category: 'prompt', link: '/07-prompt/structured', value: 6 },
    { name: 'Few-shot / Multi-shot', category: 'prompt', link: '/07-prompt/few-shot', value: 5 },

    // 08 微调
    { name: 'LoRA / QLoRA', category: 'finetuning', link: '/08-finetuning/lora', value: 6 },
    { name: '全量微调', category: 'finetuning', link: '/08-finetuning/full', value: 5 },
    { name: '数据准备', category: 'finetuning', link: '/08-finetuning/data', value: 5 },
    { name: '量化 GGUF / GPTQ', category: 'finetuning', link: '/08-finetuning/quantization', value: 5 },

    // 09 评测
    { name: 'Eval 框架', category: 'eval', link: '/09-eval/frameworks', value: 6 },
    { name: 'Benchmark 与指标', category: 'eval', link: '/09-eval/benchmark', value: 5 },
    { name: 'RLHF / DPO', category: 'eval', link: '/09-eval/alignment', value: 5 },

    // 10 部署
    { name: 'Ollama 本地推理', category: 'deploy', link: '/10-deploy/ollama', value: 6 },
    { name: 'vLLM / TGI 服务', category: 'deploy', link: '/10-deploy/vllm-tgi', value: 6 },
    { name: 'API 托管', category: 'deploy', link: '/10-deploy/hosted', value: 5 },

    // 11 工具调用
    { name: 'Function Calling', category: 'tools', link: '/11-tools/function-calling', value: 7 },
    { name: 'Tool Use 模式', category: 'tools', link: '/11-tools/tool-use', value: 6 },
    { name: 'Structured Output', category: 'tools', link: '/11-tools/structured-output', value: 6 },

    // 12 安装
    { name: 'pip / brew / npm 安装', category: 'install', link: '/12-install/package-managers', value: 5 },
    { name: 'Docker 一键部署', category: 'install', link: '/12-install/docker', value: 5 },
    { name: 'CUDA / GPU 环境', category: 'install', link: '/12-install/cuda-gpu', value: 5 },

    // 13 安全
    { name: 'API Key 管理', category: 'security', link: '/13-security/api-keys', value: 5 },
    { name: 'Guardrails / Content Safety', category: 'security', link: '/13-security/guardrails', value: 5 },
    { name: '成本控制 / Token', category: 'security', link: '/13-security/cost', value: 5 },

    // 14 面试
    { name: '高频面试题', category: 'interview', link: '/14-interview/questions', value: 5 },
    { name: '项目案例', category: 'interview', link: '/14-interview/cases', value: 4 },
    { name: '学习路径', category: 'interview', link: '/14-interview/path', value: 4 }
  ],

  links: [
    // 01 模型 → 02/03/04
    { source: 'Claude 模型家族', target: 'Claude SDK / Anthropic' },
    { source: 'GPT / OpenAI', target: 'OpenAI SDK' },
    { source: 'Gemini', target: 'Gemini / Vertex AI SDK' },
    { source: 'DeepSeek', target: '开源模型 Llama / Mistral' },
    { source: '开源模型 Llama / Mistral', target: 'Ollama 本地推理' },
    { source: '模型对比与选型', target: 'Claude 模型家族' },
    { source: '模型对比与选型', target: 'GPT / OpenAI' },
    { source: '模型对比与选型', target: 'Gemini' },

    // 02 编程工具 → 01/03
    { source: 'Claude Code / OpenCode', target: 'Claude SDK / Anthropic' },
    { source: 'Cursor IDE', target: 'Claude 模型家族' },
    { source: 'GitHub Copilot', target: 'GPT / OpenAI' },
    { source: 'Continue / Cody', target: 'LangChain' },
    { source: 'Aider', target: 'Claude SDK / Anthropic' },
    { source: '命令行速查', target: 'Claude Code / OpenCode' },

    // 03 SDK → 04
    { source: 'LangChain', target: 'LangGraph' },
    { source: 'Claude SDK / Anthropic', target: 'MCP 核心概念' },
    { source: 'OpenAI SDK', target: 'Function Calling' },
    { source: 'LangChain', target: 'Function Calling' },
    { source: 'LlamaIndex', target: 'RAG 模式详解' },
    { source: 'Gemini / Vertex AI SDK', target: 'Function Calling' },

    // 04 Agent
    { source: 'LangGraph', target: 'MCP 核心概念' },
    { source: 'CrewAI', target: 'MCP 核心概念' },
    { source: 'Dify / Coze', target: 'RAG 模式详解' },
    { source: 'Dify / Coze', target: 'Claude 模型家族' },

    // 05 RAG
    { source: 'RAG 模式详解', target: '向量数据库' },
    { source: 'RAG 模式详解', target: '嵌入模型 Embedding' },
    { source: '向量数据库', target: '嵌入模型 Embedding' },

    // 06 MCP
    { source: 'MCP Server / Client 开发', target: 'Codex MCP 集成' },
    { source: 'Codex MCP 集成', target: 'Claude Code / OpenCode' },
    { source: 'MCP 核心概念', target: 'Claude Code / OpenCode' },

    // 07 Prompt
    { source: 'Chain-of-Thought', target: 'Tool Use 模式' },
    { source: '结构化 Prompt', target: 'Structured Output' },
    { source: 'Few-shot / Multi-shot', target: 'Function Calling' },

    // 08 微调
    { source: 'LoRA / QLoRA', target: '数据准备' },
    { source: 'LoRA / QLoRA', target: '量化 GGUF / GPTQ' },
    { source: '全量微调', target: 'LoRA / QLoRA' },

    // 09 评测
    { source: 'Eval 框架', target: 'RLHF / DPO' },
    { source: 'Benchmark 与指标', target: 'Eval 框架' },
    { source: 'RLHF / DPO', target: '全量微调' },

    // 10 部署
    { source: 'Ollama 本地推理', target: 'Claude SDK / Anthropic' },
    { source: 'vLLM / TGI 服务', target: 'Ollama 本地推理' },
    { source: 'API 托管', target: 'Ollama 本地推理' },
    { source: 'vLLM / TGI 服务', target: '模型对比与选型' },

    // 11 工具调用
    { source: 'Tool Use 模式', target: 'Function Calling' },
    { source: 'Structured Output', target: 'Function Calling' },
    { source: 'Function Calling', target: 'MCP 核心概念' },

    // 12 安装
    { source: 'pip / brew / npm 安装', target: 'Claude SDK / Anthropic' },
    { source: 'Docker 一键部署', target: 'Ollama 本地推理' },
    { source: 'Docker 一键部署', target: 'vLLM / TGI 服务' },
    { source: 'CUDA / GPU 环境', target: 'Ollama 本地推理' },

    // 13 安全
    { source: 'API Key 管理', target: '成本控制 / Token' },
    { source: 'Guardrails / Content Safety', target: '结构化 Prompt' },

    // 14 面试
    { source: '高频面试题', target: 'RAG 模式详解' },
    { source: '项目案例', target: 'LangGraph' }
  ]
}