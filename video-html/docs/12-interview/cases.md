---
title: 系统设计案例
---

# 视频系统设计面试题

<span class="kg-badge kg-badge-interview">面试</span>
<span class="kg-badge kg-badge-cloud">架构</span>
<span class="kg-badge kg-badge-tools">设计</span>

## 🚀 一、短视频上传 + 转码系统设计

### 需求

- 用户上传 100MB-5GB 视频
- 支持断点续传
- 转码多分辨率 (1080p / 720p / 480p / 360p)
- 智能封面 + AI 标签
- 实时进度反馈

### 整体架构

```
┌────────────┐                ┌─────────────────────┐
│ 客户端      │                │ 服务端                │
│            │                │                     │
│ 上传 SDK   │                ├─ API Gateway        │
│  ├── 切片   ├──────→        │                     │
│  ├── 压缩   │  /upload      │ ├─ Upload Service   │
│  └── 加密   │                │ │   (生成 uploadId)  │
│            │                │ │                    │
│ 状态机:    │  /chunk        │ ├─ Chunk Service    │
│  PENDING   ├──────→        │ │   (分片接收)        │
│  UPLOADING │                │ │                    │
│  UPLOADED  │  /finish       │ ├─ Merge Service    │
│  TRANSCODE │├──────→        │ │   (合并文件)        │
│  DONE      │                │ │                    │
│            │  /progress      │ ├─ Kafka 生产者     │
│ 接收回调   │←─────          │ │   (分发转码任务)    │
└────────────┘                │ │                    │
                              │ ├─ Object Storage   │
                              │ │   (原始 + 转码产物) │
                              │ └─ Database          │
                              │     (状态持久化)      │
                              └─────────────────────┘
                                          ↓
                              ┌─────────────────────┐
                              │ 转码集群             │
                              │ (Worker pool)       │
                              │                     │
                              │ Worker 1 → 1080p    │
                              │ Worker 2 → 720p     │
                              │ Worker 3 → 480p     │
                              │ Worker 4 → 360p     │
                              └─────────────────────┘
```

### 关键设计

#### 1. 客户端分片上传

```javascript
const uploadId = await api('/upload/init', {
    filename: 'video.mp4',
    size: 100 * 1024 * 1024,  // 100MB
    md5: '...'
});

// 分片
const chunkSize = 4 * 1024 * 1024;  // 4MB
for (let i = 0; i < file.size; i += chunkSize) {
    const chunk = file.slice(i, i + chunkSize);
    const etag = await api('/chunk/upload', {
        uploadId, part: i / chunkSize,
        chunk
    });
    parts.push(etag);
}

await api('/upload/finish', {
    uploadId,
    parts
});
```

#### 2. 服务端接收逻辑

```python
# Upload Service - 主流程
class UploadService:
    def init(self, filename, size, md5):
        upload_id = uuid.uuid4().hex
        record = {
            'upload_id': upload_id,
            'filename': filename,
            'size': size,
            'md5': md5,
            'parts': [],
            'status': 'PENDING'
        }
        redis.hset(f'upload:{upload_id}', mapping=record)
        return upload_id

    def chunk_upload(self, upload_id, part_no, chunk):
        # 存到临时分片目录
        path = f'/tmp/uploads/{upload_id}/{part_no}'
        save_to_disk(path, chunk)
        # 记录 part
        redis.hset(f'upload:{upload_id}', f'parts.{part_no}', md5(chunk))
        # 异步处理：分片入库 OSS
        send_to_kafka('chunk_oss', {'upload_id': upload_id, 'part_no': part_no})

    def finish(self, upload_id, parts):
        # 检查完整性
        if not verify_parts(upload_id, parts):
            raise Exception('missing parts')
        # 触发合并
        kafka.produce('merge_task', upload_id)
        # 触发转码
        kafka.produce('transcode_task', upload_id)
        return 'processing'
```

#### 3. 转码任务队列

```python
# 转码 Worker
class TranscodeWorker:
    def run(self):
        while True:
            task = kafka.consume('transcode.tasks')
            video_id = task['video_id']

            # 拉源视频
            input_path = oss.download(task['object_key'])

            # 多分辨率转码
            futures = []
            for res in ['1080p', '720p', '480p', '360p']:
                future = self.pool.submit(self.transcode, input_path, res)
                futures.append((res, future))

            for res, f in futures:
                output = f.result()
                key = f'result/{video_id}/{res}.mp4'
                oss.upload(key, output)
                db.update(video_id, f'{res}_url', cdn_url(key))
                notify_complete(video_id, res)

            db.update(video_id, 'status', 'DONE')
            kafka.produce('ai.task', video_id)
```

#### 4. 实时进度查询

