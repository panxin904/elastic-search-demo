---
title: Docker 镜像分层
---

# Docker 镜像与分层 — Union FS 的工程化

> <span class="kg-badge kg-badge--container">容器 FS</span>
> Dockerfile 指令 → 层 · 缓存复用 · 关键优化点

Docker 镜像本质是**一系列只读层**的叠加，每一层对应 Dockerfile 的一条（或几条）指令。理解分层 = 理解镜像体积、构建速度、缓存效率。

## 1. 镜像结构

一个镜像由**多层只读目录** + **配置（manifest + config + index）** 构成：

```jsonc
// docker image inspect alpine
{
  "RootFS": {
    "Type": "layers",
    "Layers": [
      "sha256:abc...",   // 镜像层 1（基础包）
      "sha256:def...",   // 镜像层 2（python 安装）
      "sha256:xyz..."    // 镜像层 3（COPY app）
    ]
  },
  "Config": {
    "Cmd": ["python", "/app/main.py"],
    "Env": ["PATH=..."],
    "WorkingDir": "/app"
  }
}
```

存储布局（OverlayFS 驱动）：

```
/var/lib/docker/overlay2/
├── abc.../diff       # 镜像层 1 目录
├── def.../diff       # 镜像层 2 目录
├── xyz.../diff       # 镜像层 3 目录
├── <容器ID>/diff     # 容器可写层
└── <容器ID>/merged   # 挂载点（不占空间）
```

## 2. Dockerfile 指令与层

每个指令产生一个层（除了 `CMD`、`LABEL`、`ENV` 等元数据指令）：

```dockerfile
FROM ubuntu:22.04          # 层 1：基础系统
RUN apt-get update         # 层 2：apt 索引
RUN apt-get install -y python3  # 层 3：python 包
COPY app/ /app/            # 层 4：应用代码
RUN pip install -r requirements.txt  # 层 5：python 依赖
EXPOSE 8080
CMD ["python", "/app/main.py"]
```

**层只增不改**——每个层在创建时算 hash（内容寻址）。

## 3. 缓存机制

构建过程有**缓存复用**：

- 当前层之前的所有层 hash 都没变 → 跳过，直接复用缓存
- 任意一层 hash 变了 → 之后所有层**全部重跑**

```
FROM ubuntu:22.04       # 缓存命中
RUN apt-get update      # 缓存命中
COPY app/ /app/         # ← 这里改了 → 缓存失效
RUN pip install ...     # 缓存失效，重跑
```

## 4. 关键优化点

### 4.1 合并 RUN 减少层

```dockerfile
# 反例（3 层）
RUN apt-get update
RUN apt-get install -y python3
RUN apt-get clean

# 优化（1 层）
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

### 4.2 顺序优化：变化少 → 变化多

```dockerfile
# 优化前：改代码 → 重装依赖（慢）
FROM python:3.11
COPY . /app
RUN pip install -r /app/requirements.txt
COPY ./src /app/src

# 优化后：依赖先装（缓存命中）
FROM python:3.11
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
COPY . /app
```

### 4.3 用 .dockerignore

```
.git
node_modules
__pycache__
*.log
.env
```

减少构建上下文大小 = 减少 COPY 时间。

### 4.4 多阶段构建

```dockerfile
# 构建阶段（大镜像）
FROM golang:1.22 AS builder
WORKDIR /src
COPY . .
RUN go build -o /app

# 运行阶段（极小镜像）
FROM alpine:3.19
COPY --from=builder /app /app
CMD ["/app"]
```

最终镜像只有 10MB（alpine + 二进制），但编译用了 1GB 工具链。

### 4.5 BuildKit（更聪明）

```dockerfile
# syntax=docker/dockerfile:1.7

FROM alpine:3.19 AS base
RUN apk add --no-cache python3

FROM base AS builder
RUN pip install --user some-package

