---
title: 系统设计
date: 2026-08-15  # date-auto-injected
---

# 系统设计题 — 文件系统方案设计

> <span class="kg-badge kg-badge--interview">面试对比</span>
> 场景拆解 · 容量估算 · 选型决策

本章给常见系统设计题一套**存储维度**的解法。

## 1. 设计 Instagram 照片存储

### 需求

- 100 亿张照片，平均 200 KB
- 总容量：200 PB
- 读多写少
- 全球用户访问

### 方案

```
用户上传
   ↓
预处理（缩略图、EXIF）
   ↓
对象存储（S3 标准存储）
   ├─ 原图（S3 Standard）
   ├─ 缩略图（S3 Standard-IA）
   └─ 长尾（S3 Glacier）
   ↓
CDN（CloudFront）
   ↓
全球用户
```

**关键决策**：

| 选型 | 理由 |
|------|------|
| 对象存储 | 高吞吐、无限扩展 |
| 分类存储 | 热/温/冷省钱 |
| CDN | 加速 + 节省源站 |
| 异步处理 | Lambda / worker |

**估算**：

- 上传：100 亿 ÷ 10 年 ÷ 365 ÷ 86400 ≈ 350 万次/秒（峰值 10×）
- 读：上传的 50×（用户浏览 + 朋友看）≈ 1.75 亿次/秒
- 容量：原图 200 KB × 100 亿 = 200 PB

## 2. 设计 Netflix 视频流

### 需求

- 1000 万 4K 视频，平均 30 GB
- 总容量：300 PB
- 实时编码（HLS / DASH）
- CDN 边缘分发

### 方案

```
源视频
   ↓
Keystone（编码）
   ├─ 多码率（HLS）
   ├─ 加密 + DRM
   └─ 切片
   ↓
对象存储（S3 + Glacier）
   ↓
CDN 边缘
   ↓
全球用户
```

**关键**：

- 多码率（HLS）= 不同带宽不同质量
- CDN 边缘 = 大幅降低源站压力
- DRM = 数字版权保护

## 3. 设计抖音短视频存储

### 需求

- 100 亿条视频，平均 5 MB
- 总容量：500 PB
- 高并发上传 + 极速分发
- 全球低延迟

### 方案

```
用户上传
   ↓
边缘接入（多 Region）
   ↓
对象存储（多云多 Region 复制）
   ↓
转码（多分辨率）
   ↓
CDN（多厂商容灾）
   ↓
全球用户
```

**关键决策**：

- 多 Region 部署：上传就近
- 多 CDN 容灾：单一 CDN 故障切流量
- 多云复制：避免锁定

## 4. 设计 Kafka 日志存储

### 需求

- 日吞吐量 PB 级
- 顺序写
- 高吞吐读
- 保留 7 天

### 方案

**Kafka 本身就是顺序 IO 的"分布式 FS"**：

```
Producer → Partition → Append-only Segment Files → Page Cache → Disk
                            ↓
                     Retention (按时间)
                            ↓
                       删除 / 归档到 OSS
```

**关键**：

- 用 SSD（顺序写）
- OS Page Cache 命中
- 离线归档到 OSS 节省成本

## 5. 设计 Hadoop 大数据存储

### 需求

- PB 级批量分析
- 顺序 IO
- 高吞吐
- 离线

### 方案

```
HDFS（Hadoop 默认）
   ├─ NameNode + Federation
   ├─ DataNode 副本
   └─ Tiered Storage
       ├─ 热数据（HDFS）
       └─ 冷数据（OSS）
```

**关键决策**：

- 副本数 3（默认）
- 大 block（128 MB）
- Federation 解决 NameNode 瓶颈

## 6. 设计 Kubernetes 集群存储

### 需求

- 多 Pod 共享（ReadWriteMany）
- 不同业务（数据库 / 静态资源 / 日志）
- 弹性

### 方案

```
K8s Cluster
   │
   ├─ 数据库 → Rook-Ceph RBD（性能 + RWO）
   ├─ 共享目录 → JuiceFS / CephFS / Longhorn（RWX）
   ├─ 对象存储 → MinIO + CSI（S3 兼容）
   ├─ 日志 → NFS（短保留）
   └─ 备份 → Velero + OSS
```

**关键决策**：

| 业务 | 推荐 |
|------|------|
| 数据库 | Rook-Ceph RBD / Longhorn RWO |
| 共享 | JuiceFS / CephFS / NFS |
| 对象 | MinIO + CSI |
| 日志 | 节点本地 + 转发 |

## 7. 设计异地容灾

### 需求

- RPO = 0（同 AZ）
- RPO = 秒级（同城异地）
- RPO = 分钟级（异地）
- RTO ≤ 10 分钟

### 方案

```
主站 (北京)                          备站 (上海)
   │                                    │
   ├─ 同步复制 → 同 AZ（多副本）       │
   ├─ 半同步 → 同城异地（毫秒级）       │
   └─ 异步复制 → 异地（秒级）          │
                                        │
                              自动 / 手动切换
                              DNS / LB 流量切
```

**关键决策**：

| 业务 | RPO |
|------|-----|
| 金融 | 0（同步） |
| 通用 | 秒（半同步） |
| 离线 | 分钟（异步） |

## 8. 设计云原生 Lakehouse

### 需求

- 数据湖 + 数据仓库 = Lakehouse
- 支持 SQL / ML / 流
- 多引擎（Spark / Trino / Flink）

### 方案

```
Iceberg / Delta Lake
   │
   ▼ 存于 S3 / OSS / COS
   │
   ├─ Spark（批处理）
   ├─ Trino / Athena（SQL）
   ├─ Flink（流）
   └─ ML（PyTorch / TF）
```

**关键决策**：

- 表格式：Iceberg（开放、跨引擎）
- 存储：S3 / OSS
- 计算：弹性

## 9. 设计通用存储决策树

```
需要 POSIX 兼容？
│
├─ 是 → 单机 ext4/xfs
│   │
│   └─ 多机？
│       ├─ 是 → NFS / GlusterFS / CephFS / JuiceFS
│       └─ 否 → ext4
│
└─ 否 → 对象存储 S3 / OSS
    │
    └─ 高吞吐（PB 级）？
        ├─ 是 → 对象存储 + 优化
        └─ 否 → 本地 FS
```

## 10. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| 估算先行 | "估算=起点" |
| 对象存储是默认 | "S3=默认" |
| CDN 必备 | "CDN=加速" |
| 多 Region 容灾 | "多 Region=灾备" |
| Lakehouse = 新代 | "Lakehouse=湖仓" |

## 参考

- DDIA《数据密集型应用系统设计》
- LeetCode 系统设计题
- 系统设计面试（Alex Xu）