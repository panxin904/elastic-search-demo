---
title: 推荐系统
date: 2026-08-15  # date-auto-injected
---
# 推荐系统

## 1. 是什么

推荐系统 = 根据用户行为 / 兴趣，从海量物品中找出用户可能感兴趣的物品。

应用场景：
  - 电商（淘宝 / 京东）
  - 内容（抖音 / YouTube）
  - 社交（微博 / 小红书）
  - 信息流（今日头条）

## 2. 推荐架构

```
召回（粗排）→ 粗排（精排）→ 重排（业务规则）→ 展示

召回（万级）：
  - 协同过滤（ItemCF / UserCF）
  - 内容相似（Item Embedding）
  - 热门 / 兴趣
  - 深度模型（双塔 DSSM）

精排（百级）：
  - 模型打分（XGBoost / 深度学习）
  - 多目标（CTR / CVR / GMV）

重排（10 级）：
  - 业务规则（去重 / 多样性 / 新鲜度）
  - 强插（运营 / 广告）
```

## 3. 召回模型

### 3.1 协同过滤（ItemCF）

```sql
-- 用户行为
CREATE TABLE user_behavior (
  user_id BIGINT,
  item_id BIGINT,
  behavior STRING,  -- click / cart / buy
  ts TIMESTAMP
);

-- 计算物品相似度（Spark）
-- 共现矩阵
SELECT
  item_a,
  item_b,
  COUNT(DISTINCT user_id) AS co_count
FROM (
  SELECT
    a.item_id AS item_a,
    b.item_id AS item_b,
    a.user_id
  FROM user_behavior a
  JOIN user_behavior b
    ON a.user_id = b.user_id
    AND a.item_id < b.item_id
  WHERE a.behavior IN ('click', 'cart', 'buy')
    AND b.behavior IN ('click', 'cart', 'buy')
) t
GROUP BY item_a, item_b;

-- 推荐
SELECT
  user_id,
  item_b,
  SUM(co_count) AS score
FROM user_behavior a
JOIN item_similarity b
  ON a.item_id = b.item_a
WHERE a.user_id = 123
GROUP BY user_id, item_b
ORDER BY score DESC
LIMIT 100;
```

### 3.2 内容相似（Embedding）

```python
# Item2Vec（基于 Word2Vec）
from gensim.models import Word2Vec

sentences = [
  [str(item) for item in items]
  for user_id, items in user_behavior.groupby('user_id')
]

model = Word2Vec(sentences, vector_size=128, window=5, min_count=1)
item_vec = model.wv['item_123']  # 物品 123 的 embedding
```

### 3.3 双塔模型（DSSM）

```python
# 用户塔 + 物品塔
import tensorflow as tf

user_tower = tf.keras.Sequential([
  tf.keras.layers.Dense(128, activation='relu'),
  tf.keras.layers.Dense(64)
])

item_tower = tf.keras.Sequential([
  tf.keras.layers.Dense(128, activation='relu'),
  tf.keras.layers.Dense(64)
])

user_vec = user_tower(user_features)  # 用户向量
item_vec = item_tower(item_features)  # 物品向量

# 内积 / cosine 相似度
score = tf.reduce_sum(user_vec * item_vec, axis=1)
```

## 4. 精排模型

### 4.1 LR / FM

```python
# LR
from sklearn.linear_model import LogisticRegression

X = ...  # 特征：用户 / 物品 / 上下文
y = ...  # 是否点击

model = LogisticRegression()
model.fit(X, y)
```

### 4.2 深度模型（DeepFM / DIN）

```python
# DIN（Deep Interest Network）
class DIN(tf.keras.Model):
  def __init__(self):
    super().__init__()
    self.user_emb = tf.keras.layers.Embedding(...)
    self.item_emb = tf.keras.layers.Embedding(...)
    self.attention = tf.keras.layers.Attention()
    self.mlp = tf.keras.Sequential([...])

  def call(self, inputs):
    user_hist, target_item = inputs
    # Attention
    att = self.attention([user_hist, target_item])
    # 拼接 + MLP
    x = tf.concat([att, target_item], axis=1)
    return self.mlp(x)
```

## 5. 实时推荐

```java
// Flink 实时特征
DataStream<Feature> features = env
  .addSource(new KafkaSource<>("user-actions"))
  .keyBy(UserAction::getUserId)
  .window(SlidingEventTimeWindows.of(Time.minutes(10), Time.minutes(1)))
  .aggregate(new RecentItemsAgg());

// 实时召回
features.addSink(new FaissSink("user_recent_items"));
```

## 6. 推荐评估

| 指标 | 含义 | 公式 |
|------|------|------|
| **CTR** | 点击率 | clicks / impressions |
| **CVR** | 转化率 | conversions / clicks |
| **GMV** | 交易额 | sum(amount) |
| **多样性** | 推荐物品多样性 | 1 - Gini 系数 |
| **新颖度** | 推荐物品新颖度 | 推荐冷门物品比例 |
| **覆盖率** | 推荐覆盖物品数 | 物品数 / 总物品数 |

## 7. 实战架构

```
离线：
  Spark MLlib → 物品相似度（ItemCF）
  TensorFlow → 双塔 / DIN 模型
  
在线：
  Kafka → Flink → Redis（实时特征）
  Faiss → 向量召回
  TF Serving → 精排
```

## 8. 实战案例

### 案例 1：电商推荐

```
架构：
  召回：DSSM 双塔（用户塔 + 物品塔）
  精排：DIN（用户兴趣 Attention）
  重排：业务规则（去重 / 多样性）

评估：
  CTR +2.5%
  CVR +1.8%
  GMV +5%
```

### 案例 2：内容推荐

```
架构：
  召回：双塔 + 协同过滤
  精排：Multi-Task（CTR / 完播率 / 点赞）
  重排：多样性 + 新鲜度

评估：
  人均时长 +15%
  留存 +3%
```

## 9. 实战 checklist

- [ ] 召回（ItemCF / 双塔 / 内容）
- [ ] 精排（DeepFM / DIN）
- [ ] 重排（业务规则）
- [ ] 实时特征（Flink）
- [ ] 评估指标（CTR / CVR / 多样性）
- [ ] A / B 测试
- [ ] 监控（效果 / 系统）

## 10. 实战建议

1. **召回先行**：覆盖 + 多样性
2. **精排优化**：模型 + 特征
3. **业务规则**：多样性 + 新鲜度 + 去重
4. **A / B 测试**：流量分配 + 效果评估

## 🔗 下一步
- [用户画像](/13-cases/user-profile)
- [风控案例](/13-cases/risk-control)
- [OLAP 选型](/12-olap-engine/selection)
