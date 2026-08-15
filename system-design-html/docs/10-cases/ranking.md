---
title: 排行榜系统设计
---

# 排行榜系统设计

> 几千万人竞争一个榜单。**实时性 + 高并发 + 公平性**。

## 1. 排行榜的分类

```
按实时性：

1. 实时榜：
   - 每次分数变化立即更新
   - 例：游戏天梯榜、直播打赏榜
   - 延迟 < 1s

2. 准实时榜：
   - 每分钟 / 5 分钟更新
   - 例：销售榜、热搜榜
   - 延迟分钟级

3. 日榜 / 周榜 / 月榜：
   - 按周期聚合
   - 例：豆瓣 Top 250、Steam 周榜
   - 延迟小时级
```

## 2. 核心难点

```
1. 数据量大：
   - 全榜 100 万用户
   - 单用户每次分数变化都要更新
   - 更新 QPS 可能 100 万+

2. 实时性要求高：
   - 用户期待"我刚刷了多少，排名就涨了"
   - 延迟 > 5s 体验差

3. 一致性要求：
   - 不能有"我明明第一但显示第二"
   - 并发更新要原子

4. 性能：
   - 100 万用户的榜单查询
   - 必须毫秒级
```

## 3. 整体架构

```
用户分数变化（事件）
       ↓
MQ
       ↓
Rank Worker（消费事件）
       ↓
Redis Sorted Set（实时榜）
       ↓
DB（持久化）
       
用户查榜
   ↓
Redis ZRANGE
   ↓
返回前 N 名
```

## 4. Redis Sorted Set（最常用）

### 4.1 数据结构

```
Redis ZSET：
  - key = 榜单 ID（如 leaderboard:game_001）
  - member = 用户 ID
  - score = 分数

例：
  ZADD leaderboard:game_001 1500 user_1
  ZADD leaderboard:game_001 1800 user_2
  ZADD leaderboard:game_001 2000 user_3

查询前 10 名：
  ZREVRANGE leaderboard:game_001 0 9 WITHSCORES

查询用户排名：
  ZREVRANK leaderboard:game_001 user_1
  → 返回 0-based 排名

用户分数：
  ZSCORE leaderboard:game_001 user_1
```

### 4.2 ZADD 的代价

```
ZADD 是 O(log N)：
  - N = 100 万时，每次 ZADD ~ 20 次比较
  - 100 万 QPS → Redis 单实例压力大

优化：
  - 批量 ZADD（pipeline）
  - 异步更新（MQ 攒批）
  - Redis Cluster 分片
```

### 4.3 内存占用

```
每个 ZSET member：
  - key（用户 ID）：~ 50 字节
  - score（double）：8 字节
  - 跳表指针：~ 30 字节
  - 字典 entry：~ 30 字节
  - 总计：~ 120 字节

100 万用户的 ZSET：
  ~ 120 MB

1000 万用户：
  ~ 1.2 GB（需要 Redis Cluster）

📌 ZSET 内存不小，要预估容量
```

## 5. 高并发更新

### 5.1 异步更新模式

```
用户分数变化 → MQ → Worker 批量更新

  # MQ 攒批
  msgs = consume_batch(100)
  
  # Pipeline 批量更新
  pipe = redis.pipeline()
  for msg in msgs:
      pipe.zincrby(leaderboard_key, msg.score_delta, msg.user_id)
  pipe.execute()

📌 批量更新性能高 10x
```

### 5.2 限流策略

```
同一用户疯狂刷榜：
  - 1 分钟最多更新 1 次
  - 累计分数但排名按截止时间点

实现：
  - Redis SETNX 加锁
  - Lua 检查时间间隔
```

### 5.3 抗作弊

```
脚本刷榜：
  - 同一 IP 多次刷
  - 短时间大量分数变化
  - 检测 + 限流
```

## 6. 多榜与分层

### 6.1 总榜 + 分区榜

```
全国榜（前 1000 名）
  - 1000 万用户都参与
  - 单 ZSET 内存大
  
各区榜（前 100 名）
  - 按地区分
  - 小 ZSET 多

实现：
  - 维护多个 ZSET
  - 总榜 + 各区榜
  - 用户可看自己的最好成绩
```

### 6.2 周榜 + 月榜

```
实现：定时合并

  每天凌晨：
    - 把昨天分数叠加到周榜 ZSET
    - 跨周日把周榜叠加到月榜

  或：
    - 每日 ZSET（leaderboard:day_20260809）
    - 周榜 = SUM(过去 7 天 ZSET)
    - 月榜 = SUM(过去 30 天 ZSET)

📌 月榜涉及 ZUNIONSTORE，30 天合并可能慢
   优化：缓存 + 增量计算
```

### 6.3 周期结算

