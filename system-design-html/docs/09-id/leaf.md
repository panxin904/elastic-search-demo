---
title: Leaf 美团方案
---

# Leaf 美团方案

> 美团开源的分布式 ID 生成服务。**号段模式 + Snowflake 双模式**，生产验证。

## 1. Leaf 简介

```
Leaf（美团）：
  - 2017 年开源
  - Java 实现
  - 高可用、高性能
  - 已被美团 / 携程 / 360 等使用

两种模式：
  - Leaf-segment：号段模式（基于 DB）
  - Leaf-snowflake：Snowflake 改进版

📌 推荐 Leaf-segment
   简单、可靠、性能足够
```

## 2. Leaf-segment 号段模式

### 2.1 核心思想

```
传统 DB 自增：
  - 每生成 1 个 ID → 1 次 DB 请求
  - QPS 受限于 DB（1万左右）

Leaf 号段：
  - 每次从 DB 拿一段 ID
  - 例：拿 [1, 1000]
  - 内存分配 1-1000
  - 用完再拿 [1001, 2000]

性能提升：
  - DB 1 次拿 1000 个 ID
  - 1 万 QPS → 10 QPS（DB 压力骤降）
```

### 2.2 数据结构

```sql
CREATE TABLE leaf_alloc (
  biz_tag     VARCHAR(128) NOT NULL DEFAULT '',
  max_id      BIGINT       NOT NULL DEFAULT 1,
  step        INT          NOT NULL DEFAULT 1000,
  description VARCHAR(256) DEFAULT NULL,
  update_time TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (biz_tag)
) ENGINE=InnoDB;

INSERT INTO leaf_alloc (biz_tag, max_id, step) VALUES ('order', 1, 1000);
```

字段说明：
```
- biz_tag：业务标识
- max_id：当前最大 ID
- step：每次申请的步长
- update_time：更新时间
```

### 2.3 分配流程

```
1. 内存中缓存号段：[1, 1000]
2. 分配 ID = 1, current = 2
3. ...分配到 1000
4. 再次分配 → 号段用完
5. 从 DB 申请新号段：
   UPDATE leaf_alloc SET max_id = max_id + step WHERE biz_tag = 'order';
   SELECT max_id FROM leaf_alloc WHERE biz_tag = 'order';
6. 新号段 [1001, 2000]
7. 双号段缓存（防止 DB 抖动）
```

### 2.4 双 Buffer 优化

```
问题：
  - 一个号段用完，要等 DB 返回
  - 期间不能发 ID

双号段：
  - 当前号段用完时，异步加载下一个
  - 用户无感知
  - 类似 CPU 双 cache line

  ┌────────┐  ┌────────┐
  │ segment1 │  │ segment2 │
  │ (active) │  │ (loading)│
  └────────┘  └────────┘

📌 美团优化后 QPS 提升 30%
```

### 2.5 动态调整 step

```
问题：
  - 业务增长快，step 1000 不够
  - 业务变小，step 1000 浪费

动态 step：
  - 监控消费速度
  - 消费越快 → step 越大
  - 例：消费 1000/10s → 下次 step 2000
  - 消费 100/10s → 下次 step 500

📌 步长自适应
   美团内部使用
```

## 3. Leaf-snowflake

### 3.1 改进点

```
原始 Snowflake 问题：
  - workerId 分配难
  - 时钟回拨
  - 强依赖 ZK

Leaf 改进：
  - workerId 通过 ZK 持久化
  - 时钟回拨：抛错 + 报警（不生成）
  - 弱依赖 ZK（可降级）
```

### 3.2 ZK 路径

```
/snowflake/{ip}-{port}-{timestamp}
  - 启动时创建临时顺序节点
  - 节点编号 = workerId
  - 持久化到本地文件（防 ZK 不可用）

  /snowflake/192.168.1.10-8080-1234567890
  /snowflake/192.168.1.11-8080-1234567891
  /snowflake/192.168.1.12-8080-1234567892

  workerId = 顺序号 (1, 2, 3, ...)
```

### 3.3 时钟回拨

```
场景：
  - 时间回拨 1s
  - Snowflake 抛 RuntimeException
  - Leaf 改为：抛错 + 报警 + 等待时间追回

代码：
  if (timestamp < lastTimestamp) {
      long offset = lastTimestamp - timestamp;
      if (offset <= 5) {
          try { Thread.sleep(offset << 1); } catch (...) {}
      } else {
          throw new RuntimeException("Time back超过5ms");
      }
  }
```

## 4. 部署架构

