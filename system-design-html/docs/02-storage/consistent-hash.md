---
title: 一致性哈希
---

# 一致性哈希（Consistent Hashing）

> 由 David Karger 于 1997 年在 MIT 提出，最初用于 Akamai CDN 和分布式缓存。是分布式存储系统的"地基"。

## 1. 为什么需要一致性哈希？

### 1.1 朴素哈希的问题

```
N 个节点，对 key 做 hash(key) % N 决定落在哪个节点：

  N = 3: hash("user_123") % 3 = 1 → Node 1
  N = 4: hash("user_123") % 4 = 2 → Node 2  ← key 搬家了！

问题：
  - 加一个节点：几乎所有 key 都重新映射
  - 减一个节点：同样几乎所有 key 都搬家
  - 数据迁移量 = O(K)，K = 总 key 数
```

### 1.2 一致性哈希的解决思路

> 让"节点的增减**只影响**相邻节点上的 key"，迁移量降到 O(K/N)。

## 2. 原理

### 2.1 哈希环

```
把 0 ~ 2^32 想象成一个环：

        0
       / \
   2^32  ...
      |
   Node A 在 hash 值 100
   Node B 在 hash 值 8000
   Node C 在 hash 值 20000
```

### 2.2 Key 的落点

```
key "user_123" hash 值 5000 → 沿环顺时针找最近的节点 → Node B（8000）

📌 每个 key 都映射到"环上顺时针遇到的第一个节点"
📌 新增节点只影响"环上逆时针到新增节点之间的 key"
```

### 2.3 节点变化的影响

```
原始：Node A (100), Node B (8000), Node C (20000)
key K (5000) → Node B

新增 Node D (15000):
  环上 [8000, 15000) 之间的 key 从 Node B 改投 Node D
  key K (5000) 仍在 [100, 8000) → 还是 Node B
  → 只有 ~1/3 的 key 重新映射 ✓
```

## 3. 虚拟节点（Virtual Nodes）

### 3.1 节点少时的倾斜问题

```
只有 3 个节点：
  Node A 在环上分布稀疏
  Node B 在环上分布稀疏
  Node C 在环上分布稀疏

→ 不同节点"管辖区"大小差异大
→ 负载不均衡
```

### 3.2 解决方案：每个物理节点映射多个虚拟节点

```
Node A → 200 个虚拟节点（hash("A#1") ~ hash("A#200")）
Node B → 200 个虚拟节点
Node C → 200 个虚拟节点

→ 600 个虚拟节点在环上分布更均匀
→ 真实负载 = O(虚拟节点数 / 总虚拟节点数)
→ 增删节点时影响更分散
```

### 3.3 工业实践

| 系统 | 虚拟节点数 |
|---|---|
| DynamoDB | 256 |
| Cassandra | 默认 256，可配置 |
| Redis Cluster | 16384（slots，哈希环的另一实现） |
| Akamai CDN | 原始论文 200-1000 |

## 4. 代码实现（Java）

```java
public class ConsistentHash<T> {
  private final SortedMap<Long, T> ring = new TreeMap<>();
  private final int virtualNodeCount;

  public ConsistentHash(int virtualNodeCount) {
    this.virtualNodeCount = virtualNodeCount;
  }

  // 添加物理节点
  public void add(T node) {
    for (int i = 0; i < virtualNodeCount; i++) {
      long hash = hash(node.toString() + "#" + i);
      ring.put(hash, node);
    }
  }

  // 移除物理节点
  public void remove(T node) {
    for (int i = 0; i < virtualNodeCount; i++) {
      long hash = hash(node.toString() + "#" + i);
      ring.remove(hash);
    }
  }

  // 查找 key 落在哪个节点
  public T getNode(String key) {
    if (ring.isEmpty()) return null;
    long hash = hash(key);
    // 沿环顺时针找第一个 ≥ hash 的节点
    SortedMap<Long, T> tailMap = ring.tailMap(hash);
    return tailMap.isEmpty() ? ring.firstEntry().getValue() : tailMap.get(tailMap.firstKey());
  }

  private long hash(String key) {
    // FNV1-64 或 MD5 / MurmurHash
    return Math.abs(key.hashCode());
  }
}
```

## 5. Redis Cluster 的另一种实现：哈希槽

