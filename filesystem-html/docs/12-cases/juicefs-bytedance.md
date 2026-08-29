---
title: 字节跳动 JuiceFS 实践
date: 2026-08-15  # date-auto-injected
---

# 字节跳动 — JuiceFS 海量 AI / K8s 存储

> <span class="kg-badge kg-badge--cases">企业案例</span>
> JuiceFS · K8s 大规模 · AI 训练数据集

字节跳动（TikTok 母公司）是 JuiceFS 的**最大用户**之一。JuiceFS 在字节内部被用于 **Kubernetes 大规模共享存储**和**AI 训练数据集**，日承载 PB 级数据。

## 1. 字节跳动存储规模

| 指标 | 数值 |
|------|------|
| K8s 集群 | 数百万 Pod |
| 数据规模 | **EB 级**（视频、AIGC、推荐） |
| 团队规模 | 数千研发 |
| JuiceFS 实例 | 数万 |

## 2. 为什么选 JuiceFS

字节跳动的痛点：

1. **K8s 共享存储**：多 Pod ReadWriteMany，传统块存储不够
2. **AI 训练数据集**：PB 级数据集多 worker 并行读
3. **弹性**：业务峰值波动巨大
4. **跨机房**：必须支持跨 AZ

JuiceFS 优势：

- 元数据 / 数据分离（KV + 对象存储）
- 完整 POSIX
- RWX 模式 K8s
- 跨云可拔插

## 3. 架构

```
┌─────────────────────────────────────┐
│     K8s Pod × N（AI 训练 / 服务）   │
└────────────┬────────────────────────┘
             │  FUSE / CSI
┌────────────▼────────────────────────┐
│      JuiceFS Client                 │
│       (per pod)                     │
└────┬──────────────────┬─────────────┘
     │ 元数据           │ 数据
┌────▼───────────┐  ┌──▼─────────────────┐
│  TiKV (元数据) │  │  S3 / OSS / COS    │
│   多 AZ 集群    │  │   (跨 AZ 副本)     │
└────────────────┘  └────────────────────┘
```

## 4. AI 训练场景

### 4.1 数据集准备

```bash
# 1. 把训练数据上传到 JuiceFS
juicefs format --storage s3 \
    --bucket https://s3.amazonaws.com/train-data \
    --access-key xxx --secret-key yyy \
    tikv://tikv.example.com:2379 \
    training-data

# 2. 挂载
juicefs mount -d tikh://tikv.example.com:2379/training-data /mnt/jfs

# 3. 准备数据集
cp -r /raw/images/ /mnt/jfs/train/
cp labels.json /mnt/jfs/train/
```

### 4.2 多 Worker 并行读

```python
import torch
from torch.utils.data import DataLoader
from torchvision import datasets

# 多个 GPU worker 同时读 JuiceFS 上的 ImageNet
dataset = datasets.ImageFolder('/mnt/jfs/train/imagenet/')
loader = DataLoader(dataset, batch_size=128, num_workers=16)
```

- JuiceFS 数据走 S3，多 worker 并行带宽高
- 元数据走 TiKV，list 快速

### 4.3 缓存加速

```bash
# Worker 本地缓存热数据
juicefs warmup /mnt/jfs/train/imagenet --threads 32
# → 本地 /var/cache/juicefs/ 缓存命中 → 读延迟从 100ms 降到 1ms
```

## 5. K8s 场景

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: shared-data
spec:
  accessModes: [ReadWriteMany]   # 多 Pod 共享
  storageClassName: juicefs-sc
  resources:
    requests:
      storage: 1Ti
```

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: ml-trainer
spec:
  replicas: 8                  # 8 个并行 worker
  template:
    spec:
      containers:
      - name: trainer
        image: myorg/trainer:v1
        volumeMounts:
        - name: data
          mountPath: /data
  volumeClaimTemplates:
  - metadata: { name: data }
    spec:
      accessModes: [ReadWriteOnce]   # 这里其实用 RWX 共享
      storageClassName: juicefs-sc
      resources:
        requests:
          storage: 500Gi
```

## 6. 元数据服务（TiKV 集群）

字节跳动用 TiKV 做 JuiceFS 元数据服务：

- TiKV 3 副本跨 AZ
- 10万+ QPS 元数据请求
- 强一致（事务）

```bash
# 性能测试（TiKV 集群）
ycsb load tiflash -p tikv.pd-addr=pd.example.com:2379 -p recordcount=100000000
```

## 7. 性能优化

### 7.1 客户端调优

```bash
juicefs mount -d tikh://tikv.example.com:2379/training-data /mnt/jfs \
    --cache-size 100000 \       # 100 GB 本地缓存
    --buffer-size 300 \         # 写缓冲
    --upload-concurrency 5 \    # 上传并发
    --download-concurrency 20   # 下载并发
```

### 7.2 预热

```bash
# 启动 worker 前预热
juicefs warmup /mnt/jfs/train/imagenet/ --threads 32
```

### 7.3 配额管理

```bash
# 用户配额
juicefs quota set /mnt/jfs/user/alice 500G
```

## 8. 多机房与跨云

```
   北京机房             上海机房
      │                    │
      │                    │
   JuiceFS Client       JuiceFS Client
      │                    │
      └──── TiKV 集群 ────┘
                │
                ▼
      S3 跨 Region 副本
```

- 元数据 TiKV 跨机房
- 数据 S3 跨 Region
- 客户端就近访问

## 9. 监控

- JuiceFS 自带 Prometheus exporter
- 关键指标：缓存命中率、QPS、延迟

```promql
# 缓存命中率
sum(rate(juicefs_blockcache_hit_total[5m])) /
  sum(rate(juicefs_blockcache_total[5m]))

# 元数据 QPS
rate(juicefs_meta_ops_total[5m])
```

## 10. 经验教训

| 经验 | 说明 |
|------|------|
| **元数据 = 关键路径** | TiKV 必须 HA，否则整个集群挂 |
| **缓存大小很重要** | 100GB+ 才足够大模型训练 |
| **写模式决定性能** | 顺序写极快，随机写慢 |
| **回收站 = 安全** | JuiceFS 自带 trash 防误删 |
| **多 worker 并行** | JuiceFS 客户端并行 = 性能 |

## 11. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| JuiceFS = K8s RWX | "JuiceFS=共享" |
| TiKV = 元数据 | "TiKV=元数据" |
| 对象存储 = 数据 | "S3=数据底" |
| 预热 = 性能 | "warmup=加速" |
| 字节 = PB 级实践 | "字节=PB 级" |

## 参考

- JuiceFS 案例：<https://juicefs.com/blog/category/customer-stories
- TiKV 文档
- 字节跳动技术博客

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [linux](https://java-px.bot.cd/linux/):Linux 文件系统
- [observability](https://java-px.bot.cd/observability/):存储监控
- [postgresql](https://java-px.bot.cd/postgresql/):PG 存储引擎
