---
title: Grafana 集成
description: ClickHouse 作为 Grafana 数据源：原生插件 + Dashboard 实战
---

# Grafana 集成

Grafana 是 ClickHouse 最常用的可视化工具，官方提供原生插件。

## 安装插件

### Grafana 10+

```bash
grafana-cli plugins install clickhouse
systemctl restart grafana-server
```

### Docker

```yaml
# docker-compose.yml
version: '3'
services:
  grafana:
    image: grafana/grafana:latest
    environment:
      GF_INSTALL_PLUGINS: "clickhouse"
    ports:
      - 3000:3000
```

### 自定义路径

```ini
# grafana.ini
[plugin.clickhouse]
path = /var/lib/grafana/plugins/clickhouse
```

## 配置数据源

```yaml
# Grafana → Configuration → Data sources → Add
type: ClickHouse
url: http://clickhouse-1:8123
database: default
username: default
password: ''
```

### 默认数据库

`default` 库通常是测试用，生产建议用专用库：

```sql
CREATE DATABASE analytics
```

### 多数据源

可配置多个 ClickHouse 数据源（区分生产/测试）：

- `ClickHouse-Prod`（生产）
- `ClickHouse-Dev`（开发）

## 常用查询面板

### 1. QPS 时间线

```sql
SELECT
  $__timeColumn(event_time) AS time,
  count() / 5 AS qps
FROM events
WHERE $__timeFilter(event_time)
GROUP BY time
ORDER BY time
```

`$__timeColumn` 和 `$__timeFilter` 是 Grafana 宏，自动匹配面板时间范围。

### 2. P95 / P99 延迟

```sql
SELECT
  $__timeColumn(event_time) AS time,
  quantile(0.95)(duration_ms) AS p95,
  quantile(0.99)(duration_ms) AS p99,
  avg(duration_ms) AS avg_latency
FROM events
WHERE $__timeFilter(event_time) AND duration_ms > 0
GROUP BY time
ORDER BY time
```

### 3. 错误率

```sql
SELECT
  $__timeColumn(event_time) AS time,
  countIf(status_code >= 500) / count() AS error_rate
FROM events
WHERE $__timeFilter(event_time)
GROUP BY time
ORDER BY time
```

### 4. TOP 接口表格

```sql
SELECT
  path,
  count() AS request_count,
  avg(duration_ms) AS avg_latency,
  quantile(0.95)(duration_ms) AS p95,
  countIf(status_code >= 500) / count() AS error_rate
FROM events
WHERE $__timeFilter(event_time)
GROUP BY path
ORDER BY request_count DESC
LIMIT 20
```

### 5. 多维 UV（Bar Gauge）

```sql
SELECT
  country,
  bitmapCardinality(merge(uv_bitmap)) AS uv
FROM events_uv_mv_table
WHERE event_date = today()
GROUP BY country
ORDER BY uv DESC
LIMIT 10
```

## 告警

Grafana Alerting + ClickHouse 集成：

```yaml
# Grafana alert rule
- name: 'HighErrorRate'
  condition: >
    query(type:clickhouse, datasource:ClickHouse-Prod, query:
      "SELECT countIf(status_code >= 500) / count() AS error_rate
       FROM events
       WHERE $__timeFilter(event_time)
       GROUP BY time
       ORDER BY time"
    ) > 0.05
  for: 5m
  to: oncall
  frequency: 1m
```

## Dashboard 模板

### 业务看板（电商）

```yaml
panels:
  - title: 实时 GMV
    type: stat
    targets:
      - query: |
          SELECT sum(amount) AS gmv
          FROM orders
          WHERE order_time >= today()

  - title: 今日订单
    type: stat
    targets:
      - query: |
          SELECT count() AS orders FROM orders WHERE order_time >= today()

  - title: GMV 时间线
    type: timeseries
    targets:
      - query: |
          SELECT
            $__timeColumn(order_time) AS time,
            sum(amount) AS gmv
          FROM orders
          WHERE $__timeFilter(order_time)
          GROUP BY time

  - title: TOP 10 商品
    type: table
    targets:
      - query: |
          SELECT
            product_name,
            sum(amount) AS sales,
            count() AS order_count
          FROM orders o
          JOIN products p ON o.product_id = p.id
          WHERE order_time >= today()
          GROUP BY product_name
          ORDER BY sales DESC
          LIMIT 10

  - title: 用户分布
    type: piechart
    targets:
      - query: |
          SELECT country, bitmapCardinality(merge(uv_bitmap)) AS uv
          FROM events_uv_mv_table
          WHERE event_date = today()
          GROUP BY country
```

## 性能优化

### 1. 限制数据扫描

```sql
-- 添加 WHERE 条件避免全表扫
WHERE $__timeFilter(event_time) AND event_type = 'click'
```

### 2. 预聚合

```sql
-- 实时看板用物化视图预聚合
SELECT
  $__timeColumn(event_minute) AS time,
  sumMerge(pv) AS pv
FROM events_uv_pv_1m  -- 物化视图
WHERE $__timeFilter(event_minute)
GROUP BY time
```

### 3. 设置合理刷新间隔

```yaml
# Grafana panel
refresh: 30s  -- 实时看板 30 秒刷新
```

### 4. 并发控制

```yaml
# Grafana 数据源配置
maxOpenConns: 10
maxIdleConns: 5
connMaxLifetime: 600
```

## 常见问题

### Q1：Grafana 无法连接 ClickHouse？

- 检查 `url` 是否正确（带端口 `8123`）
- 检查 ClickHouse HTTP 服务是否开启：`grep '<listen_host>' /etc/clickhouse-server/config.xml`
- 防火墙 / 网络：Grafana 节点能访问 ClickHouse 8123 端口

### Q2：宏变量没替换？

- 用 `$__timeFilter(column)` 代替手动 `WHERE time BETWEEN`
- `$__fromTime` / `$__toTime` 手动使用

### Q3：查询慢？

- 检查是否用物化视图
- 加 `LIMIT` 限制返回
- 加 `PREWHERE` 过滤

## 大厂实践

- **Uber**：自研 LogGlass（Grafana 包装）
- **Cloudflare**：Grafana + 自定义面板（DNS / CDN）
- **字节跳动**：ByteInsight（自研 BI，CK + Grafana）

## 下一步

- 学习 Prometheus 集成：见 [prometheus.md](./prometheus.md)
- 学习 Go 客户端：见 [go-client.md](./go-client.md)


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
