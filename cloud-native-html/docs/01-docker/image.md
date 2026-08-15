---
title: 镜像 image
---

# Docker 镜像

> 镜像是只读模板 — 类与实例的"类"。

## 🧱 镜像分层（Union FS）

```
┌──────────┐  ← 容器运行时可写层
├──────────┤  ← RUN apt install -y xxx
├──────────┤  ← COPY ./app
├──────────┤  ← FROM node:20
└──────────┘  ← scratch / 基础镜像
```

- **只读层**：共享，复用率高
- **可写层**：容器运行时产生，commit 后变成新镜像层
- 存储驱动：overlay2 / btrfs / zfs（默认 overlay2）

## 🛠 Dockerfile

```dockerfile
# 基础镜像
FROM node:20-alpine

# 工作目录
WORKDIR /app

# 复制依赖清单（先于代码 → 缓存友好）
COPY package*.json ./
RUN npm ci --only=production

# 复制源码
COPY . .

# 暴露端口（只是声明）
EXPOSE 3000

# 启动
CMD ["node", "server.js"]
```

## 🔑 关键指令

| 指令 | 作用 |
|------|------|
| `FROM` | 基础镜像 |
| `RUN` | 跑命令（创建新层） |
| `COPY` / `ADD` | 复制文件 |
| `WORKDIR` | 工作目录 |
| `ENV` | 环境变量 |
| `EXPOSE` | 声明端口（不真正发布） |
| `CMD` | 默认启动命令（可被覆盖） |
| `ENTRYPOINT` | 启动入口（不易被覆盖） |
| `VOLUME` | 声明匿名卷 |
| `USER` | 切换用户 |
| `HEALTHCHECK` | 健康检查 |

## 🔨 构建

```bash
# 简单构建
docker build -t myapp:1.0 .

# 多个 tag
docker build -t myapp:1.0 -t myapp:latest .

# 看构建过程
docker build --progress=plain -t myapp .

# 用 BuildKit（更快）
DOCKER_BUILDKIT=1 docker build -t myapp .

# 不用缓存
docker build --no-cache -t myapp .

# 限制 .dockerignore
echo "node_modules" > .dockerignore
echo ".git" >> .dockerignore
```

## 🪜 多阶段构建

```dockerfile
# 阶段 1：构建
FROM node:20-alpine AS builder
WORKDIR /app
COPY . .
RUN npm ci && npm run build

# 阶段 2：运行（只拷贝产物）
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

最终镜像 **不包含** node_modules、构建工具，体积小（nginx 镜像 ~40MB）。

## 🏗️ 镜像命名

```
[registry/][namespace/]repository[:tag]

nginx:alpine                     # Docker Hub 官方
gcr.io/google-containers/pause   # GCR
myregistry.com:5000/myapp:1.0    # 私有仓库
```

## 📥 推送 / 拉取

```bash
# 登录
docker login
docker login myregistry.com

# tag
docker tag myapp:1.0 myregistry.com/myorg/myapp:1.0

# 推送
docker push myregistry.com/myorg/myapp:1.0

# 拉取
docker pull myregistry.com/myorg/myapp:1.0

# 离线搬运
docker save -o myapp.tar myapp:1.0
docker load -i myapp.tar
```

## 🪜 镜像优化技巧

```dockerfile
# 1. 选小基础镜像
FROM alpine:3.19                  # 5MB
# 而不是
FROM ubuntu:24.04                 # 80MB

# 2. 利用缓存（少变的先 COPY）
COPY package*.json ./
RUN npm install
COPY . .                          # 这层重 build 时不变 → 用缓存

# 3. 合并 RUN 减少层
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

# 4. 用 .dockerignore
# node_modules
# .git
# *.log

# 5. 多阶段 — 终镜像不带构建工具
```

## 🧹 清理

```bash
docker image prune                # 清 dangling
docker image prune -a             # 清所有未用
docker system prune -a            # 大扫除（⚠ 确认无重要数据）
```

## 🛠 实战

```bash
# 1. 写 Dockerfile
# 2. .dockerignore
# 3. 构建
docker build -t myapp:1.0 .
# 4. 跑测试
docker run --rm myapp:1.0 npm test
# 5. 推到 registry
docker push myregistry.com/myorg/myapp:1.0
# 6. 生产部署
kubectl create deploy myapp --image=myregistry.com/myorg/myapp:1.0
```

## 🔗 下一步

- [Docker 基础](/01-docker/intro)
- [容器 container](/01-docker/container)
- [Docker 网络](/01-docker/network)
- [Docker 存储 / 卷](/01-docker/volume)