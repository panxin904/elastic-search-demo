---
title: IoT 速查表
date: 2026-08-21  # date-auto-injected
---

# 🧾 IoT 速查表

> 协议 / 端口 / 频段 / 数据格式 一页速查。

## 协议矩阵

| 协议 | 传输层 | 端口 | QoS | 适用场景 |
|---|---|---|---|---|
| MQTT 5.0 | TCP | 8883 (TLS) | 0/1/2 | 通用 IoT、双向消息、设备管理 |
| MQTT 3.1.1 | TCP | 1883 / 8883 | 0/1/2 | 旧设备兼容 |
| CoAP | UDP | 5683 / 5684 | Confirmable / Non | 受限设备、低功耗 |
| HTTP/HTTPS | TCP | 80 / 443 | — | REST API、配置下发 |
| WebSocket | TCP | 80 / 443 | — | 浏览器直连设备 |
| Modbus TCP | TCP | 502 | — | 工业现场 |
| OPC-UA | TCP | 4840 | — | 工业 4.0、安全通信 |
| LoRaWAN | — | — | — | 远距离低功耗（< 10km） |
| NB-IoT | LTE Cat-NB | — | — | 蜂窝物联网、深覆盖 |
| BLE 5.x | 2.4GHz | — | — | 近场、可穿戴 |
| Zigbee | 2.4GHz | — | — | 智能家居 mesh |

## MQTT 关键参数

```text
keep_alive:        60s            # 心跳间隔；建议 1.5-2 倍 NAT 超时
clean_session:     true           # 1：每次新会话；0：断线保留订阅
qos:               1              # 99% 场景用 1
retain:            false          # 保留消息给新订阅者；状态类用 true
will_message:      offline        # 异常断开时发的最后遗言
will_qos:          1
will_retain:       true
max_inflight:      20             # 同时未确认消息数
max_qos:           2              # broker 限制
max_packet_size:   256KB          # 避免巨型 payload
```

## MQTT Topic 设计模板

```text
{tenant}/{product}/{deviceId}/{service}

# 示例
acme/factory-A/sensor-001/telemetry      # 设备上行数据
acme/factory-A/sensor-001/event           # 事件上报
acme/factory-A/sensor-001/command         # 下行控制
acme/factory-A/sensor-001/ack             # 命令确认
acme/factory-A/sensor-001/lwt             # 遗嘱

# 通配符订阅
acme/+/sensor-001/#                       # 某设备所有消息
acme/factory-A/#                          # 整厂所有消息
acme/+/+/telemetry                        # 所有设备的遥测
```

## 时序数据库选型

| 项 | InfluxDB | TDengine | TimescaleDB | Prometheus |
|---|---|---|---|---|
| 主语言 | Go | C | C / PG ext | Go |
| 协议 | HTTP / InfluxQL | RESTful SQL | PG SQL | PromQL |
| 写入 (ops/s) | 100w | 1000w | 100w | 100w |
| 压缩比 | 5-10x | 10-20x | 5-10x | 5x |
| 数据保留 | 策略保留 | 块级 TTL | 策略保留 | 默认 15d |
| Grafana 集成 | 原生 | 插件 | 原生 | 原生 |
| 集群 | OSS / Enterprise | 开源可集群 | 开源 | 联邦 |

## 设备端参考功耗

| 场景 | 平均电流 | 续航（2000mAh） |
|---|---|---|
| ESP32 深度睡眠 | 10 µA | 27 年 |
| ESP32 蓝牙配网 | 50 mA | 40 小时 |
| ESP32 Wi-Fi 持续连接 | 80 mA | 25 小时 |
| NB-IoT PSM 模式 | 5 µA | 45 年 |
| NB-IoT 主动上报 | 100 mA | 20 小时 |
| LoRaWAN Class A | 10 µA | 27 年 |
| LoRaWAN Class C | 30 mA | 67 小时 |

## OTA 包大小估算

| 固件类型 | 全量 | 差分（10% 改动） |
|---|---|---|
| ESP32 Arduino | 1.2 MB | 120 KB |
| STM32 FreeRTOS | 0.5 MB | 50 KB |
| Linux ARM64 | 80 MB | 8 MB |
| Android 设备 | 500 MB | 50 MB |

## 设备影子数据结构

```json
{
  "desired": { "switch": "on", "brightness": 80 },
  "reported": { "switch": "on", "brightness": 50, "fw_version": "1.2.3" },
  "delta": { "brightness": 80 }
}
```

## 安全端口速查

| 协议 | 端口 | 加密 |
|---|---|---|
| MQTT (明文) | 1883 | ❌ |
| MQTT over TLS | 8883 | ✅ mTLS 可选 |
| MQTT over WebSocket | 8083 | ❌ |
| MQTT over WSS | 8084 | ✅ |
| CoAP (明文) | 5683 | ❌ |
| CoAP over DTLS | 5684 | ✅ |

## 一句话总结

90% 场景 = **ESP32 + MQTT(TLS) + InfluxDB + Grafana**；只在工业现场加 OPC-UA / Modbus，在低功耗加 LoRaWAN / NB-IoT。


## 📱 手机扫码继续阅读

<ClientOnly>
  <QrShare />
</ClientOnly>
