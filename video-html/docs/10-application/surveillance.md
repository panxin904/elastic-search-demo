---
title: 安防监控视频
---

# 安防监控视频处理

<span class="kg-badge kg-badge-app">应用</span>
<span class="kg-badge kg-badge-protocol">网络</span>
<span class="kg-badge kg-badge-ai">智能分析</span>

安防监控视频（GB28181、海康/大华、Onvif）在 **海量摄像头接入、长时间录像、智能分析** 上有独特挑战。

## 🏗️ 安防监控架构

```
┌─────────────────────────────────────────────────┐
│ 摄像头层                                          │
│ IPC (网络摄像机) / DVR / NVR / 编码器              │
├─────────────────────────────────────────────────┤
│ 接入层                                            │
│ GB28181 平台 / RTSP 网关 / Onvif 设备管理          │
├─────────────────────────────────────────────────┤
│ 平台层                                            │
│ 流媒体服务器 / 录像存储 / 智能分析 / 报警          │
├─────────────────────────────────────────────────┤
│ 应用层                                            │
│ 客户端 (C/S / B/S) / 移动 App / 大屏 / 指挥        │
└─────────────────────────────────────────────────┘
```

## 📡 GB/T 28181 协议

中国国家标准，**SIP 信令 + RTP/RTSP 媒体**。

### 协议栈

```
┌────────────┬──────────────┬──────────────┐
│ 应用层      │ SIP 信令      │ RTSP 控制     │
├────────────┼──────────────┼──────────────┤
│ 传输层      │ UDP/TCP       │ TCP          │
├────────────┼──────────────┼──────────────┤
│ 网络层      │ IPv4/IPv6    │              │
└────────────┴──────────────┴──────────────┘
```

### 信令交互

```
客户端                          摄像头
  │
  ├── INVITE (邀请) ─────────→  │
  │   {带 SDP 描述}
  │                          ───┤
  │                          ←─┤ 100 Trying
  │                          ←─┤ 200 OK (带 SDP)
  │                          ───┤
  │                          ───┤ ACK
  │                          ───┤ (媒体流建立)
  │
  ├── BYE 结束 ──────────────→  │
```

### SIP 目录查询

```
设备搜索:
MESSAGE 摄像头 SIP ID <sip:34020000001320000001@3402000000>

回复:
MESSAGE 客户端
  <Response>
    <DeviceList>
      <Item>
        <DeviceID>34020000001310000001</DeviceID>
        <Name>摄像头 1</Name>
        <Status>ON</Status>
      </Item>
    </DeviceList>
  </Response>
```

### 媒体流 (PS 封装)

GB28181 视频流使用 **PS（MPEG-PS）** 或 **RTP/PS** 封装：

```c
// PS 包结构
PS Header
├── System Header
├── PSM (Program Stream Map)
└── ES (Elementary Stream)
    ├── Video PES (H.264/H.265)
    └── Audio PES (G.711/AAC)
```

## 🎬 海康/大华协议

### 主流协议

| 协议 | 用途 |
| --- | --- |
| **RTSP** | 实时流拉取 |
| **RTMP** | 推流（部分设备） |
| **HTTP 抓图** | 图片抓拍 |
| **SDK 私有** | 海康 HCNetSDK / 大华 DSS |

### RTSP 拉流 URL

```
海康:  rtsp://admin:password@192.168.1.64:554/Streaming/Channels/101
       (1=主码流, 2=子码流, 01=第一路)
       /Streaming/Channels/101  -> 主码流
       /Streaming/Channels/102  -> 子码流
       /Streaming/Channels/101+102 -> 主+子 (双码流)

大华:  rtsp://admin:password@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0
       subtype=0 -> 主
       subtype=1 -> 子

宇视:  rtsp://admin:password@192.168.1.100:554/video/0

萤石:  rtsp://admin:password@ip:554/Streaming/Channels/101
```

### SDK 接入示例（海康）

