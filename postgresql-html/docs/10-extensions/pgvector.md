---
title: pgvector 向量数据库
---

# pgvector 向量数据库

> PostgreSQL 同时是向量数据库。**AI 时代的关键扩展 + HNSW 索引 = 毫秒级相似度搜索**。

## 1. 为什么需要 pgvector？

```
AI 时代的问题：
  - 大模型产生 embeddings（向量）
  - 文本/图片/视频 → 768/1024/4096 维向量
  - 需要找"最相似"的 N 个

传统方案：
  - Pinecone / Weaviate / Milvus（专用向量库）
  - 数据需要同步到外部
  - 额外运维成本

pgvector 方案：
  - PG 直接存向量
  - HNSW / IVF 索引
  - 不需要外部依赖
  - ACID 事务 + 关系查询

📌 PostgreSQL = 关系型 + 文档型 + 空间型 + 向量型
   一个数据库搞定所有
```

## 2. 安装

```bash
# Ubuntu
sudo apt install postgresql-17-pgvector

# macOS (Homebrew)
brew install pgvector

# 编译安装
cd /tmp
git clone --branch v0.7.4 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install

# 在数据库中启用
psql mydb -c "CREATE EXTENSION vector;"
```

```sql
-- 验证安装
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';

-- vector 类型可用
SELECT '[1,2,3]'::vector;
```

## 3. 基本操作

### 3.1 表设计

```sql
-- 创建表（含向量列）
CREATE TABLE documents (
  id        BIGSERIAL PRIMARY KEY,
  content   TEXT NOT NULL,
  metadata  JSONB,
  embedding vector(1536)  -- 1536 维（如 OpenAI text-embedding-ada-002）
);

-- 插入数据
INSERT INTO documents (content, metadata, embedding)
VALUES
  ('PostgreSQL 是一个强大的数据库', '{"source": "wiki"}',
   '[0.1, 0.2, 0.3, ...]'::vector),  -- 实际 1536 维
  ('MySQL 是另一个数据库', '{"source": "blog"}',
   '[0.2, 0.3, 0.4, ...]'::vector);
```

### 3.2 相似度查询

```sql
-- L2 距离（欧氏距离）
SELECT id, content, embedding <-> '[0.1, 0.2, ...]'::vector AS distance
FROM documents
ORDER BY embedding <-> '[0.1, 0.2, ...]'::vector
LIMIT 5;

-- 余弦距离
SELECT id, content, embedding <=> '[0.1, 0.2, ...]'::vector AS distance
FROM documents
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 5;

-- 内积（点积）
SELECT id, content, embedding <#> '[0.1, 0.2, ...]'::vector AS score
FROM documents
ORDER BY embedding <#> '[0.1, 0.2, ...]'::vector
LIMIT 5;
```

### 3.3 距离操作符

```sql
<->   L2 距离（欧氏）
<=>   余弦距离（1 - 余弦相似度）
<#>   内积（负值越大越相似）

相似度选择：
  - 文本嵌入（OpenAI / BERT）：余弦相似度
  - 图像嵌入：L2 距离
  - 推荐系统：内积
```

### 3.4 过滤 + 相似度

```sql
-- 在指定类别中找相似
SELECT * FROM documents
WHERE metadata->>'category' = 'tech'
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 5;

-- 时间范围 + 相似度
SELECT * FROM documents
WHERE created_at > NOW() - INTERVAL '30 days'
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 5;
```

## 4. 索引（关键性能）

### 4.1 HNSW 索引

```sql
-- HNSW（Hierarchical Navigable Small World）
-- 算法：图索引，查询快，构建慢
CREATE INDEX idx_documents_embedding ON documents
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 参数：
-- m：每个节点的连接数（默认 16，越大越准但越慢）
-- ef_construction：构建时的搜索宽度（默认 64）
-- ef：查询时的搜索宽度（默认 40）
```

```sql
-- 距离函数索引选项
USING hnsw (embedding vector_l2_ops)       -- L2
USING hnsw (embedding vector_cosine_ops)  -- 余弦
USING hnsw (embedding vector_ip_ops)      -- 内积
```

### 4.2 IVFFlat 索引

