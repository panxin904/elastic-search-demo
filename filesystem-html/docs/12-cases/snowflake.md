---
title: Snowflake 云数仓
---

# Snowflake — 云原生数仓的存储架构

> <span class="kg-badge kg-badge--cases">企业案例</span>
> S3 + 微服务 · 多云 · 计算存储分离

Snowflake 是 2020 年最成功的 SaaS 公司之一，**云原生数据仓库**的开创者。它的存储架构是"计算 / 存储完全分离"的典范。

## 1. Snowflake 规模

| 指标 | 数值 |
|------|------|
| 客户 | 7000+ |
| 数据 | EB 级 |
| 每日 query | 数十亿 |
| 云 | AWS / Azure / GCP |

## 2. 核心架构

```
┌────────────────────────────────────────────┐
│  Cloud Services Layer（控制平面）            │
│  - 解析 SQL、认证、元数据                   │
└────────────────┬───────────────────────────┘
                 │
┌────────────────▼───────────────────────────┐
│  Compute Layer（虚拟仓库）                  │
│  - X-Small / Small / Medium / ...           │
│  - 弹性伸缩，按秒计费                       │
└────────────────┬───────────────────────────┘
                 │
┌────────────────▼───────────────────────────┐
│  Storage Layer（对象存储 + 元数据服务）     │
│  - S3 / Azure Blob / GCS                  │
│  - 自动压缩、微分区                       │
└────────────────────────────────────────────┘
```

## 3. 存储层细节

### 3.1 数据布局

```
表 → 微分区（Micro-Partition） → 列存文件

每个 Micro-Partition：
- 50-500 MB 压缩后
- 列存格式
- 内置统计（min/max/nulls/count）
- 不可变（immutable）
```

### 3.2 压缩与加密

```text
原始数据
   │
   ▼ Snowflake 内部压缩
micro-partition
   │
   ▼ 加密（AES-256）
S3 对象
   │
   ▼ SSE-KMS / SSE-S3
物理存储
```

### 3.3 零拷贝 clone

```sql
-- 复制 TB 级表，瞬间完成
CREATE TABLE mydb.my_clone CLONE mydb.original;

-- 底层是 copy-on-write：仅写入时复制
```

## 4. 数据安全

| 机制 | 说明 |
|------|------|
| **自动加密** | 写入前 AES-256 加密 |
| **客户密钥** | BYOK（Bring Your Own Key） |
| **Time Travel** | 90 天可恢复 |
| **Fail-safe** | 额外 7 天（Snowflake 内部） |

## 5. 实战：Time Travel

```sql
-- 看过去某时的数据
SELECT * FROM mydb.mytable AT (TIMESTAMP => '2026-01-01 12:00:00'::TIMESTAMP);

-- 恢复
CREATE TABLE mydb.restored CLONE mydb.mytable BEFORE (STATEMENT => 'query-id');

-- 保留期
ALTER TABLE mydb.mytable SET DATA_RETENTION_TIME_IN_DAYS = 90;
```

## 6. 多云架构

```text
AWS (primary)         Azure           GCP
   │                   │               │
   ├─ S3               ├─ Blob         ├─ GCS
   ├─ Compute          ├─ VM           ├─ VM
   └─ Cross-cloud replication (via customer request)
```

- **同一份数据**可在三家云
- 通过**复制组**同步
- 适合地理隔离合规要求

## 7. 零管理

Snowflake 的核心理念：

- **无索引**：自动统计 + 微分区
- **无调优**：自动选择大小
- **无备份**：Time Travel + 异地复制
- **无备份运维**：全自动

客户**完全不用**关心底层存储。

## 8. 实战：性能优化

```sql
-- 集群键（clustering key）
ALTER TABLE mydb.events CLUSTER BY (dt, user_id);

-- 自动重聚簇（后台任务）
-- 用户不用操心
```

```sql
-- 搜索优化服务（Search Optimization）
ALTER TABLE mydb.events ADD SEARCH OPTIMIZATION ON EQUALITY(user_id);
```

## 9. 与传统数仓对比

| 维度 | Snowflake | Teradata | Hadoop |
|------|----------|----------|--------|
| 存储 | 弹性对象存储 | 本地盘 / SAN | HDFS |
| 计算 | 弹性虚拟仓库 | 固定集群 | YARN |
| 扩容 | 秒级 | 月级 | 周级 |
| 定价 | 按秒 | 长期合同 | 自运维 |
| 管理 | 零管理 | 重 | 极重 |
| 云支持 | **AWS/Azure/GCP** | 私有 | 私有 |

## 10. 经验教训

| 经验 | 说明 |
|------|------|
| **存算分离 = 弹性** | 计算和存储独立扩 |
| **零拷贝 = 强大** | clone / time-travel |
| **多云 = 合规** | 不同地理 / 监管要求 |
| **微分区 = 性能** | 50-500 MB 粒度 |
| **零管理 = 商业化** | 用户关注业务 |

## 11. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| Snowflake = 存算分离 | "存算分=弹性" |
| 微分区 = 列存 | "微分区=快" |
| Time Travel = 容错 | "TimeTravel=90 天" |
| 多云 = 合规 | "多云=全" |
| 零管理 = 商业模式 | "零管理=SaaS" |

## 参考

- Snowflake 文档：<https://docs.snowflake.com/
- Snowflake 白皮书
- The Snowflake Elastic Data Warehouse 论文


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
