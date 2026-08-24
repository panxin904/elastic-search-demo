---
title: 传感器
---

# 传感器

> 温湿度 / IMU / 图像 / 气体四类常见传感器原理、选型、接口。

## 🎯 核心要点

- 温湿度：DHT22 / SHT31（I2C）/ DS18B20（1-Wire）
- 惯性 IMU：MPU6050（6 轴）/ BMI088（无人机级）
- 图像：OV2640（200万像素）/ Arducam 系列
- 气体：BME680（VOC+温湿压）/ MQ-2（烟雾）/ MH-Z19（CO2）

## 🛠️ 实战示例

```python
# Raspberry Pi + BME680 Python
import smbus2
import bme680

bus = smbus2.SMBus(1)
sensor = bme680.BME680(bus)

while True:
  data = {} if sensor.get_sensor_data() else sensor.data
  print(f"温度: {data.temperature:.1f}°C  湿度: {data.humidity:.1f}%  气压: {data.pressure:.1f}hPa")
  time.sleep(1)
```

## 🔗 相关链接

- [MCU](./mcu)
- [边缘智能](../03-edge/ai-edge)
- [← 返回 设备与硬件 目录](./)
- [← 返回 iot 首页](../)
## 🎯 传感器选型

- **精度需求**：消费级（DHT22）/ 工业级（BME680）/ 医疗级（PT100）
- **接口选择**：I2C（短距离）/ SPI（高速）/ 1-Wire（单线）
- **校准**：温湿度补偿 / 零点漂移 / 长期稳定性
- **防护等级**：IP65（户外）/ IP67（水下）
**采样率**：根据应用需求选择（1Hz / 100Hz / 1kHz）
**接口**：I2C（≤ 1Mbps 短距离）/ SPI（高速）/ 1-Wire（单线）。
