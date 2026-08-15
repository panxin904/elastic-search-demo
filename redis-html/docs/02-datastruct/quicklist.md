---
title: QuickList
---

# 🔗 QuickList

> QuickList 是 Redis 3.2 引入的 List 底层结构，**双向链表 + listpack** 的混合体。它把"无限扩展的 List"拆成若干定容的 listpack 节点，既保留 listpack 的内存紧凑，又获得了链表式的 O(1) 头尾操作和按需扩容能力。Redis 7 之后所有 List 编码统一为 QuickList。

<ClientOnly>
  <DataStructureViz />
</ClientOnly>

## 一、为什么需要 QuickList

List 类型的历史编码经历了三次迭代，每次都在权衡"内存紧凑"与"操作灵活"：

```text
linkedlist (Redis ≤ 2.x)
  ├─ 节点: listNode { void *value; listNode *prev; *next; }
  ├─ 每个 entry 一次 malloc，双向指针各 8 byte
  └─ 大 List 内存浪费严重

ziplist + linkedlist (Redis 3.0)
  ├─ 整体是 ziplist，超阈值才升级为 linkedlist
  ├─ 阈值: ziplist 整体 > 64 byte 或 entry 数 > 512
  └─ 阈值切换存在性能毛刺

quicklist (Redis 3.2+, Redis 7 默认)
  ├─ 节点是 listpack，节点之间双向链表
  ├─ 粒度更细：可配置每个 listpack 上限
  └─ 既紧凑又可伸缩
```

QuickList 的核心洞察：**List 操作绝大多数集中在头尾（LPUSH/RPUSH/LPOP/RPOP），中间访问极少**。所以应该让中间节点尽可能压缩（listpack），而把"导航"能力交给双向链表。

## 二、QuickList 节点结构

源码 `src/quicklist.h`：

```c
typedef struct quicklistNode {
    struct quicklistNode *prev;    // 前驱节点
    struct quicklistNode *next;    // 后继节点
    unsigned char *entry;         // 指向 listpack 数据（zip 格式）
    size_t sz;                     // 当前 listpack 的字节数
    unsigned int count : 16;       // listpack 内的 entry 数
    unsigned int encoding : 2;     // 1=raw, 2=lzf 压缩
    unsigned int container : 2;    // 1=listpack（Redis 7 唯一值）
    unsigned int recompress : 1;   // 临时解压标记（用于 BLPOP 等）
    unsigned int attempted_compress : 1;
    unsigned int extra : 10;
} quicklistNode;

typedef struct quicklist {
    quicklistNode *head;
    quicklistNode *tail;
    long long count;      // 所有节点 entry 总数
    long long len;        // 节点数
    int fill;             // 每个 listpack 节点的目标大小（-2..-5 或正数 byte）
    int compress;         // 两端不压缩的节点数
} quicklist;
```

整体布局：

```text
   head                                                              tail
    │                                                                 │
    ▼                                                                 ▼
  ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐
  │ node │◄──►│ node │◄──►│ node │◄──►│ node │◄──►│ node │
  │ LZUF │    │ LP   │    │ LP   │    │ LP   │    │ LRUF │
  └──────┘    └──────┘    └──────┘    └──────┘    └──────┘
  ↑              ↑                            ↑              ↑
 压缩            正常                         正常           压缩
   │                                                             │
  └─ prevrawlen / encoding / backlen ──────────────── 反向遍历 ──┘
```

`fill` 字段意义（来自 `redis.conf`）：

| fill 值 | 实际容量 | 含义 |
|---------|----------|------|
| `-5` | 64 KB | 最大 |
| `-4` | 32 KB | 较大 |
| `-3` | 16 KB | 默认（旧版本） |
| `-2` | **8 KB** | **Redis 7 默认** |
| `-1` | 4 KB | 较小 |
| `>0` | N byte | 自定义字节数 |

`fill` 越小，listpack 节点越短，整条链表节点越多，单点 `memmove` 代价越低，但双向指针开销相对上升。

## 三、两个核心配置项

```bash
# redis.conf
list-max-listpack-size -2        # 每个 listpack 节点上限 8 KB
list-compress-depth  0           # 两端保留多少节点不压缩
```

### 1. `list-max-listpack-size`

控制每个 listpack 节点的容量。值为负数时按 KB 取档，为正数时按 byte 设置。当 `LPUSH` 触发某个 listpack 超过阈值时，QuickList 会把它分裂成两个节点；反向删除导致节点空闲时，又会合并相邻空节点。

