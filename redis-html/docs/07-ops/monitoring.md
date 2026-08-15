---
title: 监控告警
---

# 监控告警

"Redis 出问题才发现"是最低级的运维。一套完整的监控告警体系，应该在内存 80%、延迟翻倍、连接数激增的**当下**就通知到人。

## INFO 命令关键指标

### 必备监控字段

```bash
redis-cli INFO all > redis_info.txt
```

#### 1. 连接数

```bash
redis-cli INFO clients
# connected_clients:1523
# cluster_connections:50
# maxclients:10000
# blocked_clients:0
# tracking_clients:0
```

| 指标 | 健康阈值 |
|---|---|
| `connected_clients` | < maxclients × 0.7 |
| `blocked_clients` | 持续 > 0 要警惕（如 BLPOP 阻塞） |

#### 2. 内存

```bash
redis-cli INFO memory
# used_memory_human:11.87G
# used_memory_peak_human:13.20G
# maxmemory_human:16.00G
# mem_fragmentation_ratio:1.32
```

| 指标 | 健康阈值 |
|---|---|
| `used_memory / maxmemory` | < 80% |
| `mem_fragmentation_ratio` | 1.0 ~ 1.5 |
| `used_memory_peak` | 用于容量规划 |

#### 3. 命中率

```bash
redis-cli INFO stats | grep keyspace
# keyspace_hits:952340
# keyspace_misses:48120

# 命中率 = hits / (hits + misses)
# 952340 / (952340 + 48120) = 95.2%
```

命中率公式：

```bash
redis-cli INFO stats | awk '
/^keyspace_hits/{hits=$2}
/^keyspace_misses/{miss=$2}
END{
    if (hits+miss > 0)
        printf "命中率: %.2f%%\n", hits/(hits+miss)*100
}'
```

| 命中率 | 状态 |
|---|---|
| ≥ 95% | 优秀 |
| 90% ~ 95% | 良好 |
| < 90% | 缓存设计有问题 |

#### 4. 流量与 QPS

```bash
redis-cli INFO stats
# instantaneous_ops_per_sec:23456
# instantaneous_input_kbps:125.43
# instantaneous_output_kbps:892.10
# total_connections_received:15234000
# rejected_connections:0
```

`rejected_connections` > 0 说明触达 `maxclients`，必须扩。

#### 5. 主从复制

```bash
redis-cli INFO replication
# role:master
# connected_slaves:2
# slave0:ip=10.0.1.5,port=6379,state=online,offset=15234000,lag=0
# slave1:ip=10.0.1.6,port=6379,state=online,offset=15233998,lag=1
```

关键字段 `lag`：从节点延迟秒数，> 10 就要警惕。

#### 6. 延迟（latency）

```bash
# 实时延迟监控
redis-cli --latency
# min: 0, max: 3, avg: 0.42 (1523 samples)

# 历史延迟
redis-cli --latency-history -i 5
# min: 0, max: 5, avg: 0.51 (1234 samples)
# min: 0, max: 2, avg: 0.48 (1523 samples)
```

`avg > 5ms` 通常意味着出现了慢查询或网络问题。

#### 7. 慢查询

```bash
redis-cli INFO stats | grep slow
# slowlog_len:23

redis-cli CONFIG GET slowlog-log-slower-than
# 1) "slowlog-log-slower-than"
# 2) "10000"
```

### 一键健康检查脚本

```bash
#!/bin/bash
# redis_health.sh
HOST=${1:-127.0.0.1}
PORT=${2:-6379}

echo "=== 连接数 ==="
redis-cli -h $HOST -p $PORT INFO clients | grep connected_clients

echo "=== 内存 ==="
redis-cli -h $HOST -p $PORT INFO memory | grep -E "used_memory_human|maxmemory_human|mem_fragmentation_ratio"

echo "=== 命中率 ==="
redis-cli -h $HOST -p $PORT INFO stats | awk '
/^keyspace_hits/{h=$2}
/^keyspace_misses/{m=$2}
END{if(h+m>0) printf "%.2f%%\n", h/(h+m)*100}'

echo "=== QPS ==="
redis-cli -h $HOST -p $PORT INFO stats | grep instantaneous_ops_per_sec

echo "=== 慢查询 ==="
redis-cli -h $HOST -p $PORT SLOWLOG LEN

echo "=== 主从 ==="
redis-cli -h $HOST -p $PORT INFO replication | grep -E "role|connected_slaves"
```

## Prometheus + Redis Exporter

### 部署 Redis Exporter

