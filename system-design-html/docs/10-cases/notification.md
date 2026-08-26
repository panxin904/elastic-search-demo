---
title: 消息推送系统
---

# 消息推送系统

> 给 1000 万用户推送一条系统消息，3 秒内到达率 99%。**多通道 + 可靠性 + 实时性**。

## 1. 什么是消息推送？

```
推送（Push）：
  - 服务端主动把消息送到客户端
  - 不需要客户端轮询
  - 节省电量和流量

产品形态：
  - 系统通知（升级提醒、订单状态）
  - 营销推送（活动、新品）
  - 即时通讯（IM 消息）
  - 验证码（OTP）
  - 实时数据（股价、比赛）
```

## 2. 核心要求

```
1. 高到达率：
   - 99% 以上用户能收到
   - 离线消息下次启动要看到

2. 实时性：
   - 在线用户秒级到达
   - P99 < 3s

3. 可靠性：
   - 不丢消息（金融场景）
   - 不重复（至少一次 + 幂等）

4. 高并发：
   - 全量推送 1000 万 QPS
   - 单点故障不能拖垮系统

5. 渠道多样：
   - iOS / Android / Web / SMS
   - 智能选择最佳通道
```

## 3. 整体架构

```
                业务系统
                   ↓ (消息事件)
            ┌─────────────┐
            │ 推送中心    │
            │ (消息分发)  │
            └──────┬──────┘
                   ↓
            ┌──────────────┐
            │ 消息队列    │
            │ (Kafka/MQ)  │
            └──────┬──────┘
                   ↓
    ┌──────┬──────┼──────┬──────┐
    ↓      ↓      ↓      ↓      ↓
  APNs   FCM    WebSocket  SMS  邮件
  (iOS)  (Android)  (Web) (备用) (兜底)

                用户设备
```

## 4. 推送通道

### 4.1 iOS APNs

```
APNs（Apple Push Notification service）：
  - 苹果官方通道
  - 二进制协议（HTTP/2 + JWT）
  - 单设备 1 个 device token
  - 离线消息 APNs 缓存 28 天

  ┌──────────┐    ┌──────┐    ┌─────┐
  │  App后端 │ →  │APNs  │ →  │iPhone│
  └──────────┘    └──────┘    └─────┘

调用：
  POST https://api.push.apple.com/3/device/{device_token}
  Headers:
    authorization: bearer {jwt}
    apns-topic: com.example.app
  Body:
    {"aps": {"alert": "Hello", "badge": 1, "sound": "default"}}

📌 优点：系统级通道，App 没启动也能收到
📌 限制：每条 4KB，仅 1 个设备
```

### 4.2 Android FCM

```
FCM（Firebase Cloud Messaging）：
  - Google 官方通道
  - 国内厂商通道：华为 HMS / 小米 Push / OPPO / vivo
  - 国内必须用厂商通道（Google 服务被墙）

  ┌─────────┐     ┌──────┐     ┌────────────┐
  │ App后端 │ →   │ FCM  │ →   │ Android    │
  └─────────┘     └──────┘     └────────────┘
                    ↓
              ┌──────────────┐
              │ 厂商通道     │（国内）
              │ HMS/小米/...│
              └──────────────┘

调用：
  POST https://fcm.googleapis.com/v1/projects/{project}/messages:send
  Body:
    {
      "message": {
        "token": "device_token",
        "notification": {"title": "Hello", "body": "World"}
      }
    }
```

### 4.3 WebSocket / SSE

```
WebSocket：
  - 长连接，全双工
  - 适合 IM / 实时数据
  - 心跳维持（30s）

  ┌──────────┐  WS Handshake  ┌────────┐
  │ 浏览器   │ ←────────────→│ 推送服务│
  └──────────┘                 └────────┘

SSE（Server-Sent Events）：
  - 单向（服务端 → 客户端）
  - 基于 HTTP，简单
  - 适合行情 / 通知

📌 WebSocket 是 IM 主流
   SSE 是 Server 主动推送场景的轻量选择
```

### 4.4 SMS / 邮件

```
SMS 短信：
  - 兜底通道
  - 到达率 99%（运营商保证）
  - 成本高（0.05 元/条）
  - 限速（每秒 1000 条）

邮件：
  - 营销 / 报表
  - 异步发送
  - 退信 / 垃圾邮件处理
```

## 5. 推送流程

### 5.1 单用户推送

