---
title: 短链系统设计
---

# 短链系统设计（Short URL）

> 短链是系统设计面试的"Hello World"。考察候选人对**高读 / 低写**场景下读写路径优化、缓存层级、短码生成等核心问题的把握。

## 1. 业务场景

```
原始长链：https://example.com/article/2024/01/15/long-title-slug
短链：    https://ex.co/Ab3xY
点击短链：302 跳转到长链
```

**为什么需要短链**：
- **短信字数限制**：短信有 70 字符限制，长链占用过多
- **美观**：微博 / Twitter 限制字符数
- **统计**：可以统计点击数据（替代长链直接发）
- **防爬**：长链带参数可被恶意爬取

## 2. 需求估算

| 指标 | 数值 | 备注 |
|---|---|---|
| 月活用户 | 10 亿 | |
| 日均生成短链 | 1 亿 / 天 | 写 |
| 日均访问短链 | 100 亿 / 天 | 读 |
| 写读比 | 1 : 100 | 典型高读低写 |
| QPS（写） | 1 亿 / 86400 ≈ 1200 QPS | 峰值 5x ≈ 6000 |
| QPS（读） | 100 亿 / 86400 ≈ 12 万 QPS | 峰值 5x ≈ 60 万 |
| 短链长度 | 6-7 字符 | Base62 |
| 存储容量 | 100 亿条 × 500B ≈ 500GB | 可控 |
| 短链有效期 | 永久 / 5 年 | 按业务定 |

## 3. 整体架构

```
        ┌──────────┐
        │  Client  │
        └────┬─────┘
             │ POST /shorten { longUrl }
             ▼
   ┌──────────────────┐
   │   API Gateway    │  鉴权 / 限流 / 路由
   └────┬─────────────┘
        │
        ▼
   ┌──────────────────┐
   │  Write Service   │  生成短码 + 持久化
   └────┬─────────────┘
        │
   ┌────┴───────┐
   ▼            ▼
 ┌─────┐    ┌─────────┐
 │ DB  │    │ Cache   │
 │主从 │    │ Redis   │
 └─────┘    └─────────┘
        │
        │ Read Path: 短码 → 长链 → 302
        ▼
   ┌──────────────────┐
   │   Read Service   │  查 cache → miss 查 DB
   └────┬─────────────┘
        │
        ▼
   ┌──────────────────┐
   │  CDN / 边缘缓存  │  热点短链就近返回
   └──────────────────┘
```

## 4. 短码生成（核心）

### 4.1 方案对比

| 方案 | 原理 | 优点 | 缺点 |
|---|---|---|---|
| **Hash + 截断** | MD5 / SHA256 → 取前 N 位 → Base62 | 简单、无状态 | 极小概率冲突；hash 不递增 → DB 写入随机 |
| **自增 ID + Base62** | 分布式 ID → 转 Base62 | 简单、唯一、不冲突 | ID 单调递增 → 可被爬取；分布式 ID 需引入 |
| **Snowflake + Base62** | 64-bit Snowflake → Base62 | 趋势递增、唯一、可排序 | 实现复杂度高；ID 长度变长 |
| **预生成** | 预先发一批短码，写入抢号 | 完全可控 | 预生成 / 回收复杂 |
| **UUID 截断** | UUID → Base62 → 截 N | 无状态 | 长度太长（32 hex） |

### 4.2 推荐方案：自增 ID + Base62（生产首选）

```java
public class ShortCodeGenerator {

  private static final String BASE62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";

  /**
   * 自增 ID 转 Base62
   * @param id 分布式生成的唯一 ID（Snowflake / Leaf）
   * @return 6-7 字符短码
   */
  public static String toBase62(long id) {
    StringBuilder sb = new StringBuilder();
    while (id > 0) {
      sb.append(BASE62.charAt((int)(id % 62)));
      id /= 62;
    }
    return sb.reverse().toString();
  }

  public static long fromBase62(String code) {
    long id = 0;
    for (char ch : code.toCharArray()) {
      id = id * 62 + BASE62.indexOf(ch);
    }
    return id;
  }
}

// 使用：ID = 10000000000L → "9r9vJN" (7 字符)
```

