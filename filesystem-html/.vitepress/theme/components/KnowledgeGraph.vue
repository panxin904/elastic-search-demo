<template>
  <div class="kg-container">
    <div ref="chartRef" :style="{ width: '100%', height: height + 'px' }"></div>
    <div class="kg-toolbar">
      <button class="kg-toolbar__btn" @click="resetLayout">🔄 重置布局</button>
      <span class="kg-toolbar__legend">
        <span><span class="kg-legend-dot" style="background: #0f766e"></span>基础</span>
        <span><span class="kg-legend-dot" style="background: #059669"></span>本地盘</span>
        <span><span class="kg-legend-dot" style="background: #0d9488"></span>分布式</span>
        <span><span class="kg-legend-dot" style="background: #0891b2"></span>对象</span>
        <span><span class="kg-legend-dot" style="background: #2563eb"></span>网络</span>
        <span><span class="kg-legend-dot" style="background: #4f46e5"></span>云原生</span>
        <span><span class="kg-legend-dot" style="background: #d97706"></span>容器</span>
        <span><span class="kg-legend-dot" style="background: #92400e"></span>工具</span>
        <span><span class="kg-legend-dot" style="background: #ea580c"></span>性能</span>
        <span><span class="kg-legend-dot" style="background: #dc2626"></span>安全</span>
        <span><span class="kg-legend-dot" style="background: #be185d"></span>备份</span>
        <span><span class="kg-legend-dot" style="background: #7e22ce"></span>案例</span>
        <span><span class="kg-legend-dot" style="background: #c026d3"></span>面试</span>
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

const props = defineProps({ height: { type: Number, default: 880 } })
const chartRef = ref(null)
let chart = null

const categoryColors = {
  basics: '#0f766e', diskFs: '#059669', distributed: '#0d9488',
  object: '#0891b2', network: '#2563eb', cloudNative: '#4f46e5',
  container: '#d97706', tools: '#92400e', perf: '#ea580c',
  security: '#dc2626', backup: '#be185d', cases: '#7e22ce',
  interview: '#c026d3'
}