### 2. `list-compress-depth`

控制链表两端不参与 LZF 压缩的节点数：

```text
list-compress-depth = 0    → 全部压缩（最省内存，操作稍慢）
list-compress-depth = 1    → 仅 head/tail 不压缩（Redis 默认）
list-compress-depth = 2    → 两端各 2 个节点不压缩
list-compress-depth = N    → 两端各 N 个节点保持原始 listpack
```

设计动机是 **80/20 法则**：List 操作 90% 集中在头尾，所以头尾节点保持原始 listpack 形态以避免解压开销；中间节点很少访问，压缩掉可节省大量内存。

```text
   compress=0:
   [c][c][c][c][c][c][c][c][c]   ← 所有节点都是 LZF 压缩

   compress=2:
   [r][r][c][c][c][c][c][c][r][r]
    ↑            ↑         ↑
   不压缩        压缩      不压缩
   (头)                    (尾)
```

## 四、QuickList 操作

```bash
127.0.0.1:6379> RPUSH mylist a b c d e f g
(integer) 7
127.0.0.1:6379> OBJECT ENCODING mylist
"quicklist"

127.0.0.1:6379> LLEN mylist
(integer) 7

# 调试：观察节点分布
127.0.0.1:6379> DEBUG OBJECT mylist
Value at:0x7f9c2c0011a0 refcount:1 encoding:quicklist serializedlength:14 lru:18945 ...

127.0.0.1:6379> QUICKLIST-VALIDATE-ENCODING mylist   # 仅 debug 命令
OK
```

`LPUSH` / `RPUSH` 复杂度分析：

```text
LPUSH mylist x
    │
    ▼
┌──────────────────────────────┐
│ head 节点剩余空间够容纳 x?  │
└──────────────────────────────┘
   │ 是                │ 否
   ▼                   ▼
 listpackInsert    新建节点 (malloc)
 O(N) 线性插头     O(1)
                   插入新 head.listpack[0]
```

`LRANGE` 跨节点时需要先遍历双向链表定位起点节点，再在节点内 listpack 顺序扫描；线性操作仍是 O(N)，但常数项更友好。

## 五、QuickList 的内存收益

对比纯 linkedlist 的实测：

| 元素规模 | linkedlist | quicklist (默认) | 节省 |
|----------|-----------|------------------|------|
| 1 万条 16 byte | ~880 KB | ~190 KB | ~78% |
| 10 万条 16 byte | ~8.8 MB | ~1.9 MB | ~78% |
| 100 万条 16 byte | ~88 MB | ~19 MB | ~78% |

收益来自两个层面：**节点内 listpack 紧凑排列**（无 listNode 指针开销）、**中间节点 LZF 压缩**。

## 六、QuickList 与 ziplist 的兼容性

Redis 7 之前版本里，小 List 仍可能编码为纯 ziplist。Redis 7 之后：

```text
LIST 类型编码：

   Redis ≤ 6.x：
       ziplist (entry ≤ 64 byte 且 总长 ≤ 8 KB)
       ↓ 超阈值
       linkedlist (大 List)

   Redis 7+：
       quicklist（统一）— 即使很小的 List 也是 1 个节点的 quicklist
```

判断方法：

```bash
127.0.0.1:6379> OBJECT ENCODING small_list
"quicklist"                  # Redis 7+

# 旧版本可能返回:
# "listpack" / "linkedlist" / "ziplist"
```

## 七、面试要点

- **为什么不用 skiplist 替代**？List 是线性有序容器，没有"按 score 区间查"的需求；skiplist 的多层指针在头部操作上反而是负担。
- **fill=-2 怎么算出来的**？经验值，8 KB 落在 L1 cache 友好区间（典型 32~64 KB）的一半附近，能让节点大概率常驻 L1。
- **compress-depth=0 会影响 LRANGE 性能吗**？会。每次访问中间节点都要 LZF 解压，因此默认 1 是折中。
- **QuickList 是否支持 BLPOP**？支持。BLPOP 命中节点时会临时把该节点解压（`recompress=1`），访问完再标脏；下次后台任务把它重新压缩。

## 八、下一步

QuickList 让 List 既紧凑又可扩展，但 List 终究只是一个先进先出的"消息队列"。Redis 4.0 引入的 Stream 才是真正的消息流，带消费者组和消费确认。

**下一步：** [🌊 Stream](/02-datastruct/stream)