```
┌──────────┐
│  Client  │
└────┬─────┘
     │ HTTP / Thrift
     ↓
┌──────────┐
│  Leaf    │  (集群)
│  Server  │
└────┬─────┘
     │
     ↓
┌──────────┐
│   MySQL  │  (号段表)
└──────────┘

部署：
  - 至少 2 节点（高可用）
  - 通过 LVS / Nginx 负载均衡
  - DB 1 主 1 从
```

## 5. Spring Boot 集成

```java
// 1. 启动 Leaf Server（独立服务）
// 2. 客户端调用

@Service
public class OrderService {
    @Autowired
    private RestTemplate restTemplate;

    public long generateOrderId() {
        // 调用 Leaf API
        String url = "http://leaf-server/api/segment/get/order";
        return Long.parseLong(restTemplate.getForObject(url, String.class));
    }
}
```

```java
// Leaf 客户端 SDK（推荐）
// github.com/Meituan-Dianping/Leaf 提供的 client
LeafService leaf = new LeafService("http://leaf-server:8080");
long id = leaf.getId("order");
```

## 6. 监控与运维

### 6.1 监控指标

```
- QPS：每秒生成数
- 延迟：P50 / P99
- DB 请求频率
- 号段使用速度
- 内存号段剩余
```

### 6.2 告警

```
- DB 请求频率 > 100/s → 可能 step 太小
- 号段切换频繁 → step 不够
- 时钟回拨 → 立即告警
- Leaf 不可用 → 立即告警
```

### 6.3 灾备

```
Leaf Server 挂了：
  - 客户端重试
  - 切到备用 Leaf 集群
  - 极端情况：DB 自增兜底

号段用完：
  - 监控告警
  - 自动扩容
  - 紧急手动调大 step
```

## 7. 容灾策略

### 7.1 读不到 DB

```
策略：
  - 用上次缓存的号段继续
  - 持久化到本地文件
  - 启动时自动加载

📌 Leaf-segment 不强依赖 DB
   DB 短时间不可用不致命
```

### 7.2 ZK 不可用

```
Leaf-snowflake：
  - 启动时从本地文件加载 workerId
  - ZK 恢复后重新注册
  - 优雅降级

📌 必须保证 workerId 唯一
   启动时检查本地文件
```

### 7.3 Leaf 全挂

```
客户端 fallback：
  1. Leaf-segment → DB 自增
  2. Snowflake
  3. UUID
  4. 报警 + 限流
```

## 8. 性能数据

```
Leaf-segment（单实例）：
  - QPS：5万+（号段模式）
  - P99：< 5ms
  - DB 压力：1000 ID/s 一次

Leaf-snowflake（单实例）：
  - QPS：10万+
  - P99：< 1ms
  - 不依赖 DB

📌 实际生产中
   Leaf-segment 更稳（DB 是真理之源）
```

## 9. 与其他 ID 方案对比

| 方案 | 性能 | 可靠性 | 复杂度 | 依赖 |
|---|---|---|---|---|
| **Leaf-segment** | 中（5w QPS） | 极高 | 低 | DB |
| **Leaf-snowflake** | 高（10w QPS） | 高 | 中 | ZK |
| **Snowflake** | 极高 | 中 | 中 | 自管 workerId |
| **UUID** | 极高 | 高 | 极低 | 无 |
| **DB 自增** | 低 | 极高 | 极低 | DB |

## 10. 适用场景

```
✅ 适合：
  - 业务规模大（DAU > 百万）
  - 趋势递增 ID
  - 业务可分 tag（订单/支付/用户）
  - 已有 MySQL 基础设施

❌ 不适合：
  - 业务量小（UUID 够用）
  - 信息安全要求（UUID）
  - 单库单表（DB 自增）
  - 实时性要求极高（Snowflake 更好）
```

## 11. 一句话总结

```
📌 Leaf = 号段模式（推荐） + Snowflake 模式
📌 号段模式：批量从 DB 拿 ID，5万 QPS，强依赖 DB 但 DB 压力小
📌 双 Buffer：当前号段用完时异步加载下一段，无缝切换
📌 动态 step：消费越快 step 越大，自适应
📌 Snowflake 模式：依赖 ZK 分配 workerId，时钟回拨抛错
📌 灾备：本地缓存号段 + ZK 本地文件 fallback + 多 Leaf 集群
📌 性能：号段 5万 QPS，Snowflake 10万 QPS
📌 适用：美团 / 携程 / 360 等大规模生产验证
```

## 12. 参考资料

- 美团 Leaf 官方 GitHub
- "Leaf：美团分布式 ID 生成服务"（美团技术博客）
- 百度 UidGenerator
- 滴滴 TinyID
- "分布式 ID 生成方案总结"（美团技术博客）


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
