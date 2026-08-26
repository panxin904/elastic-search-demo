---
title: Grafana Dashboard 设计
description: 监控大盘设计原则与实战
---

# Grafana Dashboard 设计

> **TL;DR**：好的 Dashboard 是**3 秒看到问题**，坏的是**5 分钟找不到图**。设计原则：黄金信号 → RED/USE → 业务维度分层。**Dashboard 不是图表越多越好，而是"信息密度"越高越好**。

## 一句话定义

```
Grafana Dashboard = 把多个 metrics / logs / traces 面板组合到一页，解决某个具体场景的可观测性视图
```

## 三层 Dashboard 架构

### 第 1 层：Overview（总览）

**目标**：一眼看到全公司所有服务的健康状态。

```
面板组成（推荐 6-9 个）：
├─ 全部服务可用性（数字面板 / 99.9%）
├─ 全部服务 p99 延迟（趋势图）
├─ 全公司错误率（数字 + 趋势）
├─ 全公司 QPS（趋势图）
├─ 在线实例总数（数字 + 趋势）
├─ 告警触发次数（按级别分组）
└─ 服务状态矩阵（热力图，service × time）
```

**示例 JSON 片段**：

```json
{
  "panels": [
    {
      "title": "全公司可用性 (1h)",
      "type": "stat",
      "targets": [{
        "expr": "sum(rate(http_requests_total{status!~\"5..\"}[1h])) / sum(rate(http_requests_total[1h]))",
        "legendFormat": "可用性"
      }],
      "fieldConfig": {
        "defaults": {
          "unit": "percentunit",
          "thresholds": {
            "steps": [
              { "color": "red", "value": 0.99 },
              { "color": "yellow", "value": 0.995 },
              { "color": "green", "value": 0.999 }
            ]
          }
        }
      }
    },
    {
      "title": "全公司 p99 延迟",
      "type": "timeseries",
      "targets": [{
        "expr": "histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service))",
        "legendFormat": "{{service}}"
      }]
    }
  ]
}
```

### 第 2 层：Service Dashboard（服务详情）

**目标**：针对某个服务，看清所有维度的指标。

```
面板组成（推荐 12-20 个）：
├─ 服务基础信息（服务名、版本、实例数）
├─ 黄金信号 4 件套（Latency / Traffic / Errors / Saturation）
├─ RED 方法面板（Rate / Errors / Duration）
├─ 资源使用（CPU / 内存 / 网络 / 磁盘）
├─ 依赖服务调用（调用下游的延迟和错误率）
├─ JVM 详情（如 Java 服务：堆 / GC / 线程）
├─ 数据库连接池（活跃 / 等待）
├─ 关键业务指标（订单数 / 支付金额）
├─ 最近 24h 部署事件（Annotation）
└─ 关联日志（Loki 嵌入面板）
```

### 第 3 层：Incident Dashboard（故障专用）

**目标**：当告警触发时，5 分钟内定位。

```
面板组成（推荐 8-12 个）：
├─ 触发告警的指标（突增 / 突降）
├─ 最近 1h 部署 / 配置变更（Annotation）
├─ 受影响服务的 error log
├─ 受影响请求的 trace
├─ 上下游依赖状态
├─ 当前告警列表（Alertmanager 嵌入）
├─ 值班人员信息
└─ Runbook 链接（直接给出操作手册）
```

> **黄金法则**：Incident Dashboard 应该是**只读**的（不能编辑），且**预定义好查询**，避免故障时临时拼 PromQL。

## Dashboard 设计十大原则

### 1. 信息密度优先

```
❌ Dashboard 上 30 个面板，5 个有数据
✅ Dashboard 上 12 个面板，全部有数据，3 秒看完
```

### 2. 统一颜色规范

```yaml
# 推荐的语义化颜色
可用性:
  green: > 99.9%
  yellow: 99%-99.9%
  red: < 99%

延迟:
  green: < p99 SLO
  yellow: p99 SLO - p99 SLO * 1.5
  red: > p99 SLO * 1.5
```

