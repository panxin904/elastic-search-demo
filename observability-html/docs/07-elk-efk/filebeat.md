---
title: Filebeat 轻量日志采集
date: 2026-08-15  # date-auto-injected
description: Elastic 官方的轻量采集器
---

# Filebeat 轻量日志采集

> **TL;DR**：Filebeat = **Elastic 官方的轻量日志采集器（Go 写，Go 替代了 Logstash shipper）**。**功能：tail 日志 → 解析 → 发送到 Elasticsearch / Logstash / Kafka**。**内置模块：system / nginx / mysql / kafka 等开箱即用**。**K8s 场景：DaemonSet 部署 + 自动发现容器日志**。

## 一句话定义

```
Filebeat = Elastic 官方轻量日志采集器
        = Go 写，资源占用低（< 50MB 内存）
        = 设计：Prospector（发现日志文件）+ Harvester（采集行）+ Spooler（缓冲）
        = 替代 Logstash 做 shipper（Logstash 退居 filter/aggregation）
```

## 架构

```
┌──────────────────────────────────────┐
│  Filebeat                            │
│  ┌────────────────┐  ┌────────────┐  │
│  │ Prospector     │→ │ Harvester  │  │
│  │  监控目录       │  │ 读新行      │  │
│  └────────────────┘  └─────┬──────┘  │
│                            │         │
│                     ┌──────▼──────┐  │
│                     │ Spooler     │  │
│                     │ (缓冲)      │  │
│                     └──────┬──────┘  │
│                            │         │
│                     ┌──────▼──────┐  │
│                     │ Output      │  │
│                     │ (ES/Logstash│  │
│                     └─────────────┘  │
└──────────────────────────────────────┘
```

## 配置示例

```yaml
# filebeat.yml
filebeat.inputs:
  # 1. 通用日志输入
  - type: log
    enabled: true
    paths:
      - /var/log/app/*.log
    parsers:
      - ndjson:
          target: ""
          overwrite_keys: true
          add_error_key: true
    fields:
      env: prod
      service: order-api
    fields_under_root: true

  # 2. 容器日志（K8s 场景）
  - type: container
    enabled: true
    paths:
      - /var/log/containers/*.log
    json.keys_under_root: true
    json.add_error_key: true
    json.message_key: log

filebeat.config.modules:
  path: ${path.config}/modules.d/*.yml
  reload.enabled: true

processors:
  - add_host_metadata: ~
  - add_cloud_metadata: ~
  - add_kubernetes_metadata: ~   # K8s 元数据

output.elasticsearch:
  hosts: ["https://elasticsearch:9200"]
  username: "filebeat_writer"
  password: "${ES_PASSWORD}"
  index: "app-logs-%{+yyyy.MM.dd}"
  ssl.certificate_authorities: ["/etc/ca.crt"]
  pipeline: "app-logs-pipeline"

setup.template.name: "app-logs"
setup.template.pattern: "app-logs-*"
setup.ilm.enabled: true
setup.ilm.policy: "logs-lifecycle"

logging.level: info
```

## 内置模块（开箱即用）

```bash
# 启用模块
filebeat modules enable system nginx mysql redis kafka

# 模块目录：/etc/filebeat/modules.d/
# - system.yml: 系统日志（syslog / auth.log）
# - nginx.yml: nginx access / error log
# - mysql.yml: mysql slow log / error log
# - redis.yml: redis slowlog
# - kafka.yml: kafka server log
# - elasticsearch.yml: ES server log
```

## K8s 部署

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: filebeat
  namespace: kube-system
spec:
  template:
    spec:
      serviceAccountName: filebeat
      containers:
        - name: filebeat
          image: docker.elastic.co/beats/filebeat:8.13.0
          args:
            - "-c"
            - "/etc/filebeat.yml"
            - "-e"
          env:
            - name: ES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: elastic-credentials
                  key: password
          volumeMounts:
            - name: config
              mountPath: /etc/filebeat.yml
              subPath: filebeat.yml
            - name: data
              mountPath: /var/lib/filebeat-data
            - name: varlog
              mountPath: /var/log
            - name: varlibdockercontainers
              mountPath: /var/lib/docker/containers
              readOnly: true
      volumes:
        - name: config
          configMap:
            name: filebeat-config
        - name: data
          hostPath: { path: /var/lib/filebeat-data, type: DirectoryOrCreate }
        - name: varlog
          hostPath: { path: /var/log }
        - name: varlibdockercontainers
          hostPath: { path: /var/lib/docker/containers }
```

## Filebeat vs Fluent Bit

| 维度 | Filebeat | Fluent Bit |
|---|---|---|
| 内存 | 30-50MB | 5-10MB |
| 插件 | 30+（少） | 70+ |
| 模板化 | 内置模块丰富 | 需要自定义 |
| K8s 集成 | 完善（官方支持） | 完善 |
| 学习曲线 | 低 | 中 |

## 一句话总结

> **Filebeat = Elastic 官方轻量采集器**。**内置模块开箱即用**。**K8s DaemonSet 部署 + 自动发现容器日志**。

---

## 关联章节

- [ES 日志存储](./elasticsearch-logs.md)
- [Kibana](./kibana.md)
- [Fluentd](./fluentd.md)
- [K8s 监控](../11-scenarios/k8s-monitor.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
