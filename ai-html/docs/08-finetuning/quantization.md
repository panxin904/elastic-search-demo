---
title: 量化 GGUF / GPTQ / AWQ
---

# 量化 - GGUF / GPTQ / AWQ

> 把 FP16 模型压缩到 INT4 / INT8。**模型大小 / 显存 / 推理速度**减半或更多，**质量**略降。

## 🤔 为什么量化

| | FP16 | INT8 | INT4 |
|--|------|------|------|
| 模型大小 | 100% | ~50% | ~25% |
| 显存 | 100% | ~50% | ~25% |
| 速度 | 1x | 0.9-1.5x | 1.5-3x |
| 质量 | 100% | 99% | 95-98% |

**7B 模型 FP16 = 14GB；INT4 = 3.5GB → 笔记本能跑**。

## 📚 主流格式

| 格式 | 用谁 | 适合 |
|------|------|------|
| **GGUF** | llama.cpp / Ollama | **CPU + Mac + 端侧** |
| **GPTQ** | AutoGPTQ | GPU 推理 |
| **AWQ** | AutoAWQ | **GPU（4-bit 更好）** |
| **BNB** | bitsandbytes | 训练 + 推理 |
| **HQQ** | hqq | 简单 / 通用 |

## 🛠 GGUF（Ollama / llama.cpp）

```bash
# 一键：Ollama 自动处理
ollama pull llama3:8b-instruct-q4_K_M
# 内部就是 GGUF Q4_K_M 量化

# 手动量化（用 llama.cpp）
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make

# 转换 + 量化
python convert.py /path/to/llama3-8b --outfile llama3.f16.gguf
./llama-quantize llama3.f16.gguf llama3.q4_k_m.gguf q4_k_m
# 输出 ~4GB
```

```python
# llama-cpp-python
from llama_cpp import Llama
llm = Llama(
    model_path="./llama3.q4_k_m.gguf",
    n_ctx=4096,
    n_gpu_layers=35   # 多少层放 GPU
)
out = llm.create_chat_completion(
    messages=[{"role":"user","content":"hi"}]
)
print(out["choices"][0]["message"]["content"])
```

## 🛠 GPTQ（GPU）

```bash
pip install auto-gptq
```

```python
from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig
from transformers import AutoTokenizer

model_path = "meta-llama/Meta-Llama-3-8B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_path)

# 量化配置
quantize_config = BaseQuantizeConfig(
    bits=4,                       # 4-bit
    group_size=128,
    desc_act=False,
    sym=True
)

# 加载 + 量化
model = AutoGPTQForCausalLM.from_pretrained(
    model_path,
    quantize_config=quantize_config
)
examples = [...]                 # 校准数据（几十条文本）
model.quantize(examples)

# 保存
model.save_quantized("./llama3-8b-gptq-4bit")
tokenizer.save_pretrained("./llama3-8b-gptq-4bit")

# 加载
from auto_gptq import AutoGPTQForCausalLM
model = AutoGPTQForCausalLM.from_quantized("./llama3-8b-gptq-4bit", device="cuda:0")
```

## 🛠 AWQ（推荐 GPU）

```bash
pip install autoawq
```

```python
from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer

model = AutoAWQForCausalLM.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")

quant_config = {
    "zero_point": True,
    "q_group_size": 128,
    "w_bit": 4,                # 4-bit
    "version": "GEMM"
}

model.quantize(tokenizer, quant_config=quant_config, calib_data=calib_data)
model.save_quantized("./llama3-8b-awq-4bit")
```

## 🛠 bitsandbytes（4-bit + 8-bit 训练 / 推理）

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

bnb = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3-8B-Instruct",
    quantization_config=bnb,
    device_map="auto"
)
# 8GB 显存能跑 7B
```

## 📊 选型

| 场景 | 推荐 |
|------|------|
| Mac / CPU / 笔记本 | **GGUF Q4_K_M** |
| GPU 推理（单卡 24GB） | **AWQ 4-bit** / GPTQ 4-bit |
| 大模型多卡 | INT8 |
| 训练时省显存 | bitsandbytes 4-bit (QLoRA) |
| 不想折腾 | **Ollama**（自动） |

## 🆚 vs 蒸馏 / 剪枝

| | 量化 | 蒸馏 | 剪枝 |
|--|------|------|------|
| 减小模型 | ✅ | ✅（训小模型） | ✅ |
| 需要数据 | 几十条 | 几万条 | 一般 |
| 难度 | 低 | 高 | 中 |
| 效果 | 略降 | 持平 | 略降 |

## 🛠 实战

```bash
# 1. Ollama 一行跑量化
ollama pull qwen2.5:7b-instruct-q4_K_M   # 自动 Q4_K_M

# 2. 用 GGUF + llama.cpp 推理
./llama-cli -m model.gguf -p "hi"

# 3. vLLM 加载 AWQ
vllm serve ./llama3-8b-awq-4bit --quantization awq

# 4. HuggingFace transformers + GPTQ
model = AutoModelForCausalLM.from_pretrained("./llama3-8b-gptq-4bit",
    device_map="auto")
```

## 🔗 下一步

- [LoRA / QLoRA](/08-finetuning/lora)
- [全量微调](/08-finetuning/full)
- [vLLM / TGI 服务](/10-deploy/vllm-tgi)
- [Ollama 本地推理](/10-deploy/ollama)