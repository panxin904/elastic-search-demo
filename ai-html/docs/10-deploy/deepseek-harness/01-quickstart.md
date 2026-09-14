---
title: DeepSeek Harness 使用文档
date: 2026-09-14  # date-auto-injected
---

# 🚀 DeepSeek 使用文档

> 5 分钟跑通 DeepSeek。从云端 API、本地 Ollama、到自部署 vLLM 服务，覆盖 95% 入门场景。

## 1️⃣ 云端 API（最快，推荐先体验）

### 注册与充值

```
1. 访问 https://platform.deepseek.com
2. 注册 → 实名 → 充值（最低 1 元起）
3. 创建 API Key：console.deepseek.com → API Keys
4. 保存 Key（仅显示一次）
```

### OpenAI 兼容调用（任意语言）

```python
# pip install openai
from openai import OpenAI

client = OpenAI(
    api_key="sk-xxx",                              # 你的 DeepSeek API Key
    base_url="https://api.deepseek.com/v1"         # DeepSeek 兼容 endpoint
)

# 普通对话（V3.2）
resp = client.chat.completions.create(
    model="deepseek-chat",                          # 即 V3.2
    messages=[
        {"role": "system", "content": "你是 Python 专家"},
        {"role": "user",   "content": "写个装饰器测函数耗时"}
    ],
    temperature=0.6,
    max_tokens=4096
)
print(resp.choices[0].message.content)
print(f"tokens: {resp.usage.total_tokens}")
```

```bash
# curl
curl -X POST "https://api.deepseek.com/v1/chat/completions" \
    -H "Authorization: Bearer sk-xxx" \
    -H "Content-Type: application/json" \
    -d '{
      "model": "deepseek-chat",
      "messages": [
        {"role": "user", "content": "你好"}
      ],
      "temperature": 0.6,
      "max_tokens": 1024
    }'
```

### R1 推理模型（特殊输出格式）

```python
# R1 会先输出 <think> 推理过程，再输出答案
resp = client.chat.completions.create(
    model="deepseek-reasoner",                       # 即 R1
    messages=[
        {"role": "user", "content": "9.11 和 9.9 哪个大？"}
    ]
)
msg = resp.choices[0].message
print("=== thinking ===")
print(msg.reasoning_content)                         # 推理过程
print("=== answer ===")
print(msg.content)                                    # 最终答案
```

### 流式输出

```python
stream = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "写首诗"}],
    stream=True
)
for chunk in stream:
    delta = chunk.choices[0].delta
    if delta.content:
        print(delta.content, end="", flush=True)
```

### Function Calling

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名"}
                },
                "required": ["city"]
            }
        }
    }
]

resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "北京今天天气怎么样？"}],
    tools=tools,
    tool_choice="auto"
)

# 模型决定调用工具 → 返回 tool_calls
tool_call = resp.choices[0].message.tool_calls[0]
print(tool_call.function.name)        # "get_weather"
print(tool_call.function.arguments)  # '{"city":"北京"}'

# 执行工具后再把结果回传
messages = [
    {"role": "user", "content": "北京今天天气怎么样？"},
    resp.choices[0].message,           # assistant 消息（带 tool_calls）
    {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": "{\"temp\": 22, \"weather\": \"晴\"}"
    }
]
final = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tools
)
print(final.choices[0].message.content)
# "北京今天晴，气温 22°C"
```

### 定价参考（2026 年）

```
DeepSeek-V3.2（deepseek-chat）：
  缓存命中：$0.028 / 1M tokens
  缓存未中：$0.27  / 1M tokens
  输出：    $1.10  / 1M tokens

DeepSeek-R1（deepseek-reasoner）：
  缓存命中：$0.14  / 1M tokens
  缓存未中：$0.55  / 1M tokens
  输出：    $2.19  / 1M tokens

折扣时段（UTC 16:30-00:30）半价
```

## 2️⃣ 本地 Ollama（最简单）

```bash
# 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 拉模型（选小一点的蒸馏版起步）
ollama pull deepseek-r1:7b          # R1 蒸馏 7B，约 4.7GB
ollama pull deepseek-r1:14b         # R1 蒸馏 14B，约 9GB
ollama pull deepseek-v3:671b-cloud  # V3 云端版本（本地只跑小模型）

# 运行
ollama run deepseek-r1:7b "你好"

