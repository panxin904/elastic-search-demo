---
title: 游戏日（Game Day）总览
---

# 游戏日（Game Day）总览

## 游戏日定义

游戏日（Game Day）是**组织级混沌演练活动**：在受控环境下，跨团队协作模拟真实故障，验证系统韧性 + 团队应急能力。

**与单次混沌实验的区别**：

| 维度 | 单次混沌实验 | 游戏日 |
|---|---|---|
| 规模 | 单一服务 / 单一故障 | 多服务 / 多故障 / 多团队 |
| 时间 | 30 秒 - 5 分钟 | 2-8 小时 |
| 目的 | 验证韧性假设 | 验证应急流程 + 团队协作 |
| 参与 | SRE / 开发 | SRE + 开发 + PM + 客服 + 业务 |
| 输出 | 稳态 / 偏离 | 韧性报告 + 改进清单 |

**游戏日的核心价值**：

1. **验证架构假设**：文档上的架构 ≠ 真实行为
2. **暴露协调问题**：哪个团队先响应？沟通渠道是否畅通？
3. **训练应急肌肉记忆**：oncall 工程师在真实压力下表现
4. **建立混沌文化**：让「敢做实验」成为团队共识

**Netflix 起源**：

- 2011 年内部第一次 Game Day（Chaos Monkey 团队）
- 每年 1-2 次大型 Game Day + 每月小型
- 「混乱猴子会议」（Chaos Monkey Meetup）公开分享

**Amazon 实践**：

- 「GameDay Friday」：每周五 1 小时
- 团队自愿参与（无强制）
- 故障由「GameDay Master」（专门训练过的主持人）选择

**Google DiRT**（Disaster Recovery Testing）：

- 每年 1-2 次大型演练
- 「故障注入演习」（Fault Injection Exercise）
- 公开分享：Google SRE Book Chapter 22

## 游戏日设计

**游戏日设计 5 步法**：

**Step 1：确定演练目标**

- 示例：「验证大促期间 Region 故障时的应急能力」
- 目标要 SMART：Specific / Measurable / Achievable / Relevant / Time-bound

**Step 2：选择故障场景**

- 故障画像优先级（P × I 模型）
- 本季度 TOP 5 故障：
  - Redis 主从切换（高 P，高 I）
  - 支付网关超时（中 P，高 I）
  - 数据库慢查询（高 P，中 I）
  - CDN 节点失效（中 P，中 I）
  - Region 断网（低 P，极高 I）

**Step 3：设计爆炸半径**

- **L1 单测**（首次游戏日）：1 Pod / 1 实例 / 单 AZ / 5 分钟
- **L2 进阶**（成熟期）：10% 流量 / 1 AZ / 30 分钟
- **L3 全链路**（大促前）：跨 Region / 全量 / 2 小时

**Step 4：定义观察指标**

- **业务指标**：订单成功率 / GMV / 用户投诉
- **系统指标**：错误率 / P99 延迟 / 资源利用率
- **流程指标**：oncall 响应时间 / 决策时间 / 恢复时间

**Step 5：制定回滚预案**

- 自动化：SLO breach → 自动 kill chaos
- 手动化：指挥官红色按钮
- 沟通：Slack #chaos-game-day 频道 + PagerDuty
- 退出条件：业务影响 > 预期阈值（例：订单成功率跌至 90%）

**游戏日策划文档模板**（Netflix 公开）：

```yaml
game_day:
  title: "Q3 Game Day - Region Failover"
  date: 2024-09-15
  duration: 4h
  objective: "验证 us-east-1 故障时 us-west-2 接管能力"
  scenarios:
    - name: "Redis failover"
      type: chaos-mesh
      blast_radius: L2 (10% traffic)
      duration: 30min
      success_criteria:
        - "P99 latency < 1.5s"
        - "error rate < 1%"
    - name: "Network partition"
      type: chaos-mesh
      blast_radius: L2
      duration: 30min
      success_criteria:
        - "circuit breaker opens within 10s"
        - "fallback returns cached data"
  rollback_plan: "SLO breach → 自动 kill chaos + PagerDuty 通知"
  participants:
    - "SRE 团队"
    - "支付服务 oncall"
    - "订单服务 oncall"
    - "PM 业务代表"
```

