---
title: Meta HDFS 演进
date: 2026-08-15  # date-auto-injected
---

# Meta (Facebook) — HDFS 超大规模实践

> <span class="kg-badge kg-badge--cases">企业案例</span>
> HDFS · Exabyte 级 · 从单一存储到分层

Meta（Facebook）是 HDFS 的**最大用户**。他们曾经部署了**全球最大的 HDFS 集群**，单集群达 **EB 级**，后来又演进到分层存储。

## 1. HDFS 在 Meta 的规模

| 指标 | 数值 |
|------|------|
| 单集群节点数 | 1 万+ |
| 数据量 | 1 EB+ |
| 文件数 | 千亿 |
| 每日新增 | PB |
| 业务 | 推荐 / Ads / 视觉 / 搜索 |

## 2. 历史演进

### 2.1 第一代：单体 HDFS

```
单一 HDFS 集群
- NameNode 是瓶颈
- 单机房
- 万级节点
```

**问题**：NameNode 内存爆炸、扩展性差、单机房故障。

### 2.2 Federation（联邦）

```
多 NameNode（每个管部分 namespace）
共享 DataNode 集群
```

- NameNode 拆分
- Namespace 划分（业务 / 用户）
- 解决 NameNode 内存问题

### 2.3 Tiered Storage（分层存储）

```
HDFS 改名 = 内部用 Alluxio / 自研

冷数据 → COS / 自研 Blob 存储
热数据 → HDFS（高性能盘）
```

Meta 后来推出 **Tectonic**（自研 Blob 存储）：

- 类似 S3 的对象存储
- 与 HDFS 兼容 API
- 多 AZ 副本
- EC 默认开启

## 3. Tectonic 架构

```
┌──────────────────────────────────┐
│  HDFS API（兼容层）              │
└────────────┬─────────────────────┘
             │
┌────────────▼─────────────────────┐
│  Tectonic（Meta 自研对象存储）   │
│  - 多 AZ EC                     │
│  - 元数据服务                   │
└────────────┬─────────────────────┘
             │
┌────────────▼─────────────────────┐
│  物理层（多机房 / 多 Region）    │
└──────────────────────────────────┘
```

## 4. 实战：Meta 的 EC 改造

HDFS 早期是 3 副本 → 100% 空间开销。

Meta 的策略：

- **热数据**：3 副本（推荐 / Ads）
- **温数据**：EC 6+3（50% 空间节省）
- **冷数据**：EC 12+4（33% 空间节省）

```
总空间节省：从 100% → 平均 40-50% 空间开销
```

## 5. 实战：HDFS Federation

```xml
<configuration>
  <property>
    <name>dfs.nameservices</name>
    <value>ns1,ns2,ns3</value>
  </property>
  <property>
    <name>dfs.namenode.rpc-address.ns1</name>
    <value>nn1.example.com:8020</value>
  </property>
</configuration>
```

- 客户端 mount 时用 nameservice ID
- 每个 NameNode 管自己 namespace 子集

## 6. 实战：Meta 的数据湖（Lakehouse）

Meta 用 **Iceberg** + **Tectonic** 构建 Lakehouse：

```
Iceberg 表
   │
   ▼ 存储在 Tectonic
   │
   ▼ 查询引擎
   │
Presto / Spark / Hive
```

- 数据科学家用 Presto 直接查
- ML pipeline 用 Spark 读
- 共用同一份数据

## 7. 性能数据

| 场景 | 吞吐 |
|------|------|
| HDFS 批量读 | **5 GB/s** 单 job |
| 写吞吐（3 副本） | 1.5 GB/s |
| EC 写 | 800 MB/s |
| Tectonic 批量读 | 10+ GB/s |

## 8. 故障经验

| 故障 | 教训 |
|------|------|
| NameNode OOM | 不能把过多小文件丢入 HDFS |
| DataNode 大量挂 | 网络问题比硬盘故障多 |
| 副本重建风暴 | 控制 background replication |
| 文件 lock | 短事务 |
| DataNode 元数据不一致 | fsck / 重新 balance |

## 9. Meta 与 Presto

Meta 也维护 Presto：

```
HDFS / Tectonic
   │
   ▼
Presto SQL
   │
   ▼ 内部产品（数据科学家 / 工程师）
```

- Presto 是 Meta 内部**事实标准**的查询引擎
- 比 Hive 快 10-100 倍
- Meta 用 Presto 跑海量即席查询

## 10. 经验教训

| 经验 | 说明 |
|------|------|
| **元数据是瓶颈** | NameNode / QuarkDB 必须 HA |
| **EC 节省空间** | 冷数据必用 |
| **Lakehouse** | Iceberg + 对象存储 |
| **多云 / 多机房** | 跨数据中心复制 |
| **计算存储分离** | 避免资源浪费 |

## 11. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| 单集群达 EB | "EB=实战" |
| Federation 解元数据 | "Federation=扩展" |
| EC 冷数据省钱 | "EC=省本" |
| Lakehouse = Iceberg | "Lakehouse=新代" |
| 存算分离 = 弹性 | "存算分=未来" |

## 参考

- Meta 工程博客
- 《HDFS Architecture》 Apache
- 《Presto: SQL on Everything》 Meta 论文
- 《Tectonic》 Meta 论文