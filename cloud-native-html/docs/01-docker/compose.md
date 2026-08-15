---
title: Docker Compose
---

# Docker Compose

> 多容器应用一键编排。最适合本地开发 / 单机测试 / 小规模部署。

## 🤔 为什么用 Compose

```bash
# 不靠 compose：手写一堆 docker run
docker run -d --name db -v db-data:/var/lib/postgresql/data postgres
docker run -d --name redis -p 6379:6379 redis
docker run -d --name web --link db --link redis -p 8080:80 myapp

# 用 compose：一文件搞定
docker compose up -d
```

## 📜 docker-compose.yml

```yaml
# services 顶层
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./html:/usr/share/nginx/html:ro
    depends_on:
      - api
    restart: unless-stopped

  api:
    build: ./api
    environment:
      DB_HOST: db
      DB_PORT: 5432
      REDIS_URL: redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: app
    volumes:
      - db-data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data

# 顶级 volumes
volumes:
  db-data:
  redis-data:
```

## 🔧 高频命令

```bash
docker compose up -d              # 后台启动
docker compose up --build         # 重新构建镜像再启
docker compose down               # 停 + 删容器 + 网络（保留卷）
docker compose down -v            # 停 + 删容器 + 卷（数据丢！）
docker compose ps                 # 看运行状态
docker compose logs -f            # 跟踪日志
docker compose logs -f api        # 单服务
docker compose ps -a              # 含停止的
docker compose exec api bash      # 进容器
docker compose restart api
docker compose pull               # 拉镜像更新
docker compose config             # 看实际配置
```

## 🪛 services 详细字段

| 字段 | 作用 |
|------|------|
| `image` | 用镜像 |
| `build` | 构建（路径 / Dockerfile 名） |
| `command` | 覆盖 CMD |
| `entrypoint` | 覆盖 ENTRYPOINT |
| `environment` | 环境变量 |
| `env_file` | 从文件读 env |
| `ports` | 端口映射 |
| `volumes` | 挂载 |
| `depends_on` | 启动顺序（不等待 ready，只等启动） |
| `networks` | 加入网络 |
| `restart` | 重启策略 |
| `healthcheck` | 健康检查 |
| `deploy.resources` | 资源限制 |
| `logging` | 日志配置 |
| `profiles` | 启用分组 |
| `user` | 运行用户 |
| `working_dir` | 工作目录 |
| `stdin_open` / `tty` | 交互 |

## 🩺 healthcheck（健康检查）

```yaml
services:
  web:
    image: myapp
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s      # 启动后等多久开始检查
```

```bash
docker compose ps                   # 看 STATUS（healthy / unhealthy）
```

## 🧪 profiles（分组启动）

```yaml
services:
  web:
    image: myapp
  debug-tool:
    image: alpine
    profiles: ["debug"]      # 默认不启
```

```bash
docker compose up -d                       # 不带 debug
docker compose --profile debug up          # 含 debug
```

## 🔐 .env 文件

```bash
# .env
DB_PASSWORD=secret
DB_PORT=5432
```

```yaml
services:
  db:
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_PORT: ${DB_PORT}
```

`.env` 默认自动加载，**不要 commit**（.gitignore）。

## 🛠 实战

### 本地开发

```bash
# 启动开发栈
docker compose up -d

# 看日志
docker compose logs -f api

# 进容器
docker compose exec db psql -U postgres

# 重启单个
docker compose restart web

# 重建镜像
docker compose build web
```

### 多个 compose 文件

```bash
# 基础 + 覆盖
docker compose -f docker-compose.yml -f docker-compose.override.yml up
```

常用：
- `docker-compose.yml` — 基础
- `docker-compose.override.yml` — 本地覆盖
- `docker-compose.prod.yml` — 生产
- `docker-compose.test.yml` — 测试

## 🆚 Compose vs k8s

| | Compose | Kubernetes |
|--|---------|-------------|
| 适合 | 单机 / 开发 / 小部署 | 多机 / 生产 |
| 规模 | 1 台机器 | 几百到几千节点 |
| 自愈 | 部分（restart 策略） | 完整（副本、滚动） |
| 网络 | bridge | 完整 overlay |
| 服务发现 | 容器名 | Service / DNS |
| 升级 | down + up | 滚动 / 蓝绿 / 金丝雀 |
| 学习曲线 | 平 | 陡 |

**生产用 k8s**。Compose 是开发 / 小规模。

## 🔗 下一步

- [Docker 基础](/01-docker/intro)
- [Docker 网络](/01-docker/network)
- [Docker 存储 / 卷](/01-docker/volume)
- [k8s 是什么](/02-k8s-arch/overview)