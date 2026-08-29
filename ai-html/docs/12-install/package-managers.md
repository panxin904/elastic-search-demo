---
title: pip / brew / npm 安装
date: 2026-08-15  # date-auto-injected
---

# 包管理器安装

> 装 AI SDK / 工具集。**最常用**：pip（Python）/ brew（macOS）/ npm（Node.js）。

## 🐍 pip / pipx / uv（Python）

```bash
# pip（标准）
pip install openai anthropic langchain

# pipx（隔离应用）
pipx install openai-codex
pipx install aider-chat
pipx run --spec langchain-cli

# uv（极快的 Python 包管理）
curl -LsSf https://astral.sh/uv/install.sh | sh
uv pip install openai

# 特定版本
pip install openai==1.50.0

# 升级
pip install --upgrade anthropic

# 卸载
pip uninstall openai
```

## 🍺 brew（macOS / Linux）

```bash
# 装 AI 工具
brew install --cask claude-code
brew install --cask cursor
brew install --cask ollama
brew install aider-chat
brew install codex

# 装 Python / Node
brew install python@3.12
brew install node@20

# 升级
brew upgrade claude-code

# 搜索
brew search claude
```

## 📦 npm（Node.js）

```bash
# 全局装 AI CLI
npm install -g @anthropic-ai/claude-code
npm install -g @openai/codex
npm install -g @google/gemini-cli
npm install -g aichat
npm install -g promptfoo

# 项目内
npm install openai @anthropic-ai/sdk langchain
```

## 🐳 pipx vs pip vs venv

| | pip | pipx | venv |
|--|-----|-------|------|
| 系统装库 | ✅ | ❌ | ✅ |
| CLI 工具 | ⚠ 污染系统 | ✅ 隔离 | ❌ |
| 跨项目 | 全局 | 全局 | per-project |

```bash
# 用 venv（项目隔离）
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate

# 用 uv（更快的 venv）
uv venv
uv pip install openai
```

## 🔧 requirements.txt

```txt
# requirements.txt
openai>=1.50.0
anthropic>=0.40.0
langchain>=0.3
langchain-openai>=0.2
langgraph>=0.2
tiktoken>=0.8
chromadb>=0.5
pydantic>=2.8
```

```bash
# 装
pip install -r requirements.txt

# 锁定版本（生产）
pip freeze > requirements.lock
pip install -r requirements.lock
```

## 🪟 Node 版本管理

```bash
# nvm（Node Version Manager）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40/install.sh | bash
nvm install 20
nvm use 20
node --version

# 或 fnm（更快）
fnm install 20
fnm use 20
```

## 🐍 Python 版本管理

```bash
# pyenv
curl https://pyenv.run | bash
pyenv install 3.12
pyenv global 3.12

# 或 conda
conda create -n ai python=3.12
conda activate ai
conda install openai langchain

# 或 uv（推荐）
uv python install 3.12
uv venv --python 3.12
```

## 🐳 Docker 装 AI 工具

```bash
# Ollama
docker run -d --gpus all -p 11434:11434 \
  -v ollama:/root/.ollama \
  --name ollama --restart always \
  ollama/ollama

# Open WebUI（Ollama UI）
docker run -d -p 3000:8080 \
  --link ollama \
  -e OLLAMA_BASE_URL=http://ollama:11434 \
  ghcr.io/open-webui/open-webui:main

# Dify
docker run -d -p 80:80 \
  -v dify:/app/api/storage \
  langgenius/dify
```

## 🔐 私有包 / 镜像源

```bash
# pip 镜像
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
# 国内加速

# npm 镜像
npm config set registry https://registry.npmmirror.com

# Docker 镜像
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<EOF
{
  "registry-mirrors": ["https://mirror.example.com"]
}
EOF
```

## 🛠 实战

```bash
# 1. 装 Python 项目
uv venv && source .venv/bin/activate
uv pip install openai anthropic langchain langgraph

# 2. 装 Node CLI
npm i -g @anthropic-ai/claude-code

# 3. 跑 Ollama
docker run -d --gpus all -p 11434:11434 ollama/ollama
docker exec -it ollama ollama pull qwen2.5

# 4. 跑 Dify
docker run -d -p 80:80 langgenius/dify
```

## 🆚 全局装 vs 隔离装

| 场景 | 用 |
|------|-----|
| 临时试 | pip / npm 全局 |
| CLI 工具（aider / codex） | **pipx** / brew |
| 项目开发 | venv / uv |
| 服务部署 | Docker |
| 团队开发 | 项目级 venv / requirements.txt |

## 🔗 下一步

- [Docker 一键部署](/12-install/docker)
- [CUDA / GPU 环境](/12-install/cuda-gpu)
- [Claude Code / OpenCode](/02-coding-tools/claude-code)