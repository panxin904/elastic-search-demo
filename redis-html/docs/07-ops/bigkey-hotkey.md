---
title: 大 Key 热 Key
date: 2026-08-15  # date-auto-injected
---

# 大 Key 热 Key

大 Key 和热 Key 是 Redis 运维的两大隐形炸弹。前者让运维动作"卡住"，后者让流量"打爆"。这一篇讲清楚怎么识别、怎么处理。

![Redis Bigkey Detection](/redis-bigkey-detection.svg)

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600">Redis 大 Key / 热 Key 处理</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">识别 · 拆分 · 监控 · 一致性</text>

  <!-- 大 Key 类型 -->
  <text x="155" y="95" text-anchor="middle" font-size="13" font-weight="700" fill="#1e293b">典型大 Key 类型</text>

  <rect class="at-hover-card" x="30" y="110" width="120" height="70" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="90" y="133" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">String</text>
  <text x="90" y="151" text-anchor="middle" font-size="10" fill="#475569">单个 value &gt; 10MB</text>
  <text x="90" y="167" text-anchor="middle" font-size="9" fill="#64748b" font-style="italic">缓存 JSON 大对象</text>

  <rect class="at-hover-card" x="160" y="110" width="120" height="70" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
  <text x="220" y="133" text-anchor="middle" font-size="11" font-weight="700" fill="#047857">Hash/List/Set</text>
  <text x="220" y="151" text-anchor="middle" font-size="10" fill="#475569">元素 &gt; 1万</text>
  <text x="220" y="167" text-anchor="middle" font-size="9" fill="#64748b" font-style="italic">粉丝列表 / 队列</text>

  <rect class="at-hover-card" x="30" y="190" width="250" height="60" rx="6" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5"/>
  <text x="155" y="213" text-anchor="middle" font-size="11" font-weight="700" fill="#991b1b">危害</text>
  <text x="50" y="232" font-size="10" fill="#334155">· DEL 阻塞（删除 1MB+ 元素需秒级）</text>
  <text x="50" y="248" font-size="10" fill="#334155">· 集群 slot 倾斜（请求集中）</text>

  <!-- 热 Key -->
  <text x="445" y="95" text-anchor="middle" font-size="13" font-weight="700" fill="#1e293b">典型热 Key 模式</text>

  <rect class="at-hover-card" x="320" y="110" width="120" height="70" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="380" y="133" text-anchor="middle" font-size="11" font-weight="700" fill="#92400e">秒杀商品</text>
  <text x="380" y="151" text-anchor="middle" font-size="10" fill="#475569">秒杀:item:10086</text>
  <text x="380" y="167" text-anchor="middle" font-size="9" fill="#64748b" font-style="italic">QPS 瞬间 10w+</text>

  <rect class="at-hover-card" x="450" y="110" width="120" height="70" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="510" y="133" text-anchor="middle" font-size="11" font-weight="700" fill="#92400e">热点新闻</text>
  <text x="510" y="151" text-anchor="middle" font-size="10" fill="#475569">news:hot:top10</text>
  <text x="510" y="167" text-anchor="middle" font-size="9" fill="#64748b" font-style="italic">某条新闻刷屏</text>

  <rect class="at-hover-card" x="320" y="190" width="250" height="60" rx="6" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5"/>
  <text x="445" y="213" text-anchor="middle" font-size="11" font-weight="700" fill="#991b1b">危害</text>
  <text x="340" y="232" font-size="10" fill="#334155">· 单节点带宽 / CPU 饱和</text>
  <text x="340" y="248" font-size="10" fill="#334155">· 集群扩容无法缓解（数据集中 1 节点）</text>

  <!-- 解决策略 -->
  <text x="300" y="280" text-anchor="middle" font-size="13" font-weight="700" fill="#1e293b">处理策略</text>

  <rect class="at-hover-card" x="30" y="295" width="260" height="170" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
  <text x="160" y="318" text-anchor="middle" font-size="12" font-weight="700" fill="#047857">大 Key 处理</text>

  <text x="50" y="345" font-size="11" font-weight="700" fill="#1e293b">① 拆分</text>
  <text x="50" y="362" font-size="10" fill="#475569">Hash 分桶：user:100 → user:100:1 / :2 / :3</text>

  <text x="50" y="383" font-size="11" font-weight="700" fill="#1e293b">② UNLINK 异步删除</text>
  <text x="50" y="400" font-size="10" fill="#475569">替代 DEL（Redis 4.0+）后台回收</text>

  <text x="50" y="421" font-size="11" font-weight="700" fill="#1e293b">③ SCAN 渐进遍历</text>
  <text x="50" y="438" font-size="10" fill="#475569">避免 KEYS * 阻塞（O(N) 全扫描）</text>
  <text x="50" y="453" font-size="10" fill="#475569">SCAN cursor MATCH pattern COUNT 100</text>

  <rect class="at-hover-card" x="310" y="295" width="260" height="170" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="440" y="318" text-anchor="middle" font-size="12" font-weight="700" fill="#1e40af">热 Key 处理</text>

  <text x="330" y="345" font-size="11" font-weight="700" fill="#1e293b">① 本地缓存</text>
  <text x="330" y="362" font-size="10" fill="#475569">Caffeine + Redis 二级缓存（5s TTL）</text>

  <text x="330" y="383" font-size="11" font-weight="700" fill="#1e293b">② Key 分散</text>
  <text x="330" y="400" font-size="10" fill="#475569">item:10086 → item:10086:{0..N} 随机</text>

  <text x="330" y="421" font-size="11" font-weight="700" fill="#1e293b">③ 读写分离</text>
  <text x="330" y="438" font-size="10" fill="#475569">主写 + 多从读，负载分散</text>
  <text x="330" y="453" font-size="10" fill="#475569">注意：可能读到 stale</text>
