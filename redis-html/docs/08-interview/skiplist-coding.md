---
title: 跳表手撕
date: 2026-08-15  # date-auto-injected
---

# 🦘 跳表手撕

> Redis ZSet 的底层数据结构（Redis 7 之前）。本篇从原理到完整 Java 实现，附带随机层数生成、并发安全和性能分析。

## 一、跳表是什么

**SkipList** 是一种有序数据结构，通过多层索引实现类似二分查找的效果，平均 O(log N) 插入/删除/查找。

```text
Level 3:   head ──────────────────────► 50 ──────────────────────► NIL
                ↓                         ↓
Level 2:   head ──────► 20 ──────────► 50 ──► 70 ────────────────► NIL
                       ↓               ↓    ↓
Level 1:   head ─► 10 ─► 20 ─► 30 ─► 50 ─► 70 ─► 80 ─► 90 ───────► NIL
```

每一层都是下一层的"快速通道"，层数越高索引越稀疏。查找时从最高层开始，能右跳就右跳，不能就下降一层。

## 二、为什么 Redis 用跳表而不是红黑树

| 维度 | 跳表 | 红黑树 |
|------|------|--------|
| 实现复杂度 | ~200 行 | ~500 行 |
| 范围查询 ZRANGE | O(log N + M) 顺链遍历 | 需中序遍历 |
| 调试难度 | 容易 | 复杂 |
| 内存占用 | 多级索引稍多 | 节点更紧凑 |
| 并发友好 | 局部锁即可 | 复杂 |

antirez（Redis 作者）公开说过跳表更易实现，且 ZSet 频繁使用 ZRANGE 类命令，跳表的顺链优势明显。

## 三、跳表结构定义

```java
import java.util.Random;

/**
 * 跳表完整实现，支持插入 / 删除 / 查找 / 范围查询
 * 层数通过随机晋升生成（Redis 默认晋升概率 0.25）
 */
public class SkipList<K extends Comparable<K>, V> {

    /** 最大层数 */
    private static final int MAX_LEVEL = 32;
    /** 晋升概率，Redis 用 0.25 */
    private static final double P = 0.25;
    /** 随机数生成器 */
    private static final Random RANDOM = new Random();

    /** 跳表节点 */
    private static class Node<K, V> {
        K key;
        V value;
        // forward[i] 指向本节点在第 i 层的下一个节点
        Node<K, V>[] forward;
        // span[i] 表示本节点在第 i 层到 forward[i] 的距离（用于 ZRANK）
        int[] span;

        @SuppressWarnings("unchecked")
        Node(K key, V value, int level) {
            this.key = key;
            this.value = value;
            this.forward = new Node[level];
            this.span = new int[level];
        }
    }

    /** 哨兵头节点，层数最大，方便统一处理 */
    private final Node<K, V> header = new Node<>(null, null, MAX_LEVEL);
    /** 当前跳表最大层数 */
    private int level = 0;
    /** 节点数 */
    private int size = 0;

    public int size() { return size; }

    /**
     * 随机生成节点层数。
     * 类似丢硬币，连续正面就晋升一层。
     */
    private int randomLevel() {
        int lv = 1;
        // < P 晋升，>= P 停止
        while (lv < MAX_LEVEL && RANDOM.nextDouble() < P) {
            lv++;
        }
        return lv;
    }
}
```

## 四、查找操作

从最高层开始，能右跳就右跳，否则下降一层：

```java
/**
 * 查找 key 对应的节点。
 * 时间复杂度平均 O(log N)，最坏 O(N)。
 */
public V get(K key) {
    Node<K, V> cur = header;
    // 从最高层往下找
    for (int i = level - 1; i >= 0; i--) {
        // 在第 i 层一直向右，直到 forward 为 null 或 key 更大
        while (cur.forward[i] != null
               && cur.forward[i].key.compareTo(key) < 0) {
            cur = cur.forward[i];
        }
    }
    // 落到第 0 层，再向右一步就是要找的节点
    cur = cur.forward[0];
    if (cur != null && cur.key.compareTo(key) == 0) {
        return cur.value;
    }
    return null;
}
```

