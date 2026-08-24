---
title: 离线自治
---

# 离线自治

> 网络中断时边缘设备继续工作：本地缓存 + 协议转换 + 网络恢复后批量上云。

## 🎯 核心要点

- 本地缓存：SQLite / LevelDB / BadgerDB
- 协议转换：Modbus RTU → MQTT（本地完成）
- 决策降级：网络断时按本地规则处理，恢复后上报告
- 关键指标：自治时长（电池续航 / 本地存储容量）

## 🛠️ 实战示例

```python
# 离线自治伪代码
while network_up:
  data = read_sensor()
  upload_to_cloud(data)  # 上传云端
else:
  save_to_local(data)    # 写入本地 SQLite
  when network_recovered:
    batch_upload_local_data()
```

## 🔗 相关链接

- [KubeEdge](./framework)
- [设备影子](../04-management/shadow)
- [← 返回 边缘计算 目录](./)
- [← 返回 iot 首页](../)
## 🎯 离线自治模式

- **缓存 + 重传**：本地 SQLite，网络恢复后批量同步
- **决策降级**：本地规则引擎（if-else / 决策树）
- **降级运行**：低频率采集 / 简化算法
- **关键指标**：自治时长（电池容量 / 存储上限）
