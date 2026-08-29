---
title: 业务指标设计
date: 2026-08-15  # date-auto-injected
description: DAU / 转化率 / 漏斗 / 业务 SLO
---

# 业务指标设计

> **TL;DR**：**业务指标 ≠ 技术指标**。**技术指标（RED/USE）回答"服务健康吗"，业务指标回答"用户在做什么"**。**核心：DAU / 转化率 / 漏斗 / GMV / 留存 / NPS**。**业务指标的告警阈值往往比技术指标更关键**：**凌晨 1 点订单下降 50% 立即叫醒 CEO**，**比 CPU 100% 更紧急**。

## 一句话定义

```
业务指标 = 衡量产品/业务健康度的量化数字
       = 用户行为（DAU/留存/转化）+ 商业结果（GMV/ARPU/ROI）
       = 必须可埋点 + 可聚合 + 可告警
       = 不同于技术指标（CPU/QPS/延迟），但同样需要 SLO
```

## 业务指标分类

### 1. 用户指标

```yaml
DAU (Daily Active Users):
  定义: 24 小时内有有效操作的去重用户数
  PromQL: |
    count(
      distinct(user_id) by (user_id)
      and on(user_id) (rate(user_events_total[1d]) > 0)
    )
  应用: 健康度基线 / 周同比 / 月同比

MAU (Monthly Active Users):
  定义: 30 天内活跃用户数
  应用: 估值 / 长期趋势

留存 (Retention):
  定义: 第 N 天回到产品的用户比例
  SQL: |
    SELECT cohort, day_n,
      COUNT(DISTINCT user_id) * 1.0 / cohort_size AS retention
    FROM user_activity
    GROUP BY cohort, day_n

DAU/MAU (Stickiness):
  定义: DAU / MAU，衡量产品粘性
  健康值: > 20% 是高粘性，< 10% 是低粘性
```

### 2. 转化指标

```yaml
注册转化率:
  定义: 访问 → 注册 比例
  PromQL: |
    sum(rate(user_registered_total[1h]))
    / sum(rate(user_visited_signup_page_total[1h]))

下单转化率:
  定义: 浏览 → 下单 比例
  PromQL: |
    sum(rate(orders_succeeded_total[1h]))
    / sum(rate(product_page_views_total[1h]))

支付转化率:
  定义: 下单 → 支付成功 比例
  PromQL: |
    sum(rate(payments_succeeded_total[1h]))
    / sum(rate(orders_succeeded_total[1h]))
```

### 3. 漏斗（Funnel）

```yaml
电商下单漏斗:
  步骤:
    1. 浏览商品:   product_page_views
    2. 加入购物车: cart_items_added
    3. 进入结算:   checkout_started
    4. 下单成功:   orders_succeeded
    5. 支付成功:   payments_succeeded

  健康转化率参考:
    1→2: 8-15%
    2→3: 50-70%
    3→4: 60-80%
    4→5: 90-95%（支付环节流失最大）

  PromQL 实现:
  sum(rate(cart_items_added_total[1h]))
  / sum(rate(product_page_views_total[1h]))
```

### 4. 商业指标

```yaml
GMV (Gross Merchandise Volume):
  定义: 平台总成交额（含未支付）
  PromQL: |
    sum(increase(orders_amount_total[1d]))

  实战: 按品类 / 商家 / 地区切片
  sum by (category) (increase(orders_amount_total[1d]))

ARPU (Average Revenue Per User):
  定义: 每用户平均收入
  SQL: |
    SELECT SUM(amount) / COUNT(DISTINCT user_id)
    FROM orders
    WHERE created_at > NOW() - INTERVAL '30 days'

ROI (Return On Investment):
  定义: (收益 - 成本) / 成本
  应用: 营销活动效果评估
```

### 5. 用户体验指标

```yaml
NPS (Net Promoter Score):
  定义: 推荐者比例 - 贬损者比例
  范围: -100 到 +100
  健康: > 30 是好，> 50 是极好

页面加载时间（P75）：
  定义: 75 分位首屏加载时间
  阈值: < 1.5s（移动）/ < 1s（PC）

搜索成功率：
  定义: 搜索 → 点击 ≥ 1 个结果 比例
  PromQL: |
    sum(rate(search_with_click_total[1h]))
    / sum(rate(search_total[1h]))

崩溃率（Crash Rate）：
  定义: 崩溃会话 / 总会话
  阈值: < 0.1%（移动端 < 0.5%）
```

## 业务指标埋点设计

### 1. 事件命名规范

```yaml
# 命名约定：{domain}_{object}_{action}
事件示例:
  - user_register_succeeded        # 用户注册成功
  - order_payment_failed            # 订单支付失败
  - cart_item_added                 # 加入购物车
  - page_viewed                     # 页面浏览
  - search_submitted                # 搜索提交

标签设计:
  通用标签:
    - env: prod/staging
    - app_version: 2.3.0
    - platform: ios/android/web
    - user_segment: new/existing/vip
  业务标签:
    - category: electronics/clothing
    - channel: organic/paid/referral
```