## 角色分工

**核心角色（4-8 人）**：

**1. 指挥官（Game Master / Commander）**

- 主持游戏日
- 选择故障场景 + 决定爆炸半径
- 决定「继续 / 暂停 / 中止」
- **绝对权威**：业务影响超阈值 → 立即 kill chaos
- 通常是 SRE Lead 或资深 SRE

**2. 注入者（Injector）**

- 执行 chaos 命令（kubectl apply / ChaosBlade CLI）
- 监控 chaos 状态
- 与指挥官确认爆炸半径调整

**3. 观察员（Observer）**

- 监控 dashboard（Grafana / Kibana / Prometheus）
- 实时报告指标变化
- 不直接干预，只观察

**4. 记录员（Scribe）**

- 记录每个时间点的现象
- 录音 + 截图 + 时间线
- 后续输出 Postmortem 报告

**5. oncall 工程师（On-call Engineer）**

- 真实响应告警
- 不知道是演练（避免「演戏」）
- 测试真实应急流程

**6. 业务代表（Business Owner）**

- 监控业务指标（订单 / GMV）
- 决定是否「业务可接受」
- 通常是 PM 或业务总监

**7. 客服代表（Customer Support）**

- 监控用户投诉
- 测试客服应对流程（用户咨询「为什么下单失败」）

**8. 旁观者（Observer / Learner）**

- 团队成员学习
- 不直接参与，但可提问

**典型团队组成（中型公司）**：

- 指挥官 1 人
- 注入者 2 人
- 观察员 1 人
- 记录员 1 人
- oncall 工程师 3-5 人（不同服务）
- 业务代表 1 人
- 总计 8-12 人

## 注入流程

**典型游戏日时间线**（4 小时）：

```
00:00 - 00:30  准备会议
  ├─ 指挥官回顾目标 + 场景
  ├─ 角色分工确认
  ├─ 工具检查（chaos-mesh / dashboard）
  └─ 退出条件确认

00:30 - 01:00  暖场
  ├─ 介绍游戏日规则
  ├─ 强调「真实应急」原则
  └─ 确认沟通渠道（Slack / 电话）

01:00 - 02:30  场景 1（中等爆炸半径）
  ├─ 01:00 注入故障（注入者执行）
  ├─ 01:05 oncall 收到告警
  ├─ 01:10 oncall 开始诊断
  ├─ 01:30 oncall 提出假设 + 行动
  ├─ 01:45 指挥官决定是否继续 / 加大爆炸
  └─ 02:30 故障恢复（手动或自动）

02:30 - 02:45  休息 + 第一轮复盘（快速回顾）

02:45 - 03:45  场景 2（高爆炸半径）
  ├─ 同上流程，但爆炸半径更大
  └─ 测试「跨团队协调」

03:45 - 04:00  收尾
  ├─ 确认所有故障恢复
  ├─ 清理 chaos 资源
  └─ 通知「演练结束」

（次日）         正式复盘会
  ├─ 记录员报告时间线
  ├─ oncall 报告感受
  ├─ 业务代表评估影响
  ├─ 输出 Postmortem
  └─ 改进清单（Action Items）
```

**注入关键节奏**：

**1. 预注入（Pre-injection）**：

- 确认稳态（业务指标正常）
- 通知相关方「即将注入」

**2. 注入（Injection）**：

- 慢注入（30 秒逐步加大）vs 快注入（瞬时）
- 推荐慢注入：更接近真实故障

**3. 观察（Observe）**：

- 至少观察 2 × 检测时间
- 例：监控检测时间 1 分钟 → 观察至少 2 分钟

**4. 决策（Decide）**：

- 指挥官根据退出条件决定：继续 / 暂停 / 加大 / 中止

**5. 恢复（Recover）**：

- 手动恢复（注入者执行）
- 自动恢复（chaos duration 到期）

**6. 验证恢复（Verify Recovery）**：

- 业务指标回到稳态
- 记录恢复时间（RTO）

**退出条件（Exit Criteria）必设**：

- 示例：「订单成功率跌至 95% 以下 → 立即中止」
- 没有退出条件 = 灾难

