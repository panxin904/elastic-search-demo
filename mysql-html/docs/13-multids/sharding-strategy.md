---
title: 分片策略与扩容
date: 2026-08-15  # date-auto-injected
---

# 🔀 分片策略与扩容

> 分片键的选择和扩容方案，是分库分表**最核心的决策**。选错了，扩容就要付出巨大代价。

## 🎯 分片键选择

### 三大黄金法则

```
1. 高频查询字段（80% 查询都带这个字段）
2. 数据分布均匀（避免数据倾斜）
3. 业务不可变（分片键一旦确定，不要轻易改）
```

### 候选评估表

| 字段 | 查询频率 | 数据分布 | 业务稳定 | 总分 | 是否适合 |
|---|---|---|---|---|---|
| user_id | ⭐⭐⭐⭐⭐ | 均匀 ✅ | 永不变 ✅ | 13 | ✅ **推荐** |
| id (主键) | ⭐⭐⭐⭐⭐ | 均匀 ✅ | 永不变 ✅ | 13 | ⚠️ 看场景 |
| created_at | ⭐⭐ | 不均匀 ❌ | 不可变 ✅ | 4 | ❌ |
| status | ⭐⭐ | 不均匀 ❌ | 不可变 ✅ | 4 | ❌ |
| city | ⭐⭐⭐ | 不均匀 ❌ | 可变 ❌ | 4 | ❌ |
| category | ⭐⭐⭐ | 不均匀 ❌ | 可变 ❌ | 4 | ❌ |

### 案例 1：订单表

```sql
-- 选择 user_id 作为分片键
-- 原因：
-- 1. 80% 的查询都带 user_id（"我的订单"）
-- 2. 写也是按 user_id 分布（用户下单）
-- 3. 不会出现热点（用户 ID 是均匀的）
```

### 案例 2：消息表

```sql
-- 难题：分片键只能是 1 个
-- 场景：消息表同时有 from_user_id 和 to_user_id
-- 方案 1：按 to_user_id 分片（接收者为主）
-- 方案 2：双写（to_user_id + from_user_id 各一份）
-- 方案 3：宽表（合并 to / from）
```

### 案例 3：日志表

```sql
-- 选择 created_at（按月分片）
-- 优点：冷热数据分离（老日志可归档）
-- 缺点：当前月分片会热（用 range 优化）
```

## 📊 常见分片算法

### 1. 取模分片（最常用）

```yaml
# 简单取模
algorithm-expression: ds$->{user_id % 4}
```

**特点：**
- ✅ 数据均匀
- ✅ 简单
- ❌ 扩容需要 rehash（4 → 8 分片，迁移 75% 数据）

### 2. 范围分片

```yaml
# 按时间范围
algorithm-expression: ds$->{created_at.month}
```

**特点：**
- ✅ 范围查询友好
- ✅ 容易扩容（加新分片）
- ❌ 新分片会热（最新数据集中）

### 3. 一致性 Hash

```yaml
# 使用 Sharding 内置的 MurmurHash
type: COMPLEX
sharding-count: 16
```

**特点：**
- ✅ 扩容只影响相邻分片
- ✅ 适合频繁扩容
- ❌ 实现复杂

### 4. 复合分片

```yaml
# 同时按 user_id 和 order_id
sharding-columns: user_id,order_id
sharding-algorithm-name: complex_inline

sharding-algorithms:
  complex_inline:
    type: COMPLEX_INLINE
    props:
      # 复合分片：user_id % 4 + order_id % 4
      algorithm-expression: ds$->{(user_id + order_id) % 4}
```

### 5. 自定义分片

```java
public class UserOrderShardingAlgorithm 
    implements StandardShardingAlgorithm<Long> {
    
    @Override
    public String doSharding(
        Collection<String> availableTargetNames,
        PreciseShardingValue<Long> shardingValue
    ) {
        // VIP 用户的订单单独分片（更快的实例）
        Long userId = shardingValue.getValue();
        if (isVipUser(userId)) {
            return availableTargetNames.stream()
                .filter(name -> name.contains("vip"))
                .findFirst().orElseThrow();
        }
        // 普通用户：按 user_id % N
        long suffix = userId % availableTargetNames.size();
        return "orders_" + suffix;
    }
}
```

```yaml
sharding-algorithms:
  custom:
    type: CLASS_BASED
    props:
      strategy: standard
      algorithmClassName: com.example.UserOrderShardingAlgorithm
```

## 📈 扩容方案

### 方案 1：翻倍扩容（推荐）

```
4 分片 → 8 分片（翻倍）

迁移量：50%
4 → 8，原 hash 值需要 mod 8
但 4 % 8 = 4，8 % 8 = 0
所以原分片 0 拆分为 0 和 4
```

**具体步骤：**
```
1. 创建新分片 4-7（共 4 个新库）
2. 按新规则重新计算分片位置
3. 从老分片迁移数据到新分片
4. 修改分片算法
5. 双写过渡
6. 下线老分片
```

### 方案 2：一致性 Hash 扩容

```
4 → 8 分片

迁移量：50%（翻倍）
但只影响相邻节点
适合频繁扩容
```

### 方案 3：双写迁移（零停机）

