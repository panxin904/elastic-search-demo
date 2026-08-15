---
title: Translog
category: storage
graphNodeId: translog
---

<span class="kg-badge kg-badge-storage">存储层</span>

# Translog

## 📌 一句话定义
Translog 是分片级别的**事务日志**，用于节点崩溃后**恢复尚未 flush 到磁盘的数据**。

## 🔄 Translog 工作流

```
Client Write
    ↓
Memory Buffer
    ↓
Translog (顺序写)
    ↓
Refresh (1s) → New Segment (可搜索)
    ↓
Flush (30min) → Segment 持久化 + Translog 截断
```

## ⚙️ Translog 关键配置

```json
PUT /products
{
  "settings": {
    "index.translog.durability": "request",   // 或 "async"
    "index.translog.sync_interval": "5s",
    "index.translog.flush_threshold_size": "512mb"
  }
}
```

| 参数 | 取值 | 说明 |
|---|---|---|
| `durability` | `request`（默认） | 每个请求 fsync，**安全但慢** |
| `durability` | `async` | 异步 fsync，**快但丢数据风险** |

## 🔍 查看 Translog 状态

```http
GET /products/_stats?level=shards
```

返回中包含：
```json
"translog": {
  "operations": 1234,
  "size_in_bytes": 567890,
  "uncommitted_operations": 12
}
```

## 🚨 崩溃恢复

```
节点崩溃 → 重启 → 读取 Translog → 重放未刷盘的写入 → 索引恢复
```

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="translog" :height="400" />

## 📚 延伸阅读
- [段 Segment](/01-storage/segment)
- [Refresh 机制](/01-storage/refresh)