### 2. 上报格式（JSON 示例）

```json
{
  "event_name": "order_payment_succeeded",
  "timestamp": "2026-08-09T14:23:45Z",
  "user_id": "12345",
  "session_id": "abc-def-ghi",
  "properties": {
    "order_id": "ORD-20260809-001",
    "amount": 199.00,
    "currency": "CNY",
    "payment_channel": "alipay",
    "category": "electronics"
  },
  "context": {
    "app_version": "2.3.0",
    "platform": "ios",
    "device_model": "iPhone 14",
    "os_version": "16.5",
    "network_type": "wifi"
  }
}
```

## 业务告警配置

```yaml
# Prometheus alert rules（业务）
groups:
  - name: business-slos
    rules:
      # 订单同比下降 30%
      - alert: OrderDrop
        expr: |
          sum(increase(orders_succeeded_total[1h]))
          <
          sum(increase(orders_succeeded_total[1h] offset 1d)) * 0.7
        for: 15m
        labels:
          severity: critical
          team: payments
        annotations:
          summary: "订单量同比昨日下降 30%"
          action: "立刻检查支付通道 + 推荐服务 + 营销活动是否异常"

      # 下单转化率下降
      - alert: CheckoutConversionDrop
        expr: |
          sum(rate(orders_succeeded_total[5m]))
          / sum(rate(product_page_views_total[5m]))
          < 0.05  # 健康值 8%，低于 5% 触发
        for: 10m
        labels:
          severity: warning

      # 支付失败率 spike
      - alert: PaymentFailureRateSpike
        expr: |
          sum(rate(payment_failed_total[5m]))
          / sum(rate(payment_attempted_total[5m]))
          > 0.1  # 失败率 > 10%
        for: 5m
        labels:
          severity: critical

      # 搜索无结果率
      - alert: SearchNoResultRate
        expr: |
          sum(rate(search_no_results_total[10m]))
          / sum(rate(search_total[10m]))
          > 0.3  # 30% 搜索无结果（可能是索引挂了）
        for: 5m
        labels:
          severity: warning
```

## 实战案例：电商核心业务看板

```yaml
# Grafana Dashboard 核心 panels
panels:
  - title: GMV (实时)
    type: stat
    targets:
      - expr: sum(increase(orders_amount_total[1h]))

  - title: 订单数 (同比)
    type: timeseries
    targets:
      - expr: sum(rate(orders_succeeded_total[1h]))
      - expr: sum(rate(orders_succeeded_total[1h] offset 1d))
        legendFormat: 昨日同时段

  - title: 转化漏斗
    type: bar gauge
    targets:
      - expr: sum(rate(product_page_views_total[1h])) / sum(rate(product_page_views_total[1h]))
      - expr: sum(rate(cart_items_added_total[1h])) / sum(rate(product_page_views_total[1h]))
      - expr: sum(rate(orders_succeeded_total[1h])) / sum(rate(product_page_views_total[1h]))
      - expr: sum(rate(payments_succeeded_total[1h])) / sum(rate(product_page_views_total[1h]))

  - title: 用户分布
    type: pie
    targets:
      - expr: sum by (user_segment) (count_over_time(user_active[24h]))

  - title: Top 异常商品
    type: table
    targets:
      - expr: topk(10, sum by (product_id) (rate(out_of_stock_events_total[1h])))
```

## 业务指标 vs 技术指标优先级

```
1. 业务指标是 SRE 告警的最高优先级
   例：凌晨 2 点订单下降 80%（业务告警）→ 立刻 P0 升级
       凌晨 2 点 CPU 90%（技术告警）→ 可延后到工作时间

2. 业务告警往往指向严重问题
   - 订单下降 → 可能是数据库挂了 / 支付通道挂了 / CDN 挂了 / 推荐服务挂了
   - 注册下降 → 可能是验证码服务挂了 / 注册 API 异常

3. 业务指标 → 技术指标的因果链
   业务: 订单下降 50% (P0)
     ↓ 排查
   RED: 订单 API 5xx 错误率 30% (P1)
     ↓ 排查
   USE: Redis 连接池耗尽 (P2)
     ↓ 排查
   Log: Redis Cluster 某节点 OOM (P3)
```

## 一句话总结

> **业务指标 = 用户行为 + 商业结果**。**核心：DAU / 转化 / 漏斗 / GMV / 留存**。**业务告警优先级 > 技术告警**。**埋点规范：{domain}_{object}_{action}**。**所有产品改动必须先想清楚埋点 + SLO**。

---

## 关联章节

- [RED 方法](./red-method.md) — 服务级技术指标
- [USE 方法](./use-method.md) — 资源级技术指标
- [SLI/SLO](../01-foundations/sli-slo.md) — 业务指标的 SLO 设计
- [Prometheus 告警](../03-prometheus/alert.md) — 业务告警规则

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

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

- [devops](https://java-px.bot.cd/devops/):DevOps 监控
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 监控
- [kafka](https://java-px.bot.cd/kafka/):日志收集