</svg>

## 大 Key：定义与危害

### 什么是大 Key

```bash
# 推荐阈值（来自阿里云 Redis 规范）
string > 10KB
hash / list / set / zset 元素数 > 5000
```

但实际生产中，"大"是相对的：1MB 的 string 在 32GB 内存机器上不算大，但 1MB 的 string 删一次可能卡 100ms。

### 大 Key 的三大危害

**危害 1：DEL 阻塞主线程**

```bash
redis-cli DEL huge:key
# (error) BUSYKEY Redis is busy running a script
```

Redis 是单线程处理命令的。删除一个 1GB 的 list 需要遍历 1000w 个元素，期间所有命令排队。后果：
- 主从复制延迟飙升（从节点要重放 DEL）
- 客户端 timeout 雪崩
- 集群 failover 失败

**危害 2：网络带宽打满**

```
1 个 1MB 的 Key × 10000 QPS = 10GB/s 流量
```

主从同步、客户端拉取都走这个 key 时，单 key 的网络吞吐可能超过网卡上限。

**危害 3：主从复制延迟**

```bash
# 从节点执行 RDB 重放时
redis-cli INFO replication | grep lag
# slave_lag:86400   ← 延迟一整天
```

RDB 文件里一个大 Key 会让加载慢几十秒。

## 大 Key 检测方法

### 方法 1：redis-cli --bigkeys（推荐入门）

```bash
redis-cli --bigkeys
# -------- summary -------
# Biggest string found '"session:abc"' has 524288 bytes
# Biggest   list found '"queue:tasks"' has 80000 items
# Biggest   hash found '"order:detail"' has 5000 fields

# String 总数 / 平均 / 最大
# List 总数 / 平均 / 最大
# ...
```

**局限**：是 SCAN 遍历，慢且不统计内存占用（只数元素数）。

### 方法 2：MEMORY USAGE（精确）

```bash
# 单个 key
redis-cli MEMORY USAGE "order:detail:1"
# (integer) 8388608  ← 8MB

# 批量扫描（用 SCAN + MEMORY USAGE）
redis-cli --scan --pattern "order:*" | head -100 | xargs -I {} redis-cli MEMORY USAGE {}
```

### 方法 3：RDB 分析工具

```bash
# 用 redis-rdb-tools 分析 RDB 文件
pip install rdbtools

rdb -c memory dump.rdb > memory_report.csv

# 找 Top 50 大 Key
sort -t, -k4 -nr memory_report.csv | head -50
# database,type,key,size_in_bytes,encoding,num_elements,len_largest_element
# 0,hash,order:detail:1,8388608,hashtable,5000,512
```

**优势**：离线分析，不影响线上，统计精准。

### 方法 4：DEBUG OBJECT（生产慎用）

