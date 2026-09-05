---
title: RedisObject
date: 2026-08-15  # date-auto-injected
---

# 🎯 RedisObject

> Redis 数据库里每一个键值对，在内存中都由一个 `redisObject` 结构承载。它是所有数据类型的"基类"，决定了对象的类型、编码方式和底层容器。

<ClientOnly>
  <DataStructureViz />
</ClientOnly>

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600" >Redis 内存淘汰 8 大策略</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">maxmemory-policy · LRU / LFU · allkeys / volatile</text>

  <!-- 8 策略 -->
  <g>
    <text x="60" y="90" font-size="13" font-weight="700" fill="#1e293b">① 8 种策略总览（按维度分 4 组）</text>

    <rect class="at-hover-card" x="40" y="105" width="125" height="90" rx="4" fill="#dbeafe" stroke="#3b82f6"/>
    <text x="102" y="123" text-anchor="middle" font-size="10" font-weight="700" fill="#1e40af">allkeys-lru</text>
    <text x="55" y="142" font-size="9" fill="#475569">全键 LRU</text>
    <text x="55" y="157" font-size="9" fill="#475569">推荐 ⭐</text>

    <rect class="at-hover-card" x="170" y="105" width="125" height="90" rx="4" fill="#dbeafe" stroke="#3b82f6"/>
    <text x="232" y="123" text-anchor="middle" font-size="10" font-weight="700" fill="#1e40af">volatile-lru</text>
    <text x="185" y="142" font-size="9" fill="#475569">有过期键 LRU</text>
    <text x="185" y="157" font-size="9" fill="#475569">保非过期</text>

    <rect class="at-hover-card" x="300" y="105" width="125" height="90" rx="4" fill="#dcfce7" stroke="#10b981"/>
    <text x="362" y="123" text-anchor="middle" font-size="10" font-weight="700" fill="#065f46">allkeys-lfu</text>
    <text x="315" y="142" font-size="9" fill="#475569">全键 LFU</text>
    <text x="315" y="157" font-size="9" fill="#475569">4.x+ 推荐 ⭐</text>

    <rect class="at-hover-card" x="430" y="105" width="125" height="90" rx="4" fill="#dcfce7" stroke="#10b981"/>
    <text x="492" y="123" text-anchor="middle" font-size="10" font-weight="700" fill="#065f46">volatile-lfu</text>
    <text x="445" y="142" font-size="9" fill="#475569">过期键 LFU</text>
    <text x="445" y="157" font-size="9" fill="#475569">4.x+</text>

    <rect class="at-hover-card" x="40" y="205" width="125" height="90" rx="4" fill="#fef3c7" stroke="#f59e0b"/>
    <text x="102" y="223" text-anchor="middle" font-size="10" font-weight="700" fill="#92400e">allkeys-random</text>
    <text x="55" y="242" font-size="9" fill="#475569">全键随机</text>
    <text x="55" y="257" font-size="9" fill="#475569">少用</text>

    <rect class="at-hover-card" x="170" y="205" width="125" height="90" rx="4" fill="#fef3c7" stroke="#f59e0b"/>
    <text x="232" y="223" text-anchor="middle" font-size="10" font-weight="700" fill="#92400e">volatile-random</text>
    <text x="185" y="242" font-size="9" fill="#475569">过期键随机</text>
    <text x="185" y="257" font-size="9" fill="#475569">少用</text>

    <rect class="at-hover-card" x="300" y="205" width="125" height="90" rx="4" fill="#fee2e2" stroke="#dc2626"/>
    <text x="362" y="223" text-anchor="middle" font-size="10" font-weight="700" fill="#991b1b">volatile-ttl</text>
    <text x="315" y="242" font-size="9" fill="#475569">过期键按 TTL</text>
    <text x="315" y="257" font-size="9" fill="#475569">优先快过期</text>

    <rect class="at-hover-card" x="430" y="205" width="125" height="90" rx="4" fill="#1e293b"/>
    <text x="492" y="223" text-anchor="middle" font-size="10" font-weight="700" fill="#a7f3d0">noeviction</text>
    <text x="445" y="242" font-size="9" fill="#a7f3d0">拒绝写入</text>
    <text x="445" y="257" font-size="9" fill="#a7f3d0">默认 ⛔</text>
  </g>

  <!-- LRU vs LFU -->
  <g>
    <text x="60" y="318" font-size="13" font-weight="700" fill="#1e293b">② LRU vs LFU 区别</text>

    <rect class="at-hover-card" x="40" y="333" width="250" height="130" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
    <text x="165" y="352" text-anchor="middle" font-size="12" font-weight="700" fill="#1e40af">LRU (Least Recently Used)</text>
    <text x="55" y="372" font-size="10" fill="#475569">• 淘汰最久没访问的</text>
    <text x="55" y="388" font-size="10" fill="#475569">• 记录 24-bit 时间戳</text>
    <text x="55" y="404" font-size="10" fill="#475569">• 问题：突发访问误杀</text>
    <text x="55" y="425" font-size="10" font-family="monospace" fill="#1e293b">OBJECT IDLETIME k</text>
    <text x="55" y="441" font-size="9" fill="#475569">→ 看空闲秒数</text>
    <text x="55" y="456" font-size="9" font-weight="700" fill="#1e40af">场景：均匀访问</text>

    <rect class="at-hover-card" x="310" y="333" width="250" height="130" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
    <text x="435" y="352" text-anchor="middle" font-size="12" font-weight="700" fill="#065f46">LFU (Least Frequently Used)</text>
    <text x="325" y="372" font-size="10" fill="#475569">• 淘汰访问频率最低的</text>
    <text x="325" y="388" font-size="10" fill="#475569">• 8-bit counter + 衰减</text>
    <text x="325" y="404" font-size="10" fill="#475569">• 优势：抗突发访问</text>
    <text x="325" y="425" font-size="10" font-family="monospace" fill="#1e293b">OBJECT FREQ k</text>
    <text x="325" y="441" font-size="9" fill="#475569">→ 看访问频率</text>
    <text x="325" y="456" font-size="9" font-weight="700" fill="#065f46">场景：热点分布</text>
  </g>
