---
title: 全量微调
---

# 全量微调（Full Fine-tuning）

> 解冻**所有**参数训练。LoRA 不够 / 重要场景（行业大模型）才用。

## 🤔 什么时候需要全量

```
LoRA / QLoRA 适合（90% 场景）：
  ✅ 数据 1k-10k
  ✅ 风格 / 任务适应
  ✅ 资源有限

全量微调适合（少数）：
  ❌ 基础模型大改（继续预训练）
  ❌ 大数据（百万级 token）
  ❌ 特定行业 LLM
  ❌ 多 GPU 集群
```

## 🛠 基础

```bash
pip install transformers datasets accelerate deepspeed
# 推荐：8x A100 80GB / H100
```

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from datasets import load_dataset

# 1. 加载
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3-8B",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")

# 2. 数据
dataset = load_dataset("your-dataset", split="train")
def format(ex):
    return tokenizer(ex["text"], truncation=True, max_length=2048)
dataset = dataset.map(format, remove_columns=dataset.column_names)

# 3. 训练
trainer = Trainer(
    model=model,
    args=TrainingArguments(
        output_dir="./output",
        num_train_epochs=3,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=16,
        learning_rate=2e-5,
        bf16=True,
        logging_steps=20,
        save_steps=500,
        warmup_steps=100
    ),
    train_dataset=dataset
)
trainer.train()
```

## 🚀 分布式（多 GPU / 节点）

### DDP（单机多卡）

```bash
torchrun --nproc_per_node=8 train.py
```

`device_map="auto"` 自动把模型分到 8 张卡。

### DeepSpeed（多机）

```yaml
# ds_config.json
{
  "train_micro_batch_size_per_gpu": 1,
  "gradient_accumulation_steps": 16,
  "fp16": {"enabled": true},
  "zero_optimization": {
    "stage": 3   # ZeRO-3：把 optimizer / gradient / 参数全部分片
  }
}
```

```python
from accelerate import DeepSpeedPlugin, Accelerator
plugin = DeepSpeedPlugin("ds_config.json")
accelerator = Accelerator(deepspeed_plugin=plugin)
```

### FSDP（PyTorch 原生）

```python
from torch.distributed.fsdp import FullyShardedDataParallel
# 替代 DeepSpeed / ZeRO-3
```

## 📊 资源估算

| 模型 | 优化器 | 精度 | 显存（训练） |
|------|--------|------|---------------|
| 7B  | AdamW | FP16 | ~120 GB |
| 7B  | AdamW | BF16 | ~80 GB |
| 7B  | Adafactor | BF16 | ~60 GB |
| 13B | AdamW | BF16 | ~150 GB |
| 70B | AdamW | BF16 | 1.4 TB（需要 ZeRO-3） |
| 70B | AdamW | FP8 | 700 GB（8x H100） |

## 🛠 继续预训练（CPT）

```python
# 在 1T token 中文上继续预训练 Llama-3
# 1. 拿 Llama-3 8B base（不是 instruct）
# 2. 全量微调，几百亿 token
# 3. 之后 instruct-tuning

# 关键：loss = 下一 token 预测
def data_collator(batch):
    return tokenizer(batch["text"], padding=True, truncation=True, max_length=4096, return_tensors="pt")
```

## 🛠 全量 vs LoRA 选择

| 场景 | 选 |
|------|-----|
| 数据 < 1M 条 | **LoRA / QLoRA** |
| 数据 1-10M 条 | LoRA + 大量数据 |
| 数据 > 100M 条 / 继续预训练 | **全量** |
| 显存够 / 有多卡 | 全量 |
| 想做研究（控制每个参数） | 全量 |
| 快速 demo / 行业适配 | **LoRA** |
| 模型新架构 | **全量** |

## 🛠 实战：从 0 微调一个中文模型

```python
# 1. 数据：10 万条中文对话
# 2. 基础模型：Qwen2.5-7B-Base（中文原生）
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-7B", torch_dtype=torch.bfloat16)

# 3. 多卡训练（4x A100）
torchrun --nproc_per_node=4 train.py

# 4. 保存 + 上传
model.save_pretrained("./my-chinese-model")
tokenizer.save_pretrained("./my-chinese-model")
huggingface-cli upload my-org/my-chinese-model ./my-chinese-model
```

## 🔧 关键技术

```python
# ZeRO-3 节省显存
# 混合精度 BF16 + FP32 master
# 梯度累积（gradient_accumulation_steps）
# 梯度 checkpointing（model.gradient_checkpointing_enable()）
# 优化器：AdamW / Adafactor
# LR scheduler：cosine / linear
# 混合精度 loss scaling
```

## 🔗 下一步

- [LoRA / QLoRA](/08-finetuning/lora)
- [数据准备](/08-finetuning/data)
- [量化 GGUF / GPTQ](/08-finetuning/quantization)
- [vLLM / TGI 服务](/10-deploy/vllm-tgi)