---
title: 命令速查
date: 2026-08-15  # date-auto-injected
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

## 📚 跨站参考：🧰 常用场景快速索引

<!-- xlink-dedup:do-not-edit -->

本节在 3 站展开，最权威版本位于 **redis** 站（[https://java-px.bot.cd/redis/](https://java-px.bot.cd/redis/)）。

其他站参考：[kafka](https://java-px.bot.cd/kafka/) / [python](https://java-px.bot.cd/python/)

跨站关联由 `xlink-injector.py` + `crosslink-dedup.py` 自动生成（§8.68）。


## 📱 手机扫码继续阅读

<ClientOnly>
  <QrShare />
</ClientOnly>
