---
title: 5 大基础类型
date: 2026-08-15  # date-auto-injected
---

# 📦 5 大基础类型


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
> Redis 不是简单的 key-value 缓存，**value 可以是 5 种不同的数据结构**，每种都针对特定场景优化。

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600" >Redis GEO 地理位置</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">Geohash 编码 + ZSet 存储 · 附近的人 / 餐厅搜索</text>

  <!-- Geohash 原理 -->
  <g>
    <text x="60" y="90" font-size="13" font-weight="700" fill="#1e293b">① Geohash 编码（二分 → Base32）</text>

    <rect class="at-hover-card" x="40" y="105" width="520" height="120" rx="6" fill="#f1f5f9" stroke="#64748b" stroke-width="1.5"/>

    <!-- 经度 116.40, 纬度 39.90 -->
    <text x="60" y="128" font-size="10" font-weight="700" fill="#1e293b">例：北京天安门 (116.40, 39.90)</text>

    <rect class="at-hover-card" x="60" y="138" width="240" height="75" rx="3" fill="#1e293b"/>
    <text x="75" y="155" font-size="9" font-family="monospace" fill="#a7f3d0">经度 [-180, 180] 二分:</text>
    <text x="75" y="170" font-size="9" font-family="monospace" fill="#fde68a">116.40 ∈ [0, 180) → 1</text>
    <text x="75" y="185" font-size="9" font-family="monospace" fill="#fde68a">116.40 ∈ [90, 180) → 1</text>
    <text x="75" y="200" font-size="9" font-family="monospace" fill="#fde68a">...</text>
    <text x="75" y="215" font-size="9" font-family="monospace" fill="#a7f3d0">纬度 [-90, 90] 同理</text>

    <path d="M 300 175 L 335 175" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="335" y="138" width="210" height="75" rx="3" fill="#dcfce7" stroke="#10b981"/>
    <text x="450" y="160" text-anchor="middle" font-size="10" font-weight="700" fill="#065f46">geohash = "wx4g8c"</text>
    <text x="450" y="180" text-anchor="middle" font-size="9" font-family="monospace" fill="#1e293b">1101001110111011...</text>
    <text x="450" y="197" text-anchor="middle" font-size="9" font-family="monospace" fill="#1e293b">→ base32 编码</text>
    <text x="450" y="210" text-anchor="middle" font-size="8" fill="#475569">精度 ≈ 5m × 5m</text>
  </g>

  <!-- ZSet 存储 -->
  <g>
    <text x="60" y="245" font-size="13" font-weight="700" fill="#1e293b">② Redis 内部用 ZSet 存储（geohash 52-bit 整数）</text>

    <rect class="at-hover-card" x="40" y="260" width="520" height="100" rx="6" fill="#f1f5f9" stroke="#64748b" stroke-width="1.5"/>

    <rect class="at-hover-card" x="55" y="275" width="140" height="70" rx="4" fill="#dbeafe" stroke="#3b82f6"/>
    <text x="125" y="295" text-anchor="middle" font-size="10" font-weight="700" fill="#1e40af">ZSet 键</text>
    <text x="125" y="313" text-anchor="middle" font-size="9" font-family="monospace" fill="#1e293b">"places:bj"</text>
    <text x="125" y="330" text-anchor="middle" font-size="8" fill="#475569">score = geohash</text>
    <text x="125" y="342" text-anchor="middle" font-size="8" fill="#475569">value = 地点名</text>

    <path d="M 195 310 L 225 310" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="225" y="275" width="160" height="70" rx="4" fill="#dcfce7" stroke="#10b981"/>
    <text x="305" y="293" text-anchor="middle" font-size="9" font-weight="700" fill="#065f46">ZSet 元素</text>
    <text x="240" y="312" font-size="9" font-family="monospace" fill="#1e293b">天安门   4069865812</text>
    <text x="240" y="325" font-size="9" font-family="monospace" fill="#1e293b">故宫     4069865522</text>
    <text x="240" y="338" font-size="9" font-family="monospace" fill="#1e293b">国贸     4069871225</text>

    <path d="M 385 310 L 415 310" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="415" y="275" width="135" height="70" rx="4" fill="#fef3c7" stroke="#f59e0b"/>
    <text x="482" y="293" text-anchor="middle" font-size="9" font-weight="700" fill="#92400e">跳表索引</text>
    <text x="430" y="312" font-size="9" fill="#475569">范围查询 O(log N)</text>
    <text x="430" y="325" font-size="9" fill="#475569">附近搜索：</text>
    <text x="430" y="338" font-size="9" font-family="monospace" fill="#1e293b">ZRANGEBYSCORE</text>
  </g>

  <!-- 6 个核心命令 -->
  <g>
    <text x="60" y="380" font-size="13" font-weight="700" fill="#1e293b">③ 6 个核心命令</text>

    <rect class="at-hover-card" x="40" y="395" width="250" height="70" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
    <text x="60" y="412" font-size="9" font-family="monospace" fill="#1e293b">GEOADD k 116.40 39.90 place</text>
    <text x="60" y="427" font-size="9" font-family="monospace" fill="#1e293b">GEODIST k p1 p2 [km]</text>
    <text x="60" y="442" font-size="9" font-family="monospace" fill="#1e293b">GEOHASH k place</text>
    <text x="60" y="457" font-size="9" font-family="monospace" fill="#1e293b">GEOPOS k place</text>

    <rect class="at-hover-card" x="310" y="395" width="250" height="70" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
    <text x="330" y="412" font-size="9" font-family="monospace" fill="#1e293b">GEOSEARCH k FROMLONLAT x y</text>
    <text x="330" y="427" font-size="9" font-family="monospace" fill="#1e293b">  BYRADIUS 5 km</text>
    <text x="330" y="442" font-size="9" font-family="monospace" fill="#1e293b">  WITHCOORD WITHDIST</text>
    <text x="330" y="457" font-size="9" font-family="monospace" fill="#1e293b">GEORADIUS k 116.40 39.90 5 km</text>
  </g>
