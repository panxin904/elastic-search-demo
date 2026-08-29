---
title: 分布式锁
date: 2026-08-15  # date-auto-injected
---

# 🔐 分布式锁

> 在分布式环境下保证**同一时刻只有一个节点执行某个操作**。

## 🎯 为什么需要分布式锁？

**单机场景下**，可以用 `synchronized` 或 `ReentrantLock` 加锁。

**分布式场景下**，多个 JVM 进程 / 多台机器同时访问共享资源，单机锁失效：

```
应用A (JVM-1) ─┐
                ├─→ 共享资源（DB / Redis / 文件）
应用B (JVM-2) ─┘
```

典型场景：
- **库存扣减**（防超卖）
- **订单幂等**（同一订单只能被处理一次）
- **任务调度**（多节点同时抢任务）

## 🔑 分布式锁的三大特性

| 特性 | 含义 |
|---|---|
| **互斥** | 任意时刻只有一个客户端持有锁 |
| **不死锁** | 持锁客户端崩溃后锁能释放，不会永久占用 |
| **容错** | Redis 集群部分节点故障时仍能正确加解锁 |

## 💻 实现方案对比

### 方案一：基于 Redis（最常用）

#### SETNX + EXPIRE（最简版）

```bash
# 加锁
SETNX key value
EXPIRE key 30  # 防止死锁
```

**问题：** SETNX 和 EXPIRE 不是原子的，可能中间崩溃 → 死锁。

#### SET NX EX（推荐）

```bash
# 加锁（原子操作）
SET lock_key random_uuid NX EX 30
# NX: 仅当不存在时设置
# EX: 过期时间 30 秒

# 解锁（用 Lua 保证原子性）
if redis.call("get",KEYS[1])==ARGV[1] then
    return redis.call("del",KEYS[1])
end
```

> **要点**：value 必须是**唯一值**（UUID），防止误删别人的锁。

#### Redisson 实战（Java 推荐）

```java
// 1. 配置 Redisson
Config config = new Config();
config.useSingleServer().setAddress("redis://127.0.0.1:6379");
RedissonClient redisson = Redisson.create(config);

// 2. 加锁
RLock lock = redisson.getLock("myLock");
lock.lock();                            // 默认 30 秒，自动续期（watchdog）
// 或 lock.lock(10, TimeUnit.SECONDS);    // 不自动续期

try {
    // 业务逻辑
    doBusiness();
} finally {
    lock.unlock();                       // 必须释放
}
```

**Redisson Watchdog 机制**

```
客户端 A 加锁（30s） ─→ 每 10s 自动续期（续到 30s）
     │
     └─→ 客户端 A 宕机 → 30s 后锁自动释放
```

### 方案二：基于 ZooKeeper

**利用临时顺序节点实现**

```
/lock/
  ├─ node-0001 (客户端A) ─→ 获得锁
  ├─ node-0002 (客户端B) ─→ 监听 node-0001
  └─ node-0003 (客户端C) ─→ 监听 node-0002
```

**实现步骤：**
1. 客户端在 `/lock` 下创建**临时顺序**节点
2. 判断自己是否为**最小节点**，是则获取锁
3. 否则监听**前一个节点**的删除事件
4. 前一个节点删除（释放锁或宕机）后，重新尝试

**代码示例（Curator）：**

```java
InterProcessMutex lock = new InterProcessMutex(client, "/lock/path");
if (lock.acquire(10, TimeUnit.SECONDS)) {
    try {
        // 业务逻辑
        doBusiness();
    } finally {
        lock.release();
    }
}
```

### 方案三：基于 MySQL

#### 唯一索引（悲观）

```sql
-- 加锁表
CREATE TABLE distributed_lock (
    id BIGINT PRIMARY KEY,
    lock_key VARCHAR(64) NOT NULL UNIQUE,
    expire_time DATETIME NOT NULL
);

-- 加锁（插入成功即获锁）
INSERT INTO distributed_lock (id, lock_key, expire_time)
VALUES (1, 'order_lock', DATE_ADD(NOW(), INTERVAL 30 SECOND));

-- 释放锁
DELETE FROM distributed_lock WHERE id = 1;
```

