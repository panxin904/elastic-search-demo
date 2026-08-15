---
title: 安装部署
---

# 📥 安装部署

> Redis 官方只提供源码和 Docker 镜像，没有 Windows 安装包（微软自己维护一个 3.x 兼容版）。生产环境请优先 Linux，二进制、Docker、包管理器三种方式都可以，下面按推荐顺序介绍。

## 方式一：Linux 源码编译（推荐）

> 编译安装能拿到最新版本，还能自定义 `jemalloc` / `TLS` 等特性。运维熟练的话，首选这条路。

```bash
# 1. 下载源码（国内镜像）
wget https://download.redis.io/releases/redis-7.2.4.tar.gz

# 2. 解压并进入目录
tar xzf redis-7.2.4.tar.gz
cd redis-7.2.4

# 3. 编译（需要 gcc、make）
make MALLOC=libc -j$(nproc)

# 4. 安装到 /usr/local/bin
make install PREFIX=/usr/local/redis
```

```bash
# 5. 创建专用账号（不要用 root 跑 Redis）
useradd -r -s /sbin/nologin redis
mkdir -p /var/lib/redis /var/log/redis /etc/redis
cp redis.conf /etc/redis/redis.conf
chown -R redis:redis /var/lib/redis /var/log/redis /etc/redis
```

## 方式二：包管理器（Ubuntu / CentOS）

```bash
# Ubuntu 22.04+ / Debian
sudo apt update
sudo apt install -y redis-server
sudo systemctl enable --now redis-server

# CentOS 7+ / RHEL（需要 EPEL 源）
sudo yum install -y epel-release
sudo yum install -y redis
sudo systemctl enable --now redis
```

> Ubuntu 仓库的版本通常滞后 1~2 个大版本，需要新特性的话还是编译装。

## 方式三：Docker（最快）

> 一行命令就能拉起一个带 AOF 持久化的实例，适合本地开发与 CI 环境。

```bash
# 最快起一个
docker run -d --name redis \
  -p 6379:6379 \
  -v $PWD/data:/data \
  redis:7.2-alpine \
  redis-server --appendonly yes
```

```yaml
# docker-compose.yml：开发 + 监控 + 远程管理一条龙
version: "3.8"
services:
  redis:
    image: redis:7.2-alpine
    container_name: redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    command:
      - "redis-server"
      - "/usr/local/etc/redis/redis.conf"
    volumes:
      - ./redis.conf:/usr/local/etc/redis/redis.conf:ro
      - ./data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
```

```bash
# 进入容器调试
docker exec -it redis redis-cli

# 清理实例（带数据卷）
docker compose down -v
```

## redis.conf 关键配置

> 默认配置只能本地开发用，生产一定要改下面这些项。完整配置 1500+ 行，下面只列高频必改。

```conf
# ============ 网络 ============
bind 0.0.0.0 -::*
protected-mode yes           # 没设密码时仅允许本地连接
port 6379
tcp-backlog 511
timeout 300                  # 客户端空闲 300 秒断开

# ============ 通用 ============
daemonize yes                # 后台运行（systemd 部署时改成 no）
supervised systemd           # 交给 systemd 拉起
pidfile /var/run/redis_6379.pid
loglevel notice
logfile /var/log/redis/redis.log
databases 16

# ============ 持久化 ============
save 3600 1                  # 3600 秒至少 1 个 key 变化则快照
save 300 100                 # 300 秒至少 100 个 key 变化
save 60 10000                # 60 秒至少 10000 个 key 变化
appendonly yes               # 开启 AOF
appendfsync everysec         # 每秒刷盘，平衡性能与安全

# ============ 内存 ============
maxmemory 4gb
maxmemory-policy allkeys-lru

# ============ 安全 ============
requirepass YourStrongPass!  # 必须设置密码
rename-command KEYS ""       # 在线禁用危险命令
rename-command FLUSHALL ""
```

## 后台启动三种姿势

| 方式 | 适合场景 | 关键命令 |
| --- | --- | --- |
| 源码 + redis.conf | 传统物理机/虚拟机 | `redis-server /etc/redis/redis.conf` |
| systemd 托管 | CentOS/Ubuntu 生产 | `systemctl enable --now redis` |
| Docker | 云原生/CI | `docker run -d ... redis:7.2` |

```ini
# /etc/systemd/system/redis.service
[Unit]
Description=Redis 7.2 Server
After=network.target

[Service]
Type=forking
User=redis
Group=redis
PIDFile=/var/run/redis_6379.pid
ExecStart=/usr/local/bin/redis-server /etc/redis/redis.conf
ExecStop=/bin/kill -TERM $MAINPID
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

```bash
# 加载并启动
sudo systemctl daemon-reload
sudo systemctl enable --now redis
sudo systemctl status redis
```

## redis-cli 必须会这十条

```bash
# 连接
redis-cli -h 127.0.0.1 -p 6379 -a YourStrongPass!

# 健康
PING                                           # PONG
INFO server                                    # 服务信息
INFO memory                                    # 内存细节
DBSIZE                                         # 当前库 key 数
CONFIG GET maxmemory                           # 读取配置
CONFIG SET maxmemory 2gb                       # 热改配置
CONFIG REWRITE                                  # 把内存中的配置写回文件

# 慢查询
SLOWLOG GET 5                                  # 最近 5 条慢命令
SLOWLOG LEN                                    # 慢日志条数
SLOWLOG RESET                                  # 清空慢日志

# 客户端连接
CLIENT LIST                                    # 当前所有连接
CLIENT KILL ID 1234                            # 干掉某个连接

# 数据备份
BGSAVE                                         # 后台 RDB 快照
LASTSAVE                                       # 上次快照时间
```

::: warning 注意
- 不要在生产执行 `FLUSHALL`、`FLUSHDB`、`KEYS *`，会把主线程卡住几秒到几十秒。
- 改 `maxmemory` 之类参数，线上建议先 `CONFIG SET` 验证，确认无误再 `CONFIG REWRITE`。
- `requirepass` 设了之后，`redis-cli` 必须加 `-a`，或者用 `AUTH` 命令交互式输入，避免密码进 history。
:::

## 启动后的三步验证

1. **PING**：返回 `PONG` 说明服务正常。
2. **INFO replication**：确认 `role:master` 或 `role:slave`，看是否在预期角色。
3. **写入读出**：跑一次 `SET test:v 1` + `GET test:v` + `DEL test:v`，打通整条链路。

```bash
# 一键三连验证
redis-cli PING && \
redis-cli SET __healthcheck__ ok EX 10 && \
redis-cli GET __healthcheck__
```

## 本章要点

- 生产环境至少跑 7.2+，低版本有已知的内存泄漏与复制缺陷。
- 配置文件分四块：网络、通用、持久化、内存+安全，每块都有 1~2 个必改项。
- `redis-cli` 入门先掌握 `PING / INFO / CONFIG / SLOWLOG / CLIENT` 这五个工具集。

**下一步：** [📦 5 大基础类型](/01-basics/datatypes)