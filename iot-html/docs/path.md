---
title: IoT 学习路径
---

# 🚶 IoT 学习路径

> 三条路径覆盖"嵌入式开发者 / 后端开发者 / 解决方案架构师"三种角色。按背景选择即可。

## 路径 1：纯新手（1 周）

适合：从其他方向（前端/后端/算法）转入 IoT，从未接触过嵌入式硬件。

| Day | 主题 | 关键交付 |
|---|---|---|
| Day 1 | MQTT 协议 5 分钟入门 | 用 EMQX + MQTTX 跑通 pub/sub |
| Day 2 | ESP32 + Arduino IDE 点灯 | 第一个固件：Blink + Wi-Fi 连接 |
| Day 3 | ESP32 发布 DHT11 温湿度 | 上行数据到本地 EMQX broker |
| Day 4 | 搭建 EMQX + InfluxDB + Grafana | 数据可视化一条链路 |
| Day 5 | Node-RED 入门 | 拖拽式串联设备 / 数据库 / 通知 |
| Day 6 | AWS IoT Core 免费额度试用 | 跑通"设备 → 云 → 回调" |
| Day 7 | 复盘 + 选题 | 决定走嵌入式 / 后端 / 架构 哪个细分 |

## 路径 2：后端开发者（2 周）

适合：已熟悉 Linux / 网络 / 数据库，想转 IoT 后端 / 云平台开发。

| 周 | 主题 | 关键交付 |
|---|---|---|
| W1 D1-2 | MQTT 5.0 协议深挖 | QoS 0/1/2、Topic 通配符、Retain、Will |
| W1 D3-4 | EMQX 企业级特性 | 鉴权（JWT / X.509）、桥接、规则引擎 |
| W1 D5 | InfluxDB vs TDengine vs TimescaleDB | 百万级写入 benchmark |
| W2 D1-2 | EdgeX Foundry 架构 | Core/Support/Export/Edge 服务 + Device SDK |
| W2 D3 | KubeEdge（K8s 边缘扩展） | CloudCore / EdgeCore / Mapper |
| W2 D4 | 设备影子 vs 物模型 | 对比 AWS / 阿里 / 华为 三家 |
| W2 D5 | OTA 架构 | 灰度 / 分批 / 回滚 / 签名验证 |
| W2 周末 | 实战：自建千万级 IoT 平台 demo | 含设备模拟器 + 后端 + 大盘 |

## 路径 3：嵌入式开发者（3 周）

适合：单片机 / RTOS / 驱动 开发背景，想往 IoT 全栈延伸。

| 周 | 主题 | 关键交付 |
|---|---|---|
| W1 D1-2 | 网络协议栈（TCP/IP / TLS / DNS） | 在 ESP-IDF 上跑通 HTTPS client |
| W1 D3-4 | MQTT 客户端移植 | 基于 mbedtls + 轻量 MQTT 库 |
| W1 D5 | 低功耗设计 | 休眠 / 唤醒 / 蓝牙配网 |
| W2 D1-2 | OTA 升级（断点续传 + 签名 + 回滚） | 在 ESP32 上完整实现 |
| W2 D3-4 | 边缘网关（Linux + 多协议） | 串口 / Modbus / CAN → MQTT |
| W2 D5 | 安全：SE / TEE / 安全启动 | 设备证书烧录 |
| W3 D1-2 | LoRaWAN / NB-IoT 模组 | 长距离 / 低功耗接入 |
| W3 D3-4 | 边缘 AI（TFLite Micro） | 关键词识别 / 简单 CV |
| W3 D5 | 行业认证（CE / FCC / 国密） | 合规快速入门 |

## 一句话定义

物联网 = **把物理世界数字化**：传感器采集 → 设备端处理 → 网络传输 → 边缘/云端存储 → 应用消费 → 控制回路。

## 关键 takeaway

- **协议不是越多越好**：90% 场景 MQTT 一招鲜；只在强工业场景才上 OPC-UA / Modbus
- **数据时序性是核心**：别用 MySQL 存设备数据，第一周就上 InfluxDB / TDengine
- **安全是后置必修**：先跑通再加 mTLS / 证书 / 签名，不要"以后再说"
- **云平台不是银弹**：百万级以下自建 EMQX 比上云便宜；千万级以上再评估上云 ROI