```cpp
// 海康 HCNetSDK 初始化
NET_DVR_Init();

// 登录
NET_DVR_USER_LOGIN_INFO pLoginInfo = {};
strcpy(pLoginInfo.sDeviceAddress, "192.168.1.64");
strcpy(pLoginInfo.sUserName, "admin");
strcpy(pLoginInfo.sPassword, "password123");
pLoginInfo.wPort = 8000;

LONG lUserID = NET_DVR_Login_V40(&pLoginInfo, &lpDeviceInfo);

// 实时预览
NET_DVR_CLIENTINFO lpClientInfo;
lpClientInfo.hPlayWnd = GetDlgItem(IDC_PLAYWND)->GetSafeHwnd();
lpClientInfo.lChannel = 1;

LONG lRealPlayHandle = NET_DVR_RealPlay_V40(lUserID, &lpClientInfo, NULL, NULL);

// 停止预览
NET_DVR_StopRealPlay(lRealPlayHandle);
NET_DVR_Logout(lUserID);
NET_DVR_Cleanup();
```

### ONVIF 协议

```
ONVIF 设备发现 (WS-Discovery):
UDP 组播 239.255.255.250:3702
  <Probe>
    <Types>tds:Device</Types>
  </Probe>

设备响应:
  <ProbeMatches>
    <ProbeMatch>
      <XAddrs>http://192.168.1.64/onvif/device_service</XAddrs>
    </ProbeMatch>
  </ProbeMatches>
```

## 📦 录像存储

### 存储策略

| 方案 | 描述 |
| --- | --- |
| **CVR（中心录像）** | 服务器集中存储 |
| **NVR** | 网络录像机 |
| **SD 卡** | 摄像头本地 |
| **云存** | 云端备份 |

### 时间表录像

```
全天 24h × 30天 × 2Mbps = 约 620GB / 摄像头
1080p × 8Mbps        = 2.5TB / 摄像头 / 月
```

### 录像格式

| 厂商 | 容器 | 编码 |
| --- | --- | --- |
| **海康** | MP4 | H.264 / H.265 |
| **大华** | MP4 / dav | H.264 / H.265 |
| **萤石** | MP4 | H.264 |
| **标准** | PS / MP4 | H.265/H.264 |

### 录像回放

```
录制:  /record/cam01/2026-08-05/14-00.mp4
       /record/cam01/2026-08-05/14-30.mp4
       ...

检索:  getRecordInfo(cam, start, end)
下载:  downloadFile(cam, ts)
```

## 🎥 流媒体服务器

### SRS 转 GB28181

```nginx
# SRS 5.0 支持 GB28181
vhost __defaultVhost__ {
    # RTP 监听
    rtp {
        listen 9000;
        # 对接 GB28181 PS 流
    }
}
```

### ZLMediaKit

```
ZLMediaKit 提供 GB28181 网关:
├── ZLM 接收 PS 流（RTP/PS）
├── 转 RTMP / HLS
├── 提供 HTTP-FLV / WebRTC 输出
└── 录像存储
```

### EasyCVR / EasyGBS 平台

国产开源视频汇聚平台：
- 多协议接入（GB28181 / Onvif / RTSP / 海康 SDK）
- 多协议输出（RTMP / HLS / WebRTC）
- 统一管理
- 录像、报警、级联

## 🤖 智能分析 AI

### 主流能力

| 能力 | 描述 |
| --- | --- |
| **人脸识别** | 1:N 比对、人脸库 |
| **车牌识别** | OCR + 车牌库 |
| **行为分析** | 跌倒、打架、聚集 |
| **越界检测** | 区域入侵告警 |
| **物体识别** | 包裹、动物检测 |
| **客流统计** | 跨境、密度 |
| **聚众识别** | 公共安全事件 |

### AI 处理位置

```
┌─────────────────────────────────────────┐
│ 端侧 AI (Edge)                            │
│ 摄像头内置 AI 芯片 (Hi3519A, S3)         │
│ 直接输出结构化数据 + 视频                │
│ 优势：低延迟、节省带宽、隐私             │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 中心 AI (Server)                          │
│ 云端 GPU 集群做深度学习推理              │
│ 录像 + 实时双路径                       │
│ 优势：模型大、精度高、迭代快             │
└─────────────────────────────────────────┘
```

### 主流 AI 厂商

