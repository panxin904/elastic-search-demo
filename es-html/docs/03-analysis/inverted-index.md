---
title: 倒排索引
date: 2026-08-15  # date-auto-injected
category: analysis
graphNodeId: inverted-index
---

<span class="kg-badge kg-badge-analysis">分析层</span>

# 倒排索引 Inverted Index

## 📌 一句话定义
倒排索引是**从 term 到文档列表**的映射结构，是 ES/Lucene 实现快速搜索的核心数据结构。

## 🔄 与正排索引对比

| 类型 | 映射方向 | 用途 |
|---|---|---|
| 正排索引 | 文档 → 字段 → 词 | 重建原文 |
| **倒排索引** | **词 → 文档列表** | **快速搜索** |

## 📊 倒排表示例

3 篇文档：
```
Doc 1: 机械键盘 红轴
Doc 2: 机械键盘 茶轴
Doc 3: 笔记本 RGB
```

倒排索引：
| Term | 文档列表 | 词频 |
|---|---|---|
| 机械 | [1, 2] | 2 |
| 键盘 | [1, 2] | 2 |
| 红轴 | [1] | 1 |
| 茶轴 | [2] | 1 |
| 笔记本 | [3] | 1 |
| rgb | [3] | 1 |

## 🔍 搜索 "机械"

1. 在 term 字典中找到 `机械` → 文档列表 `[1, 2]`
2. 取 `Doc 1`、`Doc 2` 评分
3. 返回结果

## 🧱 Lucene 内部结构

```
Segment
├── Postings (倒排表)
│   ├── Term "机械"
│   │   ├── DocID: 1, Freq: 1, Positions: [0]
│   │   └── DocID: 2, Freq: 1, Positions: [0]
│   └── Term "键盘" ...
├── Term Dictionary (FST 索引)
├── Stored Fields (_source)
└── Doc Values (排序/聚合列存)
```

### 关键数据结构

| 数据结构 | 用途 |
|---|---|
| **FST (Finite State Transducer)** | Term 字典的快速查找 |
| **Skip List** | postings 列表的快速跳跃 |
| **Roaring Bitmap** | 文档 ID 集合（聚合/过滤） |
| **BKD Tree** | 数值/地理/范围的快速查询 |

## ⚙️ 索引选项

```json
{
  "properties": {
    "name": {
      "type": "text",
      "index_options": "offsets"   // docs / freqs / positions / offsets
    }
  }
}
```

| options | 包含 | 用途 |
|---|---|---|
| `docs` | 仅文档号 | 基础 |
| `freqs` | + 词频 | 影响评分 |
| `positions` | + 位置 | phrase query |
| `offsets` | + 偏移 | 高亮 (fvh) |

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="inverted-index" :height="400" />

## 📚 延伸阅读
- [Analyzer 分析器](/03-analysis/analyzer)
- [BM25](/03-analysis/bm25)
- [段 Segment](/01-storage/segment)
