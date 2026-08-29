---
layout: home

hero:
  name: "IoT"
  text: "物联网全栈知识图谱"
  tagline: "通信协议 · 边缘计算 · 设备管理 · 时序数据 · 云平台 · 行业落地"
  image:
    src: /favicon.svg
    alt: IoT
  actions:
    - theme: brand
      text: 开始学习
      link: /path
    - theme: alt
      text: 知识图谱
      link: /mindmap

features:
  - title: 📡 通信协议
    details: MQTT 5.0 / CoAP / Modbus / OPC-UA / LoRaWAN / NB-IoT 协议矩阵；QoS 等级 / Topic 设计 / Retain / Will Message / 安全连接（TLS / X.509）。
    link: /path
    linkText: 协议入门
  - title: 🔌 设备与硬件
    details: MCU（ESP32 / STM32 / Arduino）/ SoC / RTOS / 传感器与执行器；GPIO / I2C / SPI / UART / ADC；低功耗设计（休眠 / 唤醒 / 能量采集）。
    link: /path
    linkText: 硬件基础
  - title: 🌐 边缘计算
    details: EdgeX Foundry / KubeEdge / Azure IoT Edge / AWS Greengrass；边缘网关协议转换、本地推理、离线自治、云边协同。
    link: /path
    linkText: 边缘架构
  - title: 🛰️ 设备管理
    details: 设备影子（Desired / Reported）/ 物模型（属性 / 服务 / 事件）/ OTA 固件升级 / 设备注册 / 拓扑与分组 / 告警与远程命令。
    link: /path
    linkText: 设备生命周期
  - title: 📊 时序数据
    details: InfluxDB / TDengine / TimescaleDB / Prometheus；高写入压缩 / Downsampling / 连续查询 / 边缘端流处理（Flink / eKuiper）。
    link: /path
    linkText: 时序存储
  - title: ☁️ 云平台与行业落地
    details: AWS IoT Core / 阿里云 LinkKit / 华为云 IoTDA / EMQX / ThingsBoard；智能家居 / 工业互联网 / 车联网 / 智慧城市 四大场景案例。
    link: /path
    linkText: 云平台选型
---

<script setup>
const painPoints = [
  "协议栈碎片：MQTT / CoAP / Modbus / OPC-UA / LoRaWAN 各自适合什么场景？",
  "边缘 vs 云端：哪些计算放边缘、哪些放云端？",
  "设备影子 vs 物模型：阿里 / 华为 / AWS 三家抽象不一致，迁移成本高？",
  "时序数据爆炸：百万设备 × 每秒 1 条数据，传统 MySQL 撑不住？",
  "OTA 升级：如何保证百万设备固件升级不回滚、不变砖？",
  "安全：设备证书、密钥管理、TLS 双向认证怎么做？"
]
const goals = [
  "协议选型矩阵（按功耗 / 带宽 / 实时性 / 部署成本）",
  "设备端硬件 + RTOS + 网络栈全栈视图",
  "边缘网关架构（EdgeX / KubeEdge / Azure IoT Edge）",
  "设备管理（影子 / 物模型 / OTA / 拓扑）",
  "时序数据库选型（InfluxDB / TDengine / TimescaleDB）",
  "主流云平台对比（AWS / 阿里 / 华为 / 自建 EMQX）"
]
const relatedSites = [
  { site: "network", path: "/path", label: "网络协议（MQTT 跑在 TCP/IP 上）" },
  { site: "cloud-native", path: "/path", label: "云原生（KubeEdge / EdgeX 容器化）" },
  { site: "bigdata", path: "/path", label: "大数据（时序数据接入 Kafka / Flink）" },
  { site: "observability", path: "/path", label: "可观测性（设备指标 / Prometheus remote_write）" },
  { site: "security", path: "/path", label: "安全（设备证书 / mTLS / ZeroTrust）" },
  { site: "architecture", path: "/path", label: "企业架构（千万级 IoT 平台架构）" }
]
</script>

<ClientOnly>
  <WhyThisGraph
    :pain-points="painPoints"
    :goals="goals"
    :related-sites="relatedSites"
    title="🎯 为什么写这个图谱？"
  />
</ClientOnly>

## 📚 相关阅读（跨站导航）

<!-- xlink-injected:do-not-edit -->

按主题跨站推荐：

- [android](https://java-px.bot.cd/android/)：Android Things
- [linux](https://java-px.bot.cd/linux/)：Linux 嵌入式
- [rust](https://java-px.bot.cd/rust/)：Rust 嵌入式
- [python](https://java-px.bot.cd/python/)：Python 数据处理
- [network](https://java-px.bot.cd/network/)：MQTT / CoAP 协议
- [security](https://java-px.bot.cd/security/)：设备安全


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

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料
<!-- auto-enrich:do-not-edit -->