```bash
redis-cli DEBUG OBJECT "huge:key"
# Value at:0x7f... refcount:1 encoding:hashtable serializedlength:8388608 ...
```

`serializedlength` 是序列化长度，能大致看出 key 大小。**DEBUG 命令会阻塞，不要在生产高峰期用**。

### 方法 5：lazyfree 兜底（Redis 4.0+）

即使有大 Key，启用 lazyfree 可以避免 DEL 阻塞：

```properties
# redis.conf
lazyfree-lazy-eviction yes
lazyfree-lazy-expire yes
lazyfree-lazy-server-del yes
replica-lazy-flush yes

# 删除包含大量元素的 unlink key
lazyfree-lazy-user-del yes    # Redis 6.0+
```

```bash
# 用 UNLINK 替代 DEL，异步删除
redis-cli UNLINK huge:key
# 立即返回，后台慢慢删
```

## 热 Key：定义与危害

### 什么是热 Key

单 key 的访问 QPS 远超平均，比如：
- 秒杀商品详情：`product:hot:1` 扛 10w QPS
- 明星微博：某条 feed 流量是其他 1w 倍
- 排行榜：`rank:top10` 每秒被读 5w 次

### 热 Key 的危害

**危害 1：单节点 QPS 瓶颈**

Redis 单实例理论 10w+ QPS，但热 Key 会把 CPU 打满：

```bash
redis-cli INFO stats | grep instantaneous
# instantaneous_ops_per_sec:120000
```

CPU 100% 后所有命令排队，集群里其他 slot 跟着遭殃。

**危害 2：带宽瓶颈**

```
单 key 1KB × 10w QPS = 100MB/s
```

单实例千兆网卡（125MB/s）直接打满，主从同步延迟。

**危害 3：缓存击穿后压垮下游**

热 Key 突然失效（比如 TTL 到期），瞬间 10w QPS 砸到 MySQL。

## 热 Key 发现方法

### 方法 1：redis-cli --hotkeys（Redis 7+）

```bash
redis-cli --hotkeys
# Summary
# Hot keys found:
# 1. "product:hot:1" with 95234 accesses
# 2. "rank:top10" with 82110 accesses
```

底层用 `OBJECT FREQ`，但只能扫当前 db 的部分 key（最多 scan 16 次）。

### 方法 2：monitor 命令（最准，生产慎用）

```bash
# 抓一段时间的所有命令
timeout 30 redis-cli MONITOR > monitor.log
# Ctrl+C 停止
```

```bash
# 统计命令频次
cat monitor.log | awk '{print $4}' | sort | uniq -c | sort -rn | head -20
# 152340 "GET" "product:hot:1"
#  82100 "GET" "rank:top10"
```

**危险**：MONITOR 会让 Redis 吞吐量降 50%+，只能在低峰期短时间用。

### 方法 3：proxy 层统计

如果用了 Twemproxy / Codis / Redis Cluster 的代理层，可以从 proxy 统计：

```
# Twemproxy 统计
# data_store:redis_servers:north-1:stats
#   get_product:hot:1: 95234
```

优势是不影响 Redis 本身。

### 方法 4：业务层埋点

最准确的方法。在业务代码里包一层：

```python
class HotKeyDetector:
    def __init__(self):
        self.counter = defaultdict(int)

    def get(self, key):
        self.counter[key] += 1
        return self.redis.get(key)

    def report_top_n(self, n=100):
        return sorted(self.counter.items(), key=lambda x: -x[1])[:n]
```

定期把 top 100 上报到监控系统，定位热 Key。

### 方法 5：Redis Exporter + Prometheus

```yaml
# prometheus 配置
scrape_configs:
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

Grafana 面板看 `redis_keyspace_hits_total` 按 key 分布需要额外定制，**默认 Exporter 不支持按 key 统计**，需要自己埋点。

## 处理方案

### 大 Key 处理

**方案 1：拆分**

```bash
# 原来：一个 hash 存所有订单字段
HSET order:1 product_id 1001 user_id 42 amount 99 ...

# 拆成：按字段前缀分组
HSET order:1:base product_id 1001 user_id 42
HSET order:1:detail amount 99 address "..."
```

**方案 2：压缩**

```python
import gzip, json

