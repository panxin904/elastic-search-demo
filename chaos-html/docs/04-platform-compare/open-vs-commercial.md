---
title: 开源 vs 商业（Gremlin）
---

# 开源 vs 商业（Gremlin）

## Gremlin 商业模式

**Gremlin 公司**：

- 2018 商业化 / 总部旧金山
- 创始人：Kolton Andrus（前 AWS Chaos Engineer）
- 累计融资：5500 万美元（B / C 轮）

**产品套餐**：

- **Free**：$0，10 个 Pod，单用户
- **Pro**：$5k/月（年付 $60k），500 Pod，5 用户
- **Enterprise**：$20k+/月（年付 $240k+），无限 Pod，无限用户
- **Self-Hosted Enterprise**：定制（年付 $500k+）

**典型客户**：

- Salesforce / Twilio / Datadog
- Atlassian / AMD / Credible
- Mailchimp / Zola / Remind

**Gremlin 独特优势**：

1. **SaaS 控制台**：Web UI（无 K8s YAML 基础也能用）
2. **故障类型最全**：12 大类 100+ 故障
3. **审批流**：实验需 manager 审批
4. **审计日志**：SOC2 / HIPAA / PCI-DSS 认证
5. **状态注入**：业务层故障（如「注入 30% 订单失败」）
6. **游戏日服务**：Gremlin 团队提供专业 Game Day 主持人

## Gremlin vs 开源对比

| 维度 | Chaos Mesh / Litmus | Gremlin |
|---|---|---|
| 成本 | $0 | $60k-$240k/年 |
| 数据合规 | 完全自托管 | 默认出境（可配 EU） |
| 故障覆盖 | 10-15 类 | 12 大类 100+ |
| 学习曲线 | 中（需 K8s） | 低（Web UI） |
| 审批流 | 需自建 | 内置 |
| 审计 | K8s audit | SOC2 内置 |
| 定制 | 高度灵活 | 黑盒 |

**Gremlin 劣势**：

1. **贵**：年付 $60k+（Pro）起步
2. **Agent 闭源**：故障逻辑在 Gremlin 私有二进制
3. **数据出境**：实验日志默认上传 Gremlin 云（GDPR 风险）
4. **耦合度高**：从 Pro 迁到自托管很困难（vendor lock-in）

**开源方案优势**：

1. **零成本**：免费
2. **数据不出境**：完全自托管
3. **可定制**：CRD + Go SDK 任意修改
4. **中文社区**：Chaos Mesh 中文文档完善

## 选型决策

**选 Gremlin**：

- 团队 < 5 SRE + 合规要求高
- 预算 > $50k/年
- 无 K8s 基础（需要 Web UI）
- 想要「游戏日」托管服务

**选开源（Chaos Mesh / Litmus）**：

- 团队技术强（K8s 熟练）
- 数据合规要求高（不出境）
- 预算紧张 / 开源文化
- 需要深度定制（修改故障逻辑）

**混合方案**：

- 内部实验：开源（成本低）
- 商业验证：Gremlin（专业服务）

**关键问题**：你买的不是工具，是「**让团队敢做混沌工程的能力**」。

- 如果团队技术强 + 自托管文化 → 开源
- 如果团队运维弱 + 合规压力大 → 商业

## 与其他站点关系

- **chaos/04-platform-compare/decision-tree**：选型决策树
- **observability**：监控集成
- **devops**：CI/CD 集成


## ## 实战案例

**Gremlin SaaS 实战**：Duo Security 用 Gremlin 跑了 5 年，发现 30+ 真实生产事故（S3 桶中断、Redis 集群故障、AKS 节点崩溃）。

**Steadybit 商业版**：德国 SAP/Siemens 用 Steadybit 做 SAP HANA 数据库故障演练，HA 切换时间从 5 分钟降到 1 分钟。

**Chaos Mesh 自研**：字节跳动基于 Chaos Mesh 二次开发，自研 Chaos Controller 支持 GPU 故障注入、Service Mesh 故障。

**AWS Fault Injection Service (FIS)**：AWS 一站式服务，集成 CloudWatch + X-Ray，无需自建控制面。


## ## 故障排查清单

1. 商业方案价格贵 → 比较 Gremlin / Steadybit / AWS FIS
2. 开源方案维护成本 → 选社区活跃度高的
3. 合规要求 → 金融行业优先商业方案
4. 跨云需求 → 商业方案更友好
5. 实验数据 → 商业方案有完整 dashboard