**容量计算**：62^6 = 568 亿，62^7 = 35 万亿。短码长度 6 位足以支撑 100 亿规模。

### 4.3 防 ID 泄露（重要）

```
问题：自增 ID 让攻击者可以遍历（如 ex.co/1, ex.co/2, ...）

📌 对策：
  - 短码混淆：把 ID 与密钥做可逆变换（位运算 / 简单 XOR）
  - 跳转时校验 referer / 签名（防爬增强）
  - 自定义短码：允许用户指定 → 单独字典存储
```

### 4.4 写流程（含 ID 混淆）

```java
public String createShortUrl(String longUrl, Long userId) {
    // 1. 校验长链合法
    validate(longUrl);

    // 2. 检查是否已存在（长链 → 短链映射，避免重复创建）
    String existingCode = cache.getLongToShort(longUrl);
    if (existingCode != null) return existingCode;

    // 3. 生成 ID（Snowflake）
    long id = snowflake.nextId();

    // 4. ID 混淆（可选）
    long obfuscatedId = id ^ SECRET_MASK;

    // 5. 转 Base62
    String shortCode = ShortCodeGenerator.toBase62(obfuscatedId);

    // 6. 写 DB
    ShortUrl record = new ShortUrl();
    record.setShortCode(shortCode);
    record.setLongUrl(longUrl);
    record.setUserId(userId);
    record.setCreatedAt(Instant.now());
    shortUrlRepository.save(record);

    // 7. 写缓存（双写）
    cache.setShortToLong(shortCode, longUrl, 24, TimeUnit.HOURS);
    cache.setLongToShort(longUrl, shortCode, 24, TimeUnit.HOURS);

    return shortCode;
}
```

## 5. 读路径优化（性能核心）

### 5.1 多级缓存

```
┌──────────────────────────────────────────────┐
│ Level 1: CDN / 边缘缓存                       │  命中率 80%+（热点）
│   key: shortCode, value: longUrl             │  TTL: 1 小时
└──────────────────────────────────────────────┘
                    │ miss
                    ▼
┌──────────────────────────────────────────────┐
│ Level 2: Redis 集群                          │  命中率 95%+
│   key: shortCode, value: longUrl             │  TTL: 24 小时
└──────────────────────────────────────────────┘
                    │ miss
                    ▼
┌──────────────────────────────────────────────┐
│ Level 3: MySQL 主库                          │  全量数据
│   按 shortCode 主键查询                       │  P99 < 50ms
└──────────────────────────────────────────────┘
                    │
                    ▼
              302 → 客户端
```

**预期总体命中率**：CDN 80% + Redis 95% * 20% = 99%+
**DB QPS**：100 万 * 1% = 1 万 QPS（可承受）

### 5.2 CDN 预热（热点短链）

```
场景：双十一主会场短链发布后 5 分钟内有 1000 万次点击

📌 对策：
  - 写短链时主动 push 到边缘节点（CDN API）
  - 设置较长 TTL（如 1 小时）
  - DB 同步异步（写完立即返回，异步刷 CDN）
```

### 5.3 缓存击穿（热点 Key 过期瞬间）

```
场景：某热点短链 cache TTL 到期，瞬间 100 万 QPS 打 DB

📌 对策（任选一）：
  - 永不过期（后台异步刷新）
  - value 设为物理时钟 + 逻辑过期，过期时异步刷新（懒加载）
  - mutex 锁：只有一个请求回源，其他等待
  - singleflight（Go）：同 key 请求合并
```

### 5.4 缓存穿透（恶意查询不存在短码）

```
场景：攻击者循环请求 /nonexistent → DB 被打满

📌 对策：
  - 缓存空值（短期）
  - 布隆过滤器（拦截 99%）
  - IP 限流 / WAF
```

## 6. 写路径优化

### 6.1 异步批量写

```
单条写 DB → 频繁事务 → 性能差

📌 优化：
  - 攒批：每 100ms 一次性写一批（Kafka 削峰）
  - 写库用 INSERT BATCH
  - DB 写入与缓存写入解耦（先返回短码给用户，异步刷缓存）
```

### 6.2 数据归档

