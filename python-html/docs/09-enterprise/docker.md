---
title: Docker 部署
---

# 🐳 Docker 部署

> **Docker** 是 Python 应用**容器化部署**的标准方式。本章详解 Python 应用的 Docker 实践。

## 🎯 Docker 基础

### 核心概念

```
镜像（Image）：只读模板（应用 + 依赖）
容器（Container）：镜像的运行实例
Dockerfile：构建镜像的脚本
仓库（Registry）：存储镜像（Docker Hub、阿里云等）
```

### 镜像 vs 容器

```
镜像 = 类（模板）
容器 = 对象（实例）

一个镜像可以创建多个容器
每个容器都是独立的运行环境
```

## 🚀 Dockerfile 基础

### 最小化 Python 镜像

```dockerfile
# 1. 选择基础镜像
FROM python:3.11-slim

# 2. 设置工作目录
WORKDIR /app

# 3. 复制依赖文件
COPY requirements.txt .

# 4. 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 5. 复制应用代码
COPY . .

# 6. 暴露端口
EXPOSE 8000

# 7. 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 多阶段构建（推荐）

```dockerfile
# 阶段 1：构建
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 阶段 2：运行（只复制构建结果）
FROM python:3.11-slim

WORKDIR /app
# 从 builder 阶段复制已安装的包
COPY --from=builder /root/.local /root/.local
# 确保脚本能找到用户安装的包
ENV PATH=/root/.local/bin:$PATH

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 优化镜像大小

```dockerfile
# ❌ 大镜像：~1GB
FROM python:3.11

# ✅ 小镜像：~150MB
FROM python:3.11-slim

# ✅✅ 更小：~50MB（Alpine）
FROM python:3.11-alpine

# ✅✅✅ 多阶段构建：~100MB
FROM python:3.11-slim AS builder
...
FROM python:3.11-slim
```

## 🛠️ 实战：完整 Python 应用 Dockerfile

```dockerfile
# 多阶段构建
# ============ 阶段 1：构建依赖 ============
FROM python:3.11-slim AS builder

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制并安装 Python 依赖
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .
# 如果需要打包
RUN python -m build

# ============ 阶段 2：运行 ============
FROM python:3.11-slim AS runtime

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建非 root 用户
RUN useradd --create-home --shell /bin/bash app

WORKDIR /app

# 从 builder 复制已安装的包
COPY --from=builder /root/.local /home/app/.local
COPY --from=builder /build /app

# 设置权限
RUN chown -R app:app /app /home/app
USER app

# 设置环境变量
ENV PATH=/home/app/.local/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🚀 构建和运行

```bash
# 构建镜像
docker build -t myapp:1.0.0 .

# 查看镜像
docker images | grep myapp

# 运行容器
docker run -d \
    --name myapp \
    -p 8000:8000 \
    -e DATABASE_URL=postgresql://... \
    -e REDIS_URL=redis://... \
    myapp:1.0.0

# 查看日志
docker logs myapp

# 进入容器
docker exec -it myapp /bin/bash

# 停止
docker stop myapp
docker rm myapp
```

## 📝 Docker Compose（多容器）

```yaml
# docker-compose.yml
version: "3.8"

services:
  web:
    build: .
    image: myapp:1.0.0
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:5432/mydb
      - REDIS_URL=redis://redis:6379/0
      - DEBUG=False
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
    networks:
      - app-network
    volumes:
      - ./logs:/app/logs

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=myuser
      - POSTGRES_PASSWORD=mypass
      - POSTGRES_DB=mydb
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    networks:
      - app-network
    volumes:
      - redis-data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - web
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  postgres-data:
  redis-data:
```

```bash
# 启动所有服务
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f web

# 停止所有
docker-compose down

# 重新构建
docker-compose build

# 进入容器
docker-compose exec web /bin/bash
```

## 🔧 Python 应用 Docker 化实战

### 1. 项目结构

```
myproject/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   ├── services/
│   └── models/
├── tests/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
└── .env
```

### 2. .dockerignore

```
# 排除不必要文件
.git
.gitignore
.env
.env.*
*.log
__pycache__
*.pyc
*.pyo
.pytest_cache
.coverage
htmlcov/
.idea/
.vscode/
*.md
LICENSE
README.md
Dockerfile
docker-compose.yml
tests/
.virtualenv/
venv/
env/
```

### 3. 多阶段构建（推荐）

```dockerfile
# 阶段 1：构建
FROM python:3.11-slim AS builder

