---
title: 蓝牙与短距
date: 2026-08-15  # date-auto-injected
---

# 蓝牙与短距

<div class="nt-badge nt-badge-wireless">无线网络</div>
<div class="nt-badge nt-badge-cases">短距</div>

蓝牙（Bluetooth）是 2.4 GHz ISM 频段的**短距离**低功耗通信协议，广泛用于耳机、手表、IoT 设备。

## 1. 蓝牙版本演进

| 版本 | 速率 | 关键特性 |
| --- | --- | --- |
| 1.0 | 721 kbps | 基础 |
| 2.0 + EDR | 3 Mbps | 增强数据率 |
| 3.0 + HS | 24 Mbps | 高速（基于 WiFi） |
| 4.0 (BLE) | 1 Mbps | 低功耗 |
| 4.2 | — | BLE 隐私、IPv6 |
| 5.0 | 2 Mbps | 范围 ×4，速率 ×2 |
| 5.2 | — | LE Audio、LC3 |
| 5.3 | — | 连接增强、低延迟 |
| 5.4 | — | 周期性广播、ESL |

## 2. 蓝牙协议栈

```
Application
   ↓
Middleware（音频/文件/网络）
   ↓
Logical Link Control（L2CAP）
   ↓
Host Controller Interface（HCI）
   ↓
Link Manager（LMP）
   ↓
Baseband（物理层 / 基带）
   ↓
RF（2.4 GHz）
```

## 3. 经典蓝牙 vs BLE

| 维度 | 经典蓝牙 | BLE |
| --- | --- | --- |
| 功耗 | 高 | 极低 |
| 速率 | 1~3 Mbps | 1~2 Mbps |
| 配对 | 必需 | 可选 |
| 适用 | 音频 / 文件 | 传感 / 信标 |
| 跳频 | 79 信道 | 40 信道 |
| 连接时间 | 100ms+ | < 3ms |

## 4. BLE 工作流程

```
1. 广播（Advertising）：固定信道 37/38/39
2. 扫描（Scanning）：扫描请求 + 响应
3. 连接请求（CONNECT_REQ）
4. 连接事件（Connection Event）
5. 数据传输（GATT）
```

## 5. GATT 服务

```
Service（服务）
  ├── Characteristic（特征）
  │     ├── Value
  │     ├── Descriptor
  │     └── Property（R/W/N/Indicate/Notify）
  └── ...
```

常见服务：
- 0x1800 Generic Access
- 0x180A Device Information
- 0x180F Battery Service
- 0x1810 Blood Pressure
- 0x1812 Heart Rate

## 6. 配对与安全

| 模式 | 描述 |
| --- | --- |
| Just Works | 不验证，自动配对 |
| Passkey Entry | 6 位数字 |
| OOB | NFC 等带外 |
| Numeric Comparison | 双方确认相同数字 |
| LE Secure Connections | P-256 ECDH |

漏洞：
- **BlueBorne**（2017）：空中攻击
- **BLESA**（2020）：BLE 冒充

## 7. 蓝牙 Mesh

- 多对多通信
- 用于照明、传感器网络
- 支持中继、代理、朋友节点

## 8. LE Audio（蓝牙 5.2）

- LC3 编码：低码率高音质
- 多流音频：左 / 耳独立流
- 广播音频：一对多
- 助听器支持

## 9. 信标（Beacon）

- iBeacon（Apple）
- Eddystone（Google）
- 用于室内定位、推送

## 10. 短距协议对比

| 协议 | 频段 | 距离 | 速率 | 功耗 |
| --- | --- | --- | --- | --- |
| 蓝牙 BLE | 2.4G | 50m | 1-2Mbps | 极低 |
| Zigbee | 2.4G | 100m | 250kbps | 低 |
| Z-Wave | 908/868 MHz | 30m | 100kbps | 低 |
| LoRa | Sub-GHz | 10km | 0.3-50kbps | 极低 |
| NB-IoT | 运营商 | 10km | 200kbps | 低 |
| Thread | 2.4G | 30m | 250kbps | 低 |
| Matter | 多 | — | — | — |
| WiFi HaLow | Sub-GHz | 1km | Mbps | 中 |

## 11. Matter 协议

- 由 CSA 主导（Apple/Google/Amazon/三星等）
- 基于 IPv6（IP-based）
- WiFi + Thread 底层
- 跨生态互联

## 12. 常见面试题

1. **BLE 全称？** Bluetooth Low Energy。
2. **经典蓝牙 vs BLE？** 功耗、速率、适用场景。
3. **GATT 是什么？** 通用属性配置文件，定义服务与特征。
4. **LE Audio 优势？** LC3 低码率 + 多流 + 广播。
5. **蓝牙 5.0 vs 4.2？** 距离 4 倍、速率 2 倍、广播容量 8 倍。
6. **Matter 协议特点？** IP-based、跨生态、WiFi+Thread。


<!-- auto-enrich:do-not-edit -->

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
