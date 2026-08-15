---
title: 内存管理优化
---

# 内存管理优化

Redis 的内存不是"用了多少就是多少"。一段 string 可能占 64 字节，一个 hash 可能比预期多 3 倍开销。理解底层结构、编码阈值、碎片率，才能把内存真打下去。

## 内存结构总览

Redis 每个 key 在内存里由三部分组成：

```
┌─────────────────────────────────────────────┐
│ redisObject (16 字节固定头)                  │
│  ├─ type (4B)：string/list/hash/set/zset    │
│  ├─ encoding (4B)：实际编码（见下文）        │
│  ├─ lru/lfu (24b) + refcount (8B)           │
│  └─ ptr (8B)：指向底层数据结构               │
├─────────────────────────────────────────────┤
│ 底层编码数据                                  │
│  ├─ SDS（简单动态字符串）                     │
│  ├─ listpack / intset / dict / skiplist     │
│  └─ 过期时间（独立 dict 存储，32 位时间戳）   │
└─────────────────────────────────────────────┘
```

### 一个 string 占多少内存？

```bash
redis-cli SET k hello
redis-cli DEBUG OBJECT k
# Value at:0x... refcount:1 encoding:embstr serializedlength:5 lru:... lfu:1 1

redis-cli MEMORY USAGE k
# (integer) 56  ← 实际 56 字节，"hello" 才 5 字节
```

56 字节里：redisObject 16 + SDS 头 4 + 字符串 5 + 空闲填充 + dictEntry 开销。所以**短 key 也别乱存，Redis 不是 KV 数据库，是 KV 内存开销放大器**。

## INFO MEMORY 详解

```bash
redis-cli INFO MEMORY
```

关键字段解读：

| 字段 | 含义 | 健康阈值 |
|---|---|---|
| `used_memory` | Redis 实际占用 | — |
| `used_memory_human` | 同上，人类可读 | — |
| `used_memory_rss` | 操作系统分配（包含碎片） | ≈ used_memory |
| `used_memory_peak` | 历史峰值 | 用于容量规划 |
| `used_memory_dataset` | 纯数据大小 | ≈ 业务数据估算 |
| `mem_fragmentation_ratio` | rss / used_memory | **1.0 ~ 1.5** |
| `mem_allocator` | 分配器（jemalloc / glibc） | 推荐 jemalloc |
| `lazyfree_pending_objects` | 待异步释放对象数 | 持续 > 0 要警惕 |

### mem_fragmentation_ratio 详解

```bash
# 比例 = used_memory_rss / used_memory
# 1.0：完美，无碎片
# 1.5：碎片 50%，常见但偏高
# > 2.0：碎片严重，必须处理
# < 1.0：swap 了，危险
```

碎片来源：
- 频繁修改不同大小的 key（删除大 key 后留下空洞）
- 大量过期 key 未及时回收
- 分配器策略（jemalloc 按 size class 分配，跨档位会浪费）

## 内存优化编码

Redis 为了省内存，会按数据规模自动切换编码。理解阈值才能预判内存。

### String 编码

| 编码 | 触发条件 | 内存 |
|---|---|---|
| `int` | 值是数字（如 `SET counter 1000`） | 16B |
| `embstr` | 字符串 ≤ 44 字节 | 64B（含 SDS） |
| `raw` | 字符串 > 44 字节 | 动态 |

```bash
redis-cli SET n 1000
redis-cli OBJECT ENCODING n
# "int"

redis-cli SET s "a"*44
redis-cli OBJECT ENCODING s
# "embstr"

redis-cli SET s "a"*45
redis-cli OBJECT ENCODING s
# "raw"
```

> 能用数字就别用字符串。`SET user:1:id "10086"` 占 64 字节，`SET user:1:id 10086` 只占 16 字节。

### Hash / List / Set / Zset 编码阈值

```properties
# redis.conf（Redis 7 后大部分被 listpack 替代）
hash-max-listpack-entries 128       # 字段数阈值
hash-max-listpack-value 64          # 单字段字节阈值
list-max-listpack-size -2           # listpack 总字节阈值（-2 = 8KB）
set-max-intset-entries 512          # 整数 set 阈值
zset-max-listpack-entries 128
zset-max-listpack-value 64
```

当数据量超过阈值，Redis 自动升级到更"贵"的编码：

| 数据类型 | 小数据用 | 大数据自动升级到 |
|---|---|---|
| Hash | `listpack`（紧凑） | `hashtable` |
| List | `listpack` | `linkedlist` / `quicklist` |
| Set（纯整数） | `intset` | `hashtable` |
| Zset | `listpack` | `skiplist + dict` |

```bash
# 查看实际编码
redis-cli HSET h f1 v1 f2 v2
redis-cli OBJECT ENCODING h
# "listpack"

# 加到 200 个字段
for i in $(seq 1 200); do redis-cli HSET h "f$i" "v$i"; done
redis-cli OBJECT ENCODING h
# "hashtable"  ← 自动升级
```

