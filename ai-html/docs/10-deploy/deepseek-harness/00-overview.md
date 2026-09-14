---
title: DeepSeek Harness 学习文档
date: 2026-09-14  # date-auto-injected
---

# 🎓 DeepSeek Harness 学习文档

> **Harness（训练/推理驾驭框架）** 是指用于驾驭 DeepSeek 系列大模型的完整工程化框架体系——从模型加载、推理服务、工具调用、Agent 构建到评测对比的全链路工具集。本章系统梳理 DeepSeek 全家桶及配套的"驾驭框架"。

## 🌐 DeepSeek 模型家族总览

| 模型 | 发布方 | 定位 | 开源情况 | 参数量 |
|---|---|---|---|---|
| **DeepSeek-V3** | DeepSeek-AI | 通用 MoE 大模型 | ✅ Apache 2.0 | 671B (37B 激活) |
| **DeepSeek-V3.1** | DeepSeek-AI | V3 升级版 + 混合推理 | ✅ | 685B |
| **DeepSeek-V3.2** | DeepSeek-AI | 稀疏注意力 DSA | ✅ | 685B |
| **DeepSeek-R1** | DeepSeek-AI | 推理专用 (CoT 强) | ✅ MIT | 671B |
| **DeepSeek-R1-Distill-Qwen/Llama** | DeepSeek-AI | R1 蒸馏小模型 | ✅ | 1.5B / 7B / 8B / 14B / 32B / 70B |
| **DeepSeek-Coder-V2** | DeepSeek-AI | 代码 MoE | ✅ | 236B (21B 激活) |
| **DeepSeek-Coder** | DeepSeek-AI | 代码补全 | ✅ | 1.3B / 6.7B / 33B |
| **DeepSeek-Math** | DeepSeek-AI | 数学 | ✅ | 7B |
| **DeepSeek-VL2** | DeepSeek-AI | 多模态 (Vision-Language) | ✅ | 3B / 16B / 27B (MoE) |
| **DeepSeek-Prover-V2** | DeepSeek-AI | 形式化数学证明 | ✅ | 671B |
| **DeepSeek-OCR** | DeepSeek-AI | OCR + 视觉编码 | ✅ | 3B |

> 📌 **2026 年 9 月最新状态**：DeepSeek-V3.2-Exp 已发布，引入 **DSA（DeepSeek Sparse Attention）**，长上下文性能显著提升。

## 🧰 "Harness" 三层含义

```
┌─────────────────────────────────────────────────┐
│ 1️⃣ 模型原生 Harness（DeepSeek 官方仓库提供）   │
│    - DeepSeek-V3/R1 inference repo              │
│    - DualPipe / EPLB（训练调度）                 │
│    - 推理模板（chat_template.json）              │
└─────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────┐
│ 2️⃣ 推理框架 Harness（第三方适配）                │
│    - vLLM / SGLang / TGI / LMDeploy / TensorRT  │
│    - OpenAI 兼容 API 服务化                       │
└─────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────┐
│ 3️⃣ 应用层 Harness（Agent / RAG 工具）           │
│    - LangChain / LlamaIndex / Dify / Coze        │
│    - Cursor / Cline / Continue / Roo Code        │
│    - 评测 harness（lm-eval-harness / OpenCompass）│
└─────────────────────────────────────────────────┘
```

## 📚 学习路径推荐

### 🟢 入门级（1 周）

```
Day 1-2: DeepSeek API 调用（OpenAI 兼容 SDK）
Day 3-4: DeepSeek-R1 推理模型特性 + Prompt 工程
Day 5-7: Ollama 本地跑 DeepSeek-R1-Distill-Qwen-7B
```

### 🟡 进阶级（2-3 周）

```
Week 1: vLLM / SGLang 部署 DeepSeek-V3 671B（多 GPU）
Week 2: Function Calling + Tool Use
Week 3: RAG + Agent 集成（LangChain / Dify）
```

