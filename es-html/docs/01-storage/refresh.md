---
title: Refresh 机制
category: storage
graphNodeId: refresh
---

<span class="kg-badge kg-badge-storage">存储层</span>

# Refresh 机制

## 📌 一句话定义
Refresh 是 ES 将**内存中的文档**转换为**可搜索的 segment**的过程，是 ES "**准实时 (NRT, Near Real-Time)**" 的核心。

## ⏱️ 默认行为

| 维度 | 默认值 |
|---|---|
| Refresh 间隔 | **1 秒** |
| 触发时机 | 定时 + `_refresh` 显式调用 |

## 🔄 Refresh 时序

```
T+0.0s: 写入文档 → Memory Buffer
T+0.1s: 写入 Translog
T+1.0s: Refresh → 创建新 Segment → 文档可搜
T+30m:  Flush → Segment 持久化 + Translog 清理
```

## 🔧 手动 Refresh

```http
POST /products/_refresh
```

> 💡 **本项目测试代码中**就有显式 refresh，避免准实时延迟导致测试断言失败：
> ```java
> client.indices().refresh(r -> r.index(INDEX_NAME));
> ```

## ⚙️ 调整 Refresh 间隔

```http
PUT /products/_settings
{
  "index.refresh_interval": "30s"   // 写入密集场景，调大降低开销
}
```

| 场景 | 建议值 |
|---|---|
| 实时搜索（默认） | `1s` |
| 写入密集（log） | `5s` / `30s` / `-1`（手动） |
| 批量导入 | `30s` 或 `-1`（导入完再 refresh） |

## ⚠️ Refresh 越频繁 → 性能越差

每次 refresh 都创建新 segment，过多 segment 会：
- 占用更多文件描述符
- 降低 search 性能（要扫更多段）
- 加重后续 merge 负担

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="refresh" :height="400" />

## 📚 延伸阅读
- [段 Segment](/01-storage/segment)
- [Translog](/01-storage/translog)