### 内存差距有多大？

```bash
# 测试一个 hash
redis-cli HSET bighash field1 "a short value"
for i in $(seq 1 50); do redis-cli HSET bighash "field$i" "value$i"; done

redis-cli MEMORY USAGE bighash
# (integer) 2048    # listpack 编码

# 加到 200 个字段，触发 hashtable 升级
for i in $(seq 100 300); do redis-cli HSET bighash "field$i" "value$i"; done
redis-cli MEMORY USAGE bighash
# (integer) 18432   # hashtable 编码，9 倍内存！
```

### 优化建议

1. **拆分大 hash**：超过 100 字段的 hash 拆成多个小 hash（用 `tag` 分组）
2. **控制单字段长度**：超过 64 字节的字段单独存
3. **整数能用 int 就别用字符串**

## 多 key 共享 value

Redis 不支持传统意义上的"引用共享"，但有几个 trick 能间接省内存。

### 1. 整数对象池

Redis 启动时预创建 0~9999 的整数对象，多个 key 引用同一个整数时只占一份内存：

```bash
# 这两个 key 共用同一个 redisObject
redis-cli SET a 100
redis-cli SET b 100

redis-cli DEBUG OBJECT a | grep refcount
# refcount:2
```

字符串、列表等复杂对象没有这个机制。

### 2. 客户端共享连接

不是 Redis 层的优化，但是常被忽略：每个客户端连接占 ~3MB 内存，1000 个连接就是 3GB。

```properties
# redis.conf
timeout 300             # 空闲连接 5 分钟自动断开
tcp-keepalive 60        # TCP keepalive
maxclients 10000        # 上限保护
```

### 3. 用 tag 减少 key 数量

```bash
# 不推荐：每个字段一个 key
SET user:1:name "Alice"
SET user:1:age 30
SET user:1:email "alice@example.com"
# 3 个 redisObject = 48B + 字符串

# 推荐：用 hash
HSET user:1 name "Alice" age 30 email "alice@example.com"
# 1 个 redisObject + listpack
```

## 内存碎片处理

### 检测碎片

```bash
redis-cli INFO memory | grep fragmentation
# mem_fragmentation_ratio:1.85
```

### 碎片率治理

| 碎片率 | 状态 | 处理 |
|---|---|---|
| 1.0 ~ 1.5 | 正常 | 无需处理 |
| 1.5 ~ 2.0 | 偏高 | 启用 `activedefrag` |
| > 2.0 | 严重 | 重启实例 或 `activedefrag yes` |

Redis 4.0+ 支持在线碎片整理：

```properties
# redis.conf
activedefrag yes

# 内存碎片达到 10% 时开始
active-defrag-enabled yes
active-defrag-threshold-lower 10
active-defrag-threshold-upper 100

active-defrag-cycle-min 5          # 占用 CPU 最低 5%
active-defrag-cycle-max 75         # 占用 CPU 最高 75%
active-defrag-max-scan-fields 1000
```

`activedefrag` 是后台渐进式整理，会占用 CPU，**不要在高峰期开启**。

### 终极方案：重启

碎片率 > 3 时，重启最有效：

```bash
# 1. 启用 AOF 或 RDB
# 2. 优雅关闭
redis-cli SHUTDOWN NOSAVE

# 3. 重启，Redis 从磁盘加载数据，内存重排
systemctl start redis
```

## 生产监控案例

### 案例 1：内存从 8GB 涨到 12GB 排查

```bash
# 1. 看总体
INFO MEMORY | grep used_memory_human
# used_memory_human:11.87G

# 2. 找大 key
redis-cli --bigkeys
# [00.00%] Biggest string found so far '"session:abc..."' with 2048 bytes
# [50.00%] Biggest   hash found so far '"order:detail:1"' with 524288 bytes

# 3. 看具体大 key
redis-cli MEMORY USAGE "order:detail:1"
# (integer) 8388608  ← 8MB

# 4. 看碎片
INFO MEMORY | grep fragmentation
# mem_fragmentation_ratio:1.42
```

定位到一个 order:detail hash 存了全字段，2MB 一个。拆分后内存降到 7GB。

### 案例 2：activedefrag 引发 CPU 100%

某实例开启 `activedefrag yes` 后 CPU 打满：

```bash
redis-cli INFO CPU | grep used_cpu_sys
# used_cpu_sys:890.23    # 比平时高 10 倍
```

```properties
# 调整碎片整理节奏
active-defrag-cycle-min 1
active-defrag-cycle-max 25    # 降低上限
```

整理一晚上后碎片率从 2.3 降到 1.2。

## 下一步

内存优化的下一步是找出"谁在吃内存"。看 [🔑 大 Key 热 Key](/07-ops/bigkey-hotkey)，定位元凶并拆分。