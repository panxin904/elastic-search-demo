---
title: 一致性 Hash
---

# 🎯 一致性 Hash

> 分布式系统经典算法。本篇从**哈希取模的问题**出发，详解一致性 Hash 原理、虚拟节点、代码实现，并对比 Redis Cluster 为何不用一致性 Hash。

## 一、传统哈希取模的问题

### 1.1 算法

最朴素的分片方式：

```text
node = hash(key) % N
```

其中 N 是节点数。Redis Cluster 没用这个，Memcached 客户端分片用过。

### 1.2 扩容灾难

```text
N=3 时:
  node = hash(key) % 3
  key1 → 0, key2 → 1, key3 → 2

N=4 扩容后:
  node = hash(key) % 4
  key1 → 1, key2 → 2, key3 → 3
```

**结论**：当 N 从 3 变为 4，**几乎 75% 的 key 路由变了**。意味着 75% 的缓存失效，全部回源 DB，缓存雪崩。

```text
数据迁移比例: 1 - N / (N + 1)  （扩容 1 节点）
N=3→4: 75% 数据失效
N=10→11: 91% 数据失效
```

## 二、一致性 Hash 原理

### 2.1 核心思想

把哈希空间想象成一个**环**（Hash Ring），值域是 `[0, 2^32)`：

```text
                    0
                    │
            Node B  │
        7 ─────────┼───────── 1  Node C
        │          │          │
        │    Key1  │          │
        6          │          2
        │          │          │
        │          │          │
        5 ─────────┼───────── 3
            Node A  │
                    │
                    4
```

### 2.2 算法步骤

1. 对每个**节点**（IP + 端口或名字）做 hash，映射到环上。
2. 对每个**数据 key** 做 hash，映射到环上。
3. 顺时针找最近的节点，就是该 key 的归属节点。

```text
key1 顺时针最近 → Node C
key2 顺时针最近 → Node A
key3 顺时针最近 → Node B
```

### 2.3 扩容效果

新增一个 Node D 落在 key1 和 Node C 之间：

```text
扩容前:  key1 → Node C
扩容后:  key1 → Node D  ← 只影响这个区间
         key2 → Node A   ← 不变
         key3 → Node B   ← 不变
```

**受影响的数据比例** ≈ 1/N。当 N=100 时，扩容只影响 1% 的 key。

## 三、数据倾斜问题

### 3.1 现象

如果节点 hash 后分布不均：

```text
Node A: 0°
Node B: 90°
Node C: 180°
Node D: 270°

key 的分布:
  0~90°:   A  25%
  90~180°: B  25%
  180~270°: C  25%
  270~360°: D  25%  ← 看起来均匀
```

但实际 hash 不可能完美均匀，常出现某个节点映射到 1° ~ 359°，覆盖 99% 的 key，其他节点几乎闲置。

### 3.2 解决方案：虚拟节点

**核心思想**：一个真实节点映射到环上 N 个虚拟节点（VNode），打破"节点数量少"的稀疏性。

```text
Node A → VNode A1, A2, A3, ... A200
Node B → VNode B1, B2, B3, ... B200
Node C → VNode C1, C2, C3, ... C200
Node D → VNode D1, D2, D3, ... D200

环上 800 个虚拟节点，每个真实节点负责 200 个区间
数据倾斜度 < 1/N（标准差）
```

## 四、Java 完整实现

