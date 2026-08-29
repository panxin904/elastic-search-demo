---
title: 负载均衡策略
---

# 🎯 负载均衡策略详解

> 选对负载均衡策略，**比加机器更有效**。理解各策略的适用场景，是微服务调优的关键。

## 📊 6 种常用策略对比

| 策略 | 优点 | 缺点 | 适用 |
|---|---|---|---|
| 轮询 (RoundRobin) | 简单均匀 | 不考虑机器差异 | **机器配置相同** |
| 随机 (Random) | 简单 | 极端不均 | 大量机器 |
| 加权轮询 | 考虑差异 | 配置静态 | 机器配置不同 |
| 响应时间 (WeightedResponseTime) | 动态感知 | 历史数据延迟 | **性能差异大** |
| 一致性 Hash | 相同请求到同一实例 | 重新哈希影响大 | **有状态服务** |
| 最少连接 (LeastConnections) | 动态感知 | 需要统计 | **长连接场景** |

## 🎯 实战：选择策略

```yaml
spring:
  cloud:
    loadbalancer:
      configs:
        default:
          type: RoundRobin  # 改这里切换策略
```

```java
// 自定义策略 Bean
@Bean
public ReactorLoadBalancer<ServiceInstance> myLoadBalancer(
    Environment environment,
    LoadBalancerClientFactory factory
) {
    String name = environment.getProperty(LoadBalancerClientFactory.PROPERTY_NAME);
    return new MyLoadBalancer(factory.getLazyProvider(name), name);
}
```

## 1️⃣ 轮询（RoundRobin）

```java
public Mono<Response<ServiceInstance>> choose(Request request) {
    return supplier.getIfAvailable().get().next()
        .map(instances -> {
            // 原子递增，依次选择
            int pos = Math.abs(counter.incrementAndGet() % instances.size());
            return new DefaultResponse(instances.get(pos));
        });
}
```

**适用：** 机器配置相同，请求处理时间相近。

## 2️⃣ 加权轮询（Weighted Round Robin）

```yaml
# Nacos 元数据
spring:
  cloud:
    nacos:
      discovery:
        metadata:
          weight: 100  # 8 核 16G 机器配 100
```

```java
public class WeightedRoundRobinLoadBalancer implements ReactorLoadBalancer<ServiceInstance> {
    
    @Override
    public Mono<Response<ServiceInstance>> choose(Request request) {
        return supplier.getIfAvailable().get().next()
            .map(instances -> {
                // 收集权重
                List<ServiceInstance> weightedList = new ArrayList<>();
                for (ServiceInstance i : instances) {
                    int weight = Integer.parseInt(
                        i.getMetadata().getOrDefault("weight", "100"));
                    for (int n = 0; n < weight / 10; n++) {  // 归一化
                        weightedList.add(i);
                    }
                }
                int pos = Math.abs(counter.incrementAndGet() % weightedList.size());
                return new DefaultResponse(weightedList.get(pos));
            });
    }
}
```

**适用：** 机器配置不同（8 核 vs 16 核）。

## 3️⃣ 一致性 Hash

```java
public class ConsistentHashLoadBalancer implements ReactorLoadBalancer<ServiceInstance> {
    
    @Override
    public Mono<Response<ServiceInstance>> choose(Request request) {
        // 1. 获取请求 key（用户 ID / 会话 ID）
        String key = request.getContext()
            .getClientRequest().getHeaders()
            .getFirst("X-User-Id");
        if (key == null) {
            return supplier.getIfAvailable().get().next()
                .map(instances -> new DefaultResponse(
                    instances.get(new Random().nextInt(instances.size()))));
        }
        
        // 2. 计算 hash
        int hash = Math.abs(key.hashCode());
        
        return supplier.getIfAvailable().get().next()
            .map(instances -> {
                // 3. 选 hash 对应的实例
                int pos = hash % instances.size();
                return new DefaultResponse(instances.get(pos));
            });
    }
}
```

**适用：**
- ✅ Session 共享（如购物车）
- ✅ 缓存亲和性（同用户访问同实例）
- ❌ 实例增减时大量请求重新路由

## 4️⃣ 响应时间加权

```java
public class ResponseTimeLoadBalancer implements ReactorLoadBalancer<ServiceInstance> {
    
    private final Map<String, Long> avgResponseTime = new ConcurrentHashMap<>();
    
    @Override
    public Mono<Response<ServiceInstance>> choose(Request request) {
        return supplier.getIfAvailable().get().next()
            .map(instances -> {
                // 选响应时间最短的
                ServiceInstance best = instances.stream()
                    .min(Comparator.comparingLong(i -> 
                        avgResponseTime.getOrDefault(i.getInstanceId(), 100L)))
                    .orElse(instances.get(0));
                return new DefaultResponse(best);
            });
    }
}
```

