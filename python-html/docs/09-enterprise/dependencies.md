---
title: 依赖管理
date: 2026-08-15  # date-auto-injected
---

# 📦 依赖管理

> 良好的**依赖管理**是 Python 项目**可复现部署**的关键。本章介绍 pip、poetry、pdm 等主流工具。

## 🎯 依赖管理工具

```
pip + requirements.txt：标准（但简陋）
pip + requirements.in + pip-compile：哈希锁定
pipenv：pip + virtualenv 集成
poetry：现代推荐（依赖解析 + 打包）
pdm：现代推荐（PEP 582）
conda：数据科学常用
uv：新兴工具（极快，Rust 实现）
```

## 📝 工具 1：pip + requirements.txt

### 基本使用

```bash
# 导出依赖
pip freeze > requirements.txt

# 安装依赖
pip install -r requirements.txt

# requirements.txt 示例
Django==4.2.0
requests==2.31.0
numpy>=1.24.0
pandas==2.0.0
```

### 进阶：分层

```bash
# requirements/
# ├── base.txt       # 生产依赖
# ├── dev.txt        # 开发依赖（含 base）
# └── prod.txt       # 生产环境额外依赖

# dev.txt
-r base.txt
pytest==7.4.0
black==23.0.0
flake8==6.0.0

# 安装
pip install -r requirements/dev.txt
```

### pip-compile（推荐）

```bash
# 安装
pip install pip-tools

# 编译
pip-compile requirements.in

# requirements.in
django>=4.0
requests
numpy
pandas

# 编译后 requirements.txt 自动锁定版本
# 同时生成 hash 用于安全部署
pip-compile --generate-hashes requirements.in
```

## 📝 工具 2：poetry（强烈推荐）

### 安装

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### pyproject.toml

```toml
[tool.poetry]
name = "myproject"
version = "0.1.0"
description = "My awesome project"
authors = ["Alice <alice@example.com>"]
readme = "README.md"
python = "^3.9"

# 生产依赖
[tool.poetry.dependencies]
python = "^3.9"
fastapi = "^0.100.0"
uvicorn = "^0.23.0"
sqlalchemy = "^2.0.0"
pydantic = "^2.0.0"
requests = "^2.31.0"

# 开发依赖
[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
black = "^23.0.0"
mypy = "^1.4.0"
pytest-cov = "^4.1.0"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```

### 常用命令

```bash
# 安装依赖
poetry install

# 添加依赖
poetry add requests
poetry add requests@^2.31
poetry add pytest --group dev

# 移除依赖
poetry remove requests

# 更新依赖
poetry update

# 显示依赖
poetry show
poetry show --tree  # 树形显示

# 激活虚拟环境
poetry shell

# 运行命令（在虚拟环境中）
poetry run python main.py
poetry run pytest

# 导出 requirements.txt（兼容 pip）
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

## 📝 工具 3：pdm（现代 PEP 582）

### 安装

```bash
curl -sS https://bootstrap.pypa.io/get-pdm.py | python3 -
```

### 使用

```bash
# 初始化
pdm init

# 添加依赖
pdm add fastapi
pdm add -dG dev pytest  # 开发依赖

# 安装
pdm install

# 运行
pdm run python main.py
```

## 📝 工具 4：uv（极快，新兴）

```bash
# 安装
curl -LsSf https://astral.sh/uv/install.sh | sh

