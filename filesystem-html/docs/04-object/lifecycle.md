---
title: 生命周期管理
date: 2026-08-15  # date-auto-injected
---

# 对象生命周期 — 让数据自动老化

> <span class="kg-badge kg-badge--object">对象存储</span>
> 标准 → 低频 → 归档 · 自动降本

对象存储的成本随"访问频率"变化极大。Amazon S3 标准存储 0.023 美元/GB/月，Glacier Deep Archive 只有 0.00099 美元/GB/月——**差 23 倍**。

生命周期策略让数据**自动从热到冷**。这是对象存储最省钱的开关。

## 1. 生命周期三阶段

```
┌──────────┐    30 天    ┌──────────┐    90 天    ┌──────────┐    365 天  ┌──────────┐
│ Standard │ ─────────→ │ Standard │ ──────────→ │ Glacier  │ ──────────→ │  删除    │
│  (热)    │             │  -IA     │             │ (归档)   │             │ (过期)   │
└──────────┘             └──────────┘             └──────────┘             └──────────┘
```

**三个动作**：

| 动作 | 含义 | 何时用 |
|------|------|--------|
| Transition | 把对象移到另一个存储类 | 访问频率变化 |
| Expiration | 把对象删除 | 不再需要 |
| AbortIncompleteMultipartUpload | 清理未完成分片上传 | 防止孤片 |

## 2. 实战：AWS S3 生命周期

```xml
<LifecycleConfiguration>
  <Rule>
    <ID>log-archive</ID>
    <Status>Enabled</Status>
    <Filter>
      <Prefix>logs/</Prefix>
    </Filter>
    <Transition>
      <Days>30</Days>
      <StorageClass>STANDARD_IA</StorageClass>
    </Transition>
    <Transition>
      <Days>90</Days>
      <StorageClass>GLACIER</StorageClass>
    </Transition>
    <Expiration>
      <Days>365</Days>
    </Expiration>
    <AbortIncompleteMultipartUpload>
      <DaysAfterInitiation>7</DaysAfterInitiation>
    </AbortIncompleteMultipartUpload>
  </Rule>
</LifecycleConfiguration>
```

## 3. 实战：阿里云 OSS 生命周期

通过 ossutil：

```bash
cat > lifecycle.json <<EOF
{
  "Rule": [
    {
      "ID": "log-archive",
      "Status": "Enabled",
      "Prefix": "logs/",
      "Expiration": {"Days": 365},
      "Transitions": [
        {"Days": 30, "StorageClass": "IA"},
        {"Days": 90, "StorageClass": "Archive"}
      ],
      "AbortMultipartUpload": {"Days": 7}
    }
  ]
}
EOF

ossutil set-bucket-lifecycle oss://my-bucket lifecycle.json
```

## 4. 实战：MinIO 生命周期（mc）

```bash
# 1. 创建生命周期配置
cat > lifecycle.json <<EOF
{
  "Rules": [
    {
      "ID": "auto-tiering",
      "Status": "Enabled",
      "Filter": {"Prefix": "logs/"},
      "Transition": {
        "Days": 30,
        "StorageClass": "STANDARD_IA"
      },
      "Expiration": {"Days": 365}
    }
  ]
}
EOF

# 2. 应用
mc ilm import local/mybucket < lifecycle.json

# 3. 看当前规则
mc ilm ls local/mybucket
```

MinIO 用服务端 ILM action（默认 Standard ↔ EC）。如果想接入 Glacier，需要用 NAS 模式或对接 AWS。

## 5. 取回与解冻成本

| 存储类 | 取回延迟 | 取回费用 | 最低存储时间 |
|--------|----------|----------|-------------|
| S3 Standard | 即时 | 无 | 无 |
| S3 Standard-IA | 即时 | 0.01/GB | 30 天 |
| S3 Glacier Instant | 即时 | 0.03/GB | 90 天 |
| S3 Glacier Flexible | 分钟-小时 | 0.01~0.03/GB | 90 天 |
| S3 Glacier Deep Archive | 小时级 | 0.02/GB | 180 天 |
| 阿里 Archive | 1 分钟 | 0.06/GB | 60 天 |
| 阿里 Cold | 小时 | 0.20/GB | 180 天 |

**关键**：提前删除未满最低存储时间 = **按最低时间收费**。所以"30 天 IA"在 30 天前删也是按 30 天算。

## 6. 取回模式（以 AWS Glacier 为例）

| Tier | 延迟 | 适用 |
|------|------|------|
| Expedited | 1~5 分钟 | 紧急 |
| Standard | 3~5 小时 | 通常 |
| Bulk | 5~12 小时 | 预算 |

阿里 Archive：Expedited=1 分钟、Standard=5 分钟、Bulk=小时。

## 7. 实战建议

### 7.1 数据分类

按"温度"把数据分层：

| 类型 | 例子 | 推荐存储类 |
|------|------|-----------|
| 7 天内活跃 | 用户上传头像、订单文件 | Standard |
| 30+ 天 | 业务日志归档 | Standard-IA |
| 90+ 天 | 历史订单、备份快照 | Glacier Instant |
| 1 年+ | 合规归档 | Glacier Deep Archive |

### 7.2 别把"频繁访问"的对象降级

常见踩坑：把静态网站资源扔进 IA，结果 CDN 回源 → 取回费爆炸。

**对策**：把"30 天访问次数 > 1"的对象**排除** IA 规则（用 S3 Analytics 看访问模式）。

### 7.3 生命周期 + 版本

如果开启 Versioning：

```xml
<Rule>
  <Filter>
    <And>
      <Prefix>logs/</Prefix>
      <ObjectSizeGreaterThan>1024</ObjectSizeGreaterThan>
    </And>
  </Filter>
  <NoncurrentVersionTransition>
    <NoncurrentDays>30</NoncurrentDays>
    <StorageClass>GLACIER</StorageClass>
  </NoncurrentVersionTransition>
  <NoncurrentVersionExpiration>
    <NoncurrentDays>365</NoncurrentDays>
  </NoncurrentVersionExpiration>
</Rule>
```

历史版本单独走归档与过期。

## 8. 与 WORM 合规归档

金融、医疗、政府场景要求数据**不可删** → 用 Object Lock：

- **Governance Mode**：有特殊权限的人可改
- **Compliance Mode**：任何人都不可删，到期前改不动
- 保留期 1~70 年

与生命周期 **Expiration 冲突** → 保留期优先。

## 9. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| 三动作：迁移 / 删除 / 清理孤片 | "Transition / Expire / Abort" |
| 30/90/365 是经典节奏 | "30→IA 90→Archive 365→删" |
| 最低存储时间门槛 | "未满=按满收" |
| 取回按 Tier 收费 | "急用=贵" |
| 版本 + 生命周期组合 | "历史版本单独走" |

## 参考

- AWS S3 生命周期配置
- 阿里云 OSS 生命周期文档
- MinIO Object Lifecycle