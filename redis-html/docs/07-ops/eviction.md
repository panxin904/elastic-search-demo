---
title: 内存淘汰策略
---

# 内存淘汰策略

当 Redis 内存达到 `maxmemory` 上限时，必须有一套规则决定该删掉哪些 key，否则写入会被拒绝。理解这 8 大策略，是运维调优的第一课。

## 为什么需要淘汰策略

Redis 把所有数据放在内存里。一台 32GB 的机器，刨去操作系统和副本开销，能给 Redis 的也就 24GB。业务一旦放量，内存迟早会满。

```bash
# 查看当前 maxmemory 配置
redis-cli CONFIG GET maxmemory
# 1) "maxmemory"
# 2) "0"          # 0 表示无限制（生产严禁这么配）

# 临时修改
redis-cli CONFIG SET maxmemory 16gb
redis-cli CONFIG REWRITE  # 落盘到 redis.conf
```

`maxmemory` 触顶后再写入时，Redis 按当前配置的策略决定行为，要么拒绝、要么挑 key 删除腾地方。

## 8 大淘汰策略

Redis 6+ 一共提供 8 个策略，可从两个维度分类：淘汰范围（全部 key / 仅过期 key）+ 淘汰算法（LRU / LFU / 随机 / TTL）。

| 策略 | 范围 | 算法 | 适用场景 |
|---|---|---|---|
| `noeviction` | — | 不淘汰 | 写少读多、不允许丢数据（默认） |
| `allkeys-lru` | 所有 key | LRU | 缓存场景，通用性最强 |
| `volatile-lru` | 仅设了过期的 key | LRU | 部分数据要持久化，部分当缓存 |
| `allkeys-lfu` | 所有 key | LFU | 热点分布明显（Redis 4.0+） |
| `volatile-lfu` | 仅设了过期的 key | LFU | 热点 + 部分持久化（Redis 4.0+） |
| `allkeys-random` | 所有 key | 随机 | 访问均匀，无法区分冷热 |
| `volatile-random` | 仅设了过期的 key | 随机 | 同上，但保留永久 key |
| `volatile-ttl` | 仅设了过期的 key | TTL 最小优先 | 明确知道哪些 key 即将过期 |

### 策略选择决策树

```
数据能否丢？
├── 不能丢 → noeviction（写满后 OOM 报错）
└── 能丢
    ├── 是否所有 key 都是缓存？
    │   └── 是 → allkeys-lru（首选）或 allkeys-lfu（热点明显）
    └── 混合（部分持久 + 部分缓存）
        └── volatile-lru / volatile-lfu / volatile-ttl
```

## LRU vs LFU 区别

这是面试高频题，两者底层完全不同。

### LRU（Least Recently Used）

最近最少使用。Redis 用**近似 LRU**：给每个 key 维护一个 24 位时间戳，淘汰时随机采样一批 key，挑最久没访问的。

### LFU（Least Frequently Used）

最不经常使用（Redis 4.0+ 引入）。给每个 key 维护两个 8 位计数器：
- `access frequency`：访问频率
- `decay`：时间衰减因子（避免老 key 永远占着位置）

```bash
# 查看某个 key 的 LFU 信息
redis-cli DEBUG OBJECT mykey
# Value at:0x7f... refcount:1 encoding:embstr serializedlength:42 lru:12345678 lfu:5 2

# OBJECT FREQ 返回访问频率
redis-cli OBJECT FREQ mykey
# (integer) 5
```

### 实战对比

| 维度 | LRU | LFU |
|---|---|---|
| 抗突发流量 | 弱，一次扫描潮就能刷掉热数据 | 强，频率有衰减周期 |
| 抗缓存污染 | 中等 | 较好 |
| 适用 | 通用缓存 | 热点分布明显（如秒杀、新闻热点） |

> 一句话：LRU 看"最近来没来"，LFU 看"来得勤不勤"。

## maxmemory 配置

