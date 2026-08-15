---
title: UUID vs Snowflake
---

# UUID vs Snowflake

> 两种最常见的 ID 方案，本质差异是"信息 vs 顺序"。**看业务场景选**。

## 1. UUID 是什么？

```
UUID（Universally Unique Identifier）：
  - 128 bit（16 字节）
  - 全局唯一（理论）
  - 不需要中心节点
  - 跨语言、跨平台

格式：
  xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
  550e8400-e29b-41d4-a716-446655440000

例：
  8-4-4-4-12 = 32 个 16 进制字符
```

## 2. UUID 版本

```
v1（基于时间 + MAC）：
  - 60 bit 时间戳
  - 48 bit MAC 地址
  - 14 bit 时钟序列
  - 可推断生成时间和机器

v2（POSIX / DCE）：
  - 极少使用

v3（基于命名空间 + MD5）：
  - namespace + name
  - MD5 哈希
  - 同输入 → 同 UUID

v4（随机数）：
  - 6 bit 版本 + 122 bit 随机
  - 最常用
  - 完全无序

v5（基于命名空间 + SHA-1）：
  - v3 的 SHA-1 版

v7（基于 Unix 时间 + 随机）⭐ 新：
  - 48 bit 时间戳
  - 74 bit 随机
  - 趋势递增 + 随机
  - RFC 9562（2024）
  - 未来主流
```

## 3. Snowflake 是什么？

```
Snowflake（Twitter 2010）：
  - 64 bit（8 字节）
  - 时间戳 + 机器 + 序列
  - 趋势递增
  - 整数
  - DB 友好
```

## 4. 核心差异

| 维度 | UUID | Snowflake |
|---|---|---|
| 位数 | 128 | 64 |
| 长度 | 36 字符（带-） | 19 字符（最大） |
| 类型 | 字符串 | 长整型 |
| 有序性 | ❌（v4） | ✅ |
| 趋势递增 | ❌ | ✅ |
| DB 索引 | 不友好 | 友好 |
| 全局唯一 | ✅（理论） | ✅ |
| 性能 | 极高（无中心） | 高（中心生成） |
| 信息安全 | ✅（无规律） | ❌（可推时间） |
| 存储空间 | 16-36 字节 | 8 字节 |
| 生成方式 | 客户端 | 服务端 |

## 5. 性能对比

```
生成性能：
  - UUID v4：500ns/个（纯本地）
  - Snowflake：100ns/个（纯内存）
  - UUID v7：200ns/个
  - 差距不大

DB 插入性能（InnoDB）：
  - Snowflake（聚簇索引）：1万 QPS
  - UUID v4（非聚簇）：3000 QPS
  - 差异 3-4 倍（主键长度 + 离散度）

  ┌─────────────────────────────────┐
  │  Snowflake 顺序写入             │   → 顺序 IO
  │  ▁▁▂▂▃▃▄▄                       │   → 范围小
  └─────────────────────────────────┘

  ┌─────────────────────────────────┐
  │  UUID v4 随机写入               │   → 随机 IO
  │  ▃▁▄▂▁▃▄▂▁▃▂▄▁▃▂               │   → 范围大
  └─────────────────────────────────┘
```

## 6. 存储与索引

### 6.1 存储空间

```
MySQL（InnoDB）：
  - bigint：8 字节
  - char(36)：36 字节
  - binary(16)：16 字节

📌 Snowflake 占空间小
   UUID 占空间大（4-5x）
```

### 6.2 索引效率

```
InnoDB 主键 = 聚簇索引：
  - 主键顺序 → 数据物理顺序
  - 顺序插入：1万 QPS
  - 随机插入：3000 QPS

Snowflake 顺序 → 高效
UUID v4 随机 → 低效（页分裂）

📌 这就是 InnoDB 强烈推荐 Snowflake 的原因
```

### 6.3 二级索引

```
二级索引存主键：
  - Snowflake：8 字节
  - UUID 字符串：36 字节
  - UUID 二进制：16 字节
```

## 7. 信息安全

### 7.1 UUID 安全优势

```
UUID v4 完全随机：
  - 无法推测时间
  - 无法推测机器
  - 撞库困难（2^122 空间）

📌 用于：
   - Session ID
   - API Key
   - Token
   - 文件名（防爬）
```

### 7.2 Snowflake 风险

