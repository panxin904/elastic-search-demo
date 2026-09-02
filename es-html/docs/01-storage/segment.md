---
title: 段 Segment
date: 2026-08-15  # date-auto-injected
category: storage
graphNodeId: segment
---

<span class="kg-badge kg-badge-storage">存储层</span>

# 段 Segment

![Elasticsearch Segment Merge 流程](/es-segment-merge-flow.svg)

## 📌 一句话定义
段是分片内部的**不可变数据文件**（Lucene Index），是 ES 真正存储倒排索引的物理单位。

## 🔄 段的生成与合并

```
Memory Buffer
  ↓ (Refresh, 默认 1s)
Segment A  ─┐
  ↓ (持续写入)         ─→ Force Merge (合并)
Segment B  ─┤
  ↓
Segment C  ─┘
```

## ⚙️ Refresh 与 Flush

| 操作 | 频率 | 作用 |
|---|---|---|
| **Refresh** | 默认 1s | Memory Buffer → 新 Segment（可搜索） |
| **Flush** | 30min 或 translog 满 | Segment 持久化 + Translog 清理 |

## 🔧 手动控制

```http
# 强制刷新，使最新文档立即可搜
POST /products/_refresh

# 强制 flush（持久化）
POST /products/_flush

# 合并段（force merge）
POST /products/_forcemerge?max_num_segments=1
```

## ⚠️ 段过多的危害

- **文件描述符耗尽**：每个段都是独立文件
- **搜索性能下降**：查询要扫描更多段
- **内存压力**：每个段都有独立的内存数据结构

> 💡 建议：写入密集型索引，定期 force merge；查询密集型，保留多个段

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="segment" :height="400" />

## 📚 延伸阅读
- [分片 Shard](/01-storage/shard)
- [Refresh 机制](/01-storage/refresh)
- [Translog](/01-storage/translog)

<!-- svg-injected:do-not-edit -->

![inverted index](/inverted-index.svg)
