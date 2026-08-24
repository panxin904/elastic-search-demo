---
title: 数据模型
---

# 数据模型

> tag / field / timestamp 三元组是时序数据核心模型。

## 🎯 核心要点

- tag：维度（设备 ID / 区域 / 类型），可索引
- field：测量值（温度 / 湿度），不可索引
- timestamp：纳秒精度时间戳
- 一设备一表 vs 一类设备一表：写入性能 vs 查询灵活

## 🛠️ 实战示例

```text
# InfluxDB Line Protocol
sensor,device_id=d001,region=shanghai temperature=25.5,humidity=60.2 1692096000000000000
```

## 🔗 相关链接

- [时序库](./database)
- [流处理](./processing)
- [← 返回 时序数据 目录](./)
- [← 返回 iot 首页](../)
## 🎯 数据模型设计

- **tag**：维度（设备 ID / 区域 / 类型），可索引
- **field**：测量值（温度 / 湿度），不可索引
- **timestamp**：纳秒精度
- **建表策略**：一设备一表 vs 一类设备一表
**写入**：tag 索引占空间，避免高基数（每条不同值）
**设计原则**：tag 不要高基数（≤ 100K 不同值），field 必须存在。
