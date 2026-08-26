---
title: MQTT 5.0
---

# MQTT 5.0

> 消息队列遥测传输协议，IoT 事实标准。轻量、发布订阅、QoS 等级、遗嘱消息。

## 🎯 核心要点

- 协议基于 TCP，默认端口 1883 / TLS 8883
- 三种 QoS 等级（at most once / at least once / exactly once）
- 主题通配符：`+` 单层匹配 / `#` 多层匹配
- 5.0 新增：reason codes / shared subscriptions / message expiry

## 🛠️ 实战示例

```python
# Python paho-mqtt 订阅示例
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("broker.emqx.io", 1883, 60)

def on_message(client, userdata, msg):
    print(f"{msg.topic}: {msg.payload.decode()}")

client.on_message = on_message
client.subscribe("sensors/+/temperature")  # 通配符订阅
client.loop_forever()
```

## 🔗 相关链接

- [CoAP](./coap)
- [EMQX Broker](../06-platform/self-hosted)
- [← 返回 通信协议 目录](./)
- [← 返回 iot 首页](../)
## 🎯 MQTT 实战建议

- **QoS 选择**：传感器上报用 QoS 0（最快）/ 命令用 QoS 1（确保到达）/ 关键事件用 QoS 2（exactly once）
- **主题设计**：分层 `/org/region/device/type` 便于通配订阅
- **保留消息（retained）**：用于设备最新状态缓存
- **遗嘱消息（will）**：设备异常断开时通知
- **Broker 选型**：EMQX（国产开源）/ Mosquitto（轻量）/ HiveMQ（商业）


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