# 启动 API 服务（默认端口 11434）
ollama serve
# OpenAI 兼容 endpoint：http://localhost:11434/v1
```

### Open WebUI（Ollama 配套前端）

```bash
docker run -d \
    --name open-webui \
    -p 3000:8080 \
    -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
    -v open-webui-data:/app/backend/data \
    ghcr.io/open-webui/open-webui:main

# 访问 http://localhost:3000
```

## 3️⃣ vLLM 自部署（中等门槛）

### 硬件需求

| 模型 | FP16 | INT8/AWQ | 4-bit/GPTQ |
|---|---|---|---|
| V3 671B | 8× H100 (80G) | 8× A100 (80G) | 不推荐 |
| V3.1 685B | 8× H100 | 8× A100 | — |
| R1 671B | 8× H100 | 8× A100 | — |
| R1-Distill-70B | 2× A100 (80G) | 1× A100 | 1× 4090 (24G) |
| R1-Distill-32B | 1× A100 (80G) | 1× A100 | 1× 4090 |
| R1-Distill-14B | 1× 4090 | 1× 3090 | 1× 3060 (12G) |
| R1-Distill-7B | 1× 3090 | 1× 2080Ti | 任意 8G |
| R1-Distill-1.5B | CPU 都能跑 | — | — |

### 启动命令

```bash
# 安装 vllm
pip install vllm

# 单 GPU 跑 R1-Distill-7B
vllm serve deepseek-ai/DeepSeek-R1-Distill-Qwen-7B \
    --port 8000 \
    --host 0.0.0.0 \
    --max-model-len 32768 \
    --gpu-memory-utilization 0.9

# 多 GPU 跑 V3 671B（4× H100）
vllm serve deepseek-ai/DeepSeek-V3 \
    --port 8000 \
    --tensor-parallel-size 4 \
    --max-model-len 32768 \
    --enable-expert-parallel    # MoE 专家并行
```

### 调用 vLLM 服务

```python
from openai import OpenAI

# 复用 OpenAI SDK，只是换 base_url
client = OpenAI(
    api_key="EMPTY",                                 # vLLM 不校验
    base_url="http://localhost:8000/v1"
)

resp = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
    messages=[{"role": "user", "content": "你好"}]
)
print(resp.choices[0].message.content)
```

## 4️⃣ SGLang 自部署（更优吞吐量）

```bash
# 安装
pip install sglang[all]

# 启动 R1
python -m sglang.launch_server \
    --model-path deepseek-ai/DeepSeek-R1-Distill-Qwen-32B \
    --port 8000 \
    --mem-fraction-static 0.85
```

### vLLM vs SGLang 对比

| 维度 | vLLM | SGLang |
|---|---|---|
| 单 batch 吞吐 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 长上下文 (R1) | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| RadixAttention | ❌ | ✅ |
| 结构化输出 | ✅ | ✅ 更强（grammar） |
| 学习曲线 | 平缓 | 略陡 |
| DeepSeek 适配 | 良好 | 优秀（R1 推理模板） |

## 5️⃣ LMDeploy（清华出品，DeepSeek 适配优化）

```bash
pip install lmdeploy

lmdeploy serve api_server \
    deepseek-ai/DeepSeek-V3 \
    --server-port 8000 \
    --tp 4 \
    --model-format hf
```

LMDeploy 对 DeepSeek-V3 有专门优化，TurboMind 引擎在 MoE 上吞吐领先。

## 6️⃣ Docker Compose 一键部署

```yaml
# docker-compose.yml
version: '3'
services:
  vllm:
    image: vllm/vllm-openai:latest
    runtime: nvidia
    ports:
      - "8000:8000"
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    volumes:
      - ~/.cache/huggingface:/root/.cache/huggingface
    command: >
      --model deepseek-ai/DeepSeek-R1-Distill-Qwen-14B
      --max-model-len 32768
      --tensor-parallel-size 1
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

```bash
docker-compose up -d
curl http://localhost:8000/v1/models
```

## 7️⃣ 命令速查

```bash
# Ollama
ollama list                              # 列出本地模型
ollama pull deepseek-r1:7b              # 拉取
ollama rm deepseek-r1:7b                # 删除
ollama cp deepseek-r1:7b my-deepseek    # 复制改名

# vLLM
vllm serve <model> --port 8000
vllm bench --model <model>              # 跑压测
vllm chat <model>                       # 启动交互式 chat

# SGLang
python -m sglang.launch_server --model-path <model>
python -m sglang.bench_serving --model <model>
```
