---
title: DeepSeek Harness 使用教程
date: 2026-09-14  # date-auto-injected
---

# 📘 DeepSeek 使用教程

> 系统化教程：环境配置、模型选择、调参技巧、典型工作流。从"刚装好 Ollama"到"搭出可上线的服务"。

## 🛠️ 第 1 课：环境准备

### 选择部署方式

```
❓ 你想怎么用 DeepSeek？

├─ 🌐 直接调 API（最快上手）
│   └─ 只需 API Key + 1 个 Python 包
│
├─ 💻 本地跑小模型（保护隐私）
│   └─ Ollama + 任意 GPU/CPU
│
├─ 🏢 自部署大模型（企业级）
│   └─ vLLM / SGLang / LMDeploy
│
└─ 📱 嵌入式集成（IDE / IM 插件）
    └─ Cursor / Cline / Continue
```

### 硬件清单

| 用途 | 推荐配置 |
|---|---|
| 本地 R1-Distill-7B | RTX 3090 / 4060Ti (8GB+) |
| 本地 R1-Distill-14B | RTX 4090 (24GB) |
| 本地 R1-Distill-32B | RTX 4090D (24GB) + 量化 |
| 生产 V3/R1 671B | 8× H100 / A100 80G |
| 云端 API | 任意（无需 GPU） |

### 安装包

```bash
# Python 环境
python -m venv .venv
source .venv/bin/activate
pip install openai requests vllm

# Docker 环境
docker --version  # 24.0+
docker compose version  # v2.20+
nvidia-smi        # 验证 GPU 可用

# Ollama
curl -fsSL https://ollama.com/install.sh | sh
```

## 🎯 第 2 课：模型选型决策树

```
任务是什么？
│
├─ 通用对话 / 写作 / 翻译
│   └─ deepseek-chat（V3.2）✅ 默认选择
│
├─ 数学 / 逻辑 / 代码 / 复杂推理
│   └─ deepseek-reasoner（R1）✅ 强推理
│
├─ 代码补全 / IDE 实时
│   └─ deepseek-coder / R1-Distill-Coder
│
├─ 超长上下文（>64K）
│   └─ V3.2（DSA 稀疏注意力）+ 配合 Context Caching
│
├─ 多模态（图 + 文）
│   └─ DeepSeek-VL2
│
├─ 本地跑 / 隐私
│   └─ R1-Distill-Qwen-7B/14B
│
└─ 极致成本
    └─ V3.2 + 缓存命中（$0.028/M）
```

## ⚙️ 第 3 课：调参指南

### Temperature（创造性 vs 确定性）

```python
# 任务类型 → 推荐 temperature

tasks = {
    "code_generation":   0.0,    # 代码生成：0（精确）
    "math":              0.0,    # 数学：0
    "data_extraction":   0.0,    # 数据抽取：0
    "translation":       0.3,    # 翻译：0.3
    "qa_factual":        0.3,    # 事实问答：0.3
    "chatbot":           0.7,    # 聊天：0.7
    "creative_writing":  1.0,    # 创意写作：1.0+
    "brainstorm":        1.2,    # 头脑风暴：1.2
}

resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[...],
    temperature=tasks["code_generation"]
)
```

### max_tokens 控制

```python
# 短回答（512）：摘要、分类
# 中等（2048）：解释、翻译
# 长文（4096-8192）：代码、文章
# 超长（16384+）：R1 推理 + 长文档分析

resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "..."}],
    max_tokens=8192,
    stream=True                    # 长文本必须 streaming
)
```

### Top-P + Frequency Penalty（避免重复）

```python
resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[...],
    temperature=0.7,
    top_p=0.95,                   # 默认 1.0，调低更聚焦
    frequency_penalty=0.5,        # 抑制常用词重复
    presence_penalty=0.3          # 鼓励新话题
)
```

### R1 特殊参数

```python
# R1 的 reasoning_content 在 content 之前
# 调整 max_tokens 必须预留 thinking 空间（默认 32K）

resp = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=[{"role": "user", "content": "复杂的数学证明题"}],
    max_tokens=16000,             # 留够推理 + 答案
    # R1 不支持 temperature（强制 0.6，top_p 0.95）
)

# 关闭 thinking（仅 V3.2 支持）
resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[...],
    extra_body={"thinking": {"type": "disabled"}}   # V3.2 新参数
)
```

## 🔁 第 4 课：缓存机制（省钱关键）

### Prompt Caching（自动开启）

```python
# DeepSeek 自动缓存匹配的 system + 工具定义
# 同一前缀的请求，缓存命中部分仅 $0.028/M tokens

messages = [
    {"role": "system", "content": "你是 RAG 助手，回答时引用 [1][2][3]..."},  # ← 长 system
    {"role": "user", "content": "问题 1"},
    # 后续问题只要前缀不变，cost 大幅下降
    {"role": "user", "content": "问题 2"},
]

# 命中缓存：response 会带 cached_tokens 字段
print(resp.usage.prompt_tokens_details.cached_tokens)
```

### 实战：构建缓存友好 prompt

```
✅ 推荐结构：
  [System]  ← 静态（角色 + 工具 + 格式说明）→ 缓存命中
  [User #1] ← 动态（每次新问题）
  [User #2]
  ...

❌ 错误结构：
  [System] 角色
  [User #1] 文档内容（变化）  ← 缓存失效
  [User #2] 文档内容（变化）
  [User #N] 实际问题          ← 缓存零命中
```

### 折扣时段利用

