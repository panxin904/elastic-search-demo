---
title: StatefulSet
date: 2026-08-15  # date-auto-injected
---

# StatefulSet - 有状态工作负载

> StatefulSet = 有**稳定身份** + **持久存储**的 Pod。适合 DB、MQ、ZK 等。

![K8S Statefulset](/k8s-statefulset.svg)

## 🤔 为什么需要 StatefulSet

```
Deployment 适合：
  ✅ 无状态 API
  ✅ 所有 Pod 互相等价（轮询都行）
  ✅ 随时扩缩 / 替换

数据库集群：
  ❌ 节点 0 / 1 / 2 互相不等价
  ❌ 节点 0 挂了不能"换"节点 1 顶上
  ❌ 需要稳定的网络身份（持久 hostname）
  ❌ 数据要绑定到具体节点
  ❌ 启动顺序敏感（master 先启）
```

## 🧬 StatefulSet 三大特性

1. **稳定的 hostname**：`web-0`, `web-1`, `web-2`（不变）
2. **稳定的网络身份**：headless Service（DNS 解析到具体 Pod IP）
3. **稳定的存储**：`pvcName-web-0` / `pvcName-web-1`（每个 Pod 一个 PVC）

## 📜 manifest

```yaml
apiVersion: v1
kind: Service            # headless service（必需）
metadata:
  name: db
spec:
  clusterIP: None          # headless
  selector:
    app: db
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: db
spec:
  serviceName: db          # 关联 headless service
  replicas: 3
  selector:
    matchLabels:
      app: db
  template:
    metadata:
      labels:
        app: db
    spec:
      containers:
      - name: postgres
        image: postgres:15
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:    # 关键：自动按 Pod 序建 PVC
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
    # 不写 storageClassName 会用集群默认
    # storageClassName: gp3
```

PVC 自动建：
- `data-db-0` → web-0
- `data-db-1` → web-1
- `data-db-2` → web-2

即使 Pod 重建 / 调度到其他 Node，PVC 跟着 Pod（PV 重新绑定）。

## 🔄 升级策略

```yaml
spec:
  updateStrategy:
    type: RollingUpdate          # 默认
    rollingUpdate:
      partition: 0              # 升级 ≥ 0 的 Pod（即全部）
    # OR
    type: OnDelete              # 手动控制
```

### 分区滚动（kafka / es 常用）

```yaml
updateStrategy:
  type: RollingUpdate
  rollingUpdate:
    partition: 2              # 只升级 ordinal >= 2 的（先升级 web-2）

# 改 partition 升级下一批
kubectl patch sts db -p '{"spec":{"updateStrategy":{"rollingUpdate":{"partition":1}}}}'
```

## 🆚 vs Deployment

| | Deployment | StatefulSet |
|--|------------|--------------|
| Pod 名字 | 随机 hash | 固定 ordinal (web-0) |
| 副本切换 | 完全替换 | 保留 identity |
| 存储 | 共享 / 无 | 每个 Pod 独立 PVC |
| 适合 | 无状态 | 有状态 |
| 启动顺序 | 并行 | 可配（按 ordinal 串行） |

## 🛠 常用命令

```bash
kubectl get sts
kubectl get pods -l app=db
kubectl get pvc                 # 自动建了 3 个 PVC

# 扩缩（**必须小心**）
kubectl scale sts db --replicas=5

# 升级镜像
kubectl set image sts/db postgres=postgres:16

# 分区升级
kubectl patch sts db -p '{"spec":{"updateStrategy":{"rollingUpdate":{"partition":2}}}}'

# 删 PVC（重置数据）
kubectl delete pvc data-db-1

# 故障 Pod 调试
kubectl describe pod db-0
kubectl logs db-0
```

## 🛠 实战

### Redis Cluster / Kafka / ZooKeeper

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis
spec:
  serviceName: redis
  replicas: 6
  template:
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        command: ["redis-server", "--cluster-enabled", "yes"]
        ports:
        - containerPort: 6379
        - containerPort: 16379   # 集群总线
        volumeMounts:
        - name: data
          mountPath: /data
  volumeClaimTemplates:
  - metadata: { name: data }
    spec:
      accessModes: ["ReadWriteOnce"]
      resources: { requests: { storage: 5Gi } }
```

### MySQL 主从

```yaml
# master
spec:
  template:
    spec:
      containers:
      - name: mysql
        image: mysql:8
        env:
        - name: MYSQL_REPLICATION_MODE
          value: master
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef: ...
```

官方 mysql operator 已成熟，**生产直接用 operator**，不要手写。

## 🩹 故障

```bash
# Pod 卡 Init
kubectl describe sts db
kubectl describe pod db-0 | grep Events
# 通常：PVC 没 bound / StorageClass 错

# 节点迁移后数据还在？
kubectl get pvc data-db-0
# 看 VolumeName（绑到哪个 PV）
```

## 🔗 下一步

- [Pod 最小单元](/03-k8s-workload/pod)
- [Deployment](/03-k8s-workload/deployment)
- [PV / PVC](/05-k8s-storage/pv-pvc)