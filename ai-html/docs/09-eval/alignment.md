---
title: RLHF / DPO - 对齐
date: 2026-08-15  # date-auto-injected
---

# RLHF / DPO - 让模型符合人类偏好

> **R**einforcement **L**earning from **H**uman **F**eedback / **D**irect **P**reference **O**ptimization。**让 LLM 输出更有用 / 更安全 / 更符合人类偏好**。

## 🤔 为什么需要对齐

```
基础模型（CPT 后）：
  ❌ 输出可能有害 / 跑偏 / 不 helpful
  ❌ 续写能力 ≠ 任务能力
  ❌ 没"知道什么时候不说"的能力

对齐 = 让模型：
  ✅ 听懂指令
  ✅ 不输出有害内容
  ✅ 风格 helpful / honest / harmless
```

## 🏗 RLHF 三步

```
1. 收集人类偏好数据
   prompt + 多个 response
   人类排序（哪个更好）
       ↓
2. 训 Reward Model（RM）
   input: (prompt, response)
   output: score
       ↓
3. PPO 训 LLM
   用 RM 评分，PPO 优化 LLM 策略
```

### 数据例子

```json
{
  "prompt": "What is photosynthesis?",
  "responses": [
    {"text": "Plants convert sunlight...", "rank": 1},
    {"text": "I don't know.", "rank": 2},
    {"text": "Photosynthesis is when...", "rank": 3}
  ]
}
```

## 🛠 RLHF 实现（PPO + TRL）

```bash
pip install trl transformers datasets accelerate
```

```python
from trl import PPOConfig, PPOTrainer, AutoModelForCausalLMWithValueHead
from transformers import AutoTokenizer
from datasets import load_dataset

# 1. 加载
model = AutoModelForCausalLMWithValueHead.from_pretrained("Qwen/Qwen2.5-7B")
ref_model = AutoModelForCausalLMWithValueHead.from_pretrained("Qwen/Qwen2.5-7B")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B")

# 2. Reward model
reward_model = ...   # 训好的 RM

# 3. 配置
config = PPOConfig(
    model_name="qwen",
    learning_rate=1e-5,
    batch_size=8,
    mini_batch_size=2,
    ppo_epochs=4
)
ppo_trainer = PPOTrainer(
    config=config,
    model=model,
    ref_model=ref_model,
    tokenizer=tokenizer,
    reward_model=reward_model
)

# 4. 训
dataset = load_dataset("your-rlhf-data", split="train")
for batch in ppo_trainer.dataloader:
    queries = batch["query"]
    responses = ppo_trainer.generate(queries)
    texts = [q + r for q, r in zip(queries, responses)]
    rewards = [reward_model(text) for text in texts]
    stats = ppo_trainer.step(queries, responses, rewards)
```

## 🛠 DPO（替代 RLHF，更简单）

**D**irect **P**reference **O**ptimization：跳过 RM，**直接用偏好数据训**。

```bash
pip install trl
```

```python
from trl import DPOTrainer, DPOConfig
from datasets import load_dataset

dataset = load_dataset("argilla/distilabel-intel-orca-dpo-pairs", split="train")

config = DPOConfig(
    output_dir="./dpo-out",
    num_train_epochs=3,
    per_device_train_batch_size=2,
    learning_rate=5e-7,
    beta=0.1                # 偏离 reference model 的力度
)
trainer = DPOTrainer(
    model="Qwen/Qwen2.5-7B-Instruct",
    ref_model="Qwen/Qwen2.5-7B-Instruct",   # reference for KL
    args=config,
    train_dataset=dataset,
    tokenizer=tokenizer
)
trainer.train()
```

DPO 数据格式：

```json
{
  "prompt": "问题...",
  "chosen": "好的回答",
  "rejected": "差的回答"
}
```

## 🆚 RLHF / DPO / RLAIF

| | RLHF | DPO | RLAIF |
|--|------|-----|--------|
| 反馈源 | 人类 | 人类 | **AI**（RLAIF） |
| RM 训练 | 必需 | ❌ 不要 | 必需 |
| 复杂度 | 高 | 中 | 高 |
| 效果 | 好 | 接近 RLHF | 接近 RLHF |
| 适合 | 大厂 / GPT-4 | **资源紧 / 实验** | 大量数据 |

## 🛠 ORPO / KTO（DPO 变种）

```bash
pip install trl
```

```python
# ORPO（odds ratio）— 不用 reference model
from trl import ORPOTrainer, ORPOConfig
config = ORPOConfig(output_dir="./orpo")
trainer = ORPOTrainer(
    model="Qwen/Qwen2.5-7B",
    args=config,
    train_dataset=dataset
)
trainer.train()

# KTO（Kahneman-Tversky）
# 不要求成对数据
```

## 🛠 RLAIF（AI 反馈）

```python
# 1. 用 Claude / GPT 评分
def ai_judge(prompt, response):
    score_prompt = f"对回答 {response} 评 1-10 分"
    return client.messages.create(...).score

# 2. 用 AI 评分当 RM 训练数据
# 3. 后续同 RLHF
```

## 🔄 RLHF 全流程

```python
# 1. 收集偏好数据
data = collect_preferences(
    questions=user_questions,
    human_rankings=human_annotations,
    n_per_q=4
)

# 2. 训 RM
reward_model = train_reward_model(data)

# 3. PPO 训 LLM
ppo_model = train_ppo(base_model, reward_model, prompts)

# 4. 评估
# - MT-Bench / Chatbot Arena 分数
# - 内部 A/B test
# - Safety benchmark
```

## 📊 数据集

```python
from datasets import load_dataset

# HH-RLHF（Anthropic，160k）
ds = load_dataset("Anthropic/hh-rlhf", split="train")

# UltraFeedback（DPO 训练常用）
ds = load_dataset("argilla/distilabel-intel-orca-dpo-pairs")

# UltraChat（多轮对话）
ds = load_dataset("stingning/ultrachat")
```

## 📊 选型

| 情况 | 选 |
|------|-----|
| 资源紧 + 已有偏好数据 | **DPO** |
| 大厂 + 大量人类标注 | RLHF + PPO |
| AI 评分代替人类 | RLAIF |
| 不想训 RM | ORPO / SimPO |

## 🔗 下一步

- [Eval 框架](/09-eval/frameworks)
- [LoRA / QLoRA](/08-finetuning/lora)
- [数据准备](/08-finetuning/data)