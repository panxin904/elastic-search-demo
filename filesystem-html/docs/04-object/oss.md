---
title: 阿里云 OSS
---

# 阿里云 OSS — 国内市场份额第一的对象存储

> <span class="kg-badge kg-badge--object">对象存储</span>
> 阿里云原生 · S3 兼容 · 国内实战首选

阿里云对象存储 OSS（Object Storage Service）是国内最早、最大规模的对象存储服务。它既提供**自有 SDK**，也兼容 S3 API，让跨云迁移无负担。

## 1. OSS 基础概念

| 概念 | 说明 |
|------|------|
| Bucket | 存储空间（全局唯一名） |
| Object | 文件 + 元数据 |
| Endpoint | 访问域名（公网 / 内网 / 加速） |
| Region | 地域（杭州、北京、上海、深圳、东京、新加坡等） |
| AccessKey | AK / SK 凭证对 |
| Storage Class | 标准 / 低频 / 归档 / 冷归档 / 深度冷归档 |
| 镜像回源 | bucket miss 时回源到指定 URL |

## 2. Region 与 Endpoint

```text
华东1（杭州）              oss-cn-hangzhou.aliyuncs.com
华东2（上海）              oss-cn-shanghai.aliyuncs.com
华北1（青岛）              oss-cn-qingdao.aliyuncs.com
华北2（北京）              oss-cn-beijing.aliyuncs.com
华北5（呼和浩特）           oss-cn-huhehaote.aliyuncs.com
华南1（深圳）              oss-cn-shenzhen.aliyuncs.com
西南1（成都）              oss-cn-chengdu.aliyuncs.com
中国香港                  oss-cn-hongkong.aliyuncs.com
新加坡                    oss-ap-southeast-1.aliyuncs.com

内网地址（VPC 内访问，免公网费用）：
  oss-cn-hangzhou-internal.aliyuncs.com
  oss-cn-shanghai-finance-1.aliyuncs.com
```

**内网免费**：同 Region 的 ECS、函数计算访问 OSS 内网 endpoint，**免流量费**，且延迟更低。

## 3. SDK 使用（Python）

```bash
pip install oss2
```

```python
import oss2

auth = oss2.Auth('AccessKeyId', 'AccessKeySecret')
bucket = oss2.Bucket(auth, 'https://oss-cn-hangzhou.aliyuncs.com', 'my-bucket')

# 上传
bucket.put_object('hello.txt', b'Hello, OSS!')

# 下载
result = bucket.get_object('hello.txt')
print(result.read())

# 列举
for obj in oss2.ObjectIterator(bucket, prefix='logs/'):
    print(obj.key)

# 预签名 URL（5 分钟）
url = bucket.sign_url('GET', 'private/secret.pdf', 300)
```

## 4. 存储类型

| 类型 | 用途 | 取回费用 | 最低存储时间 |
|------|------|----------|-------------|
| 标准存储 (Standard) | 热 | 无 | 无 |
| 低频访问 (IA) | 温 | 0.01 元/GB | 30 天 |
| 归档存储 (Archive) | 冷 | 0.06 元/GB | 60 天 |
| 冷归档 (Cold Archive) | 极冷 | 0.20 元/GB | 180 天 |
| 深度冷归档 (Deep Cold) | 罕见访问 | 0.30 元/GB | 180 天 |

**生命周期**自动迁移：

```python
lifecycle_rule = oss2.models.LifecycleRule(
    'archive-rule',
    'logs/',
    status=oss2.models.LifecycleRule.ENABLED,
    transitions=[
        oss2.models.LifecycleTransition(days=30, storage_class=oss2.BUCKET_STORAGE_IA),
        oss2.models.LifecycleTransition(days=90, storage_class=oss2.BUCKET_STORAGE_ARCHIVE),
    ],
    expiration=oss2.models.LifecycleExpiration(days=365),
)
bucket.put_bucket_lifecycle(lifecycle_rule)
```

## 5. 数据安全

### 5.1 服务端加密

| 模式 | 说明 |
|------|------|
| SSE-OSS | OSS 自管密钥（默认） |
| SSE-KMS | 阿里云 KMS 托管密钥 |
| SSE-BYOK | 用户自带密钥（BYOK） |

```bash
ossutil set-bucket-encryption oss://my-bucket --sse-algorithm AES256
```

### 5.2 防盗链（Referer）

```bash
ossutil set-bucket-referer oss://my-bucket \
    --referer "https://example.com/*" \
    --allow-empty-referer=false
```

### 5.3 WORM（合规归档）

OSS 提供合规保留策略，1~70 年不可改不可删。

## 6. 跨区域复制

```python
replication_config = oss2.models.BucketReplicationRule(
    'rule-1',
    'src-prefix/',
    'https://oss-cn-shanghai.aliyuncs.com',
    'dst-bucket',
    'dst-prefix/'
)
bucket.put_bucket_replication(...)
```

实时同步 → 异地灾备 RPO 分钟级。

## 7. 数据处理

OSS 配套图片、音视频、AI 处理：

| 能力 | URL 示例 |
|------|----------|
| 图片处理 | `?x-oss-process=image/resize,w_200,h_200` |
| 视频截图 | `?x-oss-process=video/snapshot,t_5000,f_jpg,w_800` |
| Webp 转换 | `?x-oss-process=image/format,webp` |
| ZIP 打包 | `?x-oss-process=zip/deflate,level-9` |
| 文档预览 | 需要用 imm 服务（智能媒体） |

## 8. 传输加速

OSS 全球加速（CGT）：

```python
auth = oss2.Auth('...', '...')
endpoint = 'https://oss-accelerate.aliyuncs.com'  # 走全球加速
```

适合跨洲远距离上传下载；同 Region 内 ECS 走内网，不需要加速。

## 9. RAM 权限

最小授权给子账号：

```json
{
  "Version": "1",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["oss:GetObject", "oss:PutObject"],
      "Resource": "acs:oss:*:*:my-bucket/private/*"
    }
  ]
}
```

通过 STS 发**临时凭证**给前端 → 用 STS Token 上传。

## 10. 实战清单

| 场景 | 推荐配置 |
|------|----------|
| 静态网站 | bucket 开 **静态页面托管**，配 CDN 加速 |
| 大文件备份 | 标准 → 30 天 IA → 90 天归档 |
| 跨境传输 | 用 CGT 全球加速 + 多 bucket 复制 |
| 私有访问 | bucket ACL = 私有，用 RAM STS 临时凭证 |
| 数据归档 | Archive Class（取回要 1 分钟解冻） |

## 11. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| 同 Region 内网免费 | "内网=省钱" |
| 归档取回要解冻 | "Archive 必等" |
| 防盗链靠 Referer | "Referer 黑名单" |
| SDK + S3 兼容双轨 | "oss2 + boto3 都行" |
| 跨域复制 RPO 分钟级 | "CRR=异地分钟" |

## 参考

- 阿里云 OSS 文档：<https://help.aliyun.com/oss>
- ossutil 命令手册
- 计费规则：<https://help.aliyun.com/document_detail/31817.html>