## 五、插入操作

插入 = 查找位置 + 串联指针。难点是更新所有被跨越节点的 `forward[i]`：

```java
/**
 * 插入或更新 key-value。
 * 时间复杂度平均 O(log N)。
 */
public void put(K key, V value) {
    // update[i] 记录在第 i 层，newNode 的前驱节点
    @SuppressWarnings("unchecked")
    Node<K, V>[] update = new Node[MAX_LEVEL];
    // rank[i] 记录 header 到 update[i] 在第 i 层的距离
    int[] rank = new int[MAX_LEVEL];

    Node<K, V> cur = header;
    for (int i = level - 1; i >= 0; i--) {
        rank[i] = (i == level - 1) ? 0 : rank[i + 1];
        while (cur.forward[i] != null
               && cur.forward[i].key.compareTo(key) < 0) {
            rank[i] += cur.span[i];
            cur = cur.forward[i];
        }
        update[i] = cur;
    }

    // 已存在 → 更新值
    Node<K, V> next = cur.forward[0];
    if (next != null && next.key.compareTo(key) == 0) {
        next.value = value;
        return;
    }

    // 新节点：随机层数
    int newLevel = randomLevel();
    // 如果新层数超过当前最大层数，update[] 需要扩展
    if (newLevel > level) {
        for (int i = level; i < newLevel; i++) {
            rank[i] = 0;
            update[i] = header;
            header.span[i] = size;
        }
        level = newLevel;
    }

    Node<K, V> newNode = new Node<>(key, value, newLevel);
    // 串联每一层
    for (int i = 0; i < newLevel; i++) {
        newNode.forward[i] = update[i].forward[i];
        update[i].forward[i] = newNode;

        // 更新 span
        newNode.span[i] = update[i].span[i] - (rank[0] - rank[i]);
        update[i].span[i] = (rank[0] - rank[i]) + 1;
    }
    // 老层（i >= newLevel）的 span 自增
    for (int i = newLevel; i < level; i++) {
        update[i].span[i]++;
    }
    size++;
}
```

## 六、删除操作

```java
/**
 * 删除 key 对应的节点。
 * 时间复杂度平均 O(log N)。
 */
public V remove(K key) {
    @SuppressWarnings("unchecked")
    Node<K, V>[] update = new Node[MAX_LEVEL];
    Node<K, V> cur = header;
    for (int i = level - 1; i >= 0; i--) {
        while (cur.forward[i] != null
               && cur.forward[i].key.compareTo(key) < 0) {
            cur = cur.forward[i];
        }
        update[i] = cur;
    }
    Node<K, V> target = cur.forward[0];
    if (target != null && target.key.compareTo(key) == 0) {
        V oldValue = target.value;
        // 每一层都把 target 从链表中摘掉
        for (int i = 0; i < level; i++) {
            if (update[i].forward[i] != target) break;
            update[i].span[i] -= 1;
            update[i].forward[i] = target.forward[i];
        }
        // 缩高层数（如果最高层空了）
        while (level > 0 && header.forward[level - 1] == null) {
            level--;
        }
        size--;
        return oldValue;
    }
    return null;
}
```

## 七、范围查询

跳表的杀手锏：从位置 x 开始顺链遍历 M 个节点就是 O(log N + M)。

```java
/**
 * 返回 [start, end] 范围内的所有键值对。
 * 实现对应 ZRANGE key start end。
 */
public java.util.List<V> range(K startKey, K endKey) {
    java.util.List<V> result = new java.util.ArrayList<>();
    Node<K, V> cur = header;
    // 先跳到 >= startKey 的位置
    for (int i = level - 1; i >= 0; i--) {
        while (cur.forward[i] != null
               && cur.forward[i].key.compareTo(startKey) < 0) {
            cur = cur.forward[i];
        }
    }
    cur = cur.forward[0];
    // 顺链到 endKey 为止
    while (cur != null && cur.key.compareTo(endKey) <= 0) {
        result.add(cur.value);
        cur = cur.forward[0];
    }
    return result;
}
```

