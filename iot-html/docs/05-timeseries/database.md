---
title: 时序库选型
---

# 时序库选型

> InfluxDB / TDengine / TimescaleDB / QuestDB 四大时序库对比与选型。

## 🎯 核心要点

- InfluxDB：生态最全（Telegraf / Chronograf），2.x 起闭源
- TDengine：国产开源，专为 IoT 设计，性能强（10x InfluxDB）
- TimescaleDB：PostgreSQL 扩展，SQL 兼容
- QuestDB：InfluxDB 替代，PostgreSQL 协议兼容
- 选型三问：写入吞吐？查询模式（聚合 / 原始）？生态？

## 🛠️ 实战示例

```python
# TDengine Python 写入示例
import taos

conn = taos.connect(host="localhost", user="root", password="taosdata")
cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS iot_data PRECISION 'ms';")
cursor.execute("USE iot_data")
cursor.execute("CREATE TABLE IF NOT EXISTS sensor (ts TIMESTAMP, temperature FLOAT, humidity FLOAT);")
cursor.execute("INSERT INTO sensor VALUES (NOW, 25.5, 60.2);")
```

## 🔗 相关链接

- [流处理](./processing)
- [可视化](./integration)
- [← 返回 时序数据 目录](./)
- [← 返回 iot 首页](../)
## 🎯 时序库选型

- **生态最全**：InfluxDB（Telegraf / Chronograf）
- **国产性能强**：TDengine（10x InfluxDB 性能）
- **SQL 兼容**：TimescaleDB（PostgreSQL 扩展）
- **InfluxDB 替代**：QuestDB（PostgreSQL 协议）
