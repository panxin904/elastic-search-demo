---
title: API 托管
---

# API 托管服务

> 不自己跑模型？用云厂商的 API。**起步快 / 弹性 / 免运维**。

## 🏆 主流托管

| 平台 | 模型 | 价格 (in/out $/MTok) | 特点 |
|------|------|---------------------|------|
| **OpenAI** | GPT-5 / GPT-4o | 5/20 / 2.5/10 | 行业标准 |
| **Anthropic** | Claude 4.5 | 3/15 (Sonnet) | 编码最强 |
| **Google AI Studio** | Gemini 2.5 | 1.25/5 | 长上下文 (1M) |
| **Vertex AI (GCP)** | 同上 | 同上 | 企业 / VPC |
| **AWS Bedrock** | 多家 | 看 model | 集成 AWS |
| **Azure OpenAI** | OpenAI | 看 model | 集成 Azure |
| **Together.ai** | 多家开源 | 便宜 | 适合大批量 |
| **Anyscale** | 开源 | 便宜 | vLLM 团队 |
| **Fireworks AI** | 多家 | 快 / 便宜 | 低延迟 |
| **Replicate** | 各种 | 看 model | 简单 |
| **OpenRouter** | 多家 | 路由 | 一个 key 多家 |
| **DeepSeek** | DeepSeek V3 | 0.14/0.28 | 极便宜 |
| **HuggingFace Inference** | 任何 | 看 model | 社区 |

## 🆚 怎么选

| 场景 | 推荐 |
|------|------|
| 通用生产 | **OpenAI** / Anthropic / Gemini |
| 编码 agent | **Anthropic Claude 4.5** |
| 中文 / 便宜 | DeepSeek / Qwen |
| 长上下文（>500K） | **Gemini 2.5** |
| 多模型路由 | **OpenRouter** / Portkey |
| 隐私 / 合规 | **AWS Bedrock** / Azure / 自部署 |
| 低成本大量推理 | **Together / Fireworks** |
| 临时实验 | OpenAI / Anthropic / Google AI Studio（都送免费额度） |

## 🚀 接入示例

### OpenAI

```python
from openai import OpenAI
client = OpenAI()  # OPENAI_API_KEY
resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role":"user","content":"hi"}]
)
```

### Anthropic（via OpenAI 兼容）

```python
from openai import OpenAI
client = OpenAI(
    base_url="https://api.anthropic.com/v1/",
    api_key="sk-ant-..."
)
resp = client.chat.completions.create(
    model="claude-sonnet-4-5",
    messages=[{"role":"user","content":"hi"}]
)
```

### OpenRouter（一 key 全部）

```python
from openai import OpenAI
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="sk-or-..."
)
# 任意模型：claude / gpt / gemini / llama / qwen...
resp = client.chat.completions.create(
    model="anthropic/claude-sonnet-4-5",
    messages=[{"role":"user","content":"hi"}]
)
```

### Together.ai

```python
from openai import OpenAI
client = OpenAI(
    base_url="https://api.together.xyz/v1",
    api_key="..."
)
resp = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
    messages=[...]
)
# 价格 $0.88 / MTok（vs Claude $3）
```

### AWS Bedrock

```python
import boto3
client = boto3.client('bedrock-runtime', region_name='us-east-1')
resp = client.converse(
    modelId='anthropic.claude-sonnet-4-5-20250929-v1:0',
    messages=[{"role":"user","content":[{"text":"hi"}]}]
)
```

## 💰 价格速查（输入 $/MTok）

| 模型 | Bedrock | Together | Fireworks | OpenRouter |
|------|---------|----------|-----------|-------------|
| Claude Sonnet 4.5 | 3 | - | - | 3 |
| GPT-4o | 2.5 | - | 2.5 | 2.5 |
| DeepSeek V3 | - | 0.88 | 0.88 | 0.14 |
| Llama 3.3 70B | 0.72 | 0.88 | 0.88 | 0.59 |
| Qwen 2.5 72B | - | 0.88 | - | 0.4 |

## 🛠 多模型路由

```python
# LiteLLM 统一接口
from litellm import completion

# 同一调用函数
def ask(prompt, model="gpt-4o", provider="openai"):
    return completion(
        model=f"{provider}/{model}",
        messages=[{"role":"user","content":prompt}]
    )

print(ask("hi", "gpt-4o", "openai"))
print(ask("hi", "claude-sonnet-4-5", "anthropic"))
print(ask("hi", "qwen2.5-7b-instruct", "together"))
```

```yaml
# litellm config.yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: sk-...
  - model_name: claude
    litellm_params:
      model: anthropic/claude-sonnet-4-5
      api_key: sk-ant-...
  - model_name: deepseek
    litellm_params:
      model: openai/deepseek-chat
      api_key: sk-...
      api_base: https://api.deepseek.com/v1
```

## 📈 成本优化

```python
# 1. Cache（重复前缀）
# Claude: cache_control
# OpenAI: prompt caching (gpt-4o)

# 2. 小模型优先
def ask(prompt):
    if is_simple(prompt):
        return completion("gpt-4o-mini", ...)   # 0.15 / MTok
    else:
        return completion("gpt-4o", ...)         # 2.5 / Mtok

# 3. Batch（多条 query 一次调）
# 4. Trim prompt
# 5. 设置 max_tokens
```

## 🛠 实战

```python
# 1. LiteLLM 代理（统一 API 入口）
# 装：pip install 'litellm[proxy]'
# 跑：litellm --config config.yaml
# 调用：http://localhost:4000/v1

# 2. 多个 Provider 失败转移
from litellm import Router
router = Router(
    model_list=[
        {"model_name": "gpt-4o", "litellm_params": {"model":"openai/gpt-4o"}},
        {"model_name": "claude", "litellm_params": {"model":"anthropic/claude-sonnet-4-5"}}
    ],
    fallbacks=[{"gpt-4o": ["claude"]}]
)
# OpenAI 限流自动切 Claude
```

## 🔗 下一步

- [Ollama 本地推理](/10-deploy/ollama)
- [vLLM / TGI 服务](/10-deploy/vllm-tgi)
- [成本控制 / Token](/13-security/cost)