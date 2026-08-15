---
title: etcd 存储
---

# etcd - 集群的大脑

> k8s 所有状态存在 etcd — 分布式 KV、强一致、RAFT。

## 🤔 是什么

etcd = **etcd distributed**（不是 etc）+ **d**istributed。

- 强一致 KV 存储
- 基于 **RAFT** 共识算法
- 写半数以上节点才提交
- 默认 2379（客户端）/ 2380（peer）
- 单一 etcd 集群存所有 k8s 状态

## 🏗️ 架构

```
┌─────────────┐
│   etcd-1    │  ←──┐
│  leader     │     │
└─────┬───────┘     │
      ▲             │
      │  RAF       │
      ▼             │
┌─────────────┐     │
│   etcd-2    │ ────┤
│  follower   │     │  RAF 一致
└─────┬───────┘     │
      ▲             │
      │             │
      ▼             │
┌─────────────┐     │
│   etcd-3    │ ────┘
│  follower   │
└─────────────┘
```

- 集群通常 **3 或 5 节点**（奇数）
- 3 节点可容 1 失败
- 5 节点可容 2 失败

## 🗃️ 存的什么

```
/registry/
├── pods/
│   └── default/
│       └── myapp-abc123
├── deployments/
├── services/
├── configmaps/
├── secrets/    # （base64 编码，非加密！）
├── events/
├── nodes/
└── ...
```

⚠️ **Secret 默认是 base64 不加密** — 真要加密用 KMS 集成。

## 🛠 etcdctl 命令

```bash
# 设环境变量（简化）
export ETCDCTL_API=3
export ETCDCTL_ENDPOINTS=https://127.0.0.1:2379
export ETCDCTL_CACERT=/etc/kubernetes/pki/etcd/ca.crt
export ETCDCTL_CERT=/etc/kubernetes/pki/etcd/server.crt
export ETCDCTL_KEY=/etc/kubernetes/pki/etcd/server.key

# 集群健康
etcdctl endpoint health
etcdctl endpoint status

# 成员
etcdctl member list

# 看数据
etcdctl get /registry --prefix --keys-only | head
etcdctl get /registry/pods/default/myapp

# 写
etcdctl put /test "hello"
etcdctl get /test
etcdctl del /test

# 监听变化
etcdctl watch /registry/pods --prefix

# 备份（snapshot）
etcdctl snapshot save /tmp/etcd-snap.db
etcdctl snapshot status /tmp/etcd-snap.db

# 恢复
etcdctl snapshot restore /tmp/etcd-snap.db \
  --data-dir=/var/lib/etcd-restore
```

## 📦 备份策略

```bash
#!/bin/bash
# 每日 etcd 备份
BACKUP_DIR=/var/backups/etcd/$(date +%Y%m%d)
mkdir -p $BACKUP_DIR

etcdctl snapshot save $BACKUP_DIR/snap.db
etcdctl snapshot status $BACKUP_DIR/snap.db --write-out=table

# 保留 7 天
find /var/backups/etcd/ -mtime +7 -delete
```

## 🔄 实战：恢复

```bash
# 1. 停 etcd（在所有 master）
systemctl stop etcd

# 2. 恢复
rm -rf /var/lib/etcd
etcdctl snapshot restore /var/backups/etcd/snap.db \
  --data-dir=/var/lib/etcd

# 3. 起 etcd
systemctl start etcd

# 4. 验证
etcdctl endpoint health
kubectl get nodes
```

⚠️ **慎用**：恢复会让所有 etcd 状态回滚，可能影响运行中的 Pod。

## 📊 监控

```bash
# 看 etcd 性能
etcdctl endpoint status --write-out=json | jq '.[0]'
# 看 disk / db size / leader / raft index

# Prometheus 有 etcd metrics exporter
# - etcd_disk_writes_seconds_bucket
# - etcd_network_client_grpc_received_bytes_total
```

监控项：
- **leader 切换次数**（频繁切换 = 不健康）
- **fsync 延迟**（> 10ms 需关注）
- **DB size**（默认 8GB 限制）
- **apply / commit 速率**

## ⚠️ 实战注意

```bash
# 1. DB size 默认 8GB
# 看
etcdctl endpoint status | grep dbSize
# 大集群（> 5k 服务）可能超过

# 调大（kubeadm 集群）
vim /etc/kubernetes/manifests/etcd.yaml
# --quota-backend-bytes=16777216  # 16GB
kubectl -n kube-system delete pod -l component=etcd

# 2. 备份频率
# - 重大变更前
# - 升级前
# - 定期（每日）

# 3. 多副本 + 跨可用区
# 生产 etcd 必须：
# - 3+ 节点
# - 不同机器（不要同宿主机）
# - 最好是不同可用区
```

## 🛠 实战

### 查 k8s 资源在 etcd 怎么存

```bash
# 看一个 pod
kubectl get pod myapp -o yaml > pod.yaml
# 对比 etcd
etcdctl get /registry/pods/default/myapp -o yaml > etcd-pod.yaml
# 应几乎一样
```

### 排查 "数据不一致"

```bash
# API Server 报 not found，但 kubectl get 能看到？
# 1. 检查 etcd 集群健康
etcdctl endpoint health
etcdctl endpoint status

# 2. 看 apiserver 日志
journalctl -u kube-apiserver -f | grep -i 'etcd\|storage'

# 3. 查 DB 大小
etcdctl endpoint status | grep dbSize
```

## 🔗 下一步

- [控制面 Control Plane](/02-k8s-arch/control-plane)
- [kubectl 命令行](/02-k8s-arch/kubectl)
- [k8s 是什么](/02-k8s-arch/overview)