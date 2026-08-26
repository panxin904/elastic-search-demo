---
title: 缓存模式
---

# 缓存模式

> Cache-Aside、Read-Through、Write-Through、Write-Behind 四种经典模式，以及怎么选。

## 1. 四种主流缓存模式

```
┌──────────────────┬──────────────────────────────────────┐
│ Cache-Aside      │ 应用直接操作缓存和 DB（最常用）      │
├──────────────────┼──────────────────────────────────────┤
│ Read-Through     │ 缓存代理读，DB 同步                 │
├──────────────────┼──────────────────────────────────────┤
│ Write-Through    │ 缓存代理写，同步写 DB               │
├──────────────────┼──────────────────────────────────────┤
│ Write-Behind     │ 缓存代理写，异步写 DB               │
└──────────────────┴──────────────────────────────────────┘
```

## 2. Cache-Aside（旁路缓存）

### 2.1 流程

```
读流程：
  1. 应用查缓存
  2. 命中 → 返回
  3. 未命中 → 查 DB
  4. 写入缓存 → 返回

写流程：
  1. 应用写 DB
  2. 失效缓存（或更新缓存）
  3. 返回
```

### 2.2 代码示例

```java
// 读
public User getUser(String id) {
  User user = cache.get(id);
  if (user == null) {
    user = db.getUser(id);
    cache.set(id, user, 30, TimeUnit.MINUTES);
  }
  return user;
}

// 写
public void updateUser(User user) {
  db.updateUser(user);
  cache.delete(user.getId());  // 失效缓存
}
```

### 2.3 优缺点

```
优点：
  - 实现简单
  - 灵活性高
  - 适合读多写少

缺点：
  - 不一致风险（写 DB + 失效缓存非原子）
  - 首次未命中需要穿透 DB
  - 缓存击穿 / 雪崩 / 穿透（见 three-problems.md）
```

### 2.4 失效 vs 更新

```
方案 1：失效（删除缓存）
  1. 写 DB
  2. 删除缓存
  → 下次读时从 DB 加载
  → 一致性更好（不会写错）

方案 2：更新（写缓存）
  1. 写 DB
  2. 写缓存（新值）
  → 下次读直接命中
  → 但如果写缓存失败就永远不一致

📌 推荐：失效（删除）而非更新
   业界共识：删除更安全
```

## 3. Read-Through（读穿透）

### 3.1 流程

```
读流程：
  1. 应用查缓存
  2. 命中 → 返回
  3. 未命中 → 缓存查 DB
  4. 缓存写入 + 返回

应用只与缓存交互，DB 由缓存代理

📌 与 Cache-Aside 区别：
   Cache-Aside：应用查 DB
   Read-Through：缓存查 DB
```

### 3.2 实现

```java
// Read-Through 缓存库
public class ReadThroughCache {
  public Object get(String key, Loader loader) {
    Object value = cache.get(key);
    if (value == null) {
      value = loader.load();  // loader 内部查 DB
      cache.set(key, value);
    }
    return value;
  }
}

// 应用调用
cache.get("user:123", () -> db.getUser("123"));
```

### 3.3 优缺点

```
优点：
  - 应用代码简单
  - 缓存层统一管理

缺点：
  - 缓存库要支持 loader（复杂）
  - 灵活性差（缓存策略改不了）

📌 Cache-Aside 更常用，Read-Through 是 Cache-Aside 的封装版
```

## 4. Write-Through（写穿透）

### 4.1 流程

```
写流程：
  1. 应用写缓存
  2. 缓存同步写 DB
  3. 全部成功才返回

读流程：同 Cache-Aside
```

### 4.2 优缺点

```
优点：
  - 强一致（缓存和 DB 同步）
  - 读永远命中

缺点：
  - 写延迟高（双写）
  - 写失败回滚复杂
  - 缓存层成为关键路径

📌 适合强一致场景（金融）
```

## 5. Write-Behind（异步写回）

### 5.1 流程

```
写流程：
  1. 应用写缓存
  2. 立即返回
  3. 异步批量写 DB（后台 worker）

读流程：同 Cache-Aside
```

### 5.2 优缺点

```
优点：
  - 写性能极高
  - 合并写（batch）
  - 适合写密集场景

缺点：
  - 数据丢失风险（DB 写之前宕机）
  - 一致性弱
  - 实现复杂

📌 适合能容忍丢失的场景：
   - 点赞数 / 浏览数
   - 计数器
   - 日志
   - 临时状态
```

