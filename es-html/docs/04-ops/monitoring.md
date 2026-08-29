---
title: 监控 Cerebro
date: 2026-08-15  # date-auto-injected
category: ops
graphNodeId: monitoring
---

<span class="kg-badge kg-badge-ops">运维层</span>

# 监控 Monitoring

## 📌 监控体系组成

| 组件 | 用途 |
|---|---|
| **Cerebro** | 集群拓扑可视化（开源） |
| **Elasticsearch Monitoring** | 官方指标收集（X-Pack） |
| **Kibana** | 数据可视化 + 监控仪表盘 |
| **Prometheus + Grafana** | 第三方方案 |
| **Elastic HQ** | 另一款开源 UI |

## 🔧 Cerebro 部署

```bash
# Docker 部署
docker run -d --name cerebro \
  -p 9000:9000 \
  -e CEREBRO_PORT=9000 \
  lmenezes/cerebro
```

访问 `http://localhost:9000`，输入 ES 节点地址即可。

## 📊 Cerebro 提供的视图

- 集群拓扑（节点角色、分片分布）
- 索引列表（大小、文档数、分片数）
- 节点指标（heap、CPU、load）
- 协调节点、master 状态

## 🔧 Kibana Stack Monitoring (官方)

启用：
```yaml
xpack.monitoring.collection.enabled: true
```

```http
PUT /_cluster/settings
{
  "persistent": {
    "xpack.monitoring.collection.enabled": true
  }
}
```

Kibana → Stack Monitoring → 即可看到全集群监控仪表盘。

## 📈 关键监控指标

| 类别 | 指标 | 警戒 |
|---|---|---|
| **集群** | status, unassigned_shards | red/yellow |
| **节点** | heap_used_percent, cpu | heap > 85% |
| **搜索** | search.rate, latency | p99 > 1s |
| **索引** | indexing.rate, merge.time | merge 持续高 |
| **JVM** | old.gc.count, gc.time | 频繁 Full GC |
| **磁盘** | disk.used_percent | > 85% |
| **线程池** | rejected, queue | rejected > 0 |

## 📢 告警建议

| 告警 | 阈值 | 级别 |
|---|---|---|
| 集群 yellow/red | 持续 5min | P2 |
| heap_used > 85% | 持续 10min | P1 |
| disk.used > 85% | 持续 5min | P1 |
| master 频繁切换 | 1h 内 3+ 次 | P0 |
| search rejected | 1min > 0 | P0 |

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="monitoring" :height="400" />

## 📚 延伸阅读
- [JVM 调优](/04-ops/jvm-tuning)
- [集群健康](/04-ops/cluster-health)
- [_cat API](/04-ops/cat-api)
