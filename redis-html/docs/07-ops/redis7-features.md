---
title: Redis 7 新特性
---

# Redis 7 新特性

Redis 7.0（2022 年发布）是 Redis 史上变化最大的版本之一。Functions 替代 Lua、Multi-part AOF、ACL v2、Sharded Pub/Sub，每一项都解决了生产中的真实痛点。

## Redis Functions（替代 Lua 脚本）

### 旧痛点：Lua 脚本的局限

Redis 5/6 用 `EVAL` / `EVALSHA` 跑 Lua，但有几个硬伤：

```bash
# 旧方式：每次都要传脚本源码
redis-cli EVAL "return redis.call('GET', KEYS[1])" 1 mykey
# "hello"

# 或者用 EVALSHA 缓存（但脚本丢失要重载）
redis-cli SCRIPT LOAD "return redis.call('GET', KEYS[1])"
# "a5b1..."
redis-cli EVALSHA "a5b1..." 1 mykey
```

问题：
1. 脚本管理分散，业务代码 + Redis 两边维护
2. `SCRIPT FLUSH` 后缓存失效
3. 没有版本管理、调试、权限控制

### 新方式：Redis Functions

```bash
# 1. 加载函数库（一次）
redis-cli FUNCTION LOAD "#!lua name=mylib
redis.register_function('double_get', function(keys, args)
    local v = redis.call('GET', keys[1])
    return v and v * 2 or 0
end)"

# 2. 调用（无需传脚本）
redis-cli FCALL double_get 1 mykey
# "42"

# 3. 查看所有函数
redis-cli FUNCTION LIST
# 1) 1) "library_name"
#    2) "mylib"
#    3) "engine"
#    4) "lua"

# 4. 删除函数库
redis-cli FUNCTION DELETE mylib
```

### Functions 优势

| 维度 | Lua (EVAL) | Functions |
|---|---|---|
| 持久化 | 重启丢失 | 保存在 RDB/AOF |
| 复制 | 仅 master | 同步到 replicas |
| 版本管理 | 无 | library 名隔离 |
| 调试 | 难 | `FUNCTION STATS` 看调用次数 |
| 权限 | 统一 | 可按函数粒度 ACL（Redis 7.2+） |

### 函数库管理

```bash
# 导出函数库（备份、迁移）
redis-cli FUNCTION DUMP > mylib.bin

# 在另一个实例恢复
redis-cli FUNCTION RESTORE mylib.bin

# 查看统计
redis-cli FUNCTION STATS
# running_script:0
# engines:
#   lua:
#     libraries_count:1
#     functions_count:3
```

## Multi-part AOF

### 旧痛点：单文件 AOF 的隐患

Redis 6 的 AOF 是**单个文件**（appendonly.aof），有两个问题：

1. **加载慢**：AOF 重写时生成的新文件，启动要加载全量
2. **丢数据风险**：写盘中途崩溃，文件可能损坏

### Redis 7 Multi-part AOF

Redis 7 把 AOF 拆成多个文件：

```
/var/lib/redis/
├── appendonlydir/
│   ├── appendonly.aof.1.base.rdb    # RDB 格式基础文件
│   ├── appendonly.aof.1.incr.aof    # 增量 AOF
│   ├── appendonly.aof.2.incr.aof
│   └── appendonly.aof.manifest      # 清单文件
```

### 配置

```properties
# redis.conf
appendonly yes
aof-use-rdb-preamble yes           # 使用 RDB 格式作为基础（默认 yes）

# Redis 7 新增：Multi-part AOF 自动启用
# 不需要额外配置，会自动写入 appendonlydir/ 目录
```

### 加载流程

Redis 启动加载 AOF 时：

```
1. 读取 manifest
2. 加载最新的 base.rdb（全量）
3. 顺序重放所有 incr.aof（增量）
4. 完成后删除已应用的 incr 文件
```

相比 Redis 6 整体重放，**加载速度提升 50%~80%**（实测）。

### 手动触发 AOF 重写

```bash
# 强制重写（生成新的 base + manifest）
redis-cli BGREWRITEAOF

# 查看 manifest
cat /var/lib/redis/appendonlydir/appendonly.aof.manifest
# file appendonly.aof.1.base.rdb seq 1 type b
# file appendonly.aof.1.incr.aof seq 1 type i
```

## 客户端缓存（Client-side Caching）

### 什么是 Client-side Caching