Redis Cluster **不用一致性哈希**，而是用**固定 16384 个哈希槽**：

```
slot = crc16(key) % 16384

物理节点映射：
  Node A 负责 slots 0-5460
  Node B 负责 slots 5461-10922
  Node C 负责 slots 10923-16383
```

### 5.1 为什么是 16384？

- 节点间同步配置时，每个节点发 16384 bit（2KB）描述槽归属 → 传输轻量
- 槽数太少：单个槽数据量大，迁移粒度粗
- 槽数太多：配置信息膨胀
- 16384 是经验折中

### 5.2 新增节点时的迁移

```
新增 Node D，从 A / B / C 各匀一些 slots 给 D：
  A: 0-4000
  B: 4001-7500
  C: 7501-10922
  D: 10923-16383

迁移粒度 = slot（不是 key）
迁移单位 = slot
📌 不影响其他 slot 的服务（在线迁移）
```

### 5.3 一致性哈希 vs 哈希槽

| 维度 | 一致性哈希 | 哈希槽 |
|---|---|---|
| 数据分布粒度 | key 级 | slot 级（粒度更粗） |
| 节点变动影响 | 相邻 key 受影响 | 整 slot 迁移 |
| 迁移粒度 | 单 key | slot（几千个 key 一组） |
| 均衡性 | 依赖虚拟节点 | 由 slot 分配保证 |
| 复杂度 | 简单 | 略复杂 |

## 6. 一致性哈希的局限

### 6.1 不解决数据倾斜

```
某 key 是热点（如明星微博），无论落哪个节点都打爆它
→ 一致性哈希不能解决热点 key
→ 解决思路：
   - 多级副本：热点 key 在多个节点都有副本
   - 本地缓存：在每个 app server 加 L1 cache
   - 一致性哈希 + 二级 hash（同一 key 落到多个节点）
```

### 6.2 不解决脑裂（Split Brain）

```
网络分区时，A 区认为 B 挂了，B 区认为 A 挂了 → 都独立服务 → 数据不一致
→ 需要额外机制（多数派、lease、fencing token）
```

### 6.3 节点权重不同

```
Node A（32GB）应该比 Node B（16GB）承担更多 key
→ 基础一致性哈希：虚拟节点数等比 → 比例相同
→ 加权一致性哈希：Node A 配 2 倍虚拟节点
→ 见 Ketama 一致性哈希算法（memcached 客户端实现）
```

## 7. 工程实践

### 7.1 Memcached 客户端选型

```
spymemcached（Java）：
  - 默认使用 Ketama 算法
  - 虚拟节点数可配
  - 节点增减时只影响相邻 key

libmemcached（C/C++）：
  - 支持一致性哈希
  - 提供 ketama 算法实现
```

### 7.2 数据迁移（rebalance）

```
新加节点 D，从 A / B 迁移数据：
  1. 计算 key 属于 D vs A/B 的范围
  2. 停止该 range 的写入（或者双写）
  3. 把数据从 A/B 复制到 D
  4. 切换路由
  5. 删除 A/B 上的旧数据

📌 工具支持：
  - Redis Cluster：MIGRATE 命令 + 集群管理
  - Cassandra：自动 rebalance
  - 自研：双写 + 回填 + 校验
```

## 8. 一句话总结

```
📌 一致性哈希 = 节点变动只影响相邻 key（O(K/N) 迁移）
📌 虚拟节点 = 解决节点少时的负载倾斜
📌 Redis Cluster 用哈希槽（16384）是变种，迁移粒度更可控
📌 不解决热点 key（要靠多副本 / 本地缓存）
📌 不解决脑裂（要靠多数派 / fencing）
```

## 9. 参考资料

- Consistent Hashing and Random Trees: Distributed Caching Protocols for Relieving Hot Spots (Karger et al., 1997)
- Web Caching with Consistent Hashing (Karger et al., 1999)
- Dynamo: Amazon's Highly Available Key-value Store (DeCandia et al., 2007)
- Cassandra Architecture（一致性哈希实战）
- Redis Cluster Specification（哈希槽设计）


<!-- auto-enrich:do-not-edit -->

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->

<!-- svg-injected:do-not-edit -->

![consistent hash ring](/consistent-hash-ring.svg)
