---
title: Docker 存储 / 卷
---

# Docker 存储 / 卷

> 容器是 ephemeral（短命）的，文件改动默认随容器删除消失。要保留数据：用卷。

## 🤔 为什么需要卷

```
docker run alpine touch /tmp/a    # 容器删了 → /tmp/a 没了
docker run -v /data alpine touch /data/a   # /data 在主机，保留
```

## 📦 三种挂载方式

```bash
# 1. 命名卷（推荐）— Docker 管理
docker volume create mydata
docker run -v mydata:/data alpine

# 2. 匿名卷 — 容器删了卷还在（无名字）
docker run -v /data alpine         # 自动创建 hash 名的卷

# 3. bind mount — 主机目录直挂
docker run -v /host/path:/container/path alpine
# 或
docker run --mount type=bind,source=/host/path,target=/container/path alpine
```

## 🆚 volume vs bind mount

| | named volume | bind mount |
|--|------------|------------|
| 位置 | /var/lib/docker/volumes/ | 主机任意路径 |
| 性能 | 一般（默认） | 略好（直接 IO） |
| 备份 | `docker volume` 命令 | 直接 cp |
| 跨平台 | 是 | 否 |
| 适合 | 生产数据 | 开发（热加载） |

## 🔧 常用命令

```bash
docker volume ls
docker volume inspect mydata
docker volume create mydata
docker volume create --driver local \
  --opt type=none --opt device=/srv/data \
  --opt o=bind mydata             # 用 local 驱动指定路径
docker volume rm mydata
docker volume prune              # 清未用

# 看容器用了哪些卷
docker inspect web | grep -A 10 Mounts
```

## 🛠 Dockerfile + VOLUME

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY . .

# 声明匿名卷（用户 -v 会被覆盖）
VOLUME ["/data", "/logs"]

CMD ["node", "server.js"]
```

## 🪜 tmpfs（内存盘）

```bash
# 敏感数据不落盘
docker run --tmpfs /tmp:rw,size=64m myapp
docker run --tmpfs /run --tmpfs /var/run myapp

# 等价（但 --tmpfs 旧版本不识别）
docker run --mount type=tmpfs,target=/tmp myapp
```

## 🩹 数据迁移 / 备份

```bash
# 容器间迁移（笨办法）
docker run --rm -v mydata:/from -v $PWD:/to alpine \
  sh -c "cd /from && tar cf - . | (cd /to && tar xf -)"

# 复制到主机
docker run --rm -v mydata:/from -v $(pwd):/to alpine \
  sh -c "cd /from && tar cf - . | (cd /to && tar xf -)"

# 从主机导入
docker run --rm -v mydata:/to -v $(pwd):/from alpine \
  sh -c "cd /from && tar cf - . | (cd /to && tar xf -)"
```

## 🧹 清理策略

```bash
# 容器自动删（默认不删卷）
docker run --rm ...

# 删容器时一起删卷
docker run --rm --volume mydata:/data alpine
docker rm -v web                   # 删容器 + 匿名卷
```

## 🪜 性能调优

```bash
# bind mount：用 delegated / cached（macOS）
docker run -v /host:/container:cached alpine  # 主机权威
docker run -v /host:/container:delegated alpine  # 容器权威
# macOS 上 cached / delegated 性能远好于 default

# 选存储驱动（Linux）
# overlay2 (默认 / 推荐)
# btrfs / zfs (高级)
# devicemapper (CentOS 旧版)
```

## 🛠 实战

### 1. 数据库持久化

```bash
# 一次性建卷
docker volume create pg-data

# 跑数据库
docker run -d --name db \
  -v pg-data:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=secret \
  postgres:15

# 数据落地
docker volume inspect pg-data | grep Mountpoint
# /var/lib/docker/volumes/pg-data/_data
ls /var/lib/docker/volumes/pg-data/_data
```

### 2. 开发热加载

```bash
# 代码改 → 容器内立即生效
docker run -d --name dev \
  -v $(pwd):/app:ro \
  myapp:dev
# 应用 reload 模式读文件 → 看到新代码
```

### 3. 多容器共享数据

```bash
# 同一卷挂到两容器
docker volume create shared-data
docker run -d --name writer -v shared-data:/data writer
docker run -d --name reader -v shared-data:/. cache  # 缓存读
```

## 🩺 故障

```bash
# 容器里写了文件，主机没看到
# → 可能挂载到容器内路径 ≠ 实际写入路径
docker exec web ls -la /data
docker inspect web | grep -A 5 Mounts

# 权限问题
sudo chown 1000:1000 /srv/data
docker run -v /srv/data:/data -u 1000 myapp

# 卷占用大
docker system df
du -sh /var/lib/docker/volumes/*
```

## 🔗 下一步

- [Docker 基础](/01-docker/intro)
- [容器 container](/01-docker/container)
- [Docker 网络](/01-docker/network)
- [Docker Compose](/01-docker/compose)