```
业务调用：push(user_id, content)
  1. 查用户设备 (device_id, channel, token)
  2. 在线状态判断
     - 在线：WebSocket 推送
     - 离线：APNs/FCM 推送
  3. 调用对应通道
  4. 失败重试（指数退避）
  5. 落库审计
```

### 5.2 群发推送

```
场景：全量 1000 万用户推送活动

步骤：
  1. 业务提交推送任务
  2. 任务入库（status=pending）
  3. 任务分发到多个 worker
  4. worker 批量拉取用户（分页）
  5. 每批 1000 用户 → MQ
  6. 多个推送 consumer 消费
  7. 统计到达率
  8. 任务完成

限速：
  - APNs: 1000 QPS
  - FCM: 1000 QPS
  - 厂商通道：各 200 QPS
  - 总推送：5000-10000 QPS
```

## 6. 关键技术

### 6.1 设备管理

```
数据模型：
  user_devices (
    user_id       BIGINT,
    device_id     VARCHAR,
    platform      ENUM('ios','android','web'),
    push_token    VARCHAR,
    app_version   VARCHAR,
    os_version    VARCHAR,
    is_active     TINYINT,
    last_active_at DATETIME,
    PRIMARY KEY (user_id, device_id)
  )

📌 一个用户多设备
   推送要发给所有 active 设备
```

### 6.2 在线状态

```
维护方式：
  1. WebSocket 连接时建立会话
     - session_id, user_id, device_id
     - Redis Hash: online:{user_id} → {device_id: session_id}

  2. 心跳维持
     - 客户端每 30s ping
     - 服务端续期 session

  3. 离线判定
     - 90s 没心跳 → 标记离线
     - 关闭连接

查询：
  HGETALL online:{user_id}   # 拿到所有在线设备
```

### 6.3 消息存储

```
消息表：
  push_messages (
    msg_id        BIGINT PK,
    user_id       BIGINT,
    channel       VARCHAR,
    content       TEXT,
    status        ENUM('pending','sent','failed'),
    retry_count   INT,
    sent_at       DATETIME,
    created_at    DATETIME,
    INDEX(user_id, status),
    INDEX(sent_at)
  )

离线消息：
  - 用户上线时拉取最近 N 条
  - 标记为已读
```

### 6.4 幂等与去重

```
问题：
  - APNs 不可靠，可能重复
  - 客户端网络抖动重试
  - 重复推送导致用户体验差

方案：
  1. msg_id 全局唯一
  2. 客户端记录最近 N 个 msg_id
  3. 收到消息时去重
  4. 业务层幂等（订单状态推进）
```

## 7. 推送中心设计

### 7.1 系统组件

```
                ┌────────────────┐
                │  推送中心     │
                ├────────────────┤
                │ 1. 任务调度   │ ← 定时推送 / 触发推送
                │ 2. 通道选择   │ ← 在线/离线/兜底
                │ 3. 限流       │ ← 用户级 / 全局级
                │ 4. 模板管理   │ ← 营销文案
                │ 5. 审计日志   │ ← 推送结果
                └────────┬───────┘
                         ↓
                ┌────────────────┐
                │ 消息队列      │
                │ Kafka/RocketMQ│
                └────────┬───────┘
                         ↓
                ┌────────────────┐
                │ 通道适配器    │
                │ APNs/FCM/...  │
                └────────────────┘
```

### 7.2 通道选择策略

```
用户设备：
  ┌──────────────────┐
  │  iOS + 在线      │ → WebSocket（实时）
  │  iOS + 离线      │ → APNs（系统通道）
  │  Android + 在线  │ → WebSocket
  │  Android + 离线  │ → FCM / 厂商通道
  │  Web + 在线      │ → WebSocket
  │  全部失败         │ → SMS 兜底
  └──────────────────┘

规则引擎：
  - 营销：用户设置免打扰时间 → 跳过
  - 紧急：绕过所有限制
  - 验证码：SMS 优先
```

### 7.3 限流

```
用户级限流：
  - 同一用户 1 小时最多 5 条
  - 营销类：1 天最多 3 条
  - Redis 滑动窗口

全局限流：
  - APNs 1000 QPS
  - FCM 5000 QPS
  - 令牌桶
```

## 8. 可靠性设计

### 8.1 推送重试

