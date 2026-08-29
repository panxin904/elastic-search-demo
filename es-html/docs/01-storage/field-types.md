---
title: 字段类型
date: 2026-08-15  # date-auto-injected
category: storage
graphNodeId: field-types
---

<span class="kg-badge kg-badge-storage">存储层</span>

# 字段类型 Field Types

ES 7.x 字段类型分为**六大族系**：

## 📝 字符串族

| 类型 | 用途 | 分词 |
|---|---|---|
| `text` | 全文检索 | ✅ 是 |
| `keyword` | 精确匹配、聚合、排序 | ❌ 否 |
| `wildcard` | 通配符与正则（7.9+） | ❌ 否 |

> ⚠️ ES 7 已**废弃** `string` 类型；现有 5.x 索引需迁移。

## 🔢 数值族

| 类型 | 范围 |
|---|---|
| `long` | -2^63 ~ 2^63-1 |
| `integer` | -2^31 ~ 2^31-1 |
| `short` | -32768 ~ 32767 |
| `byte` | -128 ~ 127 |
| `double` | 双精度浮点 |
| `float` | 单精度浮点 |
| `half_float` | 半精度 |
| `scaled_float` | 定点（如价格：`scaling_factor: 100`） |

## 📅 日期族

| 类型 | 说明 |
|---|---|
| `date` | 默认格式 `strict_date_optional_time\|\|epoch_millis` |
| `date_nanos` | 纳秒精度 |

```json
{ "created_at": { "type": "date", "format": "yyyy-MM-dd HH:mm:ss||epoch_millis" } }
```

## ✅ 布尔族

```json
{ "is_active": { "type": "boolean" } }
```

## 📦 对象 / 嵌套族

| 类型 | 特点 |
|---|---|
| `object` | 默认扁平化，丢失关联 |
| `nested` | 保留数组内对象关联（独立索引） |
| `join` | 父子文档 |

### nested 示例

```json
{
  "comments": {
    "type": "nested",
    "properties": {
      "user":   { "type": "keyword" },
      "rating": { "type": "integer" }
    }
  }
}
```

## 🌍 特殊类型

| 类型 | 用途 |
|---|---|
| `geo_point` | 地理位置（经纬度） |
| `geo_shape` | 复杂地理形状 |
| `ip` | IPv4 / IPv6 |
| `binary` | Base64 二进制 |
| `completion` | 自动补全 |
| `dense_vector` | 向量（用于 kNN） |

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="field-types" :height="400" />

## 📚 延伸阅读
- [映射 Mapping](/01-storage/mapping)
- [Analyzer 分析器](/03-analysis/analyzer)