def set_compressed(redis, key, data):
    raw = json.dumps(data).encode()
    compressed = gzip.compress(raw)
    redis.set(key, compressed)

def get_compressed(redis, key):
    raw = redis.get(key)
    return json.loads(gzip.decompress(raw))
```

**方案 3：UNLINK 异步删除**

```bash
# 替代 DEL
redis-cli UNLINK huge:key
```

**方案 4：分批删除**

```python
# 删除大 list，分批 POP
while redis.LLEN("huge:list") > 0:
    redis.LPOP("huge:list", count=1000)
```

### 热 Key 处理

**方案 1：多级缓存**

```
客户端 → JVM 本地缓存（Caffeine，TTL 1s）→ Redis → MySQL
```

本地缓存抗 80% 流量，Redis 只扛 20%。

```java
Cache<String, String> localCache = Caffeine.newBuilder()
    .maximumSize(10_000)
    .expireAfterWrite(Duration.ofSeconds(1))
    .build();

String getProduct(String id) {
    return localCache.get(id, k -> redis.get("product:" + k));
}
```

**方案 2：Key 分散（读写分流）**

```python
import hashlib

def get_hot_key(real_key, replica_count=10):
    shard = hashlib.md5(real_key.encode()).hexdigest()
    return f"{real_key}:shard:{shard % replica_count}"

# 写时同步所有分片
def set_hot_key(real_key, value):
    pipe = redis.pipeline()
    for i in range(10):
        pipe.set(f"{real_key}:shard:{i}", value)
    pipe.execute()
```

读取时随机打到一个分片，单 key QPS 降为 1/10。

**方案 3：Cluster 分散 slot**

```bash
# 把热 key 单独分配到不同 slot（用 hashtag 强制同 slot）
redis-cli CLUSTER KEYSLOT "product:hot:1"
# 计算后会落到某个 slot

# 用 hashtag 强制分散（不推荐，仅理论）
# "product:{shard1}:1", "product:{shard2}:1" ...
```

**方案 4：限流**

```python
from redis_rate_limit import RateLimiter

limiter = RateLimiter(redis, "hot:product:1", limit=10000, period=1)

def get_product_safe(id):
    if not limiter.allow():
        return fallback_value()  # 返回兜底数据
    return redis.get(f"product:{id}")
```

## 生产监控案例

### 案例 1：大 Key 引发主从切换失败

某实例 `cart:user:12345` 是 500MB 的 hash，运维 `DEBUG SLEEP 5` 后手动 failover，从节点重放 RDB 卡了 30 秒，哨兵认为从节点不健康，failover 反复失败。

排查：

```bash
redis-cli --bigkeys | grep "Biggest   hash"
# Biggest hash found '"cart:user:12345"' has 800000 fields

# 估算序列化时间
# 800000 字段 × 平均 64 字节 = 50MB
# 网络传输 + 序列化约 10 秒
```

修复：拆分 cart，按月份分片（`cart:user:12345:2026:01` 等）。

### 案例 2：秒杀热 Key 打爆 Redis

某秒杀商品 10w QPS 集中在 `seckill:product:888`，Redis CPU 100%。

处理：

```python
# 1. JVM 本地缓存（Caffeine，1 秒 TTL）
local_cache = Caffeine.newBuilder()
    .maximumSize(10000)
    .expireAfterWrite(1, TimeUnit.SECONDS)
    .build()

# 2. Redis 分片读
shards = [f"seckill:product:888:s{i}" for i in range(10)]
def get_seckill_stock():
    key = random.choice(shards)
    return int(redis.get(key))

# 3. 写入时同步所有分片
def set_seckill_stock(stock):
    pipe = redis.pipeline()
    for s in shards:
        pipe.set(s, stock)
    pipe.execute()
```

效果：Redis QPS 从 10w 降到 1w，CPU 50% 降到 5%。

## 下一步

定位完大 Key、热 Key 后，下一个常见问题是"为什么某些命令这么慢"。看 [🐢 慢查询分析](/07-ops/slowlog)，用 SLOWLOG 揪出慢操作。

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [mysql](https://java-px.bot.cd/mysql/):MySQL 主存
- [kafka](https://java-px.bot.cd/kafka/):Kafka 异步队列
- [java](https://java-px.bot.cd/java-web-manual/):Java 客户端（Redisson / Jedis）
