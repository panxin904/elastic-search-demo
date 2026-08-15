---
title: Service Mesh
---
# Service Mesh（服务网格）

## 1. 解决的问题

```
微服务通信难题：
  - 服务发现：客户端硬编码
  - 负载均衡：每种语言实现一遍
  - 熔断 / 重试 / 限流：代码里写
  - 可观测：tracing/metrics/logs 散落
  - mTLS：每语言实现证书管理
  - 多语言：Java/Go/Node/Rust 重复造轮子

Service Mesh = 把这些"基础设施"从应用剥离到 Sidecar
  应用只管业务逻辑
  Sidecar (Envoy) 处理所有网络通信
```

## 2. 架构

```
┌─ Service A Pod ─┐         ┌─ Service B Pod ─┐
│  App container  │         │  App container  │
│  + Sidecar     │ ──TLS── │  + Sidecar     │
│    (Envoy)      │         │    (Envoy)      │
└────────────────┘         └────────────────┘
         ↑                           ↑
         └─────── Control Plane ──────┘
              (Istio / Linkerd)
              - 配置分发
              - 证书管理
              - 流量控制
              - 可观测数据收集
```

## 3. 核心能力

| 能力 | 说明 |
|------|------|
| **服务发现** | Sidecar 自动注册 + DNS |
| **负载均衡** | 多种算法（轮询 / 最少连接 / 一致性 hash） |
| **熔断** | Sidecar 层自动熔断（不用改应用） |
| **重试 / 超时** | 配置即可 |
| **mTLS** | Sidecar 自动证书管理 + 加密 |
| **流量管理** | 灰度 / 蓝绿 / 流量切分 |
| **可观测** | 自动 trace / metrics |
| **策略** | RBAC / 黑白名单 |

## 4. 主流方案

| | Istio | Linkerd | Consul Connect | Traefik Mesh |
|--|-------|---------|-----------------|--------------|
| 数据面 | Envoy (C++) | linkerd2-proxy (Rust) | Envoy | Traefik |
| 控制面 | istiod | linkerd-controller | Consul | Traefik |
| 性能 | 中 | **高**（轻量） | 中 | 高 |
| 生态 | **大** | 较新 | 中 | 小 |
| 学习曲线 | 陡 | 平 | 平 | 平 |
| 适合 | 复杂 | 简单 | 已有 Consul | 边缘 |

## 5. Istio 实战

### 安装

```bash
# demo profile
istioctl install --set profile=demo

# 生产 profile
istioctl install --set profile=production
```

### Sidecar 注入

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  annotations:
    sidecar.istio.io/inject: "true"   # 自动注入
spec:
  ...
```

### 流量管理（VirtualService）

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: myapp
spec:
  hosts: [myapp]
  http:
  - match:
    - headers:
        x-user-type:
          exact: vip
    route:
    - destination:
        host: myapp-v2
  - route:
    - destination:
        host: myapp-v1
```

### 熔断

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: myapp
spec:
  host: myapp
  trafficPolicy:
    connectionPool:
      http:
        h2UpgradePolicy: UPGRADE
        maxRequestsPerConnection: 100
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
```

## 6. Linkerd 实战（更轻）

```bash
# 安装
curl -fsL https://run.linkerd.io/install | sh

# 注入
kubectl get deploy myapp -o yaml | linkerd inject - | kubectl apply -f -
```

```yaml
# 自动注入：annotation
metadata:
  annotations:
    linkerd.io/inject: enabled
```

## 7. Sidecar 模式 vs SDK 模式

| | Sidecar (Istio/Linkerd) | SDK (Spring Cloud / Dubbo) |
|--|------------------------|-----------------------------|
| 部署 | 透明（注入） | 应用需集成 SDK |
| 跨语言 | ✅ | ❌ 需每语言 SDK |
| 性能 | +1 hop（~0.5ms） | 0 |
| 资源 | +50MB/pod（sidecar） | 0 |
| 维护 | 集中控制面 | 各服务自己升级 |
| 适用 | 多语言 | 单语言 + 极致性能 |

## 8. Service Mesh 选型

| 场景 | 选 |
|------|-----|
| 多语言 + 大规模 | Istio |
| 简单 + 轻量 | Linkerd |
| 已有 Consul | Consul Connect |
| 边缘 / K3s | Traefik Mesh |
| 单语言 + 已有 SDK | 继续用 SDK |

## 9. 实战：渐进引入

```
阶段 1：sidecar 注入 + mTLS（立即安全收益）
阶段 2：流量管理（灰度 / 蓝绿）
阶段 3：可观测（trace / metrics 接入）
阶段 4：熔断 / 重试
阶段 5：策略（authz / 限流）
```

**不要一上来就全功能**，按需引入。

## 10. 实战：监控 + 可观测

Mesh 自动提供：
- **Distributed Tracing**：Jaeger / Zipkin
- **Metrics**：Prometheus（自动 export）
- **Service Graph**：Kiali

```bash
# Istio: 启用 Kiali dashboard
istioctl dashboard kiali
```

## 🔗 下一步
- [Sidecar 模式](/12-microservice-patterns/sidecar)
- [Saga / Bulkhead](/12-microservice-patterns/saga)
- [可观测](/13-observability/three-pillars)