</svg>
## 🎯 5 大类型一览

| 类型 | 描述 | 底层编码（Redis 7） | 适用场景 |
|------|------|---------------------|---------|
| **String** | 字符串 / 数字 / 二进制 | int / embstr / raw | 缓存、计数器、分布式锁 |
| **Hash** | 字段-值映射表 | listpack / hashtable | 对象存储（用户资料） |
| **List** | 有序可重复列表 | quicklist | 消息队列、最新列表 |
| **Set** | 无序不重复集合 | intset / hashtable | 标签、共同好友、抽奖 |
| **ZSet** | 有序不重复集合 | listpack / skiplist+hashtable | 排行榜、延迟队列 |

## 📝 String 字符串

> **最简单也最常用**。可以是字符串、整数、浮点数、二进制（最大 512MB）。

```bash
# 设置 key（SET key value [EX seconds | PX ms] [NX|XX]）
SET user:1:name "Alice"              # 设置字符串
SET counter 100                      # 设置数字
SET lock:order:1 "1" EX 30 NX        # 加锁（30 秒过期，只在不存在时设置）
SETBIT bitmap 7 1                    # 设置二进制的第 7 位

# 获取 key
GET user:1:name                      # → "Alice"
GETBIT bitmap 7                      # → 1
STRLEN user:1:name                   # → 5
GETRANGE user:1:name 0 2             # → "Ali"

# 数字操作（原子）
INCR counter                         # 自增 1 → 101
DECR counter                         # 自减 1 → 100
INCRBY counter 10                    # 增加 10 → 110
INCRBYFLOAT price 0.5                # 浮点增加
DECRBY counter 5                     # 减少 5 → 105

# 批量操作
MGET user:1:name user:2:name         # → "Alice", "Bob"
MSET user:1:age 28 user:2:age 30     # 批量设置
```

**场景**：缓存 JSON、计数器（文章阅读量）、分布式锁、Session、限流。

## 🗂️ Hash 哈希

> **字段-值**的映射表。适合存储**对象**（一个 key 包含多个字段）。

```bash
# 单字段操作
HSET user:1 name "Alice" age 28      # 设置 name 和 age
HGET user:1 name                     # → "Alice"
HGET user:1 age                      # → 28
HEXISTS user:1 name                  # → 1（存在）

# 多字段操作
HMSET user:1 name "Alice" age 28 city "Beijing"   # 批量设置（旧）
HSET user:1 name "Alice" age 28 city "Beijing"    # 批量设置（新，支持多 field）

HMGET user:1 name age                # → "Alice", "28"
HGETALL user:1                       # → 全部字段
HKEYS user:1                         # → 所有字段名
HVALS user:1                         # → 所有字段值
HLEN user:1                          # → 字段总数

# 数值操作
HINCRBY user:1 age 1                 # age 字段 +1（原子）
HDEL user:1 city                     # 删除字段
```

