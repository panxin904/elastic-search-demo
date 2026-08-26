---
title: 一致性 Hash 与分片键
---

# 🔑 一致性 Hash 与分片键

> 分库分表的核心是**分片键**的选择。选错了会导致数据倾斜、热点频发、扩容困难。

## 🎯 分片键选择的核心原则

### 三大原则

```
1. 高频查询字段
   - 80% 的查询都带这个字段
   - 例：订单表 → user_id

2. 数据分布均匀
   - 避免数据倾斜
   - 例：不要用 status（有 5 个值）

3. 业务不可变
   - 分片键一旦确定，不要轻易改
   - 例：用 user_id 而不是 username（可能改名）
```

## 📊 分片键的常见问题

### 1. 数据倾斜

```
分片键选择：status（订单状态）

分片分布：
- pending:  10 万 → 分片 0
- paid:    500 万 → 分片 1
- shipped: 300 万 → 分片 2
- done:    200 万 → 分片 3

问题：
- 分片 1 压力是分片 0 的 50 倍
- 单分片成为瓶颈
```

### 2. 热点分片

```
分片键选择：created_at（按时间）

新订单都写入最新分片
最新分片成为热点

问题：
- 新分片 IO 压力大
- 老分片闲置
```

### 3. 扩容困难

```
分片键选择：id（取模）

4 → 8 分片时：
- 所有数据需要重新 hash
- 数据迁移成本巨大
- 几乎无法不停机扩容
```

## 🎯 优秀分片键的特征

### 1. 高基数

```
✅ user_id: 100 万用户 = 100 万不同值
❌ status: 只有 5 个值
❌ is_deleted: 0/1 两个值
```

### 2. 均匀分布

```
✅ user_id: 用户 ID 均匀分布
❌ country: 某些国家数据特别多（中国 vs 冰岛）
```

### 3. 业务稳定

```
✅ user_id: 用户 ID 永不变
❌ username: 用户可能改名
❌ phone: 用户可能换号
```

### 4. 高频查询

```
✅ user_id: "我的订单" 80% 查询带 user_id
✅ order_id: 订单详情按 ID 查询
```

## 🔑 一致性 Hash 算法

### 为什么需要一致性 Hash？

```
普通 Hash 取模（4 分片）：

user_id = 1:  1 % 4 = 1  → 分片 1
user_id = 2:  2 % 4 = 2  → 分片 2
user_id = 3:  3 % 4 = 3  → 分片 3
user_id = 4:  4 % 4 = 0  → 分片 0
user_id = 5:  5 % 4 = 1  → 分片 1

扩容：4 → 8 分片
- user_id = 1:  1 % 8 = 1  → 分片 1（不变）
- user_id = 2:  2 % 8 = 2  → 分片 2（不变）
- user_id = 3:  3 % 8 = 3  → 分片 3（不变）
- user_id = 4:  4 % 8 = 4  → 分片 4（变化！）
- user_id = 5:  5 % 8 = 5  → 分片 5（变化！）

→ 50% 的数据需要迁移
```

### 一致性 Hash 原理

```
将分片组织成 Hash 环：

        分片 0
         |
   分片 3 +  分片 1
         |
        分片 2

数据也映射到环上：
key 顺时针找到的第一个分片就是它所属的分片
```

### 一致性 Hash 扩容

```
原始：分片 0、1、2、3
扩容：新增分片 4

影响：
- 只有分片 3 和分片 0 之间的数据受影响
- 其他分片的数据不动
- 迁移量从 50% 降到 12.5%（1/N）
```

## 📊 一致性 Hash 的虚拟节点

```
问题：
物理节点少时（如 4 个），数据可能分布不均

解决：虚拟节点
- 每个物理节点对应多个虚拟节点（150-200 个）
- 虚拟节点均匀分布在 Hash 环上
- 一个物理节点负责多个虚拟节点区间
```

```java
// 实现（Java）
public class ConsistentHashRouter {
    private final SortedMap<Integer, String> ring = new TreeMap<>();
    private static final int VIRTUAL_NODES = 160;

    public void addNode(String node) {
        for (int i = 0; i < VIRTUAL_NODES; i++) {
            int hash = hash(node + "#" + i);
            ring.put(hash, node);
        }
    }

    public String route(String key) {
        int hash = hash(key);
        SortedMap<Integer, String> tail = ring.tailMap(hash);
        return tail.isEmpty() ? ring.get(ring.firstKey()) : tail.get(tail.firstKey());
    }
}
```

## 🎯 分片键实战选择

### 案例 1：订单表

