---
title: 并发控制
date: 2026-08-15  # date-auto-injected
---

# 并发控制

多线程环境下保证数据一致性和线程安全。

## 常见并发问题

### 超卖（库存扣减）

```java
// ❌ 危险：读-判断-写，非原子操作
Product product = productMapper.selectById(id);
if (product.getStock() > 0) {
    product.setStock(product.getStock() - 1);
    productMapper.updateById(product);
}

// ✅ 方案1：数据库乐观锁
UPDATE t_product SET stock = stock - 1, version = version + 1
WHERE id = #{id} AND stock > 0 AND version = #{version}
// 判断 affected rows == 0 → 重试

// ✅ 方案2：Redis 扣减
Long stock = redisTemplate.opsForValue().decrement("stock:" + id);
if (stock < 0) throw new BusinessException("库存不足");

// ✅ 方案3：分布式锁
String lockKey = "lock:product:" + id;
if (redisLock.tryLock(lockKey, 3, TimeUnit.SECONDS)) {
    try {
        // 扣库存逻辑
    } finally {
        redisLock.unlock(lockKey);
    }
}
```

## ThreadLocal

```java
public class UserContext {
    private static final ThreadLocal<LoginUser> USER_HOLDER = new ThreadLocal<>();

    public static void set(LoginUser user) { USER_HOLDER.set(user); }
    public static LoginUser get() { return USER_HOLDER.get(); }
    public static void clear() { USER_HOLDER.remove(); }  // ！必须清理
}

// 拦截器设置
@Override
public boolean preHandle(...) {
    LoginUser user = parseToken(request.getHeader("Authorization"));
    UserContext.set(user);
    return true;
}

@Override
public void afterCompletion(...) {
    UserContext.clear();  // 防止内存泄漏
}
```

## synchronized vs Lock

| | synchronized | ReentrantLock |
|---|---|---|
| 实现 | JVM 级，关键字 | JDK 级，API |
| 锁释放 | 自动（代码块结束/异常） | 手动（finally unlock） |
| 功能 | 单一 | 可中断、超时、公平锁、条件变量 |
| 性能 | 优化后差异不大 | 优化后差异不大 |

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="concurrency" :height="400" />
