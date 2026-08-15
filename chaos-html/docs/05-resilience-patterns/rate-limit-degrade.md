---
title: 限流与降级
---

# 限流与降级

## 限流算法

**1. 令牌桶（Token Bucket）**：

- 桶容量 N，每 R 秒加 1 个令牌
- 请求消耗 1 个令牌，无令牌则拒绝
- 允许突发（桶满时可瞬时 N 个）

**2. 漏桶（Leaky Bucket）**：

- 请求进入桶，桶以固定速率漏水
- 桶满则溢出（拒绝）
- 强制平滑输出

**3. 滑动窗口（Sliding Window）**：

- 滚动时间窗口（1 分钟内最多 N 个请求）
- 比固定窗口更平滑

**4. 计数器（Counter）**：

- 简单：每分钟一个计数器
- 缺点：窗口边界突刺（59 秒 + 1 秒可瞬时 2N）

## Sentinel（阿里）实现

```java
@SentinelResource(value = "orderCreate", blockHandler = "handleBlock")
public Order createOrder(OrderRequest req) {
    return orderService.create(req);
}

public Order handleBlock(OrderRequest req, BlockException e) {
    throw new RateLimitException("too many requests");
}

FlowRule rule = new FlowRule("orderCreate")
    .setGrade(RuleConstant.FLOW_GRADE_QPS)
    .setCount(1000);
FlowRuleManager.loadRules(Collections.singletonList(rule));
```

**Sentinel 特性**：

- QPS 限流
- 并发线程数限流
- 慢调用比例降级
- 异常比例降级
- Sentinel Dashboard 实时监控

## Istio 限流（Envoy Filter）

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: rate-limit
spec:
  configPatches:
  - applyTo: HTTP_FILTER
    match:
      context: SIDECAR_INBOUND
      listener:
        filterChainMatch:
          destinationPort: 8080
    patch:
      operation: INSERT_BEFORE
      value:
        name: envoy.filters.http.local_ratelimit
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.http.local_ratelimit.v3.LocalRateLimit
          stat_prefix: http_local_rate_limiter
          token_bucket:
            max_tokens: 1000
            tokens_per_fill: 1000
            fill_interval: 60s
```

## 降级策略

**1. 功能降级**：

- 大促期间关闭「推荐」「个性化」非核心功能
- 关闭「历史订单查询」→ 只显示最近 7 天
- 关闭「评论 / 评分」

**2. 数据降级**：

- 用 cached data 替代实时查询
- 用 default value（如返回空列表）
- 用上次成功结果（stale-while-error）

**3. 链路降级**：

- 主链路 → 简化版（跳过非关键步骤）
- 同步链路 → 异步链路

**4. 自动 vs 手动降级**：

- 自动：根据 SLO / 错误率自动触发
- 手动：运维手动开关（如「双 11 大促开关」）

## 与其他站点关系

- **chaos/05-resilience-patterns/circuit-breaker**：熔断 + 降级
- **design-pattern/05-architectural-patterns**：限流模式
- **observability/08-alerting**：限流告警


## ## 实战案例

**Sentinel 限流**：阿里 Sentinel 在双 11 流量峰值 100w+ QPS 下精确控制每服务每接口的限流阈值。

**Envoy 限流**：Lyft Envoy 用 rls (Rate Limit Service) 过滤非核心流量，保护核心订单流程。

**Nginx 限流**：limit_req_zone 按 IP/URI 限流，突发流量 503 保护上游。

**降级策略**：读非核心数据降级（推荐、广告）、写非核心操作降级（积分、评论）、强核心功能保留（支付、登录）。


## ## 故障排查清单

1. 限流误伤 → 调整阈值 + 区分黑白名单
2. 降级不生效 → 检查 fallback 逻辑
3. 限流太严格 → 监控 503 比例
4. 分布式限流 → 用 Redis + Lua / Token Bucket
5. 降级可靠性 → 降级本身也要监控
