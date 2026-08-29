---
title: 用户画像
date: 2026-08-15  # date-auto-injected
---
# 用户画像系统

## 1. 是什么

用户画像 = 通过多源数据（行为 / 属性 / 偏好），构建用户的多维特征体系（标签）。

核心价值：
  - 精准营销
  - 个性化推荐
  - 风控反欺诈
  - 用户运营

## 2. 画像标签体系

### 2.1 标签分类

| 类别 | 示例 | 加工方式 |
|------|------|----------|
| 人口属性 | 年龄 / 性别 / 地域 | 直接采集 |
| 行为标签 | 浏览 / 收藏 / 加购 | 实时计算 |
| 偏好标签 | 品类偏好 / 品牌偏好 | 离线聚合 |
| 消费力 | 客单价 / 消费频次 | 离线聚合 |
| 风险标签 | 失信 / 欺诈 / 高危 | 实时计算 |
| 生命周期 | 新客 / 活跃 / 沉睡 / 流失 | 离线计算 |

### 2.2 标签建模

```sql
-- ODS（原始）
CREATE TABLE ods_user_action (
  user_id BIGINT,
  action_type STRING,
  item_id BIGINT,
  ts TIMESTAMP
);

-- DWD（明细）
CREATE TABLE dwd_user_behavior (
  user_id BIGINT,
  item_id BIGINT,
  item_category STRING,
  behavior STRING,
  ts TIMESTAMP
);

-- DWS（汇总，按用户）
CREATE TABLE dws_user_profile (
  user_id BIGINT,
  dt STRING,
  browse_cnt BIGINT,
  favorite_cnt BIGINT,
  cart_cnt BIGINT,
  order_cnt BIGINT,
  gmv DECIMAL(10,2)
);

-- ADS（标签）
CREATE TABLE ads_user_tag (
  user_id BIGINT,
  dt STRING,
  -- 人口
  age_range STRING,
  gender STRING,
  city STRING,
  -- 消费力
  price_level STRING,    -- 高 / 中 / 低
  purchase_level STRING, -- 高频 / 中频 / 低频
  -- 偏好
  favorite_category STRING,
  favorite_brand STRING,
  -- 生命周期
  life_cycle STRING      -- 新客 / 活跃 / 沉睡 / 流失
);
```

## 3. 标签计算

### 3.1 离线标签（T+1）

```sql
-- 1. 用户活跃度
INSERT INTO ads_user_tag
SELECT
  user_id,
  dt,
  -- 近 30 天浏览 + 收藏 + 加购 + 购买
  SUM(browse_cnt) AS browse,
  SUM(favorite_cnt) AS favorite,
  SUM(cart_cnt) AS cart,
  SUM(order_cnt) AS order_cnt,
  SUM(gmv) AS gmv,
  -- 生命周期
  CASE
    WHEN SUM(order_cnt) = 0 THEN '潜在'
    WHEN DATEDIFF(dt, last_order_dt) <= 7 THEN '活跃'
    WHEN DATEDIFF(dt, last_order_dt) <= 30 THEN '次活'
    WHEN DATEDIFF(dt, last_order_dt) <= 90 THEN '沉睡'
    ELSE '流失'
  END AS life_cycle
FROM dws_user_profile
WHERE dt >= '2024-01-15'
GROUP BY user_id, dt;
```

### 3.2 实时标签（Flink）

```java
// Flink 实时计算用户最近 1 小时浏览
public class UserBehaviorJob {
  public static void main(String[] args) throws Exception {
    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

    DataStream<UserAction> actions = env
      .addSource(new KafkaSource<>("user-actions"))
      .map(UserAction::parse);

    // 按 user_id 分组，每 1 小时计算浏览次数
    actions
      .keyBy(UserAction::getUserId)
      .window(TumblingEventTimeWindows.of(Time.hours(1)))
      .aggregate(new BrowseCntAgg())
      .addSink(new ClickHouseSink("user_realtime"));

    env.execute("User Profile Job");
  }
}
```

## 4. 标签查询（实时）