```java
import java.util.Collection;
import java.util.SortedMap;
import java.util.TreeMap;
import java.util.List;
import java.util.ArrayList;
import java.util.zip.CRC32;

/**
 * 一致性 Hash 实现，支持虚拟节点
 */
public class ConsistentHash<T> {

    /** 每个真实节点对应的虚拟节点数量 */
    private static final int VIRTUAL_NODES = 200;

    /** 虚拟节点 hash → 真实节点 */
    private final SortedMap<Long, T> ring = new TreeMap<>();

    public ConsistentHash(Collection<T> nodes) {
        for (T node : nodes) {
            add(node);
        }
    }

    /**
     * 添加节点：插入 VIRTUAL_NODES 个虚拟节点到环
     */
    public void add(T node) {
        for (int i = 0; i < VIRTUAL_NODES; i++) {
            long hash = hash(node.toString() + "#" + i);
            ring.put(hash, node);
        }
    }

    /**
     * 删除节点：移除所有该节点的虚拟节点
     */
    public void remove(T node) {
        for (int i = 0; i < VIRTUAL_NODES; i++) {
            long hash = hash(node.toString() + "#" + i);
            ring.remove(hash);
        }
    }

    /**
     * 查找 key 对应的归属节点
     */
    public T get(String key) {
        if (ring.isEmpty()) return null;
        long hash = hash(key);
        // tailMap: 返回 >= hash 的所有节点
        SortedMap<Long, T> tail = ring.tailMap(hash);
        // 顺时针第一个
        Long firstHash = tail.isEmpty() ? ring.firstKey() : tail.firstKey();
        return ring.get(firstHash);
    }

    /**
     * CRC32 哈希（生产可用 MurmurHash3 性能更好）
     */
    private long hash(String key) {
        CRC32 crc = new CRC32();
        crc.update(key.getBytes());
        return crc.getValue();
    }

    /* ------------------- 测试 ------------------- */

    public static void main(String[] args) {
        // 初始 3 个节点
        List<String> nodes = List.of("Node-A", "Node-B", "Node-C");
        ConsistentHash<String> ch = new ConsistentHash<>(nodes);

        // 模拟 10000 个 key 的分布
        int[] count = new int[3];
        for (int i = 0; i < 10000; i++) {
            String node = ch.get("key" + i);
            count[nodes.indexOf(node)]++;
        }
        System.out.println("3 节点分布: " + java.util.Arrays.toString(count));
        // 近似 [3333, 3333, 3334]

        // 增加一个节点
        ch.add("Node-D");
        count = new int[4];
        for (int i = 0; i < 10000; i++) {
            String node = ch.get("key" + i);
            count[java.util.Arrays.asList("Node-A", "Node-B", "Node-C", "Node-D").indexOf(node)]++;
        }
        System.out.println("4 节点分布: " + java.util.Arrays.toString(count));
        // 近似 [2500, 2500, 2500, 2500]
    }
}
```

## 五、MurmurHash3 优化

CRC32 在大量节点时分布不够均匀，生产环境推荐 MurmurHash3：

```java
public class MurmurHash3 {

    private static final long C1 = 0x87c37b91114253d5L;
    private static final long C2 = 0x4cf5ad432745937fL;

    public static long hash64(byte[] data, long seed) {
        long h1 = seed;
        long c1 = C1;
        long c2 = C2;

        int len = data.length;
        int nblocks = len / 16;

        for (int i = 0; i < nblocks; i++) {
            int idx = i * 16;
            long k1 = getLittleEndianLong(data, idx);
            k1 *= c1;
            k1 = Long.rotateLeft(k1, 31);
            k1 *= c2;
            h1 ^= k1;
            h1 = Long.rotateLeft(h1, 27);
            h1 = h1 * 5 + 0x52dce729;
        }

        long k1 = 0;
        int tailStart = nblocks * 16;
        switch (len & 15) {
            case 15: k1 ^= ((long) data[tailStart + 14] & 0xff) << 48;
            case 14: k1 ^= ((long) data[tailStart + 13] & 0xff) << 40;
            case 13: k1 ^= ((long) data[tailStart + 12] & 0xff) << 32;
            case 12: k1 ^= ((long) data[tailStart + 11] & 0xff) << 24;
            case 11: k1 ^= ((long) data[tailStart + 10] & 0xff) << 16;
            case 10: k1 ^= ((long) data[tailStart + 9]  & 0xff) << 8;
            case  9: k1 ^= ((long) data[tailStart + 8]  & 0xff);
                     k1 *= c1; k1 = Long.rotateLeft(k1, 31); k1 *= c2; h1 ^= k1;
            case  8: k1 ^= ((long) data[tailStart + 7] & 0xff) << 56;
            case  7: k1 ^= ((long) data[tailStart + 6] & 0xff) << 48;
            case  6: k1 ^= ((long) data[tailStart + 5] & 0xff) << 40;
            case  5: k1 ^= ((long) data[tailStart + 4] & 0xff) << 32;
            case  4: k1 ^= ((long) data[tailStart + 3] & 0xff) << 24;
            case  3: k1 ^= ((long) data[tailStart + 2] & 0xff) << 16;
            case  2: k1 ^= ((long) data[tailStart + 1] & 0xff) << 8;
            case  1: k1 ^= ((long) data[tailStart]     & 0xff);
                     k1 *= c1; k1 = Long.rotateLeft(k1, 31); k1 *= c2; h1 ^= k1;
        }

        h1 ^= len;
        h1 ^= h1 >>> 33;
        h1 *= 0xff51afd7ed558ccdL;
        h1 ^= h1 >>> 33;
        h1 *= 0xc4ceb9fe1a85ec53L;
        h1 ^= h1 >>> 33;
        return h1;
    }

    private static long getLittleEndianLong(byte[] data, int i) {
        return ((long) data[i]     & 0xff)        |
               ((long) data[i + 1] & 0xff) <<  8  |
               ((long) data[i + 2] & 0xff) << 16  |
               ((long) data[i + 3] & 0xff) << 24  |
               ((long) data[i + 4] & 0xff) << 32  |
               ((long) data[i + 5] & 0xff) << 40  |
               ((long) data[i + 6] & 0xff) << 48  |
               ((long) data[i + 7] & 0xff) << 56;
    }
}
```