</svg>
## 一、为什么需要 RedisObject

Redis 的命令处理层是**类型无关**的。比如 `GET` 命令在执行时并不知道底层到底是 int、embstr 还是 raw，它只看 `redisObject.type` 字段，再通过 `type` 特定的命令表分派。

这种"对象头 + 通用 ptr"的设计带来三个好处：

1. **同一链表可以混合不同类型**。`OBJECT ENCODING` 能识别每个对象独立的编码。
2. **五种类型共享同一内存池**，方便用 `zmalloc`/`zfree` 统一管理。
3. **编码转换无侵入**。String 从 embstr 升级到 raw，只需要把 `ptr` 换成新分配的内存即可，对外接口不变。

## 二、redisObject 结构体

源码 `src/server.h`：

```c
typedef struct redisObject {
    unsigned type    : 4;    // 类型：string/list/hash/set/zset
    unsigned encoding: 4;    // 编码：决定 ptr 指向哪种底层结构
    unsigned lru     : 24;   // LRU 时间戳或 LFU 频率（24 bit）
    int refcount;            // 引用计数，用于共享对象
    void *ptr;               // 指向底层数据结构的指针
} robj;
```

字段含义：

| 字段 | 位宽 | 作用 |
|------|------|------|
| type | 4 | 五大类型之一：`OBJ_STRING`、`OBJ_LIST`、`OBJ_HASH`、`OBJ_SET`、`OBJ_ZSET` |
| encoding | 4 | 当前对象采用的底层编码，每种 type 都有多种可选 |
| lru | 24 | 用于 `maxmemory` 淘汰策略，记录上次访问时间或 LFU 计数 |
| refcount | 32 | 引用计数为 0 时释放；`OBJECT REFCOUNT` 可查 |
| ptr | 64 | 实际数据指针，可能是 `sdshdr*`、`dict*`、`skiplist*` 等 |