```
100 亿条数据全部在主库 → 查询 / 备份都慢

📌 对策：
  - 5 年未访问的短链归档到冷存储（OSS / S3）
  - 主库只保留活跃短链
  - 查询未命中主库时查冷库（罕见路径）
```

## 7. 高可用设计

### 7.1 读写分离

```
主库写入 → binlog → 从库同步
读从库：
  - 长链查询（后台管理用）
  - cache miss 后回源（从库可能延迟几百 ms，可接受）
```

### 7.2 多机房部署

```
异地多活：
  - 用户根据 shortCode hash 路由到固定机房
  - 各机房独立写入 + 异步同步
  - 单机房故障不影响整体
```

### 7.3 限流 / 防刷

```
📌 防滥用：
  - 单 IP 短链生成限速（10 个/分钟）
  - 长链黑名单校验（防钓鱼 / 黄赌毒）
  - 短链访问限速（防恶意引流）
```

## 8. 安全考虑

### 8.1 长链合法性

```
📌 必须检查：
  - URL 协议：http/https only（拒绝 ftp/javascript:）
  - 域名黑名单（防钓鱼）
  - 内容扫描（防恶意软件分发）
  - HTTPS 证书校验（防中间人）
```

### 8.2 防爬虫

```
📌 多层防御：
  - 短码混淆（位运算 / XOR）
  - 跳转时校验 Referer
  - 频率限制（IP / UA）
  - CAPTCHA（高频请求）
```

### 8.3 短链滥用检测

```
📌 实时检测：
  - 同一短链短时间大量来自不同 IP → 可疑
  - 短链跳转后停留时间极短（< 1s）→ 可疑
  - 异常国家 / 设备访问 → 需二次验证
```

## 9. 进阶：自定义短码

```
需求：用户想用品牌相关的短码（如 ex.co/sale 而不是 ex.co/Ab3xY）

📌 实现：
  - 自定义短码字典表（short_code → 长链）
  - 创建时先查字典表（避免冲突）
  - 字典表是热点数据（命中率 < 1%）

  写入：
    INSERT INTO short_url (short_code, long_url) VALUES (?, ?)
  查询：
    字典表 → 主表（两步走）
```

## 10. 数据统计与监控

```
📌 必须采集的指标：
  - QPS（读 / 写分别）
  - 缓存命中率（CDN / Redis / DB 三级）
  - 延迟分布（P50 / P99 / P999）
  - 错误率（5xx / 短码不存在）
  - 短码冲突率（极低，要监控）
  - 短链有效期分布（清理过期短链）
```

## 11. 一句话总结

```
📌 短链是典型的高读低写场景 → 重点优化读路径
📌 短码生成推荐自增 ID + Base62 + ID 混淆
📌 多级缓存（CDN + Redis + DB）是性能核心，99%+ 命中率
📌 防滥用：限流 + 黑名单 + 异常检测
📌 数据归档：5 年以上迁冷库
```

## 12. 面试高频追问

```
Q：短码长度为什么是 6-7 位？
A：62^6 = 568 亿够 100 亿规模；62^7 = 35 万亿留扩展空间。Base62 用 0-9A-Za-z。

Q：为什么要二级缓存？一级不够吗？
A：CDN 命中率受限于地理位置和热点分布；Redis 兜底应对长尾；DB 兜底应对缓存失效。

Q：怎么防短链被爬？
A：ID 混淆 + referer 校验 + IP 限流 + 验证码。

Q：DB 主库挂了怎么办？
A：从库提升为主（failover）；短链读取走从库（最终一致）；新写入短暂拒绝。
   进阶：双主写入 + 冲突合并（牺牲一致性换可用性）。

Q：如何保证短链永不过期 / 用户删除的短链？
A：
  永不过期：定期扫描 + 数据归档
  用户删除：维护 deleted_at 字段 + 定期清理（不在主查询路径）
  短链黑名单：单独表 / 布隆过滤器，跳过缓存
```

## 13. 参考资料

- 系统设计面试经典题
- bit.ly 工程博客（短链鼻祖）
- t.cn 微博短链实现（高 QPS 实战）
- 《数据密集型应用系统设计》第 5 章（缓存层设计）
- 《System Design Interview》Vol 1 - Alex Xu（短链章节）