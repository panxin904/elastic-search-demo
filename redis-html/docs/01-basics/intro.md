---
title: Redis 是什么
date: 2026-08-15  # date-auto-injected
---

# ❓ Redis 是什么

> Redis 是一个基于内存的、支持持久化的 key-value 数据结构存储系统。它既可以当缓存用，也能当数据库、消息队列、分布式锁服务来用，是后端工程师手里的瑞士军刀。

## 一句话定义

**Redis** = **RE**mote **DI**ctionary **S**erver。核心是把数据放在内存里读写，再异步把变更刷到磁盘，所以单机能跑到十万级 QPS。

## 核心特性

- **内存存储**：读写都在内存，命中延迟通常在 0.1ms 量级。
- **丰富数据结构**：String、Hash、List、Set、ZSet、Stream、Bitmap、HyperLogLog、GEO，开箱即用。
- **单线程 IO 多路复用**：一个线程处理所有客户端请求，靠 epoll/kqueue 监听多个 socket，避免锁竞争。
- **可选持久化**：RDB 快照 + AOF 追加日志，重启不丢数据。
- **高可用与水平扩展**：Sentinel 做主从切换，Cluster 做 16384 槽位分片。
- **多语言客户端**：Java、Go、Python、Node.js、PHP 全部官方支持。

## 单线程到底快不快

> Redis 4.0 之后，其实是多线程（异步删除、I/O 解码在 6.0 后也走线程池），但**执行命令的主循环依然是单线程**。这条规则保证了同一时刻只有一条命令在跑，省掉了锁和上下文切换。

| 阶段 | 是否多线程 | 作用 |
| --- | --- | --- |
| 网络 I/O 读写（6.0+） | 多线程 | 解析协议、写入 socket |
| 命令执行 | 单线程 | 避免竞态，保证原子性 |
| 异步删除（AOF/RDB） | 多线程 | 把大 key 的释放扔到后台 |
| 集群心跳与同步 | 多线程 | Gossip、Replication I/O |

## 典型场景

| 场景 | 用什么类型 | 为什么选 Redis |
| --- | --- | --- |
| 热点缓存 | String | 毫秒级读，扛高并发 |
| 分布式 Session | Hash | 字段独立读写，过期方便 |
| 排行榜 | ZSet | `ZADD` + `ZREVRANGE` 一行搞定 |
| 点赞 / 关注集合 | Set | `SADD` / `SISMEMBER` 判断存在性 |
| 限流器 | String + Lua | 原子自增，不依赖第三方 |
| 消息队列 | List / Stream | 轻量场景够用，重度场景再上 Kafka |
| 全局 ID 生成 | String | `INCR` 原子递增 |

## Redis vs Memcached

> 两个老对手经常被放在一起比较。下面这张表能帮你 90% 的场景下做选型。

| 维度 | Redis | Memcached |
| --- | --- | --- |
| 数据结构 | 5+ 高级类型 | 仅 KV String |
| 持久化 | RDB + AOF | 不支持，重启即丢 |
| 集群方案 | Sentinel / Cluster | 客户端分片 / mcrouter |
| 单机吞吐 | 10w+ QPS | 20w+ QPS（纯 KV 更轻） |
| 内存模型 | 可淘汰（多种策略） | 仅 LRU |
| 线程模型 | 单线程主循环（6.0+ I/O 多线程） | 完全多线程 |
| 适用场景 | 缓存 + 数据库 + 锁 + 队列 | 纯缓存，无业务语义 |
| 典型客户 | 微博、GitHub、Stack Overflow | Facebook、Twitter 历史选型 |

> 简单记忆：**只要需要"业务语义"（排序、去重、原子自增），选 Redis；只要纯 KV 缓存，Memcached 也能用，但今天 Redis 已经能覆盖它的绝大多数场景。**

## Redis 不擅长的场景

- **海量冷数据存储**：内存贵，按 32GB 一台算，1 亿条 300B 的 KV 就是 30GB。冷数据请走 SSD + RocksDB。
- **复杂查询**：没有二级索引、JOIN、全文检索。要么用 RediSearch 模块，要么把数据同步到 Elasticsearch。
- **强事务**：Redis 事务不支持回滚，多 key 操作要么用 Lua 脚本保证原子性，要么用分布式事务框架兜底。
- **百 TB 级数据**：单实例最多几 GB 到几十 GB，再大要分片到 Cluster，运维复杂度会显著上升。

## 用 30 秒验证一下

```bash
# 启动本地客户端（假定 Redis 已安装在 6379 端口）
redis-cli

# 一次 PING，确认连接
127.0.0.1:6379> PING
PONG

# 写一个 String
127.0.0.1:6379> SET site "redis-docs" EX 60
OK

# 读出来，并查看剩余 TTL
127.0.0.1:6379> GET site
"redis-docs"
127.0.0.1:6379> TTL site
(integer) 58

# 查看服务版本与角色
127.0.0.1:6379> INFO server | grep redis_version
redis_version:7.2.4
```

```yaml
# Docker 启动一个最简实例，端口与密码都在这一份 compose 里
version: "3.8"
services:
  redis:
    image: redis:7.2-alpine
    container_name: redis-demo
    ports:
      - "6379:6379"
    command: ["redis-server", "--appendonly", "yes"]
    volumes:
      - ./data:/data
```

```bash
# 健康检查（运维最常用）
redis-cli -h 127.0.0.1 -p 6379 PING
redis-cli -h 127.0.0.1 -p 6379 INFO replication | grep role
```

## 本章要点

- Redis 是内存型 KV，但远不止缓存。
- 单线程主循环是它简单且高性能的关键，不要在线上跑 `KEYS *`、大对象 `DEL` 这种阻塞命令。
- 选型时优先 Redis，因为生态更完整；只有"纯 KV + 极致吞吐"的极端场景才考虑 Memcached。

**下一步：** [📥 安装部署](/01-basics/install)

<!-- svg-injected:do-not-edit -->

![redis data structures](/redis-data-structures.svg)

<!-- svg-injected:do-not-edit -->

![redis persistence](/redis-persistence.svg)
