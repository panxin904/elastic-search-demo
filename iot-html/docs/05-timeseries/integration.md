---
title: Grafana / Kafka
date: 2026-08-27  # date-auto-injected
---

# Grafana / Kafka

> Grafana 可视化 + Kafka 消息集成，时序数据生态对接。

## 🎯 核心要点

- Grafana：可视化仪表盘，多数据源支持
- Kafka：时序数据通过 Kafka 流转到下游（实时分析 / 备份）
- Prometheus remote_write：InfluxDB / TDengine 兼容此协议
- 典型架构：设备 → MQTT → Kafka → InfluxDB → Grafana

## 🛠️ 实战示例

```python
# Kafka 集成（Python）
from kafka import KafkaProducer
import json

producer = KafkaProducer(
  bootstrap_servers=["kafka:9092"],
  value_serializer=lambda v: json.dumps(v).encode()
)
producer.send("sensor-data", {"device_id": "d001", "value": 25.5})
```

## 🔗 相关链接

- [时序库](./database)
- [流处理](./processing)
- [← 返回 时序数据 目录](./)
- [← 返回 iot 首页](../)
## 🎯 生态集成

- **Grafana**：可视化仪表盘（InfluxDB / TDengine 数据源）
- **Kafka**：消息流转（设备 → MQTT → Kafka → InfluxDB）
- **Prometheus remote_write**：兼容协议
**告警**：基于阈值 / 异常检测 / 趋势预测
**降采样**：原始数据保留 7 天，1m 聚合保留 30 天，1h 聚合保留 1 年。

- **小贴士**：Grafana 8+ 原生支持 TDengine / InfluxDB 数据源。


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
