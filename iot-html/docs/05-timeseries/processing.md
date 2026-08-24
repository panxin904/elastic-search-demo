---
title: 流处理 / Downsampling
---

# 流处理 / Downsampling

> 数据降采样 + 连续查询 + 边缘流处理，时序数据降本提效。

## 🎯 核心要点

- Downsampling：1 秒原始数据降为 1 分钟 / 1 小时平均值
- 连续查询（Continuous Query）：自动定时执行聚合
- 边缘流处理：eKuiper（EMQX）/ Flink IoT
- 保留策略：原始数据保留 7 天，聚合数据保留 1 年

## 🛠️ 实战示例

```sql
# TDengine 连续查询（自动每分钟聚合）
CREATE TABLE sensor_avg_minute AS
SELECT AVG(temperature), AVG(humidity)
FROM sensor
INTERVAL(1m);
```

## 🔗 相关链接

- [时序库](./database)
- [数据模型](./schema)
- [← 返回 时序数据 目录](./)
- [← 返回 iot 首页](../)
## 🎯 流处理模式

- **Downsampling**：1s → 1min → 1h 三级聚合
- **连续查询**：定时自动聚合（Continuous Query）
- **边缘流处理**：eKuiper（EMQX）/ Flink IoT
- **保留策略**：原始 7 天 / 聚合 1 年
**精度**：降采样需保留关键特征（峰值 / 谷值）
