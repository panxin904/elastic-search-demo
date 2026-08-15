---
title: 命令速查
---

# 📋 Redis 命令速查

> 60+ 高频 Redis 命令，支持分类过滤和关键词搜索。

<ClientOnly>
  <CommandCheatsheet />
</ClientOnly>

## 🧰 常用场景快速索引

| 场景 | 命令组合 |
|------|---------|
| 计数器 | `INCR / INCRBY / DECR / HINCRBY` |
| 分布式锁 | `SET key val NX EX 30` |
| 排行榜 | `ZADD / ZRANGE / ZINCRBY / ZRANK` |
| 消息队列 | `XADD / XREAD / XREADGROUP / XACK` |
| 限流 | `INCR + EXPIRE` / Lua 脚本 |
| 延迟队列 | `ZADD + ZRANGEBYSCORE` |
| 集合运算 | `SINTER / SUNION / SDIFF` |
| Hash 存储对象 | `HSET / HGETALL / HINCRBY` |
