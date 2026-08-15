---
title: 容器化安装
---

# 容器化安装

> 用 Docker / Podman 跑应用，避免污染宿主机，避免依赖冲突。

## 🐳 Docker 基础

```bash
# 镜像
docker pull nginx:1.25-alpine
docker images                          # 列出本地镜像
docker rmi nginx:1.25-alpine           # 删镜像
docker image prune                      # 清 dangling 镜像

# 容器
docker run -d -p 80:80 --name web nginx:1.25-alpine
docker ps                              # 运行的
docker ps -a                           # 全部（含停止）
docker stop web                        # 停
docker rm web                          # 删
docker logs -f web                     # 日志
docker exec -it web bash               # 进容器

# 系统清理
docker system prune                    # 清无用数据
docker system prune -a                 # 强清（含未用镜像）
```

## 📜 关键命令

```bash
# 后台跑 + 自动删 + 限制资源
docker run -d --rm \
  --name myapp \
  --memory 512m --cpus 1.0 \
  -p 8080:80 \
  -v /opt/data:/data \
  -e NODE_ENV=production \
  myapp:1.0

# 看资源
docker stats
docker top web

# 网络
docker network create mynet
docker run --network=mynet ...

# 看容器里跑了什么
docker exec -it web ps aux
```

## 📦 Dockerfile

```dockerfile
# 多阶段构建
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 运行镜像
FROM nginx:1.25-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🗃 docker-compose

```yaml
# docker-compose.yml
services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./html:/usr/share/nginx/html:ro
    depends_on:
      - api

  api:
    build: ./api
    environment:
      DB_HOST: db
    depends_on:
      - db

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: secret
    volumes:
      - dbdata:/var/lib/postgresql/data

volumes:
  dbdata:
```

```bash
docker compose up -d           # 启动
docker compose ps              # 状态
docker compose logs -f web     # 看日志
docker compose down            # 停 + 删容器
docker compose down -v         # 一起清卷
```

## 🦭 Podman（Docker 替代）

Rootless、安全、和 Docker CLI 兼容。

```bash
sudo apt install podman
podman run -d -p 80:80 nginx:alpine    # 无需 root
podman-compose                          # 类似 docker-compose
```

详见：Podman vs Docker — Podman 默认无 daemon，更适合 rootless。

## 🪛 实战

### 单容器部署 Node 应用

```bash
# 直接跑
docker run -d --name myapp \
  -p 3000:3000 \
  -v $(pwd):/app \
  -w /app \
  node:20-alpine \
  sh -c 'npm ci && node server.js'
```

### 数据持久化

```bash
# 卷（推荐）
docker volume create mydata
docker run -v mydata:/data myapp

# bind mount（开发）
docker run -v $(pwd)/src:/app/src myapp
```

### 多容器协作

```yaml
# Compose：web + api + db
services:
  web: { image: nginx, ports: ["80:80"] }
  api: { build: ./api, depends_on: [db] }
  db: { image: postgres:16 }
```

### 镜像优化

```dockerfile
# 选用小镜像
FROM alpine:3.19      # ~7MB
# 而不是
FROM ubuntu:24.04     # ~80MB

# 多阶段（最终镜像不带编译工具）
FROM node:20 AS builder
# ... 编译 ...
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html

# 清理缓存
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# 用 .dockerignore
# node_modules
# .git
```

## 📊 容器 vs 包管理器

| | 包管理器 | 容器 |
|--|---------|------|
| 启动速度 | 慢（要装） | 极快（秒级） |
| 隔离 | ❌ | ✅ |
| 跨环境一致 | 一般 | ✅ |
| 资源占用 | 轻 | 略重（cgroups） |
| 持久化 | 系统服务 | 卷 + bind |
| 适合场景 | 系统工具 | 应用部署 |

## 🔒 安全

```bash
# 容器逃逸最小权限
docker run --read-only --tmpfs /tmp \
  --cap-drop=ALL --security-opt=no-new-privileges \
  myapp

# 镜像扫描
docker scan myapp:1.0
trivy image myapp:1.0
```

## 🔧 清理

```bash
# 系统级
docker system prune -a --volumes

# 单容器
docker rm -f web
docker rmi nginx:1.25
```

## 🔗 下一步

- [apt (Debian/Ubuntu)](/06-package/apt)
- [yum / dnf (RHEL)](/06-package/yum-dnf)
- [源码编译](/06-package/source)