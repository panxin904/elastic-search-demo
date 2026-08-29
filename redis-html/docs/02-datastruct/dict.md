---
title: Dict 哈希表
date: 2026-08-15  # date-auto-injected
---

# Dict 哈希表

Redis 的数据库键空间、Hash 对象以及 ZSet 的成员到分数映射，都依赖 Dict。它采用“数组 + 单向链表”解决哈希冲突，并用两张表完成渐进式 rehash，避免一次搬迁大量键值对导致主线程长时间阻塞。

## 一、核心结构

下面使用经典源码布局说明。`ht[0]` 是当前表，`ht[1]` 只在 rehash 期间使用；`rehashidx == -1` 表示没有迁移任务。

```c
typedef struct dictEntry {
    void *key;
    union { void *val; uint64_t u64; int64_t s64; double d; } v;
    struct dictEntry *next;        // 冲突链表
} dictEntry;

typedef struct dictht {
    dictEntry **table;             // 桶数组
    unsigned long size;            // 桶数，通常为 2 的幂
    unsigned long sizemask;        // size - 1
    unsigned long used;            // 已存节点数
} dictht;

typedef struct dict {
    dictType *type;
    void *privdata;
    dictht ht[2];                  // 当前表 + 迁移目标表
    long rehashidx;                // 下一个待迁移桶
} dict;
```

哈希值通过 `index = hash & sizemask` 定位桶。不同 key 得到同一索引时，新节点接入该桶的链表，而不是覆盖旧节点。

```text
ht[0].table
  [0] ──> NULL
  [1] ──> [key:A] ──> [key:F] ──> NULL   ← 哈希冲突
  [2] ──> [key:C] ──> NULL
  [3] ──> NULL
```

这种拉链法结构简单，平均负载合理时，查找、插入和删除都接近 O(1)；极端冲突下才会退化为 O(N)。

## 二、何时扩容或缩容

负载因子定义为：

```text
load_factor = ht[0].used / ht[0].size
```

| 条件 | 动作 | 目的 |
|---|---|---|
| 负载因子 ≥ 1.0，且允许 resize | 扩容 | 控制平均链长 |
| 负载因子 ≥ 5.0 | 强制扩容 | 即使后台持久化期间限制 resize，也不能继续恶化 |
| 负载因子 ≤ 0.1 | 缩容 | 回收大量空桶 |

扩容后的目标大小通常是不小于 `used * 2` 的最小 2 次幂；缩容则选择能容纳当前元素的最小 2 次幂。扩缩容都不在一个瞬间搬完数据。

## 三、渐进式 rehash 完整流程

1. 为 `ht[1]` 分配目标桶数组，设置 `rehashidx = 0`。
2. 每次执行增删改查时，顺便迁移 `ht[0]` 中从 `rehashidx` 开始的少量桶；定时任务也会在限定时间内推进迁移。
3. 迁移某个桶时，遍历其冲突链表，按 `ht[1].sizemask` 重新计算索引并挂入新桶，然后清空旧桶，`rehashidx++`。
4. 当 `ht[0].used == 0`，释放旧数组，把 `ht[1]` 赋给 `ht[0]`，清空 `ht[1]`，最后令 `rehashidx = -1`。

```c
while (ht[0].table[rehashidx] == NULL)
    rehashidx++;

for (dictEntry *e = ht[0].table[rehashidx]; e != NULL; ) {
    dictEntry *next = e->next;
    unsigned long i = hash(e->key) & ht[1].sizemask;
    e->next = ht[1].table[i];
    ht[1].table[i] = e;
    e = next;
}
ht[0].table[rehashidx++] = NULL;
```

```text
迁移前                 迁移中                  完成
ht[0]: [A][B][C][D]    ht[0]: [ ][ ][C][D]     ht[0]: [A'..D']
ht[1]: 空              ht[1]: [A'][B'][ ][ ]   ht[1]: 空
rehashidx = 0           rehashidx = 2            rehashidx = -1
```

关键是“分摊”：一次命令只承担很小的迁移成本，整体迁移仍是 O(N)，但单次停顿被控制在较低水平。

## 四、rehash 期间如何操作

| 操作 | 处理规则 |
|---|---|
| 查询 | 先查 `ht[0]`，未命中再查 `ht[1]` |
| 插入 | 只写入 `ht[1]`，避免新节点再次搬迁 |
| 删除 | 两张表都检查，找到后摘除 |
| 更新 | 在两张表中定位已有 key，再原位更新 value |

```c
// 概念化查询逻辑
for (int t = 0; t <= (isRehashing(d) ? 1 : 0); t++) {
    dictEntry *e = findInTable(&d->ht[t], key);
    if (e != NULL) return e;
}
return NULL;
```

因此迁移期间两张表共同构成一个逻辑 Dict，业务不会看到“半张表”。理解 `ht[2]`、`rehashidx` 与双表操作规则，就抓住了 Redis Dict 的核心。

**下一步：** [🦘 SkipList 跳表](/02-datastruct/skiplist)