#### SELECT FOR UPDATE

```sql
BEGIN;
SELECT * FROM distributed_lock WHERE lock_key = 'order_lock' FOR UPDATE;
-- 业务逻辑
COMMIT;
```

### 方案四：基于 etcd

```java
// etcd v3 的 lease + revision
Lease lease = client.grantLease(30).get();  // 30 秒租约
long revision = client.put(key, value, PutOptions.newBuilder()
        .withLeaseId(lease.getID())
        .build()).get().getHeader().getRevision();

// 监听 key 删除事件
client.watch(key, ...);
```

## 📊 方案对比

| 维度 | Redis (Redisson) | ZooKeeper | MySQL | etcd |
|---|---|---|---|---|
| **性能** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **可靠性** | 中（主从切换丢锁）| 高（ZAB 协议）| 高（DB 持久化）| 高（Raft 协议）|
| **复杂度** | 低 | 高 | 中 | 中 |
| **死锁风险** | 低（自动过期）| 极低（临时节点）| 中（需过期字段）| 低（Lease）|
| **适用场景** | 高并发业务 | 强一致协调 | 低频、强一致 | K8s / 云原生 |

## 🎯 选型建议

| 场景 | 推荐方案 |
|---|---|
| 高并发秒杀 / 抢红包 | **Redis (Redisson)** |
| 定时任务防重复执行 | **Redis / ZooKeeper** |
| 分布式选举（Leader）| **ZooKeeper / etcd** |
| 金融级强一致 | **ZooKeeper / MySQL** |
| 云原生 / K8s | **etcd** |

## ⚠️ 分布式锁的坑

### 1. 锁过期但业务未完成

```
加锁（30s） ─→ 业务执行 60s ─→ 锁已过期，另一进程加锁成功
                → 业务冲突
```

**解决：** Redisson Watchdog 自动续期 / 设置合理过期时间 / 业务幂等

### 2. Redis 主从切换丢锁

```
主节点写入锁 ─→ 还未同步到从 → 主节点宕机 → 新主没有锁数据
                 → 另一客户端加锁成功（双客户端同时持锁）
```

**解决：** RedLock（多 Redis 节点多数同意）/ 使用 ZooKeeper

### 3. 解锁误删别人的锁

```java
// 错误：A 长时间阻塞，锁已过期被 B 获取，A 醒后误删 B 的锁
lock.lock();
doBusiness();   // 耗时 > 锁过期时间
lock.unlock();  // 删除了 B 的锁！
```

**解决：** 解锁前验证 value（UUID）匹配

### 4. 锁粒度问题

- **粗粒度锁**（锁整个方法）：性能差，并发度低
- **细粒度锁**（按业务键锁）：并发高，但设计复杂

```java
// 推荐：按业务 ID 锁
RLock lock = redisson.getLock("order:lock:" + orderId);
```

## 🛡️ 分布式锁 vs 分布式事务

| 维度 | 分布式锁 | 分布式事务 |
|---|---|---|
| **目标** | 互斥访问共享资源 | 多服务数据一致性 |
| **粒度** | 单资源 / 单操作 | 多个操作原子性 |
| **实现** | Redis / ZK / DB | 2PC / TCC / Saga / 本地消息表 |
| **关系** | 分布式事务的实现手段之一 | 更高层的事务语义 |

## 🎓 面试高频问题

| 问题 | 关键点 |
|---|---|
| 分布式锁实现方案？| Redis (SETNX) / ZooKeeper / MySQL / etcd |
| Redis 分布式锁的问题？| 主从切换丢锁 → RedLock 解决 |
| 分布式锁三要素？| 互斥 / 不死锁 / 容错 |
| 如何避免锁误删？| UUID 验证，Lua 脚本原子操作 |

---

- 上一章：[🏗️ 分布式架构](/07-distributed/architecture)
- 下一章：[💰 分布式事务](/07-distributed/distributed-transaction)