```sql
-- IVFFlat（Inverted File with Flat compression）
-- 算法：聚类分桶，查询较快，构建较快
CREATE INDEX idx_documents_embedding ON documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- lists = 行数 / 1000（经验值）
-- 100万行 → lists = 1000
```

### 4.3 HNSW vs IVFFlat

| 维度 | HNSW | IVFFlat |
|---|---|---|
| 查询速度 | 快（10-100x） | 中 |
| 构建速度 | 慢 | 快 |
| 内存占用 | 大（10x） | 中 |
| 召回率 | 高（> 95%） | 中（80-90%） |
| 增量更新 | 支持 | 支持 |
| 适合 | 高 QPS、高精度 | 大数据集、构建时间敏感 |

### 4.4 索引调优

```sql
-- 查询时调整 ef（搜索宽度）
SET hnsw.ef_search = 100;  -- 默认 40，越大越准越慢
SELECT * FROM documents ORDER BY embedding <=> '...' LIMIT 5;

-- 构建时调整 ef_construction
CREATE INDEX idx ON documents USING hnsw (embedding vector_cosine_ops)
WITH (m = 32, ef_construction = 128);

-- 重建索引（不锁表，新索引构建完后切换）
REINDEX INDEX CONCURRENTLY idx_documents_embedding;
```

## 5. 实战案例

### 5.1 RAG（检索增强生成）

```python
# 文档向量化 + 检索
import openai
import psycopg

# 1. 文档入库
conn = psycopg.connect("dbname=mydb")
cur = conn.cursor()

def embed_text(text):
    resp = openai.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return resp.data[0].embedding

def add_document(content, metadata):
    embedding = embed_text(content)
    cur.execute(
        "INSERT INTO documents (content, metadata, embedding) VALUES (%s, %s, %s)",
        (content, metadata, embedding)
    )
    conn.commit()

# 2. 检索相似文档
def search(query, top_k=5):
    query_embedding = embed_text(query)
    cur.execute("""
        SELECT id, content, metadata,
               embedding <=> %s::vector AS distance
        FROM documents
        ORDER BY distance
        LIMIT %s
    """, (query_embedding, top_k))
    return cur.fetchall()

# 3. 拼接到 LLM
results = search("PostgreSQL 优势是什么？")
context = "\n".join([r[1] for r in results])
prompt = f"基于以下资料回答：\n{context}\n\n问题：PostgreSQL 优势是什么？"
```

### 5.2 推荐系统

```sql
-- 用户-物品向量表
CREATE TABLE user_item_vectors (
  user_id   BIGINT,
  item_id   BIGINT,
  score     FLOAT,
  embedding vector(128),
  PRIMARY KEY (user_id, item_id)
);

-- 推荐相似物品
SELECT uiv.item_id, i.name,
       uiv.embedding <=> (SELECT embedding FROM user_item_vectors
                          WHERE user_id = 1001 AND item_id = 5001) AS similarity
FROM user_item_vectors uiv
JOIN items i ON i.id = uiv.item_id
WHERE uiv.user_id = 1001
ORDER BY similarity
LIMIT 20;
```

### 5.3 图像检索

```sql
-- CLIP 图像向量（512 维）
CREATE TABLE image_vectors (
  id        BIGSERIAL PRIMARY KEY,
  url       TEXT,
  embedding vector(512)
);

-- 上传图像 → CLIP → 存向量
-- 查询：用图像向量找相似图像
SELECT id, url, embedding <-> $1::vector AS distance
FROM image_vectors
ORDER BY distance
LIMIT 20;
```

## 6. 性能基准

```
数据集：100 万 vectors，1536 维

无索引：
  - 顺序扫描：5000ms

HNSW 索引：
  - 查询（k=10）：5-10ms
  - 召回率：> 99%
  - 内存占用：约 2 GB（m=16）

IVFFlat 索引：
  - 查询（k=10）：20-50ms
  - 召回率：90-95%
  - 内存占用：约 1 GB

📌 HNSW 是当前主流选择
   牺牲内存换性能
```

## 7. 与专用向量库对比