### 3. 时间窗口一致

```
# ❌ 每个面板用不同时间窗口（5m / 15m / 1h），难以横向比较
# ✅ 顶部变量统一控制，所有面板默认 1h
```

```json
{
  "templating": {
    "list": [{
      "name": "interval",
      "type": "interval",
      "auto": true,
      "auto_count": 30,
      "auto_min": "10s"
    }]
  }
}
```

### 4. 关键指标放最上面

```
# 用户视线移动路径：左上 → 右上 → 左下 → 右下
# 关键指标（如可用性、错误数）放左上
```

### 5. 同类指标分屏

```
# RED 方法分一组
# USE 方法分一组
# 业务指标分一组
```

### 6. 避免数字瀑布

```
❌ "QPS: 1234 → 5678 → 9012 → ..." 多个面板
✅ 一个趋势图 + 当前值 stat
```

### 7. 链接跳转

```json
{
  "type": "table",
  "targets": [{
    "expr": "sum by (service) (rate(http_requests_total[5m]))"
  }],
  "fieldConfig": {
    "defaults": {
      "links": [{
        "title": "查看详情",
        "url": "/d/order-service?var-service=${__value.label}"
      }]
    }
  }
}
```

### 8. Annotation 必加

```yaml
# prometheus.yml
groups:
- name: annotations
  rules:
  - alert: HighErrorRate
    expr: ...
    annotations:
      summary: "错误率突增"
      description: "..."
```

**效果**：在趋势图上叠加告警 / 部署 / 配置变更事件，**指标突变立刻能关联到原因**。

### 9. 单位清晰

```json
{
  "fieldConfig": {
    "defaults": {
      "unit": "ms"     // 毫秒
    }
  }
}
```

**常用单位**：
- `s` / `ms` / `ns` ··· 时间
- `bytes` / `KB` / `MB` / `GB` ··· 字节
- `percent` / `percentunit` (0-1) ··· 百分比
- `reqps` ··· 每秒请求数
- `short` ··· 1.2k, 3.4M ··· 自动简写

### 10. 可导出为代码

```json
// ✅ Dashboard JSON 存 git 里，PR review
// ❌ 在 UI 上点来点去编辑
```

## 模板变量（Variables）

**作用**：让 Dashboard 可复用，通过下拉框切换维度。

```json
{
  "templating": {
    "list": [
      {
        "name": "service",
        "type": "query",
        "datasource": "Prometheus",
        "query": "label_values(http_requests_total, service)",
        "refresh": 1
      },
      {
        "name": "instance",
        "type": "query",
        "datasource": "Prometheus",
        "query": "label_values(http_requests_total{service=\"$service\"}, instance)"
      },
      {
        "name": "interval",
        "type": "interval",
        "auto": true,
        "auto_count": 30,
        "options": ["10s", "30s", "1m", "5m", "15m", "1h", "6h", "1d"]
      }
    ]
  }
}
```

**使用**：

```promql
# 在 PromQL 中引用变量
sum(rate(http_requests_total{service="$service", instance=~"$instance"}[$interval]))
```

## Panel 类型速览

| 类型 | 用途 | 典型场景 |
|---|---|---|
| **Time series** | 时序趋势图 | QPS、延迟、CPU |
| **Stat** | 当前值 + 阈值 | 可用性、错误数 |
| **Gauge** | 仪表盘 | CPU 使用率、队列占用 |
| **Bar gauge** | 横向条 | Top N 服务 |
| **Table** | 表格 | 实例列表、状态矩阵 |
| **Heatmap** | 热力图 | 延迟分布、调用密度 |
| **Logs** | 日志面板 | Loki 直接查日志 |
| **Trace** | trace 面板 | Tempo 直接查 trace |
| **Text** | 文本 | 注释、Runbook |

## 实战：Order Service Dashboard

