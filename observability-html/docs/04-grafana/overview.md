---
title: Grafana 概览
description: 数据源 / Dashboard / 告警
---

# Grafana 概览

> **TL;DR**：Grafana = **业界标准的可视化平台**，**支持 30+ 数据源**（Prometheus / Loki / Elasticsearch / InfluxDB / MySQL / PostgreSQL / Tempo / Jaeger）。**核心功能：Dashboard（看板）+ Explore（临时查询）+ Alerting（告警）+ Unified Alerting**。**新项目标配：Grafana + Prometheus + Loki + Tempo = 全栈可观测**。

## 一句话定义

```
Grafana = 开源可视化 + 分析平台
       = 2014 Torkel Ödegaard 创立
       = Grafana Labs 维护（Grafana / Loki / Tempo / Mimir / Pyroscope）
       = 核心：数据源抽象 + Dashboard 模板化 + 多租户
```

## 核心组件

### 1. 数据源（Data Source）

```
支持的 30+ 数据源（部分）：
  - Prometheus / Loki / Tempo（原生三件套）
  - Elasticsearch（ELK）
  - InfluxDB / TimescaleDB（时序数据库）
  - MySQL / PostgreSQL / MSSQL（关系数据库）
  - CloudWatch / Azure Monitor / GCP Monitoring（云厂商）
  - Jaeger / Zipkin（tracing）
  - Pyroscope（profiling）

每种数据源有独立的 query editor：
  - Prometheus: PromQL 编辑器 + 自动补全
  - Loki: LogQL 编辑器 + 标签选择
  - Elasticsearch: KQL / Lucene
```

### 2. Dashboard

```
Dashboard = 多个 Panel 的组合（JSON 格式）
         = 支持变量（Variables）做联动
         = 支持 drilldown（点击 panel 跳到 detail）
         = 支持时间范围（全局 + 每 panel 覆盖）

最佳实践：
  - 一个服务一个 dashboard
  - 用 input controls 联动
  - dashboard JSON 可 git 版本控制
  - 用 templating 做复用
```

### 3. Explore

```
Explore = 临时查询模式
       = 不需要保存 dashboard
       = 适合临时调试 / ad-hoc 查询
       = 支持 split view（同时查多个数据源）

用法：Explore → 选数据源 → 写 PromQL/LogQL → Run
```

### 4. Unified Alerting

```
Grafana 8+ 内置告警引擎：
  - Alert rules：基于查询的告警规则
  - Contact points：Slack / Email / PagerDuty / Webhook
  - Notification policies：路由 / 抑制 / 静默
  - Silences：手动静默告警

优势：
  - 一个 UI 管理所有数据源告警
  - 不依赖 Alertmanager
  - 支持多租户
```

## 安装与配置

```bash
# Docker 单机启动
docker run -d --name grafana   -p 3000:3000   -v grafana-data:/var/lib/grafana   grafana/grafana:latest
```

```yaml
# docker-compose（生产）
version: '3'
services:
  grafana:
    image: grafana/grafana:10.4.0
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana.ini:/etc/grafana/grafana.ini
      - ./provisioning:/etc/grafana/provisioning
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GF_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
```

```ini
# grafana.ini（关键配置）
[server]
http_port = 3000
domain = grafana.example.com
root_url = https://grafana.example.com

[security]
admin_user = admin
admin_password = ${GF_PASSWORD}

[users]
allow_sign_up = false

[auth.anonymous]
enabled = false

[smtp]
enabled = true
host = smtp.example.com:587
user = [email protected]
password = ${SMTP_PASSWORD}
```

## 实战案例：Grafana + Prometheus + Loki

```yaml
# Grafana provisioning 自动配数据源
# /etc/grafana/provisioning/datasources/datasources.yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    isDefault: true

  - name: Loki
    type: loki
    url: http://loki:3100

  - name: Tempo
    type: tempo
    url: http://tempo:3200
```

## 权限与多租户

```
Grafana 多租户模型：
  - Org 组织（顶层隔离单位）
  - Team 团队（组织内）
  - Folder 文件夹（dashboard 分组）
  - Role 角色（Admin / Editor / Viewer）
  - Permission 权限（Edit / View）

最佳实践：
  - 团队 dashboard 放在 team folder
  - 全公司 dashboard 放 General folder
  - 生产环境数据源用 Viewer 角色
```

## 一句话总结

> **Grafana = 数据源无关的可视化平台**。**支持 30+ 数据源**。**核心：Dashboard / Explore / Unified Alerting**。**新项目标配：Grafana + Prometheus + Loki + Tempo = 全栈可观测**。

---

## 关联章节

- [Dashboard 设计](../04-grafana/dashboard.md)
- [变量](../04-grafana/variables.md)
- [Grafana 告警](../04-grafana/alerting.md)
- [Annotation 注释](../04-grafana/annotation.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>


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
