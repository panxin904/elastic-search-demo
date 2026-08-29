---
title: 物联网通信
date: 2026-08-15  # date-auto-injected
---

# 物联网通信

<div class="nt-badge nt-badge-wireless">无线网络</div>
<div class="nt-badge nt-badge-cloud">IoT</div>

物联网（IoT）通信按**距离**分为短距（蓝牙、Zigbee、WiFi）和广域（LoRa、NB-IoT、4G/5G），按**功耗**分为电池供电的低功耗方案与持续供电的宽带方案。

## 1. IoT 通信分层

```
┌────────────────────────────────────────┐
│  应用层：MQTT / CoAP / HTTP / Modbus   │
├────────────────────────────────────────┤
│  网络层：IPv6 / 6LoWPAN / RPL          │
├────────────────────────────────────────┤
│  链路层：802.15.4 / BLE / LoRa         │
├────────────────────────────────────────┤
│  物理层：Sub-GHz / 2.4G / 5G           │
└────────────────────────────────────────┘
```

## 2. 短距通信

| 协议 | 频段 | 速率 | 距离 | 节点数 | 功耗 |
| --- | --- | --- | --- | --- | --- |
| WiFi | 2.4/5G | 600M | 100m | 32 | 中 |
| BLE | 2.4G | 1M | 50m | 7 | 极低 |
| Zigbee | 2.4G | 250k | 100m | 6万+ | 低 |
| Z-Wave | 868M | 100k | 30m | 232 | 低 |
| Thread | 2.4G | 250k | 30m | 300+ | 低 |
| Matter | 多 | — | — | — | 低 |
| UWB | 3-10G | 110k-27M | 10m | — | 低 |

## 3. 广域 LPWAN

| 协议 | 频段 | 速率 | 距离 | 特点 |
| --- | --- | --- | --- | --- |
| LoRa | Sub-GHz | 0.3-50k | 10km | 私有部署 |
| LoRaWAN | Sub-GHz | 0.3-50k | 10km | LoRa 联盟标准 |
| NB-IoT | 运营商 | 200k | 10km | 蜂窝 |
| Cat-M1 | 运营商 | 1M | 10km | 蜂窝移动 |
| Sigfox | Sub-GHz | 100bps | 50km | 法国 Sigfox |

### LoRa 扩频

```
SF7  - SF12：扩频因子
带宽：125 / 250 / 500 kHz
```

高 SF + 低带宽 = 远距离 + 低速率。

### LoRaWAN 架构

```
终端节点（Node）
  ↕  LoRa
网关（Gateway）
  ↕  IP
网络服务器（NS）
  ↕
应用服务器（AS）
```

## 4. 蜂窝 IoT

| 类别 | 速率 | 移动 | 语音 | 适用 |
| --- | --- | --- | --- | --- |
| Cat-1 | 10M | ✓ | ✓ | 中等 |
| Cat-M1 | 1M | ✓ | ✓ | 资产追踪 |
| NB-IoT | 200k | ✗ | ✗ | 抄表 |
| 5G eRedCap | — | ✓ | — | 中速 IoT |
| 5G RedCap | 10M | ✓ | — | 可穿戴 |

## 5. 应用层协议

| 协议 | 特点 | 适用 |
| --- | --- | --- |
| MQTT | 轻量发布订阅 | IoT 事实标准 |
| CoAP | 类 HTTP，UDP | 受限设备 |
| HTTP/REST | 通用 | 强设备 |
| Modbus | 工业串口 | 工控 |
| OPC UA | 工业统一架构 | 智能制造 |
| DDS | 实时分发 | 车联网、军工 |

### MQTT 5 大特性

| 特性 | 作用 |
| --- | --- |
| QoS 0/1/2 | 消息到达保证 |
| Retain | 保留消息 |
| Will | 遗嘱消息 |
| Topic | 主题树 |
| Pub/Sub | 多对多解耦 |

## 6. IoT 平台

| 平台 | 厂商 |
| --- | --- |
| AWS IoT Core | AWS |
| Azure IoT Hub | Microsoft |
| Google Cloud IoT | Google（已停服） |
| 阿里云 IoT | 阿里 |
| 腾讯云 IoT Explorer | 腾讯 |
| EMQX | 开源 |
| ThingsBoard | 开源 |

## 7. 安全挑战

| 风险 | 防御 |
| --- | --- |
| 设备仿冒 | 设备证书 |
| 弱口令 | 强密码 / 首次配对鉴权 |
| 固件漏洞 | OTA 升级、签名验证 |
| 中间人 | TLS / DTLS |
| DDoS | 平台限流 |
| 隐私 | 数据脱敏、端到端加密 |

## 8. 设备影子（Device Shadow）

- 平台保存设备最后状态
- 设备离线时缓存命令
- 上线后同步

## 9. OTA 升级

```
1. 服务器生成新固件包（含签名）
2. 推送到设备（含分片）
3. 设备校验签名
4. 写入双备份区
5. 重启切换
6. 失败回滚
```

## 10. 实战：MQTT 入门

```bash
# mosquitto 订阅
mosquitto_sub -h broker.emqx.io -t "test/#" -v

# 发布
mosquitto_pub -h broker.emqx.io -t "test/temp" -m '{"value":23.5}'
```

## 11. 常见面试题

1. **LPWAN 代表？** LoRa、NB-IoT、Sigfox。
2. **MQTT vs HTTP？** MQTT 轻量、发布订阅、适合弱网。
3. **QoS 0/1/2？** 0 至多一次、1 至少一次、2 恰好一次。
4. **LoRaWAN 架构？** Node → Gateway → NS → AS。
5. **NB-IoT 特点？** 蜂窝、广域、低速、海量连接。
6. **设备影子作用？** 缓存状态、离线命令、同步。
