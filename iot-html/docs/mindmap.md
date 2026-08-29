---
title: IoT 知识图谱
date: 2026-08-21  # date-auto-injected
---

# 🗺️ IoT 知识图谱

> 本页用 Mermaid mindmap 展示 IoT 全栈知识结构。

```mermaid
mindmap
  root((IoT 物联网))
    通信协议
      应用层
        MQTT 5.0
        CoAP
        HTTP/WebSocket
        AMQP
      工业现场
        Modbus
        OPC-UA
        CAN
        EtherCAT
      低功耗广域网
        LoRaWAN
        NB-IoT
        Sigfox
      短距离
        BLE 5.x
        Zigbee
        Z-Wave
        Wi-Fi 6
    设备与硬件
      MCU
        ESP32
        STM32
        Arduino
        Raspberry Pi Pico
      SoC
        nRF52
        Allwinner
        Rockchip
      操作系统
        FreeRTOS
        Zephyr
        Riot OS
        Linux Embedded
      传感器
        温湿度
        惯性 IMU
        图像
        气体
    边缘计算
      框架
        EdgeX Foundry
        KubeEdge
        Azure IoT Edge
        AWS Greengrass
      网关
        协议转换
        本地缓存
        离线自治
      边缘智能
        TensorFlow Lite
        ONNX Runtime
        OpenVINO
    设备管理
      抽象模型
        设备影子
        物模型
        数字孪生
      生命周期
        注册认证
        固件 OTA
        配置下发
        远程命令
      安全
        X.509 证书
        mTLS
        密钥管理
        OTA 签名
    时序数据
      数据库
        InfluxDB
        TDengine
        TimescaleDB
        QuestDB
      数据处理
        Downsampling
        连续查询
        边缘流处理
        Flink / eKuiper
      集成
        Grafana
        Prometheus remote_write
        Kafka 引擎
    云平台与行业落地
      公有云
        AWS IoT Core
        Azure IoT Hub
        阿里云 LinkKit
        华为云 IoTDA
      自建
        EMQX
        ThingsBoard
        HiveMQ
      场景
        智能家居 Matter
        工业互联网 IIoT
        车联网 V2X
        智慧城市
```

## 阅读建议

- **协议入门**：先看 MQTT / CoAP 两节，再看 Modbus 对比
- **设备端**：从 ESP32 + FreeRTOS 入手，进阶到 Linux Embedded
- **边缘架构**：先看 EdgeX 整体框架，再深入 KubeEdge
- **数据落地**：协议 → 设备 → 边缘 → 云端 → 时序库 → 可视化是一条完整链路

## 在图谱中的位置

物联网是 **network（网络协议）+ cloud-native（容器化边缘）+ bigdata（时序数据）** 三大领域的交叉落地场景。如果只看图谱名词不熟悉，先回到 [network](/network/)/[cloud-native](/cloud-native/) 站补基础。