让客户端缓存 Redis 的数据，读时先查本地，未命中再问 Redis。**Redis 7 用 RESP3 协议支持，服务端主动通知失效**。

### 三种模式

```bash
# 1. 默认模式（无通知）
CLIENT TRACKING ON

# 2. 失效广播模式（Redis 失效时主动通知）
CLIENT TRACKING ON REDIRECT 1234 BCAST    # 1234 是 client id

# 3. 失效定向模式（指定 key 失效才通知）
CLIENT TRACKING ON REDIRECT 1234
```

### 示例（Python + redis-py）

```python
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# 启用 tracking
r.execute_command('CLIENT', 'TRACKING', 'ON')

# 读取时自动跟踪 key
r.set('user:1', 'Alice')
val = r.get('user:1')
print(val)  # 'Alice'

# 在另一个连接修改
r2 = redis.Redis(host='localhost', port=6379)
r2.set('user:1', 'Bob')

# r 的失效消息回调触发（需要订阅 __redis__:invalidate）
```

### 与旧版 caching 的区别

| 维度 | Redis 6 caching | Redis 7 tracking |
|---|---|---|
| 协议 | RESP2 | **RESP3**（必须） |
| 失效通知 | 需客户端轮询 | 服务端推送 |
| 网络开销 | 高（轮询） | 低（按需通知） |
| 一致性 | 弱 | 强 |

### 配置

```properties
# redis.conf
# 跟踪表最大 key 数（防内存泄漏）
tracking-table-max-keys 1000000

# 不跟踪的 key 前缀
tracking-table-keys 0
```

## ACL v2

### 旧 ACL 的局限

Redis 6 引入 ACL，但粒度不够细，且命令分类粗糙。

### Redis 7 ACL v2 增强

```bash
# 创建用户
redis-cli ACL SETUSER appuser on >password ~app:* &* +@read +@write -@dangerous

# 参数解析：
# on                         启用
# >password                  密码
# ~app:*                     允许访问 app:* 的 key
# &*                         允许所有 pub/sub channel
# +@read                     允许读命令类别
# +@write                    允许写命令类别
# -@dangerous                禁止危险命令（KEYS / FLUSHDB 等）
```

### 命令分类

```bash
# 查看所有命令类别
redis-cli ACL CAT
# 1) "keyspace"
# 2) "read"
# 3) "write"
# 4) "set"
# ...

# 查看某类别下的命令
redis-cli ACL CAT dangerous
# 1) "KEYS"
# 2) "MIGRATE"
# 3) "FLUSHALL"
# 4) "FLUSHDB"

# 选中类别权限
redis-cli ACL SETUSER readonly on >pwd ~* &* +@read -@write
```

### 用户管理

```bash
# 查看用户列表
redis-cli ACL LIST
# 1) "user appuser on #fa... ~app:* &* +@read +@write -@dangerous"
# 2) "user readonly on #ab... ~* &* +@read -@write"

# 删除用户
redis-cli ACL DELUSER readonly

# 切换用户（无密码版本）
redis-cli ACL WHOAMI
# "default"

# 认证后切换
redis-cli AUTH appuser password
redis-cli ACL WHOAMI
# "appuser"
```

### ACL 持久化

```properties
# redis.conf
aclfile /etc/redis/users.acl    # ACL 配置文件路径（推荐）

# 或者用 CONFIG REWRITE 把内存中的 ACL 写回 redis.conf
```

```bash
# 把当前 ACL 写回文件
redis-cli ACL SAVE
```

## Sharded Pub/Sub

### 旧痛点：Cluster 下的 Pub/Sub

Redis 6 在 Cluster 模式下，Pub/Sub 消息会**广播到所有节点**：

```bash
# Cluster 模式发布
redis-cli -c PUBLISH news "hello"
# 所有节点都收到，浪费带宽
```

### Redis 7 Sharded Pub/Sub

消息**只在同一个 slot 的节点间传播**：

```bash
# 订阅（指定 slot）
redis-cli -c SSUBSCRIBE news

# 发布（slot 由 key 计算）
redis-cli -c SPUBLISH news "hello"

# 只有 news 所在 slot 的节点会收到
```

### 示例

```python
# 订阅端
r = redis.Redis(host='node-1', port=6379)
pubsub = r.pubsub()
pubsub.ssubscribe('order:events')   # 注意是 s 不是 p

# 发布端（任何节点都行，Cluster 自动路由）
r.spublish('order:events', json.dumps({"order_id": 1, "status": "paid"}))
```

### 适用场景