const graphData = {
  nodes: [
    // 01 basics
    { name: 'inode/dentry', category: 'basics', link: '/01-basics/inode-dentry', value: 9 },
    { name: 'VFS 抽象层', category: 'basics', link: '/01-basics/vfs', value: 9 },
    { name: '文件描述符', category: 'basics', link: '/01-basics/file-descriptor', value: 8 },
    { name: 'Page Cache', category: 'basics', link: '/01-basics/page-cache', value: 9 },
    { name: '挂载 mount', category: 'basics', link: '/01-basics/mount', value: 7 },
    { name: '日志 journal', category: 'basics', link: '/01-basics/journal', value: 7 },
    { name: '路径解析', category: 'basics', link: '/01-basics/path-resolution', value: 6 },
    // 02 disk-fs
    { name: 'ext4', category: 'diskFs', link: '/02-disk-fs/ext4', value: 9 },
    { name: 'XFS', category: 'diskFs', link: '/02-disk-fs/xfs', value: 7 },
    { name: 'Btrfs', category: 'diskFs', link: '/02-disk-fs/btrfs', value: 7 },
    { name: 'ZFS', category: 'diskFs', link: '/02-disk-fs/zfs', value: 8 },
    { name: 'NTFS/FAT', category: 'diskFs', link: '/02-disk-fs/windows-fs', value: 6 },
    { name: 'APFS/HFS+', category: 'diskFs', link: '/02-disk-fs/apple-fs', value: 5 },
    { name: '横向对比', category: 'diskFs', link: '/02-disk-fs/compare', value: 7 },
    // 03 distributed
    { name: 'HDFS', category: 'distributed', link: '/03-distributed/hdfs', value: 9 },
    { name: 'CephFS', category: 'distributed', link: '/03-distributed/cephfs', value: 8 },
    { name: 'GlusterFS', category: 'distributed', link: '/03-distributed/glusterfs', value: 7 },
    { name: 'JuiceFS', category: 'distributed', link: '/03-distributed/juicefs', value: 8 },
    { name: 'MooseFS', category: 'distributed', link: '/03-distributed/moosefs', value: 5 },
    { name: 'Lustre', category: 'distributed', link: '/03-distributed/lustre', value: 6 },
    { name: '对比选型', category: 'distributed', link: '/03-distributed/compare', value: 7 },
    // 04 object
    { name: 'S3 协议', category: 'object', link: '/04-object/s3-protocol', value: 9 },
    { name: 'MinIO', category: 'object', link: '/04-object/minio', value: 8 },
    { name: '阿里云 OSS', category: 'object', link: '/04-object/oss', value: 7 },
    { name: '腾讯云 COS', category: 'object', link: '/04-object/cos', value: 7 },
    { name: '纠删码 EC', category: 'object', link: '/04-object/erasure-coding', value: 8 },
    { name: '生命周期', category: 'object', link: '/04-object/lifecycle', value: 6 },
    { name: '一致性', category: 'object', link: '/04-object/consistency', value: 7 },
    // 05 network
    { name: 'NFS', category: 'network', link: '/05-network/nfs', value: 8 },
    { name: 'SMB/CIFS', category: 'network', link: '/05-network/smb', value: 7 },
    { name: 'WebDAV', category: 'network', link: '/05-network/webdav', value: 6 },
    { name: 'FTP/SFTP', category: 'network', link: '/05-network/ftp-sftp', value: 6 },
    { name: 'rsync', category: 'network', link: '/05-network/rsync', value: 7 },
    // 06 cloud-native
    { name: 'CSI', category: 'cloudNative', link: '/06-cloud-native/csi', value: 9 },
    { name: 'PV/PVC', category: 'cloudNative', link: '/06-cloud-native/pv-pvc', value: 8 },
    { name: '动态配置', category: 'cloudNative', link: '/06-cloud-native/dynamic', value: 7 },
    { name: 'Rook Ceph', category: 'cloudNative', link: '/06-cloud-native/rook', value: 7 },
    { name: 'Longhorn', category: 'cloudNative', link: '/06-cloud-native/longhorn', value: 6 },
    { name: 'OpenEBS', category: 'cloudNative', link: '/06-cloud-native/openebs', value: 6 },
    { name: '快照 Clone', category: 'cloudNative', link: '/06-cloud-native/snapshot', value: 7 },
    // 07 container
    { name: 'OverlayFS', category: 'container', link: '/07-container/overlayfs', value: 9 },
    { name: 'Docker layers', category: 'container', link: '/07-container/docker-layers', value: 8 },
    { name: 'containerd', category: 'container', link: '/07-container/containerd', value: 6 },
    { name: 'BuildKit', category: 'container', link: '/07-container/buildkit', value: 6 },
    { name: '存储驱动', category: 'container', link: '/07-container/storage-drivers', value: 7 },
    // 08 tools
    { name: 'FUSE', category: 'tools', link: '/08-tools/fuse', value: 7 },
    { name: 'debugfs', category: 'tools', link: '/08-tools/debugfs', value: 5 },
    { name: 'rsync 工具', category: 'tools', link: '/08-tools/rsync', value: 6 },
    { name: 'find/fd', category: 'tools', link: '/08-tools/find-fd', value: 6 },
    { name: 'inotify', category: 'tools', link: '/08-tools/inotify', value: 6 },
    { name: 'du/df', category: 'tools', link: '/08-tools/du-df', value: 5 },
    { name: 'lsof', category: 'tools', link: '/08-tools/lsof', value: 5 },
    // 09 perf
    { name: 'IO 调度', category: 'perf', link: '/09-perf/io-scheduler', value: 8 },
    { name: 'Page Cache 调优', category: 'perf', link: '/09-perf/page-cache-tune', value: 8 },
    { name: 'fsync', category: 'perf', link: '/09-perf/fsync', value: 7 },
    { name: 'readahead', category: 'perf', link: '/09-perf/readahead', value: 6 },
    { name: 'Direct I/O', category: 'perf', link: '/09-perf/direct-io', value: 7 },
    { name: '调优方法论', category: 'perf', link: '/09-perf/methodology', value: 7 },
    // 10 security
    { name: 'POSIX 权限', category: 'security', link: '/10-security/posix-perm', value: 8 },
    { name: 'ACL', category: 'security', link: '/10-security/acl', value: 7 },
    { name: 'xattr', category: 'security', link: '/10-security/xattr', value: 6 },
    { name: '加密', category: 'security', link: '/10-security/encryption', value: 7 },
    { name: 'auditd', category: 'security', link: '/10-security/auditd', value: 5 },
    // 11 backup
    { name: '快照', category: 'backup', link: '/11-backup/snapshot', value: 8 },
    { name: 'Borg', category: 'backup', link: '/11-backup/borg', value: 6 },
    { name: 'restic', category: 'backup', link: '/11-backup/restic', value: 6 },
    { name: '3-2-1 原则', category: 'backup', link: '/11-backup/3-2-1', value: 6 },
    { name: 'RPO/RTO', category: 'backup', link: '/11-backup/dr', value: 7 },
    // 12 cases
    { name: 'Netflix S3', category: 'cases', link: '/12-cases/netflix-s3', value: 8 },
    { name: 'ByteDance JuiceFS', category: 'cases', link: '/12-cases/juicefs-bytedance', value: 8 },
    { name: 'CERN EOS', category: 'cases', link: '/12-cases/cern-eos', value: 6 },
    { name: 'Snowflake', category: 'cases', link: '/12-cases/snowflake', value: 7 },
    { name: 'Meta HDFS', category: 'cases', link: '/12-cases/meta-hdfs', value: 7 },
    // 13 interview
    { name: '高频题', category: 'interview', link: '/13-interview/questions', value: 8 },
    { name: '系统设计', category: 'interview', link: '/13-interview/system-design', value: 8 },
    { name: '对比表', category: 'interview', link: '/13-interview/comparison', value: 7 }
  ],
  links: [
    // 基础 → 本地盘
    { source: 'inode/dentry', target: 'ext4' },
    { source: 'VFS 抽象层', target: 'ext4' },
    { source: 'Page Cache', target: 'ext4' },
    { source: 'ext4', target: 'XFS' },
    { source: 'ext4', target: 'Btrfs' },
    { source: 'ext4', target: 'ZFS' },
    { source: 'Btrfs', target: 'ZFS' },
    { source: 'ext4', target: 'NTFS/FAT' },
    { source: 'ext4', target: 'APFS/HFS+' },
    { source: 'ext4', target: '横向对比' },
    { source: '日志 journal', target: 'ext4' },
    { source: '日志 journal', target: 'XFS' },
    { source: '日志 journal', target: 'NTFS/FAT' },
    { source: '挂载 mount', target: 'ext4' },
    { source: '挂载 mount', target: 'NFS' },
    { source: '挂载 mount', target: 'SMB/CIFS' },
    // 本地盘 → 分布式
    { source: 'ext4', target: 'HDFS' },
    { source: 'ext4', target: 'CephFS' },
    { source: 'ext4', target: 'GlusterFS' },
    { source: '横向对比', target: 'HDFS' },
    { source: 'HDFS', target: 'CephFS' },
    { source: 'CephFS', target: 'GlusterFS' },
    { source: 'GlusterFS', target: 'JuiceFS' },
    { source: 'HDFS', target: 'MooseFS' },
    { source: 'HDFS', target: 'Lustre' },
    { source: 'CephFS', target: '对比选型' },
    { source: 'JuiceFS', target: '对比选型' },
    // 分布式 → 对象
    { source: 'HDFS', target: 'S3 协议' },
    { source: 'CephFS', target: 'S3 协议' },
    { source: 'CephFS', target: 'MinIO' },
    { source: 'S3 协议', target: 'MinIO' },
    { source: 'S3 协议', target: '阿里云 OSS' },
    { source: 'S3 协议', target: '腾讯云 COS' },
    { source: 'MinIO', target: '纠删码 EC' },
    { source: 'MinIO', target: '生命周期' },
    { source: '阿里云 OSS', target: '纠删码 EC' },
    { source: '纠删码 EC', target: '一致性' },
    // 网络协议
    { source: 'VFS 抽象层', target: 'NFS' },
    { source: 'VFS 抽象层', target: 'SMB/CIFS' },
    { source: 'NFS', target: 'SMB/CIFS' },
    { source: 'SMB/CIFS', target: 'WebDAV' },
    { source: 'WebDAV', target: 'FTP/SFTP' },
    { source: 'FTP/SFTP', target: 'rsync' },
    { source: 'rsync', target: 'rsync 工具' },
    // 云原生
    { source: 'CSI', target: 'PV/PVC' },
    { source: 'PV/PVC', target: '动态配置' },
    { source: 'CSI', target: 'Rook Ceph' },
    { source: 'CSI', target: 'Longhorn' },
    { source: 'CSI', target: 'OpenEBS' },
    { source: 'Rook Ceph', target: 'Longhorn' },
    { source: 'CephFS', target: 'Rook Ceph' },
    { source: 'PV/PVC', target: '快照 Clone' },
    { source: '快照 Clone', target: '快照' },
    // 容器
    { source: 'OverlayFS', target: 'Docker layers' },
    { source: 'Docker layers', target: 'containerd' },
    { source: 'Docker layers', target: 'BuildKit' },
    { source: 'Docker layers', target: '存储驱动' },
    { source: 'OverlayFS', target: '存储驱动' },
    { source: 'containerd', target: 'CSI' },
    // 工具
    { source: 'FUSE', target: 'OverlayFS' },
    { source: 'debugfs', target: 'ext4' },
    { source: 'find/fd', target: 'inotify' },
    { source: 'du/df', target: 'lsof' },
    { source: 'rsync 工具', target: 'restic' },
    // 性能
    { source: 'Page Cache', target: 'Page Cache 调优' },
    { source: 'IO 调度', target: 'Page Cache 调优' },
    { source: 'fsync', target: 'Page Cache 调优' },
    { source: 'readahead', target: 'Page Cache 调优' },
    { source: 'Direct I/O', target: 'fsync' },
    { source: 'Page Cache 调优', target: '调优方法论' },
    { source: 'IO 调度', target: '调优方法论' },
    // 安全
    { source: 'POSIX 权限', target: 'ACL' },
    { source: 'ACL', target: 'xattr' },
    { source: 'xattr', target: '加密' },
    { source: '加密', target: 'auditd' },
    // 备份
    { source: 'ZFS', target: '快照' },
    { source: 'Btrfs', target: '快照' },
    { source: 'LVM', target: '快照' },  // placeholder — will be filtered
    { source: '快照', target: 'Borg' },
    { source: 'Borg', target: 'restic' },
    { source: 'restic', target: '3-2-1 原则' },
    { source: '3-2-1 原则', target: 'RPO/RTO' },
    { source: 'rsync 工具', target: 'RPO/RTO' },
    // 案例
    { source: 'Netflix S3', target: 'S3 协议' },
    { source: 'ByteDance JuiceFS', target: 'JuiceFS' },
    { source: 'CERN EOS', target: 'CephFS' },
    { source: 'Snowflake', target: 'S3 协议' },
    { source: 'Meta HDFS', target: 'HDFS' },
    // 面试
    { source: '高频题', target: '系统设计' },
    { source: '对比表', target: '横向对比' },
    { source: '对比表', target: '对比选型' }
  ]
}

