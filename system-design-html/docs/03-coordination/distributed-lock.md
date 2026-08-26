---
title: 分布式锁
---

# 分布式锁

> 多台机器的进程 / 线程，对同一份资源进行互斥访问。**正确性 > 性能 > 实现复杂度**。

## 1. 为什么需要分布式锁？

```
单机锁的问题：
  - JVM 锁（synchronized / ReentrantLock）只能管本进程
  - 集群部署 N 台机器，本地锁失效
  - 例：100 台机器同时查库存，每台都做"查-减-写"
      → 全部超卖

分布式锁要求：
  - 互斥：任意时刻只有 1 个 client 持有锁
  - 死锁：持锁 client 崩溃后，锁必须能释放
  - 容错：只要多数节点存活，锁就能正常工作
  - 可重入：同一线程多次获取不阻塞
  - 公平性：FIFO 排队，避免饥饿
```

## 2. 核心实现方案

### 2.1 基于数据库

```
方法 1：唯一索引
  INSERT INTO lock_table(lock_name, owner, expire_at)
  VALUES ('order_lock', 'host-A', NOW() + 30s)
  - 成功 → 获取锁
  - 失败 → 没拿到

  释放：
  DELETE FROM lock_table WHERE lock_name = ? AND owner = ?

方法 2：SELECT FOR UPDATE
  BEGIN;
  SELECT * FROM lock_table WHERE lock_name = ? FOR UPDATE;
  -- 业务逻辑
  COMMIT;

📌 简单，但性能差
   锁等待 = 数据库连接占用
   高并发下 DB 是瓶颈
```

### 2.2 基于 Redis

```
SETNX（set if not exists）：
  SET lock:order 1 EX 30 NX
  - NX = 只在不存在时设置
  - EX = 30s 过期（防死锁）

  释放（必须验证 owner）：
  if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
  else
    return 0
  end

📌 性能高，单 Redis 10万 QPS
   缺点：单点故障（主从切换丢锁）
```

### 2.3 基于 ZooKeeper

```
临时顺序节点：
  /locks/order/lock-00000001  (client A)
  /locks/order/lock-00000002  (client B)
  /locks/order/lock-00000003  (client C)

  1. 在 /locks/order 下创建临时顺序节点
  2. 获取所有子节点，判断自己是不是最小的
  3. 如果是 → 拿到锁
  4. 如果不是 → 监听前一个节点
  5. 前一个节点删除（session 断开）→ 自己被唤醒

📌 强一致，靠 ZK 协议保证
   缺点：ZK 集群维护成本高，性能比 Redis 差
```

### 2.4 对比

| 方案 | 性能 | 可靠性 | 复杂度 | 适用场景 |
|---|---|---|---|---|
| DB 唯一索引 | 低 | 高 | 低 | 锁竞争小，秒级业务 |
| Redis SETNX | 极高 | 中（主从切换丢锁） | 低 | 高并发，性能敏感 |
| ZooKeeper | 中 | 极高 | 高 | 强一致，公平锁 |
| etcd | 中 | 极高 | 中 | K8s 生态 |

## 3. Redlock 算法

### 3.1 为什么需要 Redlock？

```
单 Redis 实例的问题：
  - Master 写入 → Slave 异步复制
  - 写入瞬间 Master 挂了 → 锁未同步
  - 新 Master 上没有锁信息 → 另一个 client 拿到锁
  - **两个 client 持有同一把锁**！

Redlock：
  - 5 个独立 Redis 节点（多数派 = 3）
  - 在 N/2+1 个节点上获取锁成功
  - 总耗时 < 锁 TTL
```

### 3.2 算法流程

```
获取锁：
  1. 当前时间 T0
  2. 依次在 5 个 Redis 实例上 SET key value EX TTL NX
  3. 当前时间 T1
  4. 当成功节点数 >= 3 且 T1 - T0 < TTL
     → 获取锁成功，有效期 = TTL - (T1 - T0)
  5. 否则 → 失败，挨个 DEL 释放

释放锁：
  在所有实例上 DEL（不存在的 key 不报错）
```

### 3.3 Redlock 争议

```
Martin Kleppmann（剑桥博士）反对：
  - 物理时钟漂移 → 锁提前失效
  - GC 停顿 / 网络延迟 → 业务执行超过锁 TTL
  - fencing token 才是正解

Antirez（Redis 作者）反驳：
  - 现实工程中 Redlock 够用
  - fencing token 难实现

📌 业界主流：业务层用 fencing token（单调递增 ID）
   写资源时检查 token，token 旧则拒绝
```

## 4. 工程实现

### 4.1 Redisson（Java 生态）