# 使用（兼容 pip 接口）
uv pip install requests
uv pip install -r requirements.txt
uv venv  # 创建虚拟环境
```

## 📝 pyproject.toml 完整示例

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "myproject"
version = "0.1.0"
description = "My awesome project"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [{name = "Alice", email = "alice@example.com"}]
keywords = ["web", "api", "fastapi"]

# 运行时依赖
dependencies = [
    "fastapi>=0.100.0,<1.0.0",
    "uvicorn[standard]>=0.23.0",
    "pydantic>=2.0.0",
    "sqlalchemy>=2.0.0",
    "redis>=5.0.0",
]

# 可选依赖
[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "black>=23.0",
    "mypy>=1.0",
    "ruff>=0.0.270",
]
prod = [
    "gunicorn>=21.0",
    "prometheus-client>=0.17",
]

[project.urls]
Homepage = "https://github.com/yourname/myproject"
Documentation = "https://myproject.readthedocs.io"

# 脚本入口
[project.scripts]
myproject = "myproject.main:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.black]
line-length = 100
target-version = ["py39", "py310", "py311"]

[tool.ruff]
line-length = 100
target-version = "py39"

[tool.mypy]
python_version = "3.9"
strict = true
ignore_missing_imports = true
```

## 📦 私有包管理

### 场景

```
公司有多个内部项目共享通用库（如 common-lib）
需要作为内部包管理
```

### 方案 1：path 依赖（poetry）

```toml
# 在子项目 pyproject.toml 中
[tool.poetry.dependencies]
common-lib = {path = "../common-lib"}
```

### 方案 2：私有 PyPI 服务器

```bash
# 启动 devpi
pip install devpi-server devpi-client
devpi-init
devpi-gen-secret
devpi-server --host 0.0.0.0 --port 3141

# 上传包
devpi use http://localhost:3141
devpi login root --password
devpi upload --path dist/

# 安装包
pip install -i http://localhost:3141/root/dev/+simple common-lib
```

### 方案 3：Git 依赖

```toml
# pyproject.toml
[tool.poetry.dependencies]
common-lib = {git = "https://github.com/company/common-lib.git", branch = "main"}
```

## 🛠️ 依赖安全检查

```bash
# pip-audit（推荐）
pip install pip-audit
pip-audit

# safety
pip install safety
safety check

# GitHub Dependabot（CI/CD）
# 自动检测依赖漏洞
```

## 🛠️ 实战：完整 Python 项目

### 1. pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "myproject"
version = "0.1.0"
requires-python = ">=3.9"
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.23.0",
    "pydantic>=2.0.0",
    "sqlalchemy>=2.0.0",
    "redis>=5.0.0",
    "pydantic-settings>=2.0.0",
    "python-jose>=3.3.0",
    "passlib>=1.7.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "httpx>=0.24.0",
    "black>=23.0.0",
    "ruff>=0.0.270",
    "mypy>=1.4.0",
]

[project.scripts]
myproject = "myproject.main:main"
serve = "myproject.main:serve"

[tool.setuptools.packages.find]
where = ["src"]
```

### 2. 安装依赖

```bash
# 生产依赖
pip install -e .

# 开发依赖
pip install -e ".[dev]"

# 导出 requirements.txt
pip freeze > requirements.txt
```

### 3. 锁定依赖（CI/CD）

```bash
# 用 pip-tools
pip install pip-tools
pip-compile pyproject.toml

# 输出 requirements.txt
```

## 📊 工具对比

| 工具 | 速度 | 依赖解析 | 锁文件 | 学习曲线 | 推荐 |
|------|------|---------|--------|---------|------|
| pip | 慢 | 简单 | requirements.txt | 低 | 标准 |
| pip-tools | 中 | 完善 | requirements.txt + hash | 中 | 兼容 pip |
| poetry | 中 | 优秀 | poetry.lock | 中 | 现代 |
| pdm | 快 | 优秀 | pdm.lock | 中 | 现代 |
| uv | **极快** | 兼容 | requirements.txt | 低 | 新兴 |

## 🎯 总结

**依赖管理核心要点**：
- ✅ pyproject.toml 是现代标准
- ✅ Poetry / PDM 是现代推荐
- ✅ 锁文件确保可复现部署
- ✅ 分层依赖（生产 / 开发）
- ✅ 安全审计（pip-audit）
- ✅ 私有包用 path / git 依赖
- ⚠️ 避免依赖冲突（定期更新）
- ⚠️ 锁定文件要提交到版本控制

**下一步：** [🧪 单元测试](/09-enterprise/testing) — pytest 实战
