---
title: 腾讯云 COS
date: 2026-08-15  # date-auto-injected
---

# 腾讯云 COS — 腾讯生态的对象存储

> <span class="kg-badge kg-badge--object">对象存储</span>
> 腾讯云原生 · S3 兼容 · 微信生态深度集成

腾讯云对象存储 COS（COS，Cloud Object Storage）是腾讯云提供的对象存储服务。它在国内市场份额仅次于阿里 OSS，特点是与微信小程序、企业微信等腾讯生态深度集成。

## 1. COS 基础概念

| 概念 | 说明 |
|------|------|
| Bucket | 存储桶（同 Region 内唯一） |
| Object | 对象（key + value） |
| 地域（Region） | 北京、上海、广州、南京、成都、重庆等 |
| 接入域名（Endpoint） | `cos.<region>.myqcloud.com` |
| CAM | 腾讯云的访问管理（类似 RAM） |
| 存储类型 | 标准 / 低频 / 归档 / 深度归档 / 智能分层 |
| 访问凭证 | API 密钥 / CAM 角色 / 临时密钥（STS） |

## 2. 地域与域名

```text
北京      cos.ap-beijing.myqcloud.com
上海      cos.ap-shanghai.myqcloud.com
广州      cos.ap-guangzhou.myqcloud.com
成都      cos.ap-chengdu.myqcloud.com
中国香港  cos.ap-hongkong.myqcloud.com
新加坡    cos.ap-singapore.myqcloud.com

# 同 Region VPC 内网（推荐）
cos.ap-guangzhou-internal.myqcloud.com
```

## 3. SDK 使用（Python）

```bash
pip install cos-python-sdk-v5
```

```python
from qcloud_cos import CosConfig, CosS3Client
from qcloud_cos import CosServiceError

config = CosConfig(
    Region='ap-guangzhou',
    SecretId='...',
    SecretKey='...',
    Scheme='https'
)
client = CosS3Client(config)

# 上传
response = client.put_object(
    Bucket='examplebucket-1250000000',
    Key='hello.txt',
    Body=b'Hello, COS!'
)
print(response['ETag'])

# 下载
response = client.get_object(
    Bucket='examplebucket-1250000000',
    Key='hello.txt'
)
print(response['Body'].get_raw_stream().read())

# 预签名 URL
url = client.get_object_url(
    Bucket='examplebucket-1250000000',
    Key='private.docx',
    Expired=300
)
```

**Bucket 名规律**：`<bucketName>-1250000000`，后面数字是 APPID。

## 4. 存储类型

| 类型 | 用途 | 取回 |
|------|------|------|
| 标准存储 | 热 | 即时 |
| 低频存储（STANDARD_IA） | 温（30 天起存） | 即时 |
| 归档存储（ARCHIVE） | 冷（60 天起存） | 解冻 1~5 分钟 |
| 深度归档（DEEP_ARCHIVE） | 极冷（180 天起存） | 解冻小时级 |
| 智能分层 | 自动 | 自动迁移 |

**冷数据解冻**：

```python
client.restore_object(
    Bucket='examplebucket-1250000000',
    Key='archive/old.log',
    RestoreRequest={
        'Days': 7,
        'CASJobParameters': {
            'Tier': 'Expedited'  # Expedited=1-5min / Standard=2-5h / Bulk=5-12h
        }
    }
)
```

## 5. 静态网站 + CDN

```python
# 开启静态网站
client.put_bucket_website(
    Bucket='myweb-1250000000',
    WebsiteConfiguration={
        'IndexDocument': {'Suffix': 'index.html'},
        'ErrorDocument': {'Key': 'error.html'}
    }
)

# 配合 CDN 加速
# 1. 创建 CDN 加速域名：img.example.com → bucket-1250000000.cos.ap-guangzhou.myqcloud.com
# 2. CDN 节点缓存静态资源
# 3. 回源走 COS（用 COS 域名作回源 host）
```

## 6. 权限与防盗链

### 6.1 CAM 策略（最小授权）

```json
{
  "version": "2.0",
  "statement": [
    {
      "effect": "allow",
      "action": [
        "cos:PutObject",
        "cos:GetObject",
        "cos:DeleteObject"
      ],
      "resource": [
        "qcs::cos:ap-guangzhou:uid/1250000000:examplebucket-1250000000/uploads/*"
      ]
    }
  ]
}
```

### 6.2 防盗链

```python
client.put_bucket_referer(
    Bucket='myweb-1250000000',
    RefererConfiguration={
        'Status': 'Enabled',
        'DomainList': {'Domain': ['example.com', '*.example.com']},
        'EmptyReferConfiguration': 'Deny'
    }
)
```

### 6.3 临时凭证（前端直传）

```python
# 后端签发 STS 给前端
from sts.sts import Sts

sts = Sts()
config = {
    'url': 'https://sts.tencentcloudapi.com/',
    'domain': 'sts.tencentcloudapi.com',
    'proxy': '',
    'secret_id': '...',
    'secret_key': '...',
    'bucket': 'examplebucket-1250000000',
    'region': 'ap-guangzhou',
    'allow_prefix': ['uploads/*'],
    'duration_seconds': 3000,
}
result = sts.get_credential(config)
# 返回给前端的临时 ak/sk/token
```

## 7. 数据处理

COS 集成数据万象 CI（Cloud Infinite）：

| 能力 | URL 示例 |
|------|----------|
| 图片缩放 | `?imageMogr2/thumbnail/200x200` |
| Webp | `?imageMogr2/format/webp` |
| 人脸识别 | `?ci-process=DetectFace` |
| 文档转 PDF | `?ci-process=doc-preview` |
| 视频转码 | 单独的服务：媒体处理 MPS |
| 内容审核 | `?ci-process=audit-img` |

## 8. 跨地域复制

```python
client.put_bucket_replication(
    Bucket='src-1250000000',
    ReplicationConfiguration={
        'Role': 'qcs::cam::uin/...:rolename/...',
        'Rules': [{
            'ID': 'rule-1',
            'Status': 'Enabled',
            'Prefix': '',
            'Destination': {
                'Bucket': 'qcs::cos:ap-shanghai::dst-1250000000',
                'StorageClass': 'STANDARD'
            }
        }]
    }
)
```

需要 CAM 角色授权，目标 bucket 也得开复制规则。

## 9. 监控告警

COS 提供 `RequestCount`、`ErrorCount`、`Traffic` 指标，可在**腾讯云监控**（CM）配置告警：

```yaml
# 告警规则示例
metric: COS Request4xxCount
period: 1m
threshold: 100
notify: SMS, email
```

## 10. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| Bucket 必带 APPID | "bucket=名+APPID" |
| 内网免流（VPC 内） | "内网=免费" |
| 归档深度分层 | "深度冷归档 5 级" |
| 数据万象 = CI | "CI=图片处理" |
| 微信生态深度集成 | "微信=无缝" |

## 参考

- COS 文档：<https://cloud.tencent.com/document/product/436>
- 数据万象 CI：<https://cloud.tencent.com/document/product/460>
- 临时密钥 STS：<https://cloud.tencent.com/document/product/436/14048>