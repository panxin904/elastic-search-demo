<template>
  <div class="kg-container">
    <div ref="chartRef" :style="{ width: '100%', height: height + 'px' }"></div>
    <div class="kg-toolbar">
      <button class="kg-toolbar__btn" @click="resetLayout">🔄 重置布局</button>
      <span class="kg-toolbar__legend">
        <span><span class="kg-legend-dot" style="background: #6d28d9"></span>基础</span>
        <span><span class="kg-legend-dot" style="background: #be185d"></span>原理</span>
        <span><span class="kg-legend-dot" style="background: #c2410c"></span>编码</span>
        <span><span class="kg-legend-dot" style="background: #0e7490"></span>算法</span>
        <span><span class="kg-legend-dot" style="background: #1d4ed8"></span>协议</span>
        <span><span class="kg-legend-dot" style="background: #16a34a"></span>工具</span>
        <span><span class="kg-legend-dot" style="background: #a21caf"></span>AI</span>
        <span><span class="kg-legend-dot" style="background: #b45309"></span>性能</span>
        <span><span class="kg-legend-dot" style="background: #b91c1c"></span>云</span>
        <span><span class="kg-legend-dot" style="background: #5b21b6"></span>应用</span>
        <span><span class="kg-legend-dot" style="background: #047857"></span>案例</span>
        <span><span class="kg-legend-dot" style="background: #7c3aed"></span>面试</span>
      </span>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts/core'
import { GraphChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
echarts.use([GraphChart, TitleComponent, TooltipComponent, CanvasRenderer])

const props = defineProps({ height: { type: Number, default: 820 } })
const chartRef = ref(null)
let chart = null

const categoryColors = {
  basics: '#6d28d9', codec: '#be185d', codecs: '#c2410c',
  algorithm: '#0e7490', protocol: '#1d4ed8', tools: '#16a34a',
  ai: '#a21caf', perf: '#b45309', cloud: '#b91c1c',
  app: '#5b21b6', cases: '#047857', interview: '#7c3aed'
}

const graphData = {
  nodes: [
    { name: '视频本质', category: 'basics', link: '/01-basics/video-essence', value: 8 },
    { name: '色彩空间', category: 'basics', link: '/01-basics/color-space', value: 7 },
    { name: '分辨率帧率', category: 'basics', link: '/01-basics/resolution-fps', value: 6 },
    { name: '容器格式', category: 'basics', link: '/01-basics/container-format', value: 7 },
    { name: '编解码概览', category: 'basics', link: '/01-basics/codec-overview', value: 8 },
    { name: '帧内预测', category: 'codec', link: '/02-codec/intra-prediction', value: 7 },
    { name: '帧间预测', category: 'codec', link: '/02-codec/inter-prediction', value: 7 },
    { name: 'DCT 量化', category: 'codec', link: '/02-codec/dct-quant', value: 7 },
    { name: '熵编码', category: 'codec', link: '/02-codec/entropy-codec', value: 6 },
    { name: '运动估计', category: 'codec', link: '/02-codec/me-mc', value: 7 },
    { name: '环路滤波', category: 'codec', link: '/02-codec/loop-filter', value: 5 },
    { name: 'H.264', category: 'codecs', link: '/03-codecs/h264', value: 9 },
    { name: 'H.265', category: 'codecs', link: '/03-codecs/h265', value: 9 },
    { name: 'AV1', category: 'codecs', link: '/03-codecs/av1', value: 8 },
    { name: 'VP9', category: 'codecs', link: '/03-codecs/vp9', value: 7 },
    { name: '音频编码', category: 'codecs', link: '/03-codecs/audio-codec', value: 6 },
    { name: '缩放插值', category: 'algorithm', link: '/04-algorithm/scaling', value: 6 },
    { name: '去噪算法', category: 'algorithm', link: '/04-algorithm/denoise', value: 6 },
    { name: '去隔行', category: 'algorithm', link: '/04-algorithm/deinterlace', value: 5 },
    { name: '锐化', category: 'algorithm', link: '/04-algorithm/sharpen', value: 5 },
    { name: '色彩转换', category: 'algorithm', link: '/04-algorithm/color-convert', value: 6 },
    { name: '帧率转换', category: 'algorithm', link: '/04-algorithm/frc', value: 6 },
    { name: '超分辨率', category: 'algorithm', link: '/04-algorithm/super-res', value: 7 },
    { name: 'RTMP', category: 'protocol', link: '/05-protocol/rtmp', value: 7 },
    { name: 'HLS', category: 'protocol', link: '/05-protocol/hls', value: 8 },
    { name: 'DASH', category: 'protocol', link: '/05-protocol/dash', value: 7 },
    { name: 'WebRTC', category: 'protocol', link: '/05-protocol/webrtc', value: 8 },
    { name: 'RTSP/SRT', category: 'protocol', link: '/05-protocol/rtsp-srt', value: 6 },
    { name: 'CDN 架构', category: 'protocol', link: '/05-protocol/cdn-arch', value: 7 },
    { name: 'FFmpeg', category: 'tools', link: '/06-tools/ffmpeg', value: 10 },
    { name: 'GStreamer', category: 'tools', link: '/06-tools/gstreamer', value: 6 },
    { name: 'OpenCV', category: 'tools', link: '/06-tools/opencv', value: 7 },
    { name: 'MoviePy', category: 'tools', link: '/06-tools/moviepy', value: 5 },
    { name: 'MediaInfo', category: 'tools', link: '/06-tools/mediainfo', value: 5 },
    { name: 'HandBrake', category: 'tools', link: '/06-tools/handbrake', value: 5 },
    { name: 'AI 超分', category: 'ai', link: '/07-ai/super-res-ai', value: 8 },
    { name: '视频修复', category: 'ai', link: '/07-ai/inpainting', value: 7 },
    { name: 'AI 插帧', category: 'ai', link: '/07-ai/interpolation-ai', value: 7 },
    { name: '视频分割', category: 'ai', link: '/07-ai/segmentation', value: 7 },
    { name: '视频生成', category: 'ai', link: '/07-ai/generation', value: 9 },
    { name: '数字人', category: 'ai', link: '/07-ai/digital-human', value: 8 },
    { name: '唇形同步', category: 'ai', link: '/07-ai/lip-sync', value: 6 },
    { name: '硬件加速', category: 'perf', link: '/08-perf/nvenc-qsv', value: 7 },
    { name: 'GPU CUDA', category: 'perf', link: '/08-perf/gpu-cuda', value: 7 },
    { name: '多线程', category: 'perf', link: '/08-perf/threading', value: 6 },
    { name: '实时性能', category: 'perf', link: '/08-perf/realtime', value: 6 },
    { name: '阿里云', category: 'cloud', link: '/09-cloud/aliyun-mps', value: 6 },
    { name: '腾讯云', category: 'cloud', link: '/09-cloud/tencent-mps', value: 6 },
    { name: 'AWS', category: 'cloud', link: '/09-cloud/aws-media', value: 6 },
    { name: 'Serverless', category: 'cloud', link: '/09-cloud/serverless', value: 5 },
    { name: '短视频', category: 'app', link: '/10-application/short-video', value: 7 },
    { name: '直播', category: 'app', link: '/10-application/live', value: 8 },
    { name: '安防', category: 'app', link: '/10-application/surveillance', value: 6 },
    { name: '视频会议', category: 'app', link: '/10-application/conference', value: 7 },
    { name: '影视后期', category: 'app', link: '/10-application/post-product', value: 6 },
    { name: 'B站', category: 'cases', link: '/11-cases/bilibili', value: 7 },
    { name: '抖音', category: 'cases', link: '/11-cases/douyin', value: 7 },
    { name: '腾讯直播', category: 'cases', link: '/11-cases/tencent-live', value: 6 },
    { name: '架构演进', category: 'cases', link: '/11-cases/video-arch', value: 6 },
    { name: '高频面试', category: 'interview', link: '/12-interview/questions', value: 7 },
    { name: '案例题', category: 'interview', link: '/12-interview/cases', value: 6 },
    { name: '对比表', category: 'interview', link: '/12-interview/comparison', value: 6 }
  ],
  links: [
    { source: '视频本质', target: '色彩空间' }, { source: '视频本质', target: '分辨率帧率' },
    { source: '视频本质', target: '容器格式' }, { source: '容器格式', target: '编解码概览' },
    { source: '编解码概览', target: '帧内预测' }, { source: '编解码概览', target: '帧间预测' },
    { source: '编解码概览', target: 'DCT 量化' }, { source: '编解码概览', target: '熵编码' },
    { source: '帧间预测', target: '运动估计' }, { source: 'DCT 量化', target: '环路滤波' },
    { source: '帧内预测', target: 'H.264' }, { source: '帧间预测', target: 'H.264' },
    { source: 'H.264', target: 'H.265' }, { source: 'H.265', target: 'AV1' },
    { source: 'AV1', target: 'VP9' }, { source: 'H.264', target: '音频编码' },
    { source: '分辨率帧率', target: '缩放插值' }, { source: '分辨率帧率', target: '帧率转换' },
    { source: '色彩空间', target: '色彩转换' }, { source: '色彩空间', target: '去隔行' },
    { source: 'DCT 量化', target: '去噪算法' }, { source: '超分辨率', target: 'AI 超分' },
    { source: '容器格式', target: 'RTMP' }, { source: '容器格式', target: 'HLS' },
    { source: 'HLS', target: 'DASH' }, { source: 'RTMP', target: 'WebRTC' },
    { source: 'RTMP', target: 'RTSP/SRT' }, { source: 'WebRTC', target: '视频会议' },
    { source: 'HLS', target: 'CDN 架构' }, { source: 'DASH', target: 'CDN 架构' },
    { source: '编解码概览', target: 'FFmpeg' }, { source: 'FFmpeg', target: 'GStreamer' },
    { source: 'FFmpeg', target: 'OpenCV' }, { source: 'FFmpeg', target: 'MoviePy' },
    { source: 'FFmpeg', target: 'MediaInfo' }, { source: 'FFmpeg', target: 'HandBrake' },
    { source: 'OpenCV', target: '视频分割' }, { source: 'FFmpeg', target: '硬件加速' },
    { source: '硬件加速', target: 'GPU CUDA' }, { source: '硬件加速', target: '实时性能' },
    { source: '多线程', target: '实时性能' }, { source: '视频修复', target: 'AI 插帧' },
    { source: 'AI 超分', target: '视频生成' }, { source: '视频分割', target: '数字人' },
    { source: '视频生成', target: '数字人' }, { source: '数字人', target: '唇形同步' },
    { source: 'FFmpeg', target: '阿里云' }, { source: 'FFmpeg', target: '腾讯云' },
    { source: 'FFmpeg', target: 'AWS' }, { source: 'FFmpeg', target: 'Serverless' },
    { source: '短视频', target: '抖音' }, { source: '直播', target: '腾讯直播' },
    { source: '直播', target: 'B站' }, { source: '影视后期', target: 'B站' },
    { source: '架构演进', target: 'B站' }, { source: '架构演进', target: '抖音' },
    { source: '高频面试', target: '案例题' }, { source: '案例题', target: '对比表' }
  ]
}

const categories = Object.keys(categoryColors).map(k => ({ name: k, itemStyle: { color: categoryColors[k] } }))

function init() {
  chart = echarts.init(chartRef.value)
  chart.setOption({
    tooltip: {
      formatter: p => {
        const c = categoryColors[p.data.category]
        return `<span style="display:inline-block;width:10px;height:10px;background:${c};border-radius:50%;margin-right:6px"></span>${p.data.name}<br/><span style="color:#999;font-size:11px">点击跳转到文档</span>`
      }
    },
    legend: [{ data: categories.map(c => c.name), show: false }],
    series: [{
      type: 'graph',
      layout: 'force',
      roam: true,
      draggable: true,
      categories,
      force: { repulsion: 220, edgeLength: 80, gravity: 0.05 },
      label: { show: true, position: 'right', fontSize: 11, color: '#374151' },
      edgeSymbol: ['none', 'none'],
      lineStyle: { color: '#d4d4d8', width: 1, curveness: 0.05, opacity: 0.6 },
      emphasis: { focus: 'adjacency', lineStyle: { width: 2 } },
      data: graphData.nodes,
      links: graphData.links
    }]
  })
  chart.on('click', params => {
    if (params.data && params.data.link) {
      window.location.href = params.data.link
    }
  })
  window.addEventListener('resize', resize)
}

function resize() { chart && chart.resize() }
function resetLayout() { chart && chart.dispatchAction({ type: 'graphRoam' }) }

onMounted(() => setTimeout(init, 50))
onBeforeUnmount(() => { window.removeEventListener('resize', resize); chart && chart.dispose() })
</script>