```json
{
  "title": "Order Service · SRE Dashboard",
  "tags": ["order", "sre", "tier-1"],
  "timezone": "browser",
  "time": { "from": "now-1h", "to": "now" },
  "templating": {
    "list": [
      { "name": "service", "type": "query", "query": "label_values(http_requests_total, service)" }
    ]
  },
  "panels": [
    // Row 1 - 黄金信号
    {
      "title": "Availability",
      "type": "stat",
      "gridPos": { "x": 0, "y": 0, "w": 6, "h": 4 },
      "targets": [{
        "expr": "sum(rate(http_requests_total{status!~\"5..\", service=\"$service\"}[5m])) / sum(rate(http_requests_total{service=\"$service\"}[5m]))"
      }]
    },
    {
      "title": "p99 Latency",
      "type": "stat",
      "gridPos": { "x": 6, "y": 0, "w": 6, "h": 4 },
      "targets": [{
        "expr": "histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{service=\"$service\"}[5m])) by (le))",
        "legendFormat": "p99"
      }],
      "fieldConfig": {
        "defaults": { "unit": "ms" }
      }
    },
    {
      "title": "Error Rate",
      "type": "stat",
      "gridPos": { "x": 12, "y": 0, "w": 6, "h": 4 },
      "targets": [{
        "expr": "sum(rate(http_requests_total{status=~\"5..\", service=\"$service\"}[5m])) / sum(rate(http_requests_total{service=\"$service\"}[5m]))"
      }]
    },
    {
      "title": "QPS",
      "type": "stat",
      "gridPos": { "x": 18, "y": 0, "w": 6, "h": 4 },
      "targets": [{
        "expr": "sum(rate(http_requests_total{service=\"$service\"}[5m]))"
      }]
    },
    // Row 2 - 趋势
    {
      "title": "Latency Distribution (p50 / p95 / p99)",
      "type": "timeseries",
      "gridPos": { "x": 0, "y": 4, "w": 12, "h": 8 },
      "targets": [
        {
          "expr": "histogram_quantile(0.50, sum(rate(http_request_duration_seconds_bucket{service=\"$service\"}[5m])) by (le))",
          "legendFormat": "p50"
        },
        {
          "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{service=\"$service\"}[5m])) by (le))",
          "legendFormat": "p95"
        },
        {
          "expr": "histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{service=\"$service\"}[5m])) by (le))",
          "legendFormat": "p99"
        }
      ]
    },
    {
      "title": "Errors by Status Code",
      "type": "timeseries",
      "gridPos": { "x": 12, "y": 4, "w": 12, "h": 8 },
      "targets": [
        {
          "expr": "sum(rate(http_requests_total{status=~\"5..\", service=\"$service\"}[5m])) by (status)",
          "legendFormat": "{{status}}"
        }
      ]
    }
  ]
}
```

## 常见错误

### 错误 1：可视化类型选错

```
# ❌ 用 bar chart 显示时序数据
# ✅ 用 time series

# ❌ 用 table 显示百分比变化
# ✅ 用 stat + threshold
```

### 错误 2：过多变量

```
# ❌ 5 个变量下拉框，每次查询都要选
# ✅ 默认值自动选最常用，变量作为"筛选器"
```

### 错误 3：没设默认值

```json
// ❌ 模板变量没有默认值，打开 Dashboard 全空
{
  "name": "service",
  "type": "query",
  "query": "label_values(http_requests_total, service)",
  "current": { "selected": false }  // 没设默认
}

// ✅ 设置默认值为第一个
{
  "name": "service",
  "type": "query",
  "query": "label_values(http_requests_total, service)",
  "current": { "selected": true, "text": "order-service", "value": "order-service" }
}
```

### 错误 4：panel 标题太抽象

```
# ❌ "Metric 1", "Query A", "Test"
# ✅ "p99 延迟 (5m)", "Error Rate", "JVM Heap Used"
```

## 一句话总结

> **Dashboard 的核心目标：3 秒看到问题**。
> 信息密度优先，模板变量复用，黄金信号 + 关键路径 + Annotation = 80% 价值。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [devops](https://java-px.bot.cd/devops/):DevOps 监控
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 监控
- [kafka](https://java-px.bot.cd/kafka/):日志收集