## 八、复杂度与概率分析

### 8.1 时间复杂度

期望 O(log N)，最坏 O(N)。

期望高度的推导：

```text
节点能晋升到第 i 层的概率 = P^i = 0.25^i
第 i 层至少有一个节点的概率阈值 < 1  →  N * 0.25^i ≥ 1 → i ≤ log_{1/P}(N) = log_4(N)
所以高度期望 ≈ log_4(N) = (1/2) * log_2(N)

每层查找是 O(层数跳数)，总共 O(log N)。
```

### 8.2 空间复杂度

期望每个节点的平均指针数 = `1 / (1 - P)` = 1.33。

证明：

```text
期望层数 = 1 + P + P² + P³ + ... = 1 / (1 - P)
P = 0.25 时 = 1.33
```

相比红黑树每个节点 3 个指针（parent / left / right），跳表更省内存。

### 8.3 概率参数 P 的取舍

| P | 高度 | 期望指针数 | 查找速度 | 适用 |
|---|------|------------|----------|------|
| 0.5 | log_2(N) | 2 | 较快 | 写少读多 |
| **0.25** | log_4(N) | 1.33 | **平衡（Redis 默认）** |
| 0.125 | log_8(N) | 1.14 | 较慢 | 写密集 |

## 九、并发安全

Redis 单线程，跳表无需并发保护。Java 中自己实现需要：

```java
// 方案 1：ReadWriteLock
private final ReadWriteLock lock = new ReentrantReadWriteLock();

public V get(K key) {
    lock.readLock().lock();
    try {
        return doGet(key);
    } finally {
        lock.readLock().unlock();
    }
}

public void put(K key, V value) {
    lock.writeLock().lock();
    try {
        doPut(key, value);
    } finally {
        lock.writeLock().unlock();
    }
}

// 方案 2：ConcurrentSkipListMap（JDK 已实现，直接用）
ConcurrentSkipListMap<Integer, String> map = new ConcurrentSkipListMap<>();
map.put(1, "A");
String v = map.get(1);
```

JDK 的 `ConcurrentSkipListMap` 源码与本篇结构高度相似，无锁 CAS 实现，是工业级跳表的参考实现。

## 十、Redis ZSet 双结构设计

Redis ZSet 同时维护两个数据结构：

```text
zset {
    dict   member → score        // O(1) 查 score
    zsl    按 score 排序的跳表    // O(log N) 范围查询
}
```

```bash
ZADD zset 100 alice   # O(log N) 跳表插入 + dict 写入
ZSCORE zset alice     # O(1) dict 查
ZRANGE zset 0 10      # O(log N + M) 跳表范围
```

两者指针共享同一节点，避免重复存储。

## 十一、面试追问清单

| 追问 | 答案 |
|------|------|
| 为什么不用红黑树？ | 范围查询更简单，调试方便，实现代码少 50% |
| 跳表高度多少？ | 期望 log_4(N)，N=1万 时约 7 层 |
| 删除要更新 span 吗？ | 是，且要缩高层数（如果最高层空了） |
| Redis 7 后跳表被淘汰了吗？ | 小 ZSet 走 listpack，超过阈值才升级到 skiplist |
| 跳表 vs B+ 树？ | B+ 树适合磁盘（页式 IO），跳表适合内存 |

## 十二、下一步

跳表搞定，下一篇进入面试超高频的"缓存三大问题"：穿透、击穿、雪崩，并给出完整 Java 代码。

**下一步：** [❄️ 缓存三大问题](/08-interview/avalanche)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [mysql](https://java-px.bot.cd/mysql/):MySQL 主存
- [kafka](https://java-px.bot.cd/kafka/):Kafka 异步队列
- [java](https://java-px.bot.cd/java-web-manual/):Java 客户端（Redisson / Jedis）