```java
// 阶段 1：双写
@DS("old_ds")
public void createOrderOld(Order order) {
    oldOrderMapper.insert(order);  // 写老分片
}

@DS("new_ds")
public void createOrderNew(Order order) {
    newOrderMapper.insert(order);  // 写新分片
}

// 业务层：同时调用两个
public void createOrder(Order order) {
    createOrderOld(order);
    createOrderNew(order);
}

// 阶段 2：数据迁移（后台任务）
@Scheduled(fixedRate = 60000)
public void migrate() {
    // 读老分片 → 写新分片
    // 标记老数据已迁移
}

// 阶段 3：切换读取
public Order getById(Long id) {
    // 从新分片读
    return newOrderMapper.selectById(id);
}

// 阶段 4：下线老分片
```

### 方案 4：逻辑扩容（修改算法）

```java
// 阶段 1：按 user_id % 4 + 时间范围
// 阶段 2：按 user_id % 8
// 通过修改分片算法实现
```

## 📊 实战：完整的扩容流程

### 案例：从 4 分片扩到 8 分片

**数据量：**
- 当前：1.6 亿订单
- 预测 1 年后：3.2 亿
- 单分片数据：2 千万 → 4 千万

**扩容步骤：**

```
第 1 步：准备新分片（不接流量）
- 创建 4 个新库：ds4, ds5, ds6, ds7
- 创建对应的 4 × 4 = 16 张表

第 2 步：双写（1-2 天）
- 应用层同时写新老分片
- 写成功率监控（差异 < 0.01%）

第 3 步：数据迁移（1-3 天）
- 全量迁移：按新规则重新计算分片位置
- 增量同步：基于 binlog 持续同步
- 数据校验：pt-table-checksum

第 4 步：切流（灰度）
- 10% 流量切新分片
- 50%
- 100%

第 5 步：下线老分片
- 确认无流量
- DROP TABLE
```

### 迁移脚本示例

```java
@Component
public class ShardMigrationService {
    
    @Autowired
    private OldOrderMapper oldOrderMapper;
    
    @Autowired
    private NewOrderMapper newOrderMapper;
    
    // 全量迁移
    public void fullMigrate() {
        int pageNum = 1;
        while (true) {
            Page<Order> page = oldOrderMapper.selectPage(
                new Page<>(pageNum, 1000)
            );
            if (page.getRecords().isEmpty()) break;
            
            for (Order order : page.getRecords()) {
                // 按新规则重新计算分片
                Long newShard = calculateNewShard(order.getUserId());
                newOrderMapper.insertIgnoreDuplicate(order);
            }
            pageNum++;
        }
    }
    
    // 增量迁移（基于 binlog）
    public void incrementalMigrate() {
        // 用 Canal / Debezium 订阅 binlog
        // 实时同步到新分片
    }
}
```

## 📊 容量规划公式

```
业务目标：
- 5 年内订单总量：50 亿
- 平均每单：1 KB
- 总数据量：5 TB

分片数计算：
- 单分片建议 ≤ 500 GB
- 5 TB / 500 GB = 10 个最小分片
- 考虑 2-3 年增长：10 × 3 = 30 个分片
- 取 2 的 N 次方：32 个分片

库表结构：
- 4 库 × 8 表 = 32 分片
- 单分片：5 TB / 32 = 156 GB ✅
```

## 🔧 ShardingSphere 扩容实践

### 1. 配置柔性分片（支持动态扩缩）

```java
// 自定义分片算法（根据配置动态调整分片数）
public class DynamicShardingAlgorithm 
    implements StandardShardingAlgorithm<Long> {
    
    private int shardCount = 4;  // 可从配置中心读取
    
    @Override
    public String doSharding(
        Collection<String> availableTargetNames,
        PreciseShardingValue<Long> shardingValue
    ) {
        // 实时从配置中心获取
        shardCount = getCurrentShardCount();
        long suffix = shardingValue.getValue() % shardCount;
        return "ds_" + suffix;
    }
}
```

### 2. 灰度发布新分片

```java
// 通过配置中心控制流量分配
public class ShardingRouter {
    
    public String route(Long userId) {
        // 10% 流量去新分片
        if (Math.random() < 0.1 && isNewShardEnabled()) {
            return "new_shard_" + (userId % 4);
        }
        return "old_shard_" + (userId % 4);
    }
}
```

## 🎯 总结

**分片键选择：**
- ✅ 高频查询字段
- ✅ 数据分布均匀
- ✅ 业务不可变
- ✅ 优先 user_id / tenant_id

**扩容原则：**
- ✅ 分片数 = 2^N（便于翻倍）
- ✅ 预留 2-3 倍容量
- ✅ 翻倍扩容（迁移量 50%）
- ✅ 灰度切流
- ✅ 双写过渡（零停机）

**扩容步骤：**
- 1. 准备新分片
- 2. 双写（确保数据一致）
- 3. 全量 + 增量迁移
- 4. 数据校验（pt-table-checksum）
- 5. 灰度切流
- 6. 下线老分片

**MyBatis-Plus 整合：**
- 详见 [🚀 MyBatis-Plus 实战](/12-mybatis/mybatis-plus)
- 自定义分片算法 + 雪花 ID

**下一步：** [🔄 分布式事务](/13-multids/transaction) — 跨数据源一致性解决方案