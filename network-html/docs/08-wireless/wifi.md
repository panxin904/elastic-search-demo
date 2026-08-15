---
title: WiFi 原理
---

# WiFi 原理

<div class="nt-badge nt-badge-wireless">无线网络</div>
<div class="nt-badge nt-badge-basics">基础</div>

WiFi 基于 IEEE 802.11 协议族，使用 **2.4 / 5 / 6 GHz** 频段，是最普及的无线局域网技术。

## 1. IEEE 802.11 协议族

| 标准 | 频段 | 最高速率 | 发布时间 |
| --- | --- | --- | --- |
| 802.11a | 5 GHz | 54 Mbps | 1999 |
| 802.11b | 2.4 GHz | 11 Mbps | 1999 |
| 802.11g | 2.4 GHz | 54 Mbps | 2003 |
| 802.11n (WiFi 4) | 2.4/5 GHz | 600 Mbps | 2009 |
| 802.11ac (WiFi 5) | 5 GHz | 6.93 Gbps | 2014 |
| 802.11ax (WiFi 6) | 2.4/5 GHz | 9.6 Gbps | 2019 |
| 802.11ax (WiFi 6E) | 6 GHz | 9.6 Gbps | 2021 |
| 802.11be (WiFi 7) | 2.4/5/6 GHz | 46 Gbps | 2024 |

## 2. 频段与信道

### 2.4 GHz
- 频率：2.412 ~ 2.472 GHz
- 中国可用 13 个信道
- 互不干扰信道：1、6、11
- 带宽：20 MHz（互不重叠信道少）

### 5 GHz
- 频率：5.15 ~ 5.85 GHz
- 信道多（25 个非 DFS）
- 带宽：20/40/80/160 MHz
- 穿墙差，距离短

### 6 GHz（WiFi 6E / 7）
- 频率：5.925 ~ 7.125 GHz
- 信道极宽
- 短距离，密集部署

## 3. 关键技术

| 技术 | 作用 |
| --- | --- |
| MIMO | 多天线收发，提升吞吐 |
| MU-MIMO | 多用户同时收发（WiFi 5+） |
| OFDM | 多载波调制 |
| OFDMA | 多用户时分频（WiFi 6） |
| Beamforming | 定向波束跟踪客户端 |
| 1024-QAM | 高密度调制（WiFi 6） |
| BSS Coloring | 同信道干扰识别（WiFi 6） |
| TWT | 目标唤醒时间，IoT 省电（WiFi 6） |
| MLO | 多链路操作（WiFi 7） |
| 320 MHz | 超宽信道（WiFi 7） |
| 4K-QAM | 4K 调制（WiFi 7） |

## 4. WiFi 6 (802.11ax) 新特性

- **OFDMA**：频分多址，多用户共享信道
- **BSS Coloring**：标记基本服务集，减少同信道干扰
- **TWT（Target Wake Time）**：IoT 设备省电
- **1024-QAM**：单符号 10 bit，速率提升 25%
- **8×8 MU-MIMO**：上下行多用户

## 5. WiFi 7 (802.11be) 特性

- **320 MHz 信道**：翻倍带宽
- **4096-QAM**：单符号 12 bit
- **MLO**：2.4 + 5 + 6 GHz 多链路聚合
- **MU-MIMO 增强**：16 流
- **EHT-PPDU**：改进的物理层封装
- **延迟 < 5ms**：XR / 云游戏

## 6. 架构

| 角色 | 作用 |
| --- | --- |
| AP（Access Point） | 接入点 |
| STA（Station） | 客户端 |
| BSS | Basic Service Set（一组 AP + STA） |
| ESS | Extended Service Set（多 BSS） |
| DS | Distribution System（连接 AP 的有线网络） |
| SSID | 网络名称 |

## 7. 工作流程

```
1. 扫描（Probe Request/Response）
2. 认证（Open / PSK / 802.1X）
3. 关联（Association Request/Response）
4. 4 次握手（WPA2/3）
5. 数据传输
6. 去关联
```

## 8. 漫游（Roaming）

- 802.11r（Fast BSS Transition）：毫秒级切换
- 802.11k（Neighbor Reports）：AP 邻居列表
- 802.11v（BSS Transition Management）：引导客户端

## 9. 部署优化

| 优化 | 做法 |
| --- | --- |
| 信道规划 | 同信道错开 5+ 信道 |
| 功率调整 | 降低 AP 功率减少同频 |
| 负载均衡 | 多 AP 频段分配 |
| 信标间隔 | 100 ms（默认） |
| DTIM | 1-3 |
| 5G 优先 | 终端优先 5 GHz |
| 漫游阈值 | RSSI -65 dBm 切换 |

## 10. WiFi 测量

```bash
# Linux
iwconfig wlan0
iw list
iw dev wlan0 link
iw dev wlan0 station dump

# 信号强度
RSSI: -30 dBm  极好
RSSI: -65 dBm  良好
RSSI: -80 dBm  弱
RSSI: -90 dBm  不可用
```

## 11. 常见问题

| 问题 | 原因 |
| --- | --- |
| 速度慢 | 信道干扰、距离远、设备老 |
| 掉线 | 漫游失败、信道干扰 |
| 延迟高 | 拥塞、AP 性能差 |
| 5G 信号差 | 5 GHz 穿墙差 |
| 设备无法连 | 加密不兼容、MAC 过滤 |

## 12. 常见面试题

1. **WiFi 6 vs WiFi 5？** OFDMA、1024-QAM、BSS Coloring、TWT。
2. **2.4G vs 5G？** 2.4G 距离远但干扰多，5G 距离短但干净。
3. **不重叠信道 2.4G？** 1、6、11。
4. **WiFi 7 关键特性？** 320MHz、4096-QAM、MLO。
5. **漫游 802.11r 作用？** 毫秒级切换。
6. **MIMO 干什么？** 多天线空间复用，提升吞吐。