WORKDIR /app

# 安装系统依赖（如果需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt

# 复制应用代码
COPY . /app

# 构建 wheel 包
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels .

# 阶段 2：运行
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖（curl 用于健康检查）
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建非 root 用户
RUN useradd --create-home --shell /bin/bash app

# 从 builder 复制 wheel 包
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/app /app/app

# 安装 wheel 包
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/* \
    && rm -rf /wheels

# 设置权限
RUN chown -R app:app /app
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4. .env 文件

```bash
# .env
APP_ENV=production
DATABASE_URL=postgresql://myuser:mypass@postgres:5432/mydb
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-super-secret-key
LOG_LEVEL=INFO
```

## 🔧 Docker 优化技巧

### 1. 缓存优化

```dockerfile
# 充分利用 Docker 缓存（变化少的层放前面）
FROM python:3.11-slim

# 系统依赖（很少变）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 依赖文件（偶尔变）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 应用代码（频繁变）← 这层会失效缓存
COPY . .
```

### 2. 减小镜像

```dockerfile
# 多阶段构建（推荐）
FROM python:3.11-slim AS builder
...
FROM python:3.11-slim
COPY --from=builder /app /app

# 使用 .dockerignore
# .dockerignore 中排除不必要的文件

# 清理 apt 缓存
RUN apt-get update && apt-get install -y --no-install-recommends \
    pkg \
    && rm -rf /var/lib/apt/lists/*

# 合并 RUN 命令
RUN apt-get update \
    && apt-get install -y gcc \
    && pip install -r requirements.txt \
    && rm -rf /var/lib/apt/lists/* /root/.cache
```

### 3. 多阶段构建示例

```dockerfile
# 前端构建（Node.js）
FROM node:18-alpine AS frontend-build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# 后端构建
FROM python:3.11-slim AS backend-build
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt
COPY backend/ ./

# 运行时
FROM python:3.11-slim
WORKDIR /app

# 复制构建结果
COPY --from=backend-build /root/.local /root/.local
COPY --from=backend-build /app /app
COPY --from=frontend-build /app/dist /app/static

ENV PATH=/root/.local/bin:$PATH
CMD ["gunicorn", "app.main:app", "-b", "0.0.0.0:8000", "-w", "4"]
```

## 🔧 Kubernetes 部署

### Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  labels:
    app: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
        - name: myapp
          image: myapp:1.0.0
          ports:
            - containerPort: 8000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: myapp-secrets
                  key: database-url
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
```

### Service

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp
  ports:
    - port: 80
      targetPort: 8000
  type: LoadBalancer
```

## 🛠️ 实战：CI/CD 部署

```yaml
# .github/workflows/deploy.yml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t myregistry/myapp:${{ github.sha }} .
      
      - name: Push to Registry
        run: |
          echo "${{ secrets.REGISTRY_PASSWORD }}" | docker login -u ${{ secrets.REGISTRY_USER }} --password-stdin
          docker push myregistry/myapp:${{ github.sha }}
      
      - name: Deploy to K8s
        run: |
          kubectl set image deployment/myapp myapp=myregistry/myapp:${{ github.sha }}
          kubectl rollout status deployment/myapp
```

## 🎯 总结

**Docker 部署核心要点**：
- ✅ 多阶段构建（减小镜像）
- ✅ .dockerignore 排除不必要文件
- ✅ 非 root 用户（安全）
- ✅ Docker Compose（多容器编排）
- ✅ 健康检查
- ✅ 环境变量管理（.env）
- ✅ Kubernetes 部署（生产）
- ⚠️ 镜像大小优化（slim / alpine）
- ⚠️ 缓存层（合理利用）
- ⚠️ 避免在容器中存储数据（用 volume）

**下一步：** [🔍 日志与监控](/09-enterprise/logging) — 可观测性
