---
title: 运维层 总览
date: 2026-08-15  # date-auto-injected
---

# 运维层 Ops

运维层关注 ES 的**部署、监控、备份、扩缩容、性能调优**，是生产环境**稳定运行**的关键。

## 🛠️ 部署与调优

| 主题 | 说明 |
|---|---|
| [安装部署](/04-ops/installation) | 单机 / 集群 / Docker |
| [JVM 调优](/04-ops/jvm-tuning) | 堆内存、GC |
| [分片分配](/04-ops/shard-allocation) | 副本与均衡策略 |

## 🏥 监控与诊断

| 主题 | 说明 |
|---|---|
| [集群健康](/04-ops/cluster-health) | green/yellow/red |
| [_cat API](/04-ops/cat-api) | 人类可读 API |
| [慢日志](/04-ops/slow-log) | 慢查询/慢索引 |
| [监控 Cerebro](/04-ops/monitoring) | 集群可视化 |

## 💾 备份与生命周期

| 主题 | 说明 |
|---|---|
| [Snapshot 备份](/04-ops/snapshot) | 集群快照 |
| [ILM 生命周期](/04-ops/ilm) | hot/warm/cold/delete |
| [Curator](/04-ops/curator) | 索引管理工具 |

## ⚙️ 模板与高级操作

| 主题 | 说明 |
|---|---|
| [索引模板](/04-ops/index-template) | 自动套用 settings/mapping |
| [别名 Alias](/04-ops/alias) | 零停机切换 |
| [集群重启](/04-ops/restart) | 滚动重启流程 |

## 🗺️ 本层在图谱中的位置

<KnowledgeGraph mode="full" :height="500" />
