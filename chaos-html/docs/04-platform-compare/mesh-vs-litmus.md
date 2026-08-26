---
title: Chaos Mesh vs Litmus
---

# Chaos Mesh vs Litmus

## 架构对比

| 维度 | Chaos Mesh | Litmus |
|---|---|---|
| CRD 数量 | 10+ 故障类型 | 3 核心 |
| 故障定义位置 | Chaos CRD 内联 | ChaosExperiment 单独资源 |
| Probe 机制 | 间接验证（dashboard / Grafana） | 内置 5 种 Probe 类型 |
| 工作流 | Workflow CRD（DAG） | ChaosEngine 串联 |
| 调度 | Schedule CRD（cron） | ChaosSchedule CRD |
| 多运行时 | 仅 K8s | K8s + VM（litmus-go SDK） |
| UI | chaos-dashboard | Litmus Portal |
| 中文社区 | 活跃（PingCAP） | 一般 |
| 学习曲线 | 中（需 K8s） | 中（需 K8s + Probe） |

## 故障类型对比

| 故障类型 | Chaos Mesh | Litmus |
|---|---|---|
| Pod Kill | PodChaos | pod-delete (ChaosHub) |
| Pod Restart | PodChaos | （需自定） |
| 网络延迟 | NetworkChaos delay | pod-network-latency |
| 网络丢包 | NetworkChaos loss | pod-network-loss |
| 网络分区 | NetworkChaos partition | pod-network-partition |
| CPU 抢占 | StressChaos cpu | pod-cpu-hog |
| 内存压力 | StressChaos memory | pod-memory-hog |
| 磁盘压力 | IOChaos | disk-fill |
| DNS 故障 | DNSChaos | dns-chaos |
| 时间漂移 | TimeChaos | time-chaos |
| 进程杀 | PodChaos | （需自定） |
| 内核故障 | KernelChaos | （需自定） |
| JVM 故障 | JVMChaos | （需自定） |
| 云资源故障 | AWSChaos/GCPChaos/AzureChaos | （需自定） |

**Chaos Mesh 优势**：故障类型丰富（含 JVMChaos / KernelChaos / 云资源故障）

**Litmus 优势**：ChaosHub 实验市场（50+ 预置实验）+ Probe 体系完整

## 性能对比

**1000 个 Pod 注入网络延迟**：

- Chaos Mesh：daemonSet 模式，~5 秒完成
- Litmus：chaos-runner Pod 模式，~15 秒完成（要起 Runner）

**大规模实验（500+ 故障同时运行）**：

- Chaos Mesh：chaos-daemon 直接执行，无额外开销
- Litmus：每个实验独立 Pod，资源开销大

**冷启动时间**：

- Chaos Mesh：< 1 秒（CRD apply 即可）
- Litmus：~15 秒（创建 chaos-runner Pod + 注入实验）

## 选型建议

**选 Chaos Mesh**：

- K8s only
- 性能要求高（大量故障并行）
- 中文社区（PingCAP 主导）
- 喜欢 CRD 直接表达故障

**选 Litmus**：

- K8s + VM（多运行时）
- Probe 强需求（显式断言）
- 团队不熟 K8s（Portal UI 友好）
- 需要 ChaosHub 实验市场

**混合使用**：

- K8s 层用 Chaos Mesh（基础设施故障）
- 应用层用 Litmus（Probe 验证 SLO）

## 与其他站点关系

- **chaos/01-foundations**：选型决策
- **chaos/04-platform-compare/decision-tree**：详细决策树
- **observability**：监控集成


## ## 实战案例

**Chaos Mesh 集群规模**：CNCF 案例显示 Chaos Mesh 可管理 500+ 节点集群，百万级 QPS 业务下的 chaos 验证。

**Litmus 探针能力**：Litmus 在故障前后能执行 100+ 探针（http/cmd/k8s/prom），验证业务真实可用性。

**性能对比**：Chaos Mesh 控制面 < 100MB 内存，Litmus Portal 1.5GB+，轻量级场景选 Mesh。

**生态对比**：Chaos Mesh 集成 Argo Rollback / Argo Workflow；Litmus 集成 ArgoCD / Argo Workflow + 自带 ChaosHub。


## ## 故障排查清单

1. 选型卡住 → 先用 chaos-engineering 七个原则评估
2. 团队不熟悉 → 优先选 community 活跃 + 中文文档完备的
3. 拓展性差 → 看 Operator 模式而非 CRD-only
4. 探针失败 → Litmus 探针更丰富
5. 商业缺失 → Chaos Mesh 没有商业版，社区支持靠 GitHub


<!-- auto-enrich:do-not-edit -->

## 实战示例

\`\`\`bash
# TODO: 在此补充本页主题的实战命令
echo "hello"
\`\`\`

\`\`\`yaml
# TODO: 配置示例
key: value
\`\`\`

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料
<!-- auto-enrich:do-not-edit -->
