---
title: S3 协议
---

# Amazon S3 协议 — 对象存储的事实标准

> <span class="kg-badge kg-badge--object">对象存储</span>
> HTTP/REST · bucket+key · 2006 年至今

S3（Simple Storage Service）是 Amazon 2006 年推出的对象存储服务，**它定义的协议**后来成为整个对象存储的事实标准——MinIO、Ceph RGW、阿里 OSS、腾讯 COS、华为 OBS 全部兼容 S3 API。

## 1. S3 的基本模型

| 概念 | 含义 |
|------|------|
| Bucket | 全局唯一的命名空间（早期是命名空间，现在每个账户独立） |
| Object | 一个文件 + 元数据（key + value） |
| Key | 对象名（flat 字符串，靠 `/` 模拟层级） |
| Version | 同一 key 的多次写历史（开启 Versioning 后） |
| Region | bucket 所在的地理区域 |
| ACL / Policy | 资源权限控制 |

S3 是**扁平**的，没有真正的目录。`/a/b/c.txt` 里的 `/` 只是 key 里的字符，前缀列表 = "伪目录"。

## 2. HTTP API 概览

| 操作 | HTTP 方法 | 含义 |
|------|-----------|------|
| PutObject | `PUT /<bucket>/<key>` | 上传对象 |
| GetObject | `GET /<bucket>/<key>` | 下载对象 |
| DeleteObject | `DELETE /<bucket>/<key>` | 删除 |
| HeadObject | `HEAD /<bucket>/<key>` | 看元数据 |
| ListObjects | `GET /<bucket>?list-type=2` | 列对象 |
| CopyObject | `PUT /<bucket>/<key>` 配 `x-amz-copy-source` | 服务端拷贝 |
| Multipart | `POST /<bucket>/<key>?uploadId` 等 | 大文件分片 |

## 3. 鉴权：SigV4

S3 用 AWS Signature Version 4（SigV4）签每个请求：

```
Authorization: AWS4-HMAC-SHA256 Credential=AKIA.../20260101/us-east-1/s3/aws4_request,
SignedHeaders=host;range;x-amz-date,
Signature=...

# 待签名字符串
canonicalRequest =
  HTTPMethod + '\n' +
  CanonicalURI + '\n' +
  CanonicalQueryString + '\n' +
  CanonicalHeaders + '\n' +
  SignedHeaders + '\n' +
  HashedPayload
```

实战要点：

- **服务端时间偏差** > 15 分钟 → 签名失效（同步 NTP）
- **临时凭证**（STS）→ 用 SigV4 不够，用 `X-Amz-Security-Token`
- **预签名 URL**（presigned）→ 用长期 AK/SK 临时签名 5 分钟有效期给前端上传

## 4. Multipart Upload：大文件的标准姿势

```python
import boto3
s3 = boto3.client('s3')

# 1. 初始化
mp = s3.create_multipart_upload(Bucket='bkt', Key='big.bin')
upload_id = mp['UploadId']

# 2. 分片上传
parts = []
for i in range(1, 11):
    with open(f'part_{i}', 'rb') as f:
        r = s3.upload_part(
            Bucket='bkt', Key='big.bin', PartNumber=i,
            UploadId=upload_id, Body=f
        )
        parts.append({'PartNumber': i, 'ETag': r['ETag']})

# 3. 完成
s3.complete_multipart_upload(
    Bucket='bkt', Key='big.bin', UploadId=upload_id,
    MultipartUpload={'Parts': parts}
)
```

**为什么用 Multipart**：并行上传、断点续传、单片失败重试。

## 5. Storage Class 与生命周期

S3 不止一种存储，Amazon 提供：

| Storage Class | 用途 | AZ 冗余 | 取回延迟 |
|---------------|------|---------|----------|
| Standard | 热 | ≥3 AZ | ms |
| Intelligent-Tiering | 自动 | ≥3 AZ | ms |
| Standard-IA | 冷 | ≥3 AZ | ms |
| One Zone-IA | 冷 | 1 AZ | ms |
| Glacier Instant Retrieval | 归档 | ≥3 AZ | ms |
| Glacier Flexible Retrieval | 归档 | ≥3 AZ | 分钟~小时 |
| Glacier Deep Archive | 长期归档 | ≥3 AZ | 小时 |

**生命周期规则**自动把对象从热 → 冷：

```xml
<LifecycleConfiguration>
  <Rule>
    <ID>archive-old</ID>
    <Status>Enabled</Status>
    <Prefix>logs/</Prefix>
    <Transition>
      <Days>30</Days>
      <StorageClass>GLACIER</StorageClass>
    </Transition>
    <Expiration>
      <Days>365</Days>
    </Expiration>
  </Rule>
</LifecycleConfiguration>
```

## 6. 跨域 / 复制 / 事件

| 场景 | 机制 |
|------|------|
| 跨域访问 | CORS 规则（bucket policy + `*`/指定 origin） |
| 跨区域复制 | CRR（CROSS-Region Replication） |
| 同区域复制 | SRR（Same-Region Replication） |
| 对象变化触发 | SNS/SQS/Lambda（Put/Post/Delete 事件） |
| 静态网站托管 | bucket 配置 `Website` |

## 7. S3 API 在国产云的映射

| 特性 | AWS S3 | 阿里 OSS | 腾讯 COS | 华为 OBS |
|------|--------|---------|---------|---------|
| 命名空间 | bucket | bucket | bucket | bucket |
| SDK 兼容 | 官方 | oss2 / S3 兼容 | COS SDK / S3 兼容 | obs sdk |
| 分片上传 | Multipart | Multipart | 分块上传 | 多段上传 |
| 生命周期 | Lifecycle | Lifecycle | Lifecycle | 生命周期 |
| 取回归档 | Glacier | Archive | Archive | COLD |
| IAM | IAM Policy | RAM Policy | CAM | IAM |

**经验**：跨云迁移时用 S3 SDK 最省事——大部分厂商都做 S3 兼容层。

## 8. 一致性模型

S3 从 2020 年起宣布了 **强一致（read-after-write）**：PUT 后立刻 GET 拿到最新版（不再有 "eventual consistency" 的副本同步窗口）。

但**列表一致性**仍然是 eventual：上传一个对象后，`LIST` 可能短暂看不到（通常秒级收敛）。

## 9. 性能与扩展性

| 维度 | 限制 |
|------|------|
| 单对象大小 | 5 TiB |
| 单次 PUT | 5 GiB（更大必须用 Multipart） |
| 分片数 | 10000 片 × 5GiB = 5 TiB |
| 单分片大小 | 5 MiB ~ 5 GiB（最后一片除外） |
| 单 bucket 吞吐 | **无限制**（横向扩 prefix） |
| 单 prefix 吞吐 | 3.5k req/s 写、5.5k req/s 读（可加随机前缀破限） |

**前缀散列**是性能优化核心：`/2026/01/01/<uuid>-image.jpg` 比 `/images/2026-01-01-1.jpg` 强。

## 10. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| 协议而非实现 | "S3 = 协议标杆" |
| bucket + key = flat | "无目录、靠前缀" |
| Multipart 是大文件默认 | "5GiB 起必 Multipart" |
| 强一致：2020 起 | "2020 后强一致" |
| 性能靠散列 prefix | "前缀散列破 5.5K" |

## 参考

- AWS S3 官方文档：<https://docs.aws.amazon.com/s3/>
- S3 协议 SigV4 规范（AWS 文档）
- MinIO S3 兼容文档（实现细节）