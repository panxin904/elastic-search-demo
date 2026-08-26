---
title: 复盘与改进
---

# 复盘与改进

## Postmortem 文化

**Blameless（无指责）原则**：

- 聚焦「系统如何失败」而非「谁犯了错」
- 故障 = 学习机会
- 严禁「追责文化」

**事实优先**：

- 时间线 + 数据 + 截图
- 不猜测、不臆断、不甩锅

**学习导向**：

- 每个故障都是改进机会
- 输出 Action Items（不是抱怨）

**公开分享**：

- 内部 Wiki / 公众号
- 跨团队学习

## 复盘会议程（90 分钟）

```
00:00 - 00:15  时间线回放（记录员主导）
  ├─ 投影时间线
  ├─ 每个关键节点：发生了什么 + 谁响应了 + 决策是什么
  └─ 客观陈述（无指责）

00:15 - 00:45  oncall 感受分享
  ├─ oncall A：「收到告警后我以为是真的，10 分钟才发现是演练」
  ├─ oncall B：「诊断假设走错了 2 次方向，浪费了 15 分钟」
  └─ 指挥官：「我在 30 分钟时本应中止但没有，导致影响扩大」

00:45 - 01:15  改进清单（Action Items）
  ├─ 监控：增加订单成功率 SLO dashboard
  ├─ 流程：oncall 收到告警后 5 分钟无人工响应 → 自动 page backup
  ├─ 文档：应急 Runbook 缺失 Redis failover 步骤
  ├─ 架构：payment-service 缺少 bulkhead 隔离
  └─ 工具：chaos-dashboard 增加「指挥官视图」

01:15 - 01:30  责任分配
  ├─ 每条 Action Item 指定：负责人 + 截止日期 + 验证标准
  └─ 写入 Jira / Linear
```

## Action Items 跟踪

**Jira Epic 模板**：

```
Epic: Game Day 改进 Q3-2024
├── [HIGH] STORY-101: 增加订单成功率 SLO dashboard
│   ├─ 负责人：张三（SRE）
│   ├─ 截止：2024-10-15
│   └─ 验证：dashboard 显示成功率 + 告警配置
├── [MED] STORY-102: 应急 Runbook 补充 Region 切换步骤
│   ├─ 负责人：李四（SRE）
│   ├─ 截止：2024-10-30
│   └─ 验证：Runbook 通过 Game Day 演练
└── [LOW] STORY-103: chaos-dashboard 增加「指挥官视图」
    ├─ 负责人：王五（前端）
    ├─ 截止：2024-11-15
    └─ 验证：截图 + 演练使用反馈
```

**Sprint Review 跟踪**：

- 每 Sprint Review 汇报 Action Items 完成度
- 未完成项说明原因 + 调整截止日期
- 累积 3 个未完成 → 升级到管理层

## 游戏日报告模板

```markdown
# Q3 Game Day 报告

## 元数据
- 日期：2024-09-15
- 主题：Region Failover 演练
- 参与者：12 人
- 指挥官：张三（SRE Lead）

## 目标
- 验证 us-east-1 故障时 us-west-2 接管能力

## 场景
1. Redis 主从切换（30min）
2. 跨 Region 网络分区（30min）

## 结果
- 场景 1：通过（P99 < 1.2s，错误率 < 0.5%）
- 场景 2：部分通过（circuit breaker 10s 内打开，但 fallback 返回过期数据）

## 时间线
- 13:00 注入故障
- 13:05 oncall 告警
- 13:10 开始诊断

## 改进清单
1. [HIGH] 增加 fallback 数据的 staleness 标记
2. [MED] oncall Runbook 补充 Region 切换步骤
3. [LOW] chaos-dashboard 增加「指挥官视图」

## 经验教训
- 跨团队沟通顺畅
- Redis 切换时间过长（45 秒）
- fallback 数据无 staleness 标识
```

## 与其他站点关系

- **chaos/06-game-day/exercise-design**：演练设计
- **chaos/06-game-day/roles**：角色分工
- **devops/06-best-practices**：Postmortem 流程


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

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