```bash
# Docker 启动
docker run -d \
  --name redis-exporter \
  -p 9121:9121 \
  oliver006/redis_exporter \
  --redis.addr=redis://10.0.1.1:6379 \
  --redis.password=yourpassword
```

验证：

```bash
curl http://localhost:9121/metrics | head
# HELP go_gc_duration_seconds A summary of the GC duration.
# TYPE go_gc_duration_seconds summary
# ...
# HELP redis_up Information about the Redis instance.
# TYPE redis_up gauge
redis_up 1
```

### Prometheus 抓取配置

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'redis'
    static_configs:
      - targets:
          - 'redis-exporter-1:9121'
          - 'redis-exporter-2:9121'
          - 'redis-exporter-3:9121'

  # 集群模式：每个主节点一个 Exporter
  - job_name: 'redis-cluster'
    static_configs:
      - targets:
          - 'redis-exporter-master-1:9121'
          - 'redis-exporter-master-2:9121'
          - 'redis-exporter-master-3:9121'
```

### 关键指标列表

| 指标 | 含义 |
|---|---|
| `redis_up` | 实例存活（0/1） |
| `redis_connected_clients` | 当前连接数 |
| `redis_used_memory_bytes` | 已用内存 |
| `redis_memory_used_percent` | 内存使用率 |
| `redis_mem_fragmentation_ratio` | 碎片率 |
| `redis_keyspace_hits_total` | 命中次数 |
| `redis_keyspace_misses_total` | 未命中次数 |
| `redis_commands_total` | 命令计数（按 command 标签分类） |
| `redis_evicted_keys_total` | 驱逐次数 |
| `redis_slowlog_length` | 慢查询队列长度 |
| `redis_net_input_bytes_total` | 入流量 |
| `redis_net_output_bytes_total` | 出流量 |
| `redis_latency_percentiles_us` | 延迟分位数 |

## Grafana Dashboard

### 推荐面板（基于 11833 Dashboard）

1. **Overview**：uptime、connected_clients、used_memory
2. **Memory**：内存使用趋势、碎片率、命中率
3. **Commands**：QPS 趋势、按命令分类
4. **Network**：入/出流量
5. **Replication**：主从同步延迟
6. **Slow Query**：慢查询队列长度

### 自定义面板配置示例

```json
{
  "title": "Redis Memory Usage",
  "panels": [
    {
      "title": "Used Memory",
      "type": "graph",
      "targets": [
        {
          "expr": "redis_used_memory_bytes{instance=~\"$instance\"}",
          "legendFormat": "{{instance}}"
        }
      ],
      "yaxes": [
        {"format": "bytes"}
      ]
    },
    {
      "title": "Memory Used %",
      "type": "singlestat",
      "targets": [
        {
          "expr": "redis_memory_used_percent{instance=~\"$instance\"}",
          "legendFormat": "{{instance}}"
        }
      ],
      "thresholds": "70,85"
    }
  ]
}
```

## 告警规则配置

### Prometheus 告警规则

```yaml
# /etc/prometheus/rules/redis.yml
groups:
  - name: redis_alerts
    rules:
      # 1. 实例存活
      - alert: RedisDown
        expr: redis_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Redis 实例 {{ $labels.instance }} 不可用"
          description: "Redis 实例已宕机超过 1 分钟"

      # 2. 内存使用率
      - alert: RedisHighMemory
        expr: redis_memory_used_percent > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Redis 内存使用率 {{ $value }}%"
          description: "{{ $labels.instance }} 内存使用率超过 80%"

      # 3. 内存使用率紧急
      - alert: RedisCriticalMemory
        expr: redis_memory_used_percent > 95
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Redis 内存即将爆满"
          description: "{{ $labels.instance }} 内存使用率 {{ $value }}%"

      # 4. 命中率低
      - alert: RedisLowHitRate
        expr: |
          rate(redis_keyspace_hits_total[5m]) /
          (rate(redis_keyspace_hits_total[5m]) + rate(redis_keyspace_misses_total[5m]))
          < 0.8
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Redis 命中率过低"
          description: "{{ $labels.instance }} 命中率 {{ $value | humanizePercentage }}"

      # 5. 连接数过高
      - alert: RedisHighConnections
        expr: redis_connected_clients > 8000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Redis 连接数过高"
          description: "{{ $labels.instance }} 连接数 {{ $value }}"

      # 6. 主从延迟
      - alert: RedisReplicationLag
        expr: redis_connected_slave_lag_seconds > 10
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Redis 主从延迟 {{ $value }} 秒"
          description: "{{ $labels.labels.slave_ip }} 延迟超过 10 秒"

      # 7. 频繁驱逐
      - alert: RedisEviction
        expr: rate(redis_evicted_keys_total[5m]) > 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Redis 频繁驱逐 key"
          description: "{{ $labels.instance }} 每秒驱逐 {{ $value }} 个 key"

      # 8. 慢查询堆积
      - alert: RedisSlowQuery
        expr: redis_slowlog_length > 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Redis 慢查询队列堆积"
