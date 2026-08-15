---
title: IK 分词器
category: analysis
graphNodeId: ik-analyzer
---

<span class="kg-badge kg-badge-analysis">分析层</span>

# IK 分词器

## 📌 一句话定义
IK 是**国内最常用的中文分词器**，由 Elasticsearch-Medcl 维护，支持细粒度和智能两种模式。

## 🔧 安装

```bash
./bin/elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v7.17.10/elasticsearch-analysis-ik-7.17.10.zip
```

> ⚠️ 插件版本必须**与 ES 主版本严格一致**（如 7.17.x 对应 IK 7.17.x）

## 📚 两种分词模式

| 模式 | 行为 | 典型用途 |
|---|---|---|
| `ik_max_word` | 细粒度（拆得最细） | **索引时**（最大化召回） |
| `ik_smart` | 智能（最少词数） | **查询时**（提高精度） |

### 示例：输入 `中华人民共和国国歌`

| 模式 | 输出 |
|---|---|
| `ik_max_word` | `["中华人民共和国", "中华人民", "中华", "华人", "人民共和国", "人民", "共和国", "国歌"]` |
| `ik_smart` | `["中华人民共和国", "国歌"]` |

## 🔧 在 Mapping 中使用

```http
PUT /products
{
  "mappings": {
    "properties": {
      "name": {
        "type": "text",
        "analyzer": "ik_max_word",
        "search_analyzer": "ik_smart"
      }
    }
  }
}
```

## 🔧 扩展词典

**IK 配置目录**: `config/analysis-ik/`

| 文件 | 作用 |
|---|---|
| `IKAnalyzer.cfg.xml` | 主配置（启用/禁用扩展词典） |
| `extra_stopword.dic` | 自定义停用词 |
| `custom_dict.dic` | 自定义词库（如新增网络用语） |

示例配置：
```xml
<!-- IKAnalyzer.cfg.xml -->
<entry key="ext_dict">custom_dict.dic</entry>
<entry key="ext_stopwords">extra_stopword.dic</entry>
```

`custom_dict.dic` 内容（每行一词）：
```
机械键盘
红轴
茶轴
青轴
罗永浩
```

> ⚠️ 修改词典后需要**重启**节点（IK 不支持热加载）

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="ik-analyzer" :height="400" />

## 📚 延伸阅读
- [Analyzer 分析器](/03-analysis/analyzer)
- [pinyin 分词器](/03-analysis/pinyin-analyzer)
- [内置分词器](/03-analysis/builtin-analyzers)
