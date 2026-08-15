---
title: ES 集群仪表板
---

<span class="kg-badge kg-badge-storage">监控</span>

# ES 集群实时监控仪表板

> 从 4 个维度（集群健康 / 节点指标 / 索引概览 / 分片分布）实时可视化 ES 集群状态。

## 🎯 仪表板用法

1. 配置 **endpoint**（自动持久化到 localStorage）
2. 首次进入页面**自动拉取**数据
3. 点击右上角 **↻ 刷新** 手动更新
4. 勾选 **「自动刷新」** 进入轮询模式（5s / 15s / 30s / 1min 可选）
5. 4 个 sub-tab 切换查看不同维度
6. 表格**点击列头**可排序

<EsClusterDashboard />

## 📡 使用的数据接口

| Sub-tab | 接口 | 用途 |
|---|---|---|
| 🏥 集群健康 | `GET /_cluster/health` | green/yellow/red 状态 + 分片统计 |
| 📈 节点指标 | `GET /_nodes/stats` + `/_cat/master` | JVM Heap/CPU/Load/Disk |
| 📂 索引概览 | `GET /_cat/indices` | 所有索引的大小/文档/分片 |
| 🧩 分片分布 | `GET /_cat/shards` | 分片在节点的分布 |

## ⚠️ CORS 配置

仪表板通过浏览器 fetch 调用 ES，需要 ES 开启 CORS：

```yaml
# elasticsearch.yml
http.cors.enabled: true
http.cors.allow-origin: "*"
http.cors.allow-methods: "OPTIONS, HEAD, GET, POST, PUT, DELETE"
http.cors.allow-headers: "Authorization, Content-Type"
```

## 🎨 颜色规则

| 指标 | 阈值 |
|---|---|
| 🟢 OK | < 70% |
| 🟡 警告 | 70-85% |
| 🔴 危险 | ≥ 85% |