| 场景 | 用 Pub/Sub 还是 Sharded Pub/Sub |
|---|---|
| 全局通知（如配置变更） | Pub/Sub |
| 业务消息（如订单事件） | **Sharded Pub/Sub** |
| 大流量业务消息 | **Sharded Pub/Sub**（省带宽） |

## Listpack 全面替代 Ziplist

### 背景

Ziplist 是 Redis 早期的紧凑编码，节省内存。但 Ziplist 有连锁更新问题（一个 entry 变大会导致后续 entry 级联重写）。

### Redis 7 改动

Redis 7 用 **Listpack** 全面替代 Ziplist：

| 数据类型 | Redis 6 | Redis 7 |
|---|---|---|
| Hash（小） | ziplist | **listpack** |
| Zset（小） | ziplist | **listpack** |
| List（小） | quicklist + ziplist | **quicklist + listpack** |

### Listpack 优势

1. **无连锁更新**：每个 entry 独立存储长度，修改不级联
2. **更紧凑**：结构更简单，节省约 10% 内存
3. **更快解析**：定位 entry 一次扫描即可

### 配置

```properties
# redis.conf（Redis 7 后这些参数依然保留，但内部已用 listpack）
hash-max-listpack-entries 128
hash-max-listpack-value 64
list-max-listpack-size -2
set-max-listset-entries 512
zset-max-listpack-entries 128
zset-max-listpack-value 64
```

## 其他改进

### 1. 改进的 RDB 加载速度

Redis 7 重写了 RDB 解析器，加载速度比 Redis 6 快 **20%~30%**。

### 2. 多线程 I/O（Redis 6 引入，7 完善）

```properties
# redis.conf
io-threads 4              # 4 个 I/O 线程
io-threads-do-reads yes   # 读也用多线程
```

### 3. 集群下的子命令改进

```bash
# Redis 7 集群模式支持更多子命令
CLUSTER MYID
CLUSTER MYSHARDID
CLUSTER LINKS
```

### 4. 改进的 `FUNCTION FLUSH`

```bash
# 异步刷新
redis-cli FUNCTION FLUSH ASYNC

# 同步刷新
redis-cli FUNCTION FLUSH SYNC
```

## 升级建议

### 从 Redis 6 升级到 7

```bash
# 1. 备份 RDB 和 AOF
cp /var/lib/redis/dump.rdb /backup/
cp /var/lib/redis/appendonlydir/ /backup/appendonlydir.bak/ -r

# 2. 查看不兼容命令
redis-cli --version
# Redis 6.2.x

# 3. 滚动升级主从
# 先升级从节点，确认无异常后再升级主节点
```

### 注意事项

| 项目 | 说明 |
|---|---|
| 客户端协议 | 启用 Client-side Caching 需 RESP3 |
| ACL | Redis 7 ACL 格式与 6 兼容 |
| Lua | Lua 脚本无需修改，但 Functions 是新机制 |
| RDB 格式 | Redis 7 可读 6 的 RDB，但 6 不能读 7 的 RDB |

## 生产监控案例

### 案例 1：升级到 Redis 7 后加载时间减半

某 16GB 实例从 Redis 6 升级到 7 后：

```
Redis 6: 加载 60 秒
Redis 7: 加载 28 秒
```

RDB 解析器优化效果显著，**业务可用性提升明显**。

### 案例 2：Sharded Pub/Sub 减少 90% 带宽

某直播平台用 Pub/Sub 推送弹幕，从 Redis 6 升到 7 后：

```
Redis 6: 每条弹幕广播到所有 24 个节点，带宽 800Mbps
Redis 7: Sharded Pub/Sub，只在 1 个节点传播，带宽 50Mbps
```

### 案例 3：Functions 替代 Lua 后的运维改善

某公司 200 个 Lua 脚本，升级到 Functions 后：

```bash
# 升级前：脚本分散在各业务代码里，Redis 重启要重载
# 升级后：函数库统一管理，重启自动恢复
```

```
脚本丢失事故：从 5 次/年 → 0 次/年
```

## 下一步

Redis 运维的所有知识点都在这里了。下一步到 [📝 高频面试题（上）](/08-interview/basic)，把这些核心知识点串成面试题答案。

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [mysql](https://java-px.bot.cd/mysql/):MySQL 主存
- [kafka](https://java-px.bot.cd/kafka/):Kafka 异步队列
- [java](https://java-px.bot.cd/java-web-manual/):Java 客户端（Redisson / Jedis）
