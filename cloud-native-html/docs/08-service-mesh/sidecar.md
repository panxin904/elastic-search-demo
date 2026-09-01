---
title: Sidecar 模式
date: 2026-08-15  # date-auto-injected
---

![Service Mesh Sidecar 模式](/servicemesh-sidecar-pattern.svg)

# Sidecar 模式

> Sidecar = 把"基础设施"放进业务 Pod 的"副驾"，让业务代码 0 改动获得各种能力。

## 🤔 Sidecar 模式

```
传统：
  [Service]  ── 业务代码实现：TLS / 限流 / 监控 / 重试 / 路由

Sidecar 模式：
  [Service]  [Sidecar Proxy]  ──  proxy 接管所有进出流量
  业务容器    Envoy / Linkerd proxy    ↑ 业务代码 0 改动
                                  业务代码完全不知道 sidecar 存在
```

优势：
- ✅ 业务代码 0 改动
- ✅ 跨语言一致
- ✅ 基础设施升级不重启业务

## 🧬 Istio 数据面

每个 Pod 注入 1 个 Envoy sidecar（用 initContainer 把流量劫持到 Envoy）：

```
Pod
├── containers:
│   ├── app (业务)
│   └── istio-proxy (Envoy)        ← sidecar
└── initContainers:
    └── istio-init                  ← 改 iptables 把流量劫到 15001 (out) / 15006 (in)
```

### iptables 劫持

```bash
# pod 内部 iptables
# 所有 OUTBOUND 流量 → 15001 (Envoy 出口)
# 所有 INBOUND 流量 → 15006 (Envoy 入口)

# Envoy 收到后根据 xDS 配置决定：
# - 路由（哪个服务）
# - 熔断 / 重试
# - 限流
# - mTLS 加密
# - 上报 metrics / trace / log
```

## 🛠 Envoy 配置下发 (xDS)

```
istiod ── xDS ──► Envoy (sidecar)
        │ CDS - cluster
        │ EDS - endpoint
        │ LDS - listener
        │ RDS - route
        │ SDS - secret
```

**好处**：配置变化（路由 / 限流）实时下发，业务 Pod 不用重启。

## 🪛 实战

### 1. Sidecar 注入

```bash
# 整 namespace 注入
kubectl label namespace default istio-injection=enabled

# 注入示例
kubectl rollout restart deploy/myapp -n default
# Pod 重启后会带 sidecar

# 看
kubectl get pod myapp-xxx -o jsonpath='{.spec.containers[*].name}'
# app istio-proxy            ← 业务 + sidecar
```

### 2. sidecar 资源控制

```yaml
apiVersion: networking.istio.io/v1beta1
kind: Sidecar
metadata:
  name: myapp
  namespace: default
spec:
  outboundTrafficPolicy:
    mode: REGISTRY_ONLY          # 只允许 registry 中的服务
  ingress:
  - port:
      number: 8080
      protocol: HTTP
      name: http
    defaultEndpoint: 127.0.0.1:8080
```

控制 sidecar 的资源占用 / 监听范围。

### 3. 限制 sidecar CPU

```yaml
# pod template
spec:
  containers:
  - name: istio-proxy
    resources:
      requests:
        cpu: 100m
        memory: 128Mi
      limits:
        cpu: 500m
        memory: 256Mi
```

```bash
# 装时全局限制
istioctl install --set values.global.proxy.resources.requests.cpu=100m
```

## 🔄 流量劫持细节

```
业务容器发送：app → db:5432
  ↓ 容器内 iptables OUTPUT 链拦截
  ↓ 转到 host 上的 Envoy 15001
  ↓ Envoy 根据 EDS 找到 db 的所有 endpoint
  ↓ 选择一个（负载均衡）
  ↓ 通过新连接发到 db pod
```

```
返回：db → app
  ↓ db pod 的 Envoy 15006 收到
  ↓ 转发给业务容器 127.0.0.1:5432
```

业务代码完全不知道有 proxy。

## 🩹 故障

```bash
# 注入后启动变慢（每次请求多一跳）
# 解决：升级硬件 / 限制 sidecar 资源

# 连接耗尽
ss -s
# 解决：sidecar 资源调大 / 调 connection pool

# DNS 解析慢
# 解决：调 sidecar dns refresh rate
```

## 🆚 各种 sidecar 模式

| 模式 | 优 | 缺 |
|------|---|---|
| **Per-pod sidecar** (Istio) | 隔离 / 弹性 | 资源多 1 倍 |
| **Per-node sidecar** (Linkerd / 实验) | 省资源 | 节点挂了所有 pod 受影响 |
| **Ambient Mesh** (Istio 新) | 不需要 sidecar，ztunnel 在节点 | 早期功能，兼容性待验证 |

## 🪛 ambient mesh（未来）

```bash
# 不再注入 Envoy 到每个 Pod
istioctl install --set profile=ambient
# 节点级 ztunnel + 命名空间级 waypoint
```

减少资源占用，简化运维。

## 🔗 下一步

- [Istio 核心](/08-service-mesh/istio)
- [流量管理](/08-service-mesh/traffic)
- [Service 三种类型](/04-k8s-service/service)