**适用：** 实例性能差异大，部分机器快部分慢。

## 5️⃣ 最少活跃数

```java
public class LeastActiveLoadBalancer implements ReactorLoadBalancer<ServiceInstance> {
    
    private final Map<String, AtomicInteger> activeCount = new ConcurrentHashMap<>();
    
    @Override
    public Mono<Response<ServiceInstance>> choose(Request request) {
        return supplier.getIfAvailable().get().next()
            .map(instances -> {
                // 选活跃数最少的（处理请求最少的）
                ServiceInstance best = instances.stream()
                    .min(Comparator.comparingInt(i -> 
                        activeCount.getOrDefault(i.getInstanceId(), new AtomicInteger(0)).get()))
                    .orElse(instances.get(0));
                
                activeCount.computeIfAbsent(best.getInstanceId(), 
                    k -> new AtomicInteger(0)).incrementAndGet();
                return new DefaultResponse(best);
            });
    }
}
```

**适用：** 长连接 / WebSocket / 慢请求。

## 🎯 实战：综合策略

```java
// 综合策略：优先机房 + 加权 + 响应时间
public class SmartLoadBalancer implements ReactorLoadBalancer<ServiceInstance> {
    
    @Override
    public Mono<Response<ServiceInstance>> choose(Request request) {
        // 1. 获取请求的期望机房
        String zone = request.getContext()
            .getClientRequest().getHeaders().getFirst("X-Zone");
        
        return supplier.getIfAvailable().get().next()
            .map(instances -> {
                // 2. 优先同机房
                List<ServiceInstance> sameZone = instances.stream()
                    .filter(i -> zone == null || zone.equals(
                        i.getMetadata().get("zone")))
                    .collect(Collectors.toList());
                List<ServiceInstance> candidates = sameZone.isEmpty() 
                    ? instances : sameZone;
                
                // 3. 加权随机
                List<ServiceInstance> weighted = new ArrayList<>();
                for (ServiceInstance i : candidates) {
                    int weight = Integer.parseInt(
                        i.getMetadata().getOrDefault("weight", "100"));
                    for (int n = 0; n < weight / 10; n++) {
                        weighted.add(i);
                    }
                }
                int pos = ThreadLocalRandom.current().nextInt(weighted.size());
                return new DefaultResponse(weighted.get(pos));
            });
    }
}
```

## 🛡️ 重试机制

```yaml
spring:
  cloud:
    openfeign:
      client:
        config:
          default:
            # 连接超时
            connect-timeout: 5000
            # 读取超时
            read-timeout: 5000
            # 重试
            retryer: com.example.config.CustomRetryer
```

```java
public class CustomRetryer implements Retryer {
    @Override
    public void continueOrPropagate(FeignException e) {
        // 只对连接错误重试
        if (e.status() == -1) {
            try { Thread.sleep(100); } catch (InterruptedException ignored) {}
            return;  // 重试
        }
        throw e;  // 不重试
    }
    
    @Override
    public Retryer clone() {
        return new CustomRetryer();
    }
}
```

## 📊 策略选型指南

```
机器配置相同 + 请求均匀 → 轮询
机器配置不同 → 加权轮询
请求处理时间差异大 → 响应时间
有状态服务（session） → 一致性 Hash
长连接 / WebSocket → 最少活跃数
跨机房 → 同机房优先 + 加权
```

## 🎯 总结

**核心原则：**
- ✅ 没有最好，只有最合适
- ✅ 大多数场景：轮询（默认）就够
- ✅ 机器性能差异大：加权轮询
- ✅ 有状态服务：一致性 Hash
- ✅ 长连接：最少活跃数

**实战经验：**
- ✅ 默认轮询
- ✅ 根据 Nacos 元数据做加权
- ✅ 机房 / 地域感知的就近路由
- ✅ 超时重试（避免雪崩）
- ✅ 熔断降级（Sentinel）

**下一步：** [🛡️ Spring Security 基础](/05-security/basic) — 认证与授权

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [architecture](https://java-px.bot.cd/architecture/):微服务架构
- [system-design](https://java-px.bot.cd/system-design/):系统设计
- [cloud-native](https://java-px.bot.cd/cloud-native/):Docker / K8s 落地
