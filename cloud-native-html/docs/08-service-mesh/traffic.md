---
title: 流量管理
date: 2026-08-15  # date-auto-injected
---

# Istio 流量管理

> 蓝绿 / 金丝雀 / A/B 测试 / 熔断 — 不用改应用代码，纯声明式配置。

## 🤔 业务场景

```
新版本上线：
  ❌ 停机部署
  ❌ 一次性切（风险大）
  ❌ 回滚慢

Istio 流量管理：
  ✅ 灰度（1% → 10% → 50% → 100%）
  ✅ 蓝绿（老版本 / 新版本切换）
  ✅ A/B（按用户 / header 路由）
  ✅ 熔断（自动隔离故障服务）
```

## 🧬 三大 CRD

| CRD | 作用 |
|-----|------|
| **VirtualService** | 路由规则（按 header / path / 权重） |
| **DestinationRule** | 目标规则（subset / 负载均衡 / 熔断） |
| **Gateway** | 入口网关（与 Ingress 配合） |

## 📜 灰度发布（按权重）

### 1. Deployment 多个版本

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-v1
spec:
  replicas: 9                    # 90% 流量
  selector:
    matchLabels: { app: myapp, version: v1 }
  template:
    metadata:
      labels: { app: myapp, version: v1 }
    spec:
      containers:
      - name: app
        image: myapp:1.0
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-v2
spec:
  replicas: 1                    # 10% 流量（先少量）
  selector:
    matchLabels: { app: myapp, version: v2 }
  template:
    metadata:
      labels: { app: myapp, version: v2 }
    spec:
      containers:
      - name: app
        image: myapp:2.0
```

### 2. Service 选 v1 + v2

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp                    # 选所有 version
  ports:
  - port: 80
    targetPort: 8080
```

### 3. DestinationRule 定义 subset

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: myapp
spec:
  host: myapp
  subsets:
  - name: v1
    labels: { version: v1 }
  - name: v2
    labels: { version: v2 }
```

### 4. VirtualService 切流量

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: myapp
spec:
  hosts: [myapp]
  http:
  - match:
    - uri:
        prefix: /
    route:
    - destination:
        host: myapp
        subset: v1
      weight: 90
    - destination:
        host: myapp
        subset: v2
      weight: 10
```

### 5. 调整比例

```bash
# 100% 切 v2
kubectl patch vs myapp --type merge -p '{"spec":{"http":[{"route":[{"destination":{"host":"myapp","subset":"v2"},"weight":100}]}]}}'

# 回滚
kubectl patch vs myapp --type merge -p '{"spec":{"http":[{"route":[{"destination":{"host":"myapp","subset":"v1"},"weight":100}]}]}}'
```

## 🧪 A/B 测试

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: myapp
spec:
  hosts: [myapp]
  http:
  # VIP 客户看 v2
  - match:
    - headers:
        cookie:
          regex: ".*vip=1.*"
    route:
    - destination:
        host: myapp
        subset: v2
  # 其他用户看 v1
  - route:
    - destination:
        host: myapp
        subset: v1
```

## 🔄 蓝绿

```yaml
spec:
  http:
  - route:
    - destination:
        host: myapp
        subset: v2
      # 100% 切 v2（v1 副本可随时缩到 0）
```

回滚：改 subset 到 v1 + 缩 v2 副本到 0。

## 🔌 故障注入（混沌测试）

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: myapp
spec:
  hosts: [myapp]
  http:
  - fault:
      delay:
        percentage:
          value: 50             # 50% 请求延迟
        fixedDelay: 5s          # 延迟 5 秒
    route:
    - destination: { host: myapp }
```

测："我们的应用能不能扛 5s 延迟 + 一半请求"。

```yaml
# 模拟 500 错误
- fault:
    abort:
      percentage: { value: 10 }
      httpStatus: 500
  route:
  - destination: { host: myapp }
```

## 🔁 熔断 / 连接池

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: myapp
spec:
  host: myapp
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 10
        maxRequestsPerConnection: 10
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
```

应用没动 Envoy 自动：5xx 5 次 → 标记不健康 → 30s 内不路由过去。

## 🔁 重试 / 超时

```yaml
spec:
  http:
  - timeout: 3s                   # 整体 3s 超时
    retries:
      attempts: 3                 # 重试 3 次
      perTryTimeout: 1s          # 每次 1s
      retryOn: 5xx,reset,connect-failure
    route:
    - destination: { host: myapp }
```

## 🛠 实战

```bash
# 看当前 VirtualService
kubectl get vs -A
kubectl get vs myapp -o yaml

# 切流量
kubectl edit vs myapp

# 模拟故障
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: myapp
spec:
  hosts: [myapp]
  http:
  - fault:
      delay: { fixedDelay: 5s }
    route:
    - destination: { host: myapp }
EOF

# 取消
kubectl delete vs myapp
# 或
kubectl edit vs myapp
```

## 🔗 下一步

- [Istio 核心](/08-service-mesh/istio)
- [Sidecar 模式](/08-service-mesh/sidecar)
- [Service 三种类型](/04-k8s-service/service)