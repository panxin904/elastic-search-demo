---
title: LRU 算法手撕
---

# 📚 LRU 算法手撕

> 字节跳动、阿里、美团高频算法题。"设计一个 LRU 缓存"几乎是后端面试标配。本篇从原理到三版实现（双向链表手撕 / LinkedHashMap / Guava）全部讲透。

## 一、LRU 是什么

**LRU（Least Recently Used）** 缓存淘汰策略：容量满时淘汰最久未使用的元素。

```text
操作        时间复杂度
get(key)    O(1)
put(key,v)  O(1)
淘汰最久     O(1)
```

## 二、数据结构选择

单纯用数组或 HashMap 都无法满足 O(1)。LRU 需要两个能力：

| 能力 | 数据结构 |
|------|----------|
| 快速定位 key | HashMap |
| 快速找到最久未用 + 维护访问顺序 | **双向链表** |

```text
              ┌────────────────────────────────────┐
              │                                    │
              ▼                                    │
        head ⇄ A ⇄ B ⇄ C ⇄ D ⇄ tail                │
              │              │                    │
              └──────────────┴─────► 最近访问的移到 head 附近
                                          最久未用靠近 tail
```

**组合策略**：

- HashMap 存 `key → 链表节点`，O(1) 定位。
- 双向链表维护访问顺序：head 是最近访问，tail 是最久未访问。
- 访问（get 或 put）时把节点移到 head，淘汰时直接删 tail。

## 三、v1 双向链表 + HashMap 手撕（推荐面试版）

LeetCode 146 原题，完整可运行代码：

```java
public class LRUCache<K, V> {

    /** 双向链表节点 */
    private static class Node<K, V> {
        K key;
        V value;
        Node<K, V> prev;
        Node<K, V> next;

        Node() {}
        Node(K key, V value) {
            this.key = key;
            this.value = value;
        }
    }

    private final int capacity;
    private final Map<K, Node<K, V>> map;
    /** 哨兵节点，避免 head/tail 空判断 */
    private final Node<K, V> head = new Node<>();
    private final Node<K, V> tail = new Node<>();

    public LRUCache(int capacity) {
        this.capacity = capacity;
        this.map = new HashMap<>(capacity);
        head.next = tail;
        tail.prev = head;
    }

    public V get(K key) {
        Node<K, V> node = map.get(key);
        if (node == null) return null;
        moveToHead(node);    // 标记为最近访问
        return node.value;
    }

    public void put(K key, V value) {
        Node<K, V> node = map.get(key);
        if (node == null) {
            Node<K, V> newNode = new Node<>(key, value);
            map.put(key, newNode);
            addToHead(newNode);
            if (map.size() > capacity) {
                Node<K, V> removed = removeTail();
                map.remove(removed.key);   // ⚠️ 必须从 map 也删
            }
        } else {
            node.value = value;            // 更新值
            moveToHead(node);
        }
    }

    /* ------------------- 双向链表操作 ------------------- */

    private void addToHead(Node<K, V> node) {
        node.prev = head;
        node.next = head.next;
        head.next.prev = node;
        head.next = node;
    }

    private void removeNode(Node<K, V> node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
    }

    private void moveToHead(Node<K, V> node) {
        removeNode(node);
        addToHead(node);
    }

    private Node<K, V> removeTail() {
        Node<K, V> node = tail.prev;
        removeNode(node);
        return node;
    }

    /* ------------------- 调试 ------------------- */

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder("[");
        Node<K, V> cur = head.next;
        while (cur != tail) {
            sb.append(cur.key).append("=").append(cur.value);
            cur = cur.next;
            if (cur != tail) sb.append(", ");
        }
        return sb.append("]").toString();
    }

    /* ------------------- 测试 ------------------- */

    public static void main(String[] args) {
        LRUCache<Integer, String> cache = new LRUCache<>(2);
        cache.put(1, "A");   // {1=A}
        cache.put(2, "B");   // {1=A, 2=B}
        System.out.println(cache.get(1));  // A → {2=B, 1=A}
        cache.put(3, "C");   // 容量满 → 淘汰 2 → {1=A, 3=C}
        System.out.println(cache.get(2));  // null
        System.out.println(cache);         // [1=A, 3=C]
    }
}
```

**复杂度分析**

| 操作 | 时间 | 空间 |
|------|------|------|
| get | O(1) — HashMap + 链表移动 | O(1) |
| put | O(1) — 同上 + 可能淘汰 | O(1) |
| 总空间 | O(capacity) | — |

## 四、面试要点拆解

### 4.1 为什么用双向链表而不是单向？

```text
单链表删除节点需要 prev，时间 O(N)
双链表已知 node → 直接 prev.next = node.next.next，O(1)
```

LRU 的"移到头部"和"淘汰尾部"都需要修改前驱指针，单链表做不到 O(1)。

### 4.2 哨兵节点的好处

```java
private final Node head = new Node();   // 哨兵
private final Node tail = new Node();
head.next = tail;
tail.prev = head;
```