```sql
CREATE TABLE orders (
  id BIGINT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  amount DECIMAL(10, 2),
  status VARCHAR(20),
  created_at DATETIME
);

-- 候选分片键：id, user_id, created_at

-- 评估：
-- 1. id：均匀、稳定，但多数查询不按 id
-- 2. user_id：高频（"我的订单"），均匀
-- 3. created_at：均匀性差（新分片热）

-- ✅ 选择 user_id
-- 原因：80% 查询带 user_id
```

### 案例 2：消息表

```sql
CREATE TABLE messages (
  id BIGINT PRIMARY KEY,
  from_user_id BIGINT,
  to_user_id BIGINT,
  content TEXT,
  created_at DATETIME
);

-- 候选分片键：id, from_user_id, to_user_id, created_at

-- 场景分析：
-- 1. 发送消息：按 from_user_id
-- 2. 接收消息：按 to_user_id（更频繁）

-- ❌ 难点：分片键只能选一个
-- 解决：
-- 1. 用 to_user_id（接收更频繁）
-- 2. 用 to_user_id 分片 + 维护 from 索引表
-- 3. 双写：to_user_id 和 from_user_id 各自一份
```

### 案例 3：日志表

```sql
CREATE TABLE logs (
  id BIGINT PRIMARY KEY,
  user_id BIGINT,
  level VARCHAR(20),
  message TEXT,
  created_at DATETIME
);

-- 按 user_id 还是 created_at？

-- 用户日志查询（"我的操作记录"）：用 user_id
-- 系统日志查询（"今天的错误"）：用 created_at

-- ✅ 实际方案：
-- 1. 按 created_at 按月分片（热冷分离）
-- 2. 老数据归档到 HDFS / 冷存储
```

## 🛠️ 跨分片查询的处理

### 1. 强制带分片键

```sql
-- ✅ 好：带分片键，路由到单分片
SELECT * FROM orders WHERE user_id = 100;

-- ❌ 差：不带分片键，需要扫所有分片
SELECT * FROM orders WHERE amount > 1000;
-- 优化：用 ES 维护二级索引
```

### 2. 二级索引表

```sql
-- 创建索引表（用 ES 或单独的 MySQL 表）
-- key: amount
-- value: order_id 列表

-- 查询流程：
-- 1. 先查 ES（amount > 1000）→ 拿到 order_id 列表
-- 2. 再查分片（WHERE id IN (...)）
```

### 3. 异构索引

```
ES（Elasticsearch）：
- 适合复杂查询、模糊查询
- 不适合事务

TiDB：
- 既是分片又是事务
- 适合复杂查询 + 事务

MySQL：
- 主力分片
- 强事务
```

## 🔧 扩容策略

### 1. 翻倍扩容（推荐）

```
4 分片 → 8 分片（翻倍）

数据迁移：
- 4 → 8，hash 值要 mod 8
- 但 4 mod 8 = 4
- 8 mod 8 = 0
- 所以原分片 0 拆分为新分片 0 和 4
- 迁移量：1/2 = 50%
```

```
一致性 Hash 扩容：
- 4 → 8 分片
- 新增 4 个分片
- 迁移量：4/8 = 50%
```

### 2. 双写迁移

```sql
-- 1. 配置双写（新旧分片都写）
INSERT INTO orders_new ...  -- 写新分片
INSERT INTO orders_old ...  -- 写旧分片

-- 2. 数据迁移（后台任务）
-- 把旧分片数据按新规则迁移到新分片

-- 3. 数据校验
SELECT COUNT(*) FROM orders_new;
SELECT COUNT(*) FROM orders_old;
-- 必须一致

-- 4. 切流（应用开始读新分片）

-- 5. 下线旧分片
DROP TABLE orders_old;
```

### 3. 灰度切流

```
阶段 1：1% 流量切到新分片
阶段 2：10%
阶段 3：50%
阶段 4：100%

每个阶段观察：
- 延迟
- 错误率
- 数据一致性
```

## 🎯 总结

**分片键选择黄金法则：**
- ✅ 高频查询字段
- ✅ 高基数（> 10000）
- ✅ 分布均匀
- ✅ 业务稳定（不会变）

**一致性 Hash：**
- ✅ 扩容只影响相邻节点
- ✅ 虚拟节点均匀分布
- ✅ 适用频繁扩容场景

**扩容策略：**
- 翻倍扩容（4 → 8）迁移量 50%
- 一致性 Hash 扩容更平滑
- 双写迁移保证数据一致性
- 灰度切流控制风险

**下一步：** [💻 mysql client 命令](../11-tools/mysql-client) — 工具速查系列


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
