---
title: Sidecar 边车模式
description: 辅助能力剥离主应用 + K8s Pod / Istio / Dapr / Envoy
---

# Sidecar 边车模式

## 核心问题

业务应用经常需要一些**与业务无关**的辅助能力：
- 日志收集
- 监控埋点
- 配置中心
- 服务发现
- 链路追踪
- 熔断限流

但把这些能力塞进主应用会导致：
1. 语言绑定（Java 应用的日志格式 vs Node 应用不同）
2. 升级困难（日志 SDK 升级需要重写业务代码）
3. 主应用膨胀（10% 业务代码 + 90% 辅助代码）
4. 团队耦合（业务团队被迫关心基础设施）

## 核心思想

把辅助能力从主应用中剥离，部署在同一个 Host / Pod 的「边车」容器 / 进程中。

**关键点**：
- 边车与主应用共享网络 / 存储 / 生命周期
- 边车与主应用通过本地 IPC 通信
- 边车可以独立升级、独立选择技术栈

## Kubernetes Pod 实战

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-sidecars
spec:
  containers:
    - name: app                          # 主应用
      image: myapp:1.0
      ports:
        - containerPort: 8080
      volumeMounts:
        - name: logs
          mountPath: /var/log/app

    - name: fluent-bit                   # 边车 1：日志收集
      image: fluent-bit:2.0
      volumeMounts:
        - name: logs
          mountPath: /var/log/app  # 共享日志目录

    - name: istio-proxy                  # 边车 2：服务网格数据面
      image: istio/proxyv2:1.20.0

    - name: prometheus-exporter          # 边车 3：指标导出
      image: prom/node-exporter:1.5
      ports:
        - containerPort: 9100

  volumes:
    - name: logs
      emptyDir: {}  # Pod 共享存储
```

四个容器：
- **app**：业务应用
- **fluent-bit**：收集 app 日志并发送到 ES
- **istio-proxy**：拦截网络流量，提供熔断 / 链路追踪
- **prometheus-exporter**：暴露指标给 Prometheus

## 服务网格 Istio

Istio 数据面就是经典的 Sidecar：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  template:
    metadata:
      labels:
        app: order-service
        # 关键：注入 Istio sidecar
    spec:
      containers:
        - name: order-service
          image: order-service:1.0
        # istio-proxy 自动注入：
        # - name: istio-proxy
        #   image: docker.io/istio/proxyv2:1.20.0
```

Istio sidecar 提供：
- **流量管理**：负载均衡 / 熔断 / 重试
- **安全**：mTLS 加密
- **可观测性**：自动埋点 / 链路追踪
- **策略**：限流 / 黑白名单

业务应用零修改，所有这些能力由 sidecar 提供。

## Dapr（分布式应用运行时）

Dapr 是 Sidecar 模式的另一个典范：

```yaml
# Kubernetes 部署
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  template:
    spec:
      containers:
        - name: order-service
          image: order-service:1.0
          env:
            - name: DAPR_HTTP_PORT
              value: "3500"
        - name: daprd
          image: daprio/daprd:1.10
          args:
            - "--app-id=order-service"
            - "--components-path=/components"
```

```typescript
// 业务应用通过 Dapr sidecar 调用
import { DaprClient } from '@dapr/dapr';

const client = new DaprClient();

// 调用其他服务（不直接 HTTP，交给 Dapr）
await client.invoker.invoke('payment-service', 'charge', { amount: 100 });

// 发布订阅
await client.pubsub.publish('order-events', { orderId: '123' });

// 状态存储
await client.state.save('statestore', [{ key: 'order-123', value: order }]);

// 密钥管理
const secret = await client.secret.get('vault', 'api-key');
```

Dapr 把分布式能力（服务调用 / 状态 / 事件 / 配置）封装成 sidecar，业务应用通过 HTTP / gRPC 调用 sidecar。

## Envoy 边缘代理

Envoy 是 Sidecar 模式的另一个核心实现：

```yaml
# Envoy 作为 sidecar 代理
static_resources:
  listeners:
    - name: listener_0
      address:
        socket_address:
          address: 0.0.0.0
          port_value: 8080  # 拦截主应用的所有出口流量
      filter_chains:
        - filters:
            - name: envoy.filters.network.http_connection_manager
              typed_config:
                route_config:
                  virtual_hosts:
                    - domains: ['*']
                      routes:
                        - match: { prefix: '/' }
                          route: { cluster: main_app }
  clusters:
    - name: main_app
      connect_timeout: 1s
      type: STATIC
      load_assignment:
        cluster_name: main_app
        endpoints:
          - lb_endpoints:
              - endpoint:
                  address: { socket_address: { address: 127.0.0.1, port_value: 9090 } }
```

Envoy sidecar 提供：
- HTTP/2 / gRPC 代理
- 熔断 / 重试 / 超时
- 负载均衡
- 指标 / 日志 / 追踪

## 适用边界

✅ **使用场景**：
- 多语言微服务（避免每个语言重写日志/监控/追踪）
- 辅助能力统一（Istio / Dapr 等基础设施）
- 升级解耦（业务应用不用随基础设施升级）
- 安全合规（统一加密 / 认证）

❌ **避免场景**：
- 性能极敏感（sidecar 有 IPC 开销）
- 单体应用（不需要拆）
- 边车能力极简（直接放主应用更简单）

🔄 **演进路径**：
- 单体应用 → 微服务
- 业务代码内置辅助能力 → SDK → Sidecar
- 自研 Sidecar → 用现成 Istio / Dapr

💡 **最佳实践**：
- Sidecar 应该是无状态的（容易扩缩）
- Sidecar 失败不应影响主应用（要 try-catch）
- 不要让 Sidecar 持有业务状态（违反职责）
- 用 K8s operator 自动注入 sidecar（避免每个 deployment 手动加）
