---
title: 混沌工程基础总览
---

# 混沌工程基础总览

## 什么是混沌工程


混沌工程（Chaos Engineering）是在生产环境或类生产环境中，**主动注入可控故障**来验证系统韧性的工程实践。
它不是「破坏测试」（break things），也不是「故障演练」（drill）的同义词，而是一套**有方法论、有工具、有度量的科学实验体系**。

2010 年 Netflix 的云架构迁移催生了 Chaos Monkey，2012 年公开后引发业界跟进；2014 年 Netflix 推出 Simian Army（Chaos Gorilla / Chaos Kong 等），2015 年 Principles of Chaos 白皮书发布，
2020 年 Gremlin 完成 C 轮融资（2950 万美元），2021 年 Chaos Mesh 进入 CNCF Sandbox，2023 年晋升 Incubating，2024 年毕业（Graduated），
标志着混沌工程从「Netflix 内部工具」走向「CNCF 主流可观测性+韧性体系」。

**与相似概念区分**：
- **故障演练（Drill）**：偏向流程（火灾逃生、机房断电），不深入系统行为
- **渗透测试（Pen Test）**：偏向安全（攻防），不涉及基础设施韧性
- **压力测试（Stress Test）**：偏向性能（高负载），不涉及故障模拟
- **故障注入（Fault Injection）**：偏向技术（注入字节错误），不涉及系统级实验设计

混沌工程的核心是「**实验假设 + 稳态度量 + 最小爆炸半径 + 自动化持续运行**」四要素。


## 四大原则（Principles of Chaos）


Principles of Chaos 白皮书 2015 提出四大原则：

**1. 建立围绕稳态的假设（Build a Hypothesis around Steady-State Behavior）**
- 不是「注入 Redis 故障」，而是「**如果 Redis 主从切换延迟 > 500ms，订单服务的 5xx 错误率应在 30 秒内恢复 < 0.1%**」
- 稳态是可度量的（订单成功率 / 端到端延迟 / 队列积压深度）

**2. 多样化真实事件（Vary Real-world Events）**
- 故障画像（Failure Mode Catalog）：进程崩溃 / 磁盘 IO 抖动 / 网络分区 / DNS 解析失败 / 证书过期 / 时钟漂移 / 资源耗尽
- 优先级：发生频率 × 业务影响（如「Pod 抢占」在 K8s 中频率 > 100 次/月）

**3. 在生产环境运行实验（Run Experiments in Production）**
- 预生产环境「一切正常」（资源充足 / 网络稳定），无法暴露真实缺陷
- 黄金路径：「**预生产 50% → 金丝雀 5% → 全量 100%**」逐步提升爆炸半径

**4. 自动化持续运行（Automate Experiments to Run Continuously）**
- 一次性实验无价值：每周 Netflix 自动跑 Chaos Monkey，每天 Stripe 跑 200+ 故障实验
- 与 CI/CD 集成：PR 合并 → 灰度 → 混沌实验 → 指标对比 → 自动回滚

**四大原则的工程意义**：从「手动 fire drill」走向「**持续韧性验证**」（Continuous Resilience Validation）。


## 稳态假设（Steady-State Hypothesis）


稳态是混沌实验的「**对照组**」。没有稳态，实验结果无法解读。

**定义稳态三步法**：

**步骤 1：识别关键业务指标（KBI）**
- 电商：订单成功率（≥ 99.5%）/ 支付成功率 / 端到端 P99 延迟
- 视频：缓冲率 / 卡顿率 / 首帧时间
- 金融：交易成功率 / 清算时效

**步骤 2：转化为系统级可观测指标**
- 业务指标 → 客户端 → 网关 → 服务 → 存储的可观测链路
- 订单成功率下降 → 网关 5xx → 订单服务超时 → 数据库连接池耗尽
- 每个系统级指标都要有**基线值**（过去 7 天 / 30 天的 P95 / P99）

**步骤 3：定义稳态区间**
- 不是单点值，而是「区间 + 时间窗口」
- 示例：订单成功率稳态 = [99.5%, 99.9%]，持续时间 ≥ 5 分钟
- 超出区间 = 系统进入「非常态」= 实验「破坏了稳态」

**常见误区**：
- ❌ 用 CPU 使用率做稳态（资源利用率 ≠ 用户体验）
- ❌ 用瞬时值（每秒成功率波动 0.5% 正常）
- ✅ 用「**SLO 维度的滑动窗口**」（如 5 分钟成功率）


## 爆炸半径（Blast Radius）


爆炸半径是「**实验失败时的最大影响范围**」。混沌工程的核心伦理是「**实验失败不能比不实验更糟**」。

**爆炸半径控制四要素**：

**1. 流量比例**
- 金丝雀 1% → 灰度 10% → 全量 100%
- 通过 Service Mesh（Istio VirtualService）或 API Gateway 切流

**2. 实例比例**
- 1 个 Pod → 10% Pods → 50% Pods → 100% Pods
- 通过 PodChaos 的 `mode: one / all / fixed / fixed-percent` 控制

**3. 区域比例**
- 单可用区 → 同城双活 → 跨地域
- 通过 chaos-mesh `selector.spec.namespaces` + `nodes` 限制

**4. 时长控制**
- 实验时长 ≤ 影响传播时间（订单超时一般 30 秒）
- 默认 `duration: 30s` + `chaos-mesh` 自动恢复（chaos 结束 → Pod 自动重启）

