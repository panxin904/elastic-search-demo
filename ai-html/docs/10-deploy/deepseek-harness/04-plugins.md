---
title: DeepSeek 常用插件
date: 2026-09-14  # date-auto-injected
---

# 🧩 DeepSeek 常用插件

> IDE / IM / Agent 框架 / 评测工具的 DeepSeek 集成方案。

## 💻 IDE 编程助手

### Cursor

```
1. Cursor → Settings → Models
2. Add Custom Provider:
   - Provider Name: DeepSeek
   - Base URL: https://api.deepseek.com/v1
   - API Key: sk-xxx
3. Available Models:
   - deepseek-chat         (V3.2)
   - deepseek-reasoner     (R1)
4. 设置默认模型为 deepseek-chat
5. 享受 Composer / Tab / Chat 全功能
```

### Cline（VS Code 原生）

```bash
# 1. 安装扩展：Cline (VS Code marketplace)
# 2. Cline → Settings → API Provider → OpenAI Compatible
# 3. 配置：
#    Base URL: https://api.deepseek.com/v1
#    API Key: sk-xxx
#    Model ID: deepseek-chat
# 4. 可选 deepseek-reasoner 用于"Plan"模式
```

### Continue.dev

```yaml
# ~/.continue/config.json
{
  "models": [
    {
      "title": "DeepSeek-V3",
      "provider": "openai",
      "model": "deepseek-chat",
      "apiBase": "https://api.deepseek.com/v1",
      "apiKey": "sk-xxx"
    },
    {
      "title": "DeepSeek-R1",
      "provider": "openai",
      "model": "deepseek-reasoner",
      "apiBase": "https://api.deepseek.com/v1",
      "apiKey": "sk-xxx"
    }
  ],
  "tabAutocompleteModel": {
    "title": "DeepSeek-Coder",
    "provider": "openai",
    "model": "deepseek-coder",
    "apiBase": "https://api.deepseek.com/v1",
    "apiKey": "sk-xxx"
  }
}
```

### Roo Code / Cline Fork

```json
// VS Code settings.json
{
  "roo-cline.apiProvider": "openai",
  "roo-cline.openAiBaseUrl": "https://api.deepseek.com/v1",
  "roo-cline.openAiApiKey": "sk-xxx",
  "roo-cline.openAiModelId": "deepseek-chat"
}
```

## 🗨️ IM / 客户端

### ChatBox（桌面 + 移动端）

```
设置 → 模型提供方 → 添加
  名称：DeepSeek
  API 密钥：sk-xxx
  API 域名：https://api.deepseek.com/v1
  模型：deepseek-chat / deepseek-reasoner
```

### Cherry Studio（国内最流行）

```
设置 → 模型服务 → 添加
  服务商类型：OpenAI 兼容
  API Key: sk-xxx
  API 端点：https://api.deepseek.com/v1
  模型：deepseek-chat, deepseek-reasoner

对话 → 选 DeepSeek 模型
```

### ChatGPT-Next-Web

```bash
docker run -d \
    --name chatgpt-next-web \
    -p 3000:3000 \
    -e BASE_URL=https://api.deepseek.com/v1 \
    -e OPENAI_API_KEY=sk-xxx \
    -e CUSTOM_MODELS=deepseek-chat,deepseek-reasoner \
    yidadaa/chatgpt-next-web
```

### Lobe Chat

```bash
# 环境变量
OPENAI_API_KEY=sk-xxx
OPENAI_PROXY_URL=https://api.deepseek.com/v1
DEFAULT_MODELS=deepseek-chat,deepseek-reasoner
```

### Open WebUI（Ollama 配套）

```bash
# 直接添加 DeepSeek 端点
docker run -d \
    --name open-webui \
    -p 3000:8080 \
    -e OPENAI_API_BASE_URL=https://api.deepseek.com/v1 \
    -e OPENAI_API_KEYS=sk-xxx \
    -e ENABLE_OPENAI_API=True \
    ghcr.io/open-webui/open-webui:main
```

## 🧠 Agent 框架

### LangChain

```python
# 已展示在实战 7
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key="sk-xxx",
    openai_api_base="https://api.deepseek.com/v1"
)
```

### LlamaIndex

```python
from llama_index.llms.openai import OpenAI

llm = OpenAI(
    model="deepseek-chat",
    api_key="sk-xxx",
    api_base="https://api.deepseek.com/v1"
)
```

### Dify（低代码 Agent 平台）

```
1. https://dify.ai 创建工作流
2. 添加模型 → OpenAI 兼容 API
   - API Key: sk-xxx
   - API Endpoint: https://api.deepseek.com/v1
3. 在"模型供应商"添加：
   - deepseek-chat (V3.2)
   - deepseek-reasoner (R1)
4. 工作流里调用
```

