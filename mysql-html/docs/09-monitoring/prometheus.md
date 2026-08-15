---
title: Prometheus + mysqld_exporter
---

# 📊 Prometheus + mysqld_exporter 监控

> Prometheus + Grafana 是云原生时代的标准监控方案，配合 mysqld_exporter 可以实现 MySQL 的**全方位生产级监控**。

## 🎯 监控体系概览

```
┌──────────────┐
│  MySQL       │
│  多个实例     │
└──────┬───────┘
       │ 采集指标
       ▼
┌──────────────┐
│  mysqld_     │ ← 每个 MySQL 实例一个
│  exporter    │
└──────┬───────┘
       │ HTTP /metrics
       ▼
┌──────────────┐
│  Prometheus  │ ← 存储时序数据
│  时序数据库  │
└──────┬───────┘
       │ PromQL 查询
       ▼
┌──────────────┐
│  AlertManager│ ← 告警（邮件/钉钉/Slack）
└──────────────┘
       │
       ▼
┌──────────────┐
│   Grafana    │ ← 可视化面板
│   仪表板     │
└──────────────┘
```

## 📦 mysqld_exporter 安装

### 1. 下载安装

```bash
# 下载最新版本
wget https://github.com/prometheus/mysqld_exporter/releases/download/v0.15.1/mysqld_exporter-0.15.1.linux-amd64.tar.gz

# 解压
tar -xzf mysqld_exporter-0.15.1.linux-amd64.tar.gz
cd mysqld_exporter-0.15.1.linux-amd64

# 复制二进制文件
sudo cp mysqld_exporter /usr/local/bin/
```

### 2. 创建监控用户

```sql
-- 在 MySQL 中创建 exporter 用户
CREATE USER 'exporter'@'%' IDENTIFIED BY 'StrongP@ss!';
GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'exporter'@'%';
FLUSH PRIVILEGES;
```

### 3. 配置 exporter

```bash
# 创建配置文件
cat > /etc/mysqld_exporter.cnf << EOF
[client]
user=exporter
password=StrongP@ss!
host=127.0.0.1
port=3306
EOF

# 设置权限
chmod 600 /etc/mysqld_exporter.cnf
```

### 4. 启动 exporter

```bash
# 启动（默认端口 9104）
mysqld_exporter \
  --config.my-cnf=/etc/mysqld_exporter.cnf \
  --web.listen-address=:9104

# 用 systemd 管理
cat > /etc/systemd/system/mysqld_exporter.service << EOF
[Unit]
Description=Prometheus MySQL Exporter
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/mysqld_exporter \
  --config.my-cnf=/etc/mysqld_exporter.cnf \
  --web.listen-address=:9104
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now mysqld_exporter
```

## 📊 Prometheus 配置

### 1. prometheus.yml

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'mysql'
    static_configs:
      - targets:
          - 'mysql-prod-1:9104'
          - 'mysql-prod-2:9104'
          - 'mysql-slave-1:9104'
        labels:
          env: production
          team: dba
```

### 2. 启动 Prometheus

```bash
prometheus \
  --config.file=/etc/prometheus/prometheus.yml \
  --storage.tsdb.path=/var/lib/prometheus/ \
  --web.console.libraries=/usr/share/prometheus/console_libraries \
  --web.console.templates=/usr/share/prometheus/consoles
```

## 📈 Grafana 仪表板

### 1. 添加 Prometheus 数据源

```
Grafana → Configuration → Data Sources → Add
- Type: Prometheus
- URL: http://localhost:9090
```

### 2. 导入 MySQL 仪表板

```bash
# 使用社区仪表板 ID 7362（最流行）
Grafana → Dashboards → Import
- Dashboard ID: 7362
- Data Source: Prometheus
```

**关键面板：**
- MySQL Up/Down
- QPS / TPS
- 连接数
- 慢查询数量
- Buffer Pool 命中率
- 主从延迟
- 锁等待
- 复制状态

## 🎯 关键监控指标

### 1. 性能指标

```promql
# QPS
rate(mysql_global_status_questions[5m])