```

### Alertmanager 配置

```yaml
# /etc/alertmanager/alertmanager.yml
route:
  receiver: 'default'
  group_by: ['alertname', 'instance']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
      continue: true
    - match:
        severity: warning
      receiver: 'slack'

receivers:
  - name: 'default'
    webhook_configs:
      - url: 'http://alertmanager-webhook:8080/'

  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: '<your-key>'

  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/xxx'
        channel: '#redis-alerts'
        title: 'Redis Alert'
```

## 性能监控工具

### redis-cli --latency

```bash
# 实时延迟（持续输出）
redis-cli --latency -h 127.0.0.1
# min: 0, max: 1, avg: 0.18 (2345 samples)
# ^C 退出
```

### redis-cli --latency-history

```bash
# 历史延迟，每 N 秒一个采样
redis-cli --latency-history -h 127.0.0.1 -i 5
# min: 0, max: 3, avg: 0.32 (1234 samples)
# min: 0, max: 2, avg: 0.45 (2345 samples)
```

### redis-cli --stat

```bash
# 一行一输出，类 vmstat 风格
redis-cli --stat -h 127.0.0.1
# ------- data ------ --------------------- load -------------------- - child -
# keys       mem      clients blocked requests            connections
# 152340     11.87G   1523    0       234567 (+0)         152340
# 152341     11.87G   1523    0       234589 (+22)        152340
```

### redis-benchmark

```bash
# 压测命令
redis-benchmark -h 127.0.0.1 -t set,get -n 100000 -q
# SET: 89234.12 requests per second
# GET: 91234.56 requests per second
```

## 生产监控案例

### 案例 1：内存增长曲线异常

监控发现 Redis 内存从 11GB 突然涨到 15GB，4 小时没回落：

```promql
# Prometheus 查询
rate(redis_used_memory_bytes[1h])
```

排查：

```bash
# 1. 看驱逐次数（说明在疯狂淘汰）
redis-cli INFO stats | grep evicted
# evicted_keys:1523400   # 4 小时 152 万次

# 2. 看最大 key
redis-cli --bigkeys
# Biggest list found '"task:queue"' has 2000000 items

# 3. 处理
# a. 用 SCAN + LTRIM 缩减 list
# b. 临时 maxmemory 调大
# c. 改用 Kafka
```

### 案例 2：主从延迟告警风暴

Prometheus 频繁告警 `RedisReplicationLag`，但 `redis-cli INFO replication` 看 lag = 0。

原因：Redis Exporter 用 `INFO replication` 算 lag，**但 cluster 模式下主从关系复杂，部分节点确实有延迟**。

修复：
1. 区分"真延迟"和"统计误差"
2. 主从延迟阈值改为 `slave_lag > 30`（而非 10）
3. `for: 5m`（而非 2m），避免抖动告警

### 案例 3：客户端连接爆表

某应用重启后 Redis 连接数从 1500 涨到 9500：

```bash
redis-cli INFO clients
# connected_clients:9500
# maxclients:10000
```

排查：用 `CLIENT LIST` 看来源：

```bash
redis-cli CLIENT LIST | awk '{print $2}' | sort | uniq -c | sort -rn | head
# 7800 addr=10.0.5.23:54321  ← 应用服务器 IP
```

定位到是某应用 Redis 连接池配置错误（maxTotal 10000 而实际只需要 50）。

修复：

```java
// JedisPool 配置
JedisPoolConfig config = new JedisPoolConfig();
config.setMaxTotal(100);          // 最大连接
config.setMaxIdle(20);            // 最大空闲
config.setMinIdle(5);             // 最小空闲
config.setTestOnBorrow(true);     // 借出时检测
```

## 下一步

监控告警是"稳定运行"的最后一公里，但 Redis 自身也在持续演进。Redis 7 带来了多项重磅特性（Functions、Multi-part AOF、ACL v2 等）。看 [🆕 Redis 7 新特性](/07-ops/redis7-features)，了解如何用上新版本能力。