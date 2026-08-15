---
title: Service 三种类型
---

# Service - Pod 集合的稳定入口

> Pod 不稳定（会换 Node / 重建 IP 变）。Service = Pod 集合的"固定 IP"。

## 🤔 为什么需要 Service

```
Pod IP 变来变去（滚动升级 / 节点故障 / 扩缩）
客户端需要"固定地址" → Service

Service 不会随 Pod 重建而变化
背后是 kube-proxy 在 Node 上用 iptables / IPVS 转发
```

## 📜 基础 manifest

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector:
    app: web                  # 匹配 Pod 标签
  ports:
  - port: 80                  # Service 暴露端口
    targetPort: 8080          # Pod 容器端口
    protocol: TCP
    name: http
  type: ClusterIP            # 默认
```

## 🎯 三种类型

### 1. ClusterIP（默认 — 仅集群内）

```yaml
spec:
  type: ClusterIP
  # 分配一个虚拟 IP（只在 cluster 内可达）
```

适合：集群内服务间调用（API → DB）。

### 2. NodePort（每 Node 暴露端口）

```yaml
spec:
  type: NodePort
  ports:
  - port: 80
    targetPort: 8080
    nodePort: 30080          # 范围 30000-32767
```

- 主机 30080 端口 → 转发到 Pod 8080
- 通过 `任意NodeIP:30080` 访问
- 适合：开发 / 演示 / 简单公网访问

### 3. LoadBalancer（云厂商 LB）

```yaml
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8080
```

- 自动创建云 LB（AWS ELB / GCP LB / 阿里 SLB）
- 适合：生产公网访问

## 🧠 Headless Service（StatefulSet 用）

```yaml
apiVersion: v1
kind: Service
metadata:
  name: db
spec:
  clusterIP: None               # headless
  selector:
    app: db
```

无 clusterIP — DNS 直接解析到每个 Pod IP（StatefulSet 必须）。

## 🧩 Endpoints

```bash
# 看 Service 后面哪些 Pod
kubectl get endpoints web
# NAME   ENDPOINTS
# web    10.244.1.5:8080,10.244.1.6:8080,10.244.1.7:8080

# 详细
kubectl describe endpoints web
```

## 🔀 流量策略

```yaml
spec:
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 8080

  # 会话保持
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800      # 3 小时

  # 外部流量策略（k8s 1.22+）
  internalTrafficPolicy: Cluster  # Cluster / Local / Local
  externalTrafficPolicy: Local    # NodePort / LB 流量要不要转发到其他 Node
```

## 🌐 DNS 解析

```
service.namespace.svc.cluster.local
  └─       └──┬──┘  └────┬───┘
       namespace   cluster

示例：web.default.svc.cluster.local
```

短名（默认 ns 内）：`web`

```bash
# 容器内测试
kubectl exec -it <pod> -- nslookup web
kubectl run -it --rm debug --image=alpine --restart=Never -- nslookup web
```

## 🔧 端口转发（本地调试）

```bash
# 转发到本地
kubectl port-forward svc/web 8080:80
# 本地访问 localhost:8080

# 转发 Pod
kubectl port-forward pod/web 8080:8080

# 监听所有接口
kubectl port-forward --address 0.0.0.0 svc/web 8080:80
```

## 🛠 实战

```bash
# 创建
kubectl expose deploy web --port=80 --target-port=8080
# 或写 yaml

# 看
kubectl get svc
kubectl get endpoints web

# 测
kubectl run -it --rm debug --image=alpine --restart=Never -- wget -O- http://web

# 删
kubectl delete svc web
```

## 🆚 vs Ingress

| | Service | Ingress |
|--|---------|----------|
| 层级 | 4 层（TCP / UDP） | 7 层（HTTP / HTTPS） |
| 路由 | 端口 / IP | 域名 / 路径 / 头 |
| TLS | 自己处理 | 自己处理 |
| 适合 | 内部互通 | 外部 HTTP 入口 |

详见 [Ingress 入口](/04-k8s-service/ingress)。

## 🔗 下一步

- [Ingress 入口](/04-k8s-service/ingress)
- [NetworkPolicy](/04-k8s-service/network-policy)
- [Deployment](/03-k8s-workload/deployment)