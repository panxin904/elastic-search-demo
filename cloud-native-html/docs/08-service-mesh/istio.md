---
title: Istio 核心
date: 2026-08-15  # date-auto-injected
---

# Istio 核心

> Istio = 主流 **Service Mesh** 实现。把服务间通讯（流量 / 安全 / 可观测）从应用层抽到基础设施层。

## 🤔 为什么需要 Service Mesh

```
微服务多了：
  ❌ 每个服务都要做：服务发现 / 负载均衡 / 熔断 / 重试 / TLS / 监控 / 灰度
  ❌ 不同语言都得实现一遍
  ❌ 业务代码被"基础设施"污染

Service Mesh：
  ✅ 边车代理（sidecar）统一接管流量
  ✅ 业务代码 0 改动获得这些能力
  ✅ 跨语言一致
  ✅ 控制面统一配置
```

## 🏗️ 架构

```
[Service A]  ──► [Envoy Sidecar]  ──►  [Envoy Sidecar]  ──►  [Service B]
                  (数据面)               (数据面)              (业务容器)
                       ▲                    ▲
                       └──────────┬─────────┘
                                  │ xDS
                              [istiod]           ←─── [kubectl apply]
                              (控制面)              (Operator)
```

| 组件 | 作用 |
|------|------|
| **Envoy (Sidecar)** | 数据面：拦截所有进出流量 |
| **istiod** | 控制面：配置分发 / 证书 / 服务发现 |

每个 Pod 注入 1 个 Envoy 容器（在原 Pod 内），与业务容器共享网络 namespace。

## 🚀 安装

### 生产（Helm）

```bash
helm repo add istio https://istio-release.storage.googleapis.com/charts
helm repo update

# 用 profile 装（demo / default / 生产）
helm install istio-base istio/base -n istio-system --create-namespace
helm install istiod istio/istiod -n istio-system --wait
helm install istio-ingress istio/gateway -n istio-system

# Demo profile
istioctl install --set profile=demo -y
```

### Demo（快速验证）

```bash
# 下载 istioctl
curl -L https://istio.io/downloadIstio | sh -
cd istio-*/
export PATH=$PWD/bin:$PATH

istioctl install --set profile=demo -y
kubectl label namespace default istio-injection=enabled
```

## 🧪 部署一个示例应用

```bash
# Bookinfo 示例
kubectl apply -f samples/bookinfo/platform/kube/bookinfo.yaml
kubectl apply -f samples/bookinfo/networking/bookinfo-gateway.yaml

# 访问
kubectl get svc istio-ingressgateway -n istio-system
# INGRESS_PORT=80 → localhost

# 浏览器
http://localhost/productpage
```

## 🎛 Sidecar 注入

```bash
# 整 ns 注入
kubectl label namespace default istio-injection=enabled

# 单 pod 注入
kubectl annotate pod myapp-xxx sidecar.istio.io/inject=true

# 卸载
kubectl label namespace default istio-injection-
```

## 🔄 流量管理

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
  - reviews
  http:
  - match:
    - headers:
        end-user:
          exact: jason
    route:
    - destination:
        host: reviews
        subset: v2            # 灰度：jason 看 v2
  - route:
    - destination:
        host: reviews
        subset: v1            # 其他用户看 v1
```

```yaml
# 流量切分（90/10 灰度）
- route:
  - destination: { host: reviews, subset: v1 }
    weight: 90
  - destination: { host: reviews, subset: v2 }
    weight: 10
```

详见 [流量管理](/08-service-mesh/traffic)。

## 🔐 mTLS

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT              # 所有 pod 间必须 mTLS
```

应用代码无感，自动加密。

## 📊 可观测

注入 sidecar 后，**自动**获得：

- 流量指标（QPS / 延迟 / 错误率） → Prometheus
- 链路追踪（Jaeger / Zipkin）→ 请求路径
- 访问日志 → stdout（用 Loki 收）

```bash
# 配 Jaeger
kubectl apply -f samples/addons/jaeger.yaml
```

## 🆚 vs 其他

| 工具 | 风格 |
|------|------|
| **Istio** | 功能最全，生态最大 |
| Linkerd | 轻量，Rust 写的 Proxy |
| Consul Connect | HashiCorp 系 |
| Kuma | 跨 mesh / VM + k8s |

## 🛠 实战

```bash
# 装 + 启 demo
istioctl install --set profile=demo -y
kubectl label namespace default istio-injection=enabled
kubectl apply -f samples/bookinfo/platform/kube/bookinfo.yaml
kubectl apply -f samples/bookinfo/networking/bookinfo-gateway.yaml

# 看 sidecar
kubectl get pod -l app=ratings -o jsonpath='{.items[0].spec.containers[*].name}'
# ratings istio-proxy         ← sidecar

# 流量切分
kubectl apply -f samples/bookinfo/networking/virtual-service-reviews-80-20.yaml

# 卸载
istioctl uninstall -y
```

## 🔗 下一步

- [Sidecar 模式](/08-service-mesh/sidecar)
- [流量管理](/08-service-mesh/traffic)
- [k8s Service](/04-k8s-service/service)
- [Ingress](/04-k8s-service/ingress)