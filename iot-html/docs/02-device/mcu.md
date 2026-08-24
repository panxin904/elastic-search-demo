---
title: MCU / SoC
---

# MCU / SoC

> 微控制器与片上系统选型。算力 / 内存 / 功耗 / 价格 / 外设的权衡。

## 🎯 核心要点

- 入门级：ESP32（双核 240MHz / Wi-Fi+BLE / ¥10）/ Arduino
- 中端：STM32（ARM Cortex-M，工业级）/ nRF52（BLE 强）
- 高端：树莓派 Pico（RP2040 双核 M0）/ Allwinner / Rockchip（Linux）
- 选型三问：电池供电？实时性？需要哪些外设？

## 🛠️ 实战示例

```cpp
# ESP32 Arduino 读取温度传感器（伪代码）
#include <OneWire.h>
OneWire ds(4);  // GPIO4 接 DS18B20

void loop() {
  ds.reset();
  ds.write(0xCC);  // 跳过 ROM
  ds.write(0x44);  // 温度转换
  delay(750);
  ds.reset();
  ds.write(0xCC);
  ds.write(0xBE);  // 读 Scratchpad
  byte data[9]; ds.readBytes(data, 9);
  int raw = (data[1] << 8) | data[0];
  float temp = raw / 16.0;
  Serial.printf("Temperature: %.2f°C\n", temp);
}
```

## 🔗 相关链接

- [FreeRTOS](./rtos)
- [网关硬件](./gateway)
- [← 返回 设备与硬件 目录](./)
- [← 返回 iot 首页](../)
## 🎯 MCU 选型三问

- **是否需要 Wi-Fi/BLE？** 需要 → ESP32 / nRF52 / ESP32-C3
- **是否需要硬实时？** 需要 → STM32F4 / Nordic nRF52
- **是否需要 Linux？** 需要 → 树莓派 / Allwinner / Rockchip