整个对象头大小：

```text
4 + 4 + 24 = 32 bit  =  4 byte (位域部分)
+ 4 byte (refcount 填充对齐后)
+ 8 byte (ptr)
────────────────────────
≈ 16 byte (实际 sizeof 在 64 位系统)
```

## 三、五大类型与 encoding 映射

```text
type ─┬─ OBJ_STRING ─┬─ OBJ_ENCODING_INT      (整型直接存 ptr)
      │              ├─ OBJ_ENCODING_EMBSTR   (≤44 byte 嵌入式)
      │              └─ OBJ_ENCODING_RAW      (SDS 独立分配)
      ├─ OBJ_LIST   ─── OBJ_ENCODING_QUICKLIST (Redis 7 默认)
      ├─ OBJ_HASH   ─┬─ OBJ_ENCODING_LISTPACK (≤ 阈值)
      │              └─ OBJ_ENCODING_HT       (超过阈值)
      ├─ OBJ_SET    ─┬─ OBJ_ENCODING_INTSET   (纯整数 + 数量小)
      │              └─ OBJ_ENCODING_HT       (出现非整数)
      └─ OBJ_ZSET   ─┬─ OBJ_ENCODING_LISTPACK (≤ 阈值)
                     └─ OBJ_ENCODING_SKIPLIST (skiplist + dict 双结构)
```

可视化决策树：

```text
                  SET key "hello"
                       │
                       ▼
              ┌──────────────────┐
              │  解析 → redisObject │
              └──────────────────┘
                       │
            ┌──────────┴──────────┐
        是数字?                  否
            │                     │
            ▼                     ▼
     encoding=INT         length ≤ 44 byte?
            │                     │
            ▼                   是 ┴─ 否
   refcount+1 复用       embstr(连续)   raw(独立 SDS)
```

## 四、编码转换阈值

Redis 通过一系列 `redis.conf` 参数控制编码切换，这些参数是面试高频考点。

### String 类型

- 整数且能用 `long` 表示 → `INT`
- 字符串长度 ≤ 44 byte → `EMBSTR`（一次性分配 redisObject + SDS 紧邻内存）
- 字符串长度 > 44 byte → `RAW`

> 44 这个数字来自：`sizeof(redisObject)=16` 加上 `sdshdr8` 头部的 `3 byte` 加上 `\0` 终止符，再加上 Redis 内存分配器 `jemalloc` 的 64 byte 分配粒度。

### Hash 类型

```c
// server.h 默认值
#define OBJ_HASH_MAX_LISTPACK_ENTRIES 128
#define OBJ_HASH_MAX_LISTPACK_VALUE  64
```

- 字段数 ≤ 128 且每个 value ≤ 64 byte → `LISTPACK`
- 任意一项超出 → 升级为 `HT`（dict）

### Set 类型

- 全部是整数且成员数 ≤ `set-max-intset-entries`（默认 512）→ `INTSET`
- 一旦插入非整数 → 升级为 `HT`

### ZSet 类型

```c
#define OBJ_ZSET_MAX_LISTPACK_ENTRIES 128
#define OBJ_ZSET_MAX_LISTPACK_VALUE   64
```

- 元素数 ≤ 128 且每个 member ≤ 64 byte → `LISTPACK`
- 任意一项超出 → 升级为 `SKIPLIST`（同时维护 dict 提供 O(1) 查 score）

### List 类型

Redis 7 之后 List 统一用 `QUICKLIST`，不再像早期那样在 `LINKEDLIST` 和 `ZIPLIST` 之间切换。

## 五、encoding 转换示例

