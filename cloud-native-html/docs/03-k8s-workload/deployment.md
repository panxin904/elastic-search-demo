---
title: Deployment
---

# Deployment - 无状态工作负载

> Deployment 是无状态 Pod 的"工厂"，管副本 + 滚动升级 + 回滚。

## 🤔 为什么用 Deployment（不直接写 Pod）

```
❌ 裸 Pod：
  - 挂了不自动重启
  - 升级要手动
  - 没法扩缩
  - 节点挂了 Pod 也丢

✅ Deployment：
  - 自动维持副本数（replicas）
  - 滚动升级 / 回滚
  - 暂停 / 恢复
  - 自动选 Node + 跨节点分散
```

## 📜 完整 manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: default
  labels:
    app: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: web
    spec:
      nodeSelector:
        disktype: ssd
      containers:
      - name: web
        image: nginx:1.25-alpine
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 256Mi
        readinessProbe:
          httpGet:
            path: /
            port: 80
        livenessProbe:
          httpGet:
            path: /
            port: 80
        volumeMounts:
        - name: data
          mountPath: /usr/share/nginx/html
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: web-data
```

## 🚦 升级策略

### RollingUpdate（默认 — 零停机）

```
replicas: 3
1. 启 v2 → 总 4 个（maxSurge: 1）
2. 旧 v1 停 1 个 → 总 3 个（v2 = 2, v1 = 1）
3. 启 v2 → 总 4 个
4. 旧 v1 停 1 个 → 总 3 个
5. 全部 v2
```

### Recreate（停服升级）

```yaml
strategy:
  type: Recreate
```

适合：单实例 / 不能双版本共存。

## 🛠 升级 / 回滚

```bash
# 升级镜像
kubectl set image deploy/web web=nginx:1.27-alpine

# 改 env
kubectl set env deploy/web DEBUG=true

# 限资源
kubectl set resources deploy/web -c web --limits=cpu=1,memory=512Mi

# 历史
kubectl rollout history deploy/web
# REVISION  CHANGE-CAUSE
# 1         <none>
# 2         <none>

# 暂停
kubectl rollout pause deploy/web

# 继续
kubectl rollout resume deploy/web

# 回滚
kubectl rollout undo deploy/web
kubectl rollout undo deploy/web --to-revision=2
```

## 🔄 副本管理

```bash
# 手动
kubectl scale deploy/web --replicas=10

# 自动（HPA - Horizontal Pod Autoscaler）
kubectl autoscale deploy/web --min=2 --max=20 --cpu-percent=70
```

详见 `horizontalpodautoscaler`（CKA 常考）。

## 🧬 Deployment 与 ReplicaSet / Pod 关系

```
Deployment
    │
    └─ ReplicaSet (自动创建)
            │
            └─ Pod × N
```

`kubectl get rs` 列出 ReplicaSet（每个 revision 一个）。

## 🛠 实战

```bash
# 部署
kubectl apply -f deploy.yaml

# 状态
kubectl get deploy
kubectl get pods -l app=web
kubectl get rs

# 升级
kubectl set image deploy/web web=nginx:1.27
kubectl rollout status deploy/web

# 扩缩
kubectl scale deploy/web --replicas=5

# 回滚
kubectl rollout undo deploy/web
```

## 🔗 下一步

- [Pod 最小单元](/03-k8s-workload/pod)
- [StatefulSet](/03-k8s-workload/statefulset)
- [DaemonSet](/03-k8s-workload/daemonset)