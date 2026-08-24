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
  replicas: 3                    # 副本数
  selector:
    matchLabels:
      app: web                    # 必填，找 Pod 用
  
  strategy:
    type: RollingUpdate           # 默认
    rollingUpdate:
      maxSurge: 1                 # 最多超出 replicas 1 个
      maxUnavailable: 0           # 最多同时 0 个不可用
  
  template:
    metadata:
      labels:
        app: web                  # 必填：和 selector 对应
    spec:
      # 节点选择
      nodeSelector:
        disktype: ssd
      
      # 容器
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
  # 全部杀掉再起新
```

适合：单实例 / 不能双版本共存（如 DB schema 不兼容）。

## 🛠 升级 / 回滚

```bash
# 看当前
kubectl get deploy
kubectl rollout status deploy/web

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

# 状态
kubectl rollout status deploy/web
# deployment "web" successfully rolled out

# 暂停（灰度回滚 / debug 阶段用）
kubectl rollout pause deploy/web

# 继续
kubectl rollout resume deploy/web

# 回滚到上一版
kubectl rollout undo deploy/web

# 回滚到指定版
kubectl rollout undo deploy/web --to-revision=2
```

## 🔄 副本管理

```bash
# 手动
kubectl scale deploy/web --replicas=10

# 自动（HPA - Horizontal Pod Autoscaler）
kubectl autoscale deploy/web --min=2 --max=20 --cpu-percent=70

# 看 HPA
kubectl get hpa
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

```bash
# 升级时：新建 ReplicaSet → 旧 RS 副本数渐 0
kubectl get rs
# NAME                DESIRED  CURRENT  READY  AGE
# web-7c8d9f8b6c       3        3        3      5m
# web-6b4d8f7c5b       0        0        0      30m   ← 旧的
```

## 🩹 故障

```bash
# 升级卡住
kubectl rollout status deploy/web --timeout=60s
# 可能是新 Pod 健康检查不过

# 看哪些 pod 错
kubectl get pods -l app=web
kubectl describe pod <failing-pod>

# ImagePull 错
kubectl set image deploy/web web=myapp:1.0  # 改回旧版
kubectl rollout undo deploy/web

# 资源不够
kubectl describe pod <pending-pod>
# Events: FailedScheduling, 0/3 nodes are available
```

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

- Pod 最小单元
- StatefulSet
- DaemonSet
- Job / CronJob