```java
// 1. 引入
<dependency>
  <groupId>org.redisson</groupId>
  <artifactId>redisson-spring-boot-starter</artifactId>
</dependency>

// 2. 配置
@Bean
public RedissonClient redisson() {
    Config config = new Config();
    config.useClusterServers()
          .addNodeAddress("redis://10.0.0.1:6379", ...);
    return Redisson.create(config);
}

// 3. 使用
RLock lock = redisson.getLock("order:1001");
try {
    if (lock.tryLock(5, 30, TimeUnit.SECONDS)) {
        // 业务逻辑
    }
} finally {
    lock.unlock();
}

📌 Redisson 看门狗：每 10s 续期（TTL/3）
   自动处理 client 崩溃场景
```

### 4.2 超时与续期

```
问题：
  - 业务执行 60s，锁 TTL 设 30s → 锁过期被另一个 client 拿到
  - 业务执行 5s，锁 TTL 设 60s → 浪费 55s

方案 1：合理设置 TTL
  - 业务最大耗时 × 1.5 = TTL

方案 2：看门狗续期
  - 后台线程每 TTL/3 续期
  - Redisson 默认开启

方案 3：业务方主动续期
  - 长任务分阶段续期
```

### 4.3 可重入锁

```java
// Redisson 天然支持
RLock lock = redisson.getLock("order:1001");
lock.lock();     // 第一次获取，count=1
lock.lock();     // 同线程再获取，count=2
lock.unlock();   // count=1
lock.unlock();   // count=0，释放

// 内部数据结构：Hash
// key = 锁名
// field = threadId
// value = count
```

### 4.4 公平锁

```
非公平锁（默认）：
  - client A 拿到锁，client B C D 排队
  - A 释放 → B C D 同时抢，谁先到谁拿
  - 可能造成饥饿

公平锁：
  - 排队，FIFO
  - Redisson：getFairLock("xxx")
  - 性能比非公平低 30-50%
```

## 5. 锁的细分场景

### 5.1 读写锁

```
场景：缓存重建
  - 读：可以并发（共享锁）
  - 写：必须独占（排他锁）

Redisson：
  RReadWriteLock rwLock = redisson.getReadWriteLock("cache:user:1001");
  RLock readLock = rwLock.readLock();
  RLock writeLock = rwLock.writeLock();

  // 读线程
  readLock.lock();
  // 读缓存

  // 写线程
  writeLock.lock();
  // 重建缓存
```

### 5.2 联锁（MultiLock）

```
场景：同时锁多个资源
  - 锁 A、B、C 都拿到才执行
  - 任何一个失败 → 全部释放

RLock lockA = redisson.getLock("A");
RLock lockB = redisson.getLock("B");
RLock lockC = redisson.getLock("C");
RedissonMultiLock multiLock = new RedissonMultiLock(lockA, lockB, lockC);
multiLock.lock();

📌 注意锁顺序，避免死锁
   所有线程按相同顺序加锁：A → B → C
```

### 5.3 信号量（Semaphore）

```
场景：限流
  - 最多 10 个并发访问某个资源
  - 超过排队

RSemaphore semaphore = redisson.getSemaphore("api:limit");
semaphore.trySetPermits(10);   // 设置 10 个许可
semaphore.acquire();           // 获取 1 个
semaphore.release();           // 释放
```

## 6. 经典踩坑

### 6.1 锁过期 vs 业务未完成

```
场景：
  1. client A 拿锁，TTL 30s
  2. GC 停顿 35s
  3. 锁过期，client B 拿到锁
  4. A GC 恢复，继续执行 → 写脏数据

方案：
  - 监控 GC 时间
  - 业务增加 fencing token
  - 看门狗续期（Redisson 默认）
```

### 6.2 时钟漂移

```
场景：
  1. Redis 节点 A 时间快 5s
  2. 节点 B 时间慢 5s
  3. A 以为锁 30s 后过期，B 以为还剩 40s
  4. 同一时刻状态不一致

方案：
  - 部署 NTP 同步
  - 监控时钟漂移
```

### 6.3 锁粒度

```
粗粒度：
  lock("order:process")
  - 全局唯一，串行化
  - 性能差

细粒度：
  lock("order:1001")
  lock("order:1002")
  - 互不阻塞
  - 实现复杂

📌 原则：锁的粒度尽量小
   按业务主键分锁
```

## 7. 一句话总结

```
📌 分布式锁 = 互斥 + 死锁防护 + 容错
📌 实现：DB 唯一索引（最简） / Redis SETNX（最快） / ZK 临时节点（最强一致）
📌 Redlock = 5 节点多数派，业界主流但有争议
📌 Redisson 看门狗：自动续期，处理 client 崩溃
📌 必做：fencing token（单调递增）防 GC 停顿导致的双写
📌 防死锁：合理 TTL + 续期 + 锁顺序
📌 锁粒度：尽量小（按业务主键）
📌 公平锁：FIFO，避免饥饿，但性能低 30-50%
```

## 8. 参考资料

- Redis Redlock 算法规范 (antirez)
- "How to do distributed locking" (Martin Kleppmann, 2016)
- Redisson 官方文档
- ZooKeeper Recipes (Curator)
- etcd v3 Concurrency API


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