```
可以从 ID 推：
  - 生成时间（误差 ms）
  - 机器 ID
  - 业务量

📌 不能用于：
   - Session ID（可推测创建时间）
   - API Key（可枚举）
```

## 8. 网络传输

```
JSON：
  - UUID：36 字符 → 36 字节
  - Snowflake：20 字符 → 20 字节
  - Snowflake 优势

二进制：
  - UUID：16 字节
  - Snowflake：8 字节
  - Snowflake 优势

📌 高 QPS / 移动端 → Snowflake
   后台管理 / 配置 → UUID 字符串方便
```

## 9. 业务场景选型

### 9.1 用 Snowflake

```
- 业务主键（订单 ID / 支付 ID / 用户 ID）
- 高 QPS（10w+）
- DB 主键
- 趋势查询（按时间分页）
- 多机房（ID 携带机房信息）
```

### 9.2 用 UUID

```
- 分布式唯一标识
- 离线生成（不需要中心）
- 信息安全要求（防枚举）
- 跨语言 / 跨系统传递
- Session ID / Token
- 资源 ID（文件名 / 临时文件）
```

### 9.3 用 UUID v7（新趋势）

```
- 想用 UUID 但要趋势递增
- 2024+ 主流推荐
- 兼容 UUID 库
- 索引友好

📌 UUID v7 是未来 5 年的方向
   但需要库支持
```

## 10. 实际工程建议

### 10.1 主键选型

```
MySQL（InnoDB）主键：
  - 优先：bigint + Snowflake
  - 次选：binary(16) + UUID v7
  - 避免：char(36) + UUID v4

业务表：
  - 订单 ID：Snowflake（业务量大、要排序）
  - 用户 ID：Snowflake（聚簇友好）
  - 商品 ID：Snowflake / 业务前缀
```

### 10.2 分布式唯一标识

```
非主键场景：
  - 订单号：业务前缀 + Snowflake
    例：OR2026080912345601
  - 流水号：业务前缀 + UUID
    例：TR-550e8400-e29b-41d4
  - 跟踪 ID：UUID v4
    例：trace-550e8400-e29b-41d4
```

### 10.3 混合方案

```
实际项目：
  - 业务 ID（外露）：业务前缀 + Snowflake
  - 内部主键：Snowflake
  - 文件名：UUID v4
  - 跟踪 ID：UUID v4
  - Token：UUID v4

📌 按场景选
   不是非此即彼
```

## 11. 经典面试题

### 11.1 为什么 MySQL 主键不推荐 UUID？

```
A：
  1. UUID v4 128 bit，bigint 64 bit
  2. UUID 字符串 36 字节，bigint 8 字节
  3. UUID 随机 → 主键非顺序 → 页分裂
  4. 页分裂 → 写入性能下降 3-4x
  5. 二级索引占空间大

  解决：
    - binary(16) 存 UUID
    - 用 UUID v7（趋势递增）
    - 或直接用 Snowflake
```

### 11.2 Snowflake 唯一 ID 怎么保证？

```
A：
  - 41 bit 时间戳：不同毫秒 ID 必不同
  - 10 bit 机器：不同机器 ID 必不同
  - 12 bit 序列：同毫秒同机器不同序列
  - 三段至少一段不同 → ID 唯一
```

### 11.3 Snowflake 时钟回拨怎么办？

```
A：
  1. 拒绝生成（最稳）
  2. 等待追回（叶 Leaf 方案）
  3. 备用 workerId
  4. 监控告警
```

## 12. 一句话总结

```
📌 UUID = 128 bit + 随机 + 安全，趋势无序 + 索引不友好
📌 Snowflake = 64 bit + 趋势递增 + DB 友好，但可推时间
📌 性能：生成接近（< 1μs），但 DB 插入 Snowflake 快 3-4x（顺序写）
📌 存储：Snowflake 8B / UUID 16-36B，索引大
📌 选型：
   主键 → Snowflake
   标识 → UUID
   未来 → UUID v7
📌 UUID v7 是新趋势（RFC 9562），兼容 UUID 库 + 趋势递增
📌 实际项目：业务 ID 用 Snowflake，跟踪 ID 用 UUID
```

## 13. 参考资料

- RFC 4122 UUID 标准
- RFC 9562 UUID v7 新标准
- Twitter Snowflake 原始论文
- "MySQL 为什么 UUID 不适合主键"（美团技术博客）
- "UUIDv7 介绍"（IETF 草案）
- Percona UUID vs bigint 性能测试
