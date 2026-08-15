---
title: LogQL 查询语言
description: Loki + Promtail + Grafana
---

# LogQL 查询语言

> **TL;DR**：LogQL = **Loki 版的 PromQL**，分两类查询：**Log query**（日志内容过滤）+ **Metric query**（从日志生成指标）。**核心操作符：`{}` 标签过滤 + `|=` / `!=` 行内容匹配 + `|~` / `!~` 正则 + pipeline 解析阶段**。

## 一句话定义

```
LogQL = Loki 的查询语言
     = 两大类型：Log query（查日志原文）/ Metric query（聚合日志生成指标）
     = 标签过滤（必须）+ 内容过滤（可选）+ pipeline（解析）
     = 借鉴 PromQL，但操作对象是日志流
```

## Log Query（日志查询）

### 基础语法

```logql
# 1. 标签过滤（必须有标签选择，否则扫描全量数据 → 极慢）
{job="nginx", cluster="prod"}

# 2. 行内容过滤
{job="nginx"} |= "error"
{job="nginx"} != "healthcheck"
{job="nginx"} |~ "status=5[0-9]{2}"
{job="nginx"} !~ "favicon.ico"

# 3. 组合（多条件 AND）
{app="api", env="prod"} |= "exception" != "timeout" |~ "stacktrace|traceback"
```

### Pipeline 解析

```logql
# 1. json 解析（提取字段）
{app="api"} | json | status_code=500

# 2. logfmt 解析（k=v 格式）
{app="api"} | logfmt | level="error"

# 3. regexp 解析
{app="api"} | regexp "<status> (?P<status>\\d+) <duration> (?P<dur>\\d+)ms"

# 4. 阶段顺序：line_format（格式化输出）
{app="api"}
  | json
  | status_code=500
  | line_format "{{.status_code}} {{.request_path}} {{.err_message}}"
```

## Metric Query（指标查询）

```
从日志流聚合生成指标，等价 PromQL over log streams
核心函数：
  rate({...} [5m])              # 每秒行数
  count_over_time({...} [5m])   # 总行数
  sum by (...) (rate(...))      # 按标签聚合
  quantile_over_time(0.95, {...}) # 分位数
  bytes_rate({...} [5m])        # 每秒字节数
```

### 实战案例：HTTP 错误率

```logql
# 1. 总请求率（5 分钟窗口）
sum(rate({app="api", env="prod"}[5m]))

# 2. 5xx 错误率
sum(rate(
  {app="api", env="prod"}
  | json
  | status_code=~"5.."
  [5m]))

# 3. 错误率（百分比）
sum(rate({app="api"} | json | status_code=~"5.." [5m]))
/
sum(rate({app="api"} [5m]))

# 4. 按 endpoint 分组
sum by (endpoint) (
  rate({app="api"} | json | status_code=~"5.." [5m])
)

# 5. P99 延迟（从日志提取 duration_ms 字段）
quantile_over_time(0.99,
  {app="api"}
  | json
  | __error__=""
  | unwrap duration_ms [5m]
)
```

### 实战案例：解析 Java 异常

```logql
# Java 异常日志格式：
# 2026-08-09 12:34:56 ERROR com.example.Service - NullPointerException at UserService.findById(UserService.java:42)

# 1. 提取异常类型
{app="java-service"}
| regexp "ERROR (?P<exception>\\S+) at (?P<location>[^\\s]+)"

# 2. 按异常类型分组计数
sum by (exception) (
  count_over_time(
    {app="java-service"} |= "ERROR"
    | regexp "ERROR (?P<exception>\\S+)"
    [10m]
  )
)

# 3. 异常率告警
sum(rate(
  {app="java-service"} |= "ERROR" [5m]
)) > 10
```

## 高级技巧

### 1. Drop 解析失败的行

```logql
{app="api"} | json | __error__="" | level="error"
# 只保留 JSON 解析成功的行
```

### 2. 模板变量（Grafana 配合）

```
${job}        # 动态选择
$__range      # Grafana 时间范围
{app=~"$app"} # 正则匹配
```

### 3. 高基数优化

```logql
# 错误示例：标签包含 user_id → 高基数爆炸
{user_id="12345"}  # ✗ user_id 是高基数，禁止作为 Loki 标签

# 正确做法：user_id 作为 line 字段提取，不放标签
{app="api"}
| regexp "user_id=(?P<user_id>\\d+)"
| user_id="12345"
```

## 实战配置：Loki + Promtail + Grafana

```yaml
# promtail config：采集 nginx 日志
server:
  http_listen_port: 9080

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: nginx
    static_configs:
      - targets: [localhost]
        labels:
          job: nginx
          env: prod
          __path__: /var/log/nginx/*.log
    pipeline_stages:
      - regex:
          expression: '^(?P<remote_addr>\S+) - \S+ \[(?P<time>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+) \S+" (?P<status>\d+) (?P<bytes>\d+)'
      - labels:
          method:
          status:
```

## 一句话总结

> **LogQL = Loki 版的 PromQL**。**两类查询：Log query（看日志）+ Metric query（聚合指标）**。**核心：标签过滤（必须）+ Pipeline（json/logfmt/regexp）+ Metric 函数（rate/count_over_time/quantile）**。**避免高基数标签（user_id/order_id）**。

---

## 关联章节

- [Loki 概览](../05-loki/overview.md) — Loki 架构 / chunks / ingester
- [Pipeline 处理](../05-loki/pipeline.md) — Promtail pipeline 详解
- [Loki 最佳实践](../05-loki/best-practice.md) — 标签设计 / 存储优化
- [Grafana Dashboard](../04-grafana/dashboard.md) — 把 LogQL 可视化

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>