**爆炸半径分级（参考 Netflix / Stripe 实践）**：

| 级别 | 流量 | 实例 | 区域 | 时长 | 适用 |
|---|---|---|---|---|---|
| L1 · 单测 | 0% | 1 Pod | 单 AZ | 5s | 首次实验 |
| L2 · 金丝雀 | 1% | 10% Pods | 单 AZ | 30s | 灰度验证 |
| L3 · 灰度 | 10% | 50% Pods | 单 Region | 5min | 回归测试 |
| L4 · 全量 | 100% | 100% Pods | 多 Region | 30min | 持续运行 |

**回滚预案（必备）**：
- 自动化：实验触发 SLO 告警 → 自动 `kubectl delete chaos <name>`
- 手动化：混沌平台「红色按钮」一键 kill 所有实验


## 故障画像（Failure Mode Catalog）


故障画像是把「**真实世界的故障**」分类成「**可注入的实验**」。

**云原生系统十大故障画像**（来自 Netflix / Stripe / LinkedIn 公开分享）：

**1. 进程类**：
- Pod kill（SIGKILL）/ Pod restart / OOM Kill
- 进程 hang（deadlock / livelock）

**2. 资源类**：
- CPU 抢占（stress cpu --cpus 2）
- 内存压力（stress vm --vm-bytes 4G）
- 磁盘 IO（fio 随机写）
- 磁盘满（disk fill）

**3. 网络类**：
- 网络延迟（tc netem delay 100ms）
- 网络丢包（tc netem loss 1%）
- 网络分区（iptables drop / chaos-mesh partition）
- DNS 解析失败（coredns 故障）

**4. 状态类**：
- 服务降级（502 / 503 注入）
- 慢响应（slowloris）
- 错误响应（500 注入）

**5. 依赖类**：
- 数据库主从切换（Redis Sentinel failover）
- 第三方 API 故障（HTTP 502 注入）
- 缓存击穿（cache miss 100%）

**6. 时钟类**：
- 时钟漂移（chrony offset）
- NTP 不可达

**7. 配置类**：
- 环境变量错误（注入 `JAVA_OPTS=invalid`）
- 配置文件损坏（注入错 JSON）

**8. 证书类**：
- TLS 证书过期
- mTLS 失败

**9. 镜像类**：
- 启动镜像损坏
- 运行时 OOM（cgroup limit）

**10. 基础设施类**：
- 节点 drain（kubectl drain）
- AZ 故障（cloud provider zone down）
- Region 故障（跨区域断网）

**优先级排序（P × I 模型）**：
- P = 发生概率（过去 6 个月故障统计）
- I = 业务影响（故障持续 30 分钟的 GMV 损失）
- 优先级 = P × I（前 20% 故障占 80% 影响）


## 实验方法论与最小可行实验


**最小可行混沌实验（MVE, Minimum Viable Experiment）**：

**步骤 1：定义假设**
- 「假设 Redis 主从切换延迟 > 500ms 时，订单服务缓存命中率从 95% 降至 60%，但 P99 延迟保持在 1.5s 以内」

**步骤 2：定义稳态度量**
- 主：订单服务 P99 延迟（基线 800ms）
- 辅：缓存命中率（基线 95%）/ 数据库 QPS（基线 5000）/ 错误率（基线 0.05%）

**步骤 3：选择爆炸半径**
- L2 金丝雀：1 个 Redis 实例 + 10% 订单服务 Pod + 单 AZ + 30s

**步骤 4：注入故障**
- chaos-mesh：RedisStressChaos + 100ms 延迟 + 30s 时长

**步骤 5：观察与判定**
- 成功：P99 延迟 ≤ 1500ms + 缓存命中率 ≥ 60% + 自动恢复（30s 内）
- 失败：P99 > 1500ms 或 错误率 > 1% → 立即 kill chaos + 写入事故复盘

**步骤 6：自动化**
- 把实验写入 Chaos Mesh Workflow（每周一 14:00 自动运行）
- 与 PagerDuty / AlertManager 联动：失败自动 @oncall

**成熟度模型（5 级）**：
- L1：手动 fire drill（一次性脚本）
- L2：工具化（Chaos Mesh + 手动调度）
- L3：CI/CD 集成（PR 触发）
- L4：持续运行（cron + 工作流）
- L5：自适应（AI 自动生成故障画像 + 自动调参）


## 与其他站点的关系


- **observability 站**：混沌实验需要 metric/log/trace 度量稳态 → 引用 observability/03-prometheus（稳态指标采集）+ observability/06-tracing（故障链路分析）
- **devops 站**：混沌实验纳入 CI/CD → 引用 devops/05-cicd-observability
- **system-design 站**：可用性原则（CAP / 降级 / 多活）→ 引用 system-design/08-availability
- **design-pattern 站**：Circuit Breaker / Bulkhead / Outbox 是混沌实验要验证的代码层模式 → 引用 design-pattern/05-architectural-patterns
- **architecture 站**：微服务韧性 / 服务网格（Service Mesh）→ 引用 architecture/05-microservices


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

<!-- svg-injected:do-not-edit -->

## 图示：混沌实验 5 阶段流程

![混沌实验 5 阶段流程](/chaos-experiment.svg)