FROM base
COPY --from=builder /root/.local /root/.local
```

BuildKit 提供：

- 真正的并行构建
- `--mount=type=cache`：构建期缓存（apt index、pip cache）
- `--mount=type=ssh`：ssh agent forward
- `--mount=type=secret`：secret 不入层

```dockerfile
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
```

## 5. 镜像瘦身

### 5.1 选小基础镜像

| 基础镜像 | 大小 |
|----------|------|
| ubuntu:22.04 | ~70 MB |
| debian:12-slim | ~30 MB |
| alpine:3.19 | **~7 MB** |
| scratch | 0（自己 link） |
| distroless | ~20 MB（Google 维护） |

### 5.2 清理 apt cache

```dockerfile
RUN apt-get update && apt-get install -y \
        python3 \
    && rm -rf /var/lib/apt/lists/*
```

### 5.3 用 dive 工具分析层

```bash
# 安装 dive
brew install dive

# 分析镜像
dive your-image:tag
```

dive 显示每一层的内容、大小、文件树。

### 5.4 压缩历史层

```bash
# Docker 1.13+ 只能 squash（合并为单层）
docker build --squash .

# BuildKit 提供同样的能力
```

## 6. 实战：多架构镜像

```dockerfile
FROM --platform=$TARGETPLATFORM golang:1.22 AS builder
ARG TARGETPLATFORM
ARG TARGETARCH
RUN GOARCH=$TARGETARCH go build -o /app

FROM --platform=$TARGETPLATFORM alpine:3.19
COPY --from=builder /app /app
```

```bash
# 用 buildx 同时构建 amd64 + arm64
docker buildx build --platform linux/amd64,linux/arm64 \
    -t myorg/myapp:v1 \
    --push .
```

## 7. 实战：镜像分发

### 7.1 推送到 Registry

```bash
docker login registry.example.com
docker build -t registry.example.com/myorg/myapp:v1 .
docker push registry.example.com/myorg/myapp:v1
```

### 7.2 用 ORAS 推 OCI artifact

```bash
oras push registry.example.com/myorg/bundle:v1 \
    --manifest-type application/vnd.oci.image.manifest.v1+json \
    file.txt:application/octet-stream
```

### 7.3 镜像导出

```bash
docker save myimage:tag -o myimage.tar
docker load -i myimage.tar
```

## 8. 实战：内容寻址与去重

Docker 用 SHA256 hash 内容寻址：

- 同样的层 → 同样的 hash → 自动去重
- 同一镜像不同 tag 共享层
- `docker pull` 只下载新层

```bash
# 看各层大小
docker history myimage:tag

# 看总占用
docker system df
```

## 9. 实战：layer-cache 在 CI

```yaml
# GitHub Actions
- uses: actions/cache@v4
  with:
    path: /tmp/.buildx-cache
    key: ${{ runner.os }}-buildx-${{ github.sha }}
    restore-keys: ${{ runner.os }}-buildx-

- name: Build
  uses: docker/build-push-action@v5
  with:
    cache-from: type=local,src=/tmp/.buildx-cache
    cache-to: type=local,dest=/tmp/.buildx-cache-new,mode=max
```

## 10. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| 每条 RUN/COPY 一个层 | "一条指令=一层" |
| 缓存复用按 hash | "Hash 一致=复用" |
| 顺序：变化少 → 变化多 | "不变在前，变在后" |
| 多阶段 = 极小镜像 | "多阶段=瘦身" |
| BuildKit 是当前推荐 | "BuildKit=现代" |

## 参考

- Docker 官方 Dockerfile 最佳实践
- BuildKit 文档：<https://github.com/moby/buildkit>
- dive 工具：<https://github.com/wagoodman/dive>

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [linux](https://java-px.bot.cd/linux/):Linux 文件系统
- [observability](https://java-px.bot.cd/observability/):存储监控
- [postgresql](https://java-px.bot.cd/postgresql/):PG 存储引擎
