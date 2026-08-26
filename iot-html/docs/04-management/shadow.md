---
title: 设备影子 / 物模型
---

# 设备影子 / 物模型

> 设备状态在云端的抽象表示，用于状态同步、命令下发、状态查询。

## 🎯 核心要点

- 设备影子（Device Shadow）：AWS IoT / Azure IoT 都用此概念
- 物模型（Thing Specification）：阿里云 LinkKit 定义设备属性 / 服务 / 事件
- 数字孪生（Digital Twin）：更复杂的物理模型仿真
- 同步机制：reported vs desired，最终一致

## 🛠️ 实战示例

```json
# AWS IoT Device Shadow JSON 示例
{
  "reported": { "temperature": 25.5, "fan_speed": 1500 },
  "desired": { "temperature": 24.0 }
}
```

## 🔗 相关链接

- [OTA](./ota)
- [云平台](../06-platform/public-cloud)
- [← 返回 设备管理 目录](./)
- [← 返回 iot 首页](../)
## 🎯 设计模式

- **AWS IoT Shadow**：AWS IoT 标准
- **Azure Digital Twins**：数字孪生（更复杂物理模型）
- **阿里云物模型**：国内标准（属性 / 服务 / 事件）
**同步**：reported vs desired 最终一致

- **小贴士**：状态合并用 MQTT 保留消息 + 版本号。


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
