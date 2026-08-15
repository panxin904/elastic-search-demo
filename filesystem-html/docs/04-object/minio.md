---
title: MinIO
---

# MinIO — 开源的 S3 兼容对象存储

> <span class="kg-badge kg-badge--object">对象存储</span>
> 兼容 S3 API · 轻量 · 自建对象存储首选

MinIO 是一款采用 **AGPLv3** 协议发布的开源对象存储。它以单二进制、Go 语言、S3 协议 100% 兼容而著称，是私有化部署对象存储的事实标准。

## 1. 为什么用 MinIO

| 场景 | 是否合适 |
|------|----------|
| 私有云 S3 替代 | **是**（完全 S3 兼容） |
| Kubernetes 原生对象存储 | **是**（Operator 完善） |
| 边缘 / 嵌入式存储 | **是**（单 binary、低资源） |
| 替代 FastDFS | **是**（更现代，HTTP API） |
| 纯 PB 级超大数据 | 中等（推荐 100 TB 以下） |

## 2. 核心特性

- **完全 S3 API 兼容**：boto3、aws-sdk 都能用
- **纠删码（Erasure Coding）**：默认 EC:k=4, m=2（容 2 盘坏）
- **Lambda 通知**：与 Kafka / NATS / AMQP 集成
- **Bitrot 检测**：Hedwig 库查对象位损坏
- **多云复制**：bucket replication / mc mirror
- **服务端加密**：AES-256 / SSE-KMS
- **WORM**：合规只读保留

## 3. 部署形态

### 3.1 单机模式（开发用）

```bash
# 下载单二进制
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio

# 启动（会自动建目录）
MINIO_ROOT_USER=admin MINIO_ROOT_PASSWORD=admin123 \
    ./minio server /data/minio --console-address ":9001"

# 访问
# S3 API: http://localhost:9000
# Web Console: http://localhost:9001
```

### 3.2 分布式模式（生产）

至少 4 节点 × 4 盘，生产推荐 8 节点：

```bash
# 节点1（其余节点换 host）
MINIO_ROOT_USER=minioadmin MINIO_ROOT_PASSWORD=minioadmin \
    ./minio server \
    http://node1/data{1...4} \
    http://node2/data{1...4} \
    http://node3/data{1...4} \
    http://node4/data{1...4} \
    --console-address ":9001"
```

**注意**：每个节点上的盘数必须一致。`{1...4}` = 同节点 4 个目录。

### 3.3 K8s Operator

```bash
helm repo add minio https://charts.min.io/
helm install minio minio/minio \
    --namespace minio \
    --create-namespace \
    --set rootUser=admin \
    --set rootPassword=admin12345 \
    --set persistence.size=100Gi \
    --set replicas=4
```

## 4. mc 客户端（管理神器）

`mc` 是 MinIO 提供的命令行工具，比 aws-cli 简洁：

```bash
mc alias set local http://localhost:9000 admin admin123
mc alias set prod https://s3.example.com ak sk

# 常用操作
mc mb local/mybucket                       # 建 bucket
mc ls local/                               # 列 bucket
mc cp /etc/hosts local/mybucket/hosts.txt # 上传
mc ls local/mybucket/                      # 列对象
mc cp local/mybucket/hosts.txt -           # 下载
mc mirror /var/log local/mybucket/logs/    # 同步目录

# 桶复制
mc mirror local/src prod/dst --remove

# 看硬盘
mc admin info local
mc admin heal -r local/mybucket

# 看事件
mc events list local/mybucket
```

## 5. 纠删码（EC）调优

MinIO 默认 **k=4, m=2**（4 数据片 + 2 校验片，容 2 盘坏）。

```bash
# 看 EC 拓扑
mc admin policy info local

# 改 EC：先设环境变量再启动
MINIO_STORAGE_CLASS_STANDARD=EC:5
```

| EC 配置 | 容错盘数 | 存储开销 |
|---------|----------|----------|
| EC:2 | 1 | 50% |
| EC:4 | 2 | 50% |
| EC:8 | 4 | 50% |
| Replication (无 EC) | 1 | 100% |

**实战建议**：容量紧张用 EC；低延迟场景用单节点 / Replication。

## 6. 安全配置

### 6.1 访问策略

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"AWS": ["*"]},
      "Action": ["s3:GetObject"],
      "Resource": ["arn:aws:s3:::public-bucket/*"]
    }
  ]
}
```

### 6.2 服务端加密

```bash
# 启动时启用
MINIO_KMS_SECRET_KEY=... ./minio server /data

# 桶级加密（SSE-S3）
mc encrypt set sse-s3 local/mybucket

# 看对象加密状态
mc stat local/mybucket/secret.dat
```

### 6.3 TLS 终止

```bash
MINIO_HTTPS_CERT_FILE=/path/to/cert.pem \
MINIO_HTTPS_KEY_FILE=/path/to/key.pem \
./minio server https://node1/data{1...4}...
```

## 7. 性能 & 监控

### 7.1 关键指标

- **S3 API latency**：用 `mc` 的 `trace` 或 Prometheus exporter
- **磁盘 IO**：iostat -x 1
- **网络**：sar -n DEV 1
- **Memcached 状态**：`mc admin trace`

### 7.2 Prometheus 集成

```yaml
scrape_configs:
  - job_name: minio
    bearer_token: <admin-token>
    metrics_path: /minio/v2/metrics/cluster
    static_configs:
      - targets: ['minio:9000']
```

### 7.3 关键告警

```yaml
- alert: MinIODriveOffline
  expr: minio_node_drive_offline > 0
- alert: MinIOBucketUsage
  expr: minio_bucket_usage_object_total > 1e8
```

## 8. 与 S3 兼容性矩阵

| S3 特性 | MinIO 支持 |
|---------|-----------|
| PutObject / GetObject | ✅ |
| Multipart Upload | ✅ |
| Bucket Versioning | ✅ |
| Lifecycle Policy | ✅ |
| Object Lock / WORM | ✅ |
| Replication | ✅ |
| Lambda Notifications | ✅（KAFKA / NATS / AMQP / MQTT / Webhook） |
| S3 Select | ⚠️ 部分（CSV/JSON，SQL 子集） |
| S3 Inventory | ⚠️ 第三方实现 |
| Glacier Deep Archive | ❌（MinIO 自己也不做冷层） |

## 9. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| 单 binary + Go | "MinIO=单绿" |
| 默认 EC 4+2 | "EC=4+2 必记" |
| mc 比 awscli 简单 | "mc=运维神器" |
| K8s 友好 | "Operator=原生" |
| S3 100% 兼容 | "换 S3 零成本" |

## 参考

- 官方文档：<https://min.io/docs/minio/linux/index.html>
- mc 命令大全
- Bitrot：Hedwig 论文（MinIO 团队）