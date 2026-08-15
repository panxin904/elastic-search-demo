<template>
  <div class="mindmap-container">
    <div ref="chartRef" :style="{ width: '100%', height: height + 'px' }"></div>
    <div class="mm-toolbar">
      <button class="mm-toolbar__btn" @click="expandAll">📖 全部展开</button>
      <button class="mm-toolbar__btn" @click="collapseAll">📕 全部收起</button>
      <button class="mm-toolbar__btn" @click="resetView">🎯 重置视图</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts/core'
import { TreeChart } from 'echarts/charts'
import { TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([TreeChart, TooltipComponent, CanvasRenderer])
const props = defineProps({ height: { type: Number, default: 940 } })
const chartRef = ref(null)
let chart = null

const mindMapData = {
  name: 'AI 工程全栈',
  symbolSize: 30,
  itemStyle: { color: '#1f2937' },
  children: [
    {
      name: '🧠 大模型与推理', itemStyle: { color: '#8b5cf6' },
      children: [
        { name: 'Claude 模型家族', link: '/01-models/claude' },
        { name: 'GPT / OpenAI', link: '/01-models/gpt' },
        { name: 'Gemini', link: '/01-models/gemini' },
        { name: 'DeepSeek', link: '/01-models/deepseek' },
        { name: '开源模型 Llama / Mistral', link: '/01-models/open-source' },
        { name: '模型对比与选型', link: '/01-models/compare' }
      ]
    },
    {
      name: '🔧 AI 编程工具', itemStyle: { color: '#06b6d4' },
      children: [
        { name: 'Claude Code / OpenCode', link: '/02-coding-tools/claude-code' },
        { name: 'Cursor IDE', link: '/02-coding-tools/cursor' },
        { name: 'GitHub Copilot', link: '/02-coding-tools/copilot' },
        { name: 'Continue / Cody', link: '/02-coding-tools/continue-cody' },
        { name: 'Aider', link: '/02-coding-tools/aider' },
        { name: '命令行速查', link: '/02-coding-tools/commands' }
      ]
    },
    {
      name: '📦 SDK 接入', itemStyle: { color: '#f59e0b' },
      children: [
        { name: 'Claude SDK / Anthropic', link: '/03-sdks/claude-sdk' },
        { name: 'OpenAI SDK', link: '/03-sdks/openai-sdk' },
        { name: 'Gemini / Vertex AI SDK', link: '/03-sdks/gemini-sdk' },
        { name: 'LangChain', link: '/03-sdks/langchain' },
        { name: 'LlamaIndex', link: '/03-sdks/llamaindex' }
      ]
    },
    {
      name: '🏗️ Agent 框架', itemStyle: { color: '#10b981' },
      children: [
        { name: 'LangGraph', link: '/04-agents/langgraph' },
        { name: 'CrewAI', link: '/04-agents/crewai' },
        { name: 'AutoGen / Semantic Kernel', link: '/04-agents/autogen' },
        { name: 'Dify / Coze', link: '/04-agents/dify-coze' }
      ]
    },
    {
      name: '🔍 RAG 架构', itemStyle: { color: '#ec4899' },
      children: [
        { name: 'RAG 模式详解', link: '/05-rag/patterns' },
        { name: '向量数据库 Pinecone / Chroma', link: '/05-rag/vector-db' },
        { name: '嵌入模型 Embedding', link: '/05-rag/embedding' }
      ]
    },
    {
      name: '🔌 MCP 协议', itemStyle: { color: '#ef4444' },
      children: [
        { name: 'MCP 核心概念', link: '/06-mcp/core' },
        { name: 'MCP Server / Client 开发', link: '/06-mcp/dev' },
        { name: 'Codex MCP 集成', link: '/06-mcp/codex-integration' }
      ]
    },
    {
      name: '📝 Prompt 工程', itemStyle: { color: '#6366f1' },
      children: [
        { name: 'Chain-of-Thought CoT', link: '/07-prompt/cot' },
        { name: '结构化 Prompt / 系统提示词', link: '/07-prompt/structured' },
        { name: 'Few-shot / Multi-shot', link: '/07-prompt/few-shot' }
      ]
    },
    {
      name: '🎯 微调与训练', itemStyle: { color: '#d946ef' },
      children: [
        { name: 'LoRA / QLoRA', link: '/08-finetuning/lora' },
        { name: '全量微调', link: '/08-finetuning/full' },
        { name: '数据准备', link: '/08-finetuning/data' },
        { name: '量化 GGUF / GPTQ', link: '/08-finetuning/quantization' }
      ]
    },
    {
      name: '📊 评测与质量', itemStyle: { color: '#14b8a6' },
      children: [
        { name: 'Eval 框架', link: '/09-eval/frameworks' },
        { name: 'Benchmark 与指标', link: '/09-eval/benchmark' },
        { name: 'RLHF / DPO', link: '/09-eval/alignment' }
      ]
    },
    {
      name: '🏗️ 部署与推理', itemStyle: { color: '#f97316' },
      children: [
        { name: 'Ollama 本地推理', link: '/10-deploy/ollama' },
        { name: 'vLLM / TGI 服务', link: '/10-deploy/vllm-tgi' },
        { name: 'API 托管 / Together / Replicate', link: '/10-deploy/hosted' }
      ]
    },
    {
      name: '📡 工具调用', itemStyle: { color: '#84cc16' },
      children: [
        { name: 'Function Calling', link: '/11-tools/function-calling' },
        { name: 'Tool Use 模式', link: '/11-tools/tool-use' },
        { name: 'Structured Output', link: '/11-tools/structured-output' }
      ]
    },
    {
      name: '🛠️ 安装与环境', itemStyle: { color: '#0ea5e9' },
      children: [
        { name: 'pip / brew / npm 安装', link: '/12-install/package-managers' },
        { name: 'Docker 一键部署', link: '/12-install/docker' },
        { name: 'CUDA / GPU 环境', link: '/12-install/cuda-gpu' }
      ]
    },
    {
      name: '🔒 安全与治理', itemStyle: { color: '#78716c' },
      children: [
        { name: 'API Key 管理', link: '/13-security/api-keys' },
        { name: 'Guardrails / Content Safety', link: '/13-security/guardrails' },
        { name: '成本控制 / Token 管理', link: '/13-security/cost' }
      ]
    },
    {
      name: '🎯 面试与学习', itemStyle: { color: '#a855f7' },
      children: [
        { name: '高频面试题', link: '/14-interview/questions' },
        { name: '项目案例', link: '/14-interview/cases' },
        { name: '学习路径', link: '/14-interview/path' }
      ]
    }
  ]
}

function renderChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value, undefined, { renderer: 'canvas' })
  chart.setOption({
    tooltip: { trigger: 'item', triggerOn: 'mousemove', formatter: (p) => p.data?.link ? `<b>${p.name}</b><br/>点击跳转` : p.name },
    series: [{
      type: 'tree', data: [mindMapData], top: '5%', left: '8%', bottom: '5%', right: '20%',
      symbolSize: 14, orient: 'LR', expandAndCollapse: true, initialTreeDepth: 2,
      label: { position: 'left', verticalAlign: 'middle', align: 'right', fontSize: 13, color: 'var(--vp-c-text-1, #333)' },
      leaves: { label: { position: 'right', verticalAlign: 'middle', align: 'left' } },
      emphasis: { focus: 'descendant' }, animationDuration: 550, animationDurationUpdate: 750,
      lineStyle: { color: '#aaa', width: 1, curveness: 0.05 }
    }]
  })
  chart.on('click', (params) => { if (params.data?.link) window.location.href = params.data.link })
}
function expandAll() {
  if (!chart) return
  const traverse = (node, depth) => {
    if (depth > 0 && node.children) chart.dispatchAction({ type: 'treeExpandAndCollapse', data: node, seriesIndex: 0 })
    if (node.children) node.children.forEach(c => traverse(c, depth + 1))
  }
  traverse(mindMapData, 0)
}
function collapseAll() { const traverse = (node) => { if (node.children) { node.children.forEach(c => { chart.dispatchAction({ type: 'treeExpandAndCollapse', data: c, seriesIndex: 0 }); traverse(c) }) } }; traverse(mindMapData) }
function resetView() { if (chart) chart.dispatchAction({ type: 'restore' }) }
onMounted(() => { renderChart(); window.addEventListener('resize', () => chart?.resize()) })
onBeforeUnmount(() => { chart?.dispose(); chart = null })
</script>