```properties
# redis.conf
# 单位支持 KB / MB / GB
maxmemory 16gb

# 策略选择
maxmemory-policy allkeys-lru

# 采样数，越大越接近真实 LRU，但 CPU 也越高
maxmemory-samples 10

# 副本是否使用独立内存（默认 no，副本继承主节点驱逐决定）
# replica-ignore-maxmemory yes
```

### 内存到底该配多大？

经验公式：

```
maxmemory = (机器总内存 - 系统预留 - 副本占用) × 0.7
```

- 系统预留：留 4~6GB 给 OS 页缓存、fork 内存
- 副本开销：如果是主从，副本会全量复制，内存压力相同
- 0.7 是安全系数，避免 OOM

## 采样精度：maxmemory-samples

Redis 的 LRU/LFU 都是**近似**算法，不是真正的全局 LRU。`maxmemory-samples` 决定每次淘汰时随机抽多少 key 来挑"最该被淘汰的那个"。

```bash
# 默认 5，可调到 10（接近真实 LRU，CPU +20%）
redis-cli CONFIG SET maxmemory-samples 10
```

| 采样数 | 精度 | CPU 开销 | 推荐 |
|---|---|---|---|
| 1 | 低 | 极低 | 不推荐 |
| 5（默认） | 中 | 低 | 通用 |
| 10 | 高 | 中 | 内存敏感场景 |
| 20+ | 极高 | 高 | 慎用 |

## 面试题：MySQL 里有 2000w 数据，Redis 只存 20w 热点数据，怎么配？

这是经典场景：MySQL 是冷数据全量库，Redis 只缓存热点 20w。

### 配置方案

```properties
# 1. 内存上限：按 20w 条数据预估，单 key 平均 1KB → 200MB 足够
maxmemory 4gb              # 留余量给未来增长
maxmemory-policy allkeys-lru
maxmemory-samples 10
```

### 数据预热 + 同步策略

```python
# 伪代码：启动时从 MySQL 加载热点
HOT_KEYS = mysql.query("SELECT id FROM items WHERE is_hot=1 LIMIT 200000")

# 写入 Redis（用 pipeline 批量）
pipe = redis.pipeline()
for key in HOT_KEYS:
    pipe.setex(f"item:{key}", 3600, mysql.get(f"item:{key}"))
pipe.execute()
```

### 关键点

1. **不设过期时间**：让 LRU 自主淘汰，业务方无需关心"该删谁"
2. **动态加载**：MySQL 数据变更时双写或异步同步到 Redis
3. **监控命中率**：`keyspace_hits / (keyspace_hits + keyspace_misses)`，目标 ≥ 95%

```bash
redis-cli INFO stats | grep keyspace
# keyspace_hits:950000
# keyspace_misses:50000
# 命中率 = 950000 / (950000+50000) = 95%
```

## 生产监控案例

### 案例 1：写入失败告警

某电商大促，缓存写满后开始报错：

```
MISCONF Redis is configured to save RDB snapshots, but it is currently not able to persist on disk.
```

排查：

```bash
redis-cli CONFIG GET maxmemory*
# maxmemory 设为 8gb，触发上限

redis-cli INFO memory | grep maxmemory
# maxmemory_human:8.00G
# maxmemory_policy:noeviction
```

修复：调大 maxmemory 到 16gb，策略改为 `allkeys-lfu`。

### 案例 2：命中率从 99% 掉到 70%

```
keyspace_hits 增长但命中率下降 → maxmemory 不够，频繁淘汰
```

```bash
# 查看驱逐次数
redis-cli INFO stats | grep evicted
# evicted_keys:15230  # 5 分钟内被驱逐 1.5w 次，太多了

# 解决：扩内存 + 调采样
CONFIG SET maxmemory 24gb
CONFIG SET maxmemory-samples 10
```

扩内存后 `evicted_keys` 应该停止增长，命中率回升。

## 下一步

淘汰策略只是"亡羊补牢"，根本还是要控制内存本身。下一步看 [💾 内存管理优化](/07-ops/memory)，从编码、碎片、共享 value 三个维度把内存打下去。