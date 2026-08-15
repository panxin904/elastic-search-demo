---
title: Kibana 可视化
description: Elastic Stack 的可视化层
---

# Kibana 可视化

> **TL;DR**：Kibana = **Elastic Stack 的可视化 + 分析层**。**数据源：Elasticsearch**。**核心功能：Discover（查询日志）+ Visualize（图表）+ Dashboard（综合看板）+ Lens（拖拽可视化）+ Alerting（告警）**。**Kibana 8+ 把 ELK 栈简化为单一 UI：日志 + 指标 + APM + 可观测性都在一个 Kibana**。

## 一句话定义

```
Kibana = Elastic Stack 的 UI 层
      = 数据源：Elasticsearch（也可连 Prometheus/Beats）
      = 核心功能：Discover / Dashboard / Lens / Alerting / Canvas
      = Kibana 8.0+ 把可观测性（Logs / Metrics / APM / Uptime）整合到一个 UI
```

## 架构总览

```
┌──────────────┐
│ Filebeat     │──┐
│ Metricbeat   │  │
│ Logstash     │──┼──▶ Elasticsearch ──▶ Kibana ──▶ 用户
│ APM Server   │  │   (存储 + 索引)    (可视化)
│ Heartbeat    │──┘
└──────────────┘
```

## 核心功能

### 1. Discover（日志发现）

```
功能：
  - 选择 index pattern（*logs*, *metrics*）
  - KQL / Lucene 查询语法
  - 时间范围选择
  - 字段过滤 + 直方图

KQL 示例：
  status:500 AND service:"order-api"
  http.response.status_code:[500 TO 599]
  @timestamp >= "2026-08-09" AND message: "exception"

操作：
  - 加 column 显示
  - 保存查询 → 复用
  - 导出 CSV
```

### 2. Visualize（可视化）

```
可视化类型：
  - Lens（拖拽式，推荐）
  - TSVB（Time Series Visual Builder）
  - Aggregation Based（柱图/饼图/折线/数据表）
  - Maps（地理）
  - Vega（自定义可视化）

Lens 示例：每分钟错误数
  1. 选 index pattern: logs-*
  2. Horizontal axis: @timestamp (date_histogram, 1m)
  3. Vertical axis: count of records
  4. Filter: level:error
  5. Save
```

### 3. Dashboard（看板）

```
多个可视化 + 控件组合：
  - 顶部：KPI（数字 + 趋势）
  - 中部：时间序列（QPS / 延迟 / 错误率）
  - 下部：日志表格（最近错误）
  - 左侧：过滤器（dropdown）

最佳实践：
  - 一个服务一个 dashboard
  - 用 input controls 做联动（选择 service → 所有 panel 联动）
  - 设 drilldown（点 panel → 跳到 trace）
```

### 4. Lens（拖拽可视化）

```
Kibana 7.6+ 主推，Kibana 8+ 默认
特点：
  - 拖拽字段到画布
  - 自动建议图表类型
  - 支持 formula（Druid-like 表达式）

Lens 公式示例：
  count() / overall_count() * 100   # 错误率百分比
  percentile(http.response.body.bytes, 95)
  derivative(count())  # 增长率
```

### 5. APM（应用性能监控）

```
Kibana 内置 APM：
  - 自动发现服务的 trace
  - 服务地图（依赖图）
  - Service / Endpoint / Trace 三层 drilldown
  - 错误率 / 延迟 / 吞吐量三件套

部署：
  1. APM Server（独立进程）
  2. Elasticsearch（APM 索引）
  3. Kibana（APM UI）
  4. App 集成 APM Agent（Java/Node.js/Python/Go/Ruby/.NET）

Java Agent 启动：
  java -javaagent:./elastic-apm-agent.jar \
       -Delastic.apm.service_name=order-service \
       -Delastic.apm.server_url=http://apm-server:8200 \
       -jar order-service.jar
```

### 6. Alerting（告警）

