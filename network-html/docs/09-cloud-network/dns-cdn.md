---
title: 云上 DNS 与 CDN
---

# 云上 DNS 与 CDN

<div class="nt-badge nt-badge-cloud">云网络</div>
<div class="nt-badge nt-badge-cases">实战</div>

云上 DNS 提供智能解析与负载均衡，CDN 在全球边缘节点缓存静态内容，两者共同支撑大规模网站的高可用与高性能。

## 1. 云 DNS 服务

| 厂商 | 产品 |
| --- | --- |
| AWS | Route 53 |
| Azure | Azure DNS |
| GCP | Cloud DNS |
| 阿里 | 云解析 DNS / PrivateZone |
| 腾讯 | DNSPod |
| Cloudflare | DNS |

## 2. Route 53 路由策略

| 策略 | 描述 |
| --- | --- |
| Simple | 单值 |
| Weighted | 加权 |
| Latency | 就近 |
| Failover | 主备 |
| Geolocation | 地理位置 |
| Geoproximity | 地理邻近 + 偏差 |
| Multi-value | 多 IP 轮询 |
| IP-based | 基于客户端 IP |

## 3. Private DNS

- VPC 内私有域（internal.example.com）
- 跨账号共享
- 内部服务发现
- Split-horizon：内外不同解析

```
外部: example.com → 公网 IP
内部: example.com → 10.0.1.10
```

## 4. 健康检查

- HTTP / HTTPS / TCP
- 跨区域检查
- 失败自动切换
- 与流量策略联动

```json
{
  "IPAddress": "1.2.3.4",
  "Port": 80,
  "Type": "HTTP",
  "ResourcePath": "/health",
  "FailureThreshold": 3,
  "RequestInterval": 30
}
```

## 5. 云 CDN 服务

| 厂商 | 产品 |
| --- | --- |
| AWS | CloudFront |
| Azure | Azure CDN / Front Door |
| GCP | Cloud CDN |
| 阿里 | 阿里云 CDN |
| 腾讯 | 腾讯云 CDN |
| Cloudflare | Cloudflare CDN |

## 6. CloudFront 核心

| 概念 | 描述 |
| --- | --- |
| Distribution | 加速域名 |
| Origin | 源站（S3、ALB、EC2、自定义） |
| Behavior | 路径路由规则 |
| Edge Location | 全球边缘节点 |
| Price Class | 价格档位（仅美/欧/全球） |
| Lambda@Edge | 边缘运行代码 |
| Origin Shield | 源站保护层 |

## 7. 缓存键与行为

```
Path Pattern: /static/*
Viewer Protocol: Redirect HTTP to HTTPS
Cache Policy: CachingOptimized
Origin Request Policy: CORS-S3Origin
Compress: Yes
```

## 8. 签名 URL / Cookie

- 私有内容分发
- 临时访问凭证
- 避免直连源站

```
https://cdn.example.com/video.mp4
?Expires=1700000000
&Signature=abc...
&Key-Pair-Id=APKA...
```

## 9. WAF 集成

CloudFront + AWS WAF：

| 规则 | 防护 |
| --- | --- |
| AWSManagedRulesCommonRuleSet | OWASP Top 10 |
| AWSManagedRulesSQLiRuleSet | SQL 注入 |
| AWSManagedRulesKnownBadInputsRuleSet | 已知攻击 |
| Rate-based rule | 限流 |
| IP 黑白名单 | 基础 |
| Bot Control | 机器人 |

## 10. 实时日志

- Kinesis Data Stream
- 字段：timestamp, edge location, status, url, ua...

## 11. Front Door（Azure 全局 LB）

- L7 负载均衡
- WAF 集成
- 路由：path-based、host-based
- 自动扩缩

## 12. Cloud WAN / Global Accelerator

- 全球骨干网
- Anycast 入口
- 跨区域加速

## 13. 实战：CloudFront 部署

```bash
# 创建 distribution
aws cloudfront create-distribution \
  --origin-domain-name example-bucket.s3.amazonaws.com \
  --default-root-object index.html
```

```json
{
  "CallerReference": "2026-08-05",
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3-example",
        "DomainName": "example-bucket.s3.amazonaws.com",
        "S3OriginConfig": { "OriginAccessIdentity": "" }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-example",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": { "Quantity": 2, "Items": ["GET", "HEAD"] },
    "Compress": true,
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": { "Forward": "none" }
    }
  },
  "Enabled": true,
  "PriceClass": "PriceClass_All"
}
```

## 14. 监控

- CloudFront 访问日志
- CloudWatch 指标
- 命中率、源站请求数
- 4xx / 5xx 比率

## 15. 常见面试题

1. **Route 53 路由策略？** 加权、就近、主备、地理位置、多值。
2. **CloudFront 怎么加速？** 全球边缘节点 + 缓存 + Anycast。
3. **签名 URL 作用？** 临时授权访问私有内容。
4. **Origin Shield 是什么？** 减少源站压力，集中缓存层。
5. **Front Door 作用？** Azure 全局 L7 负载均衡 + WAF。
6. **CDN 命中怎么看？** X-Cache 头 / CloudFront 监控。
