---
title: Key 通用操作
date: 2026-08-15  # date-auto-injected
---

# 🔑 Key 通用操作

> 掌握 Key 的**查找、删除、判断、命名规范**，是 Redis 使用的基石。

## 🔍 Key 查找

### KEYS 命令（⚠️ 危险！）

```bash
# 匹配所有 key
KEYS *                               # ⚠️ 生产环境禁用！会阻塞主线程

# glob 模式匹配
KEYS user:*                          # 匹配 user: 开头的所有 key
KEYS order:2024:*                    # 多级通配
KEYS user:1??                        # 通配单个字符（user:1 开头，2 位）
KEYS user:[12]*                      # 方括号匹配单个字符
```

**为什么 KEYS 危险？**
- KEYS 是 O(N) 操作，需要遍历所有 key
- 在百万级 key 时，阻塞主线程几秒甚至几十秒
- 阻塞期间所有客户端请求都会被挂起
- **生产环境绝对不能用**

### SCAN 命令（✅ 推荐）

```bash
# 渐进式迭代（不会阻塞主线程）
SCAN 0                               # 从游标 0 开始，返回新的游标
SCAN 0 MATCH user:* COUNT 100        # 匹配模式 + 每次扫描 100 个
SCAN 0 MATCH order:* COUNT 50

# 完整遍历示例
cursor=0
while [ "$cursor" != "0" ]; do
    result=$(redis-cli SCAN $cursor MATCH "user:*" COUNT 100)
    cursor=$(echo $result | head -1)
    echo $result | tail -n +2        # 输出本次匹配的 key
done
```

**SCAN 的特点：**
- ✅ 每次只返回少量 key，不阻塞
- ⚠️ 不保证每次返回不重复（可能某个 key 被返回多次）
- ⚠️ 迭代过程中如果有新 key，不保证能扫到
- ✅ 可以在迭代过程中安全地对 key 进行修改

**参数说明：**
- `cursor`：游标，第一次传 0，后续传返回的游标
- `MATCH pattern`：可选的过滤模式
- `COUNT n`：每次扫描的元素数量（提示，不是硬性限制）
- `TYPE type`：只匹配指定类型（Redis 6+）

```bash
SCAN 0 MATCH user:* TYPE string COUNT 100  # 只匹配 string 类型的 key
```

### 性能对比

| 命令 | 时间复杂度 | 阻塞主线程 | 适用场景 |
|------|----------|----------|---------|
| `KEYS pattern` | O(N) | ⚠️ 是 | 调试环境 |
| `SCAN cursor` | O(1) 每次迭代 | ✅ 否 | 生产环境 |
| `DBSIZE` | O(1) | ✅ 否 | 快速统计 key 数量 |

## 📦 Key 存在与类型判断

```bash
# 判断 key 是否存在
EXISTS user:1                         # → 1（存在）
EXISTS user:1 user:2 user:3           # → 2（2 个存在）

# 判断 key 的类型
TYPE user:1                           # → "string" / "hash" / "list" / "set" / "zset"
TYPE missing                          # → "none"

# 删除 key
DEL user:1                            # 删除 1 个
DEL user:1 user:2 user:3              # 删除 3 个（原子操作）

# 异步删除（不阻塞，Redis 4+）
UNLINK user:1                         # 异步删除
UNLINK user:1 user:2                  # 批量异步删除
```

**DEL vs UNLINK：**
- DEL：同步删除，立即释放内存（O(1)，但大 Key 会阻塞）
- UNLINK：异步删除，先从 keyspace 移除，再后台线程释放内存（大 Key 推荐）

## ✏️ Key 重命名

```bash
# 重命名 key
RENAME user:1 user:1:old              # 强制覆盖目标
RENAMENX user:1 user:1:new            # 仅当目标不存在时重命名

# 应用场景：缓存更新时切换
SET cache:product:1001:new "{...}"
RENAME cache:product:1001:new cache:product:1001   # 原子切换
```

## 📏 Key 大小与序列化

```bash
# 查看 value 的序列化长度
STRLEN user:1                         # 字符串长度（字节）
HLEN user:1                           # Hash 字段数
LLEN user:1                           # List 长度
SCARD user:1                          # Set 基数
ZCARD leaderboard                     # ZSet 基数

# 查看 value 的字节数
MEMORY USAGE user:1                   # 这个 key 占用的内存字节数
MEMORY USAGE user:1 SAMPLES 0         # 精确统计

# 序列化 value
DUMP user:1                           # 返回二进制序列化数据
RESTORE user:1:backup 0 "\x..."       # 从序列化数据恢复
```

**MEMORY USAGE 用法：**
- 找到内存占用大的 key（排查大 Key）
- 估算缓存总占用
- 一般搭配 SCAN 使用