| 维度 | pgvector | Pinecone | Milvus | Weaviate |
|---|---|---|---|---|
| 部署 | 现有 PG | 托管 | 自建/托管 | 自建/托管 |
| 扩展性 | 单 PG 实例 | 无限 | 无限 | 无限 |
| 事务 | ACID | 无 | 有限 | 无 |
| 关联查询 | 原生 JOIN | 不支持 | 有限 | 有限 |
| 性能 | 中（毫秒级） | 高（亚毫秒） | 高（亚毫秒） | 高（亚毫秒） |
| 成本 | PG 集群成本 | 按 QPS | 按节点 | 按节点 |

📌 pgvector 适合：
   - 中小规模（百万级）
   - 需要关联查询（向量 + 关系）
   - 已有 PG 集群

专用向量库适合：
   - 超大规模（千万-亿级）
   - 极致延迟（亚毫秒）
   - 纯向量场景

## 8. 高级特性

### 8.1 量化

```sql
-- pgvector 0.7+ 支持量化（压缩）
-- 减少内存占用 4-32x

-- half-precision（float16）：内存减半
-- bit 向量（1 bit）：内存减少 32x
-- 待官方正式发布

-- 当前可用：HNSW 索引可省内存
SET hnsw.iterative_scan = on;  -- 迭代扫描省内存
```

### 8.2 混合查询

```sql
-- 全文检索 + 向量检索
SELECT id, content,
       ts_rank_cd(to_tsvector('english', content), query) AS text_rank,
       embedding <=> $1::vector AS vec_distance
FROM documents, to_tsquery('english', 'database') query
WHERE to_tsvector('english', content) @@ query
ORDER BY vec_distance
LIMIT 10;

-- BM25 + 向量（pgvector + tsvector + 权重融合）
```

### 8.3 增量更新

```sql
-- 删除 + 插入（索引自动更新）
DELETE FROM documents WHERE id = 1;
INSERT INTO documents (...) VALUES (...);

-- 性能：HNSW 支持增量，IVFFlat 也支持

-- 定期重建（大批量变化后）
REINDEX INDEX CONCURRENTLY idx_documents_embedding;
```

## 9. 常见陷阱

### 9.1 向量归一化

```sql
-- 余弦相似度：向量应该归一化
-- 未归一化会让大向量"占便宜"

-- 归一化（L2 norm）
UPDATE documents
SET embedding = embedding / |/ (embedding <-> embedding::vector) ;
-- pgvector 0.7+：
UPDATE documents
SET embedding = l2_normalize(embedding);
```

### 9.2 维度匹配

```sql
-- ⚠️ 维度必须严格匹配
CREATE TABLE t (embedding vector(1536));
INSERT INTO t VALUES ('[1,2,3]'::vector);  -- 错！3 ≠ 1536
-- ERROR:  expected 1536 dimensions, not 3

-- 不同模型维度不同：
-- OpenAI text-embedding-3-small: 1536
-- OpenAI text-embedding-3-large: 3072
-- BERT base: 768
-- CLIP: 512

-- 必须用同一模型
```

### 9.3 内存爆炸

```
HNSW 索引内存估算：
  100万向量 × 1536 维 × 4 bytes = 6 GB（原始）
  HNSW overhead ≈ 3-5x = 18-30 GB

解决：
  1. 减 m（16 → 8）
  2. 减 ef_construction
  3. 量化（未来支持）
  4. 分区（多个 PG 实例）
```

## 10. 一句话总结

```
📌 pgvector = PG 同时是向量数据库
📌 安装：apt / brew / CREATE EXTENSION vector
📌 距离：<->（L2）/<=>（余弦）/<#>（点积）
📌 索引：HNSW（快但占内存）+ IVFFlat（快且省内存）
📌 性能：100万向量 HNSW 5-10ms
📌 实战：RAG / 推荐 / 图像检索 / 文本去重
📌 vs 专用向量库：适合中小规模 + 关系查询 + 已有 PG
📌 陷阱：维度匹配、归一化、内存爆炸
📌 AI 时代关键：让 PG 一库搞定"业务 + 向量"
```

## 11. 参考资料

- pgvector GitHub（github.com/pgvector/pgvector）
- Supabase pgvector 文档
- "Building RAG with PostgreSQL"（Anthropic）
- HNSW 论文（Malkov & Yashunin, 2018）
- "Vector Search with PostgreSQL"（AWS）
- AI 时代 pgvector 案例（Shopify / Notion）


<!-- auto-enrich:do-not-edit -->

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