## 六、为什么 Redis Cluster 不用一致性 Hash

这是个反直觉但很经典的面试题。

| 维度 | 一致性 Hash | Redis Cluster 哈希槽 |
|------|-------------|----------------------|
| 粒度 | 每个 key 单独映射 | 先映射到 16384 槽，槽再映射到节点 |
| 扩容迁移 | 单个 key 粒度（细） | 槽粒度（粗但可控） |
| 心跳包大小 | 每个节点要知道全环 | 每个节点 2KB bitmap 即可（16384 bit） |
| 路由计算 | 客户端计算或代理 | 客户端缓存 slot 表 + MOVED 重定向 |
| 运维复杂度 | 节点多时环维护难 | 槽位迁移可控 |

**Redis Cluster 选择 16384 槽的核心原因**：

```text
心跳包大小 = 16384 bit = 2 KB
如果用 65536 槽 → 8 KB，过大
如果用 256 槽 → 32 byte，但粒度太粗，节点少时分布不均
16384 是 trade-off
```

**另一个重要原因**：哈希槽让**数据迁移可控**。

一致性 Hash 扩容时，节点上的数据迁移比例 ≈ 1/N 且**随机散布**；哈希槽扩容时，按槽整块迁移（默认 16384/N 个槽），**迁移边界清晰**且**运维友好**。

```bash
# Redis Cluster 迁移：把 1000 个槽从 A 迁到 B
redis-cli --cluster reshard --cluster-from A --cluster-to B --cluster-slots 1000
```

## 七、一致性 Hash 在其他场景的应用

| 场景 | 用途 |
|------|------|
| **Memcached** | 客户端用一致性 Hash 分片 |
| **Cassandra** | 数据分区使用 MurmurHash3 + VNode |
| **DynamoDB** | 一致性 Hash + VNode 解决数据倾斜 |
| **Nginx / LVS** | upstream 一致性 Hash 负载均衡 |
| **Dubbo** | 路由规则中支持一致性 Hash |

## 八、面试追问清单

| 追问 | 答案 |
|------|------|
| 虚拟节点数量怎么定？ | 一般 100~500，节点越少虚拟节点越多，平衡分布 |
| 删除节点会丢数据吗？ | 是的，所以生产中通常先复制再删除（迁移语义） |
| 一致性 Hash + 副本怎么做？ | 每个真实节点创建 N 个副本 VNode，相同 VNode 映射到不同物理节点 |
| Redis Cluster 为何不用？ | 槽位粒度更适合运维，且 2KB 心跳包合理 |
| 客户端分片 vs 代理分片？ | 客户端分片（Twemproxy）/ 服务端代理（Codis） / Cluster 原生 |

## 九、下一步

一致性 Hash 解决的是**数据分布**问题。下一篇进入分布式系统更底层的**一致性问题**：Paxos / Raft 共识算法。

**下一步：** [📜 Paxos/Raft 概述](/08-interview/consensus)