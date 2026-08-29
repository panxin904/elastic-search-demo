---
title: 排行榜
date: 2026-08-15  # date-auto-injected
---

# 🏆 排行榜

> **排行榜**是 Redis ZSet 的经典应用场景。ZSet 的 score 排序特性天然适合做各种排行榜。

## 🎯 排行榜场景

```
✅ 游戏战力榜（游戏角色战力排名）
✅ 销量榜（商品销售数量排名）
✅ 积分榜（用户积分排名）
✅ 礼物榜（直播间礼物贡献榜）
✅ 投票榜（候选人得票数排名）
✅ 文章热度榜（阅读数 + 点赞数 + 评论数综合）
```

## 🛠️ ZSet 实现

```bash
# 添加玩家分数
ZADD leaderboard:game1 1500 "player:1001"
ZADD leaderboard:game1 2300 "player:1002"
ZADD leaderboard:game1 1800 "player:1003"

# 获取前 10 名（按分数降序）
ZREVRANGE leaderboard:game1 0 9 WITHSCORES
# 1) "player:1002"
# 2) "2300"
# 3) "player:1003"
# 4) "1800"
# 5) "player:1001"
# 6) "1500"

# 获取玩家排名
ZREVRANK leaderboard:game1 "player:1002"  # → 0（第 1 名）

# 获取玩家分数
ZSCORE leaderboard:game1 "player:1002"    # → 2300
```

## 📊 核心命令

| 命令 | 用途 | 时间复杂度 |
|------|------|----------|
| `ZADD` | 添加/更新分数 | O(log N) |
| `ZINCRBY` | 增加分数（自增） | O(log N) |
| `ZREVRANGE` | 按分数倒序获取 | O(log N + M) |
| `ZRANGEBYSCORE` | 按分数区间获取 | O(log N + M) |
| `ZREVRANK` | 获取排名（降序） | O(log N) |
| `ZSCORE` | 获取分数 | O(1) |
| `ZCARD` | 总数 | O(1) |

## 🛠️ 实战：游戏战力榜

```java
@Service
public class GameLeaderboardService {
    
    @Autowired
    private StringRedisTemplate redisTemplate;
    
    private static final String BOARD = "leaderboard:game1";
    
    // 1. 更新玩家战力
    public void updatePower(Long playerId, long power) {
        redisTemplate.opsForZSet().add(BOARD, "player:" + playerId, power);
    }
    
    // 2. 增加战力（如打怪获得经验）
    public void increasePower(Long playerId, long delta) {
        redisTemplate.opsForZSet().incrementScore(BOARD, "player:" + playerId, delta);
    }
    
    // 3. 获取 Top 10
    public List<PlayerRank> getTop10() {
        Set<ZSetOperations.TypedTuple<String>> tuples = redisTemplate.opsForZSet()
            .reverseRangeWithScores(BOARD, 0, 9);
        
        List<PlayerRank> ranks = new ArrayList<>();
        int rank = 1;
        for (ZSetOperations.TypedTuple<String> tuple : tuples) {
            PlayerRank r = new PlayerRank();
            r.setRank(rank++);
            r.setPlayerId(Long.parseLong(tuple.getValue().replace("player:", "")));
            r.setPower(tuple.getScore().longValue());
            ranks.add(r);
        }
        return ranks;
    }
    
    // 4. 获取玩家排名（含前后 5 名）
    public PlayerRankInfo getPlayerRank(Long playerId) {
        String member = "player:" + playerId;
        
        // 玩家自身排名
        Long rank = redisTemplate.opsForZSet().reverseRank(BOARD, member);
        Double score = redisTemplate.opsForZSet().score(BOARD, member);
        
        // 前后 5 名
        long start = Math.max(0, rank - 5);
        long end = Math.min(redisTemplate.opsForZSet().zCard(BOARD), rank + 5);
        
        Set<TypedTuple<String>> around = redisTemplate.opsForZSet()
            .reverseRangeWithScores(BOARD, start, end);
        
        return new PlayerRankInfo(rank + 1, score.longValue(), around);
    }
}
```

## 🛠️ 实战：多维度排行榜

> 单一 ZSet 只支持一个维度的排序。**多维度排行榜**（战力 + 等级 + 财富）需要组合方案。

### 方案 1：多个 ZSet

```java
// 战力榜
ZADD leaderboard:power 2300 "player:1001"

// 等级榜
ZADD leaderboard:level 50 "player:1001"

// 财富榜
ZADD leaderboard:wealth 100000 "player:1001"
```

### 方案 2：组合分数

```
用 score 编码多个维度（位运算）

score = power_score * 10^8 + level_score * 10^4 + wealth_score

ZADD leaderboard:composite 230000500100000 "player:1001"
ZREVRANGE leaderboard:composite 0 9   # 复合排名
```

```java
public void updateComposite(Long playerId, long power, int level, long wealth) {
    long compositeScore = power * 1_000_000_0000L + level * 10000L + wealth;
    redisTemplate.opsForZSet().add("leaderboard:composite", "player:" + playerId, compositeScore);
}
```

