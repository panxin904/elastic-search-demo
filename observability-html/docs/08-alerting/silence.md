---
title: 告警静默
description: Silence / 维护窗口 / 已知问题屏蔽
---

# 告警静默

> **TL;DR**：**Silence = 临时屏蔽特定告警**（维护窗口 / 已知问题 / 演练）。**Alertmanager + Grafana 都支持**。**关键：必须有到期时间 + matcher + 创建人**，**避免"永不过期"的 silence**。

## 一句话定义

```
Silence = 临时屏蔽告警规则匹配
       = 不会触发，不会通知
       = 但 PromQL 仍正常评估（只是不进 Alertmanager）
       = 用途：维护窗口 / 已知问题 / 故障演练 / 升级演练
```

## Alertmanager 静默（amtool）

```bash
# 1. 创建 silence（4 小时屏蔽，匹配 service=order, severity=warning）
amtool silence add   --alertmanager.url=http://alertmanager:9093   --comment "DB 升级维护窗口"   --start="2026-08-09 14:00:00"   --end="2026-08-09 18:00:00"   --matcher service=order   --matcher severity=warning

# 2. 查询 silence
amtool silence query   --alertmanager.url=http://alertmanager:9093

# 3. 提前结束 silence
amtool silence expire   --alertmanager.url=http://alertmanager:9093   <silence-id>
```

## Alertmanager UI 创建

```
1. 打开 http://alertmanager:9093/#/silences
2. 点击 "New Silence"
3. 设置 matcher（如 service=order, severity=critical）
4. 设置 start / end 时间
5. 填 comment / 创建人
6. Submit

UI 会显示所有 active / pending / expired silences
```

## Grafana 静默

```bash
# 通过 API 创建 silence
curl -X POST http://admin:[email protected]/api/v1/provisioning/alert/rules   -H "Content-Type: application/json"   -d '{
    "matchers": [
      {"name": "service", "value": "order"},
      {"name": "severity", "value": "warning"}
    ],
    "startsAt": "2026-08-09T14:00:00Z",
    "endsAt": "2026-08-09T18:00:00Z",
    "comment": "DB 升级",
    "createdBy": "ops-team"
  }'
```

## 实战场景

### 1. 计划维护窗口

```yaml
# 数据库迁移维护：周六 02:00 - 06:00
# 提前 1 周创建 silence
silence:
  matchers:
    - name: service
      value: db-migration
    - name: severity
      value: ~"warning|critical"   # 正则匹配
  time:
    start: "2026-08-15 02:00:00"
    end: "2026-08-15 06:00:00"
  comment: "DB 迁移维护（PRG-1234）"
  created_by: "alice"
```

### 2. 已知问题（带工单）

```yaml
silence:
  matchers:
    - name: alertname
      value: "HighMemoryUsage"
    - name: instance
      value: "web-3"
  time:
    start: "now"
    end: "now + 7d"     # 最多 7 天
  comment: "已知内存泄漏，JIRA-1234 处理中"
  created_by: "bob"
```

### 3. 演练

```yaml
silence:
  matchers:
    - name: severity
      value: "warning"
  time:
    start: "now"
    end: "now + 2h"
  comment: "2026 春季故障演练，warning 级别暂屏蔽"
  created_by: "sre-team"
```

## Silence 与 Inhibit 的区别

| 维度 | Silence | Inhibit |
|---|---|---|
| 触发 | 手动 / 定时 | 自动（更高 severity 触发） |
| 范围 | 任意 matcher | 关联告警（如 cluster 全挂 → 抑制该 cluster 其他） |
| 时间 | 有 end time | 实时 |
| 用途 | 维护 / 演练 / 已知问题 | 告警噪音减少（避免告警风暴） |
| 管理 | amtool / UI | alertmanager.yml |

## 一句话总结

> **Silence = 临时屏蔽告警**。**必须有 end time + matcher + 创建人 + comment**。**Alertmanager + Grafana 都支持**。

---

## 关联章节

- [Alertmanager](./alertmanager.md) — 告警如何路由
- [告警分级](./severity.md) — P0/P1/P2/P3
- [On-call](./oncall.md) — 值班文化

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
