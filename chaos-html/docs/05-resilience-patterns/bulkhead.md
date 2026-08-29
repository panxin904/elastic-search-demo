---
title: 舱壁与隔离
---

# 舱壁与隔离

## 隔离层级

**1. 线程池隔离**：

- 每个下游服务一个独立线程池
- payment-service 线程池满 → order-service 不受影响
- 缺点：线程上下文切换开销

**2. 信号量隔离**：

- 轻量（不切换线程）
- 仅限制并发数，不隔离线程
- 适用：纯计算型调用

**3. 进程隔离**：

- 每个下游服务独立进程（Sidecar）
- Istio / Linkerd 默认采用

**4. 集群隔离**：

- 物理集群分组（核心 / 非核心）
- 大促前把核心服务独立集群

## Resilience4j Bulkhead（线程池版）

```java
BulkheadConfig config = BulkheadConfig.custom()
    .maxConcurrentCalls(20)
    .maxWaitDuration(Duration.ofMillis(500))
    .build();

Bulkhead bulkhead = Bulkhead.of("paymentService", config);

CheckedSupplier<String> supplier = Bulkhead.decorateCheckedSupplier(bulkhead,
    () -> paymentClient.charge(orderId, amount));
```

## Sidecar 隔离（Istio）

每个 Pod 一个 Envoy Sidecar，自动隔离：

- payment-service Pod 的 Envoy 故障 → order-service 不受影响
- Envoy 资源（CPU / 内存）独立管理

**Istio 资源隔离配置**：

```yaml
apiVersion: v1
kind: Pod
metadata:
  annotations:
    sidecar.istio.io/proxyCPU: "200m"
    sidecar.istio.io/proxyMemory: "256Mi"
    sidecar.istio.io/proxyCPULimit: "500m"
    sidecar.istio.io/proxyMemoryLimit: "1Gi"
```

**Outbound 隔离**：

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: payment-service
spec:
  host: payment-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        h2UpgradePolicy: UPGRADE
        maxRequestsPerConnection: 10
```

## 数据库连接池隔离

**HikariCP 多实例**：

```java
@Bean(name = "orderDataSource")
@ConfigurationProperties("spring.datasource.order")
public DataSource orderDataSource() {
    return DataSourceBuilder.create().build();
}

@Bean(name = "paymentDataSource")
@ConfigurationProperties("spring.datasource.payment")
public DataSource paymentDataSource() {
    return DataSourceBuilder.create().build();
}
```

**配置**：

```yaml
spring:
  datasource:
    order:
      url: jdbc:mysql://order-db:3306/order
      hikari:
        maximum-pool-size: 20
    payment:
      url: jdbc:mysql://payment-db:3306/payment
      hikari:
        maximum-pool-size: 10
```

**效果**：

- 慢查询拖垮 payment 连接池 → 不影响 order
- 每个服务独立的连接池（独立资源）

## 与其他站点关系

- **design-pattern/05-architectural-patterns**：Bulkhead 模式
- **system-design/08-availability**：隔离原则
- **architecture/05-microservices**：微服务隔离


## ## 实战案例

**Hystrix 线程池隔离**：Hystrix 通过线程池隔离不同服务调用，某个服务阻塞不影响其他服务（已停止维护，但思想保留）。

**Resilience4j Bulkhead**：SemaphoreBulkhead / FixedThreadPoolBulkhead 两种隔离模式，spring-cloud-circuitbreaker 集成。

**字节跳动 Bulkhead 实践**：通过 Envoy 的 connection_limit + outlier_detection 实现连接级别的舱壁。

**美团线程池隔离**：每个下游服务独立线程池，token 服务 30 线程，订单服务 50 线程，互不干扰。


## ## 故障排查清单

1. 线程池过小 → 调整 maxThreadPoolSize
2. 隔离过度 → 资源浪费，监控利用率
3. 共享线程池 → 退化为无隔离
4. 信号量 vs 线程池 → 看是否需要超时
5. 监控不足 → 增加 bulkhead 命中率指标


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

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

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 混沌
- [observability](https://java-px.bot.cd/observability/):故障注入监控
- [system-design](https://java-px.bot.cd/system-design/):系统韧性
