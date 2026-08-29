---
title: 选型决策树
date: 2026-08-15  # date-auto-injected
---

# 选型决策树

## 5 步选型法

**Step 1：你的运行时是什么？**

- **仅 K8s** → Chaos Mesh 或 Litmus（两大开源主力）
- **K8s + VM** → Litmus / Gremlin / ChaosBlade（多运行时支持）
- **VM + Host**（传统数据中心） → Gremlin / ChaosBlade（覆盖宿主机）
- **多云**（AWS/GCP/Azure） → Gremlin / Steadybit / 云厂商原生命令

**Step 2：你的预算？**

- **$0**（开源） → Chaos Mesh / Litmus / ChaosBlade
- **$5k-50k/年**（商业） → Gremlin（Pro 套餐）
- **$100k+/年**（企业） → Steadybit / Gremlin Enterprise

**Step 3：你的团队规模？**

- **3 人以下**：Chaos Mesh（CRD 直接 kubectl，UI 可选）
- **5-10 人**：Litmus（Portal UI + 共享实验库）
- **20 人以上**：Gremlin（权限管理 + 审批流 + 审计）

**Step 4：你的合规要求？**

- **PCI-DSS / HIPAA**：Gremlin（审计日志完整）/ Steadybit（SOC2）
- **GDPR**：开源（数据不出公司）/ Gremlin Enterprise（EU 数据中心）

**Step 5：你的实验类型？**

- **基础设施层**（Pod/Node/Network） → Chaos Mesh / Litmus / ChaosBlade 都能
- **应用层**（HTTP/SQL/缓存） → Litmus Probe 最强
- **业务层**（订单/支付） → Litmus 自定义 Probe + 业务指标

## 典型选型示例

**示例 1：互联网初创公司（50 人）**：

- 运行时：仅 K8s（EKS）
- 预算：$0
- 团队：3 SRE
- 合规：无特殊要求
- 实验：Pod kill / 网络延迟
- **推荐**：Chaos Mesh

**示例 2：金融科技公司（200 人）**：

- 运行时：K8s + 传统 VM
- 预算：$50k/年
- 团队：8 SRE + 4 DevOps
- 合规：PCI-DSS
- 实验：Pod kill / Redis failover / 业务层故障
- **推荐**：Litmus + Gremlin Pro 混合

**示例 3：传统银行（5000 人）**：

- 运行时：多云 + 私有数据中心
- 预算：$200k+/年
- 团队：30+ SRE
- 合规：SOC2 + GDPR + 银保监
- 实验：跨 Region 故障转移 / 数据库主从切换
- **推荐**：Gremlin Enterprise + Steadybit

**示例 4：电商大促准备**：

- 运行时：阿里云（K8s）
- 预算：$20k/年
- 团队：10 SRE
- 合规：等保三级
- 实验：JVM 故障 / 流量调度 / 多活切换
- **推荐**：ChaosBlade + AHAS（阿里云）

## 与其他站点关系

- **chaos/04-platform-compare/mesh-vs-litmus**：深度对比
- **chaos/04-platform-compare/open-vs-commercial**：商业模式对比
- **observability**：监控集成对比


## ## 实战案例

**金融行业选型**：银行场景下，Gremlin / Steadybit 的合规审计能力更强 → 选商业方案；互联网公司 → Chaos Mesh。

**制造业 K8s 改造**：制造业 K8s 集群 < 100 节点 → ChaosBlade 轻量级；> 100 节点 + 多集群 → Chaos Mesh。

**GPU 集群场景**：AI 训练集群需要 StressChaos（GPU 注入）→ 选 Chaos Mesh；纯 RDBMS 集群 → Litmus。


## ## 故障排查清单

1. 选型矛盾 → 列出 3 个不可妥协的需求作为 hard constraint
2. 维护成本失控 → 评估团队 K8s 能力
3. 实验跑不通 → 检查目标集群连通性 + RBAC
4. 商业方案价格贵 → 谈判 SLA 等级 + 用户数
5. 切换工具 → 预留 3 个月过渡期


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
<!-- auto-enrich:do-not-edit -->
