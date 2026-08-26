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
