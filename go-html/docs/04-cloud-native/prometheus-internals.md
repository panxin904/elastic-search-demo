---
title: Prometheus 源码导读
date: 2026-08-15  # date-auto-injected
---

# Prometheus 源码导读

**Prometheus = Cloud Native 监控的事实标准**——Go 写，80+ 组件，10 年迭代。

## 一句话总结

> **Prometheus = pull-based TSDB + PromQL + alerting + service discovery**。**Go 让单机/集群部署都简单**。

---

## 一、Prometheus 架构

```
┌──────────────┐
│  targets     │  ← 应用 / exporter
└──────┬───────┘
       │ HTTP GET /metrics
       ▼
┌──────────────┐
│  Prometheus  │  ← 采集 + TSDB + 规则
│   Server     │
└──────┬───────┘
       │ remote_write
       ▼
┌──────────────┐
│  Alertmanager│  ← 告警聚合 / 去重 / 路由
└──────┬───────┘
       │ Webhook / Email / Slack
       ▼
┌──────────────┐
│  Grafana     │  ← 可视化
└──────────────┘
```

## 二、源码结构

```bash
git clone https://github.com/prometheus/prometheus
ls cmd/prometheus/      # 主服务
ls cmd/promtool/        # 工具
ls discovery/           # 服务发现（k8s / consul / file）
ls rules/               # 告警规则
ls storage/             # TSDB 存储
ls scrape/              # 抓取逻辑
ls web/                 # Web UI
```

**关键包**：
- `prometheus/tsdb/`：自研 TSDB
- `prometheus/promql/`：查询引擎
- `prometheus/discovery/`：服务发现
- `prometheus/rules/`：告警/记录规则

## 三、TSDB 存储

```go
// storage/tsdb/db.go
type DB struct {
    dir   string
    opts  *Options
    chunkPool chunkenc.Pool
    blocks []*Block
    head   *Head
    
    // 时间序列索引
    series *seriesIndex
    postings *index.Postings
}

// 时间序列由 labels hash 索引
type labels.Labels []Label  // 键值对

// Append 一个样本
func (a *headAppender) Add(lset labels.Labels, t int64, v float64) (uint64, error) {
    s, _, err := a.head.getOrCreate(lset.Hash(), lset)
    if err != nil { return 0, err }
    a.samples = append(a.samples, record.RefSample{Ref: s, T: t, V: v})
    return s, nil
}
```

**TSDB 关键概念**：
- **Block**：2 小时数据，压缩成 mmap 块
- **WAL**：Write-Ahead Log，崩溃恢复
- **Compaction**：小 block 合并成大 block
- **Retention**：超过保留期 block 删
- **Out-of-order**：乱序样本支持（Prometheus 2.4+）

## 四、PromQL 引擎

```go
// promql/engine.go
type Engine struct {
    opts           EngineOptions
    ng             *numberLoader
    storage        storage.Storage
}

// 编译 PromQL → AST → 逻辑计划 → 物理计划
func (ng *engine) NewInstantQuery(queryable storage.Queryable, qs string, ts time.Time) (Query, error) {
    expr, err := parser.ParseExpr(qs)
    if err != nil { return nil, err }
    q, err := ng.newQuery(queryable, expr, ts, ts, 0)
    return q, err
}
```

**核心算子**：
- `rate()`：每秒增长率
- `irate()`：瞬时增长率
- `sum/rate`：聚合
- `histogram_quantile()`：直方图分位数
- `predict_linear()`：线性预测

**查询优化**：向量匹配、索引查找、并发执行。

## 五、Scrape 抓取

```go
// scrape/scrape.go
type scrapePool struct {
    config    *config.ScrapeConfig
    client    *http.Client
    targets   map[uint64]*Target
    // ...
}

func (sp *scrapePool) sync(targets []*Target) {
    // 1. 标记 active
    for _, t := range targets {
        if t.Disabled(GlobalState.Labels) { continue }
        t.setActive(GlobalState.ScrapePools.OC())
    }
    
    // 2. 拉取 metrics
    for _, t := range active {
        go t.scrapeAndReport()
    }
}
```

**Target 抓取**：
1. HTTP GET `<target>/metrics`
2. 解析文本格式
3. 写到 TSDB
4. 失败标记

## 六、Service Discovery

```go
// discovery/kubernetes/kubernetes.go
type Discovery struct {
    client kubernetes.Interface
    role   string  // endpoints/pod/service
}

func (d *Discovery) Run(ctx context.Context, ch chan<- []*targetgroup.Group) {
    // 1. 列出资源
    endpoints, _ := d.client.CoreV1().Endpoints("default").List(ctx, metav1.ListOptions{})
    // 2. 转成 targets
    for _, ep := range endpoints.Items {
        tg := &targetgroup.Group{Source: ep.Name}
        for _, ss := range ep.Subsets {
            for _, addr := range ss.Addresses {
                tg.Targets = append(tg.Targets, model.LabelSet{
                    "__address__":                  model.LabelValue(dn + ":" + port),
                    "__meta_kubernetes_pod_label_app":  model.LabelValue("myapp"),
                })
            }
        }
        ch <- []*targetgroup.Group{tg}
    }
}
```

**支持 30+ SD**：
- k8s / endpoints / pod / service / ingress
- consul / eureka
- file / http / dns / aws / gce / azure

## 七、Alerting

```yaml
# rule.yaml
groups:
  - name: example
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status="500"}[5m]))
            /
          sum(rate(http_requests_total[5m]))
            > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate"
          description: "{{ $value | humanizePercentage }} errors"
```

**告警生命周期**：
1. Prometheus 评估规则
2. ALERT 状态推送 Alertmanager
3. Alertmanager 路由 / 去重 / 抑制 / 静默
4. 发送 Webhook / Email / Slack

## 八、Remote Write

```go
// storage/remote/write.go
func (w *WriteStorage) Write(req *remote.WriteRequest) error {
    // 1. 编码（snappy + protobuf）
    // 2. 发送到 remote（Thanos / Cortex / Mimir / VictoriaMetrics）
    // 3. 队列 + 重试
}
```

**为何需要 remote write**：
- Prometheus 单机容量有限（百万级时间序列）
- Remote write 到对象存储（S3/GCS）实现长期
- 多 Prometheus 联邦查询

## 九、Go 的优势在 Prometheus

| 优势 | 体现 |
|---|---|
| 静态二进制 | 单文件部署，无需 Python/Ruby runtime |
| goroutine | 10000+ target 并发抓取 |
| mmap | TSDB block 用 mmap 提升 IO |
| Prometheus client_golang | Go 应用无缝埋点 |
| go mod | 各组件独立发布 |

## 十、Prometheus 2.x vs VictoriaMetrics

| 指标 | Prometheus | VictoriaMetrics |
|---|---|---|
| 单机容量 | 千万级 | 亿级 |
| 存储压缩 | ~2 bytes/sample | ~0.5 bytes/sample |
| Remote write | 支持 | 支持（更快） |
| Go 写 | 是 | 是 |
| 集群方案 | Agent + 联邦 / Cortex | Enterprise Cluster |

## 关联章节

- **04-cloud-native/kubernetes-internals**：K8s SD
- **04-cloud-native/etcd-internals**：另一种分布式存储
- **04-cloud-native/cncf-ecosystem**：CNCF 全景

## 一句话总结

> **Prometheus 源码 = TSDB + PromQL + scrape + SD + alert**。**Go 的并发 + mmap + 静态部署让监控变简单**。


<!-- auto-enrich:do-not-edit -->

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
