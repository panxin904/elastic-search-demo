---
title: 微服务网络
---

# 微服务网络

<div class="nt-badge nt-badge-cases">企业案例</div>
<div class="nt-badge nt-badge-cloud">微服务</div>

微服务架构中，服务间通信、流量治理、可观测性是网络层的核心挑战。本章梳理典型方案与落地。

## 1. 微服务通信模式

| 模式 | 协议 | 适用 |
| --- | --- | --- |
| 同步 RPC | gRPC / Thrift | 高频内部调用 |
| 异步消息 | Kafka / RabbitMQ | 解耦、削峰 |
| REST | HTTP | 跨语言、外部 |
| GraphQL | HTTP | 前端聚合 |
| 事件流 | Pulsar / Kafka | 实时 |

## 2. 服务发现

```
服务 A → DNS / Registry → 服务 B 地址
```

| 方案 | 特点 |
| --- | --- |
| K8s DNS | 原生、CoreDNS |
| Consul | 健康检查 + KV |
| Nacos | 阿里、配置 + 注册 |
| Eureka | Netflix、AP |
| Etcd | 强一致 |

## 3. 负载均衡

| 层 | 工具 |
| --- | --- |
| 客户端 | Ribbon、gRPC LB |
| 边缘 | Nginx、Envoy、ALB |
| K8s Service | ClusterIP / NodePort / LoadBalancer |
| Ingress | Nginx Ingress / Traefik / Istio |

## 4. 流量治理

| 能力 | 工具 |
| --- | --- |
| 灰度发布 | Istio / Spring Cloud Gateway |
| 限流 | Sentinel / Envoy |
| 熔断 | Resilience4j / Hystrix（已停维） |
| 重试 | Failsafe / Istio |
| 鉴权 | OAuth2 / mTLS |
| 超时 | Istio / Ribbon |

## 5. Service Mesh 落地

```yaml
# Istio VirtualService 灰度
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: user-service
spec:
  hosts:
  - user-service
  http:
  - match:
    - headers:
        x-user-tag:
          exact: beta
    route:
    - destination:
        host: user-service
        subset: v2
      weight: 100
  - route:
    - destination:
        host: user-service
        subset: v1
      weight: 90
    - destination:
        host: user-service
        subset: v2
      weight: 10
```

## 6. 分布式追踪

```
Trace → Span → Span → Span
  ↓
Jaeger / Zipkin / SkyWalking
```

自动注入：

```yaml
env:
- name: JAEGER_AGENT_HOST
  value: jaeger.observability.svc.cluster.local
- name: JAEGER_AGENT_PORT
  value: "6831"
```

## 7. 跨域与 API Gateway

```
Client → API Gateway → Microservice
                  ↑
          鉴权 / 限流 / 灰度
```

| 网关 | 特点 |
| --- | --- |
| Kong | Lua 插件 |
| APISIX | 高性能 |
| Envoy | 服务网格入口 |
| Spring Cloud Gateway | Java |
| Zuul | Netflix（已停维） |

## 8. 多集群网络

```
Cluster-A (Region1) ←→ Cluster-B (Region2)
        ↕                  ↕
       ALB                ALB
        ↕                  ↕
      Envoy               Envoy
```

| 方案 | 特点 |
| --- | --- |
| Submariner | 多集群 Pod 互联 |
| Istio Multi-Primary | 多控制面 |
| Skupper | 应用层网络 |
| Linkerd Multi-cluster | 简化 |

## 9. 可观测性

| 维度 | 工具 |
| --- | --- |
| Metrics | Prometheus + Grafana |
| Logs | Loki / EFK |
| Traces | Jaeger / SkyWalking / Tempo |
| Topology | Kiali / Service Catalog |

## 10. 故障案例

### 案例 1：雪崩

```
服务 A 慢 → 调用 B 慢 → 线程池满 → A 拒绝服务 → 全链路
```

解法：
- 熔断
- 限流
- 超时
- 隔离（bulkhead）
- 降级

### 案例 2：循环调用

```
A → B → A → B → ...
```

解法：
- 调用链监控
- 跳数限制
- 重试策略（避免同步重试）

### 案例 3：跨地域延迟

解法：
- 同 Region 调用
- 异步消息
- 数据就近

## 11. 落地清单

```
[ ] 服务发现
[ ] 负载均衡
[ ] 灰度发布
[ ] 限流熔断
[ ] mTLS
[ ] 链路追踪
[ ] 统一日志
[ ] 监控告警
[ ] 多集群容灾
[ ] 文档
```

## 12. 常见面试题

1. **微服务通信怎么选？** 内部 gRPC，外部 REST，异步消息。
2. **服务发现怎么实现？** K8s DNS / Nacos / Consul。
3. **灰度发布怎么做？** Gateway + Header / Cookie / 权重。
4. **如何避免雪崩？** 熔断 / 限流 / 隔离 / 超时 / 降级。
5. **mTLS 价值？** 服务间零信任，无需业务改代码。
6. **可观测性三大支柱？** Metrics + Logs + Traces。


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
