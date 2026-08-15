---
title: 容器 container
---

# Docker 容器

> 容器 = 镜像的运行实例。每个容器有独立的进程树 / 文件系统 / 网络栈。

## 🚀 docker run

```bash
docker run [OPTIONS] IMAGE [COMMAND] [ARG...]
```

### 高频选项

| 选项 | 简写 | 作用 |
|------|------|------|
| `--detach` | `-d` | 后台运行 |
| `--interactive` | `-i` | 保持 STDIN |
| `--tty` | `-t` | 分配伪终端 |
| `--rm` | | 容器退出后自动删除 |
| `--name <name>` | | 给容器起名 |
| `--hostname` | `-h` | 容器内主机名 |
| `--publish` | `-p <host>:<cont>` | 端口映射 |
| `--volume` | `-v` | 挂载卷 |
| `--env` | `-e` | 环境变量 |
| `--restart` | | 退出时重启策略 |
| `--network` | | 网络模式 |
| `--privileged` | | 特权模式（高权限，慎用） |
| `--user` | `-u` | 运行用户 |
| `--workdir` | `-w` | 工作目录 |
| `--env-file` | | 从文件读环境变量 |
| `--memory` | `-m` | 内存限制 |
| `--cpus` | | CPU 限制 |

## 🏃 run 模式

```bash
# 一次性
docker run --rm alpine echo hello

# 后台
docker run -d --name web -p 8080:80 nginx:alpine

# 交互
docker run -it --rm alpine sh

# 一次性执行命令
docker run --rm alpine ls /

# 自动重启
docker run -d --restart=always nginx
# 重启策略：
#   no              不自动重启
#   on-failure[:n]  失败时重启（最多 n 次）
#   always          总是重启
#   unless-stopped  除非手动停止
```

## 🔄 容器生命周期

```
Created   →  Running   →  Paused / Stopped / Removed
            ↓
          Restarting (策略触发)
```

```bash
docker create --name web nginx     # 只创建不启动
docker start web
docker stop web                   # 优雅（SIGTERM → SIGKILL）
docker kill web                   # 强制（SIGKILL）
docker restart web
docker pause / unpause web
docker rm web                      # 删除已停止的
docker rm -f web                   # 强制删除运行中的
```

## 🔍 查容器

```bash
docker ps                         # 运行中
docker ps -a                      # 全部
docker ps -q                      # 仅 ID
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

# 详细信息
docker inspect web
docker top web                    # 容器内进程
docker port web                   # 端口映射
docker diff web                   # 文件系统变化
docker stats                      # 实时资源
```

## 🪛 交互

```bash
# 进 shell
docker exec -it web bash
docker exec -it web sh            # alpine

# 用 root（多用户镜像）
docker exec -it -u root web bash

# 跑命令不进入
docker exec web cat /etc/nginx/nginx.conf

# 看日志
docker logs web
docker logs -f --tail 100 --since 10m web

# 文件拷贝
docker cp web:/etc/nginx/nginx.conf .
docker cp ./index.html web:/usr/share/nginx/html/

# 进程
docker top web ps aux
```

## 🛡 资源限制

```bash
# 内存
docker run -m 512m nginx           # 最大 512MB
docker run -m 1g --memory-swap 1g nginx  # 内存 + swap

# CPU
docker run --cpus 1.5 nginx       # 1.5 核
docker run --cpuset-cpus="0,1" nginx    # 限定到 CPU 0,1

# IO
docker run --device-read-bps /dev/sda:1mb

# 完整示例
docker run -d --name web \
  --memory 1g --cpus 1.0 \
  --restart=on-failure:5 \
  -p 8080:80 \
  nginx:alpine
```

## 🔄 容器网络

```bash
# 看容器的 IP / 网络
docker inspect web | grep IPAddress

# 容器互联
docker run -d --name db postgres:15
docker run -d --name app --link db:db myapp
# app 内可用 db 主机名

# 推荐：自定义网络
docker network create mynet
docker run -d --name db --network mynet postgres:15
docker run -d --name app --network mynet myapp
```

详见 [Docker 网络](/01-docker/network)。

## 💾 数据持久化

```bash
# bind mount（开发）
docker run -v $(pwd):/app myapp

# 命名卷（生产）
docker volume create db-data
docker run -v db-data:/var/lib/postgresql/data postgres
```

详见 [Docker 存储 / 卷](/01-docker/volume)。

## 🩺 故障排查

```bash
# 启动失败
docker logs web
docker inspect web | grep -A 5 State
docker run --rm -it myapp sh      # 进镜像看

# 端口冲突
docker run -p 80:80 nginx
# bind: address already in use
docker ps                          # 找谁占着
sudo lsof -i :80                   # 或 lsof

# 容器退出
docker logs web --tail 50
docker events --since 1h            # 看 daemon 事件

# 镜像拉不下来
docker pull nginx:alpine
# 检查 daemon 代理 / DNS
```

## 🪛 实战

```bash
# 单容器应用
docker run -d --name web \
  -p 8080:80 \
  -v $(pwd)/html:/usr/share/nginx/html:ro \
  --restart unless-stopped \
  nginx:alpine

# 看 log + 跟
docker logs -f web

# 备份容器数据
docker commit web myapp:snapshot   # ❌ 不推荐
docker run --volumes-from web -v $(pwd):/backup alpine tar cvf /backup/webdata.tar /data
# ✅ 推荐：直接用 volume

# 删除所有停止的
docker container prune
```

## 🔗 下一步

- [Docker 基础](/01-docker/intro)
- [镜像 image](/01-docker/image)
- [Docker 网络](/01-docker/network)
- [Docker Compose](/01-docker/compose)