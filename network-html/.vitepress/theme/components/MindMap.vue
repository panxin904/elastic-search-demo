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
const props = defineProps({ height: { type: Number, default: 940 } })
const chartRef = ref(null)
let chart = null

const mindMapData = {
  name: '计算机网络全栈', symbolSize: 32, itemStyle: { color: '#1f2937' },
  children: [
    { name: '🌐 网络基础', itemStyle: { color: '#2563eb' }, children: [
      { name: 'OSI 七层模型', link: '/01-basics/osi' },
      { name: 'TCP/IP 四层', link: '/01-basics/tcp-ip' },
      { name: '封装/解封装', link: '/01-basics/encapsulation' },
      { name: '性能指标', link: '/01-basics/metrics' }
    ]},
    { name: '🔌 物理层', itemStyle: { color: '#0891b2' }, children: [
      { name: '信号编码', link: '/02-physical/signal' },
      { name: '传输介质', link: '/02-physical/media' },
      { name: '复用技术', link: '/02-physical/multiplexing' }
    ]},
    { name: '🔗 数据链路层', itemStyle: { color: '#d97706' }, children: [
      { name: 'MAC 地址', link: '/03-data-link/mac' },
      { name: '以太网/交换机', link: '/03-data-link/ethernet' },
      { name: 'VLAN', link: '/03-data-link/vlan' },
      { name: 'STP/RSTP', link: '/03-data-link/stp' }
    ]},
    { name: '🌍 网络层', itemStyle: { color: '#7c3aed' }, children: [
      { name: 'IP 地址', link: '/04-network/ip-address' },
      { name: '子网划分', link: '/04-network/subnet' },
      { name: 'IPv6', link: '/04-network/ipv6' },
      { name: 'ARP', link: '/04-network/arp' },
      { name: 'ICMP/ping', link: '/04-network/icmp' },
      { name: '路由原理', link: '/04-network/routing' },
      { name: 'OSPF/BGP', link: '/04-network/bgp-ospf' },
      { name: 'NAT', link: '/04-network/nat' }
    ]},
    { name: '🚚 传输层', itemStyle: { color: '#dc2626' }, children: [
      { name: 'UDP', link: '/05-transport/udp' },
      { name: 'TCP 三次握手', link: '/05-transport/tcp-handshake' },
      { name: 'TCP 四次挥手', link: '/05-transport/tcp-wave' },
      { name: 'TCP 可靠传输', link: '/05-transport/tcp-reliable' },
      { name: 'TCP 流量控制', link: '/05-transport/tcp-flow' },
      { name: 'TCP 拥塞控制', link: '/05-transport/tcp-congestion' },
      { name: 'Socket 编程', link: '/05-transport/socket' }
    ]},
    { name: '📱 应用层', itemStyle: { color: '#16a34a' }, children: [
      { name: 'HTTP 协议', link: '/06-application/http' },
      { name: 'HTTPS/TLS', link: '/06-application/https' },
      { name: 'HTTP/2 HTTP/3', link: '/06-application/http2-3' },
      { name: 'DNS 解析', link: '/06-application/dns' },
      { name: 'CDN 加速', link: '/06-application/cdn' },
      { name: 'WebSocket', link: '/06-application/websocket' },
      { name: 'RESTful API', link: '/06-application/restful' },
      { name: 'RPC 协议', link: '/06-application/rpc' }
    ]},
    { name: '🔒 网络安全', itemStyle: { color: '#be185d' }, children: [
      { name: '加密算法', link: '/07-security/encryption' },
      { name: '数字签名', link: '/07-security/digital-signature' },
      { name: 'PKI/CA', link: '/07-security/pki' },
      { name: 'TLS 握手', link: '/07-security/tls-handshake' },
      { name: '常见攻击', link: '/07-security/attacks' },
      { name: '防火墙/WAF', link: '/07-security/firewall' },
      { name: 'VPN/IPsec', link: '/07-security/vpn' }
    ]},
    { name: '📡 无线网络', itemStyle: { color: '#a21caf' }, children: [
      { name: 'WiFi 802.11', link: '/08-wireless/wifi' },
      { name: '5G/4G', link: '/08-wireless/5g' },
      { name: '蓝牙/NFC', link: '/08-wireless/bluetooth' },
      { name: '物联网协议', link: '/08-wireless/iot' }
    ]},
    { name: '☁️ 云网络', itemStyle: { color: '#0e7490' }, children: [
      { name: 'VPC', link: '/09-cloud-network/vpc' },
      { name: '负载均衡 SLB', link: '/09-cloud-network/slb' },
      { name: 'SDN', link: '/09-cloud-network/sdn' },
      { name: 'Service Mesh', link: '/09-cloud-network/service-mesh' }
    ]},
    { name: '🛠️ 抓包排查', itemStyle: { color: '#047857' }, children: [
      { name: 'Wireshark', link: '/10-tools/wireshark' },
      { name: 'tcpdump', link: '/10-tools/tcpdump' },
      { name: 'curl 调试', link: '/10-tools/curl' },
      { name: '性能优化', link: '/10-tools/performance' },
      { name: '故障排查', link: '/10-tools/troubleshooting' }
    ]},
    { name: '🏢 企业案例', itemStyle: { color: '#5b21b6' }, children: [
      { name: 'CDN 加速架构', link: '/11-cases/cdn-arch' },
      { name: '微服务网络治理', link: '/11-cases/microservice' },
      { name: '全链路 HTTPS', link: '/11-cases/full-https' },
      { name: '跨地域网络', link: '/11-cases/cross-region' }
    ]}
  ]
}

function renderChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value, undefined, { renderer: 'canvas' })
  chart.setOption({
    tooltip: { trigger: 'item', formatter: (p) => p.data.link ? `<b>${p.name}</b>` : p.name },
    series: [{
      type: 'tree',
      data: [mindMapData],
      top: '5%', left: '12%', bottom: '5%', right: '15%',
      symbolSize: 8,
      label: { position: 'left', verticalAlign: 'middle', align: 'right', fontSize: 12 },
      leaves: { label: { position: 'right', align: 'left' } },
      expandAndCollapse: true,
      initialTreeDepth: 2,
      animationDuration: 400,
      animationDurationUpdate: 400
    }]
  })
  chart.on('click', (params) => {
    if (params.data && params.data.link) window.location.href = params.data.link
  })
}
function expandAll() { if (chart) chart.dispatchAction({ type: 'treeExpandAll' }) }
function collapseAll() { if (chart) chart.dispatchAction({ type: 'treeCollapseAll' }) }
function resetView() { if (chart) chart.dispatchAction({ type: 'treeRestore' }) }
onMounted(() => { renderChart(); window.addEventListener('resize', () => chart?.resize()) })
onBeforeUnmount(() => { chart?.dispose(); chart = null })
</script>