---
title: vLLM / TGI 服务
date: 2026-08-15  # date-auto-injected
---

# vLLM / TGI - 高吞吐推理服务

> **生产首选**。vLLM 用 **PagedAttention**（类 OS 虚拟内存），吞吐量比 HF transformers 高 14-24x。

## 🤔 为什么用 vLLM

```
HF Transformers：
  ❌ 显存碎片（KV cache 占连续显存）
  ❌ 吞吐量低（batch 小，GPU 浪费）
  ❌ 长上下文爆显存

vLLM：
  ✅ PagedAttention：KV cache 分页（像 OS 虚拟内存）
  ✅ Continuous batching：动态调整 batch
  ✅ Chunked prefill：长 prompt 分块
  ✅ 多 GPU 推理
  ✅ OpenAI 兼容 API
  ✅ 支持 HuggingFace 任意模型
```

## 📦 安装

```bash
# Python
pip install vllm

# 跑服务
vllm serve meta-llama/Meta-Llama-3-8B-Instruct \
  --port 8000 \
  --host 0.0.0.0 \
  --gpu-memory-utilization 0.9
```

## 🚀 命令行启动

```bash
# 基础
vllm serve Qwen/Qwen2.5-7B-Instruct

# 量化（AWQ / GPTQ）
vllm serve Qwen/Qwen2.5-7B-Instruct-AWQ

# 多 GPU
vllm serve meta-llama/Meta-Llama-3-70B-Instruct \
  --tensor-parallel-size 4

# 高吞吐配置
vllm serve meta-llama/Meta-Llama-3-8B-Instruct \
  --max-num-batched-tokens 8192 \
  --max-num-seqs 256 \
  --gpu-memory-utilization 0.95

# 量化
vllm serve ./my-llama3-8b-awq-4bit --quantization awq

# LoRA
vllm serve Qwen/Qwen2.5-7B-Instruct \
  --enable-lora \
  --lora-modules my-lora=/path/to/lora

# 多模态（视觉）
vllm serve llava-hf/llava-1.5-7b-hf
```

## 🐍 Python 客户端（OpenAI 兼容）

```python
from openai import OpenAI

# vLLM 默认 :8000/v1
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY"        # 随便填
)

# Chat
resp = client.chat.completions.create(
    model="Qwen/Qwen2.5-7B-Instruct",
    messages=[{"role":"user","content":"你好"}],
    temperature=0.7,
    max_tokens=512
)
print(resp.choices[0].message.content)

# 流式
for chunk in client.chat.completions.create(
    model="Qwen/Qwen2.5-7B-Instruct",
    messages=[{"role":"user","content":"讲笑话"}],
    stream=True
):
    print(chunk.choices[0].delta.content or "", end="", flush=True)

# Embedding
resp = client.embeddings.create(
    model="BAAI/bge-m3",
    input="hello world"
)
print(len(resp.data[0].embedding))
```

## 🔧 进阶配置

```python
# 直接用 vLLM Python API
from vllm import LLM, SamplingParams

llm = LLM(
    model="Qwen/Qwen2.5-7B-Instruct",
    tensor_parallel_size=2,           # 2 卡
    gpu_memory_utilization=0.9,
    dtype="bfloat16",
    max_model_len=8192
)

params = SamplingParams(
    temperature=0.7,
    top_p=0.9,
    max_tokens=512
)

outputs = llm.generate(["讲个笑话", "Python 怎么用？"], params)
for out in outputs:
    print(out.outputs[0].text)
```

## 🐳 Docker / k8s

```yaml
# docker-compose.yml
services:
  vllm:
    image: vllm/vllm-openai:latest
    command: >
      vllm serve Qwen/Qwen2.5-7B-Instruct
      --host 0.0.0.0 --port 8000
      --gpu-memory-utilization 0.9
    ports:
      - "8000:8000"
    runtime: nvidia              # GPU
    environment:
      HUGGING_FACE_HUB_TOKEN: xxx
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

## 📊 性能对比

| 模型 | 框架 | 吞吐（tokens/s/GPU） |
|------|------|---------------------|
| Llama 70B | HF Transformers | ~1500 |
| Llama 70B | vLLM | **~18000** |
| Llama 70B | TGI | ~12000 |
| Llama 8B | vLLM | ~15000 |

## 🔥 TGI（HuggingFace Text Generation Inference）

Rust 实现，HF 官方推理服务。

```bash
docker run --gpus all -p 8080:80 \
  -v $HOME/.cache/huggingface:/data \
  ghcr.io/huggingface/text-generation-inference:latest \
  --model-id meta-llama/Meta-Llama-3-8B-Instruct
```

```python
from huggingface_hub import InferenceClient
client = InferenceClient(model="http://localhost:8080")
for token in client.text_generation("hi", max_new_tokens=100, stream=True):
    print(token, end="", flush=True)
```

## 🔧 vLLM vs TGI vs LMDeploy

| | vLLM | TGI | LMDeploy |
|--|------|-----|----------|
| 出品 | UC Berkeley | HF | 商汤 |
| 语言 | Python | Rust | Python + C++ |
| PagedAttention | ✅ | 部分 | ✅ |
| 多模态 | ✅ | ✅ | ✅ |
| 性能 | **极强** | 强 | 极强 |
| 生态 | **最大** | HF 生态 | 中国 |

## 🛠 实战

```python
# 1. vLLM 服务
vllm serve Qwen/Qwen2.5-7B-Instruct --port 8000

# 2. LangChain 接 vLLM
from langchain_community.llms import VLLM
llm = VLLM(
    model="Qwen/Qwen2.5-7B-Instruct",
    vllm_server_url="http://localhost:8000/v1"
)
print(llm.invoke("hi"))

# 3. 监控（Prometheus）
vllm serve ... --enable-prometheus
# :8000/metrics
```

## 🆚 vs 托管

| | vLLM 自部署 | 托管 |
|--|------------|------|
| 成本 | 服务器（贵） | 按 Token（便宜起步） |
| 隐私 | ✅ | ❌ |
| 速度 | 同机房内 | 网络延迟 |
| 弹性 | 固定 | 自动 |
| 适合 | 大流量 / 私有 | 起步 / 突发 |

## 🔗 下一步

- [Ollama 本地推理](/10-deploy/ollama)
- [API 托管](/10-deploy/hosted)
- [量化 GGUF / GPTQ](/08-finetuning/quantization)