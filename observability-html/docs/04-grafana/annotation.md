---
title: Grafana Annotation
description: 时间轴标记 / 部署事件 / 告警叠加
---

# Grafana Annotation

> **TL;DR**：Annotation = **Dashboard 时间轴上的事件标记**（如部署 / 告警 / 提交）。**两层叠加：内建（来自数据源告警）+ 自定义（来自 Grafana API / Prometheus deploy webhook）**。**实战：在 trace 上看部署时间点，定位"是不是这次上线出的问题"**。

## 一句话定义

```
Annotation = Dashboard 上时间轴的"事件标记"
           = 竖线 + 标签，标记关键时刻
           = 内建：来自 Grafana Alerting / 数据源告警
           = 自定义：来自外部 webhook / API
```

## 内建 Annotation

```
Grafana 自动从以下来源获取 annotations：
  1. Alerting：触发 / 解决的告警
  2. Dashboard URL：手动添加（按住 Ctrl 拖动）
  3. 数据源查询（query 类型）

每种类型用不同颜色区分
```

## 自定义 Annotation（最常用）

### 1. 通过 Grafana HTTP API

```bash
# 添加 deployment annotation
curl -X POST http://admin:[email protected]/api/annotations   -H "Content-Type: application/json"   -d '{
    "dashboardId": 1,
    "panelId": 1,
    "time": 1723219200000,
    "tags": ["deploy", "prod"],
    "text": "v2.3.1 deployed (PR #1234)"
  }'
```

### 2. 部署时自动添加（CI/CD 集成）

```yaml
# GitHub Actions 示例
- name: Add deploy annotation
  run: |
    curl -X POST "$GRAFANA_URL/api/annotations"       -H "Authorization: Bearer $GRAFANA_TOKEN"       -H "Content-Type: application/json"       -d '{
        "dashboardId": 1,
        "time": $(date +%s)000,
        "tags": ["deploy", "${{ github.event.repository.name }}"],
        "text": "Deploy ${{ github.sha }} by ${{ github.actor }}"
      }'
```

### 3. 从 Prometheus 拉取（query 类型）

```yaml
# Grafana Dashboard JSON
annotations:
  list:
    - name: deploys
      datasource: Prometheus
      iconColor: blue
      enable: true
      query:
        - 'ALERTS{alertstate="firing",severity="critical"}'
      tagKeys: "alertname,severity"
      titleFormat: "{{alertname}}"
```

## 实战案例：trace + deploy 联动

```
场景：15:00 发现错误率突增，需要判断是否与 14:55 的部署相关

步骤：
  1. 打开 Grafana Dashboard（订单服务）
  2. 时间窗口：14:30 ~ 15:30
  3. 在 dashboard 上看到 14:55 有一条 annotation（v2.3.1 部署）
  4. 错误率从 14:58 开始飙升 → 时间相关
  5. 结论：v2.3.1 引入的 bug，触发回滚

没有 annotation：
  - 需要手动 grep 部署日志
  - 需要问运维 / 同事
  - 排查时间长 5-10 分钟
```

## Annotation Tags 最佳实践

```
常用标签：
  - deploy: 部署事件
  - config-change: 配置变更
  - alert: 告警
  - incident: 故障
  - release: 版本发布
  - maintenance: 维护窗口

颜色编码（iconColor）：
  - red: 严重事件
  - orange: 警告
  - yellow: 注意
  - green: 成功
  - blue: 信息
```

## 一句话总结

> **Annotation = 时间轴事件标记**。**部署时通过 API 自动添加**。**Trace / 错误率 / 告警叠加 = 故障定位 1 步到位**。

---

## 关联章节

- [Dashboard 设计](../04-grafana/dashboard.md)
- [Grafana 概览](../04-grafana/overview.md)
- [Alertmanager](../08-alerting/alertmanager.md)

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
