---
title: Ingress 入口
date: 2026-08-15  # date-auto-injected
---

# Ingress - 七层 HTTP 入口

> Ingress = 集群对外的 HTTP / HTTPS 网关。Service 是 4 层，Ingress 是 7 层（懂 HTTP 头 / 路径 / 主机名）。

## 🤔 为什么需要 Ingress

```
没有 Ingress：
  - 每个服务开 NodePort / LoadBalancer → 贵 / 散
  - 没域名路由 / TLS 终止

Ingress：
  - 一个入口（一个 LB） → 路由多个服务
  - 域名 / 路径 / 头路由
  - 集中 TLS
```

## 🏗️ 架构

```
客户端
  ↓ (HTTPS)
[Cloud LB / NodePort]
  ↓
[Ingress Controller]   ← 需要部署（nginx / traefik / HAProxy）
  ↓
[Ingress 资源]         ← 路由规则
  ↓
[Service] → [Pod]
```

**关键**：Ingress = 资源对象 + 控制器实现。要装一个 Ingress Controller（k8s 自带不包含）。

## 🚀 主流 Ingress Controller

| Controller | 特点 |
|------------|------|
| **nginx-ingress** | 最常用，k8s 官方 |
| **Traefik** | 自动服务发现，配置简单 |
| **HAProxy** | 高性能 |
| **Contour** | Envoy-based，Gateway API 友好 |
| **APISIX** | Apache 出品，国产友好 |
| **Kong** | 商业版，插件丰富 |

## 📜 基础 manifest

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx              # 选哪个 controller
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api
            port:
              number: 80
      - path: /web
        pathType: Prefix
        backend:
          service:
            name: web
            port:
              number: 80
  tls:
  - hosts:
    - app.example.com
    secretName: app-tls-secret
```

| 字段 | 含义 |
|------|------|
| `ingressClassName` | 用哪个 controller |
| `rules[].host` | 域名（vhost） |
| `rules[].http.paths[].path` | URL 路径 |
| `pathType` | Prefix / Exact / ImplementationSpecific |
| `backend.service` | 路由到的 Service |
| `tls[].secretName` | TLS 证书（Secret） |

## 🔐 TLS 证书

```bash
# 用 cert-manager（自动）
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: app-tls
  namespace: default
spec:
  secretName: app-tls-secret
  dnsNames:
  - app.example.com
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
EOF
```

或者手工：
```bash
openssl req -x509 -nodes -newkey rsa:2048 \
  -keyout tls.key -out tls.crt \
  -subj "/CN=app.example.com"

kubectl create secret tls app-tls-secret \
  --cert=tls.crt --key=tls.key
```

## 🩹 故障

```bash
# 502 Bad Gateway
# 1. 看 ingress controller 日志
kubectl -n ingress-nginx logs deploy/ingress-nginx-controller
# 常见：backend service 没端口 / Pod 不 ready

# 2. 看 Service Endpoints
kubectl get endpoints <svc>
# 为空 → selector 错 / Pod 标签错

# 3. 看 ingress 事件
kubectl describe ingress web
# Events 显示 sync 成功 / 失败

# 域名不解析
# 检查 DNS 指向 LB 外部 IP
nslookup app.example.com
```

## 🪜 实战：nginx-ingress 部署

```bash
# 装 helm
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# 装（bare metal：NodePort / 内部 IP）
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace \
  --set controller.service.type=NodePort

# 装（云：LoadBalancer）
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace \
  --set controller.service.type=LoadBalancer
```

## 🆚 Ingress vs Gateway API

| | Ingress | Gateway API |
|--|---------|-------------|
| 状态 | v1（稳定） | v1.0+（GA 2024） |
| 跨厂商 | 各 controller 自定义 annotation | 标准化 CRD |
| 多协议 | 仅 HTTP | HTTP / TCP / UDP |
| 角色分离 | ❌ | ✅ GatewayClass / Gateway / Route |
| 未来 | 维护模式 | 长期方向 |

生产新项目建议直接 Gateway API。

## 🔗 下一步

- [Service 三种类型](/04-k8s-service/service)
- [NetworkPolicy](/04-k8s-service/network-policy)
- [Helm Chart](/06-helm/chart)