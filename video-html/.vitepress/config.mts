import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

export default withMermaid(defineConfig({
  mermaid: {
    theme: 'default'
  },
  base: '/video/',
  title: '视频处理 / 编解码 / AI 视频算法 知识图谱',
  description: '系统化学习视频处理 - 编解码原理 / FFmpeg / 流媒体 / AI 视频算法 - 12 大类 · 50+ 节点 · 60+ 内容页',
  lang: 'zh-CN',
  lastUpdated: true,
  srcDir: 'docs',
  cleanUrls: false,
  ignoreDeadLinks: true,
  head: [
    ['link', { rel: 'apple-touch-icon', href: '/apple-touch-icon.png', sizes: '180x180' }],
    ['link', { rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' }],
    ['link', { rel: 'icon', href: '/favicon.ico', type: 'image/x-icon' }],
    ['meta', { name: 'theme-color', content: '#a855f7' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:locale', content: 'zh_CN' }]  ],
  themeConfig: {
    siteTitle: '视频全栈',
    nav: [

      { text: '🏠 门户', link: 'https://java-px.bot.cd/', target: '_blank' },
{ text: '首页', link: '/' },
      { text: '知识图谱', link: '/graph' },
      { text: '思维导图', link: '/mindmap' },
      { text: '学习路径', link: '/path' },
      { text: '速记卡', link: '/cheatsheet' },
      {
        text: '更多站点',
        items: [
          { text: 'AI 工具 / 大模型', link: 'https://java-px.bot.cd/ai/' },
          { text: '企业级架构', link: 'https://java-px.bot.cd/architecture/' },
          { text: '大数据', link: 'https://java-px.bot.cd/bigdata/' },
          { text: '云原生 / Docker / K8s', link: 'https://java-px.bot.cd/cloud-native/' },
          { text: 'ElasticSearch', link: 'https://java-px.bot.cd/es/' },
          { text: '前端 & Node', link: 'https://java-px.bot.cd/frontend/' },
          { text: 'Java 语言', link: 'https://java-px.bot.cd/java-language/' },
          { text: 'Java Web 开发', link: 'https://java-px.bot.cd/java/' },
          { text: 'Kafka', link: 'https://java-px.bot.cd/kafka/' },
          { text: 'Linux 服务器', link: 'https://java-px.bot.cd/linux/' },
          { text: 'MySQL', link: 'https://java-px.bot.cd/mysql/' },
          { text: 'Python', link: 'https://java-px.bot.cd/python/' },
          { text: 'Redis', link: 'https://java-px.bot.cd/redis/' },
          { text: '微服务 / Spring Cloud', link: 'https://java-px.bot.cd/cloud/' },
          { text: '计算机网络', link: 'https://java-px.bot.cd/network/' },
          { text: '文件系统与存储', link: 'https://java-px.bot.cd/filesystem/' },
          { text: '在线工具', link: 'https://java-px.bot.cd/tools/' }
        ]
      }
    ],
    sidebar: {
      '/': [
        {
          text: '🎯 开始',
          items: [
            { text: '📖 学习路径', link: '/path' },
            { text: '🧠 知识图谱', link: '/graph' },
            { text: '🧭 思维导图', link: '/mindmap' },
            { text: '⚡ 速记卡', link: '/cheatsheet' }
          ]
        },
        {
          text: '🎬 视频基础',
          items: [
            { text: '视频本质 - 像素与帧', link: '/01-basics/video-essence' },
            { text: '色彩空间 YUV/RGB', link: '/01-basics/color-space' },
            { text: '分辨率 / 帧率 / 码率', link: '/01-basics/resolution-fps' },
            { text: '容器格式 MP4/AVI/MKV', link: '/01-basics/container-format' },
            { text: '编解码概览', link: '/01-basics/codec-overview' }
          ]
        },
        {
          text: '🧮 编解码原理',
          items: [
            { text: '帧内预测', link: '/02-codec/intra-prediction' },
            { text: '帧间预测', link: '/02-codec/inter-prediction' },
            { text: 'DCT 变换与量化', link: '/02-codec/dct-quant' },
            { text: '熵编码 CABAC/CAVLC', link: '/02-codec/entropy-codec' },
            { text: '运动估计与补偿', link: '/02-codec/me-mc' },
            { text: '环路滤波', link: '/02-codec/loop-filter' }
          ]
        },
        {
          text: '🎥 主流编码标准',
          items: [
            { text: 'H.264 / AVC', link: '/03-codecs/h264' },
            { text: 'H.265 / HEVC', link: '/03-codecs/h265' },
            { text: 'AV1', link: '/03-codecs/av1' },
            { text: 'VP9 / VP8', link: '/03-codecs/vp9' },
            { text: '音频编码 AAC/MP3', link: '/03-codecs/audio-codec' }
          ]
        },
        {
          text: '🎨 视频处理算法',
          items: [
            { text: '缩放插值', link: '/04-algorithm/scaling' },
            { text: '去噪算法', link: '/04-algorithm/denoise' },
            { text: '去隔行', link: '/04-algorithm/deinterlace' },
            { text: '锐化算法', link: '/04-algorithm/sharpen' },
            { text: '色彩转换', link: '/04-algorithm/color-convert' },
            { text: '帧率转换 插帧', link: '/04-algorithm/frc' },
            { text: '超分辨率 SR', link: '/04-algorithm/super-res' }
          ]
        },
        {
          text: '📡 流媒体协议',
          items: [
            { text: 'RTMP 实时消息', link: '/05-protocol/rtmp' },
            { text: 'HLS HTTP 切片', link: '/05-protocol/hls' },
            { text: 'DASH 自适应', link: '/05-protocol/dash' },
            { text: 'WebRTC 实时通信', link: '/05-protocol/webrtc' },
            { text: 'RTSP / SRT', link: '/05-protocol/rtsp-srt' },
            { text: 'CDN 分发架构', link: '/05-protocol/cdn-arch' }
          ]
        },
        {
          text: '🛠️ 工具实战',
          items: [
            { text: 'FFmpeg 入门精通', link: '/06-tools/ffmpeg' },
            { text: 'GStreamer 框架', link: '/06-tools/gstreamer' },
            { text: 'OpenCV 视觉库', link: '/06-tools/opencv' },
            { text: 'MoviePy Python', link: '/06-tools/moviepy' },
            { text: 'MediaInfo 元数据', link: '/06-tools/mediainfo' },
            { text: 'HandBrake 转码', link: '/06-tools/handbrake' }
          ]
        },
        {
          text: '🤖 AI 视频处理',
          items: [
            { text: 'AI 超分辨率', link: '/07-ai/super-res-ai' },
            { text: '视频修复 Inpainting', link: '/07-ai/inpainting' },
            { text: 'AI 插帧 RIFE', link: '/07-ai/interpolation-ai' },
            { text: '视频分割 / 抠像', link: '/07-ai/segmentation' },
            { text: 'AI 视频生成 Sora', link: '/07-ai/generation' },
            { text: '数字人 / 虚拟主播', link: '/07-ai/digital-human' },
            { text: '唇形同步 Wav2Lip', link: '/07-ai/lip-sync' }
          ]
        },
        {
          text: '⚡ 性能优化',
          items: [
            { text: '硬件加速 NVENC/QSV', link: '/08-perf/nvenc-qsv' },
            { text: 'GPU 处理 CUDA', link: '/08-perf/gpu-cuda' },
            { text: '多线程并行', link: '/08-perf/threading' },
            { text: '实时流性能', link: '/08-perf/realtime' }
          ]
        },
        {
          text: '☁️ 云视频服务',
          items: [
            { text: '阿里云媒体处理', link: '/09-cloud/aliyun-mps' },
            { text: '腾讯云媒体处理', link: '/09-cloud/tencent-mps' },
            { text: 'AWS Elemental', link: '/09-cloud/aws-media' },
            { text: 'Serverless 视频', link: '/09-cloud/serverless' }
          ]
        },
        {
          text: '📱 应用场景',
          items: [
            { text: '短视频处理', link: '/10-application/short-video' },
            { text: '直播技术', link: '/10-application/live' },
            { text: '安防监控', link: '/10-application/surveillance' },
            { text: '视频会议', link: '/10-application/conference' },
            { text: '影视后期', link: '/10-application/post-product' }
          ]
        },
        {
          text: '🏢 企业案例',
          items: [
            { text: 'B 站视频架构', link: '/11-cases/bilibili' },
            { text: '抖音 / TikTok', link: '/11-cases/douyin' },
            { text: '腾讯直播架构', link: '/11-cases/tencent-live' },
            { text: '视频架构演进', link: '/11-cases/video-arch' }
          ]
        },
        {
          text: '🎯 面试 / 实战',
          items: [
            { text: '高频面试题', link: '/12-interview/questions' },
            { text: '场景案例题', link: '/12-interview/cases' },
            { text: '编码对比表', link: '/12-interview/comparison' }
          ]
        }
      ]
    },
    socialLinks: [{ icon: 'github', link: 'https://github.com' }],
    footer: {
      message: '视频处理全栈 - 编解码原理 / FFmpeg / AI 视频 · 🏠 <a href="https://java-px.bot.cd/" target="_blank">门户首页</a>',
      copyright: 'MIT License'
    },
    outline: { level: [2, 3], label: '页面大纲' },
    docFooter: { prev: '上一篇', next: '下一篇' },

    search: { provider: 'local' },
  }
}))
