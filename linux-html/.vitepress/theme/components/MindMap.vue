<template>
  <div class="mindmap-container">
    <div ref="chartRef" :style="{ width: '100%', height: height + 'px' }"></div>
    <div class="mm-toolbar">
      <button class="mm-toolbar__btn" @click="expandAll">📖 全部展开</button>
      <button class="mm-toolbar__btn" @click="collapseAll">📕 全部收起</button>
      <button class="mm-toolbar__btn" @click="resetView">🎯 重置视图</button>
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

const props = defineProps({
  height: { type: Number, default: 920 }
})

const chartRef = ref(null)
let chart = null

const mindMapData = {
  name: 'Linux 服务器',
  symbolSize: 30,
  itemStyle: { color: '#1f2937' },
  children: [
    {
      name: '🌐 入门基础',
      itemStyle: { color: '#d97706' },
      children: [
        { name: 'Linux 是什么', link: '/01-foundation/intro' },
        { name: '发行版选择', link: '/01-foundation/distros' },
        { name: 'Shell 与终端', link: '/01-foundation/shell' },
        { name: '文件系统树', link: '/01-foundation/fs-tree' }
      ]
    },
    {
      name: '📁 文件与目录',
      itemStyle: { color: '#2563eb' },
      children: [
        { name: 'ls / cp / mv', link: '/02-filesystem/ls' },
        { name: 'find 查找', link: '/02-filesystem/find' },
        { name: '软链与硬链', link: '/02-filesystem/ln' },
        { name: '权限 (rwx)', link: '/02-filesystem/permissions' },
        { name: '压缩与归档', link: '/02-filesystem/archive' }
      ]
    },
    {
      name: '📦 文本处理三剑客',
      itemStyle: { color: '#06b6d4' },
      children: [
        { name: 'grep', link: '/03-text/grep' },
        { name: 'awk', link: '/03-text/awk' },
        { name: 'sed', link: '/03-text/sed' },
        { name: 'sort / uniq', link: '/03-text/sort-uniq' },
        { name: 'xargs / find 配合', link: '/03-text/xargs' }
      ]
    },
    {
      name: '⚙️ 进程与任务',
      itemStyle: { color: '#8b5cf6' },
      children: [
        { name: 'ps / top / htop', link: '/04-process/ps-top' },
        { name: '信号 (kill)', link: '/04-process/signals' },
        { name: 'systemd', link: '/04-process/systemd' },
        { name: 'cron 定时任务', link: '/04-process/cron' },
        { name: '前台后台 (jobs)', link: '/04-process/jobs' }
      ]
    },
    {
      name: '🛠️ 用户与权限',
      itemStyle: { color: '#ea580c' },
      children: [
        { name: '用户 / 用户组', link: '/05-user/users-groups' },
        { name: 'chmod 权限', link: '/05-user/chmod' },
        { name: 'chown / chgrp', link: '/05-user/chown' },
        { name: 'sudo 提权', link: '/05-user/sudo' },
        { name: 'ACL 细粒度权限', link: '/05-user/acl' }
      ]
    },
    {
      name: '📦 软件与包管理',
      itemStyle: { color: '#ec4899' },
      children: [
        { name: 'apt (Debian/Ubuntu)', link: '/06-package/apt' },
        { name: 'yum / dnf (RHEL)', link: '/06-package/yum-dnf' },
        { name: '源码编译', link: '/06-package/source' },
        { name: '容器化安装', link: '/06-package/container' }
      ]
    },
    {
      name: '🌐 网络',
      itemStyle: { color: '#0891b2' },
      children: [
        { name: 'ip / ifconfig', link: '/07-network/ip' },
        { name: 'ping / traceroute', link: '/07-network/ping' },
        { name: 'curl / wget', link: '/07-network/curl' },
        { name: 'DNS 解析', link: '/07-network/dns' },
        { name: 'ss / netstat', link: '/07-network/ss' }
      ]
    },
    {
      name: '🔥 防火墙 / SSH',
      itemStyle: { color: '#4f46e5' },
      children: [
        { name: 'iptables', link: '/08-firewall-ssh/iptables' },
        { name: 'ufw / firewalld', link: '/08-firewall-ssh/ufw-firewalld' },
        { name: 'OpenSSH 配置', link: '/08-firewall-ssh/openssh' },
        { name: 'ssh-keygen / ssh-copy-id', link: '/08-firewall-ssh/ssh-keys' },
        { name: 'SSH 隧道 / 代理', link: '/08-firewall-ssh/ssh-tunnel' }
      ]
    },
    {
      name: '🗄️ 存储',
      itemStyle: { color: '#10b981' },
      children: [
        { name: 'mount / umount', link: '/09-storage/mount' },
        { name: 'fstab 自动挂载', link: '/09-storage/fstab' },
        { name: 'LVM 逻辑卷', link: '/09-storage/lvm' },
        { name: 'ext4 / xfs / btrfs', link: '/09-storage/fs-types' },
        { name: 'swap 交换分区', link: '/09-storage/swap' }
      ]
    },
    {
      name: '⚡ 性能监控',
      itemStyle: { color: '#eab308' },
      children: [
        { name: 'top / htop', link: '/10-perf/top-htop' },
        { name: 'vmstat / mpstat', link: '/10-perf/vmstat' },
        { name: 'iostat / iotop', link: '/10-perf/iostat' },
        { name: 'sar 持续监控', link: '/10-perf/sar' },
        { name: 'perf / strace', link: '/10-perf/perf-strace' }
      ]
    },
    {
      name: '📜 Shell 脚本',
      itemStyle: { color: '#16a34a' },
      children: [
        { name: 'bash 基础语法', link: '/11-shell/bash-syntax' },
        { name: '变量与参数', link: '/11-shell/variables' },
        { name: '数组与字符串', link: '/11-shell/arrays' },
        { name: '函数与脚本组织', link: '/11-shell/functions' },
        { name: '调试与陷阱', link: '/11-shell/debug' }
      ]
    },
    {
      name: '🛠️ systemd 服务',
      itemStyle: { color: '#be123c' },
      children: [
        { name: 'systemctl 命令', link: '/12-systemd/systemctl' },
        { name: 'Unit 文件', link: '/12-systemd/unit' },
        { name: 'journald 日志', link: '/12-systemd/journald' },
        { name: 'systemd Timer', link: '/12-systemd/timer' }
      ]
    },
    {
      name: '🔒 安全加固',
      itemStyle: { color: '#7c3aed' },
      children: [
        { name: 'SELinux', link: '/13-security/selinux' },
        { name: 'AppArmor', link: '/13-security/apparmor' },
        { name: 'sshd_config 加固', link: '/13-security/sshd-config' },
        { name: 'auditd 审计', link: '/13-security/auditd' },
        { name: '合规检查 (lynis)', link: '/13-security/lynis' }
      ]
    },
    {
      name: '🏗️ 内核与启动',
      itemStyle: { color: '#475569' },
      children: [
        { name: 'GRUB 引导', link: '/14-kernel/grub' },
        { name: 'initramfs', link: '/14-kernel/initramfs' },
        { name: '内核模块', link: '/14-kernel/modules' },
        { name: 'sysctl 调参', link: '/14-kernel/sysctl' }
      ]
    }
  ]
}

function renderChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value, undefined, { renderer: 'canvas' })
  chart.setOption({
    tooltip: {
      trigger: 'item',
      triggerOn: 'mousemove',
      formatter: (p) => {
        if (p.data?.link) return `<b>${p.name}</b><br/>点击跳转`
        return p.name
      }
    },
    series: [{
      type: 'tree',
      data: [mindMapData],
      top: '5%',
      left: '8%',
      bottom: '5%',
      right: '20%',
      symbolSize: 14,
      orient: 'LR',
      expandAndCollapse: true,
      initialTreeDepth: 2,
      label: {
        position: 'left',
        verticalAlign: 'middle',
        align: 'right',
        fontSize: 13,
        color: 'var(--vp-c-text-1, #333)'
      },
      leaves: {
        label: { position: 'right', verticalAlign: 'middle', align: 'left' }
      },
      emphasis: { focus: 'descendant' },
      animationDuration: 550,
      animationDurationUpdate: 750,
      lineStyle: { color: '#aaa', width: 1, curveness: 0.05 }
    }]
  })
  chart.on('click', (params) => {
    if (params.data?.link) window.location.href = params.data.link
  })
}

function expandAll() {
  if (!chart) return
  const traverse = (node, depth) => {
    if (depth > 0 && node.children) chart.dispatchAction({ type: 'treeExpandAndCollapse', data: node, seriesIndex: 0 })
    if (node.children) node.children.forEach(c => traverse(c, depth + 1))
  }
  traverse(mindMapData, 0)
}
function collapseAll() {
  if (!chart) return
  const traverse = (node) => {
    if (node.children) {
      node.children.forEach(c => {
        chart.dispatchAction({ type: 'treeExpandAndCollapse', data: c, seriesIndex: 0 })
        traverse(c)
      })
    }
  }
  traverse(mindMapData)
}
function resetView() { if (chart) chart.dispatchAction({ type: 'restore' }) }

onMounted(() => {
  renderChart()
  window.addEventListener('resize', () => chart?.resize())
})
onBeforeUnmount(() => { chart?.dispose(); chart = null })
</script>