# TPS（事务数/秒）
rate(mysql_global_status_commands_total{command="commit"}[5m]) + 
rate(mysql_global_status_commands_total{command="rollback"}[5m])

# 慢查询数量
mysql_global_status_slow_queries

# 缓冲池命中率
1 - (rate(mysql_global_status_innodb_buffer_pool_reads[5m]) / 
        rate(mysql_global_status_innodb_buffer_pool_read_requests[5m]))
```

### 2. 连接指标

```promql
# 当前连接数
mysql_global_status_threads_connected

# 活跃连接数
mysql_global_status_threads_running

# 连接使用率
mysql_global_status_threads_connected / 
mysql_global_variables_max_connections
```

### 3. InnoDB 指标

```promql
# 缓冲池使用率
mysql_global_status_innodb_buffer_pool_pages_used / 
mysql_global_status_innodb_buffer_pool_pages_total

# 锁等待数
mysql_global_status_innodb_row_lock_waits

# 死锁数
mysql_global_status_innodb_deadlocks
```

### 4. 复制指标（主从）

```promql
# 主从延迟
mysql_slave_status_seconds_behind_master

# Slave IO 线程状态
mysql_slave_status_slave_io_running

# Slave SQL 线程状态
mysql_slave_status_slave_sql_running
```

## 🚨 告警规则

### Prometheus AlertManager 配置

```yaml
# /etc/prometheus/rules/mysql.yml
groups:
- name: mysql_alerts
  rules:

  # 服务不可用
  - alert: MySQLDown
    expr: mysql_up == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "MySQL 实例 {{ $labels.instance }} 不可用"

  # 慢查询过多
  - alert: MySQLTooManySlowQueries
    expr: increase(mysql_global_status_slow_queries[5m]) > 10
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "MySQL 慢查询过多"

  # 连接数过高
  - alert: MySQLHighConnectionUsage
    expr: mysql_global_status_threads_connected / 
          mysql_global_variables_max_connections > 0.8
    for: 5m
    labels:
      severity: warning

  # 主从延迟过大
  - alert: MySQLReplicationLag
    expr: mysql_slave_status_seconds_behind_master > 60
    for: 2m
    labels:
      severity: warning

  # 主从复制中断
  - alert: MySQLReplicationBroken
    expr: mysql_slave_status_slave_io_running == 0 or
          mysql_slave_status_slave_sql_running == 0
    for: 1m
    labels:
      severity: critical

  # 缓冲池命中率低
  - alert: MySQLLowBufferPoolHitRate
    expr: |
      1 - (rate(mysql_global_status_innodb_buffer_pool_reads[5m]) / 
           rate(mysql_global_status_innodb_buffer_pool_read_requests[5m])) < 0.95
    for: 10m
    labels:
      severity: warning
```

### 钉钉告警

```yaml
# /etc/alertmanager/config.yml
route:
  receiver: 'dingtalk'

receivers:
- name: 'dingtalk'
  webhook_configs:
  - url: 'https://oapi.dingtalk.com/robot/send?access_token=xxx'
    send_resolved: true
```

## 📊 监控告警分层

### P0 - 紧急（立即响应）

```
- MySQL 实例宕机
- 主从复制中断
- 数据库连接耗尽
- 磁盘空间 100%
```

### P1 - 重要（30 分钟内）

```
- 慢查询突增
- 主从延迟 > 60s
- CPU 使用率 > 90%
- 死锁频繁
```

### P2 - 警告（工作时间处理）

```
- 缓冲池命中率 < 95%
- 索引使用率低
- 长事务
- 大查询
```

## 🎯 总结

**监控体系核心：**
- ✅ mysqld_exporter 采集指标
- ✅ Prometheus 存储时序数据
- ✅ AlertManager 触发告警
- ✅ Grafana 可视化

**关键指标：**
- QPS / TPS / 连接数
- 慢查询 / 缓冲池
- 主从延迟 / 复制状态
- 锁等待 / 死锁

**告警分层：**
- P0 紧急 → 立即处理
- P1 重要 → 30 分钟
- P2 警告 → 工作时间

**下一步：** [📐 垂直拆分 vs 水平拆分](../10-sharding/strategy) — 分库分表系列