哨兵让链表永远不会空，省去 `if (head == null)` 这种边界判断。`removeTail()` 直接拿 `tail.prev` 即可。

### 4.3 put 时为什么必须从 map 删除淘汰节点？

```java
if (map.size() > capacity) {
    Node removed = removeTail();
    map.remove(removed.key);   // 关键！
}
```

不删会导致：

1. map 越来越大，超过 capacity 后不再触发淘汰。
2. 后续 get 一个已淘汰的 key 会从 map 返回节点（指针已成野指针），导致 NPE 或脏数据。

### 4.4 为什么 HashMap 要预分配 capacity？

```java
this.map = new HashMap<>(capacity);
```

避免 put 过程中频繁 resize（JDK 8 HashMap 默认负载因子 0.75）。

## 五、v2 LinkedHashMap 五行实现

JDK `LinkedHashMap` 已经内置 LRU 能力（`accessOrder=true`），面试不要求手撕时用这个：

```java
public class SimpleLRU<K, V> extends LinkedHashMap<K, V> {
    private final int capacity;

    public SimpleLRU(int capacity) {
        // accessOrder=true: get 也会改变顺序
        super(capacity, 0.75f, true);
        this.capacity = capacity;
    }

    @Override
    protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
        return size() > capacity;
    }

    public static void main(String[] args) {
        SimpleLRU<Integer, String> cache = new SimpleLRU<>(2);
        cache.put(1, "A");
        cache.put(2, "B");
        cache.get(1);            // 访问 1
        cache.put(3, "C");        // 触发淘汰 → 淘汰 2
        System.out.println(cache); // {1=A, 3=C}
    }
}
```

**核心三行**

1. `super(capacity, 0.75f, true)` — `accessOrder=true` 让 get 改变顺序。
2. 重写 `removeEldestEntry` — 返回 `true` 时插入自动删最旧。
3. 一行 `return size() > capacity;` — 容量判定。

## 六、v3 生产级：Guava Cache

```java
Cache<String, String> cache = CacheBuilder.newBuilder()
    .maximumSize(10_000)                            // 容量上限
    .expireAfterWrite(Duration.ofMinutes(10))       // 写后 10 分钟过期
    .expireAfterAccess(Duration.ofMinutes(5))       // 访问后 5 分钟过期
    .recordStats()                                  // 开启统计
    .build();

cache.put("key", "value");
String v = cache.getIfPresent("key");
CacheStats stats = cache.stats();   // hitRate / missCount
```

**对比 LinkedHashMap**

| 维度 | LinkedHashMap | Guava Cache |
|------|---------------|-------------|
| 容量淘汰 | ✓ | ✓ |
| TTL 过期 | ✗ | ✓ |
| 加载策略 | ✗ | LoadingCache 回源 |
| 线程安全 | ✗（Collections.synchronizedMap） | ✓ 内部实现 |
| 统计 | ✗ | ✓ hitRate / eviction |

## 七、Redis 中的 LRU 实现

Redis 用**近似 LRU**（不维护完整链表）：

```c
// redisObject 24 bit lru 字段记录上次访问时间
typedef struct redisObject {
    unsigned lru : 24;   // 秒级时间戳（LRU_CLOCK_RESOLUTION 精度）
    ...
};

// 每次访问 key 时更新 lru 字段
// 淘汰时随机采样 N 个 key（默认 5），淘汰 lru 最小的
```

**为什么是近似？**

维护完整链表每次访问都要调整指针，开销巨大。Redis 采样 + LRU 字段方案在牺牲少量精度的前提下让 `O(1)` get 保持 O(1)，整体命中率与精确 LRU 差距 < 5%。

**采样大小可调**

```conf
maxmemory-samples 10   # 默认 5，增大到 10 让 LRU 更接近真实
```

## 八、面试追问清单

| 追问 | 答案 |
|------|------|
| LRU 和 LFU 区别？ | LRU 看最近访问时间，LFU 看访问频率。Redis 4+ 支持 LFU（24 bit 中 16 bit 衰减 + 8 bit 计数） |
| 为什么 Redis 用近似 LRU？ | 全量 LRU 维护成本高，近似采样足够准确 |
| LRU 有什么问题？ | 突发流量会让热点 key 被一次性扫描驱逐，LFU 更稳定 |
| 双向链表能否用 LinkedList 自己实现？ | 可以，但 Node 需要 prev 引用，需要自己写 |
| 线程安全怎么做？ | Collections.synchronizedMap / ReadWriteLock / Caffeine |

## 九、下一步

LRU 是 Redis 淘汰策略的简化版思想。下一篇进入 Redis ZSet 的核心数据结构：**跳表（SkipList）**。

**下一步：** [🦘 跳表手撕](/08-interview/skiplist-coding)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [mysql](https://java-px.bot.cd/mysql/):MySQL 主存
- [kafka](https://java-px.bot.cd/kafka/):Kafka 异步队列
- [java](https://java-px.bot.cd/java-web-manual/):Java 客户端（Redisson / Jedis）
