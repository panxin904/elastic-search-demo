---
title: Modbus / OPC-UA
---

# Modbus / OPC-UA

> 工业现场总线协议，Modbus 简单通用，OPC-UA 工业 4.0 标准。

## 🎯 核心要点

- Modbus RTU（串口） / Modbus TCP（以太网，端口 502）
- 寄存器分类：Coil / Discrete Input / Holding Register / Input Register
- OPC-UA：二进制协议 + 信息建模 + 安全加密
- 适用场景：PLC / 工业仪表 / SCADA 系统

## 🛠️ 实战示例

```python
# pymodbus 读保持寄存器
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient("192.168.1.100", port=502)
result = client.read_holding_registers(0, 10, slave=1)
if not result.isError():
    print(f"寄存器值: {result.registers}")
```

## 🔗 相关链接

- [MQTT](./mqtt)
- [工业互联网](../06-platform/iiot)
- [← 返回 通信协议 目录](./)
- [← 返回 iot 首页](../)
## 🎯 Modbus 实战建议

- **寄存器映射**：用 Excel / 文档记录每个从站地址含义
- **轮询间隔**：根据设备响应时间设置（典型 100-1000ms）
- **异常处理**：超时重试 + 断线告警 + 数据校验
- **库选择**：Python 用 pymodbus / Java 用 modbus4j


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
