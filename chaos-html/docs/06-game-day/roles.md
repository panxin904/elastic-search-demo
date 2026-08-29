---
title: 角色分工
date: 2026-08-15  # date-auto-injected
---

# 角色分工

## 核心角色

**1. 指挥官（Game Master / Commander）**：

- 主持游戏日
- 选择故障场景 + 决定爆炸半径
- 决定「继续 / 暂停 / 中止」
- **绝对权威**：业务影响超阈值 → 立即 kill chaos

**2. 注入者（Injector）**：

- 执行 chaos 命令（kubectl apply / ChaosBlade CLI）
- 监控 chaos 状态
- 与指挥官确认爆炸半径调整

**3. 观察员（Observer）**：

- 监控 dashboard（Grafana / Kibana / Prometheus）
- 实时报告指标变化
- 不直接干预，只观察

**4. 记录员（Scribe）**：

- 记录每个时间点的现象
- 录音 + 截图 + 时间线
- 后续输出 Postmortem 报告

**5. oncall 工程师（On-call Engineer）**：

- 真实响应告警
- 不知道是演练（避免「演戏」）
- 测试真实应急流程

## 辅助角色

**6. 业务代表（Business Owner）**：

- 监控业务指标（订单 / GMV）
- 决定是否「业务可接受」

**7. 客服代表（Customer Support）**：

- 监控用户投诉
- 测试客服应对流程

**8. 旁观者（Observer / Learner）**：

- 团队成员学习
- 不直接参与，但可提问

## 典型团队组成

**中型公司（8-12 人）**：

- 指挥官 1 人
- 注入者 2 人
- 观察员 1 人
- 记录员 1 人
- oncall 工程师 3-5 人（不同服务）
- 业务代表 1 人
- 客服代表 1 人

**大型公司（15-20 人）**：

- 指挥官 1 人 + 副指挥官 1 人
- 注入者 3-4 人
- 观察员 2-3 人
- 记录员 1-2 人
- oncall 工程师 5-8 人（不同服务）
- 业务代表 2-3 人
- 客服代表 1 人
- 旁观者 3-5 人

**小型团队（4-6 人）**：

- 指挥官 1 人（兼任）
- 注入者 1 人
- 观察员 1 人
- oncall 工程师 1-2 人

## 角色职责矩阵

| 角色 | 故障注入 | 监控 | 决策 | 复盘 |
|---|---|---|---|---|
| 指挥官 | 审批 | 决策 | ✅ | 主持 |
| 注入者 | ✅ | 监控 | - | 参与 |
| 观察员 | - | ✅ | - | 参与 |
| 记录员 | - | 时间线 | - | ✅ |
| oncall | - | 监控 | 应急 | 反馈 |
| 业务代表 | - | 业务指标 | 业务决策 | 评估 |
| 客服代表 | - | 用户投诉 | - | 反馈 |

**职责分离原则**：

- 注入 ≠ 监控（避免利益冲突）
- 监控 ≠ 决策（避免「自导自演」）
- 决策 ≠ 应急（指挥官 vs oncall）

## 与其他站点关系

- **chaos/06-game-day/exercise-design**：演练设计
- **chaos/06-game-day/retro**：复盘改进
- **architecture/05-microservices**：oncall Runbook


## ## 实战案例

**Google DiRT 角色分工**：Incident Commander（决策）、 Communications Lead（对外）、 Operations Lead（执行）、 Scribe（记录）。

**阿里大促 Cmder**：专职 Cmder 组，平时训练有素，演练时全程不睡觉，做到 30s 完成决策。

**蚂蚁 On-Call**：On-Call 工程师必须 5 分钟内 ack，10 分钟内成立应急小组，30 分钟内通报。


## ## 故障排查清单

1. 角色混乱 → 演练前发 role card，每人贴桌上
2. 决策延误 → 提前给 Incident Commander 决策表
3. 沟通风暴 → Communications Lead 统一对外
4. 记录缺失 → Scribe 用时间轴模板
5. 复盘无主 → 提前指定 retro leader


<!-- auto-enrich:do-not-edit -->

## 实战示例

```bash
# TODO: 在此补充本页主题的实战命令
echo "hello"
```

```yaml
# TODO: 配置示例
key: value
```

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料
<!-- auto-enrich:do-not-edit -->