## 6. 模式对比

```
┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│              │ Cache-Aside  │ Read-Through │ Write-Through│ Write-Behind │
├──────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ 一致性       │ 弱           │ 弱           │ 强           │ 弱（丢失）   │
│ 读性能       │ 高           │ 高           │ 高           │ 高           │
│ 写性能       │ 中           │ 中           │ 低（双写）   │ 极高         │
│ 实现复杂度   │ 低           │ 中           │ 中           │ 高           │
│ 灵活性       │ 高           │ 中           │ 中           │ 低           │
│ 数据丢失风险 │ 低           │ 低           │ 低           │ 高           │
│ 适用         │ 通用         │ 读多写少     │ 强一致       │ 写密集       │
│ 代表         │ Redis 主流   │ Spring Cache │ -            │ 点赞计数     │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
```

## 7. 实战选型

### 7.1 决策树

```
Q1: 是否能容忍数据丢失？
  No  → Write-Through（强一致）
  Yes → Q2

Q2: 读性能 vs 写性能哪个更重要？
  读 → Cache-Aside 或 Read-Through
  写 → Write-Behind

Q3: 应用是否需要直接控制缓存？
  Yes → Cache-Aside
  No  → Read-Through
```

### 7.2 经典场景

```
电商商品详情（读多写少）：
  → Cache-Aside（最常用）

金融账务（强一致）：
  → Write-Through

点赞计数（写密集，可丢失）：
  → Write-Behind

字典数据（读多写少，配置）：
  → Cache-Aside 或 Read-Through
```

## 8. 缓存模式的一致性问题

### 8.1 Cache-Aside 的不一致

```
场景：
  1. 线程 A 写 DB（旧值→新值）
  2. 线程 B 读缓存（miss）
  3. 线程 B 读 DB（读到旧值）
  4. 线程 A 删缓存
  5. 线程 B 写缓存（旧值）
  → 缓存是旧值

📌 双写不一致：
   写 DB + 删缓存非原子
   可能出现"先写缓存后写 DB"

解决：
  - 先删缓存再写 DB（Cache-Aside 变种）
  - 加锁（性能差）
  - 用消息队列异步失效
```

### 8.2 双删策略

```
1. 删缓存
2. 写 DB
3. 延迟 N 毫秒
4. 再删缓存

目的：
  - 第一次删：让旧值失效
  - 延迟：等中间可能有的读请求完成
  - 第二次删：清理第一次删除和读之间的"脏数据"

📌 不是银弹，仍然可能不一致
   但比单删更稳
```

### 8.3 基于消息队列的失效

```
1. 写 DB
2. 发消息到 MQ（key）
3. 多个消费者订阅消息
4. 收到消息后失效缓存

优点：
  - 异步失效，不阻塞写
  - 多消费者保证最终一致

缺点：
  - 引入 MQ 复杂度
  - 消息可能延迟
```

## 9. 缓存 + 事务

```
问题：
  事务内操作缓存？
  - 事务回滚 → 缓存已写 → 不一致
  - 缓存写入失败 → 事务回滚？脏数据？

方案 1：事务后清理
  - 事务内只写 DB
  - 事务提交后异步失效缓存

方案 2：本地缓存 + 延迟双删
  - 事务内写本地缓存
  - 提交后双删

📌 简单业务用方案 1
   复杂业务用 Canal 监听 binlog 异步失效
```

## 10. 一句话总结

```
📌 四种缓存模式：Cache-Aside（最常用）、Read-Through、Write-Through、Write-Behind
📌 Cache-Aside：应用直接操作缓存和 DB
📌 Read-Through：缓存代理读
📌 Write-Through：缓存代理写（强一致）
📌 Write-Behind：缓存异步写（高吞吐，可丢失）
📌 写 DB 后推荐"失效"而非"更新"缓存
📌 Cache-Aside 有不一致风险：双删 / MQ 异步失效可缓解
📌 选型根据一致性要求和读写比例
```

## 11. 参考资料

- Caching Strategies (Microsoft Azure 文档)
- Redis Caching Patterns
- Spring Cache 抽象
- Designing Data-Intensive Applications 第 5 章
- Cache-Aside Pattern (Chris Richardson)


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

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
