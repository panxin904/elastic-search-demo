---
title: Grafana 变量
description: Variables / Templating / Dropdown
---

# Grafana 变量

> **TL;DR**：**Grafana Variables = Dashboard 上的下拉筛选器**。**联动所有 panel 的查询**。**核心类型：Query（数据源查询）/ Custom（静态列表）/ Datasource（数据源切换）/ Interval（时间步长）**。**最佳实践：用 variables 做多服务 / 多环境 / 多 region 的统一看板**。

## 一句话定义

```
Variable（变量）= Dashboard 上的交互式参数
              = 在 dashboard 顶部显示为下拉框
              = 联动所有 panel 的查询
              = 模板化 dashboard 的关键
```

## 变量类型

| 类型 | 数据来源 | 典型用途 |
|---|---|---|
| Query | 数据源查询 | 服务列表、环境列表 |
| Custom | 静态自定义 | 固定选项（如 P0/P1/P2） |
| Datasource | 数据源切换 | 多 Prometheus 实例 |
| Interval | 时间步长 | rate / histogram bucket |
| Text box | 自由输入 | 临时查询 |
| Constant | 常量 | 业务常量 |
| Hidden | 隐藏变量 | URL 传参 |

## Query 变量（最常用）

```yaml
# 1. 从 Prometheus 查询所有服务名
type: query
name: service
label: 服务
query: label_values(http_requests_total, service)

# 2. 多选
multi: true
include_all: true   # 自动加 "All" 选项

# 3. 依赖其他变量
type: query
name: instance
query: label_values(http_requests_total{service="$service"}, instance)

# 4. 正则过滤
regex: /.*-prod/
```

## 在 Panel 中使用变量

```promql
# 1. 直接插值
sum(rate(http_requests_total{service="$service"}[5m]))

# 2. 多选变量 → 用 =~
service=~"$service"   # 选多个 → service=~"a|b|c"

# 3. 用 ${var} 还是 $var
# 推荐 ${var}（更明确，避免与字符混淆）

# 4. 变量默认转义
# 文本变量自动 quote，label 变量自动处理
```

## 实战案例：多服务 SLO 看板

```yaml
# 变量配置
variables:
  - name: service
    type: query
    query: label_values(http_requests_total, service)
    multi: true
    include_all: true
    default: "All"

  - name: env
    type: custom
    options:
      - prod
      - staging
      - dev
    default: prod

  - name: percentile
    type: custom
    options:
      - { text: "P50", value: "0.5" }
      - { text: "P95", value: "0.95" }
      - { text: "P99", value: "0.99" }
    default: P95

  - name: interval
    type: interval
    options:
      - 1m
      - 5m
      - 15m
    default: 5m

# Panel 查询
panels:
  - title: ${service} ${env} Rate
    targets:
      - expr: sum(rate(http_requests_total{service=~"$service", env="$env"}[$interval]))

  - title: ${service} ${env} P${percentile}
    targets:
      - expr: |
        histogram_quantile($percentile,
          sum by (le) (rate(http_request_duration_seconds_bucket{service=~"$service", env="$env"}[$interval]))
        )
```

## 嵌套变量

```yaml
# 复杂场景：选择 region → 选择 service → 选择 instance
variables:
  - name: region
    type: custom
    options: [cn-north, cn-east, us-west]

  - name: service
    type: query
    query: label_values(http_requests_total{region="$region"}, service)
    refresh: on_time_change  # 父变量变时自动 refresh

  - name: instance
    type: query
    query: label_values(http_requests_total{region="$region", service="$service"}, instance)
```

## URL 参数传变量

```
Dashboard URL 可带变量值：
  https://grafana/d/order-slo?var-service=order-api&var-env=prod&from=now-1h

应用：
  - 告警通知附 URL（直接定位到 dashboard）
  - 第三方系统集成（如 status page）
```

## 一句话总结

> **Variables = Dashboard 的下拉筛选器**。**Query 变量最常用**。**支持嵌套（service → instance）**。**一个 dashboard 服务所有服务所有环境**。

---

## 关联章节

- [Dashboard 设计](../04-grafana/dashboard.md)
- [Grafana 概览](../04-grafana/overview.md)
- [Grafana 告警](../04-grafana/alerting.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
