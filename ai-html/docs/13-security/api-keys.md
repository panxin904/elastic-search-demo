---
title: API Key 管理
---

# API Key 管理

> 密钥泄露 = 钱被刷光 + 数据被爬。**必须**规范化管理。

## 🤔 常见坑

```
❌ 提交到 git
❌ .env 上传云
❌ 写在前端代码
❌ 团队共用 1 把 key
❌ 不轮换
❌ 没有用量监控
```

## 🔐 最佳实践

### 1. 永远不硬编码

```python
# ❌ 死
api_key = "sk-..."

# ✅ 读环境变量
import os
api_key = os.getenv("ANTHROPIC_API_KEY")

# ✅ 用 .env 文件（不 commit）
from dotenv import load_dotenv
load_dotenv()  # 读 .env
api_key = os.getenv("ANTHROPIC_API_KEY")
```

### 2. .env 模板

```bash
# .env.example（commit 进去）
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=sk-...
DEEPSEEK_API_KEY=sk-...
GITHUB_TOKEN=ghp-...
HUGGINGFACE_TOKEN=hf_...

# .env（git ignore，填真值）
ANTHROPIC_API_KEY=sk-ant-api03-xxx
```

```gitignore
# .gitignore
.env
.env.local
.env.*.local
```

### 3. 不同环境用不同 key

```python
import os

KEYS = {
    "dev":   "sk-dev-xxx",
    "staging":"sk-stg-xxx",
    "prod":  "sk-prod-xxx",
}

env = os.getenv("APP_ENV", "dev")
api_key = KEYS[env]
```

### 4. 团队按角色发 key

```
Owner: full access, $1000 预算
Dev: read + write 自己的应用, $100 预算
QA: read only, $50
CI/CD: build + deploy, $500 with spending limits
```

OpenAI 团队版支持。Anthropic Console 支持 org + workspace + 角色。

## 🔑 轮换 + 监控

```python
# Anthropic
import anthropic

client = anthropic.Anthropic()
# 轮换（admin 操作）：
# 1. 在 Console 创建新 key
# 2. 更新环境变量 / secret
# 3. 旧 key 保留 1-2 周后删
```

```python
# OpenAI
# 1. 创建新 key（Console / API）
# 2. 测试 → 切换 → 旧 key 删
# 提示：建"备用 key" 用于切换
```

```bash
# OpenAI 设用量告警（Console → Usage limits）
# 单次 / 月上限

# Anthropic 设工作区预算
# Workspace → Limits → Monthly budget
```

## 🛡 存储

```python
# 1. AWS Secrets Manager
import boto3
sm = boto3.client("secretsmanager")
secret = sm.get_secret_value(SecretId="openai/key")
api_key = secret["SecretString"]

# 2. HashiCorp Vault
import hvac
client = hvac.Client(url="https://vault:8200", token=...)
api_key = client.secrets.kv.v2.read_secret_version(
    path="ai/openai"
)["data"]["data"]["key"]

# 3. GCP Secret Manager
from google.cloud import secretmanager
client = secretmanager.SecretManagerServiceClient()
name = "projects/proj/secrets/openai/versions/latest"
api_key = client.access_secret_version(name=name).payload.data
```

## 🔍 扫描泄露

```bash
# 1. GitHub secret scanning（自动开启）
# Settings → Code security → Enable secret scanning

# 2. pre-commit hook（本地）
pip install detect-secrets
cat > .pre-commit-config.yaml <<EOF
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
EOF
pre-commit install

# 3. 工具：gitleaks / trufflehog
brew install gitleaks
gitleaks detect --source .

pip install truffleHog
trufflehog git file://. --only-verified
```

## 🔄 加密 + 备份

```python
# 1. Sealed Secrets（k8s）
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.18.0/controller.yaml
kubeseal --format yaml < secret.yaml > sealed-secret.yaml

# 2. External Secrets Operator
# （从 Vault / AWS SM / GCP SM 同步到 k8s Secret）

# 3. SOPS（YAML / JSON 加密）
brew install sops
sops --encrypt --age age1xxx... .env > .env.enc
# 提交 .env.enc 到 git
# 提交 .sops.yaml 规则

# 解密
sops --decrypt .env.enc
```

## 📊 监控

```python
# 1. OpenAI Usage API
import openai
client = OpenAI()
usage = client.beta.usage.list(limit=7)  # 最近 7 天

# 2. OpenAI / Anthropic 自带 console 告警
# 3. 自建（langfuse / lunary）
```

```python
# langfuse
from langfuse.decorators import observe
@observe()
def llm_call(prompt):
    return openai.chat.completions.create(...)
# 自动记录所有调用 + token + cost
```

## 🛡 实战

```python
# .env 文件管理 + vault 同步
# 1. 写代码
from openai import OpenAI
import os

# 2. 启动时拉
def get_api_key():
    env = os.getenv("APP_ENV", "dev")
    # dev 从 .env
    if env == "dev":
        return os.getenv("OPENAI_API_KEY")
    # prod 从 vault
    import hvac
    client = hvac.Client(...)
    return client.secrets.kv.v2.read_secret_version(
        path=f"ai/{env}/openai"
    )["data"]["data"]["key"]

# 3. 监控用量
# - 每日 cron 拉 usage → 告警 > 80% 预算
```

## 🔗 下一步

- [Guardrails / Content Safety](/13-security/guardrails)
- [成本控制 / Token](/13-security/cost)
- [Secret 管理（k8s）](#)