| 厂商 | 方案 |
| --- | --- |
| **旷视（Face++）** | 人脸 / 车辆 / 行为 |
| **商汤** | SenseAR / 行为 / 城市 |
| **依图** | 人脸识别 |
| **云从** | 安防 AI |
| **海康** | Hikvision AI Cloud |
| **大华** | Dahua ThinkAI |
| **华为** | HoloSens 智能摄像机 |
| **地平线** | 边缘 AI 芯片 |

## 📊 海量摄像头接入

### 接入能力估算

单台流媒体服务器：
- 200-500 路 1080p 实时流（软转）
- 1000+ 路 720p（硬转）
- 主要瓶颈：网络 + 磁盘 IO

### 分层架构

```
亿级摄像头
└── 区域 (city) 级联
    └── 区县平台
        └── 行业平台
            └── 单个视频网关
                └── 单台服务器 (200-500 路)
```

### 分布式集群

```
                ┌─ Node 1 (200 路)
                ├─ Node 2 (200 路)
  GB28181 SIP ←─┤─ Node 3 (200 路)
                ├─ ...
                └─ Node N (200 路)
                       ↓
                   Kafka 消息总线
                       ↓
                  AI 推理集群
                       ↓
                  告警 / 录像
```

### 消息总线

Kafka / RocketMQ：
- 视频帧元数据
- 告警事件
- 录像索引
- 设备状态

## 🗄️ 录像与对象存储

### 录像策略

| 策略 | 适合 |
| --- | --- |
| **循环覆盖** | 监控场景（默认） |
| **事件保留** | 报警录像 |
| **长期归档** | 重要录像 → 冷存储 |
| **云端备份** | 容灾 |

### 存储容量计算

```
摄像头数量 × 单摄像头码率 × 时间 ÷ 1024

例: 1000 摄像头 × 4Mbps × 30 天 ÷ 8 ÷ 1024 ≈ 1.3 PB
```

### 存储优化

1. **动态帧率**：无人时降低帧率（VFR）
2. **H.265**：比 H.264 节省 30-50%
3. **智能判断**：录无意义视频
4. **分层存储**：热数据 SSD + 温数据 HDD + 冷数据磁带

## ⚠️ 安防特色需求

### 录像完整性

- **N+1 冗余**：多副本录像
- **断电保护**：UPS + 本地 SSD 备份
- **录像加密**：对称 + 非对称加密

### 时钟同步

- 所有摄像头 NTP 同步（误差 < 0.5s）
- 用于录像回放时间定位

### 网络环境

- 政企专网 / 互联网 / VPN
- 弱网下 VFR + 重传

## 📱 客户端形态

| 客户端 | 描述 |
| --- | --- |
| **C/S 客户端** | Windows / Mac 客户端 |
| **Web 客户端** | B/S 架构（H5 + WebRTC） |
| **手机 App** | iOS / Android |
| **电视墙** | 大屏拼接 |
| **报警主机** | 联动报警 |

### Web 客户端架构

```
H5 Video Player
├── Hls.js (HLS)
├── flv.js (HTTP-FLV)
├── WebRTC (实时)
└── jsmpeg.js (JS 解码)
```

## 📚 实战案例

### 案例 1：智慧城市监控

```
10万级摄像头接入
├── 区域级联
├── 视频云存储
├── AI 联动（人脸、车辆、行为）
├── GIS 一张图
└── 应急指挥
```

### 案例 2：连锁门店监管

```
2000 门店
├── 每店 4-8 路摄像头
├── 4G / 专线回传
├── 云端集中管理
├── 远程巡店（手机 App）
└── AI 异常告警
```

### 案例 3：智能交通

```
路口摄像头 (电警/卡口)
├── 车牌识别
├── 车速检测
├── 违章抓拍
├── 信号联动
└── 流量统计
```

## 🛠️ 开发建议

1. **多协议兼容**：GB28181 + RTSP + Onvif + SDK 都要支持
2. **带宽预估**：单台千兆带宽最多 ~200 路 4Mbps
3. **录像接口**：按时间切片高效检索
4. **告警实时**：Kafka 队列 + WebSocket 推送
5. **历史回放**：分段存储 + 时空索引
6. **设备心跳**：定期 Ping + 状态上报
7. **权限管理**：摄像机/录像精细权限
8. **审计日志**：所有操作可追溯
