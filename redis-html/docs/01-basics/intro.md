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

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600" >Redis 5 大数据类型</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">底层编码 · sds / listpack / skiplist</text>

  <g font-size="11" font-weight="700">
    <!-- String -->
    <rect class="at-hover-card" x="40" y="100" width="100" height="100" rx="8" fill="#dbeafe" stroke="#3b82f6" stroke-width="2"/>
    <text x="90" y="120" text-anchor="middle" font-size="12" fill="#1e3a8a">String</text>
    <text x="90" y="140" text-anchor="middle" font-size="10" fill="#1e40af">SET / GET</text>
    <text x="90" y="158" text-anchor="middle" font-size="9" fill="#3b82f6">int / embstr</text>
    <text x="90" y="172" font-size="9" fill="#3b82f6" text-anchor="middle">raw</text>
    <text x="90" y="190" text-anchor="middle" font-size="9" fill="#1e40af">场景：缓存</text>

    <!-- Hash -->
    <rect class="at-hover-card" x="160" y="100" width="100" height="100" rx="8" fill="#d1fae5" stroke="#10b981" stroke-width="2"/>
    <text x="210" y="120" text-anchor="middle" font-size="12" fill="#064e3b">Hash</text>
    <text x="210" y="140" text-anchor="middle" font-size="10" fill="#065f46">HSET / HGET</text>
    <text x="210" y="158" text-anchor="middle" font-size="9" fill="#10b981">listpack</text>
    <text x="210" y="172" font-size="9" fill="#10b981" text-anchor="middle">hashtable</text>
    <text x="210" y="190" text-anchor="middle" font-size="9" fill="#065f46">场景：对象</text>

    <!-- List -->
    <rect class="at-hover-card" x="280" y="100" width="100" height="100" rx="8" fill="#fef3c7" stroke="#f59e0b" stroke-width="2"/>
    <text x="330" y="120" text-anchor="middle" font-size="12" fill="#92400e">List</text>
    <text x="330" y="140" text-anchor="middle" font-size="10" fill="#78350f">LPUSH / RPOP</text>
    <text x="330" y="158" text-anchor="middle" font-size="9" fill="#f59e0b">listpack</text>
    <text x="330" y="172" font-size="9" fill="#f59e0b" text-anchor="middle">quicklist</text>
    <text x="330" y="190" text-anchor="middle" font-size="9" fill="#78350f">场景：队列</text>

    <!-- Set -->
    <rect class="at-hover-card" x="400" y="100" width="100" height="100" rx="8" fill="#fce7f3" stroke="#ec4899" stroke-width="2"/>
    <text x="450" y="120" text-anchor="middle" font-size="12" fill="#9f1239">Set</text>
    <text x="450" y="140" text-anchor="middle" font-size="10" fill="#9d174d">SADD / SMEMBERS</text>
    <text x="450" y="158" text-anchor="middle" font-size="9" fill="#ec4899">intset</text>
    <text x="450" y="172" font-size="9" fill="#ec4899" text-anchor="middle">hashtable</text>
    <text x="450" y="190" text-anchor="middle" font-size="9" fill="#9d174d">场景：标签</text>

    <!-- Sorted Set -->
    <rect class="at-hover-card" x="100" y="240" width="200" height="100" rx="8" fill="#ede9fe" stroke="#8b5cf6" stroke-width="2"/>
    <text x="200" y="260" text-anchor="middle" font-size="12" fill="#5b21b6">Sorted Set</text>
    <text x="200" y="280" text-anchor="middle" font-size="10" fill="#6b21a8">ZADD / ZRANGEBYSCORE</text>
    <text x="200" y="298" text-anchor="middle" font-size="9" fill="#8b5cf6">listpack + skiplist</text>
    <text x="200" y="315" text-anchor="middle" font-size="9" fill="#6b21a8">场景：排行榜</text>
    <text x="200" y="330" text-anchor="middle" font-size="9" fill="#6b21a8">延迟队列</text>

    <!-- 高级 -->
    <rect class="at-hover-card" x="320" y="240" width="200" height="100" rx="8" fill="#fef3c7" stroke="#f59e0b" stroke-width="2"/>
    <text x="420" y="260" text-anchor="middle" font-size="12" fill="#92400e">Stream / Bitmap / Geo</text>
    <text x="420" y="280" text-anchor="middle" font-size="10" fill="#78350f">XADD / SETBIT / GEOADD</text>
    <text x="420" y="298" text-anchor="middle" font-size="9" fill="#78350f">消息流 / 位图 / 地理位置</text>
    <text x="420" y="315" text-anchor="middle" font-size="9" fill="#78350f">Redis 6+ 模块化</text>
    <text x="420" y="330" text-anchor="middle" font-size="9" fill="#78350f">RedisJSON / RediSearch</text>
  </g>

  <!-- 底层编码说明 -->
  <g font-size="11">
    <rect class="at-hover-card" x="40" y="375" width="520" height="80" rx="8" fill="#f1f5f9" stroke="#64748b" stroke-width="1"/>
    <text x="300" y="395" text-anchor="middle" font-weight="700" fill="#1e293b">底层编码演进</text>
    <text x="60" y="415" fill="#475569">SDS：Simple Dynamic String · 替代 C 字符串 · O(1) 取长度</text>
    <text x="60" y="432" fill="#475569">listpack：紧凑列表 · 替代 ziplist · 节省内存</text>
    <text x="60" y="449" fill="#475569">skiplist：跳跃表 · ZSet 排序 · 范围查询 O(logN)</text>
    <text x="320" y="415" fill="#475569">embstr：≤44 字节内嵌 · 减少分配</text>
    <text x="320" y="432" fill="#475569">quicklist：list + zlist 组合</text>
    <text x="320" y="449" fill="#475569">编码自动切换 · 阈值由 redis.conf 配置</text>
  </g>