## 复盘与改进

**复盘会（Postmortem）**：游戏日结束后 24-48 小时内召开。

**复盘会议程（90 分钟）**：

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

**Postmortem 文化（关键）**：

- **Blameless**（无指责）：聚焦「系统如何失败」而非「谁犯了错」
- **事实优先**：时间线 + 数据 + 截图
- **学习导向**：每个故障都是改进机会
- **公开分享**：跨团队学习

**改进清单跟踪**：

- Jira Epic：游戏日改进
- 每个 Action Item 是独立 Story
- Sprint Review 跟踪完成度

**游戏日报告模板**：

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
- ...

## 改进清单
1. [HIGH] 增加 fallback 数据的 staleness 标记
2. [MED] oncall Runbook 补充 Region 切换步骤
3. [LOW] chaos-dashboard 增加「指挥官视图」

## 经验教训
- 跨团队沟通顺畅
- Redis 切换时间过长（45 秒）
- fallback 数据无 staleness 标识
```

## 实战案例与文化

**Netflix 案例**（公开分享）：

- 每年 1-2 次大型 Game Day + 每月小型
- 「Chaos Kong」：模拟整个 AWS Region 故障
- 全员参与（含 CEO Reed Hastings）
- 失败经验写成「SRE 手册」开源

**Amazon 案例**：

- 「GameDay Friday」：每周五 1 小时
- 选故障由「GameDay Master」决定
- 「DiRT」（Disaster Recovery Testing）每年大型演练

**Google 案例**（SRE Book Chapter 22）：

- 「DiRT」（Disaster Recovery Testing）
- 「FireDrill」（小规模每月）
- 「Resilience Review」（项目交付前必做）

**阿里巴巴案例**：

- 「大促演练」：双 11 前 6 个月启动
- 每月 1-2 次「故障演练日」
- 跨 SRE / 开发 / 客服 / 业务
- 「全链路压测」+ 故障注入

**字节跳动案例**：

- 抖音 2023 春节活动前 Game Day
- 4 场大型演练 / 8 场小型
- 跨 20+ 服务团队参与

**关键文化要素**：

1. **管理层支持**：
   - CEO / CTO 必须支持「游戏日失败 ≠ 绩效考核扣分」
   - 否则团队会「演戏」（提前准备好应对）

2. **Blameless 文化**：
   - 故障 = 学习机会
   - 严禁「追责文化」

3. **频率渐进**：
   - 季度 1 次 → 月度 1 次 → 周度 1 次
   - 频率与成熟度正相关

4. **公开分享**：
   - 内部 Wiki / 公众号
   - 跨团队学习

5. **工具支撑**：
   - 标准化 chaos 平台（Chaos Mesh / Litmus）
   - 应急 Runbook 文档化
   - SLO Dashboard 统一

**常见失败模式**：

- 管理层不支持，团队演戏
- 没有退出条件，业务影响过大
- 复盘变成「追责会」
- 改进清单无跟踪，流于形式
- 频率太低（年 1 次），失去训练价值

**成熟度模型**：

| 级别 | 频率 | 规模 | 自动化 | 文化 |
|---|---|---|---|---|
| L1 起步 | 年 1 次 | 单团队 | 手动 | 高层驱动 |
| L2 形成 | 季度 1 次 | 3-5 团队 | 半自动 | SRE 主导 |
| L3 常规 | 月度 1 次 | 跨部门 | 自动 | 团队共识 |
| L4 持续 | 每周 | 全公司 | 持续运行 | 文化基因 |
| L5 自适应 | 实时 | 自适应 | AI 驱动 | 全员混沌思维 |

## 与其他站点的关系

- **devops**：游戏日纳入 CI/CD → 引用 devops/05-cicd-observability
- **observability**：稳态度量 → 引用 observability/03-prometheus
- **architecture**：应急 Runbook → 引用 architecture/05-microservices
- **design-pattern**：韧性模式验证 → 引用 design-pattern/05-architectural-patterns
- **system-design**：可用性原则演练 → 引用 system-design/08-availability

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 混沌
- [observability](https://java-px.bot.cd/observability/):故障注入监控
- [system-design](https://java-px.bot.cd/system-design/):系统韧性