```bash
# 找出占用内存最大的 10 个 key
SCAN 0 COUNT 1000 | xargs -I{} sh -c 'echo "$(redis-cli MEMORY USAGE {} 2>/dev/null) {}"' | sort -nr | head -10
```

## 📋 Key 命名规范（最佳实践）

### 命名约定

```
业务:对象:id:字段
```

| 命名 | 含义 | 示例 |
|------|------|------|
| `user:1001:name` | 用户 1001 的名字 | `user:1001:name = "Alice"` |
| `order:2024:1001` | 订单 | `order:2024:1001 = "..."` |
| `cache:product:1001` | 缓存 | `cache:product:1001 = "..."` |
| `lock:order:1001` | 分布式锁 | `lock:order:1001 = "uuid"` |
| `ratelimit:user:1001` | 限流 | `ratelimit:user:1001 = 100` |
| `session:abc123` | 会话 | `session:abc123 = "..."` |

### 命名要点

```
✅ 好的命名
  - user:1001            简短明确
  - order:2024:01:1001   可按时间前缀扫描
  - lock:order:1001      业务对象 + 操作类型

❌ 不好的命名
  - u1                   含义不清
  - userprofile          单层结构，无法扩展
  - ORDER_1001_DATA      大小写不一致 + 下划线不规范
```

### Key 长度限制

- Redis key 最大长度 **512 MB**（实际推荐不超过 1KB）
- 太长的 key 会占用更多内存
- 太短的 key 含义不清

```bash
# ⚠️ 太长的 key
SET user:profile:level:1:section:2:field:3:value "data"
# 上面 50 字节都是 key，浪费内存

# ✅ 简洁的 key
SET user:1:l1:s2:f3 "data"           # 但要在文档里说明含义
```

## 🛡️ 安全与限制

### 禁止的危险命令

```bash
# ⚠️ 生产环境可能阻塞
KEYS *                                # O(N) 阻塞
FLUSHDB                               # 清空当前 DB
FLUSHALL                              # 清空所有 DB
DEBUG SLEEP 5                         # 让 Redis 阻塞 5 秒

# 解决方案：rename-command 重命名
# redis.conf 中配置
rename-command KEYS ""                # 禁用 KEYS
rename-command FLUSHALL ""            # 禁用 FLUSHALL
rename-command CONFIG ""              # 禁用 CONFIG
rename-command DEBUG ""               # 禁用 DEBUG

# 或者改名
rename-command KEYS "KEYS_LIST"
# 这样客户端必须用 KEYS_LIST 才能用
```

### 使用 CONFIG 限制危险操作

```bash
# 限制客户端最大连接数
CONFIG SET maxclients 10000

# 限制 key 最大内存
CONFIG SET maxmemory 4gb

# 限制 keyspace 通知（用于过期事件）
CONFIG SET notify-keyspace-events Ex  # 监听过期事件
```

## 🧹 批量删除

```bash
# 1. 用 SCAN + DEL
cursor=0
while [ "$cursor" != "0" ]; do
    keys=$(redis-cli SCAN $cursor MATCH "temp:*" COUNT 500 | tail -n +2)
    if [ -n "$keys" ]; then
        redis-cli DEL $keys           # 批量删除
    fi
    cursor=$(redis-cli SCAN $cursor MATCH "temp:*" COUNT 500 | head -1)
done

# 2. 用 UNLINK（更安全，非阻塞）
redis-cli --scan --pattern "temp:*" | xargs redis-cli UNLINK

# 3. Lua 脚本（原子）
EVAL "for i,k in ipairs(redis.call('keys', ARGV[1])) do redis.call('del', k) end return 1" 0 "user:*"
```

## 🔄 RANDOMKEY 与 OBJECT

```bash
# 随机返回一个 key
RANDOMKEY                             # → "user:1001"

# 查看 key 的详细信息
OBJECT ENCODING user:1                # 底层编码
OBJECT FREQ user:1                    # LFU 频率（Redis 4.0+）
OBJECT IDLETIME user:1                # 空闲时间（秒）
OBJECT REFCOUNT user:1                # 引用计数（0 表示可释放）
OBJECT HELP                           # 帮助
```

## 🧪 互动练习

<ClientOnly>
  <CommandPlayground />
</ClientOnly>

```bash
SET user:1:name "Alice"
SET user:2:name "Bob"
EXISTS user:1
TYPE user:1
KEYS user:*                           # ⚠️ 别在生产用
SCAN 0 MATCH user:* COUNT 10
```

## 🎯 总结

**Key 操作核心**：
- ✅ `SCAN` 代替 `KEYS`（生产环境）
- ✅ `UNLINK` 代替 `DEL`（大 Key）
- ✅ `MEMORY USAGE` 排查内存问题
- ✅ 命名规范：业务:对象:id:字段
- ✅ 禁用危险命令（rename-command）

**下一步：** [⏱️ 过期策略](/01-basics/expiration) — TTL、过期删除、内存淘汰关系