```
周期结束（如赛季结束）：
  - 快照保存（dump 数据到 DB）
  - 重置 ZSET
  - 发放奖励（按排名）

实现：
  - 后台定时任务
  - ZRANGE 取前 N 名 → DB → 发奖
  - DEL 清空 ZSET
```

## 7. 查询优化

### 7.1 我的排名

```
查询用户当前排名：
  ZREVRANK leaderboard:game_001 user_1

复杂度：O(log N)
100 万用户：~ 20 次比较
Redis 性能：单实例 10 万 QPS

📌 足够快
```

### 7.2 前 N 名

```
ZRANGE 0 99（升序）或 ZREVRANGE 0 99（降序）

复杂度：O(log N + M)，M 是返回数量
100 名：< 1ms
```

### 7.3 我的排名附近

```
"我的前后各 50 名"

实现：
  rank = ZREVRANK(key, user_id)
  ZRANGE key (rank-50) (rank+50) WITHSCORES

适合：
  - 用户感知"我在榜单里的位置"
```

### 7.4 排名总数

```
"榜单共多少人"

  ZCARD leaderboard:game_001

复杂度：O(1)
```

## 8. 一致性问题

### 8.1 缓存与 DB 不一致

```
问题：
  - Redis 更新成功
  - DB 异步更新失败
  → DB 没分数，下次周期结算错误

解决：
  - 异步重试
  - 定期对账
  - 以 Redis 为准（榜单用 Redis）
```

### 8.2 跨榜一致性

```
问题：
  - 用户在 A 榜 100 名
  - 同时 B 榜 50 名
  - 跨榜统计时数据不一致

解决：
  - 异步同步 + 容忍延迟
  - 或：分库分表 + 事务保证
```

## 9. 大规模挑战

### 9.1 Redis Cluster 分片

```
单 Redis 容量有限：
  - 单实例内存有限
  - 单实例 QPS 有限

Redis Cluster：
  - 16384 slot 分布到多节点
  - 按榜单 ID hash 到 slot
  - 跨节点查询需要遍历

📌 单榜单尽量放单节点（避免跨节点事务）
```

### 9.2 冷数据归档

```
历史榜单（如去年赛季）：
  - 不再查询
  - 但要保留数据
  → 归档到 DB / OSS

实现：
  - 定时导出
  - 压缩存储
  - 按需查询历史
```

### 9.3 实时计算的替代

```
当榜单规模过大：

方案 1：分层聚合
  - 区域榜 → 全国榜（合并）
  - 减少单榜数据量

方案 2：近似计算
  - 采样 + 估算
  - 损失精度换性能

方案 3：专用系统
  - Doris / ClickHouse
  - 实时 OLAP 查询
  - 比 Redis 更适合大规模榜单
```

## 10. 实战案例

### 10.1 游戏天梯

```
游戏天梯：
  - 100 万玩家
  - 实时匹配对手（找相近排名）
  - 排名 + 段位（青铜 / 白银 / 黄金）

设计：
  - Redis ZSET 存排名
  - 段位缓存（按区间划分）
  - 匹配时 ZRANGEBYSCORE 找对手
```

### 10.2 直播打赏

```
直播打赏榜：
  - 本场前 10 名
  - 实时更新
  - 礼物效果（霸屏）

设计：
  - Redis ZSET（10 人小榜）
  - MQ 异步处理礼物事件
  - WebSocket 推送实时更新
```

### 10.3 销售榜

```
电商销售榜：
  - 月度 TOP 100
  - 销量 = 订单数 + 金额
  - 准实时（分钟级）

设计：
  - MQ 攒批更新 Redis
  - 定时聚合到 DB
  - 缓存层提供查询
```

## 11. 一句话总结

```
📌 排行榜核心：Redis Sorted Set（ZSET）+ MQ 异步 + 批量更新
📌 ZSET 操作：ZADD（O(log N)）/ ZREVRANK（O(log N)）/ ZRANGE（O(log N + M)）
📌 高并发：异步更新 + Pipeline 批量 + Redis Cluster 分片
📌 多榜单：总榜 + 区域榜 + 周榜 + 月榜（按业务分）
📌 周期结算：定时任务取前 N 名 → DB → 发奖 → 清榜
📌 数据规模：100 万用户 ~120 MB，1000 万 ~1.2 GB
📌 大规模方案：Doris / ClickHouse 实时 OLAP
📌 一致性：Redis 是权威，DB 异步同步 + 定期对账
```

## 12. 参考资料

- Redis Sorted Set 文档
- 游戏天梯设计（League of Legends / 王者荣耀）
- 直播打赏架构（虎牙 / 抖音）
- ClickHouse 排行榜实践
- Redis ZADD pipeline 优化