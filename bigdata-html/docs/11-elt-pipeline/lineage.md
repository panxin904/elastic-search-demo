---
title: 数据血缘
---

# 数据血缘

数据血缘（Data Lineage）追踪数据从源系统经过 ETL/ELT 到下游消费的全链路流转关系，是数据治理与可观测性的核心。

## 为什么需要血缘

- **故障定位**：下游数据异常时，快速定位上游哪个任务/源表出问题
- **影响分析**：上游表 schema 变更时，识别所有受影响的下游任务和报表
- **合规审计**：满足 GDPR / 数据安全法规对"谁的数据流向哪里"的追溯要求
- **数据资产盘点**：自动生成数据资产清单（哪些表被消费、哪些字段是核心）

## 血缘类型

- **表级血缘**：字段 → 字段（SQL 解析 / dbt manifest）
- **任务级血缘**：DAG 节点上下游（Airflow / DolphinScheduler）
- **数据集市血缘**：主题域 → 应用（DataHub / Atlas 元数据）

## 两个视角

- **ELT 视角**（本章）：dbt / Airflow / DataHub 等调度层血缘
- **流式视角**：[Kafka 流式血缘](/07-kafka-streaming/lineage) — Kafka Connect / Schema Registry / Stream lineage

## 工具对比

| 工具 | 适用场景 | 血缘粒度 |
|------|---------|---------|
| dbt | ELT SQL 任务 | 表级 + 列级 |
| Airflow | 通用 DAG 调度 | 任务级 |
| DataHub | 元数据平台 | 表/列/任务 |
| OpenLineage | 开放标准 | 跨工具统一 |

## 实践建议

1. **从关键报表反推**：先标记 5-10 个核心报表，沿下游反查上游链路
2. **dbt 自动捕获**：开启 dbt `generate_manifest` + DataHub dbt ingestion
3. **Airflow OpenLineage**：通过 Marquez 或 DataHub 自动捕获 task 血缘
4. **定期巡检**：周/月度 review 未覆盖的下游表，及时补血缘

详见 [Kafka 流式血缘章节](/07-kafka-streaming/lineage)。


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

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
