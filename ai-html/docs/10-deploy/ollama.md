---
title: Ollama 本地推理
---

# Ollama - 一行命令跑 LLM

> **最简单**的本地推理工具。装好 = 拉模型 = 跑。Mac / Linux / Windows 都支持。

## 📦 安装

```bash
# macOS
brew install ollama
brew services start ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows：下载 ollama.exe
# https://ollama.com/download

# 看版本
ollama --version

# 看跑的模型
ollama ps
ollama list
```

## 🚀 跑模型

```bash
# 拉 + 跑（自动）
ollama run llama3
ollama run qwen2.5:7b
ollama run deepseek-coder-v2
ollama run llama3.2:1b    # 小模型

# 指定大小
ollama run qwen2.5:72b     # 需要 48GB 显存
ollama run qwen2.5:7b      # 8GB 显存

# 拉（不跑）
ollama pull llama3

# 删除
ollama rm llama3
```

## 🛠 OpenAI 兼容 API

```bash
# 启动服务（默认 :11434）
ollama serve

# 兼容 OpenAI API
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"     # 随便填
)

resp = client.chat.completions.create(
    model="qwen2.5",
    messages=[{"role":"user","content":"你好"}]
)
print(resp.choices[0].message.content)
```

```bash
# 用 curl
curl http://localhost:11434/api/chat -d '{
  "model": "qwen2.5",
  "messages": [{"role":"user","content":"hi"}],
  "stream": false
}'
```

## 📚 主流模型

```bash
# 拉各种
ollama pull llama3
ollama pull qwen2.5:7b
ollama pull qwen2.5:72b
ollama pull deepseek-coder-v2
ollama pull mistral
ollama pull gemma3:9b
ollama pull nomic-embed-text       # embedding
ollama pull llava:13b               # vision
ollama pull llama3.2-vision:11b
ollama pull phi3:14b
```

## 📊 量化标签

Ollama 默认**自动量化**：

| tag | 量化 | 模型大小 | 适合 |
|-----|------|---------|------|
| `:7b-q4_K_M` | 4-bit | ~4GB | 显存 6GB+ |
| `:7b-q8_0` | 8-bit | ~7GB | 显存 10GB+ |
| `:7b` | 默认 (Q4_0) | ~4GB | 显存 6GB+ |
| `:7b-fp16` | FP16 | ~14GB | 显存 16GB+ |

## 🛠 自定义模型（Modelfile）

```dockerfile
# Modelfile
FROM qwen2.5:7b

# 设定 system prompt
SYSTEM """你是"运维小助手"，专门排查 Linux / k8s 问题。
回答简洁，给命令和原因。"""

# 调整参数
PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER num_ctx 4096

# 设定模板（消息格式）
TEMPLATE """[INST] {{ .System }} {{ .Prompt }} [/INST]
{{ .Response }}"""
```

```bash
ollama create ops-bot -f Modelfile
ollama run ops-bot "k8s Pod Pending 怎么排查？"
```

## 🐚 Modelfile 常用指令

```dockerfile
FROM qwen2.5:7b               # 基础模型
SYSTEM "..."                  # 系统提示
PARAMETER temperature 0.5    # 0-1，越低越确定
PARAMETER top_p 0.9         # nucleus sampling
PARAMETER top_k 40          # top-k sampling
PARAMETER num_ctx 4096      # 上下文长度
PARAMETER stop "<|im_end|>" # 停止 token
PARAMETER seed 42           # 随机种子
TEMPLATE "..."              # 消息格式
ADAPTER ...                  # LoRA adapter
LICENSE "..."               # license
MESSAGE ...                  # 初始消息
```

## 🌐 REST API

```bash
# 生成（流式）
curl http://localhost:11434/api/generate -d '{
  "model":"qwen2.5",
  "prompt":"讲个笑话"
}'

# Chat
curl http://localhost:11434/api/chat -d '{
  "model":"qwen2.5",
  "messages":[{"role":"user","content":"hi"}],
  "stream": false
}'

# Embedding
curl http://localhost:11434/api/embeddings -d '{
  "model":"nomic-embed-text",
  "prompt":"hello"
}'

# Pull
curl -X POST http://localhost:11434/api/pull -d '{"name":"qwen2.5:7b"}'

# 创建 model
curl -X POST http://localhost:11434/api/create -d '{
  "name":"my-bot",
  "modelfile":"FROM qwen2.5\nSYSTEM 你好"
}'

# 列出模型
curl http://localhost:11434/api/tags
```

## 🐍 Python SDK

```python
import ollama
# pip install ollama

# Chat
resp = ollama.chat(
    model='qwen2.5',
    messages=[{'role': 'user', 'content': '你好'}]
)
print(resp['message']['content'])

# 流式
for chunk in ollama.chat(
    model='qwen2.5',
    messages=[{'role':'user','content':'hi'}],
    stream=True
):
    print(chunk['message']['content'], end='', flush=True)

# Embedding
resp = ollama.embeddings(model='nomic-embed-text', prompt='hello')
print(len(resp['embeddings'][0]))

# Generate（单轮）
resp = ollama.generate(model='qwen2.5', prompt='讲个笑话')
print(resp['response'])
```

## 🐳 Docker

```bash
# 官方镜像（带 GPU）
docker run -d --gpus all -p 11434:11434 \
  --name ollama -v ollama:/root/.ollama \
  ollama/ollama

# 拉模型
docker exec -it ollama ollama pull qwen2.5
```

## 🔌 远程 Ollama

```python
# 远程：传 base_url
import ollama
client = ollama.Client(host='http://gpu-server:11434')
resp = client.chat(model='llama3', messages=[...])
```

## 🆚 vs vLLM

| | Ollama | vLLM |
|--|---------|------|
| 易用 | **一行跑** | 装 Python 依赖 |
| 性能 | 中 | **PagedAttention 极快** |
| 模型来源 | Ollama 库 | HuggingFace 任意 |
| 适合 | 个人 / 小流量 | **生产高并发** |
| 自定义模型 | Modelfile | 改代码 |

## 🛠 实战

```python
# 1. 起服务
ollama serve &

# 2. 用 OpenAI SDK 接
from openai import OpenAI
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

# 3. 跟 LangChain 集成
from langchain_community.chat_models import ChatOllama
llm = ChatOllama(model="qwen2.5")
```

## 🔗 下一步

- [vLLM / TGI 服务](/10-deploy/vllm-tgi)
- [API 托管](/10-deploy/hosted)
- [Claude Code / OpenCode](/02-coding-tools/claude-code)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [python](https://java-px.bot.cd/python/):Python AI
- [bigdata](https://java-px.bot.cd/bigdata/):大数据训练
- [system-design](https://java-px.bot.cd/system-design/):AI 系统架构
