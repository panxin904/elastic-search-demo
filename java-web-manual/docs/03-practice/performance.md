---
title: 性能优化
date: 2026-08-15  # date-auto-injected
---

# 性能优化

性能优化是一个持续的过程，从 SQL 调优到架构升级，逐层深入。

## 优化层次

```
第一层 - SQL 层：慢 SQL 优化、索引、读写分离
第二层 - 应用层：缓存、异步、批量、连接池
第三层 - JVM 层：GC 调优、堆内存
第四层 - 架构层：分库分表、微服务拆分、CDN
```

## SQL 优化

```sql
-- ❌ 全表扫描
SELECT * FROM t_order WHERE YEAR(create_time) = 2024;

-- ✅ 走索引
SELECT * FROM t_order
WHERE create_time >= '2024-01-01' AND create_time < '2025-01-01';

-- ❌ 负向查询不走索引
SELECT * FROM t_user WHERE status != 1;

-- ✅ 正向查询
SELECT * FROM t_user WHERE status IN (2, 3);
```

## 应用层优化

```java
// 批量操作替代循环
// ❌ 循环插入
for (Order order : orders) {
    orderMapper.insert(order);
}

// ✅ 批量插入（MyBatis-Plus）
orderMapper.insertBatch(orders);

// 异步处理
@Async
public void sendNotification(Order order) {
    // 发短信、推送通知等非核心操作
}

// 并行调用
CompletableFuture<User> userFuture = CompletableFuture
    .supplyAsync(() -> userService.getById(userId));
CompletableFuture<Product> productFuture = CompletableFuture
    .supplyAsync(() -> productService.getById(productId));
CompletableFuture.allOf(userFuture, productFuture).join();
```

## 连接池配置

```yaml
spring:
  datasource:
    hikari:
      minimum-idle: 10
      maximum-pool-size: 50           # 根据业务调整
      idle-timeout: 300000
      max-lifetime: 1200000
      connection-timeout: 30000
```

## 性能排查工具

| 工具 | 用途 |
|---|---|
| Arthas | 在线诊断（方法耗时、热更新） |
| JProfiler | JVM 性能分析 |
| Druid | SQL 监控 |
| SkyWalking | 链路追踪（找慢接口） |

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="performance" :height="400" />
