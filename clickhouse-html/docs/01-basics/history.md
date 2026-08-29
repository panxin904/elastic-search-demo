---
title: ClickHouse 简史与生态
description: 从 2009 年 Yandex.Metrica 内部项目到 2026 年全球 OLAP 事实标准的演进历程
---

# ClickHouse 简史与生态

## 起源（2009-2015）

ClickHouse 诞生于 [Yandex.Metrica](https://metrica.yandex.com/)，俄罗斯最大的网站分析平台（类似 Google Analytics）。2009 年，Yandex 团队遇到一个难题：现成的 OLAP 引擎（Greenplum、Vertica、MonetDB）都无法支撑 PB 级实时聚合查询，单查询延迟常常达到 30 秒甚至 OOM。

团队决定自研一个 OLAP 引擎，目标是：
- **单查询秒级响应**（即使数据量 PB 级）
- **列存压缩**（10-100x 压缩比）
- **向量执行**（SIMD 加速）
- **实时写入**（无需离线导入）

2009 年第一版在 Yandex 内部上线，2012 年支撑了 Yandex.Metrica 的全部业务（200+ 亿事件/天）。2014 年团队开始考虑开源，2016 年 6 月在 GitHub 公开仓库（License: Apache 2.0）。

## 开源演进（2016-2020）

- **2016.06**：GitHub 开源，初始版本 1.0
- **2017**：v1.1 引入 `Kafka` 表引擎，奠定实时数仓基础
- **2018**：v18.x 引入 `MaterializedPostgreSQL` 引擎，开始构建 CDC 生态
- **2019**：v19.x 引入 `Live View`、`Window View`，开始支持流式查询
- **2020**：v20.x 引入 `Dictionary` 增强、`Executable` 表引擎、UDP 协议

这段时间 ClickHouse 在俄罗斯、欧洲企业市场快速渗透，Cloudflare、Uber 等大厂开始迁移日志分析负载。

## 高速发展（2021-2024）

- **2021**：v21.x 引入 `S3` 存算分离能力、`AzureBlobStorage` 引擎
- **2022**：v22.x 引入 `Dynamic` 磁盘选择、`Parallel Replicas`、`Query Cache`
- **2023**：v23.x 引入 `Iceberg`/`DeltaLake`/`Hudi` 数据湖集成、`Workload Scheduling`
- **2024**：v24.x 引入 `MergeTree` 主键支持表达式、`JSON` 类型动态子列

这段时期，ClickHouse 完成了从「单点 OLAP 引擎」到「实时数仓操作系统」的转型。

## 当前状态（2025-2026）

- **GitHub stars**：35k+
- **全球贡献者**：1000+
- **生产用户**：Uber、Cloudflare、字节、京东、B 站、美团、GitHub、Yandex、Cloudflare、Disney 等
- **生态产品**：
  - **客户端**：ch-go (Go 原生)、clickhouse-cpp (C++)、clickhouse-jdbc (Java)、clickhouse-connect (Python)、nodejs-client (Node.js)
  - **运维**：clickhouse-keeper（替代 Zookeeper）、clickhouse-backup、clickhouse-copier、Vector、Altinity Operator
  - **BI 集成**：Grafana、Metabase、Superset、Tableau、DataGrip、DBeaver
  - **数据集成**：dbt-clickhouse、Airbyte Source/Destination、Fivetran
  - **云服务**：ClickHouse Cloud、Altinity.Cloud、阿里云 ClickHouse、腾讯云 ClickHouse

## 国内生态（特别补充）

国内对 ClickHouse 的接受度极高，字节跳动、京东、B 站、美团、网易、滴滴、知乎等头部互联网公司均有大规模生产案例：

- **字节跳动**：抖音埋点 + 广告归因，单集群数千节点
- **京东**：订单履约 + 商品分析，PB 级
- **B 站**：用户行为 + 弹幕反垃圾，替代 Druid
- **美团**：外卖实时监控，多机房容灾
- **网易**：游戏埋点 + 反作弊

中文社区也非常活跃，CSDN、思否、知乎都有大量实战分享。

## 设计哲学

ClickHouse 的设计哲学至今未变：

1. **实时的**：所有数据都可查询，无需离线导入
2. **列存的**：按列压缩、按列向量化、按列 IO
3. **聚合优先**：聚合查询比行查询快 10-100x
4. **零共享（Shared-Nothing）**：每个节点独立存储 + 计算
5. **LSM 风格**：`MergeTree` 系列引擎，后台异步合并
6. **向量化执行**：利用 SIMD 指令集（SSE/AVX/AVX-512）

## 学习路径建议

- **入门**：[overview](./overview.md) 总览
- **安装**：见 [installation](./installation.md)
- **SQL 基础**：见 [02-sql/overview.md](../02-sql/overview.md)
- **表引擎**：见 [03-table-engine/overview.md](../03-table-engine/overview.md)
- **实战场景**：见 [04-olap-scenarios/overview.md](../04-olap-scenarios/overview.md)
- **生态**：见 [05-ecosystem/overview.md](../05-ecosystem/overview.md)
- **对比选型**：见 [06-compare/overview.md](../06-compare/overview.md)


<!-- auto-enrich:do-not-edit -->

## 实战示例

```bash
# TODO: 在此补充本页主题的实战命令
echo "hello"
```

```yaml
# TODO: 配置示例
key: value
```

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |
<!-- auto-enrich:do-not-edit -->
