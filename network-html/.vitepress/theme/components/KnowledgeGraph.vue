<template>
  <div class="kg-container">
    <div ref="chartRef" :style="{ width: '100%', height: height + 'px' }"></div>
    <div class="kg-toolbar">
      <button class="kg-toolbar__btn" @click="resetLayout">🔄 重置布局</button>
      <span class="kg-toolbar__legend">
        <span><span class="kg-legend-dot" style="background: #2563eb"></span>基础</span>
        <span><span class="kg-legend-dot" style="background: #0891b2"></span>物理层</span>
        <span><span class="kg-legend-dot" style="background: #d97706"></span>链路层</span>
        <span><span class="kg-legend-dot" style="background: #7c3aed"></span>网络层</span>
        <span><span class="kg-legend-dot" style="background: #dc2626"></span>传输层</span>
        <span><span class="kg-legend-dot" style="background: #16a34a"></span>应用层</span>
        <span><span class="kg-legend-dot" style="background: #be185d"></span>安全</span>
        <span><span class="kg-legend-dot" style="background: #a21caf"></span>无线</span>
        <span><span class="kg-legend-dot" style="background: #0e7490"></span>云网络</span>
        <span><span class="kg-legend-dot" style="background: #047857"></span>工具</span>
        <span><span class="kg-legend-dot" style="background: #5b21b6"></span>案例</span>
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
  basics: '#2563eb', physical: '#0891b2', datalink: '#d97706',
  network: '#7c3aed', transport: '#dc2626', app: '#16a34a',
  security: '#be185d', wireless: '#a21caf', cloud: '#0e7490',
  tools: '#047857', cases: '#5b21b6'
}

