---
title: 过期策略
---

# ⏱️ 过期策略

> Redis 不是所有 key 都永久存在，**每个 key 都可以设置过期时间（TTL）**。理解 Redis 如何处理过期 key，是理解内存淘汰的前提。

## 🎯 为什么需要过期策略？

```bash
# 场景 1：缓存必须有过期时间
SET cache:user:1001 "{...}" EX 600    # 缓存 10 分钟过期

# 场景 2：验证码 5 分钟失效
SET verify:phone:13800138000 "1234" EX 300

# 场景 3：分布式锁 30 秒自动释放
SET lock:order:1001 "uuid" EX 30 NX

# 场景 4：限流统计（1 分钟滑动窗口）
SET ratelimit:user:1001 1 EX 60 NX
```

如果不过期 → **内存无限增长** → Redis OOM（内存溢出）。

## ⏰ TTL 命令

### 设置过期时间

```bash
# EXPIRE：设置秒级过期
EXPIRE user:1 60                      # 60 秒后过期
EXPIRE user:1 60 XX                   # 仅在 key 存在时设置过期

# PEXPIRE：设置毫秒级过期
PEXPIRE user:1 60000                  # 60000 毫秒后过期

# SET 时直接设置（推荐）
SET user:1 "value" EX 60              # 等价于 SET + EXPIRE
SET user:1 "value" PX 60000           # 毫秒
SET user:1 "value" EXAT 1730000000    # Unix 时间戳（秒）
SET user:1 "value" PXAT 1730000000000 # Unix 时间戳（毫秒）

# EXPIREAT：Unix 时间戳（秒）
EXPIREAT user:1 1730000000            # 到时间点过期
```

### 查看 TTL

```bash
TTL user:1                            # 剩余 TTL（秒）
TTL user:1                            # 返回值含义：
                                      #   > 0  剩余秒数
                                      #   -1   没有设置过期（永久存在）
                                      #   -2   key 不存在

PTTL user:1                           # 剩余 TTL（毫秒）

# 示例
SET user:1 "alice" EX 60
TTL user:1                            # → 60
TTL user:2                            # → -2（不存在）
SET user:2 "bob"
TTL user:2                            # → -1（无过期）
```

### 取消过期

```bash
# 移除 key 的过期时间（让 key 永久存在）
PERSIST user:1
TTL user:1                            # → -1
```

### TTL 精度

Redis 7+ 提供**精确过期**：
- ✅ Redis 7.4+ 通过 hash table 多级索引实现精确过期
- ⚠️ Redis 7.4 之前是**惰性删除 + 定期删除**，可能有几十秒延迟
- ⚠️ 即使 key 已过期，业务可能仍读到数据（直到访问时才被删除）

## 🧠 过期删除策略

> Redis 不会主动轮询所有 key 是否过期，而是采用**三种策略组合**：

### 1. 惰性删除（Lazy Expiration）

```bash
# 访问 key 时才检查是否过期
GET user:1                            # 如果已过期，返回 nil 并删除
```

**优点**：对 CPU 友好，不需要后台扫描
**缺点**：已经过期的 key 如果再也没人访问，会一直占用内存

### 2. 定期删除（Periodic Expiration）

```bash
# 后台定时任务，每 100ms 扫描一批 key
# 默认：每秒 10 次（hz 10）
# 每次扫描不超过 25 个 key
# 删除逻辑：
#   1. 随机取 20 个 key
#   2. 删除其中过期的 key
#   3. 如果过期 key 占比 > 25%，重复步骤 1-2
```

**优点**：能在合理时间内清理过期 key
**缺点**：不能保证所有过期 key 立即被删除

### 3. 主动清理（Active Expire Cycle，Redis 7.4+）

Redis 7.4 引入了**主动过期循环**，不再依赖惰性删除：
- 后台线程主动扫描过期 key
- 可以在配置时间窗口内清理掉大部分过期 key
- 减少内存泄漏风险

### 三种策略组合

```
┌────────────────────────────────────┐
│       Redis 内存中的所有 Key         │
├────────────────────────────────────┤
│  持久 key（无过期）                  │
│  过期 key（未到期）                  │
│  过期 key（已到期）                  │ ← 等待清理
└────────────────────────────────────┘
                ↓
    ┌──────────────────────┐
    │   访问时惰性删除        │ ← 立即删除被访问的过期 key
    └──────────────────────┘
                ↓
    ┌──────────────────────┐
    │   定期删除（每 100ms）  │ ← 随机扫描过期 key
    └──────────────────────┘
                ↓
    ┌──────────────────────┐
    │  Redis 7.4+ 主动清理   │ ← 后台线程扫描
    └──────────────────────┘
                ↓
    ┌──────────────────────┐
    │ 仍未清理的过期 key      │
│  → 当内存不足时触发【内存淘汰】│
    └──────────────────────┘
```

## 💾 TTL 实现原理

### 内部数据结构

Redis 在每个 key 的内部结构 `redisObject` 中保存 TTL 信息：

```c
typedef struct redisObject {
    unsigned type:4;        // 类型
    unsigned encoding:4;    // 编码
    unsigned lru:24;        // LRU 或 LFU 信息
    int refcount;           // 引用计数
    void *ptr;              // 数据指针
} robj;
```

TTL 单独存储在 `expires` 哈希表中：

```
keyspace（数据字典）     expires（过期字典）
┌──────────┐           ┌──────────┐
│ key      │ ──────→   │ key      │
│ value    │           │ ttl      │
└──────────┘           └──────────┘
```

### 过期字典的维护