```sql
-- Doris / StarRocks
SELECT user_id, life_cycle, price_level, favorite_category
FROM ads_user_tag
WHERE user_id IN (?, ?, ?);

-- 圈选：近 30 天活跃 + 客单 > 500 + 偏好 = 数码
SELECT user_id
FROM ads_user_tag
WHERE dt = CURRENT_DATE - 1
  AND life_cycle = '活跃'
  AND price_level = '高'
  AND favorite_category = '数码';
```

## 5. 实时圈选（人群包）

```sql
-- 创建人群包：近 7 天活跃 + 高客单 + 偏好 = 美妆
CREATE TABLE crowd_beauty_active (
  user_id BIGINT
) AS
SELECT user_id
FROM ads_user_tag
WHERE dt = CURRENT_DATE - 1
  AND life_cycle = '活跃'
  AND price_level IN ('高', '中')
  AND favorite_category = '美妆';

-- 推送（营销）
INSERT INTO push_queue
SELECT user_id, '美妆活动', NOW()
FROM crowd_beauty_active;
```

## 6. 用户画像架构

```
Kafka（行为） → Flink（实时计算） → Doris（实时画像）
                                    ↓
                              Redis（缓存 / 圈选）
                                  
MySQL（属性） → Spark（离线 ETL） → Hive（离线画像 ODS / DWD / DWS / ADS）
                                       ↓
                                  Doris / StarRocks（融合）
```

## 7. 画像应用

### 7.1 精准营销

```
人群圈选（人群包）
  - 用户属性 / 行为 / 偏好
  - 实时（实时圈选）
  - 离线（T+1 圈选）

推送渠道：
  - 短信 / Push / 微信
  - EDM / 站内信
```

### 7.2 个性化推荐

```
召回 → 用户画像（偏好）
粗排 → 历史行为 + 实时行为
精排 → 模型（深度学习）
```

### 7.3 风控反欺诈

```
实时特征：
  - 设备指纹
  - IP / GPS
  - 行为模式

模型：
  - XGBoost / 深度学习
  - 实时评分
```

## 8. 实战案例

### 案例 1：电商用户画像

```
需求：精准营销 + 个性化推荐 + 风控

架构：
  MySQL（用户） → Spark ETL → Hive（离线）
  Kafka（行为） → Flink → Doris（实时）
  
标签：
  - 人口 / 消费力 / 偏好 / 生命周期
  
查询：
  - Doris（实时）：ms
  - Hive（离线）：min
```

### 案例 2：内容平台用户画像

```
需求：用户兴趣 + 内容推荐

架构：
  日志 → Kafka → Flink → ClickHouse
  　　　　　　　↓
  　　　　　 Spark → Hive（离线）
  
标签：
  - 兴趣（品类 / 主题 / 实体）
  - 行为（阅读 / 点赞 / 评论 / 关注）
```

## 9. 实战 checklist

- [ ] 标签体系设计（人口 / 行为 / 偏好 / 风险 / 生命周期）
- [ ] 数据源接入（MySQL / Kafka / 日志）
- [ ] 离线计算（Spark / Hive）
- [ ] 实时计算（Flink / Doris）
- [ ] 标签查询（Doris / Hive）
- [ ] 标签应用（推荐 / 营销 / 风控）
- [ ] 监控（计算延迟 / 标签覆盖率）

## 10. 实战建议

1. **标签体系先行**：业务驱动，避免过多标签
2. **离线 + 实时结合**：T+1 全量 + 分钟级增量
3. **圈选优化**：Bitmap（RoaringBitmap）
4. **监控**：标签覆盖率 / 计算延迟 / 数据质量

## 🔗 下一步
- [推荐系统](/13-cases/recommendation)
- [风控案例](/13-cases/risk-control)
- [实时数仓](/10-data-lake/lakehouse)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [kafka](https://java-px.bot.cd/kafka/):Kafka 流处理
- [es](https://java-px.bot.cd/es/):Elasticsearch
- [clickhouse](https://java-px.bot.cd/clickhouse/):ClickHouse OLAP
