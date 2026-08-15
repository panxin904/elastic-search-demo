---
title: 开源模型 Llama / Mistral / Qwen
---

# 开源大模型

> 自部署、微调、离线 / 隐私场景**首选**。代表：Meta Llama、Mistral、阿里 Qwen、DeepSeek。

## 🧬 主流开源模型

| 模型 | 出品 | 上下文 | 参数 | 特点 |
|------|------|--------|------|------|
| **Llama 3.3 70B** | Meta | 128K | 70B | 当前最强开源通用 |
| Llama 3.2 1B/3B | Meta | 128K | 1B / 3B | 端侧 / 边缘 |
| **Mistral Large 2** | Mistral | 128K | 123B | 欧洲开源之光 |
| Mixtral 8x22B | Mistral | 64K | MoE 141B | MoE 高效 |
| **Qwen 2.5 72B** | 阿里 | 128K | 72B | 中文最强开源 |
| Qwen 2.5-Coder 32B | 阿里 | 128K | 32B | 代码强 |
| Yi-1.5 34B | 零一万物 | 4K | 34B | 中文优秀 |
| DeepSeek-V3 | DeepSeek | 128K | MoE 671B | 推理 + 中文 |
| Qwen 2.5-VL | 阿里 | 128K | 72B | 多模态 |

## 🚀 跑起来

### Ollama（一行命令）

```bash
# 安装
curl -fsSL https://ollama.com/install.sh | sh

# 拉 + 跑
ollama pull llama3.3:70b
ollama pull qwen2.5:72b
ollama run llama3.3 "你好"

# 服务（OpenAI 兼容 API）
ollama serve
# http://localhost:11434/v1
```

### vLLM（高吞吐推理）

```bash
pip install vllm
vllm serve meta-llama/Meta-Llama-3-70B-Instruct \
  --port 8000 --host 0.0.0.0 \
  --gpu-memory-utilization 0.9

# OpenAI 兼容 API
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")
resp = client.chat.completions.create(
    model="meta-llama/Meta-Llama-3-70B-Instruct",
    messages=[{"role":"user","content":"hi"}]
)
```

### TGI（HuggingFace）

```bash
docker run --gpus all -p 8080:80 \
  -v ~/.cache/huggingface:/data \
  ghcr.io/huggingface/text-generation-inference:latest \
  --model-id meta-llama/Meta-Llama-3-70B-Instruct
```

## 🔌 接入 SDK

```python
# OpenAI 兼容
from openai import OpenAI
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
resp = client.chat.completions.create(
    model="llama3.3",
    messages=[{"role":"user","content":"hi"}]
)
print(resp.choices[0].message.content)

# HuggingFace transformers（直接）
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

tok = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3-8B-Instruct",
    torch_dtype=torch.float16,
    device_map="auto"
)
inputs = tok("Hello", return_tensors="pt").to("cuda")
out = model.generate(**inputs, max_new_tokens=100)
print(tok.decode(out[0]))
```

## 🔬 微调

```python
# LoRA（用 PEFT）
from peft import LoraConfig, get_peft_model

lora = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj","v_proj"])
model = get_peft_model(base_model, lora)

# 训练（用 transformers Trainer）
from transformers import Trainer
trainer = Trainer(model=model, args=..., train_dataset=...)
trainer.train()
model.save_pretrained("./my-llama-lora")
```

详见 [LoRA / QLoRA](/08-finetuning/lora)。

## 🔢 量化

| 格式 | 大小 | 推理 | 适合 |
|------|------|------|------|
| FP16 | 100% | 原生 GPU | 服务器推理 |
| INT8 | ~50% | 几乎无损 | CPU / 边端 |
| GGUF Q4_K_M | ~25% | 质量略降 | CPU / 笔记本 |
| AWQ INT4 | ~28% | 极快 | GPU 推理加速 |

详见 [量化 GGUF / GPTQ](/08-finetuning/quantization)。

## 🆚 vs 闭源

| | 开源 | 闭源 |
|--|------|------|
| 成本 | 自己机器 / 极低 API | 按 Token |
| 数据隐私 | 100% 自留 | 上传厂商 |
| 定制 | 微调 / 系统提示 | 系统提示为主 |
| 性能 | 略弱（但追赶快） | 最强 |
| 维护 | 自己 | 厂商 |
| 适合 | 敏感数据 / 大流量 / 边缘 | 快速起步 / 最强能力 |

## 🔗 下一步

- [DeepSeek](/01-models/deepseek)
- [Ollama 本地推理](/10-deploy/ollama)
- [vLLM / TGI 服务](/10-deploy/vllm-tgi)
- [LoRA / QLoRA](/08-finetuning/lora)
- [量化 GGUF / GPTQ](/08-finetuning/quantization)