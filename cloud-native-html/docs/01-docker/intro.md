---
title: Docker 基础
date: 2026-08-15  # date-auto-injected
---

# Docker 基础

> Docker = 操作系统级虚拟化（容器），比 VM 轻量。

## 🤔 容器 vs 虚拟机

| | 容器 | 虚拟机 |
|--|------|--------|
| 启动 | 毫秒 | 秒 ~ 分钟 |
| 体积 | MB | GB |
| 性能 | 接近原生 | 有损耗（虚拟化层） |
| 隔离 | 进程级（共享内核） | 硬件级 |
| 镜像 | Docker Hub | ISO / OVF |
| 启动密度 | 千级 | 几十 |

## 🏗️ Docker 架构

```
┌──────────────────────────────┐
│  Client (docker CLI)         │
└─────────────────┬────────────┘
                  │ REST API
┌─────────────────▼────────────┐
│  Docker Daemon (dockerd)     │
│  - 镜像管理                  │
│  - 容器生命周期              │
│  - 网络 / 卷                 │
└─────────────────┬────────────┘
                  │
┌─────────────────▼────────────┐
│  containerd                   │
│  - OCI 容器运行时             │
└─────────────────┬────────────┘
                  │
┌─────────────────▼────────────┐
│  runc (OCI 规范)             │
│  - 真正 spawn 容器进程        │
└──────────────────────────────┘
```

## 🔧 安装

```bash
# Debian / Ubuntu
curl -fsSL https://get.docker.com | sh

# 装 docker-compose plugin（v2 内置）
# macOS / Windows：装 Docker Desktop

# 加权限（避免每次 sudo）
sudo usermod -aG docker $USER
newgrp docker
docker run hello-world          # 测试
```

## 🐳 第一个容器

```bash
docker run -it --rm alpine sh
# -i 交互 / -t tty / --rm 退出后删 / alpine 镜像 / sh 命令

# 等价
docker pull alpine               # 先拉
docker run -it --rm alpine sh
```

## 📦 核心概念

| 概念 | 解释 |
|------|------|
| 镜像 (Image) | 只读模板（类 / 类） |
| 容器 (Container) | 镜像运行实例（类 / 实例） |
| 仓库 (Registry) | 镜像存储（Docker Hub） |
| Dockerfile | 镜像构建脚本 |
| Compose | 多容器编排（docker-compose.yml） |
| Volume | 持久化数据 |
| Network | 容器间网络 |

## 📜 高频命令

```bash
# 镜像
docker images                    # 列出
docker pull nginx:alpine
docker rmi <image-id>
docker image ls

# 容器
docker run -d --name web -p 80:80 nginx     # 后台
docker ps -a                            # 全部
docker ps -q                            # 仅 ID
docker stop web
docker rm web
docker restart web

# 进入 / 日志
docker exec -it web bash
docker logs -f --tail 100 web
docker inspect web

# 系统
docker system df
docker system prune -a
```

## 🪛 实战

```bash
# 跑一个 nginx 看欢迎页
docker run -d --name web -p 8080:80 nginx:alpine
curl localhost:8080

# 把容器文件系统拷出来
docker cp web:/etc/nginx/nginx.conf .

# 看容器资源使用
docker stats
docker top web
```

## 🔗 下一步

- [镜像 image](/01-docker/image)
- [容器 container](/01-docker/container)
- [Docker 网络](/01-docker/network)
- [Docker Compose](/01-docker/compose)

<!-- svg-injected:do-not-edit -->

![docker architecture](/docker-architecture.svg)
