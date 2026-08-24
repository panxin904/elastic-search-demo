---
title: 公有云 IoT
---

# 公有云 IoT

> AWS IoT Core / Azure IoT Hub / 阿里云 LinkKit / 华为云 IoTDA 四大公有云对比。

## 🎯 核心要点

- AWS IoT Core：Device Gateway / Registry / Shadow / Rules Engine
- Azure IoT Hub：与 Azure Functions / Digital Twins 集成
- 阿里云 LinkKit：物模型 + 设备影子，国内 IoT 接入首选
- 华为云 IoTDA：LiteOS + 物联网平台，国内第二

## 🛠️ 实战示例

```python
# 阿里云 LinkKit 接入伪代码
import linkkit

lk = linkkit.LinkKit(
  host_name="cn-shanghai.link.aliyuncs.com",
  product_key="pk123",
  device_name="sensor001",
  device_secret="secret"
)
lk.connect()
lk.post_property("temperature", 25.5)
```

## 🔗 相关链接

- [设备影子](../04-management/shadow)
- [自建 IoT](./self-hosted)
- [← 返回 云平台与行业落地 目录](./)
- [← 返回 iot 首页](../)
## 🎯 公有云对比

- **AWS IoT Core**：Device Gateway / Registry / Shadow / Rules Engine
- **Azure IoT Hub**：与 Azure Functions / Digital Twins 集成
- **阿里云 LinkKit**：国内 IoT 首选，物模型 + 设备影子
- **华为云 IoTDA**：LiteOS + IoT 平台
**费用**：消息数 / 设备数 / 流量计费