```python
# 客户端轮询 / WebSocket
GET /api/v1/video/{id}/progress
{
    "uploaded_chunks": 25,
    "total_chunks": 25,
    "upload_status": "DONE",
    "transcode_progress": {
        "1080p": "DONE",
        "720p": "PROCESSING",
        "480p": "PROCESSING",
        "360p": "PENDING"
    },
    "overall_progress": "85%"
}
```

### 进阶要点

1. **大文件加速**：P2P + 边缘节点
2. **上传前压缩**：客户端 H.265 预编码
3. **失败重试**：分片级别独立重试
4. **断点续传**：客户端缓存 uploadId
5. **安全**：病毒扫描、加密、签名
6. **进度反馈**：WebSocket 实时推送
7. **超时清理**：24h 未完成上传清理
8. **配额管理**：VIP / 普通用户分开

## 🎥 二、互动直播系统设计

### 需求

- 1+ N 实时互动
- < 500ms 延迟
- 10w+ 观众
- 弹幕 / 礼物 / 连麦

### 架构

```
┌──────────────────────────────────────────────┐
│ 主播端 (推流)                                   │
│ 编码器/RTMP SDK/WebRTC                         │
└──────────┬───────────────────────────────────┘
           ↓
┌──────────────────────────────────────────────┐
│ 接入层                                          │
│ RTMP WebRTC / SRT                              │
└──────────┬───────────────────────────────────┘
           ↓
┌──────────────────────────────────────────────┐
│ 媒体分发 (SFU)                                  │
│ ├─ 录像集群 (自动录制)                          │
│ ├─ 转码集群 (推流立即拉流)                      │
│ └─ 互动集群 (连麦)                              │
└──────────┬───────────────────────────────────┘
           ↓ ↓ ↓
┌──────────────────────────────────────────────┐
│ CDN 加速 (200+ 节点)                            │
└──────────┬───────────────────────────────────┘
           ↓
观众 (Web / App)
```

### 连麦架构（多人）

```
   主播 A (推流) ───┐
                    ↓
                 ┌─→ SFU 1 ──┐
                 │             ↓
                 │           混流 ──→ 主推流 ──→ CDN
                 │             ↑
                 └─→ 主播 B ──┘ (音频 + 视频混流)
```

### 弹幕系统

```
观众客户端 → WebSocket 服务
                          ↓
                  房间管理 (Sharded)
                          ↓
                  NATS / Kafka (消息总线)
                          ↓
                  广播给同房间用户 (200ms 内)
```

#### 弹幕设计关键

1. **分级策略**：付费弹幕 > 普通弹幕
2. **频率限制**：每用户每秒 1 条
3. **房间隔离**：跨房间不互通
4. **异步分发**：抗瞬时峰值
5. **历史弹幕**：异步落到 ClickHouse / HBase

## 📞 三、视频会议系统设计

### 需求

- 1V1 / 多人
- 屏幕共享
- 多人音视频
- 会议录像
- IM 互动

### 架构

```
┌────────────────────────────────────────┐
│ 媒体服务器 (SFU)                       │
│ ├─ WebRTC 信令                          │
│ ├─ 媒体协商                              │
│ ├─ TURN / STUN                           │
│ └─ 录制服务                              │
└──────────┬─────────────────────────────┘
           ↓
┌────────────────────────────────────────┐
│ 应用层                                   │
│ 房间管理 / 用户管理 / 鉴权 / 计费         │
└────────────────────────────────────────┘
```

### 信令流程

```
1. 入会邀请
   控制信令 1 → 创建会议 → 通知用户

2. 加入会议
   控制信令 2 → 加入房间 → 媒体握手
   WebRTC offer/answer/ICE

3. 媒体交换
   双向音频 + 视频流（DTLS-SRTP）

4. 会议控制
   静音 / 取消静音 / 视频开关 / 屏幕共享

5. 结束会议
   资源释放 + 录像归档
```

### 关键考量

1. **延迟**：< 500ms
2. **带宽**：动态降低
3. **弱网**：NACK + FEC
4. **录制**：服务端合成一录
5. **跨国**：多 region SFU

## 📺 四、点播系统设计

### 需求

- 百万级视频
- 100w+ DAU
- 流畅播放
- 广告插入

### 架构

```
内容生产 → 转码 → 分发 → 播放 → 数据回流
   ↓        ↓      ↓        ↓       ↓
  源        CDN    CDN    客户端   分析
  视频     切片   多端   实时统计  算法优化
```

### 关键技术

#### 1. 转码 + ABR

