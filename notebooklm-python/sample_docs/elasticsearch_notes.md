# 弹性搜索与 NotebookLM 集成笔记

## Elasticsearch 7 dense_vector

Elasticsearch 从 7.3 版本开始支持 dense_vector 字段类型。从 7.6 版本开始，
可以在 script_score 查询中使用 cosineSimilarity 函数计算向量相似度。

在 notebooklm-python 项目中，我们使用以下 mapping：

    {
      "properties": {
        "text":      { "type": "text" },
        "embedding": { "type": "dense_vector", "dims": 768 },
        "source":    { "type": "keyword" },
        "chunk_id":  { "type": "keyword" },
        "page":      { "type": "integer" }
      }
    }

## BM25 与向量检索的融合

传统的 RAG 系统要么只用 BM25（关键词匹配），要么只用向量检索（语义匹配）。
这两种方法各有缺点：

- BM25 无法捕捉"近义词"或"语义相似但用词不同"的情况。
- 纯向量检索对专有名词、型号、代码标识符不敏感。

NotebookLM 的做法是同时跑两种检索，然后通过 RRF（Reciprocal Rank Fusion）
融合排序。RRF 的公式很简单：对每个 chunk，把它的 BM25 排名和向量排名
取倒数加权求和。

## 重排（Reranking）

混合检索会召回 20 个左右的候选 chunk，但最终送给 LLM 的 prompt 只能容纳
5-10 个，否则 token 数会爆炸。所以需要重排器（cross-encoder）对候选
chunk 做精确打分，按分数取 Top-N。

我们使用 cross-encoder/ms-marco-MiniLM-L-6-v2 作为重排器。