从 `SET k hello` 开始，逐步追加字符观察编码变化：

```text
127.0.0.1:6379> SET k hello
OK
127.0.0.1:6379> OBJECT ENCODING k
"embstr"

127.0.0.1:6379> APPEND k " world! this is a long string for raw encoding"
(integer) 50
127.0.0.1:6379> OBJECT ENCODING k
"raw"
```

Hash 的升级更隐蔽：

```text
127.0.0.1:6379> HSET h f1 v1
(integer) 1
127.0.0.1:6379> OBJECT ENCODING h
"listpack"

127.0.0.1:6379> HSET h f129 v129     # 触发阈值
(integer) 1
127.0.0.1:6379> OBJECT ENCODING h
"hashtable"
```

## 六、OBJECT 命令家族

Redis 提供了多个 `OBJECT` 子命令调试编码：

```text
OBJECT HELP                    # 查看所有子命令
OBJECT ENCODING <key>          # 当前编码（上面示例）
OBJECT REFCOUNT <key>          # 引用计数
OBJECT IDLETIME <key>          # 距离上次访问的秒数
OBJECT FREQ <key>              # LFU 频率（需要 maxmemory-policy=lfu）
OBJECT DEBUG HELP              # 内部调试
```

更底层的是 `DEBUG OBJECT <key>`，会打印整个 `redisObject` 字段：

```text
127.0.0.1:6379> DEBUG OBJECT k
Value at:0x7f8b1c0047c0 refcount:1 encoding:raw serializedlength:50 lru:18234 lru_seconds_idle:0
```

## 七、DEBUG OBJECT 详解

```text
serializedlength     # RDB 序列化后的字节数
lru                  # 24 bit LRU 时间戳（秒级）
lru_seconds_idle     # 当前时间 - lru（空闲秒数）
type                 # 真实类型
encoding             # 真实编码
refcount             # 当前引用数
```

> 生产慎用 `DEBUG OBJECT`，它是 `O(1)` 但会在内部加锁，长期监控请用 `INFO memory`。

## 八、为什么这样设计

1. **位域压缩头部**。type+encoding+lru 共 32 bit，正好 4 byte。`embstr` 编码要求 `redisObject` + SDS 在一次 `zmalloc` 中连续分配，节省一次 malloc 调用和指针解引用。
2. **ptr 字段灵活切换**。所有底层容器都是独立的 `malloc`，升级编码时只换 ptr，不动对象头，避免大块内存拷贝。
3. **24 bit LRU 足够排序**。24 bit 能表示 194 天滚动窗口，配合 `LRU_CLOCK_RESOLUTION`（默认 10 秒采样），精度足够淘汰策略。
4. **refcount 支持共享**。整数 0~9999、空字符串、常见错误回复是共享对象；新版 Redis 用 `OBJECT REFCOUNT` 仍能看到 5 以上的整数被多键引用。

## 九、面试要点

- **`embstr` 为什么是 44 byte 而不是 45 byte**？因为 `jemalloc` 的 64 byte 桶用 64 - 16（对象头）- 3（sds 头）- 1（\0）= 44。
- **`raw` 和 `embstr` 的区别**？embstr 一次分配，连续内存；raw 两次分配，分别拿 redisObject 和 SDS。
- **编码升级是单向的吗**？是的，目前 Redis 只支持从小编码升级到大编码，不会自动降级。
- **Hash 何时升级为 hashtable**？字段数 > 128 或 value 长度 > 64 byte。
- **LRU 24 bit 怎么算的**？`(lruttl % 65535) << 8 | lfu` 之类的位操作组合，LFU 模式下高 16 bit 是衰减计数器，低 8 bit 是频率。

## 十、下一步

到这里你已经掌握了 Redis 对象的"骨架"。接下来看真正存字符串的容器——SDS。

**下一步：** [📝 SDS 简单动态字符串](/02-datastruct/sds)