### Coze（字节，海外版 coze.com）

```
1. 工作流 → 添加节点 → 大模型
2. 选择"自定义" → 填 DeepSeek endpoint
3. 或用 OpenAI 兼容协议连接
```

### AutoGen / CrewAI

```python
# AutoGen
from autogen import AssistantAgent, UserProxyAgent

llm_config = {
    "config_list": [{
        "model": "deepseek-chat",
        "api_key": "sk-xxx",
        "base_url": "https://api.deepseek.com/v1",
        "api_type": "openai"
    }]
}

assistant = AssistantAgent("coder", llm_config=llm_config)
user = UserProxyAgent("user", code_execution_config={"work_dir": "coding"})
user.initiate_chat(assistant, message="写个排序算法")
```

## 📊 评测框架

### lm-evaluation-harness（EleutherAI）

```bash
git clone https://github.com/EleutherAI/lm-evaluation-harness
cd lm-evaluation-harness
pip install -e .

# 跑 DeepSeek-V3 在 MMLU 上
lm_eval --model openai-completions \
    --model_args model=deepseek-chat,base_url=https://api.deepseek.com/v1,api_key=sk-xxx \
    --tasks mmlu_high_school_computer_science \
    --batch_size 8 \
    --output_path ./results
```

### OpenCompass（上海AI Lab）

```bash
pip install opencompass

# config 目录新建 deepseek_v3.py
from opencompass.models import OpenAISDK

models = [
    OpenAISDK(
        path="deepseek-chat",
        key="sk-xxx",
        api_base="https://api.deepseek.com/v1",
        is_chat=True,
        meta_template=...,
    )
]

# 跑评测
run.py configs/eval_deepseek.py --datasets mmlu_gen cmmlu_gen
```

### DeepEval（专注 RAG/Agent 评测）

```python
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.models import DeepSeekModel

# 自定义 evaluator
model = DeepSeekModel(api_key="sk-xxx")

metric = AnswerRelevancyMetric(model=model, threshold=0.7)
test_case = LLMTestCase(
    input="什么是 RAG?",
    actual_output="RAG 是检索增强生成...",
    expected_output="..."
)
metric.measure(test_case)
print(metric.score, metric.reason)
```

## 🌐 浏览器扩展

### Page Assist

```
Chrome 扩展商店搜索 "Page Assist"
设置 → Ollama → 选 DeepSeek 端点
支持侧边栏聊天、网页摘要、翻译
```

### Monica AI

```
1. 安装 Monica 扩展
2. 设置 → 模型 → 自定义 OpenAI 兼容
3. 配置 DeepSeek endpoint
4. 网页摘要 / 翻译 / 写作 全功能
```

## 📱 移动端

### iOS / Android App

```
- ChatBox (iOS / Android)
- Lobe Chat (PWA)
- Cherry Studio (Android)
- OpenCat (iOS)

均支持配置自定义 OpenAI 兼容 endpoint
```

## 🔌 第三方插件汇总表

| 类别 | 工具 | 集成方式 | 难度 |
|---|---|---|---|
| IDE | Cursor | 内置配置 | ⭐ |
| IDE | Cline / Roo Code | OpenAI 兼容 | ⭐ |
| IDE | Continue | 配置文件 | ⭐⭐ |
| IM | ChatBox | 图形界面 | ⭐ |
| IM | Cherry Studio | 图形界面 | ⭐ |
| IM | ChatGPT-Next-Web | 环境变量 | ⭐⭐ |
| Agent | LangChain | Python SDK | ⭐⭐ |
| Agent | LlamaIndex | Python SDK | ⭐⭐ |
| 平台 | Dify | 图形界面 | ⭐ |
| 平台 | Coze | 图形界面 | ⭐ |
| Agent | AutoGen | Python SDK | ⭐⭐ |
| 评测 | lm-eval-harness | CLI | ⭐⭐ |
| 评测 | OpenCompass | Python SDK | ⭐⭐⭐ |
| 评测 | DeepEval | Python SDK | ⭐⭐ |
| 浏览器 | Page Assist | 扩展配置 | ⭐ |
| 浏览器 | Monica AI | 扩展配置 | ⭐ |

## 💡 选型建议

```
🌟 日常对话、写作：Cherry Studio / ChatBox
🌟 IDE 编程：Cursor / Cline + R1-Distill-Coder
🌟 企业级 RAG：Dify + deepseek-chat
🌟 复杂 Agent：LangChain / AutoGen + R1
🌟 学术评测：OpenCompass / lm-eval-harness
🌟 隐私本地：Ollama + R1-Distill-Qwen-7B
```
