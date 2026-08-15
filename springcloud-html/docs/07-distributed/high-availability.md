---
title: 高可用与限流熔断
---

# 🛡️ 高可用与限流熔断

> 保障分布式系统**在故障和高压下仍能提供服务**。

## 🎯 高可用的目标

**可用性 = 系统可以正常服务的时间 / 总时间**

| 可用性等级 | 年宕机时间 | 适用场景 |
|---|---|---|
| **99%** | 87.6 小时 | 一般业务 |
| **99.9%** | 8.76 小时 | 互联网应用 |
| **99.99%** | 52.6 分钟 | 金融级 |
| **99.999%** | 5.26 分钟 | 电信级 |

## 🛡️ 稳定性设计四大法宝

| 法宝 | 英文 | 作用 |
|---|---|---|
| **限流** | Rate Limiting | 拒绝超额请求，保护系统 |
| **熔断** | Circuit Breaking | 快速失败，避免雪崩 |
| **降级** | Degradation | 关闭非核心，保核心 |
| **隔离** | Isolation | 故障不扩散（线程池 / 进程）|

```
              客户端
                 │
                 ↓
        ┌──────────────┐
        │   限流        │ ← 第一道防线：拒绝超额
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │   熔断        │ ← 第二道防线：快速失败
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │   降级        │ ← 第三道防线：保护核心
        └──────┬───────┘
               ↓
            核心服务
```

## 🚧 限流（Rate Limiting）

### 限流算法

| 算法 | 原理 | 优点 | 缺点 |
|---|---|---|---|
| **固定窗口** | 固定时间段内计数 | 简单 | 临界突刺 |
| **滑动窗口** | 多个小窗口加权平均 | 平滑 | 实现复杂 |
| **令牌桶** | 匀速放令牌 | 允许突发 | 复杂 |
| **漏桶** | 匀速漏水 | 平滑限流 | 不灵活 |

**令牌桶示意：**
```
令牌桶容量 100，每秒放 10 个令牌

      ┌─→ 处理请求（消耗令牌）
令牌 →│
      └─→ 桶满则丢弃新令牌

突发时桶内有 100 个令牌，可一次性处理 100 个
稳态时每秒最多处理 10 个
```

### Nginx 限流

```nginx
# 按 IP 限流
limit_req_zone $binary_remote_addr zone=ip_limit:10m rate=10r/s;

location /api/ {
    limit_req zone=ip_limit burst=20 nodelay;
    proxy_pass http://backend;
}
```

### Sentinel 限流（推荐）

```java
// 引入依赖
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-sentinel</artifactId>
</dependency>
```

**定义资源：**
```java
@Service
public class OrderService {

    @SentinelResource(
        value = "createOrder",           // 资源名
        blockHandler = "handleBlock",    // 限流处理
        fallback = "handleFallback"      // 降级处理
    )
    public Order create(OrderDTO dto) {
        // 业务逻辑
        return orderMapper.insert(dto);
    }

    // 限流时调用
    public Order handleBlock(OrderDTO dto, BlockException ex) {
        log.warn("限流: {}", dto);
        throw new BusinessException("系统繁忙，请稍后再试");
    }

    // 降级时调用
    public Order handleFallback(OrderDTO dto, Throwable ex) {
        return new Order(-1L, "降级订单");
    }
}
```

**Sentinel 控制台配置规则：**
- **QPS 限流**：每秒最多 100 个请求
- **并发线程数**：最多 50 个线程
- **关联限流**：下单限流时连带限制支付
- **链路限流**：只针对特定入口限流

### 分布式限流

**Redis + Lua 滑动窗口：**

```lua
-- Redis Lua 脚本
local key = KEYS[1]
local window = tonumber(ARGV[1])  -- 窗口大小（秒）
local limit = tonumber(ARGV[2])   -- 限流阈值
local now = tonumber(ARGV[3])     -- 当前时间戳

-- ZSET 移除窗口外的元素
redis.call('ZREMRANGEBYSCORE', key, 0, now - window * 1000)

-- 当前窗口内元素数量
local count = redis.call('ZCARD', key)

if count < limit then
    -- 添加新请求
    redis.call('ZADD', key, now, now)
    redis.call('EXPIRE', key, window)
    return 1   -- 允许
else
    return 0   -- 限流
end
```

```java
// Java 调用
Long allowed = redisTemplate.execute(redisScript, keys, args);
if (allowed == 0) {
    throw new RateLimitException("请求过于频繁");
}
```

## ⚡ 熔断（Circuit Breaking）

### 三种状态

```
                  失败率 > 阈值
        ┌──────────────────────────┐
        ↓                          │
   ┌─────────┐  失败率 < 阈值   ┌─────────┐
   │CLOSED   │ ─────────────→   │HALF_OPEN│
   │关闭（正常）│ ←──────────     │半开（探测）│
   └────▲────┘   连续成功 N 次    └────┬────┘
        │                            │ 失败
        │                            ↓
        │                       ┌─────────┐
        └───────────────────────┘OPEN     │
                            ↑  │ 打开（拒绝）│
                            └──┴─────────┘
                              超时后转 HALF_OPEN
```

| 状态 | 行为 |
|---|---|
| **CLOSED** | 正常调用，统计失败率 |
| **OPEN** | 直接拒绝请求（快速失败）|
| **HALF_OPEN** | 放部分请求探测，成功则恢复，失败则继续 OPEN |

### Sentinel 熔断

**控制台规则：**
- 慢调用比例：响应时间 > 1s 的请求占比 > 50%
- 异常比例：异常请求占比 > 50%
- 异常数：1 分钟内异常数 > 10

### Resilience4j（Spring 推荐）

