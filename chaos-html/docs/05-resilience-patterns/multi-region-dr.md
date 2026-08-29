---
title: 多活与灾备
---

# 多活与灾备

## 多活 vs 灾备

**多活（Active-Active）**：

- 多个 Region 同时服务流量
- 任意 Region 故障，其他 Region 接管
- 资源利用率高（无闲置）

**灾备（Active-Passive / DR）**：

- 主 Region 服务流量，备 Region 待机
- 主 Region 故障，备 Region 接管
- 资源利用率低（备 Region 闲置）

## 灾备 RTO / RPO 矩阵

| 级别 | RTO（恢复时间） | RPO（数据丢失） | 成本 |
|---|---|---|---|
| L0（无灾备） | 小时级 | 不保证 | $0 |
| L1（备份恢复） | 24 小时 | 24 小时 | $ |
| L2（同城灾备） | 1 小时 | 几分钟 | $$ |
| L3（异地灾备） | 4 小时 | 几分钟 | $$$ |
| L4（同城多活） | 分钟级 | 秒级 | $$$$ |
| L5（异地多活） | 分钟级 | 秒-分钟 | $$$$$ |

**金融业典型要求**：

- 支付系统：L4（同城多活）
- 银行核心：L5（异地多活）

## 多活架构层级

**1. DNS 层**：

- 智能 DNS（Route 53 / AliDNS）按地理位置解析
- 健康检查 + 故障转移

**2. 全球负载均衡**：

- AWS Global Accelerator / Cloudflare Spectrum
- 任意cast IP（Anycast）

**3. 数据库同步**：

- 同步复制（强一致）：性能损耗
- 异步复制（最终一致）：性能高，但 RPO > 0
- 双向同步（Active-Active）：冲突处理复杂

## 混沌验证

**1. Region kill 实验**：

- chaos-mesh AWSChaos：随机停止一个 AZ 的 EC2
- 验证：流量 100% 自动转移到其他 AZ
- 验证：RTO < 5 分钟（自动恢复）

**2. 数据库主从切换实验**：

- chaos-mesh + Redis Sentinel：手动 failover
- 验证：写请求自动路由到新主
- 验证：RPO < 1 秒（异步复制延迟）

**3. DNS 切换实验**：

- 注入 DNS 解析失败
- 验证：客户端 failover 到备用 DNS

## 多活陷阱

- 不考虑数据冲突（同一订单在两个 Region 创建）
- 时钟不同步（订单时间错乱）
- 流量调度策略简单（无权重 / 无健康检查）
- 灾备演练不足（主 Region 真挂了切不动）

**典型多活案例**：

- **阿里淘宝**：3 地 5 中心（同城 + 异地）
- **AWS S3**：11 个 9 的可用性（多区域存储）
- **Netflix**：跨 AWS Region 多活 + Chaos Monkey 持续验证

## 与其他站点关系

- **system-design/08-availability**：可用性分级
- **design-pattern/05-architectural-patterns**：多活架构模式
- **chaos/01-foundations/blast-radius**：爆炸半径分级


## ## 实战案例

**Netflix 多区域 active-active**：us-east-1 + us-west-2 + eu-west-1 三区域 active-active 部署，任意一区故障 30s 内自动切流。

**阿里云 unit 化架构**：把数据中心切成 100+ unit 单元，每个单元 10w QPS 独立运营，单元间通过中间件隔离，故障爆炸半径可控。

**字节跳动异地多活**：上海 + 杭州 + 深圳三地部署，DNS + 数据双写双读，TPS 1.5M 稳定。


## ## 故障排查清单

1. 切换时间过长 → 优化健康检查 + 预热逻辑
2. 数据不一致 → 启用 CRDT 或最终一致
3. 切流后 5xx 飙升 → 检查 SLA 限流
4. 跨区域延迟 → 边缘缓存 + 就近读
5. 演练失败 → 演练前必须 verify 全链路


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
