---
title: Netflix S3 数据湖
---

# Netflix — S3 上 EB 级数据湖

> <span class="kg-badge kg-badge--cases">企业案例</span>
> S3 + Iceberg + IceD  ·  AWS 极致实践

Netflix 是全球最大的流媒体公司，也是 AWS 上**最大的对象存储用户之一**。他们在 S3 上构建了**EB 级数据湖**，是"云时代数据湖架构"的典范。

## 1. Netflix 数据规模

| 指标 | 数值 |
|------|------|
| S3 对象数 | **百亿级** |
| 总容量 | **EB 级** |
| 每日新增 | PB 级 |
| 视频资产 | **多 PB** |
| 每日 query | 数十万次 |

## 2. 架构总览

```
┌─────────────────────────────────────────────┐
│            S3 Data Lake (primary)           │
│         Iceberg table format                │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│     Compute Layer                           │
│  - Spark / Trino / Athena / Iceberg         │
└────────────────┬────────────────────────────┘
                 │
┌────────────────▼────────────────────────────┐
│     Processing / ML                         │
│  - Flink / Spark Streaming / PyTorch / TF   │
└─────────────────────────────────────────────┘
```

## 3. Iceberg 表格式

Netflix 把数据组织成 **Apache Iceberg** 表：

- **ACID**：读写一致
- **Schema evolution**：加列不重写
- **Partition evolution**：改分区策略
- **Time travel**：查历史版本

```python
from pyspark.sql import SparkSession
spark = SparkSession.builder.getOrCreate()

df = spark.read.format("iceberg").load("s3://bucket/db.table")
df.filter("date >= '2026-01-01'").groupBy("...").count()
```

## 4. S3 优化实践

### 4.1 分桶（sharding）

```bash
# prefix 散列避免热 key
s3://bucket/event/dt=2026-01-01/<hash>-<uuid>-event.json
```

### 4.2 生命周期管理

```xml
<LifecycleConfiguration>
  <Rule>
    <ID>log-archive</ID>
    <Filter><Prefix>logs/</Prefix></Filter>
    <Transition><Days>30</Days><StorageClass>STANDARD_IA</StorageClass></Transition>
    <Transition><Days>90</Days><StorageClass>GLACIER</StorageClass></Transition>
    <Expiration><Days>365</Days></Expiration>
  </Rule>
</LifecycleConfiguration>
```

### 4.3 智能分层

```bash
# S3 Intelligent-Tiering（自动迁移热冷）
aws s3api put-bucket-intelligent-tiering-configuration ...
```

## 5. 实战：Netflix 与 S3 一致性

Netflix 在早期遭遇了 S3 的 **eventual consistency** 问题：

- 写入后立刻读：可能读到旧版
- 解决：业务层用"乐观锁 + 版本号"

**S3 在 2020 后变强一致**，Netflix 利用这个改进简化了代码。

## 6. MaaS / Mantis（流处理）

**Mantis**：Netflix 自研的流处理平台。

```java
// Mantis Job
public class RealtimeJob extends MantisJob {
    public Stream<LogEvent> process(Stream<LogEvent> events) {
        return events
            .filter(...)
            .map(...)
            .window(SlidingWindow.of(Duration.ofMinutes(5)));
    }
}
```

- 消费 S3 上的事件
- 写回 S3
- 全链路 S3 + Kafka

## 7. 实战：Keystone 管道

**Keystone**：Netflix 的视频处理管道。

```
源视频 (上传到 S3)
    │
    ▼ 编码（多分辨率）
中间产物 (S3)
    │
    ▼ 加密 + DRM
成品 (S3, 多 CDN 边缘)
    │
    ▼ CDN
用户
```

- **全 S3 中转**
- **PB/天**处理量
- **10 万 + 并行任务**

## 8. IceD（Netflix 自研）

**IceD**：Netflix 自研的 Iceberg 表服务。

- 提供 REST API 访问 Iceberg 表
- 用 S3 作为底层存储
- 集成 Spark / Trino / Athena

## 9. 实战：灾备与多区域

```text
us-east-1 (主)
   │
   ├── 同 Region 多 AZ（默认）
   │
   ├── S3 CRR → us-west-2（异地）
   │
   ├── S3 CRR → eu-west-1（异地）
   │
   └── S3 Glacier Deep Archive（长期）
```

## 10. 学到的经验

| 经验 | 说明 |
|------|------|
| **对象存储 + 表格式 = 数据湖** | 不要"自己造 FS"，用 Iceberg 等 |
| **生命周期分级** | 区分热 / 温 / 冷 数据 |
| **prefix 散列** | 避免单分区热 |
| **弹性是云时代根本** | 不预测容量，按需扩容 |
| **监控 = 业务 SLA** | S3 5xx 立即告警 |

## 11. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| S3 = 数据湖 | "S3=湖" |
| Iceberg = 表格式 | "Iceberg=表" |
| prefix 散列 | "散列=破热" |
| 生命周期分级 | "分级=省本" |
| 多区域复制 | "CRR=异地" |

## 参考

- Netflix Tech Blog：<https://netflixtechblog.com/
- Apache Iceberg 文档
- AWS re:Invent Netflix 演讲


<!-- auto-enrich:do-not-edit -->

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
