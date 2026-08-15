---
title: Docker 一键部署
---

# Docker 一键部署 AI 服务

> Ollama / vLLM / Dify / Open WebUI 等**都有官方 Docker 镜像**。一行命令起。

## 🐳 Ollama

```bash
# CPU only
docker run -d --name ollama -p 11434:11434 \
  -v ollama:/root/.ollama \
  ollama/ollama

# NVIDIA GPU
docker run -d --gpus all --name ollama -p 11434:11434 \
  -v ollama:/root/.ollama \
  ollama/ollama

# 拉模型
docker exec -it ollama ollama pull qwen2.5

# 跑
docker exec -it ollama ollama run qwen2.5 "你好"
```

## 🦙 Open WebUI（Ollama 的 UI）

```bash
docker run -d -p 3000:8080 \
  --link ollama \
  -e OLLAMA_BASE_URL=http://ollama:11434 \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main
# 浏览器 http://localhost:3000
```

## 🤖 Dify（LLM 应用平台）

```bash
git clone https://github.com/langgenius/dify.git
cd dify/docker
cp .env.example .env
docker compose up -d
# 浏览器 http://localhost/install
```

## 🚀 vLLM

```bash
# CPU
docker run -d -p 8000:8000 \
  --name vllm \
  vllm/vllm-openai:latest \
  --model Qwen/Qwen2.5-7B-Instruct

# GPU
docker run -d -p 8000:8000 --gpus all \
  --name vllm \
  vllm/vllm-openai:latest \
  --model Qwen/Qwen2.5-7B-Instruct
# 客户端：
# from openai import OpenAI
# c = OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")
```

## 🐍 Chroma（向量库）

```bash
docker run -d -p 8000:8000 \
  -v chroma-data:/chroma/chroma \
  --name chroma \
  chromadb/chroma:latest
```

## 🏠 AnythingLLM（桌面 / RAG 工具）

```bash
docker run -d -p 3001:3001 \
  --name anythingllm \
  mintplex-labs/anything-llm:latest
# 浏览器 http://localhost:3001
```

## 🔥 Postgres + pgvector

```bash
docker run -d --name pgvector \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=ai \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

## 🤖 n8n（工作流）

```bash
docker run -d -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  --name n8n \
  n8nio/n8n
# 浏览器 http://localhost:5678
# n8n 是开源工作流 + AI 集成
```

## 📋 docker-compose.yml（一次起全栈）

```yaml
version: "3.9"
services:
  ollama:
    image: ollama/ollama
    runtime: nvidia
    ports: ["11434:11434"]
    volumes: ["ollama:/root/.ollama"]

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports: ["3000:8080"]
    depends_on: [ollama]
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
    volumes: ["open-webui:/app/backend/data"]

  chroma:
    image: chromadb/chroma
    ports: ["8000:8000"]
    volumes: ["chroma:/chroma/chroma"]

  pgvector:
    image: pgvector/pgvector:pg16
    environment:
      - POSTGRES_PASSWORD=secret
    ports: ["5432:5432"]
    volumes: ["pgvector:/var/lib/postgresql/data"]

networks:
  default:
    driver: bridge
```

```bash
docker compose up -d
# Ollama + WebUI + Chroma + Postgres 一键起
```

## 🔧 关键技巧

```bash
# 1. 命名卷（持久化）
docker volume create ollama
docker run -v ollama:/root/.ollama ollama/ollama

# 2. 健康检查
docker run --health-cmd "curl localhost:11434" ...

# 3. 重启策略
docker run --restart unless-stopped ...

# 4. 网络隔离
docker network create ai-net
docker run --network ai-net ...

# 5. 看资源
docker stats
```

## 🛠 实战

```bash
# 1. 起 Ollama + WebUI
docker run -d --gpus all -p 11434:11434 \
  -v ollama:/root/.ollama --name ollama ollama/ollama
docker run -d -p 3000:8080 --link ollama \
  -e OLLAMA_BASE_URL=http://ollama:11434 --name webui \
  ghcr.io/open-webui/open-webui:main
docker exec -it ollama ollama pull qwen2.5

# 浏览器 http://localhost:3000 → 选 qwen2.5 → 聊天

# 2. 起 Dify（生产）
cd /opt/dify && docker compose up -d
```

## 🔗 下一步

- [pip / brew / npm 安装](/12-install/package-managers)
- [CUDA / GPU 环境](/12-install/cuda-gpu)
- [Ollama 本地推理](/10-deploy/ollama)