```bash
# EXPIRE 调用：
# 1. 在 expires dict 中查找 key
# 2. 如果存在，更新过期时间
# 3. 如果不存在，添加新条目
# 4. 内存占用：每个 TTL 条目 ~16 字节

# 清理过期条目：
# - 惰性删除：从 expires dict 删除
# - 定期删除：从 expires dict 删除
# - AOF 重写：不会写入 expires（避免 AOF 文件膨胀）
```

## 📊 TTL 相关配置

```properties
# redis.conf 中关于过期的配置

# 定期删除的执行频率（每秒多少次）
hz 10                                  # 默认 10，可调整到 100 提升清理速度

# 主动清理（Redis 7.4+）
active-expire-effort 1                 # 1-10，越大越积极清理，但 CPU 占用更高
#   1 = 默认
#   10 = 非常激进（生产慎用）

# 启用 keyspace 通知
notify-keyspace-events Ex              # Ex = 监听 expired 事件
# 完整事件类型：
#   K  Keyspace 事件，以 __keyspace@<db>__ 前缀发布
#   E  Keyevent 事件，以 __keyevent@<db>__ 前缀发布
#   g  del、expire、rename 等通用命令
#   $  String 命令
#   l  List 命令
#   s  Set 命令
#   h  Hash 命令
#   z  ZSet 命令
#   x  过期事件（每次 key 过期时）
#   e  驱逐事件（maxmemory 淘汰时）
#   A  g$lshzxe 的别名
```

## 🔔 keyspace 通知实战

监听 key 过期事件，实现**自动清理缓存**：

```bash
# 1. 启用通知
CONFIG SET notify-keyspace-events Ex

# 2. 订阅过期事件（另一个客户端）
redis-cli PSUBSCRIBE "__keyevent@0__:expired"
```

**Java 实现：**

```java
@Configuration
public class RedisListenerConfig {

    @Bean
    public RedisMessageListenerContainer listener(RedisConnectionFactory factory) {
        RedisMessageListenerContainer container = new RedisMessageListenerContainer();
        container.setConnectionFactory(factory);

        // 监听所有 db 的过期事件
        container.addMessageListener((message, pattern) -> {
            String key = new String(message.getBody());
            System.out.println("Key expired: " + key);
            // 业务逻辑：清理关联缓存、记录日志等
        }, PatternTopic("__keyevent@*__:expired"));

        return container;
    }
}
```

## ⚠️ 过期与内存淘汰的关系

```
过期删除 vs 内存淘汰 是两个不同的机制：

过期删除：
  - 处理设置了 TTL 的 key
  - 时间到了就清理（无论内存是否够）

内存淘汰：
  - 处理所有 key（包括无过期的）
  - 内存不足时主动清理
  - 有 8 种策略可选
```

### 触发顺序

```
1. 写入新 key 时
   ↓
2. 检查 maxmemory 是否足够
   ↓ 不够
3. 尝试清理过期 key（过期删除）
   ↓ 仍不够
4. 触发内存淘汰策略（按策略清理）
   ↓ 仍不够
5. 返回 OOM 错误（拒绝写入）
```

```bash
# 关键配置
CONFIG SET maxmemory 4gb              # 最大内存
CONFIG SET maxmemory-policy volatile-lru   # 淘汰策略
CONFIG SET maxmemory-samples 5       # LRU/LFU 采样精度
```

## 🎯 实战：TTL 使用场景

### 场景 1：Session 存储

```java
// 写入 session
redisTemplate.opsForValue().set("session:" + sessionId, user, 30, TimeUnit.MINUTES);

// 自动清理过期 session（依赖 Redis 过期删除）
```

### 场景 2：验证码

```java
// 发送验证码
String code = generateCode(6);
redisTemplate.opsForValue().set("verify:" + phone, code, 5, TimeUnit.MINUTES);

// 校验验证码
String stored = redisTemplate.opsForValue().get("verify:" + phone);
if (code.equals(stored)) {
    redisTemplate.delete("verify:" + phone);  // 校验成功后立即删除
    return true;
}
return false;
```

### 场景 3：限流

```java
// 1 分钟内最多 100 次请求
Long count = redisTemplate.opsForValue().increment("ratelimit:" + userId);
if (count == 1) {
    redisTemplate.expire("ratelimit:" + userId, 60, TimeUnit.SECONDS);
}
if (count > 100) {
    throw new RateLimitException();
}
```

## 🧪 互动练习

<ClientOnly>
  <CommandPlayground />
</ClientOnly>

```bash
SET greeting "Hello Redis"
EXPIRE greeting 60
TTL greeting
PEXPIRE greeting 30000
TTL greeting
PERSIST greeting
TTL greeting
```

## 🎯 总结

**TTL 核心命令**：
- ✅ `EXPIRE / PEXPIRE`：设置秒级/毫秒级过期
- ✅ `EXPIREAT`：Unix 时间戳
- ✅ `TTL / PTTL`：查看剩余时间
- ✅ `PERSIST`：移除过期（永不过期）
- ✅ `SET key value EX 60`：一步到位

**过期删除机制**：
- 🔄 惰性删除（访问时）
- 🔄 定期删除（每 100ms）
- 🔄 主动清理（Redis 7.4+）

**注意事项**：
- ⚠️ 过期 key 不是立即删除的，可能有几十秒延迟
- ⚠️ 内存不足时，即使 key 未过期也会被淘汰
- ⚠️ Redis 7.4 之前没有主动清理，过期 key 会一直占用内存直到被淘汰

**下一步：** [🎯 RedisObject](/02-datastruct/object) — 深入了解 5 大类型的底层 RedisObject 结构
