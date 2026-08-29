---
title: Strangler Fig 绞杀者模式
date: 2026-08-15  # date-auto-injected
description: 渐进式迁移 monolith + API Gateway 流量切换 + Netflix / Amazon / 蚂蚁金服
---

# Strangler Fig 绞杀者模式

## 核心问题

Monolith 系统（巨石应用）有以下问题：
- 代码复杂（百万行级）
- 部署困难（一次部署影响全局）
- 技术栈僵化（无法引入新语言 / 新框架）
- 团队规模大（沟通成本指数增长）
- 故障影响范围广（一个 bug 可能挂全部）

但**完全重写**风险极高：
- 业务不能中断（在线服务 24/7）
- 重写通常需要 1-2 年（业务早已变化）
- 工程师流失（写新系统的人走了）
- 数据迁移风险（旧数据格式可能丢失）

## 核心思想

**逐步**用新服务**包裹**旧系统，逐步把流量从旧系统迁移到新服务。最终旧系统只剩壳子，被「绞杀」。

**类比自然界**：绞杀榕（Strangler Fig）从种子长成树，根系包裹宿主树，最终宿主被绞死。

## 三阶段迁移

```text
阶段 1：共存（0-3 月）
┌──────────────────────────┐
│      Monolith (旧)        │
│   ┌──────────────────┐   │
│   │  Business Logic  │   │    ┌──────────────────┐
│   │                  │   │    │   新服务 A        │
│   └──────────────────┘   │    │  (新功能独立)    │
│                          │    └──────────────────┘
└──────────────────────────┘
              ▲
              │
         API Gateway
         (分发路由)


阶段 2：迁移（3-18 月）
┌──────────────────────────┐
│      Monolith (旧)        │
│   ┌──────────────────┐   │    ┌──────────────────┐
│   │  部分业务 (迁移中) │   │    │   新服务 A        │
│   └──────────────────┘   │    │  (已迁移)        │
│   ┌──────────────────┐   │    ├──────────────────┤
│   │  剩余业务 (未迁移) │   │    │   新服务 B        │
│   └──────────────────┘   │    │  (迁移中)        │
└──────────────────────────┘    ├──────────────────┤
              ▲                │   新服务 C        │
              │                │  (新功能独立)    │
         API Gateway           └──────────────────┘
         (灰度分流)


阶段 3：绞杀（18-24 月）
┌──────────────────────────┐
│      Monolith (空壳)      │    ┌──────────────────┐
│   ┌──────────────────┐   │    │   新服务 A        │
│   │   几乎无业务     │   │    ├──────────────────┤
│   └──────────────────┘   │    │   新服务 B        │
└──────────────────────────┘    ├──────────────────┤
              ▲                │   新服务 C        │
              │                ├──────────────────┤
         API Gateway           │   新服务 D        │
         (全部新服务)           └──────────────────┘

→ 最终下线 Monolith
```

## API Gateway 流量切换

```nginx
# Nginx：10% 流量切到新服务
upstream old_service {
    server old.internal:8080;
}

upstream new_service {
    server new.internal:8080;
}

server {
    location /api/users {
        # 灰度策略：基于 cookie / header / 比例
        set $backend old_service;
        if ($http_x_canary = "true") {        # 1. 内部员工全量
            set $backend new_service;
        }
        if ($cookie_user_group = "beta") {    # 2. Beta 用户
            set $backend new_service;
        }
        # 3. 10% 随机抽样
        set $rand $request_id;
        if ($rand ~ "^.{0}$") {
            set $backend new_service;
        }
        proxy_pass http://$backend;
    }
}
```

## Spring Cloud Gateway