</svg>
<!-- svg-injected:do-not-edit -->

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600" >Redis 持久化：RDB vs AOF</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">快照 vs 日志 · 混合模式</text>

  <!-- RDB 左侧 -->
  <rect class="at-hover-card" x="40" y="100" width="240" height="280" rx="10" fill="#dbeafe" stroke="#3b82f6" stroke-width="2"/>
  <text x="160" y="125" text-anchor="middle" font-size="16" font-weight="700" fill="#1e3a8a">RDB（快照）</text>
  <text x="160" y="142" text-anchor="middle" font-size="11" fill="#1e40af">Redis Database</text>

  <g font-size="11" font-weight="700">
    <rect class="at-hover-card" x="60" y="155" width="200" height="40" rx="6" fill="#3b82f6" opacity="0.9"/>
    <text x="160" y="180" text-anchor="middle" fill="white">save / bgsave</text>
    <text x="160" y="195" text-anchor="middle" font-size="10" fill="#dbeafe">fork 子进程</text>

    <rect class="at-hover-card" x="60" y="205" width="200" height="40" rx="6" fill="#10b981" opacity="0.9"/>
    <text x="160" y="230" text-anchor="middle" fill="white">dump.rdb</text>
    <text x="160" y="245" text-anchor="middle" font-size="10" fill="#d1fae5">二进制压缩</text>

    <rect class="at-hover-card" x="60" y="255" width="200" height="40" rx="6" fill="#f59e0b" opacity="0.9"/>
    <text x="160" y="280" text-anchor="middle" fill="white">触发策略</text>
    <text x="160" y="295" text-anchor="middle" font-size="10" fill="#fef3c7">900s 1 次 / 300s 10 / 60s 10000</text>

    <rect class="at-hover-card" x="60" y="305" width="200" height="40" rx="6" fill="#ec4899" opacity="0.9"/>
    <text x="160" y="330" text-anchor="middle" fill="white">优点 / 缺点</text>
    <text x="160" y="345" text-anchor="middle" font-size="10" fill="#fce7f3">快 / 可能丢分钟级数据</text>

    <text x="160" y="365" text-anchor="middle" font-size="10" font-weight="700" fill="#1e3a8a">适合：备份 · 容灾</text>
  </g>

  <!-- AOF 右侧 -->
  <rect class="at-hover-card" x="320" y="100" width="240" height="280" rx="10" fill="#d1fae5" stroke="#10b981" stroke-width="2"/>
  <text x="440" y="125" text-anchor="middle" font-size="16" font-weight="700" fill="#064e3b">AOF（日志）</text>
  <text x="440" y="142" text-anchor="middle" font-size="11" fill="#065f46">Append Only File</text>

  <g font-size="11" font-weight="700">
    <rect class="at-hover-card" x="340" y="155" width="200" height="40" rx="6" fill="#10b981" opacity="0.9"/>
    <text x="440" y="180" text-anchor="middle" fill="white">everysec / always</text>
    <text x="440" y="195" text-anchor="middle" font-size="10" fill="#d1fae5">fsync 策略</text>

    <rect class="at-hover-card" x="340" y="205" width="200" height="40" rx="6" fill="#3b82f6" opacity="0.9"/>
    <text x="440" y="230" text-anchor="middle" fill="white">appendonly.aof</text>
    <text x="440" y="245" text-anchor="middle" font-size="10" fill="#dbeafe">RESP 协议文本</text>

    <rect class="at-hover-card" x="340" y="255" width="200" height="40" rx="6" fill="#f59e0b" opacity="0.9"/>
    <text x="440" y="280" text-anchor="middle" fill="white">rewrite 重写</text>
    <text x="440" y="295" text-anchor="middle" font-size="10" fill="#fef3c7">bgrewriteaof</text>

    <rect class="at-hover-card" x="340" y="305" width="200" height="40" rx="6" fill="#ec4899" opacity="0.9"/>
    <text x="440" y="330" text-anchor="middle" fill="white">优点 / 缺点</text>
    <text x="440" y="345" text-anchor="middle" font-size="10" fill="#fce7f3">丢 ≤1s 数据 / 文件大</text>

    <text x="440" y="365" text-anchor="middle" font-size="10" font-weight="700" fill="#064e3b">适合：金融 · 关键数据</text>
  </g>

  <!-- 混合模式 -->
  <g font-size="11">
    <rect class="at-hover-card" x="40" y="400" width="520" height="60" rx="8" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="60" y="420" font-weight="700" fill="#92400e">Redis 4+ 混合持久化（推荐）</text>
    <text x="60" y="438" fill="#78350f">RDB 全量 + AOF 增量：RDB 记录快照点 · AOF 记录快照后的增量</text>
    <text x="60" y="455" fill="#78350f">恢复快 + 数据全 · 配置 aof-use-rdb-preamble yes</text>
  </g>
</svg>
