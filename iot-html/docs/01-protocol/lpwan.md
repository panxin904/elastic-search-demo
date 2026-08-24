---
title: LoRaWAN / NB-IoT
---

# LoRaWAN / NB-IoT

> 低功耗广域网协议，远距离（数公里）+ 低功耗（电池用数年）+ 低数据量。

## 🎯 核心要点

- LoRaWAN：免授权频段，1-3km 城市 / 10km+ 郊区，速率 0.3-50 kbps
- NB-IoT：运营商授权频段（蜂窝），覆盖更广，模组成本低
- Sigfox：欧洲主导，极低数据量（每天 140 条消息）
- 适用场景：智能水电气表 / 农业传感 / 资产追踪

## 🛠️ 实战示例

```cpp
# LoRaWAN 节点伪代码（基于 LMIC 库）
void setup() {
  os_init();  // 初始化 LMIC
  LMIC_setLinkMode(MODE_LORAWAN);
  LMIC_setDrTxpow(DR_SF7, 14);  // SF7 数据率，14dBm 功率
}

void loop() {
  LMIC_send(1, payload, len, 0);  // 端口 1 发送
  os_runloop_once();
}
```

## 🔗 相关链接

- [MQTT](./mqtt)
- [设备安全](../04-management/security)
- [← 返回 通信协议 目录](./)
- [← 返回 iot 首页](../)
## 🎯 LPWAN 选型

- **LoRaWAN**：免授权频段，自建网关，1-3km 城市覆盖
- **NB-IoT**：运营商频段（移动 / 电信 / 联通），无需自建网关
- **Sigfox**：欧洲主导，国内应用少
- **数据包大小**：LoRaWAN 最大 51 字节 / NB-IoT 最大 1600 字节
