---
title: FreeRTOS / Zephyr
---

# FreeRTOS / Zephyr

> 嵌入式实时操作系统，多任务调度 + 同步原语 + 硬件抽象层。

## 🎯 核心要点

- FreeRTOS：小型内核（4-12KB），MIT 许可，Arduino / ESP-IDF 内置
- Zephyr：Linux 基金会维护，模块化设计，BLE / LoRa / Wi-Fi 驱动丰富
- Riot OS：欧洲学术项目，低内存友好（10KB 即可运行）
- 任务间同步：信号量 / 互斥锁 / 队列 / 事件组

## 🛠️ 实战示例

```cpp
# FreeRTOS 多任务示例（ESP32）
xTaskCreate(
  sensorTask,    // 任务函数
  "Sensor",      // 名称
  4096,          // 栈大小
  NULL,          // 参数
  1,             // 优先级
  NULL           // 句柄
);
xTaskCreate(uploadTask, "Upload", 8192, NULL, 1, NULL);

void sensorTask(void* arg) {
  while (1) {
    float data = readSensor();
    xQueueSend(sensorQueue, &data, portMAX_DELAY);
    vTaskDelay(1000 / portTICK_PERIOD_MS);
  }
}
```

## 🔗 相关链接

- [MCU](./mcu)
- [边缘智能](../03-edge/ai-edge)
- [← 返回 设备与硬件 目录](./)
- [← 返回 iot 首页](../)
## 🎯 RTOS 选型

- **入门**：FreeRTOS（资源最少，Arduino / ESP-IDF 内置）
- **中端**：Zephyr（Linux 基金会，蓝牙协议栈完善）
- **学术**：Riot OS（欧洲学术项目，内存极小）
- **任务设计**：优先级 / 栈大小 / 同步原语 / 看门狗


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
