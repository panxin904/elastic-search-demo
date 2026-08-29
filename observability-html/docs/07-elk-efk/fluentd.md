---
title: Fluentd 日志采集
date: 2026-08-15  # date-auto-injected
description: CNCF 毕业的统一日志层
---

# Fluentd 日志采集

> **TL;DR**：Fluentd = **CNCF 毕业的统一日志采集层**（2019）**。**类比 Logstash，但更轻量（Ruby 写）**。**核心架构：Input → Filter → Output（pipeline plugin）**。**生态丰富：1000+ 插件（源 + 过滤 + 输出）**。**K8s 场景：Fluent Bit（轻量版，Go 写）**。

## 一句话定义

```
Fluentd = CNCF 毕业的统一日志采集器
       = Ruby 写（C 扩展加速），基于 jemalloc
       = 设计：Input → Filter → Output pipeline
       = 插件架构：1000+ 插件（Source / Filter / Output）
       = 轻量版：Fluent Bit（Go 写，CNCF 子项目）
```

## 与 Filebeat / Logstash 对比

| 维度 | Fluentd | Fluent Bit | Filebeat | Logstash |
|---|---|---|---|---|
| 语言 | Ruby + C | Go + C | Go | JRuby |
| 内存 | 40-60MB | 5-10MB | 30-50MB | 200-500MB |
| 插件 | 1000+ | 70+ | 30+ | 200+ |
| 解析能力 | 强（filter DSL） | 中 | 弱 | 极强（grok） |
| 路由能力 | 极强（match + rewrite） | 中 | 弱 | 强 |
| 适用 | 复杂路由 | K8s sidecar / DaemonSet | 简单日志采集 | ELK 重度处理 |

## 架构

```
Input Plugin → Buffer → Filter Plugin → Buffer → Output Plugin
   (tail)       chunk    (parse/regex)    chunk    (ES/S3/HTTP)
                          (geoip enrich)
                          (record_transform)
```

## 配置示例

```ruby
# /etc/fluent/fluent.conf
<source>
  @type tail
  path /var/log/app/*.log
  pos_file /var/log/fluentd.pos
  tag app.logs
  <parse>
    @type json
    time_key timestamp
    time_format %Y-%m-%dT%H:%M:%S.%LZ
  </parse>
</source>

<filter app.logs>
  @type record_transformer
  enable_ruby true
  <record>
    hostname ${hostname}
    env "prod"
  </record>
</filter>

<filter app.logs>
  @type grep
  <regexp>
    key level
    pattern /^(error|warn|info)$/
  </regexp>
</filter>

<match app.logs>
  @type elasticsearch
  host elasticsearch
  port 9200
  index_name app-logs-${tag[1]}-%Y.%m.%d
  flush_interval 10s
  buffer_type file
  buffer_path /var/log/fluentd/buffer
  retry_max_times 5
</match>
```

## K8s 部署（Fluent Bit）

```yaml
# DaemonSet：每个 K8s 节点一份
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluent-bit
spec:
  template:
    spec:
      containers:
        - name: fluent-bit
          image: fluent/fluent-bit:2.2
          volumeMounts:
            - name: varlog
              mountPath: /var/log
            - name: varlibdockercontainers
              mountPath: /var/lib/docker/containers
              readOnly: true
            - name: fluent-bit-config
              mountPath: /fluent-bit/etc/
      volumes:
        - name: varlog
          hostPath: { path: /var/log }
        - name: varlibdockercontainers
          hostPath: { path: /var/lib/docker/containers }
        - name: fluent-bit-config
          configMap:
            name: fluent-bit-config
```

```ini
# fluent-bit ConfigMap
[INPUT]
    Name              tail
    Path              /var/log/containers/*.log
    Parser            docker
    Tag               kube.*
    Refresh_Interval  5

[FILTER]
    Name              kubernetes
    Match             kube.*
    Kube_URL          https://kubernetes.default.svc:443
    Kube_CA_File      /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    Kube_Token_File   /var/run/secrets/kubernetes.io/serviceaccount/token
    Merge_Log         On
    Merge_Log_Key     log_processed

[OUTPUT]
    Name              loki
    Match             *
    Host              loki
    Port              3100
    Labels            job=fluent-bit,k8s_namespace_name=$kubernetes['namespace_name']
```

## 一句话总结

> **Fluentd = CNCF 统一日志层**。**Fluent Bit（Go 轻量版）= K8s sidecar / DaemonSet 首选**。**复杂场景用 Fluentd（强大 filter DSL）**。

---

## 关联章节

- [ES 日志存储](./elasticsearch-logs.md)
- [Kibana](./kibana.md)
- [Filebeat](./filebeat.md)
- [K8s 监控](../11-scenarios/k8s-monitor.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
