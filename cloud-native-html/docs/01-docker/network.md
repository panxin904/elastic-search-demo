---
title: Docker 网络
---

# Docker 网络

> 容器之间、容器与外部之间如何通信。

## 🧬 网络驱动

| 驱动 | 用途 |
|------|------|
| `bridge` | 默认。单主机容器互联 |
| `host` | 共享主机网络（无隔离） |
| `none` | 关闭网络（仅 lo） |
| `overlay` | 多主机容器互联（Swarm） |
| `macvlan` | 容器像独立设备（有 MAC） |
| `ipvlan` | 类似 macvlan 但共享 MAC |

## 🌉 bridge（默认）

```bash
docker network ls
# NETWORK ID     NAME       DRIVER    SCOPE
# abc123         bridge     bridge    local
# def456         host       host      local
# ghi789         none       null      local
```

### 容器互联

```bash
# 旧方式：--link（已弃用）
docker run -d --name db postgres
docker run -d --link db:db myapp
# myapp 内 /etc/hosts 有 db → db 容器 IP

# 推荐：自定义网络
docker network create mynet
docker run -d --name db --network mynet postgres
docker run -d --name app --network mynet myapp
# app 内可用 db 主机名（自动 DNS 解析）
```

### 默认网桥

```bash
# 容器只能用 IP 通信（默认网桥无 DNS）
docker run -d --name web1 nginx
docker run -d --name web2 nginx
# 在 web1 容器内 ping web2 → 失败（web2 解析不到）
# 必须用 IP：docker inspect web2 | grep IPAddress

# 解决：改用自定义网络
docker network create mynet
docker network connect mynet web1
docker network connect mynet web2
```

## 🌍 端口发布

```bash
# 主机端口 : 容器端口
docker run -p 8080:80 nginx        # TCP（默认）
docker run -p 8080:80/udp nginx   # UDP
docker run -p 8080:80/tcp -p 53:53/udp nginx

# 绑定到特定 IP
docker run -p 127.0.0.1:8080:80 nginx

# 随机端口
docker run -p 80 nginx
docker port web                   # 看实际端口

# 范围内端口（罕见）
docker run -p 8000-8005:8000-8005 nginx
```

## 🔒 容器间通信

```bash
# 容器用容器名互相访问
docker run -d --name api myapp
docker exec api curl http://db:5432

# 在用户定义网络里：自动 DNS（容器名 = 主机名）
docker network create backend
docker run -d --name db --network backend postgres
docker run -d --name api --network backend myapp
# api 内：curl http://db:5432  ← DNS 解析
```

## 📜 网络命令

```bash
docker network ls
docker network inspect mynet
docker network create mynet                # bridge
docker network create --driver overlay mynet  # Swarm 多机
docker network create --subnet 10.5.0.0/16 mysub
docker network rm mynet
docker network prune                        # 清未用

# 看容器在哪些网络
docker inspect web | grep -A 5 Networks

# 容器加入/离开网络（运行时）
docker network connect mynet web
docker network disconnect mynet web
```

## 🎯 实战模式

### 1. 微服务互联

```yaml
# docker-compose.yml
services:
  web:
    image: nginx:alpine
  api:
    image: myapp
    environment:
      DB_HOST: db
  db:
    image: postgres:15
# 同一 network 默认即可
```

### 2. 开发环境暴露数据库到主机

```bash
docker run -d --name db -p 5432:5432 postgres
# 主机 psql -h localhost -U postgres
```

### 3. 跨主机通信（Swarm）

```bash
docker swarm init
docker network create -d overlay mynet
# 多机 Swarm 节点上容器自动能互联
```

## 🪜 高级：自定义网络（vlan / 隔离）

```bash
# macvlan：容器像独立设备
docker network create -d macvlan \
  --subnet=192.168.1.0/24 --gateway=192.168.1.1 \
  -o parent=eth0 myvlan

# 容器获得 192.168.1.x 地址，可被同网段设备直连
docker run --network myvlan -d alpine
```

## 🩺 故障

```bash
# 容器之间连不上
docker exec web1 ping web2          # 看能不能解析
docker exec web1 cat /etc/resolv.conf

# 端口发布但外面连不上
docker port web                     # 确认映射
sudo iptables -L -n | grep 8080     # 看防火墙
docker network inspect bridge

# 容器里 curl 慢 / 卡
docker exec web nslookup docker.com
# 看 DNS 配的是 8.8.8.8 还是宿主
```

## 🔗 下一步

- [Docker 基础](/01-docker/intro)
- [Docker 存储 / 卷](/01-docker/volume)
- [Docker Compose](/01-docker/compose)