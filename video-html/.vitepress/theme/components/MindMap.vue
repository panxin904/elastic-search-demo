<template>
  <div class="mindmap-container">
    <div ref="chartRef" :style="{ width: '100%', height: height + 'px' }"></div>
    <div class="mm-toolbar">
      <button class="mm-toolbar__btn" @click="expandAll">📖 全部展开</button>
      <button class="mm-toolbar__btn" @click="collapseAll">📕 全部折叠</button>
      <button class="mm-toolbar__btn" @click="resetView">🎯 重置视角</button>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts/core'
import { TreeChart } from 'echarts/charts'
import { TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
echarts.use([TreeChart, TooltipComponent, CanvasRenderer])

const props = defineProps({ height: { type: Number, default: 720 } })
const chartRef = ref(null)
let chart = null

const colors = {
  '基础': '#6d28d9', '原理': '#be185d', '编码': '#c2410c',
  '算法': '#0e7490', '协议': '#1d4ed8', '工具': '#16a34a',
  'AI': '#a21caf', '性能': '#b45309', '云': '#b91c1c',
  '应用': '#5b21b6', '案例': '#047857', '面试': '#7c3aed'
}

const treeData = {
  name: '视频处理', itemStyle: { color: '#a855f7' },
  children: [
    { name: '1. 视频基础', itemStyle: { color: colors['基础'] }, children: [
      { name: '视频本质' }, { name: '色彩空间' }, { name: '分辨率/帧率' }, { name: '容器格式' }, { name: '编解码概览' }
    ]},
    { name: '2. 编解码原理', itemStyle: { color: colors['原理'] }, children: [
      { name: '帧内预测' }, { name: '帧间预测' }, { name: 'DCT 量化' }, { name: '熵编码' }, { name: '运动估计' }, { name: '环路滤波' }
    ]},
    { name: '3. 主流编码', itemStyle: { color: colors['编码'] }, children: [
      { name: 'H.264' }, { name: 'H.265' }, { name: 'AV1' }, { name: 'VP9' }, { name: '音频编码' }
    ]},
    { name: '4. 视频算法', itemStyle: { color: colors['算法'] }, children: [
      { name: '缩放插值' }, { name: '去噪' }, { name: '去隔行' }, { name: '锐化' }, { name: '色彩转换' }, { name: '帧率转换' }, { name: '超分辨率' }
    ]},
    { name: '5. 流媒体协议', itemStyle: { color: colors['协议'] }, children: [
      { name: 'RTMP' }, { name: 'HLS' }, { name: 'DASH' }, { name: 'WebRTC' }, { name: 'RTSP/SRT' }, { name: 'CDN 架构' }
    ]},
    { name: '6. 工具实战', itemStyle: { color: colors['工具'] }, children: [
      { name: 'FFmpeg' }, { name: 'GStreamer' }, { name: 'OpenCV' }, { name: 'MoviePy' }, { name: 'MediaInfo' }, { name: 'HandBrake' }
    ]},
    { name: '7. AI 视频', itemStyle: { color: colors['AI'] }, children: [
      { name: 'AI 超分' }, { name: '视频修复' }, { name: 'AI 插帧' }, { name: '视频分割' }, { name: '视频生成' }, { name: '数字人' }, { name: '唇形同步' }
    ]},
    { name: '8. 性能优化', itemStyle: { color: colors['性能'] }, children: [
      { name: '硬件加速' }, { name: 'GPU CUDA' }, { name: '多线程' }, { name: '实时性能' }
    ]},
    { name: '9. 云视频', itemStyle: { color: colors['云'] }, children: [
      { name: '阿里云' }, { name: '腾讯云' }, { name: 'AWS' }, { name: 'Serverless' }
    ]},
    { name: '10. 应用场景', itemStyle: { color: colors['应用'] }, children: [
      { name: '短视频' }, { name: '直播' }, { name: '安防' }, { name: '视频会议' }, { name: '影视后期' }
    ]},
    { name: '11. 企业案例', itemStyle: { color: colors['案例'] }, children: [
      { name: 'B 站' }, { name: '抖音' }, { name: '腾讯直播' }, { name: '架构演进' }
    ]},
    { name: '12. 面试实战', itemStyle: { color: colors['面试'] }, children: [
      { name: '高频题' }, { name: '案例题' }, { name: '对比表' }
    ]}
  ]
}

function init() {
  chart = echarts.init(chartRef.value)
  chart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}' },
    series: [{
      type: 'tree',
      data: [treeData],
      top: '5%', left: '12%', bottom: '5%', right: '15%',
      symbolSize: 12,
      label: { position: 'left', verticalAlign: 'middle', align: 'right', fontSize: 12, color: '#374151' },
      leaves: { label: { position: 'right', verticalAlign: 'middle', align: 'left' } },
      expandAndCollapse: true,
      initialTreeDepth: 2,
      lineStyle: { color: '#d4d4d8', curveness: 0.5 },
      animationDurationUpdate: 600
    }]
  })
  window.addEventListener('resize', resize)
}

function resize() { chart && chart.resize() }
function expandAll() {
  const list = []
  chart && chart._api && chart._api.dispatchAction({ type: 'treeExpandAndCollapse', list })
  if (chart) { try { chart.setOption({ series: [{ initialTreeDepth: -1 }] }) } catch(e){} }
}
function collapseAll() {
  if (chart) { try { chart.setOption({ series: [{ initialTreeDepth: 1 }] }) } catch(e){} }
}
function resetView() {
  chart && chart.dispatchAction({ type: 'graphRoam' })
}

onMounted(() => setTimeout(init, 50))
onBeforeUnmount(() => { window.removeEventListener('resize', resize); chart && chart.dispose() })
</script>