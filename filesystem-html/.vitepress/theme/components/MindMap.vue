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

const props = defineProps({ height: { type: Number, default: 760 } })
const chartRef = ref(null)
let chart = null

const colors = {
  '基础': '#0f766e', '本地盘': '#059669', '分布式': '#0d9488',
  '对象': '#0891b2', '网络': '#2563eb', '云原生': '#4f46e5',
  '容器': '#d97706', '工具': '#92400e', '性能': '#ea580c',
  '安全': '#dc2626', '备份': '#be185d', '案例': '#7e22ce',
  '面试': '#c026d3'
}

const treeData = {
  name: '文件全栈', itemStyle: { color: '#0f766e' },
  children: [
    { name: '1. 文件系统基础', itemStyle: { color: colors['基础'] }, children: [
      { name: 'inode/dentry' }, { name: 'VFS' }, { name: '文件描述符' },
      { name: 'Page Cache' }, { name: '挂载' }, { name: '日志' }, { name: '路径解析' }
    ]},
    { name: '2. 本地盘 FS', itemStyle: { color: colors['本地盘'] }, children: [
      { name: 'ext4' }, { name: 'XFS' }, { name: 'Btrfs' },
      { name: 'ZFS' }, { name: 'NTFS/FAT' }, { name: 'APFS' }, { name: '对比选型' }
    ]},
    { name: '3. 分布式 FS', itemStyle: { color: colors['分布式'] }, children: [
      { name: 'HDFS' }, { name: 'CephFS' }, { name: 'GlusterFS' },
      { name: 'JuiceFS' }, { name: 'MooseFS' }, { name: 'Lustre' }, { name: '对比' }
    ]},
    { name: '4. 对象存储', itemStyle: { color: colors['对象'] }, children: [
      { name: 'S3 协议' }, { name: 'MinIO' }, { name: 'OSS' },
      { name: 'COS' }, { name: '纠删码' }, { name: '生命周期' }, { name: '一致性' }
    ]},
    { name: '5. 网络协议', itemStyle: { color: colors['网络'] }, children: [
      { name: 'NFS' }, { name: 'SMB' }, { name: 'WebDAV' }, { name: 'FTP/SFTP' }, { name: 'rsync' }
    ]},
    { name: '6. 云原生存储', itemStyle: { color: colors['云原生'] }, children: [
      { name: 'CSI' }, { name: 'PV/PVC' }, { name: '动态配置' },
      { name: 'Rook' }, { name: 'Longhorn' }, { name: 'OpenEBS' }, { name: '快照' }
    ]},
    { name: '7. 容器 FS', itemStyle: { color: colors['容器'] }, children: [
      { name: 'OverlayFS' }, { name: 'Docker 分层' }, { name: 'containerd' }, { name: 'BuildKit' }, { name: '存储驱动' }
    ]},
    { name: '8. 工具集', itemStyle: { color: colors['工具'] }, children: [
      { name: 'FUSE' }, { name: 'debugfs' }, { name: 'rsync' },
      { name: 'find/fd' }, { name: 'inotify' }, { name: 'du/df' }, { name: 'lsof' }
    ]},
    { name: '9. 性能调优', itemStyle: { color: colors['性能'] }, children: [
      { name: 'IO 调度' }, { name: 'Page Cache 调优' }, { name: 'fsync' },
      { name: 'readahead' }, { name: 'Direct I/O' }, { name: '调优方法论' }
    ]},
    { name: '10. 安全权限', itemStyle: { color: colors['安全'] }, children: [
      { name: 'POSIX' }, { name: 'ACL' }, { name: 'xattr' }, { name: '加密' }, { name: 'auditd' }
    ]},
    { name: '11. 备份快照', itemStyle: { color: colors['备份'] }, children: [
      { name: '快照' }, { name: 'Borg' }, { name: 'restic' }, { name: '3-2-1' }, { name: 'RPO/RTO' }
    ]},
    { name: '12. 企业案例', itemStyle: { color: colors['案例'] }, children: [
      { name: 'Netflix S3' }, { name: 'ByteDance' }, { name: 'CERN' }, { name: 'Snowflake' }, { name: 'Meta' }
    ]},
    { name: '13. 面试对比', itemStyle: { color: colors['面试'] }, children: [
      { name: '高频题' }, { name: '系统设计' }, { name: '对比表' }
    ]}
  ]
}

const baseOption = {
  tooltip: { trigger: 'item', triggerOn: 'mousemove' },
  series: [{
    type: 'tree',
    data: [treeData],
    symbolSize: 9,
    orient: 'LR',
    roam: true,
    initialTreeDepth: -1,
    expandAndCollapse: true,
    animationDuration: 600,
    label: {
      position: 'left', verticalAlign: 'middle', align: 'right',
      fontSize: 12, color: '#334155', fontWeight: 600
    },
    leaves: { label: { position: 'right', verticalAlign: 'middle', align: 'left' } },
    lineStyle: { color: '#94a3b8', width: 1.5, curveness: 0.5 }
  }]
}

onMounted(() => {
  chart = echarts.init(chartRef.value, null, { renderer: 'canvas' })
  chart.setOption(baseOption)
  window.addEventListener('resize', resize)
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  chart?.dispose()
})
const resize = () => chart?.resize()

const collapseAll = () => {
  const newData = JSON.parse(JSON.stringify(treeData))
  const collapse = (n) => {
    if (n.children) { n.collapsed = true; n.children.forEach(collapse) }
  }
  collapse(newData)
  chart.setOption({ series: [{ data: [newData] }] }, true)
}
const expandAll = () => {
  const newData = JSON.parse(JSON.stringify(treeData))
  const expand = (n) => { if (n.children) { delete n.collapsed; n.children.forEach(expand) } }
  expand(newData)
  chart.setOption({ series: [{ data: [newData] }] }, true)
}
const resetView = () => {
  chart.setOption(baseOption, true)
  chart.dispatchAction({ type: 'graphRoam', roamDelta: 0 })
}
</script>