---
title: 自建 IoT 平台
date: 2026-08-27  # date-auto-injected
---

# 自建 IoT 平台

> EMQX / ThingsBoard / HiveMQ 三大开源 IoT Broker 与平台对比。

## 🎯 核心要点

- EMQX：国产开源，百万级 MQTT 连接，性能强
- ThingsBoard：可视化设备管理 + 仪表盘 + 规则引擎
- HiveMQ：商业友好，集群支持完善
- 选型：纯 Broker → EMQX；含设备管理 → ThingsBoard

## 🛠️ 实战示例

```bash
# EMQX 启动（Docker）
docker run -d --name emqx -p 1883:1883 -p 18083:18083 emqx/emqx:latest
# Web 控制台: http://localhost:18083
# 默认账户: admin / public
```

## 🔗 相关链接

- [公有云](./public-cloud)
- [智能家居](./smart-home)
- [← 返回 云平台与行业落地 目录](./)
- [← 返回 iot 首页](../)
## 🎯 自建选型

- **EMQX**：国产开源，百万级 MQTT 连接
- **ThingsBoard**：含设备管理 + 仪表盘 + 规则引擎
- **HiveMQ**：商业友好，集群支持完善
**集群**：EMQX / ThingsBoard 都支持集群部署
**高可用**：EMQX / ThingsBoard 集群部署至少 3 节点。


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