### 🔴 专家级（1-2 月）

```
Month 1:
  - DeepSeek-V3 推理优化（PD 分离、Chunked Prefill）
  - DeepSeek-R1 蒸馏自己数据（LoRA / Full SFT）
  - MoE 路由理解（Expert Parallel）
  - 评测体系搭建（lm-eval-harness）

Month 2:
  - DualPipe 训练流水线（DeepSeek 自研）
  - 自定义 Chat Template + Reasoning Parser
  - 多模态（DeepSeek-VL2）实战
```

## 🔍 与其他模型的对比

| 维度 | DeepSeek-V3.2 | GPT-5 | Claude 4.5 | Qwen3-235B |
|---|---|---|---|---|
| 价格 (per 1M token) | $0.27 in / $1.1 out | $5 / $20 | $3 / $15 | $0.3 / $1.2 |
| 上下文长度 | 128K (稀疏扩 1M) | 256K | 200K | 128K |
| 中文能力 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 代码能力 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 推理能力 (R1) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 开源可部署 | ✅ | ❌ | ❌ | ✅ |
| 本地 GPU 需求 | V3:8x A100, R1:同 | N/A | N/A | 4x A100 |

## 🏛️ DeepSeek 核心技术

### 1. MLA（Multi-head Latent Attention）

```
传统 MHA：缓存每个 head 的 K/V
MLA：压缩到低秩潜空间，KV 缓存减少 5-10x
效果：长上下文推理显存大幅降低
```

### 2. MoE 架构（DeepSeek-V3）

```
671B 总参数，37B 激活
256 个路由专家 + 1 个共享专家
每次 token 激活 8 个专家
```

### 3. DualPipe（训练调度）

```
流水线并行 + 专家并行 + 张量并行
DualPipe = 双向流水线调度
解决 MoE 训练中的"气泡"问题
吞吐量提升 30%+
```

### 4. FP8 混合精度训练

```
业界首个大规模 FP8 训练框架
在 H800 上训练 V3
显存占用降低 50%+
```

### 5. DeepSeek-R1 的 GRPO

```
Group Relative Policy Optimization
无 Critic，纯策略优化
奖励 = 准确率 + 格式
```

### 6. DSA（DeepSeek Sparse Attention）— V3.2 新增

```
动态稀疏注意力
128K 上下文几乎零衰减
推理速度提升 2-5x（长文本）
```

## 📦 配套生态仓库

```
deepseek-ai/DeepSeek-V3          训练/推理代码
deepseek-ai/DeepSeek-R1          R1 模型权重 + 推理模板
deepseek-ai/DeepSeek-VL2         多模态
deepseek-ai/DeepSeek-Coder-V2    代码模型
deepseek-ai/DeepSeek-Math        数学
deepseek-ai/awesome-deepseek-coder  社区资源汇总
deepseek-ai/DeepSeek-Prover-V2   形式化证明
```

## 🎯 学习资源清单

| 资源 | 类型 | 说明 |
|---|---|---|
| DeepSeek 官方文档 | docs | platform.deepseek.com/docs |
| DeepSeek-V3 论文 | paper | arxiv.org/abs/2412.19437 |
| DeepSeek-R1 论文 | paper | arxiv.org/abs/2501.12948 |
| DualPipe 论文 | paper | DeepSeek 技术博客 |
| HuggingFace 模型卡 | model | 各模型权重 + chat_template |
| 官方 Discord | community | 答疑 + 案例分享 |
| DeepSeek Status 页 | service | status.deepseek.com |

## 💡 关键认知

```
1. DeepSeek 的核心壁垒 = 极致工程效率 + 开源开放
2. V3 / R1 671B 需要 8x H100/A100 才能跑（FP16）
3. R1-Distill 系列是消费级 GPU（24GB）能跑的"平替"
4. 所有模型都 OpenAI 兼容 API → 工具链零迁移
5. R1 输出 `<thinking>` 块 → 需要 streaming + reasoning parser
```
