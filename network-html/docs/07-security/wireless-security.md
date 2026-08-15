---
title: 无线安全
---

# 无线安全

<div class="nt-badge nt-badge-security">网络安全</div>
<div class="nt-badge nt-badge-wireless">无线</div>

无线网络因**空气传播**特性，安全挑战与有线不同。本章梳理 WiFi 安全演进、常见攻击与防御。

## 1. WiFi 安全协议演进

| 协议 | 全称 | 状态 |
| --- | --- | --- |
| WEP | Wired Equivalent Privacy | **已破解** |
| WPA | WiFi Protected Access | TKIP 弃用 |
| WPA2 | WiFi Protected Access 2 | **当前主流**（PSK / Enterprise） |
| WPA3 | WiFi Protected Access 3 | **现代推荐** |
| WPS | WiFi Protected Setup | 弱 PIN，已不推荐 |

## 2. WEP 破解

- 24 bit IV 容易碰撞
- RC4 流密码漏洞
- Aircrack-ng 几分钟可破解
- **结论：禁用 WEP**

## 3. WPA2 安全

### 3.1 个人模式（PSK）

```
4 次握手 (WPA2-PSK)
PMK = PBKDF2(PSK, SSID, 4096, 256)
PTK = PRF(PMK, ANonce, SNonce, MACs)
```

### 3.2 企业模式（802.1X）

```
AP ──> Supplicant
     <── EAP (EAP-TLS / PEAP / TTLS)
     ──> RADIUS
          └── 认证通过 → 主密钥 → PTK
```

- 认证服务器：RADIUS / FreeRADIUS
- 证书 / 用户名密码 / OTP

### 3.3 已知漏洞

- **KRACK**（2017）：4 次握手重放，攻击 PTK
- **Dragonblood**（2019）：WPA3 SAE 侧信道

## 4. WPA3 改进

| 特性 | 描述 |
| --- | --- |
| SAE（Simultaneous Authentication of Equals） | 防离线字典攻击 |
| 个性化数据加密 | 防止开放 WiFi 抓包 |
| 前向保密 | 会话密钥独立 |
| 简化配置 | 易用性提升 |

## 5. 常见攻击

| 攻击 | 描述 |
| --- | --- |
| 暴力破解 PSK | 抓握手包离线字典破解 |
| WPS 攻击 | 8 位 PIN 撞库 |
| 仿冒 AP（Evil Twin） | 同 SSID 假 AP |
| 中间人 | 强制降级到无加密 |
| 拒绝服务 | 干扰 / 注入 Deauth |
| 隐匿 SSID 抓取 | Probe 抓包 |

## 6. 防御

| 措施 | 做法 |
| --- | --- |
| WPA3 + 强密码 | 16+ 字符 |
| 关闭 WPS | 防 PIN 攻击 |
| 隐藏 SSID | 弱保护，但增加攻击难度 |
| MAC 过滤 | 弱保护，可绕过 |
| 802.11w | 管理帧保护（防 Deauth） |
| Rogue AP 检测 | 无线 IDS |
| 802.1X | 企业级认证 |
| 客户端证书 | mTLS |

## 7. 企业无线安全

```
AP ──> Controller ──> RADIUS
                       └── 动态 VLAN
                            ↓
                       员工 / 访客 / IoT 隔离
```

- 员工：802.1X + 证书 → 内部 VLAN
- 访客：Captive Portal → 互联网 VLAN
- IoT：MAB（MAC 认证）→ 设备 VLAN

## 8. Captive Portal

访客认证门户：
1. 连接 SSID（开放）
2. 浏览器自动跳转
3. 输入手机号 / 微信 / 短信
4. 认证通过 → 放行

## 9. 监控与审计

- WIDS / WIPS（无线入侵检测 / 防御）
- 工具：Kismet、AirMagnet、Ekahau
- 检测：未授权 AP、伪 AP、Deauth 攻击

## 10. 蓝牙与 Zigbee 安全

### 蓝牙

- 模式：Just Works / Passkey / OOB / Numeric Comparison
- 漏洞：BlueBorne（2017）、BLESA（2020）
- 防御：禁用不必要的发现、配对加密

### Zigbee

- 加密：AES-128
- 默认 link key 公开（已被破解）
- 工业 / 智能家居需独立密钥

## 11. 移动安全

| 风险 | 防御 |
| --- | --- |
| 假基站（IMSI Catcher） | 强制 4G/5G，禁用 2G |
| SS7 漏洞 | 运营商侧加固 |
| WiFi 仿冒 | VPN 加密 |
| Rogue AP | 客户端探测 |

## 12. 常见面试题

1. **WEP 为什么被淘汰？** 24 bit IV 太短，RC4 弱。
2. **WPA2 vs WPA3？** WPA3 用 SAE 防离线字典，强制前向保密。
3. **4 次握手做什么？** 协商 PTK，证明双方拥有相同 PSK。
4. **KRACK 攻击原理？** 重放 4 次握手第 3 个包导致 nonce 重用。
5. **Evil Twin 怎么防？** 证书校验、VPN、802.11w。
6. **企业无线认证？** 802.1X + RADIUS。
