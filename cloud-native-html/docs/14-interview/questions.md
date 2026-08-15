---
title: 高频面试题
---

# 高频面试题

> 真实面试 + 笔试常见题汇总。

## 🟢 Easy（基础）

### 1. Pod / Deployment / Service 关系？

```
Pod：最小调度单位（1+ 容器）
Deployment：管 N 个 Pod（Deployment → ReplicaSet → Pod × N）
Service：Pod 集合的稳定入口（IP + DNS）

Pod 不稳定（IP 变），Service 提供 ClusterIP 不变。
```

### 2. StatefulSet vs Deployment？

| | Deployment | StatefulSet |
|--|------------|--------------|
| 身份 | 随机 | 固定 ordinal |
| 存储 | 共享 | 每 Pod 独立 PVC |
| 适合 | 无状态 | DB / MQ |

### 3. 解释 k8s Service 三种类型

- **ClusterIP**（默认）：集群内
- **NodePort**：每 Node 暴露一个端口（30000-32767）
- **LoadBalancer**：云 LB（AWS ELB / GCP LB）

### 4. 解释 livenessProbe vs readinessProbe

- **livenessProbe**：失败 → 重启容器（"活没活"）
- **readinessProbe**：失败 → 移除 Service 端点（"能不能接流量"）

### 5. ConfigMap vs Secret？

- **ConfigMap**：非敏感
- **Secret**：敏感（默认 base64，加密需开）

## 🟡 Medium（实操）

### 6. 怎么把 Pod 调度到指定 Node？

```yaml
nodeSelector:
  disktype: ssd
# 或
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: disktype
          operator: In
          values: [ssd]
```

### 7. 怎么保证 Pod 不会被调度到某些 Node？

```bash
# Node 加污点
kubectl taint node1 dedicated=dev:NoSchedule

# Pod 加容忍
tolerations:
- key: dedicated
  operator: Equal
  value: dev
  effect: NoSchedule
```

### 8. 怎么从容器内部看 K8s 集群？

```bash
# 容器内有 service account token
ls /var/run/secrets/kubernetes.io/serviceaccount/
cat /var/run/secrets/kubernetes.io/serviceaccount/token
# 用 kubectl 调用 API（Image 内有）

# 短名解析（默认 ns 内）
nslookup kubernetes
nslookup kube-dns
# 跨 ns
nslookup my-service.other-ns.svc.cluster.local
```

### 9. Pod 卡 CrashLoopBackOff 怎么排？

```bash
# 1. 看上次实例日志（已崩的）
kubectl logs <pod> --previous

# 2. 看事件
kubectl describe pod <pod>
# Events: OOMKilled / Error / BackOff

# 3. 看启动命令
kubectl get pod <pod> -o yaml | grep -A 5 containers

# 4. 进 debug
kubectl debug -it <pod> --image=nicolaka/netshoot
```

### 10. K8s 怎么实现服务发现？

- **DNS**（CoreDNS）：Service 名解析
- **环境变量**：Pod 启动时注入 SERVICE_HOST / PORT
- **API**：直接调 API Server（不推荐）

## 🟠 Hard（架构 / 原理）

### 11. 解释 K8s 控制面组件

```
apiServer   ← 所有请求入口
scheduler  ← 决定 Pod 放哪
controller-manager  ← 状态控制循环
etcd       ← 状态存储

数据面：
kubelet    ← Node 代理
kube-proxy ← Service IP 转发
container runtime  ← 跑容器
```

### 12. Pod 启动过程

```
1. kubectl apply → API Server
2. etcd 存 spec
3. Controller 看到 "replicas: 3" 实际 0 → 创建 3 个 Pod 对象
4. Scheduler 看到未调度的 Pod → 选 Node
5. 目标 Node 的 kubelet 看到 → CRI 拉镜像 → 启动容器
6. kubelet 报告 Pod 状态 → etcd
7. Endpoints Controller 看到 Pod ready → 更新 Endpoints
8. kube-proxy watch 到 Endpoints 变化 → 更新 iptables / IPVS
9. Service ClusterIP 流量转发到新 Pod
```

### 13. K8s 网络模型（CNI 视角）

- Pod IP 集群内唯一
- 同 Node Pod 通过 bridge/loopback 通信
- 跨 Node Pod 通过 overlay / 路由
- Pod → Service ClusterIP 通过 iptables/IPVS DNAT
- Service → Pod 通过 iptables/IPVS 负载均衡
- 外部 → Service 通过 Ingress / NodePort / LoadBalancer

### 14. 灰度发布 / 金丝雀怎么做？

```yaml
# 1. 多 Deployment
spec:
  replicas: 9  # v1
---
spec:
  replicas: 1  # v2

# 2. DestinationRule
subsets:
- name: v1
  labels: { version: v1 }
- name: v2
  labels: { version: v2 }

# 3. VirtualService（按权重）
route:
- destination: { host: myapp, subset: v1 }
  weight: 90
- destination: { host: myapp, subset: v2 }
  weight: 10
```

或用 Argo Rollouts。

### 15. 怎么保证 K8s 高可用？

- 控制面 3+ 节点（API Server 多个，etcd 集群）
- 节点 ≥ 3（容忍 1 节点失联）
- Pod replicas ≥ 3 + PodDisruptionBudget
- 多 AZ 部署
- etcd 定期备份

## 🛠 实战（手写）

### 16. 写一个完整 Deployment + Service + Ingress

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  selector:
    matchLabels: { app: web }
  template:
    metadata:
      labels: { app: web }
    spec:
      containers:
      - name: web
        image: nginx:1.25-alpine
        ports: [{ containerPort: 80 }]
        readinessProbe:
          httpGet: { path: /, port: 80 }
---
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector: { app: web }
  ports: [{ port: 80, targetPort: 80 }]
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web
spec:
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web
            port: { number: 80 }
```

### 17. 写 NetworkPolicy 限 DB 仅 API 访问

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: db-isolation
spec:
  podSelector: { matchLabels: { app: db } }
  policyTypes: [IngressPolicy, EgressPolicy]
  ingress:
  - from:
    - podSelector: { matchLabels: { app: api } }
    ports: [{ port: 5432 }]
  egress:
  - to:
    - namespaceSelector: {}
    - podSelector: { matchLabels: { k8s-app: kube-dns } }
    ports: [{ port: 53, protocol: UDP }]
```

## 🧠 软技能 / 行为题

### 18. 生产 K8s 故障你怎么处理？

**STAR 答法**：
- **S**ituation：背景
- **T**ask：目标
- **A**ction：你怎么排查
- **R**esult：结果 / 学到什么

例子：线上服务突然 5xx 告警
- **S**：某 K8s 集群服务 QPS 下跌
- **T**：10 分钟内恢复
- **A**：describe pod → 发现 Endpoints 为空 → 查 Service selector → 发现是新加的 Pod label 没匹配 → 改 selector → 自动恢复
- **R**：引入 Pod label 自动同步检查 / CD 前预演

## 📚 准备路径

```
1. CKA 考过（基础）
2. 写 5-10 个小项目（side project）
3. 读 K8s 源码关键路径（kubelet / scheduler）
4. 刷题：
   - killer.sh
   - 真实 K8s 部署经验
5. 系统设计题：
   - 短链 / 限流 / Feed / 抢购
   - K8s + Service Mesh + 可观测
```

## 🔗 下一步

- [CKA 考试要点](/14-interview/cka)
- [CKS 安全加固](/14-interview/cks)
- [k8s 架构](/02-k8s-arch/overview)