```
Kibana 8+ 内置告警引擎：
  - 规则类型：Elasticsearch query / index threshold / APM / Uptime / ML
  - 触发器：Action（Slack / Email / Webhook / PagerDuty）
  - 定时检查（每分钟）

实战：订单 API 5xx 错误率告警
  Rule type: APM
  Service: order-service
  Transaction type: request
  Filter: transaction.result: "HTTP 5xx"
  Threshold: count > 10 in 5min
  Action: Slack #ops-alerts
```

## Index Pattern 与字段映射

```yaml
# Filebeat 配置 → 自动创建 index template
filebeat.inputs:
  - type: log
    paths: [/var/log/app/*.log]
    fields:
      service: order-service
      env: prod
    fields_under_root: true

filebeat.config.modules:
  path: ${path.config}/modules.d/*.yml
  reload.enabled: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "app-logs-%{+yyyy.MM.dd}"

# Kibana → Stack Management → Index Patterns
# 创建 pattern: app-logs-* → 选择 @timestamp
# 自动发现的字段：service (keyword), env (keyword), message (text)
```

## Index Lifecycle Management（ILM）

```yaml
# Elasticsearch ILM 策略：日志 7 天 → warm → 30 天 → cold → 365 天 → delete
PUT _ilm/policy/logs-policy
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {
            "max_size": "50gb",
            "max_age": "1d"
          },
          "set_priority": {"priority": 100}
        }
      },
      "warm": {
        "min_age": "7d",
        "actions": {
          "shrink": {"number_of_shards": 1},
          "forcemerge": {"max_num_segments": 1},
          "set_priority": {"priority": 50}
        }
      },
      "cold": {
        "min_age": "30d",
        "actions": {
          "freeze": {},
          "set_priority": {"priority": 0}
        }
      },
      "delete": {
        "min_age": "365d",
        "actions": {"delete": {}}
      }
    }
  }
}
```

## 实战案例：电商 ELK + APM 全链路

```
架构：
  App → Filebeat → Elasticsearch → Kibana（Discover/Dashboard/APM）

Filebeat 模块：
  - system（CPU/内存/磁盘）
  - nginx（access log）
  - elasticsearch（ES 日志）
  - 应用 log（自定义）

Kibana 看板：
  1. 顶部 KPI：今日 GMV / 订单数 / 错误率
  2. 中部时序：QPS / P99 / 5xx 错误率（来自 APM）
  3. 下部日志：错误日志表（来自 Discover，filter level:error）
  4. APM：服务地图 + 慢 trace 列表
  5. 联动：点 error log → 跳到对应 trace → 看 span 详情
```

## Kibana vs Grafana

| 维度 | Kibana | Grafana |
|---|---|---|
| 出品 | Elastic | Grafana Labs |
| 数据源 | Elasticsearch（首选） | 30+（Prometheus/Loki/ES/InfluxDB） |
| 强项 | 日志分析 + APM（原生） | 多数据源 + 看板灵活 |
| 弱项 | 数据源相对单一 | 无内建 APM（需 Tempo/Jaeger） |
| 商业化 | Elastic Stack（部分功能收费） | OSS 完全免费 |
| 适用 | 已有 ES / 用 Elastic APM | 多数据源 / 已有 Prometheus |

## 一句话总结

> **Kibana = Elastic Stack 可视化层**。**Kibana 8+ = Logs + Metrics + APM + Uptime 四合一 UI**。**Lens 是可视化首选**。**最佳搭配：Filebeat → Elasticsearch → Kibana + ILM（自动冷热分层）**。**已有 ES 选 Kibana，多数据源选 Grafana**。

---

## 关联章节

- [ELK 日志存储](./elasticsearch-logs.md) — Elasticsearch 配置 + ILM
- [Fluentd](./fluentd.md) — 日志采集替代 Filebeat
- [Grafana Dashboard](../04-grafana/dashboard.md) — Kibana vs Grafana 选型
- [K8s 监控](../11-scenarios/k8s-monitor.md) — 容器日志采集

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>