const option = {
  tooltip: {
    formatter: (p) => p.dataType === 'node'
      ? `<b>${p.name}</b><br/>点击访问 → ${p.data.link || ''}`
      : `${p.data.source} → ${p.data.target}`
  },
  legend: { show: false },
  animationDurationUpdate: 800,
  animationEasingUpdate: 'cubicInOut',
  series: [{
    type: 'graph',
    layout: 'force',
    roam: true,
    draggable: true,
    symbolSize: 42,
    edgeSymbol: ['none', 'arrow'],
    edgeSymbolSize: 6,
    force: { repulsion: 220, edgeLength: 90, gravity: 0.05 },
    categories: Object.keys(categoryColors).map(k => ({ name: k, itemStyle: { color: categoryColors[k] } })),
    label: { show: true, position: 'right', fontSize: 11, color: '#334155' },
    data: graphData.nodes,
    links: graphData.links,
    lineStyle: { color: '#cbd5e1', width: 1, opacity: 0.7, curveness: 0.1 },
    emphasis: { focus: 'adjacency', lineStyle: { width: 3 } }
  }]
}

onMounted(() => {
  chart = echarts.init(chartRef.value, null, { renderer: 'canvas' })
  chart.setOption(option)
  chart.on('click', (params) => {
    if (params.dataType === 'node' && params.data.link) {
      window.location.href = params.data.link
    }
  })
  window.addEventListener('resize', resize)
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  chart?.dispose()
})
const resize = () => chart?.resize()
const resetLayout = () => {
  chart.setOption(option, true)
}
</script>