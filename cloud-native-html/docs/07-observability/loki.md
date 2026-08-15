---
title: Loki 日志聚合
---

# Loki - 日志聚合系统

> Loki = Prometheus 思路的日志系统（标签 + 拉模式 + 不索引全文）。Grafana 同公司出品。

## 🤔 为什么需要 Loki

```
ELK（Elasticsearch + Logstash + Kibana）：
  ❌ 重（ES 吃资源）
  ❌ 全文本索引 → 存储爆炸
  ❌ 运维复杂

Loki：
  ✅ 轻量（标签索引，不索引全文）
  ✅ 对象存储（S3 / GCS）扩展
  ✅ Grafana 集成（同公司）
  ✅ 与 Prometheus 思路一致
```

## 🏗️ 架构

```
App / Node ──promtail──> Loki ─────► Object Storage (S3)
                            │         (chunks)
                            ▼
                        index (BoltDB)
                            ▲
                            │
                          Grafana
```

| 组件 | 作用 |
|------|------|
| **Loki** | 日志存储 + 查询（LogQL） |
| **promtail** | 采集 agent（推送到 Loki） |
| **grafana-agent / alloy** | 替代 promtail（推荐） |
| **Object Storage** | 长期存储（chunks + indexes） |
| **Grafana** | 查询 + 可视化 |

## 🚀 部署

### Helm 装

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# 装（带对象存储）
helm install loki grafana/loki \
  --set loki.storage.type=filesystem \
  --set loki.storage.filesystem.directories="/loki/chunks" \
  --set singleBinary.replicas=1

# 装 promtail
helm install promtail grafana/promtail
```

### 集成 prometheus-stack

如果用 `kube-prometheus-stack`，已有 Loki 模式：

```bash
helm install kube-prometheus ... --set grafana.additionalDataSources[0].name=Loki ...
# 或后装
helm install loki grafana/loki-stack -n monitoring
```

## 📜 promtail 配置

```yaml
# promtail ConfigMap
server:
  http_listen_port: 9080

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  # k8s pod 日志
  - job_name: kubernetes
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        target_label: app
      - source_labels: [__meta_kubernetes_namespace]
        target_label: namespace
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: pod
    pipeline_stages:
      - docker:
          docker_path_regex: /var/lib/docker/containers/(?P<container_path>.+)
```

## 🔍 LogQL 速查

```logql
# 简单：所有 myapp 日志
{app="myapp"}

# 过滤内容
{app="myapp"} |= "error"

# 不包含
{app="myapp"} != "DEBUG"

# 正则
{app="myapp"} |~ "error|warning"

# 统计（rate）
rate({app="myapp"} |= "error" [5m])

# 解析 json
{app="myapp"} | json | status_code >= 500

# 抽取字段
{app="myapp"} | json | line_format "{{.status}} {{.method}} {{.path}}"

# 聚合（按状态码）
sum by (status) (
  rate({app="myapp"} | json | status_code!="" [5m])
)
```

## 🪜 Grafana 集成

数据源 → Loki：
- URL: `http://loki.monitoring.svc.cluster.local:3100`
- 自动装在 kube-prometheus-stack + loki-stack

```logql
{namespace="prod", app="myapp"} |= "error"
```

## 🔧 高级

### 多租户 / 多集群

```yaml
# 每个租户独立路径
limits_config:
  retention_period: 744h           # 31 天
  ingestion_rate_mb: 10
  ingestion_burst_size_mb: 20
```

### 对象存储（S3 / GCS / MinIO）

```yaml
storage_config:
  aws:
    s3: s3://my-loki-bucket
    s3forcepathstyle: true
    access_key_id: xxx
    secret_access_key: xxx
```

### 采样（降低存储成本）

```yaml
limits_config:
  reject_old_samples: true
  reject_old_samples_max_age: 168h
  max_entries_limit_per_query: 5000
```

## 🩹 故障

```bash
# promtail 没推上去
kubectl -n monitoring logs -l app=promtail

# Loki 503
kubectl -n monitoring logs -l app=loki

# Grafana 看不到
# 1. 数据源 URL 对吗？
# 2. loki 命名空间一致吗？
# 3. promtail job 标签匹配？
```

## 🆚 ELK vs Loki

| | ELK | Loki |
|--|-----|------|
| 索引 | 全文 | 仅标签 |
| 存储 | ES（重） | 对象存储（轻） |
| 资源 | 高 | 低 |
| 查询语法 | Lucene | LogQL |
| 全文搜索 | ✅ 快 | ❌（只能正则） |
| 适合 | 通用日志 | 容器 / 指标型日志 |

**Loki 不擅长全文搜索**。需要全文 → 上 ES / Meilisearch。

## 🛠 实战

```bash
# 1. 装
helm install loki grafana/loki -n monitoring
helm install promtail grafana/promtail -n monitoring

# 2. 看 pod 日志
kubectl -n monitoring port-forward svc/loki 3100:3100
# 浏览器 Loki API: /ready

# 3. Grafana 加 Loki 数据源
# URL: http://loki.monitoring.svc.cluster.local:3100

# 4. Explore → 选 Loki
{namespace="default", app="myapp"}
```

## 🔗 下一步

- [Prometheus](/07-observability/prometheus)
- [Grafana 仪表板](/07-observability/grafana)
- [Alertmanager](/07-observability/alertmanager)