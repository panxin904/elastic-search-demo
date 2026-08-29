---
title: pinyin 分词器
date: 2026-08-15  # date-auto-injected
category: analysis
graphNodeId: pinyin-analyzer
---

<span class="kg-badge kg-badge-analysis">分析层</span>

# pinyin 分词器

## 📌 一句话定义
pinyin 分词器将**中文转为拼音**，常用于**拼音搜索**场景（如"罗永浩" → "luoyonghao"）。

## 🔧 安装

```bash
./bin/elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-pinyin/releases/download/v7.17.10/elasticsearch-analysis-pinyin-7.17.10.zip
```

## 🔧 基础用法

```http
PUT /products
{
  "mappings": {
    "properties": {
      "name": {
        "type": "text",
        "analyzer": "pinyin"
      }
    }
  }
}
```

输入：`"机械键盘"`
输出：`["ji", "xie", "jian", "pan", "jixie", "jianpan"]`

## 🎯 拼音搜索场景

### multi-field：中文 + 拼音

```http
PUT /products
{
  "mappings": {
    "properties": {
      "name": {
        "type": "text",
        "analyzer": "ik_max_word",
        "fields": {
          "pinyin": {
            "type": "text",
            "analyzer": "pinyin"
          }
        }
      }
    }
  }
}
```

这样查询时：
- 中文：搜"键盘" → 命中
- 拼音：搜"jianpan" → 命中
- 拼音首字母：搜"jxp" → 命中

## ⚙️ pinyin tokenizer 参数

```json
{
  "settings": {
    "analysis": {
      "analyzer": {
        "my_pinyin": {
          "tokenizer": {
            "type": "pinyin",
            "keep_first_letter": true,       // 保留首字母 jxp
            "keep_separate_first_letter": false,
            "keep_full_pinyin": true,        // 保留全拼 jixiejianpan
            "keep_joined_full_pinyin": true, // 保留连接全拼
            "keep_original": true,           // 保留原中文
            "limit_first_letter_length": 16,
            "lowercase": true
          }
        }
      }
    }
  }
}
```

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="pinyin-analyzer" :height="400" />

## 📚 延伸阅读
- [Analyzer 分析器](/03-analysis/analyzer)
- [IK 分词器](/03-analysis/ik-analyzer)
- [自定义分词](/03-analysis/custom-analyzer)