### 方案 3：定时任务计算综合榜

```java
@Scheduled(fixedRate = 300_000)  // 5 分钟一次
public void calculateCompositeLeaderboard() {
    // 从 DB 读取所有玩家最新数据
    List<Player> players = playerMapper.findAll();
    
    // 综合分数
    for (Player p : players) {
        long compositeScore = computeComposite(p);
        redisTemplate.opsForZSet().add("leaderboard:composite",
            "player:" + p.getId(), compositeScore);
    }
}
```

## 📊 周榜 / 月榜

```
需求：每周一清零，显示本周排行

方案 1：每周一个 key
  ZADD leaderboard:weekly:2024-W28 2300 "player:1001"  # ISO 周
  ZADD leaderboard:weekly:2024-W29 2300 "player:1001"
  老周数据自动失效

方案 2：永久 key + 时间范围查询
  ZADD leaderboard:total 1698000000000 "player:1001"  # score = 时间戳
  ZRANGEBYSCORE leaderboard:total <start> <end>
```

## 🛠️ 实战：直播间礼物榜

```java
@Service
public class LiveGiftLeaderboard {
    
    private static final String DAILY = "gift:daily:";
    private static final String TOTAL = "gift:total";
    
    public void addGift(Long userId, Long roomId, long amount) {
        // 当日榜
        String dailyKey = DAILY + LocalDate.now();
        redisTemplate.opsForZSet().incrementScore(dailyKey, "user:" + userId, amount);
        redisTemplate.expire(dailyKey, 25, TimeUnit.HOURS);
        
        // 总榜
        redisTemplate.opsForZSet().incrementScore(TOTAL, "user:" + userId, amount);
    }
    
    public List<UserRank> getDailyTop(Long roomId, int topN) {
        String key = DAILY + LocalDate.now();
        Set<TypedTuple<String>> tuples = redisTemplate.opsForZSet()
            .reverseRangeWithScores(key, 0, topN - 1);
        
        return tuples.stream().map(t -> {
            UserRank r = new UserRank();
            r.setUserId(Long.parseLong(t.getValue().replace("user:", "")));
            r.setAmount(t.getScore().longValue());
            return r;
        }).collect(Collectors.toList());
    }
}
```

## 🛠️ 实战：文章热度榜

```java
// 文章热度 = 阅读数 * 0.5 + 点赞数 * 2 + 评论数 * 3
public void updateHotScore(Long articleId, long views, long likes, long comments) {
    double hotScore = views * 0.5 + likes * 2 + comments * 3;
    redisTemplate.opsForZSet().add("hot:articles", "article:" + articleId, hotScore);
}

// 实时调整（异步）
@Async
public void onView(Long articleId) {
    redisTemplate.opsForZSet().incrementScore("hot:articles", "article:" + articleId, 0.5);
}

@Async
public void onLike(Long articleId) {
    redisTemplate.opsForZSet().incrementScore("hot:articles", "article:" + articleId, 2);
}
```

## 📊 排行榜方案对比

| 方案 | 数据规模 | 性能 | 实现复杂度 |
|------|---------|------|----------|
| **Redis ZSet** | 10w-1000w | 极高 | 简单 |
| **MySQL + Index** | 1000w+ | 中 | 中 |
| **Elasticsearch** | 海量 | 高 | 复杂 |
| **ClickHouse** | 海量 | 极高 | 复杂 |

**推荐**：10 万 ~ 1000 万级别用 Redis ZSet 是最佳选择。

## ⚠️ 常见问题

### 问题 1：分页性能

```
场景：获取第 1000 页排行榜
问题：ZREVRANGE start end 在大 offset 时性能差
解决：
  1. 缓存前 N 名到内存
  2. 用 ZRANGEBYSCORE + 时间戳
  3. 限制最大页数（如最多前 100 页）
```

### 问题 2：分数相同怎么办？

```
场景：两个玩家分数相同
问题：ZSet 按字典序排序 member
解决：
  1. 时间戳作为 second sort key
  2. 业务规则（先达到分数的优先）
```

### 问题 3：超大排行榜

```
场景：1 亿玩家排行榜
问题：ZSet 占内存大
解决：
  1. 只保留 Top 10000（用 ZREMRANGEBYRANK 裁剪）
  2. 分区榜（按段位分）
  3. 多级缓存
```

## 🎯 总结

**排行榜核心要点**：
- ✅ ZSet score 存分数，member 存 ID
- ✅ ZREVRANGE 取前 N 名
- ✅ ZREVRANK 查玩家排名
- ✅ 多维度：多个 ZSet 或组合分数
- ✅ 周榜/月榜：按周/月分 key
- ⚠️ 分页性能：避免大 offset
- ⚠️ 数据量过大：只保留 Top N

**下一步：** [🔢 计数器](/06-practice/counter) — INCR 实战