```java
@Bean
public RouteLocator routes(RouteLocatorBuilder builder) {
    return builder.routes()
        .route("user-service", r -> r.path("/api/users/**")
            .uri("lb://user-service-new"))  // 全部走新服务
        .route("order-service", r -> r.path("/api/orders/**")
            .uri("lb://order-service"))  // 还在旧服务
        .build();
}

// 灰度
@Bean
public RouteLocator grayRoutes(RouteLocatorBuilder builder) {
    return builder.routes()
        .route("order-gray", r -> r.path("/api/orders/**")
            .and().header("X-Canary", "true")
            .uri("lb://order-service-new"))
        .route("order-main", r -> r.path("/api/orders/**")
            .uri("lb://order-service-old"))
        .build();
}
```

## 实战案例

## Netflix

Netflix 是 Strangler Fig 的典范：
- 2008 年：单块 DVD 租赁系统
- 2009-2015：迁移到 AWS 微服务（500+ 服务）
- 迁移用了 7 年，期间业务持续运营

关键经验：
- **不要停机**：每天 1.5 亿次 API 调用不能断
- **逐步迁移**：每次迁移 1-2 个服务，灰度切换
- **数据迁移**：双写 + 后台校验 + 最终一致

## Amazon

- 2002 年开始从 monolith 拆出 SOA
- 2010 年代完成（用了 8+ 年）
- 关键经验：CEO Jeff Bezos 强制要求**所有团队必须通过 API 通信**

## 京东

- 2014 年开始订单系统迁移
- 迁移期间经历多次 618 / 双 11 大促
- 关键经验：**先迁移非核心业务（评论 / 收藏），最后迁移核心（下单 / 支付）**

## 蚂蚁金服

- 2014 年开始从 IOE（IBM / Oracle / EMC）迁移到 SOFA
- 用了 5+ 年完成
- 关键经验：**单元化架构**（按用户 ID 拆分，独立单元独立部署）

## 迁移策略选择

## 数据迁移

### 双写 + 后台校验

```java
@Service
public class UserService {
    @Autowired private OldUserRepo oldRepo;
    @Autowired private NewUserRepo newRepo;

    @Transactional
    public void update(User user) {
        oldRepo.save(user);  // 写旧库
        // 异步双写新库
        CompletableFuture.runAsync(() -> newRepo.save(user));

        // 后台校验：定期比对旧库 vs 新库
        // 发现不一致 → 修复 + 告警
    }
}

// 验证脚本（每日跑）
@Scheduled(cron = "0 2 * * *")  // 凌晨 2 点
public void verify() {
    List<User> oldUsers = oldRepo.findAll();
    for (User old : oldUsers) {
        User newUser = newRepo.findById(old.getId()).orElseThrow();
        if (!old.equals(newUser)) {
            alertService.report(old, newUser);
        }
    }
}
```

## 流量切换

| 阶段 | 比例 | 时长 |
|---|---|---|
| 内部员工 | 100% | 1 周 |
| Beta 用户 | 10% | 2 周 |
| 灰度 | 10% → 50% | 2-4 周 |
| 全量 | 100% | — |

每一步都有**回滚预案**（出问题立即切回旧服务）。

## 适用边界

✅ **使用场景**：
- 业务不能中断（在线服务）
- 代码历史包袱重（无法重写）
- 团队分批交付（新功能要上线）
- 业务复杂度高（重写风险大）

❌ **避免场景**：
- 业务极简（直接重写）
- 流量太小（不值得拆分）
- 没有 API Gateway 基础设施
- 团队无微服务经验

🔄 **替代方案**：
- **完全重写**：业务简单 / 团队有能力
- **Carving**：直接从 monolith 抽模块
- **Modular Monolith**：不拆分，先模块化

💡 **最佳实践**：
- API Gateway 是关键基础设施
- 数据迁移用双写 + 校验
- 每个迁移步骤都有回滚预案
- 监控新旧两套系统的指标差异
- 优先迁移非核心业务，最后迁移核心

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [java-language](https://java-px.bot.cd/java-language/):Java 设计模式
- [java](https://java-px.bot.cd/java-web-manual/):Java 实现
- [architecture](https://java-px.bot.cd/architecture/):架构模式