```python
# UTC 16:30 - 00:30 半价（北京时间 00:30 - 08:30）
# 批量任务、压测、生成数据集 → 放到折扣时段
import schedule

def batch_job():
    run_large_evaluation()

schedule.every().day.at("02:00").do(batch_job)   # 北京时间 2 点
```

## 🧠 第 5 课：R1 推理模型使用范式

### R1 适用场景

```
✅ 复杂数学证明、几何
✅ 多步逻辑推理、谜题
✅ 深度代码分析、调试
✅ 需要"展示思路"的场景
✅ 学术研究、论文撰写

❌ 简单问答（用 V3 即可）
❌ 高频短对话（成本高）
❌ 实时低延迟（thinking 慢）
```

### R1 Prompt 技巧

```python
# 1. 不要让 R1 "强行思考"——它本来就会
bad = "请一步一步思考这个问题：什么是 1+1？"  # R1 会觉得侮辱智商

# 2. 直接给问题，让 R1 自由发挥
good = "什么是 1+1？"  # R1 知道 1+1=2，但会展示过程

# 3. 数学 / 算法题：让 R1 验证
good = "用反证法证明 √2 是无理数"

# 4. 编程题：让 R1 写出测试用例
good = "写一个 LRU Cache，要求覆盖以下场景：1) 容量满时的淘汰 2) 并发访问"
```

### 解析 R1 输出

```python
# 完整解析 R1 流式响应
import re

def parse_r1_response(text):
    # R1 输出格式：<thinking>...</thinking>答案
    thinking_match = re.search(r'<thinking>(.*?)</thinking>', text, re.DOTALL)
    thinking = thinking_match.group(1) if thinking_match else ""
    answer = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL).strip()
    return thinking, answer

# 或直接用 SDK 的 reasoning_content 字段
resp = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=[{"role": "user", "content": "..."}],
    stream=False
)
print("思考:", resp.choices[0].message.reasoning_content)
print("答案:", resp.choices[0].message.content)
```

## 🛡️ 第 6 课：常见问题排查

### 报错 401 Unauthorized

```
❌ sk-xxx 写错 / 过期 / 余额不足
✅ 检查：
  1. API Key 是否复制完整（区分大小写）
  2. platform.deepseek.com 余额是否 < 0
  3. base_url 写没写错（https://api.deepseek.com/v1）
```

### 报错 429 Rate Limit

```
❌ QPS 超限（默认 50 QPS，企业可提）
✅ 解决：
  1. 客户端加 retry + exponential backoff
  2. 申请企业级配额
  3. 多 Key 轮询
```

### R1 输出格式错乱

```
❌ 没解析 thinking 标签就展示给用户
✅ 解决：
  1. 用 reasoning_content 字段（推荐）
  2. 或正则解析 <thinking>...</thinking>
  3. UI 上折叠 thinking，只展开答案
```

### vLLM 显存 OOM

```bash
# 报错 CUDA out of memory
✅ 解决（按优先级）：
  1. 调小 --max-model-len（如 16384 → 8192）
  2. 调小 --gpu-memory-utilization（0.9 → 0.85）
  3. 启用 --enable-prefix-caching（节省 KV cache）
  4. 切到量化版本（AWQ / GPTQ）
  5. 加 GPU（多卡 tensor-parallel）
```

### Ollama 跑模型慢

```bash
# 报错或卡顿
✅ 排查：
  1. ollama ps                # 看显存占用
  2. nvidia-smi               # 看 GPU 利用率
  3. 模型是否量化（默认 Q4_K_M）
  4. 上下文是否过长
  5. macOS 用 Metal GPU 加速
```

## 🔄 第 7 课：迁移指南（从其他模型到 DeepSeek）

### 从 OpenAI 迁移

```python
# 只需改两个参数！
-client = OpenAI(api_key="sk-openai-xxx")
+client = OpenAI(
+    api_key="sk-deepseek-xxx",
+    base_url="https://api.deepseek.com/v1"
+)
-model="gpt-4o"
+model="deepseek-chat"
```

### 从 Anthropic 迁移

```python
# 用 OpenAI SDK 适配（手动构造消息）
def to_openai_messages(anthropic_msgs):
    # Anthropic system 在顶层，OpenAI 在 messages 里
    openai_msgs = []
    if "system" in anthropic_msgs:
        openai_msgs.append({"role": "system", "content": anthropic_msgs["system"]})
    for m in anthropic_msgs["messages"]:
        openai_msgs.append(m)
    return openai_msgs

# tools 格式：Anthropic input_schema → OpenAI parameters
def to_openai_tools(anthropic_tools):
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["input_schema"]
            }
        }
        for t in anthropic_tools
    ]
```

### 从其他开源模型迁移（vLLM）

```bash
# 启动命令几乎一样，只需换 model
-vllm serve meta-llama/Meta-Llama-3-8B-Instruct
+vllm serve deepseek-ai/DeepSeek-V3

# 注意：
# 1. tokenizer / chat_template 自动加载
# 2. R1 模型需要 reasoning parser（vllm 内置）
# 3. MoE 模型加 --enable-expert-parallel
```

## 📊 第 8 课：成本优化清单

```python
# 1. 用 prompt caching
#    节省 50-80% 成本（重复 system）

# 2. 选对模型
#    简单任务用 V3（$0.27/M），别用 R1（$0.55/M）

# 3. 折扣时段跑批
#    0.5x off（北京时间 00:30-08:30）

# 4. max_tokens 限制
#    别默认 4096，按需设置

# 5. 流式 vs 非流式
#    流式首 token 快 200ms+

# 6. 本地小模型替代
#    高频短问答用 Ollama R1-Distill-7B

# 7. 批量 + async
#    asyncio.gather 并发 50 个
```
