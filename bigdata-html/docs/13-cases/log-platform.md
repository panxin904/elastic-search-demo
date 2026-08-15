---
title: 日志平台
---
# 日志平台

## 1. 是什么

日志平台 = 集中式日志采集 + 存储 + 查询 + 分析系统。

核心价值：
  - 故障定位
  - 性能分析
  - 安全审计
  - 业务监控
  - 用户行为分析

## 2. 日志平台架构

```
应用 / 系统
  ↓
日志采集（Filebeat / Flume / Fluentd）
  ↓
消息队列（Kafka）
  ↓
存储（Elasticsearch / ClickHouse / HDFS）
  ↓
查询（Kibana / Grafana）
  ↓
告警（ElastAlert / 自研）
```

## 3. 主流日志方案

### 3.1 ELK（Elasticsearch + Logstash + Kibana）

```
应用 → Filebeat → Logstash → Elasticsearch → Kibana

特点：
  - 全功能
  - 全文搜索强
  - 社区活跃
```

### 3.2 EFK（Elasticsearch + Fluentd + Kibana）

```
应用 → Fluentd → Elasticsearch → Kibana

特点：
  - Kubernetes 友好
  - 资源占用低
```

### 3.3 ClickHouse 方案

```
应用 → Vector → Kafka → ClickHouse → Grafana

特点：
  - 写入极快
  - 列式压缩
  - 实时查询
```

### 3.4 Loki 方案

```
应用 → Promtail → Loki → Grafana

特点：
  - 云原生
  - 标签索引
  - 资源占用低
```

## 4. 日志规范

### 4.1 日志格式（JSON）

```json
{
  "timestamp": "2024-01-15T10:00:00.123Z",
  "level": "INFO",
  "service": "order-service",
  "trace_id": "abc123",
  "user_id": 12345,
  "request_id": "req-001",
  "method": "POST",
  "path": "/api/orders",
  "status": 200,
  "duration_ms": 123,
  "message": "Order created successfully",
  "error": null,
  "extra": {
    "order_id": 67890,
    "amount": 99.99
  }
}
```

### 4.2 日志级别

| 级别 | 用途 |
|------|------|
| DEBUG | 调试信息 |
| INFO | 一般信息 |
| WARN | 警告 |
| ERROR | 错误 |
| FATAL | 致命错误 |

### 4.3 Trace ID 串联

```java
// 生成 Trace ID
String traceId = UUID.randomUUID().toString();
MDC.put("trace_id", traceId);

// 日志
log.info("User login: userId={}", userId);

// 跨服务传递
HttpHeaders headers = new HttpHeaders();
headers.set("X-Trace-Id", traceId);
```

## 5. 实战案例

### 案例 1：电商日志平台

```
架构：
  Java 应用 → Filebeat → Kafka → Elasticsearch → Kibana
  Nginx → Fluentd → ClickHouse → Grafana

存储：
  - Elasticsearch（7 天，全文搜索）
  - ClickHouse（90 天，聚合）
  - HDFS（1 年，备份）

查询：
  - Kibana（错误排查）
  - Grafana（业务监控）
```

### 案例 2：Kubernetes 日志

```
架构：
  Pod → Fluentd → Elasticsearch → Kibana

特点：
  - DaemonSet 部署
  - 自动采集所有 Pod
  - 标签（namespace / pod / container）
```

## 6. 日志查询

### 6.1 Kibana 查询

```
# 错误日志
level:ERROR AND service:order-service

# 慢查询
duration_ms:>1000

# 特定用户
user_id:12345

# 时间范围
@timestamp:[now-1h TO now]
```

### 6.2 ClickHouse 查询

```sql
-- 错误日志统计
SELECT
  service,
  COUNT(*) AS error_cnt,
  uniq(user_id) AS user_cnt
FROM logs
WHERE level = 'ERROR'
  AND ts > now() - INTERVAL 1 HOUR
GROUP BY service
ORDER BY error_cnt DESC;

-- 慢查询分布
SELECT
  service,
  path,
  quantile(0.95)(duration_ms) AS p95
FROM logs
WHERE ts > now() - INTERVAL 1 HOUR
GROUP BY service, path
ORDER BY p95 DESC
LIMIT 20;
```

## 7. 告警

### 7.1 ElastAlert（Elasticsearch）

```yaml
# config.yaml
rules_folder: rules

rule_configs:
  - name: high_error_rate
    type: frequency
    index: logs-*
    num_events: 100
    timeframe:
      minutes: 5
    filter:
      - level: ERROR
    alert:
      - slack
```

### 7.2 Grafana 告警

```
# PromQL（来自 Loki）
sum(rate({service="order-service", level="ERROR"}[5m])) > 10
```

## 8. 实战建议

1. **日志规范先行**：JSON + Trace ID + 字段
2. **分层存储**：热 / 温 / 冷
3. **告警分级**：紧急 / 警告 / 信息
4. **可视化**：Kibana / Grafana

## 9. 实战 checklist

- [ ] 日志规范（JSON + Trace ID）
- [ ] 采集（Filebeat / Fluentd）
- [ ] 传输（Kafka）
- [ ] 存储（Elasticsearch / ClickHouse）
- [ ] 查询（Kibana / Grafana）
- [ ] 告警（ElastAlert / Grafana）
- [ ] 监控（采集延迟 / 存储容量）

## 10. 实战技术栈

| 场景 | 推荐 |
|------|------|
| 全文搜索 | Elasticsearch + Kibana |
| 高写入 | ClickHouse + Grafana |
| 云原生 | Loki + Grafana |
| 私有化 | ELK |

## 🔗 下一步
- [用户画像](/13-cases/user-profile)
- [推荐系统](/13-cases/recommendation)
- [风控案例](/13-cases/risk-control)
