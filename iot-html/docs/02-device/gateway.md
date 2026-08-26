---
title: 网关硬件
---

# 网关硬件

> 树莓派 / 工业网关 / 边缘网关。对接多种协议 + 本地缓存 + 离线自治。

## 🎯 核心要点

- 入门：树莓派 4B（4GB / ¥300）/ Orange Pi 5
- 工业：研华 UNO 系列 / 西门子 IOT2050（IP65 防护）
- 协议转换：Modbus → MQTT / Zigbee → Wi-Fi
- 离线自治：本地缓存 + 网络恢复后批量上云

## 🛠️ 实战示例

```text
# Node-RED 流程（树莓派网关）
[Modbus TCP] -> [Function: 数据清洗] -> [InfluxDB]
                              |
                              v
                       [MQTT 上传]
# 本地缓存：网络断时数据先写 SQLite，恢复后批量同步
```

## 🔗 相关链接

- [KubeEdge](../03-edge/k8s-edge)
- [EMQX](../06-platform/self-hosted)
- [← 返回 设备与硬件 目录](./)
- [← 返回 iot 首页](../)
## 🎯 网关选型

- **入门**：树莓派 4B / Orange Pi 5（4GB / ¥300-500）
- **工业**：研华 UNO 系列 / 西门子 IOT2050（IP65）
- **协议转换**：Modbus TCP → MQTT / Zigbee → Wi-Fi
- **本地能力**：缓存 / 离线自治 / 边缘 AI
**存储**：本地 SSD 或 eMMC 缓存


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