**场景**：用户资料、商品属性、购物车（field=商品ID, value=数量）。

```bash
# 购物车实战
HSET cart:user:1001 1001 1           # 商品 1001 数量 1
HSET cart:user:1001 1002 2           # 商品 1002 数量 2
HGETALL cart:user:1001               # 查看购物车
HINCRBY cart:user:1001 1001 1        # 商品 1001 +1
```

## 📜 List 列表

> **有序可重复**的字符串列表。底层是 **quicklist**（双向链表 + listpack）。

```bash
# 插入元素
LPUSH news "msg1"                    # 左侧压入
RPUSH news "msg3"                    # 右侧压入
LPUSH news "msg2" "msg4"             # 左侧压入多个
# 结果：news = [msg4, msg2, msg1, msg3]

# 弹出元素
LPOP news                            # → "msg4"（左侧弹出）
RPOP news                            # → "msg3"（右侧弹出）

# 获取元素
LRANGE news 0 -1                     # 获取所有元素
LRANGE news 0 2                      # 获取前 3 个
LINDEX news 0                        # 获取下标 0
LLEN news                            # → 长度
LSET news 0 "new msg1"               # 修改下标 0

# 阻塞队列
BRPOP news 30                        # 阻塞等待右侧弹出，超时 30 秒
```

**场景**：消息队列（LPUSH + BRPOP）、最新文章列表（LPUSH + LRANGE 0 9）、关注列表。

```bash
# 消息队列实战
LPUSH task:queue "task1"
LPUSH task:queue "task2"
BRPOP task:queue 0                   # 阻塞消费，永远等待直到有任务
```

## 🎯 Set 集合

> **无序不重复**的字符串集合。底层是 **intset（整数集合）** 或 **hashtable**。

```bash
# 添加元素
SADD tags:article:1 "redis" "db" "cache"
SADD tags:article:2 "redis" "nosql"

# 获取元素
SMEMBERS tags:article:1              # → {redis, db, cache}
SISMEMBER tags:article:1 "redis"     # → 1（是成员）
SCARD tags:article:1                 # → 3（基数）
SPOP tags:article:1 2                # 随机弹出 2 个

# 删除
SREM tags:article:1 "cache"

# 集合运算
SINTER tags:article:1 tags:article:2 # 交集：共同标签
SUNION tags:article:1 tags:article:2 # 并集
SDIFF  tags:article:1 tags:article:2 # 差集：A 有 B 没有

# 随机抽取（抽奖）
SRANDMEMBER lucky:draw 3             # 随机抽 3 人（不删除）
SPOP lucky:draw 1                    # 抽 1 人（删除）
```

**场景**：标签、共同好友、抽奖、UV 统计、点赞用户集合。

```bash
# 抽奖实战
SADD lucky:draw user:1 user:2 user:3 ... user:100
SPOP lucky:draw 1                    # 中奖
```

## 🏆 ZSet 有序集合

> **有序不重复**的集合，每个元素关联一个 score（分数）。底层是 **skiplist + hashtable** 双结构。

```bash
# 添加元素
ZADD leaderboard 95 "Alice" 87 "Bob" 76 "Charlie"
ZADD leaderboard 88 "David"          # 添加一个

# 获取元素（按 score 升序）
ZRANGE leaderboard 0 -1              # → Charlie, Bob, David, Alice
ZRANGE leaderboard 0 -1 WITHSCORES   # → 含分数
ZREVRANGE leaderboard 0 -1 WITHSCORES  # 倒序

# 按分数区间
ZRANGEBYSCORE leaderboard 80 100     # 分数 80-100 之间
ZRANGEBYSCORE leaderboard (80 100    # 大于 80 小于等于 100

# 排名 / 分数
ZSCORE leaderboard "Alice"           # → 95
ZRANK leaderboard "Alice"            # → 3（从 0 开始，升序）
ZREVRANK leaderboard "Alice"         # → 0（倒序第一名）

# 修改分数
ZINCRBY leaderboard 5 "Alice"        # Alice +5 分 → 100
ZINCRBY leaderboard -10 "Bob"        # Bob -10 分 → 77

# 删除
ZREM leaderboard "Charlie"
ZREMRANGEBYSCORE leaderboard 0 80    # 删除 80 分以下

# 统计
ZCARD leaderboard                    # 元素总数
ZCOUNT leaderboard 80 100            # 80-100 分的人数
```

**场景**：排行榜（游戏 / 销量 / 积分）、延迟队列（score=执行时间）、滑动窗口限流。

