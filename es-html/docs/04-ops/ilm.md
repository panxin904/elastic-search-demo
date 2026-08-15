---
title: ILM 生命周期
category: ops
graphNodeId: ilm
---

<span class="kg-badge kg-badge-ops">运维层</span>

# ILM 索引生命周期

## 📌 一句话定义
ILM (Index Lifecycle Management) 自动管理索引从**创建到删除**的整个生命周期，按**阶段**触发动作。

## 🧱 四阶段 (Phase)

| 阶段 | 典型操作 |
|---|---|
| **hot** | 频繁写入、查询 |
| **warm** | 不再写入、偶尔查询 |
| **cold** | 极少查询、可降配 |
| **delete** | 自动删除 |

## 🔧 创建 ILM 策略

```http
PUT /_ilm/policy/products-policy
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {
            "max_age":   "7d",
            "max_size":  "50gb",
            "max_docs":  200000000
          }
        }
      },
      "warm": {
        "min_age": "30d",
        "actions": {
          "forcemerge": { "max_num_segments": 1 },
          "shrink":     { "number_of_shards": 1 }
        }
      },
      "cold": {
        "min_age": "60d",
        "actions": {
          "freeze": {}
        }
      },
      "delete": {
        "min_age": "90d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
```

## 📋 应用到索引模板

```http
PUT /_index_template/products-template
{
  "index_patterns": ["products-*"],
  "template": {
    "settings": {
      "number_of_shards": 2,
      "number_of_replicas": 1,
      "index.lifecycle.name": "products-policy"
    }
  }
}
```

## 🔄 Rollover 机制

写索引使用**写别名**，触发 rollover 时自动新建索引并切换别名：

```http
POST /products-000001/_rollover
{
  "conditions": {
    "max_age":   "7d",
    "max_size":  "50gb"
  }
}
```

返回：
```json
{
  "acknowledged": true,
  "old_index": "products-000001",
  "new_index": "products-000002",
  "rolled_over": true
}
```

## 🔍 查看 ILM 状态

```bash
GET /products-*/_ilm/explain
```

返回每个索引的当前阶段、动作、进度。

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="ilm" :height="400" />

## 📚 延伸阅读
- [索引模板](/04-ops/index-template)
- [别名 Alias](/04-ops/alias)
- [Snapshot 备份](/04-ops/snapshot)
