---
title: BuildKit
---

# BuildKit — 现代容器构建引擎

> <span class="kg-badge kg-badge--container">容器 FS</span>
> 并行构建 · 缓存优化 · 多前端多后端

BuildKit 是 Docker 公司开发、Moby 项目孵化的下一代镜像构建工具。它有：

- **并行构建**：依赖自动 DAG 化
- **高级缓存**：本地 / registry / inline 多种
- **mount / ssh / secret**：构建期挂载
- **多平台构建**：arm64 / amd64 / windows 同时

## 1. 为什么 BuildKit 比老 builder 快

老 builder（docker build）：

- **线性串行**：一层一层走
- **无并行**：CPU 浪费
- **缓存粗粒度**：整层复用
- **无 context-aware**：本地 vs remote 无法区分

BuildKit：

- **DAG 并行**：互不依赖的层并行
- **缓存多源**：可同时用本地 + registry cache
- **精细缓存**：文件级别（--mount=type=cache）
- **懒求值**：仅需要的资源被构建

## 2. 启用 BuildKit

### 2.1 Docker Desktop

Docker 23+ 默认启用。

### 2.2 Linux 上启用

```bash
# 方法 1：环境变量
export DOCKER_BUILDKIT=1
docker build -t myapp .

# 方法 2：daemon 配置（永久）
# /etc/docker/daemon.json
{
  "features": {
    "buildkit": true
  }
}
systemctl restart docker
```

### 2.3 buildctl standalone

```bash
wget https://github.com/moby/buildkit/releases/download/v0.13.0/buildkit-v0.13.0.linux-amd64.tar.gz
tar -xzf buildkit-v0.13.0.linux-amd64.tar.gz
cp bin/buildctl buildkitd /usr/local/bin/

# 启动 daemon
buildkitd &

# 构建
buildctl build \
    --frontend dockerfile.v0 \
    --local context=. \
    --local dockerfile=. \
    --output type=docker,name=myapp:latest \
    --export-cache type=local,dest=/tmp/cache
```

## 3. 高级特性

### 3.1 --mount=type=cache

构建期缓存，**不入最终镜像**：

```dockerfile
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
```

效果：

- 第一次构建：装包 + 缓存到 /root/.cache/pip
- 第二次构建：缓存命中，秒级
- 最终镜像：**不包含** /root/.cache/pip（避免镜像膨胀）

### 3.2 --mount=type=ssh

构建时使用 ssh agent（如访问私有 git）：

```dockerfile
RUN --mount=type=ssh \
    git clone git@github.com:private/repo.git
```

```bash
docker build --ssh default .
```

### 3.3 --mount=type=secret

构建时使用 secret（如私钥），**不入镜像**：

```dockerfile
RUN --mount=type=secret,id=npmrc,dst=/root/.npmrc \
    npm install
```

```bash
docker build --secret id=npmrc,src=$HOME/.npmrc .
```

### 3.4 --mount=type=bind

挂载主机目录到构建容器：

```dockerfile
FROM golang:1.22
WORKDIR /src
RUN --mount=type=bind,target=/src \
    --mount=type=cache,target=/root/.cache/go-build \
    go build -o /app
```

**好处**：本地源码改动实时生效（无需 docker cp）。

### 3.5 多平台构建

```bash
docker buildx create --name multi --use

docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --push -t myorg/myapp:v1 .
```

### 3.6 BuildKit 输出（output）

```bash
# 输出到镜像
--output type=image,name=myapp:latest,push=true

# 输出到 tar
--output type=tar,dest=./myapp.tar

# 输出到本地目录（OCI layout）
--output type=oci,dest=./oci
```

## 4. BuildKit 前端（Frontend）

```bash
# Docker 前端（默认）
buildctl build --frontend dockerfile.v0

# 远程 Dockerfile
buildctl build --frontend dockerfile.v0 --opt filename=Dockerfile.dev

# 自定义前端（自定义构建流程）
buildctl build --frontend gateway.v0 --opt source=...
```

## 5. BuildKit 与 OCI Image Layout

```bash
# BuildKit 直接输出 OCI Layout
buildctl build --output type=oci,dest=./myapp-oci .

# 用 oras 推到任意 registry
oras push myreg.example.com/myapp:v1 \
    --manifest-type application/vnd.oci.image.manifest.v1+json \
    ./myapp-oci/index.json:application/vnd.oci.image.index.v1+json

# 或用 BuildKit 直接 push
buildctl build --output type=image,name=myreg.example.com/myapp:v1,push=true .
```

## 6. 缓存策略

### 6.1 推送缓存到 Registry

```bash
docker buildx build \
    --cache-to type=registry,ref=myreg.example.com/cache/myapp:cache,mode=max \
    --cache-from type=registry,ref=myreg.example.com/cache/myapp:cache \
    --push -t myorg/myapp:v1 .
```

`mode=max` = 所有中间层都缓存；`mode=min` = 只缓存最终层。

### 6.2 多 cache source

```bash
docker buildx build \
    --cache-from type=registry,ref=cache:v1 \
    --cache-from type=gha \
    --cache-from type=local,src=/tmp/cache \
    -t myapp:latest .
```

多源按顺序查找。

## 7. Dockerfile 语法（新）

```dockerfile
# syntax=docker/dockerfile:1.7

FROM --platform=$BUILDPLATFORM golang:1.22 AS builder
ARG TARGETOS
ARG TARGETARCH
WORKDIR /src
COPY . .
RUN --mount=type=cache,target=/go/pkg/mod \
    CGO_ENABLED=0 GOOS=$TARGETOS GOARCH=$TARGETARCH \
    go build -o /app

FROM alpine:3.19
COPY --from=builder /app /app
```

`# syntax=` 必须放在第一行，启用对应版本的解析器。

## 8. 实战：buildx 高级用法

```bash
# 创建 builder（支持 docker-container driver）
docker buildx create --name mybuilder --driver docker-container --use

# 启动并配置
docker buildx inspect mybuilder

# 构建（缓存到本地）
docker buildx build \
    --cache-to type=local,dest=/tmp/buildx-cache \
    --cache-from type=local,src=/tmp/buildx-cache \
    -t myapp:latest --load .
```

## 9. CI/CD 集成

### 9.1 GitHub Actions

```yaml
- uses: docker/setup-buildx-action@v3

- uses: docker/build-push-action@v5
  with:
    push: true
    tags: user/app:latest
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

### 9.2 GitLab CI

```yaml
build:
  image: docker:24
  services: [docker:24-dind]
  variables:
    DOCKER_BUILDKIT: 1
  script:
    - docker buildx create --use
    - docker buildx build --cache-to type=inline --cache-from type=registry,ref=registry.gitlab.com/myapp/cache:latest -t registry.gitlab.com/myapp:latest --push .
```

## 10. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| BuildKit = 现代 builder | "BuildKit=新代" |
| --mount=cache 是核心 | "cache=构建不存层" |
| 并行构建是速度利器 | "并行=快" |
| 多平台：--platform | "多平台=amd64+arm64" |
| 缓存到 registry | "缓存=推到远端" |

## 参考

- BuildKit GitHub：<https://github.com/moby/buildkit
- docker buildx 文档
- Dockerfile 前端规范


<!-- auto-enrich:do-not-edit -->

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
