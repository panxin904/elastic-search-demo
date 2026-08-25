---
layout: home
title: 视频处理知识库
hero:
  name: 视频处理
  text: 编解码原理 · AI 视频 · 流媒体协议
  tagline: 系统掌握视频编解码 / FFmpeg / 流媒体协议 / AI 视频算法，构建完整视频工程师能力栈
  actions:
    - theme: brand
      text: 开始学习
      link: /path
    - theme: alt
      text: 知识图谱
      link: /graph
    - theme: alt
      text: 思维导图
      link: /mindmap
    - theme: alt
      text: 速记卡
      link: /cheatsheet
features:
  - icon: 🎬
    title: 视频基础
    details: 像素 / 色彩空间 / 分辨率 / 帧率 / 码率 / 容器格式
    link: /01-basics/video-essence
    linkText: 基础篇
  - icon: 🧮
    title: 编解码原理
    details: 帧内预测 / 帧间预测 / DCT / 熵编码 / 运动估计
    link: /02-codec/intra-prediction
    linkText: 原理篇
  - icon: 🎥
    title: 主流编码
    details: H.264 / H.265 / AV1 / VP9 / 音频编码
    link: /03-codecs/h264
    linkText: 编码篇
  - icon: 🎨
    title: 视频算法
    details: 缩放 / 去噪 / 去隔行 / 锐化 / 帧率转换 / 超分辨率
    link: /04-algorithm/scaling
    linkText: 算法篇
  - icon: 📡
    title: 流媒体协议
    details: RTMP / HLS / DASH / WebRTC / RTSP / CDN 架构
    link: /05-protocol/hls
    linkText: 协议篇
  - icon: 🛠️
    title: 工具实战
    details: FFmpeg / GStreamer / OpenCV / MoviePy / HandBrake
    link: /06-tools/ffmpeg
    linkText: 工具篇
  - icon: 🤖
    title: AI 视频处理
    details: 超分 / 插帧 / 修复 / 分割 / 视频生成 / 数字人 / 唇形
    link: /07-ai/super-res-ai
    linkText: AI 篇
  - icon: ⚡
    title: 性能优化
    details: 硬件加速 NVENC / GPU CUDA / 多线程 / 实时流
    link: /08-perf/nvenc-qsv
    linkText: 性能篇
---

<script setup>
// WhyThisGraph 数据：原写在 :prop="..." 里会触发 Vue 编译错误（多行 YAML 数组），
// 改为 script setup 形式。
const painPoints = [
      "像素 / 色彩 / 帧率 / 容器格式基础概念混？",
      "帧内 / 帧间 / DCT / 熵编码 原理讲不清？",
      "H.264 / H.265 / AV1 / VP9 选哪个？",
      "RTMP / HLS / DASH 流媒体协议区别？",
      "FFmpeg 命令太多记不住？"
    ]
const goals = [
      "视频基础（像素 / 色彩 / 帧率 / 容器）",
      "编解码原理（帧内 / 帧间 / DCT / 熵编码）",
      "主流编码（H.264 / H.265 / AV1 / VP9）",
      "流媒体协议（RTMP / HLS / DASH / WebRTC）",
      "工具实战（FFmpeg / OpenCV / MediaInfo）",
      "AI 视频（超分 / 插帧 / 数字人 / Sora）"
    ]
const relatedSites = [
      { site: "ai", path: "/10-deploy/ollama", label: "AI 推理部署" },
      { site: "frontend", path: "/01-foundation/html", label: "Web 前端" },
      { site: "cloud-native", path: "/06-storage/overview", label: "云原生存储" },
      { site: "go", path: "/02-concurrency/goroutine", label: "Go 高性能" },
      { site: "observability", path: "/05-sre/overview", label: "流媒体监控" }
    ]
</script>

<ClientOnly>
  <WhyThisGraph
    :pain-points="painPoints"
    :goals="goals"
    :related-sites="relatedSites"
    title="🎯 为什么写这个图谱？"
  />
</ClientOnly>


## 关于本站

| 章节 | 内容 | 关键文档 |
| --- | --- | --- |
| [视频基础](/01-basics/video-essence) | 像素 / 色彩 / 帧率 / 容器 | YUV 4:2:0、容器格式 |
| [编解码原理](/02-codec/intra-prediction) | 帧内 / 帧间 / DCT / 熵编码 | 运动估计、环路滤波 |
| [主流编码](/03-codecs/h264) | H.264 / H.265 / AV1 | 编码对比 |
| [视频算法](/04-algorithm/scaling) | 缩放 / 去噪 / 超分 | AI 超分辨率 |
| [流媒体协议](/05-protocol/hls) | RTMP / HLS / DASH | CDN 架构 |
| [工具实战](/06-tools/ffmpeg) | FFmpeg / OpenCV | FFmpeg 命令大全 |
| [AI 视频](/07-ai/super-res-ai) | 超分 / 插帧 / 数字人 | Sora、Real-ESRGAN |
| [性能优化](/08-perf/nvenc-qsv) | 硬件加速 / GPU | NVENC、CUDA |
| [云视频](/09-cloud/aliyun-mps) | 阿里云 / 腾讯云 / AWS | 媒体处理 MPS |
| [应用场景](/10-application/live) | 直播 / 短视频 / 监控 | 短视频处理 |
| [企业案例](/11-cases/bilibili) | B 站 / 抖音 / 腾讯 | 视频架构演进 |
| [面试实战](/12-interview/questions) | 高频题 / 案例 | 编解码对比 |

### 学习建议

- **入门** → [视频基础](/01-basics/video-essence) → [色彩空间](/01-basics/color-space) → [容器格式](/01-basics/container-format) → [编解码概览](/01-basics/codec-overview)
- **音视频工程师** → [编解码原理](/02-codec/intra-prediction) → [H.264](/03-codecs/h264) → [H.265](/03-codecs/h265) → [FFmpeg](/06-tools/ffmpeg) → [硬件加速](/08-perf/nvenc-qsv)
- **直播开发** → [流媒体协议](/05-protocol/rtmp) → [HLS](/05-protocol/hls) → [CDN 架构](/05-protocol/cdn-arch) → [直播应用](/10-application/live)
- **AI 算法** → [超分](/04-algorithm/super-res) → [AI 超分](/07-ai/super-res-ai) → [视频生成](/07-ai/generation) → [数字人](/07-ai/digital-human)
- **面试** → [高频题](/12-interview/questions) → [案例题](/12-interview/cases) → [编码对比](/12-interview/comparison)

## 📚 相关阅读（跨站导航）

<!-- xlink-injected:do-not-edit -->

按主题跨站推荐：

- [ffmpeg-html](https://java-px.bot.cd/ffmpeg-html/)：FFmpeg 命令行
- [frontend](https://java-px.bot.cd/frontend/)：Web 播放器
- [ai](https://java-px.bot.cd/ai/)：视频 AI
- [python](https://java-px.bot.cd/python/)：Python 处理
