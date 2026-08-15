---
title: SkipList 跳表
---

# 🦘 SkipList 跳表

> **跳表（SkipList）**是一种**多层索引链表**，通过空间换时间实现 **O(log N)** 的查找/插入/删除。Redis 的 **ZSet（有序集合）**的底层实现之一就是跳表。

## 🎯 跳表原理

```
传统链表（O(N)）：
  L1 → L3 → L5 → L8 → L12 → L20
  查找 L20 需要遍历所有节点

跳表（O(log N)）：
  Level 3:  L1 ────────────► L20
  Level 2:  L1 ───► L8 ────► L20
  Level 1:  L1 ─► L5 ─► L8 ─► L12 ─► L20
  Level 0:  L1 → L3 → L5 → L8 → L12 → L15 → L20

  查找 L20：
    Level 3: L1 → 直接跳到 L20（因为 L20 >= L20）
    总共跳了 2 步！
```

**每一层都是下一层的索引**，高层跳得远，低层跳得近，从最高层开始查找，逐层下沉。

## 🏗️ 跳表节点结构

```c
typedef struct zskiplistNode {
    // 存储实际数据（member）
    sds ele;
    // 分数（用于排序）
    double score;
    // 后退指针（从后向前遍历）
    struct zskiplistNode *backward;
    // 层数组（柔性数组）
    struct zskiplistLevel {
        // 前进指针
        struct zskiplistNode *forward;
        // 跨度（节点到 forward 跨越了多少个节点）
        unsigned long span;
    } level[];
} zskiplistNode;

typedef struct zskiplist {
    // 表头节点、表尾节点
    struct zskiplistNode *header, *tail;
    // 跳表中的节点数量（除头节点外）
    unsigned long length;
    // 跳表中的最大层数
    int level;
} zskiplist;
```

## 🎲 随机层数算法

```c
// Redis 的随机层数算法（带权重）
int zslRandomLevel(void) {
    int level = 1;
    // 概率 1/4，p = 0.25
    while ((random() & 0xFFFF) < (0.25 * 0xFFFF)) {
        level += 1;
    }
    // 最大层数 32
    return (level < ZSKIPLIST_MAXLEVEL) ? level : ZSKIPLIST_MAXLEVEL;
}
```

```
p = 0.25 时各层节点的比例：
  Level 1: 100%
  Level 2:  25%
  Level 3:   6.25%
  Level 4:   1.5625%
  ...
  
为什么用 0.25 而不是 0.5？
  - p=0.5 时平均每个节点 2 层 → 内存浪费
  - p=0.25 时平均每个节点 1.33 层 → 内存效率高
  - 同时仍能保证 O(log N) 复杂度
```

## ⏱️ 复杂度分析

| 操作 | 平均复杂度 | 最坏复杂度 |
|------|----------|----------|
| 查找 | O(log N) | O(N) |
| 插入 | O(log N) | O(N) |
| 删除 | O(log N) | O(N) |
| 范围查询 | O(log N + M) | O(N) |

**N 是元素数量，M 是范围大小。**

## 🤔 为什么 Redis 用跳表不用红黑树？

面试官最爱问的问题！4 大原因：

```
✅ 1. 实现简单
   跳表：200 行代码
   红黑树：500+ 行代码，包含旋转等复杂操作

✅ 2. 范围查询方便
   跳表：天然有序，ZRANGEBYSCORE 直接遍历
   红黑树：需要中序遍历

✅ 3. 调试友好
   跳表：结构可视化（多层索引清晰）
   红黑树：旋转操作难追踪

✅ 4. 内存可接受
   跳表：每个节点多 4 个指针（Level 1）
   红黑树：每个节点需要颜色位
   实际差距不大
```

```
❌ 1. 理论最坏复杂度差
   跳表：O(N)
   红黑树：O(log N) 严格保证

但实践中跳表的最坏情况几乎不会触发。
```

## 🔬 Redis ZSet 编码

> Redis ZSet 同时使用 **跳表 + 哈希表**双结构：

```c
typedef struct zset {
    // 哈希表：member → score，O(1) 查 score
    dict *dict;
    // 跳表：按 score 排序，O(log N) 范围查询
    zskiplist *zsl;
} zset;
```

**两个结构各司其职**：
- `dict`：ZSCORE key member → O(1)
- `zsl`：ZRANGE / ZRANGEBYSCORE → O(log N)

写入时同时更新两个结构（O(log N)）。

## 📊 跳表 vs 其他数据结构

| 数据结构 | 查找 | 插入 | 删除 | 范围查询 | 实现难度 |
|---------|------|------|------|---------|---------|
| **跳表** | O(log N) | O(log N) | O(log N) | ✅ O(log N) | 中 |
| **红黑树** | O(log N) | O(log N) | O(log N) | ⚠️ 中序遍历 | 难 |
| **平衡 AVL** | O(log N) | O(log N) | O(log N) | ⚠️ 中序遍历 | 难 |
| **哈希表** | O(1) | O(1) | O(1) | ❌ 不支持 | 简单 |
| **B+ 树** | O(log N) | O(log N) | O(log N) | ✅ O(log N) | 难 |

## 🛠️ 实战：ZSet 命令与跳表

```bash
# 添加元素
ZADD leaderboard 95 "Alice" 87 "Bob" 76 "Charlie"

# 跳表结构（按 score 升序）：
# Level 3:  Charlie → Bob → Alice
# Level 2:  Charlie → Alice
# Level 1:  Charlie → Bob → Alice

# 范围查询（跳表的优势）
ZRANGE leaderboard 0 10              # 前 10 名（O(log N + 10)）
ZRANGEBYSCORE leaderboard 80 100     # 分数 80-100（O(log N + M)）

# 排名
ZRANK leaderboard "Alice"            # O(log N)
ZREVRANK leaderboard "Alice"         # O(log N)
```

## 🎯 总结

**跳表核心要点**：
- ✅ 多层索引链表，O(log N) 查找
- ✅ p = 0.25 随机层数，内存效率高
- ✅ Redis ZSet 底层实现之一
- ✅ 比红黑树实现简单，支持范围查询
- ⚠️ 最坏复杂度 O(N)，但实践中不会触发

**下一步：** [📋 Listpack 紧凑列表](/02-datastruct/listpack) — 紧凑数据结构的演进