```bash
# 延迟队列实战（score = 时间戳）
ZADD delay:queue 1730000000 "task1"  # 任务 1 在 1730000000 后执行
ZRANGEBYSCORE delay:queue 0 $(date +%s) LIMIT 0 10  # 取到期任务
ZREM delay:queue "task1"             # 取出后删除（避免重复执行）
```

## 🔄 编码自动转换

Redis 会根据**数据规模**自动选择最优底层编码：

| 类型 | 阈值（Redis 7 默认） | 小数据编码 | 大数据编码 |
|------|----------------------|-----------|-----------|
| Hash | `hash-max-listpack-entries = 128`<br/>`hash-max-listpack-value = 64 字节` | listpack | hashtable |
| Set | `set-max-intset-entries = 512`（仅当所有元素是整数） | intset | hashtable |
| ZSet | `zset-max-listpack-entries = 128`<br/>`zset-max-listpack-value = 64 字节` | listpack | skiplist+hashtable |
| List | 总是 quicklist（list-max-listpack-size 控制节点大小） | quicklist | quicklist |

```bash
# 查看实际编码
OBJECT ENCODING user:1               # → "listpack" 或 "hashtable"
OBJECT HELP                          # 查看 OBJECT 系列命令
DEBUG OBJECT user:1                  # 查看详细信息
```

**为什么要编码转换**：小数据用 listpack 节省内存，大数据用 hashtable 保证性能。

## 📊 5 大类型对比

| 维度 | String | Hash | List | Set | ZSet |
|------|--------|------|------|-----|------|
| **有序** | - | - | ✅ | ❌ | ✅ |
| **重复** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **查找复杂度** | O(1) | O(1) | O(N) | O(1) | O(log N) |
| **内存效率** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **典型场景** | 缓存 | 对象 | 队列 | 标签 | 排行 |

## 🎯 选型指南

```
✅ 计数器、单个字段的缓存      → String
✅ 用户资料、商品属性          → Hash
✅ 队列、最新列表              → List
✅ 标签、共同好友、抽奖        → Set
✅ 排行榜、延迟队列、滑动窗口   → ZSet
```

## 🛠️ 实战：用户资料 3 种存法对比

```bash
# 方案 1：JSON 字符串
SET user:1 '{"name":"Alice","age":28}'
GET user:1                           # 一次取所有，修改需全量写

# 方案 2：Hash（推荐）
HSET user:1 name "Alice" age 28
HGET user:1 name                     # 单字段读，节省带宽
HINCRBY user:1 age 1                 # 原子自增

# 方案 3：多个 String
SET user:1:name "Alice"
SET user:1:age 28                    # 单字段粒度更细，但 key 数量膨胀
```

**推荐**：Hash 是对象存储的最优解。

## ⚠️ 常见误区

```bash
# ❌ 用 List 当消息队列 - 缺少 ACK 机制
LPUSH task:queue "task1"
BRPOP task:queue                     # 如果消费者崩溃，任务丢失

# ✅ 用 Stream 做消息队列（推荐）
XADD task:stream * payload "task1"
XREADGROUP GROUP g1 c1 COUNT 1 STREAMS task:stream >
XACK task:stream g1 1698...          # 确认消费
```

## 🧪 互动练习

<ClientOnly>
  <CommandPlayground />
</ClientOnly>

试试在 Playground 里用 5 种类型的命令：

```bash
SET greeting "Hello"
HSET user name "Alice" age 28
LPUSH tasks "task1" "task2"
SADD tags "redis" "db" "cache"
ZADD scores 90 "alice" 80 "bob"
```

## 🎯 总结

**5 大基础类型核心**：
- ✅ String：缓存、计数器、分布式锁
- ✅ Hash：对象存储、购物车
- ✅ List：消息队列、最新列表
- ✅ Set：标签、共同好友、抽奖
- ✅ ZSet：排行榜、延迟队列

**编码自动转换**：小数据用 listpack/intset 节省内存，大数据用 hashtable/skiplist 保证性能。

**下一步：** [🔑 Key 通用操作](/01-basics/keys) — KEYS / SCAN / EXISTS / DEL / 命名规范

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [mysql](https://java-px.bot.cd/mysql/):MySQL 主存
- [kafka](https://java-px.bot.cd/kafka/):Kafka 异步队列
- [java](https://java-px.bot.cd/java-web-manual/):Java 客户端（Redisson / Jedis）