```
重试策略：
  1. 指数退避：1s, 2s, 4s, 8s, 16s
  2. 最大重试 3 次
  3. 失败原因分类
     - token 失效 → 标记设备无效
     - 通道限流 → 切换通道
     - 网络超时 → 重试
  4. 死信队列：最终失败入死信，人工处理
```

### 8.2 消息不丢

```
生产端：
  - MQ 持久化（Kafka acks=all）
  - 业务事务：业务 + MQ 一起成功

消费端：
  - 手动 ack
  - 处理成功才 ack
  - 处理失败重试

推送端：
  - 至少一次语义
  - 客户端幂等
  - msg_id 去重
```

### 8.3 监控告警

```
关键指标：
  - 推送总量 / 到达率
  - 各通道成功率
  - 推送延迟 P50 / P99
  - 失败原因分布
  - 设备在线数

告警：
  - 到达率 < 95% → 告警
  - APNs 错误率 > 5% → 告警
  - MQ 积压 > 10万 → 告警
```

## 9. 高级话题

### 9.1 推送合并

```
场景：用户有 100 条未读消息
方案：
  - 客户端聚合：本地 5 条合并成 "您有 100 条新消息"
  - 服务端合并：推送前聚合（按业务类型）
  - iOS thread-id：合并成同组通知
```

### 9.2 推送 + IM 融合

```
IM 消息也要走推送：
  - 在线用户：WebSocket 实时送达
  - 离线用户：APNs/FCM 推送
  - 推送携带 msg_id + 业务字段
  - 客户端收到推送后：
    - 在前台：直接处理
    - 在后台：标记未读，等用户点开
```

### 9.3 厂商通道对接

```
国内 Android 推送：
  - 华为 HMS Core
  - 小米 Mi Push
  - OPPO Push
  - vivo Push
  - 魅族 Push
  - 各家 API 不同
  - 需要适配层

📌 推送平台抽象：
  - 统一接口 PushProvider
  - 各厂商实现
  - 动态选择最优通道
```

## 10. 经典面试题

### 10.1 设计推送系统

```
Q：设计 1000 万 DAU 的推送系统
A：
  1. 推送中心 + MQ + 多通道适配
  2. 设备管理（user_devices 表）
  3. 在线状态（Redis Hash）
  4. 消息不丢（持久化 + 重试 + 幂等）
  5. 限流（用户级 + 全局级）
  6. 监控（到达率 / 延迟 / 失败率）

追问：怎么保证到达率？
  - 多通道兜底（APNs → FCM → SMS）
  - 离线消息入库
  - 上线时拉取
  - 失败重试 + 死信

追问：怎么限流不打扰用户？
  - 用户设置免打扰
  - 营销类合并
  - 智能时间段（8:00-22:00 营销）
  - VIP 用户优先
```

### 10.2 实时消息延迟

```
Q：1000 万在线，消息延迟 3 秒
A：
  1. WebSocket 长连接
  2. 连接分片（按 user_id 哈希）
  3. 单机 10万连接（epoll）
  4. 100 台机器 = 1000万连接
  5. 消息按 user_id 路由到对应机器
  6. 推送延迟 P99 < 1s

追问：怎么水平扩展？
  - 一致性哈希分片
  - 用户迁移工具
  - 双写过渡期
```

## 11. 一句话总结

```
📌 推送 = 通道适配 + 消息队列 + 设备管理 + 限流
📌 通道：iOS(APNs) / Android(FCM+厂商) / Web(WebSocket) / SMS兜底
📌 实时：WebSocket 长连接，心跳 30s，离线判定 90s
📌 可靠：MQ 持久化 + 至少一次 + 客户端幂等
📌 限流：用户级（防打扰）+ 全局级（通道限速）
📌 群发：任务分发 + 批量推送 + 限速 + 审计
📌 监控：到达率 / 延迟 / 失败率，三大核心指标
📌 厂商通道：国内必须适配 HMS/小米/OPPO/vivo
```

## 12. 参考资料

- Apple APNs 官方文档
- Google FCM 官方文档
- 国内厂商推送文档（HMS / Mi Push / OPPO / vivo）
- Kafka 消息可靠性
- WebSocket 协议 (RFC 6455)
- 系统设计面试 (Alex Xu, 2020)
- 推送平台架构演进（极客时间）


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

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [architecture](https://java-px.bot.cd/architecture/):企业架构
- [java](https://java-px.bot.cd/java-web-manual/):Java 实现
- [kafka](https://java-px.bot.cd/kafka/):消息