```
源视频 (原画)
  ↓
转码集群
  ├─ 1080p H.264 (4Mbps)
  ├─ 720p H.264 (2Mbps)
  ├─ 540p H.265 (1Mbps)
  └─ 360p H.264 (500k)
  
生成 HLS：
  master.m3u8
  playlist_1080p.m3u8
  playlist_720p.m3u8
  ...
```

#### 2. 播放优化

```javascript
// 首屏优化
player.preload('next-video');     // 预加载下一段
player.bufferAhead(20);            // 缓冲 20s
player.startFrom('first-frame');   // 首帧不缓冲
player.abr.fastSwitch();           // 快速切换清晰度
```

#### 3. CDN 调度

```
用户请求 → DNS 解析
            ↓
       GeoIP 调度
            ↓
    ┌──────┴──────┐
    ↓             ↓
  边缘 PoP    区域 PoP
    ↓             ↓
  缓存命中    回源拉取
                       ↓
                   源站 (S3 / OSS)
```

## 🎬 五、监控系统设计

### 需求

- 10000+ 摄像头
- 智能分析
- 实时报警
- 录像回放

### 架构

```
┌───────────────────────────────────────┐
│ 设备层                                  │
│ IPC / NVR / 编码器 / DVR              │
└──────┬──────────────────────────────┘
       ↓
┌───────────────────────────────────────┐
│ 接入层                                  │
│ GB28181 / RTSP / ONVIF / SDK          │
└──────┬──────────────────────────────┘
       ↓
┌───────────────────────────────────────┐
│ 流媒体服务器                            │
│ SRS / ZLMediaKit / 自研                 │
│ ├─ 录像                                │
│ ├─ 截图                                │
│ ├─ RTMP/HLS/WebRTC 输出                │
│ └─ 报警事件                            │
└──────┬──────────────────────────────┘
       ↓
┌───────────────────────────────────────┐
│ AI 智能分析                              │
│ 人脸 / 车辆 / 行为 / 越界               │
└──────┬──────────────────────────────┘
       ↓
┌───────────────────────────────────────┐
│ 应用层                                  │
│ 客户端 / 大屏 / 报警 / 录像回放         │
└───────────────────────────────────────┘
```

### 重点

1. **GB28181 接入**：SIP / RTP 流
2. **录像存储**：HLS / MP4 / 自适应
3. **AI 推理**：CPU / GPU / NPU
4. **事件总线**：Kafka / Pulsar
5. **分布式**：上百路 → 千路 → 万路

## 📊 六、系统设计通用思路

### 设计框架（4S 方法）

1. **Scenario 场景**：
   - 什么功能？
   - 多大规模？
   - 什么场景？

2. **Service 服务**：
   - 拆分成哪些服务？
   - 服务关系？

3. **Storage 存储**：
   - 数据怎么存？
   - 什么数据库？

4. **Scale 扩展**：
   - 性能瓶颈？
   - 怎么应对？

### 关键点

#### 性能
- **缓存优先**（CDN / Redis）
- **异步化**（消息队列）
- **并行化**（多线程 / 多机）
- **限流熔断**

#### 可靠性
- **冗余设计**（双机 / 多活）
- **降级方案**（限功能 + 兜底）
- **故障转移**（自动 + 手动）
- **数据备份**（冷热分层）

#### 可扩展性
- **微服务化**
- **消息驱动**
- **数据库分库分表**
- **中间件解耦**

#### 安全性
- **身份认证**（JWT / OAuth）
- **权限控制**（RBAC / ABAC）
- **数据加密**（TLS / AES）
- **限流防刷**（Token 桶）

## 🎓 高频设计题清单

### 简单题（30min 内）
1. 视频上传系统
2. 视频播放器
3. 实时直播

### 中等题（45-60min）
4. 短视频推荐
5. 多人会议
6. 智能审核
7. CDN 分发系统

### 复杂题（60min+）
8. 视频网站全栈架构
9. 跨国直播系统
10. 数字人直播平台

## 📝 答题模板（伪代码）

```python
# 1. 需求澄清
print("澄清需求：")
print("- 多少用户？")
print("- 多大带宽？")
print("- 什么延迟要求？")
print("- 是否需要扩展？")

# 2. 概要设计
print("\n架构：")
print("- 客户端")
print("- 接入层")
print("- 服务层")
print("- 数据层")

# 3. 详细设计
print("\n关键技术：")
print("- 编码 / 转码")
print("- CDN 分发")
print("- 数据持久化")

# 4. 性能与可用性
print("\n可靠性：")
print("- 多活")
print("- 降级")
print("- 监控")

# 5. 反问
print("\n反问环节：")
print("- 当前架构最大挑战？")
print("- 团队技术栈偏好？")
print("- 业务发展前景？")
```


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料
<!-- auto-enrich:do-not-edit -->
