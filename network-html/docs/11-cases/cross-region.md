---
title: 跨地域组网
---

# 跨地域组网

<div class="nt-badge nt-badge-cases">企业案例</div>
<div class="nt-badge nt-badge-cloud">基础设施</div>

跨地域组网是全球化业务的关键，涉及专线、SD-WAN、Global Accelerator、Anycast 等技术。

## 1. 业务场景

| 场景 | 需求 |
| --- | --- |
| 多地办公 | 内网互通 |
| 异地多活 | 数据同步、流量调度 |
| 海外业务 | 就近接入 |
| 灾备 | 跨地域备份 |
| 数据合规 | 数据不出境 |

## 2. 方案对比

| 方案 | 速度 | 稳定 | 成本 | 适用 |
| --- | --- | --- | --- | --- |
| 公网 VPN | 慢 | 中 | 低 | 临时、测试 |
| 专线 (DX) | 快 | 高 | 高 | 长期、关键 |
| SD-WAN | 中 | 中 | 中 | 混合 |
| 公有云骨干 | 快 | 高 | 中 | 跨云 |
| 自建 BGP | 快 | 高 | 极高 | 运营商 |

## 3. 专线方案

### 3.1 架构

```
Local IDC ──[光纤]──> DX Location ──[云骨干]──> VPC
```

### 3.2 选型

| 厂商 | 特点 |
| --- | --- |
| AWS Direct Connect | 全球接入点 |
| Azure ExpressRoute | 多区域 |
| GCP Dedicated Interconnect | 私有 |
| 阿里云专线 | 国内覆盖全 |
| 腾讯云专线 | 金融级 |
| 中国电信 | 国内线路 |

### 3.3 双线热备

```
IDC ─┬─ DX-A ─┐
     │        ├─ VPC
     └─ DX-B ─┘
```

## 4. SD-WAN

| 厂商 | 特点 |
| --- | --- |
| Cisco Viptela | 大型 |
| VMware VeloCloud | 中型 |
| Versa | 灵活 |
| 阿里云 SD-WAN | 混合云 |
| 华为 SD-WAN | 企业 |
| Fortinet | 安全+SD-WAN |

优势：
- 多链路负载均衡
- 应用识别
- 智能选路
- 集中管理

## 5. 全球加速

### 5.1 Anycast

- 同一 IP 全球广播
- 客户端路由到最近节点
- CDN 常用

### 5.2 Global Accelerator

- AWS Global Accelerator
- 阿里云 GA
- 腾讯云 GAAP

```
客户端 → Anycast IP → 边缘 → 私有骨干 → 区域
```

## 6. 跨云互联

| 方案 | 特点 |
| --- | --- |
| SDX | 公有云 SD-WAN 互联 |
| Megaport | 第三方互联 |
| PacketFabric | 全球 |
| Equinix | 数据中心 |
| Cloud Interconnect | 同厂商多云 |

## 7. 数据同步

| 工具 | 用途 |
| --- | --- |
| 数据库同步 | MySQL binlog、PostgreSQL logical |
| 消息队列 | Kafka MirrorMaker |
| 对象存储 | S3 Cross-Region Replication |
| 文件同步 | rsync、rclone、Syncthing |

## 8. 多活架构

| 模式 | 描述 |
| --- | --- |
| 同城双活 | 同城多机房 |
| 异地灾备 | 平时冷备 |
| 异地多活 | 双向同步，单元化 |
| 单元化 | 按用户切分流量 |

### 单元化

```
用户 ID % N → 单元号 → 该单元
```

- 数据按单元分布
- 流量按用户路由
- 单元自治

## 9. 一致性

| 方案 | 描述 |
| --- | --- |
| 强一致 | 两地三中心、共识 |
| 最终一致 | 异步同步、补偿 |
| 弱一致 | 多版本、CRDT |
| 业务层幂等 | 重试安全 |

## 10. 实战案例

### 案例 1：游戏全球同服

- Anycast + 全球加速
- 数据按地域分区
- 匹配服务就近

### 案例 2：电商多活

- 用户单元化
- 库存最终一致
- 全局流量调度

### 案例 3：金融两地三中心

- 同城双活
- 异地灾备
- 数据强一致

## 11. 选型决策

| 业务阶段 | 方案 |
| --- | --- |
| 早期 | 公网 VPN |
| 中期 | 单线 SD-WAN |
| 大型 | 多线 SD-WAN + 专线 |
| 跨国 | Global Accelerator + 专线 |
| 金融 | 双专线 + 同城多活 |

## 12. 常见面试题

1. **专线 vs VPN？** 专线稳定但贵，VPN 走公网便宜但慢。
2. **SD-WAN 优势？** 多链路、智能选路、降低成本。
3. **多活怎么实现？** 单元化 + 数据同步 + 流量调度。
4. **异地多活最大挑战？** 数据一致性、流量切分。
5. **Anycast 优势？** 自动选最近节点、容灾。
6. **跨云怎么连？** SDX / Megaport / 同厂商 Interconnect。
