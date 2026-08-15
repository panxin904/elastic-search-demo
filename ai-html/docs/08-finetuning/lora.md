---
title: LoRA / QLoRA
---

# LoRA / QLoRA - 低成本微调

> 全量微调 70B 模型需要 1.4 TB 显存。**LoRA / QLoRA 把成本降到 1/100**。

## 🤔 为什么需要 LoRA

```
全量微调：
  70B 模型  ×  12 字节 / 参数（FP16 + 优化器）  ×  3 副本（模型 / 梯度 / 优化器）
  = 70e9 × 12 × 3 = 2.5 TB 显存 ❌

LoRA（Low-Rank Adaptation）：
  冻结原模型
  在每层加两个小矩阵 A（down-project）+ B（up-project）
  只训练 A、B（< 1% 参数）
  显存 7B ~16GB，70B 几百 GB

QLoRA：
  进一步把原模型量化到 4-bit
  70B 能在 24GB 单卡微调
```

## 📐 LoRA 原理

```
原始 W (d × d)
LoRA: W + ΔW = W + (B @ A)        B: d × r,  A: r × d
训练：A、B（r 是 rank，常见 8-64）
r << d（d 可能是 4096）

参数：
  全量 = d × d
  LoRA = 2 × d × r（典型 r=16：减少 99.97%）
```

## 🛠 实战（用 PEFT + transformers）

```bash
pip install transformers peft datasets accelerate bitsandbytes
```

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
from transformers import TrainingArguments, Trainer

# 1. 加载模型（QLoRA 4-bit 量化）
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3-8B-Instruct",
    load_in_4bit=True,                                    # 4-bit
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")

# 2. 准备 4-bit 训练
model = prepare_model_for_kbit_training(model)

# 3. LoRA 配置
lora_config = LoraConfig(
    r=16,                        # rank
    lora_alpha=32,              # scaling = alpha / r
    lora_dropout=0.05,
    bias="none",
    target_modules=["q_proj","k_proj","v_proj","o_proj"],  # attention
    task_type="CAUSAL_LM"
)

# 4. 套 LoRA
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# trainable params: 7M || all params: 8B || trainable%: 0.087%

# 5. 准备数据
dataset = load_dataset("your-dataset", split="train")
def format(example):
    return tokenizer(f"### Question: {example['q']}\n### Answer: {example['a']}",
                     truncation=True, max_length=512)
dataset = dataset.map(format)

# 6. 训练
trainer = Trainer(
    model=model,
    args=TrainingArguments(
        output_dir="./output",
        num_train_epochs=3,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        fp16=True
    ),
    train_dataset=dataset
)
trainer.train()

# 7. 保存（只 LoRA 权重，~50MB）
model.save_pretrained("./my-lora")
```

## 🛠 推理（merge + load）

```python
# 方式 1：LoRA 单独加载
from peft import PeftModel
base = AutoModelForCausalLM.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")
model = PeftModel.from_pretrained(base, "./my-lora")

# 方式 2：merge 后保存完整模型
model = model.merge_and_unload()
model.save_pretrained("./my-merged")
```

## 🛠 用 unsloth（更快 + 省显存）

```bash
pip install unsloth
```

```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    "meta-llama/Meta-Llama-3-8B-Instruct",
    max_seq_length=2048,
    load_in_4bit=True
)

model = FastLanguageModel.get_peft_model(
    model, r=16, target_modules=["q_proj","k_proj","v_proj","o_proj"]
)

# 训练接口一样
```

**2x 速度，-50% 显存**。

## 🔧 超参

| 参数 | 推荐 |
|------|------|
| r (rank) | 8-64（越大越接近全量，显存更多） |
| lora_alpha | r × 2（常用 32 / 64） |
| lora_dropout | 0-0.1 |
| target_modules | q/k/v/o_proj（attn），或加 gate/up/down_proj（ffn） |
| learning_rate | 1e-4 ~ 5e-4 |
| epochs | 1-5（看数据量） |
| batch_size | 1-4 + grad_accum |

## 📊 数据准备

```python
# 1. 对话格式（instruction tuning）
{"messages": [
    {"role":"system","content":"你是助手"},
    {"role":"user","content":"..."},
    {"role":"assistant","content":"..."}
]}

# 2. 用 tokenizer apply_chat_template
def format(ex):
    text = tokenizer.apply_chat_template(ex["messages"], tokenize=False)
    return {"text": text}

# 3. 数据量：起步 1000 条高质量对话
# 高质量 > 大量
```

## 🛠 全流程

```python
# 1. 装环境
# pip install peft trl accelerate bitsandbytes

# 2. 用 TRL（HF 官方）
from trl import SFTTrainer, SFTConfig

config = SFTConfig(
    output_dir="./lora-out",
    num_train_epochs=3,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    learning_rate=2e-4,
    bf16=True,
    logging_steps=10
)
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    peft_config=lora_config,
    args=config
)
trainer.train()
```

## 🆚 vs 全量微调

| | LoRA | QLoRA | 全量 |
|--|------|--------|------|
| 显存（70B） | 几百 GB | **24-48 GB** | 1.4 TB |
| 训练时间 | 中 | 慢（量化） | 慢 |
| 效果 | 好 | 略好 | 最好 |
| 灵活 | 单任务 | 单任务 | 通用 |

## 🔗 下一步

- [全量微调](/08-finetuning/full)
- [数据准备](/08-finetuning/data)
- [量化 GGUF / GPTQ](/08-finetuning/quantization)
- [RLHF / DPO](/09-eval/alignment)