const graphData = {
  nodes: [
    { name: 'OSI 七层模型', category: 'basics', link: '/01-basics/osi', value: 8 },
    { name: 'TCP/IP 四层', category: 'basics', link: '/01-basics/tcp-ip', value: 8 },
    { name: '封装/解封装', category: 'basics', link: '/01-basics/encapsulation', value: 6 },
    { name: '性能指标', category: 'basics', link: '/01-basics/metrics', value: 5 },
    { name: '信号编码', category: 'physical', link: '/02-physical/signal', value: 5 },
    { name: '传输介质', category: 'physical', link: '/02-physical/media', value: 5 },
    { name: '复用技术', category: 'physical', link: '/02-physical/multiplexing', value: 5 },
    { name: 'MAC 地址', category: 'datalink', link: '/03-data-link/mac', value: 6 },
    { name: '以太网 交换机', category: 'datalink', link: '/03-data-link/ethernet', value: 6 },
    { name: 'VLAN', category: 'datalink', link: '/03-data-link/vlan', value: 6 },
    { name: 'STP/RSTP', category: 'datalink', link: '/03-data-link/stp', value: 5 },
    { name: 'IP 地址', category: 'network', link: '/04-network/ip-address', value: 8 },
    { name: '子网划分', category: 'network', link: '/04-network/subnet', value: 7 },
    { name: 'IPv6', category: 'network', link: '/04-network/ipv6', value: 6 },
    { name: 'ARP', category: 'network', link: '/04-network/arp', value: 6 },
    { name: 'ICMP/ping', category: 'network', link: '/04-network/icmp', value: 6 },
    { name: '路由原理', category: 'network', link: '/04-network/routing', value: 7 },
    { name: 'OSPF/BGP', category: 'network', link: '/04-network/bgp-ospf', value: 7 },
    { name: 'NAT', category: 'network', link: '/04-network/nat', value: 6 },
    { name: 'UDP', category: 'transport', link: '/05-transport/udp', value: 7 },
    { name: 'TCP 三次握手', category: 'transport', link: '/05-transport/tcp-handshake', value: 9 },
    { name: 'TCP 四次挥手', category: 'transport', link: '/05-transport/tcp-wave', value: 8 },
    { name: 'TCP 可靠传输', category: 'transport', link: '/05-transport/tcp-reliable', value: 8 },
    { name: 'TCP 流量控制', category: 'transport', link: '/05-transport/tcp-flow', value: 7 },
    { name: 'TCP 拥塞控制', category: 'transport', link: '/05-transport/tcp-congestion', value: 8 },
    { name: 'Socket 编程', category: 'transport', link: '/05-transport/socket', value: 7 },
    { name: 'HTTP 协议', category: 'app', link: '/06-application/http', value: 9 },
    { name: 'HTTPS/TLS', category: 'app', link: '/06-application/https', value: 9 },
    { name: 'HTTP/2 HTTP/3', category: 'app', link: '/06-application/http2-3', value: 7 },
    { name: 'DNS 解析', category: 'app', link: '/06-application/dns', value: 8 },
    { name: 'CDN 加速', category: 'app', link: '/06-application/cdn', value: 7 },
    { name: 'WebSocket', category: 'app', link: '/06-application/websocket', value: 6 },
    { name: 'RESTful API', category: 'app', link: '/06-application/restful', value: 7 },
    { name: 'RPC 协议', category: 'app', link: '/06-application/rpc', value: 7 },
    { name: '加密算法', category: 'security', link: '/07-security/encryption', value: 7 },
    { name: '数字签名', category: 'security', link: '/07-security/digital-signature', value: 7 },
    { name: 'PKI/CA', category: 'security', link: '/07-security/pki', value: 6 },
    { name: 'TLS 握手', category: 'security', link: '/07-security/tls-handshake', value: 8 },
    { name: '常见攻击', category: 'security', link: '/07-security/attacks', value: 7 },
    { name: '防火墙/WAF', category: 'security', link: '/07-security/firewall', value: 7 },
    { name: 'VPN/IPsec', category: 'security', link: '/07-security/vpn', value: 6 },
    { name: 'WiFi 802.11', category: 'wireless', link: '/08-wireless/wifi', value: 6 },
    { name: '5G/4G', category: 'wireless', link: '/08-wireless/5g', value: 6 },
    { name: '物联网协议', category: 'wireless', link: '/08-wireless/iot', value: 6 },
    { name: 'VPC', category: 'cloud', link: '/09-cloud-network/vpc', value: 7 },
    { name: '负载均衡 SLB', category: 'cloud', link: '/09-cloud-network/slb', value: 7 },
    { name: 'SDN', category: 'cloud', link: '/09-cloud-network/sdn', value: 6 },
    { name: 'Service Mesh', category: 'cloud', link: '/09-cloud-network/service-mesh', value: 7 },
    { name: 'Wireshark', category: 'tools', link: '/10-tools/wireshark', value: 7 },
    { name: 'tcpdump', category: 'tools', link: '/10-tools/tcpdump', value: 7 },
    { name: '性能优化', category: 'tools', link: '/10-tools/performance', value: 7 },
    { name: 'CDN 架构', category: 'cases', link: '/11-cases/cdn-arch', value: 6 },
    { name: '微服务网络', category: 'cases', link: '/11-cases/microservice', value: 6 },
    { name: '全链路 HTTPS', category: 'cases', link: '/11-cases/full-https', value: 6 }
  ],
  links: [
    { source: 'OSI 七层模型', target: 'TCP/IP 四层' },
    { source: 'OSI 七层模型', target: '封装/解封装' },
    { source: '封装/解封装', target: '以太网 交换机' },
    { source: 'MAC 地址', target: '以太网 交换机' },
    { source: '以太网 交换机', target: 'VLAN' },
    { source: '以太网 交换机', target: 'STP/RSTP' },
    { source: 'IP 地址', target: '子网划分' },
    { source: 'IP 地址', target: 'IPv6' },
    { source: 'IP 地址', target: 'ARP' },
    { source: 'IP 地址', target: 'NAT' },
    { source: '子网划分', target: '路由原理' },
    { source: '路由原理', target: 'OSPF/BGP' },
    { source: 'ARP', target: 'ICMP/ping' },
    { source: 'UDP', target: 'TCP 三次握手' },
    { source: 'TCP 三次握手', target: 'TCP 四次挥手' },
    { source: 'TCP 三次握手', target: 'TCP 可靠传输' },
    { source: 'TCP 可靠传输', target: 'TCP 流量控制' },
    { source: 'TCP 流量控制', target: 'TCP 拥塞控制' },
    { source: 'TCP 三次握手', target: 'Socket 编程' },
    { source: 'UDP', target: 'Socket 编程' },
    { source: 'HTTP 协议', target: 'HTTPS/TLS' },
    { source: 'HTTPS/TLS', target: 'HTTP/2 HTTP/3' },
    { source: 'HTTP 协议', target: 'RESTful API' },
    { source: 'HTTP 协议', target: 'WebSocket' },
    { source: 'DNS 解析', target: 'CDN 加速' },
    { source: 'HTTP 协议', target: 'RPC 协议' },
    { source: '加密算法', target: '数字签名' },
    { source: '数字签名', target: 'PKI/CA' },
    { source: 'PKI/CA', target: 'TLS 握手' },
    { source: 'TLS 握手', target: 'HTTPS/TLS' },
    { source: '常见攻击', target: '防火墙/WAF' },
    { source: '防火墙/WAF', target: 'VPN/IPsec' },
    { source: 'WiFi 802.11', target: '5G/4G' },
    { source: '5G/4G', target: '物联网协议' },
    { source: 'VPC', target: '负载均衡 SLB' },
    { source: '负载均衡 SLB', target: 'SDN' },
    { source: 'SDN', target: 'Service Mesh' },
    { source: 'Wireshark', target: 'tcpdump' },
    { source: 'tcpdump', target: '性能优化' },
    { source: 'CDN 加速', target: 'CDN 架构' },
    { source: 'Service Mesh', target: '微服务网络' },
    { source: 'TLS 握手', target: '全链路 HTTPS' },
    { source: 'HTTP 协议', target: '性能指标' },
    { source: 'TCP 三次握手', target: '性能指标' }
  ]
}

function renderChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value, undefined, { renderer: 'canvas' })
  const nodes = graphData.nodes.map(n => ({
    ...n,
    itemStyle: { color: categoryColors[n.category] || '#1f2937' },
    symbolSize: n.value ? Math.min(60, 22 + n.value * 3) : 28,
    label: { show: true, position: 'right', fontSize: 11 }
  }))
  const links = graphData.links.map(l => ({ ...l, lineStyle: { color: '#aaa', width: 1, curveness: 0.05 } }))
  chart.setOption({
    tooltip: { formatter: (p) => p.dataType === 'node' ? `<b>${p.name}</b>` : `${p.source} → ${p.target}` },
    series: [{
      type: 'graph', layout: 'force', roam: true, draggable: true, animation: true,
      data: nodes, links: links,
      force: { repulsion: 280, edgeLength: 110, gravity: 0.05 },
      emphasis: { focus: 'adjacency', lineStyle: { width: 3, color: '#0ea5e9' } }
    }]
  })
  chart.on('click', (params) => {
    if (params.dataType === 'node' && params.data.link) window.location.href = params.data.link
  })
}
function resetLayout() { if (chart) chart.dispatchAction({ type: 'restore' }) }
onMounted(() => { renderChart(); window.addEventListener('resize', () => chart?.resize()) })
onBeforeUnmount(() => { chart?.dispose(); chart = null })
</script>