```java
@Service
public class InventoryService {

    private final CircuitBreaker circuitBreaker =
        CircuitBreaker.ofDefaults("inventory");

    public Inventory query(Long id) {
        return CircuitBreaker.decorateCallable(
            circuitBreaker,
            () -> remoteCall(id)
        ).call();
    }
}
```

**配置：**
```yaml
resilience4j:
  circuitbreaker:
    instances:
      inventory:
        sliding-window-size: 10
        failure-rate-threshold: 50      # 失败率 50%
        wait-duration-in-open-state: 30s # OPEN 30 秒
        permitted-number-of-calls-in-half-open-state: 5
```

### Hystrix（已停止维护）

```java
@HystrixCommand(
    fallbackMethod = "fallback",
    commandProperties = {
        @HystrixProperty(name = "circuitBreaker.errorThresholdPercentage", value = "50"),
        @HystrixProperty(name = "circuitBreaker.sleepWindowInMilliseconds", value = "30000")
    }
)
public String query(Long id) {
    return remoteCall(id);
}

public String fallback(Long id) {
    return "兜底数据";
}
```

## 🔻 降级（Degradation）

### 降级分类

| 降级方式 | 说明 | 示例 |
|---|---|---|
| **页面降级** | 返回静态 / 缓存页面 | 秒杀返回"已售罄" |
| **服务降级** | 关闭非核心服务 | 关闭推荐、评论 |
| **数据降级** | 返回兜底数据 | 默认头像、默认昵称 |
| **功能降级** | 关闭部分功能 | 关闭导出、关闭搜索 |
| **读降级** | 读缓存代替读 DB | Redis 代替 MySQL |
| **写降级** | 异步写代替同步写 | MQ 代替直接写 |

### Sentinel 降级

```java
@SentinelResource(
    value = "queryProduct",
    fallback = "queryProductFallback"
)
public Product queryProduct(Long id) {
    return productMapper.findById(id);
}

public Product queryProductFallback(Long id) {
    // 返回默认商品
    return new Product(id, "默认商品", 0.0);
}
```

## 🚪 隔离（Isolation）

### 隔离方式

| 方式 | 原理 | 优缺点 |
|---|---|---|
| **线程池隔离** | 每个服务独立线程池 | 隔离彻底 / 线程开销大 |
| **信号量隔离** | 用信号量控制并发 | 轻量 / 不支持超时 |
| **进程隔离** | 每个服务独立进程 | 强隔离 / 资源浪费 |
| **集群隔离** | 不同业务用不同集群 | 物理隔离 / 成本高 |
| **读写隔离** | 读写走不同集群 | 性能优化 |

### Sentinel 线程池隔离

```java
@SentinelResource(
    value = "slowService",
    blockHandler = "slowBlock",
    fallback = "slowFallback"
)
@SentinelResource(value = "fastService")
```

## 🏔️ 多活 / 容灾

### 部署模式

| 模式 | 含义 | 优点 | 缺点 |
|---|---|---|---|
| **同城双活** | 同城两个机房，互备 | RTO 短 | 不能抗机房级灾难 |
| **异地多活** | 多地部署 | 抗灾难 | 数据同步复杂 |
| **两地三中心** | 生产 + 同城灾备 + 异地灾备 | 平衡 | 成本高 |

### 数据同步方案

```
        主机房                  灾备机房
       ┌────┐                 ┌────┐
       │Master│──binlog/CDC──→│Standby│
       └────┘                 └────┘
```

| 同步方式 | 时延 | 一致性 |
|---|---|---|
| **同步复制** | 高 | 强一致 |
| **异步复制** | 低 | 最终一致 |
| **半同步** | 中 | 中 |

## ⚠️ 雪崩场景与防护

### 雪崩发生过程

```
T1: Service-A 调用 Service-B（响应慢）
T2: Service-A 线程池被 B 阻塞
T3: Service-A 接收新请求 → 拒绝（线程满）
T4: 上游 Service 调用 A → 也阻塞
T5: 整个调用链崩溃 💥
```

### 防护策略

| 策略 | 作用 |
|---|---|
| **超时设置** | 避免无限等待 |
| **线程池隔离** | 故障不蔓延 |
| **熔断器** | 快速失败，保护上游 |
| **限流** | 拒绝超额 |
| **降级** | 保留核心功能 |
| **重试（带熔断）** | 临时故障可恢复 |

**完整防护配置示例：**

```java
@SentinelResource(
    value = "createOrder",
    blockHandler = "handleBlock",       // 限流
    fallback = "handleFallback",        // 降级
    exceptionsToIgnore = {BusinessException.class}  // 业务异常不熔断
)
```

## 🎯 限流 / 熔断 / 降级的区别

| 维度 | 限流 | 熔断 | 降级 |
|---|---|---|---|
| **目标** | 控制流量 | 避免雪崩 | 保留核心 |
| **触发** | 流量超限 | 失败率超阈 | 系统压力 |
| **行为** | 直接拒绝 | 直接拒绝 | 返回兜底 |
| **触发方** | 自身 | 自身 | 系统配置 |

## 🎓 面试高频问题

| 问题 | 关键点 |
|---|---|
| 限流算法？| 固定窗口 / 滑动窗口 / 令牌桶 / 漏桶 |
| 熔断状态机？| CLOSED → OPEN → HALF_OPEN → CLOSED |
| 雪崩如何防护？| 超时 + 隔离 + 熔断 + 限流 + 降级 |
| Sentinel vs Hystrix？| Sentinel 实时监控 + 多维度规则，Hystrix 已停止维护 |
| 隔离方式？| 线程池隔离 / 信号量隔离 / 进程隔离 |

---

- 上一章：[🔍 分布式追踪](/07-distributed/distributed-tracing)
- 下一章：[💼 综合实战](/06-practice/comprehensive)