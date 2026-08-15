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
  height: { type: Number, default: 940 }
})

const chartRef = ref(null)
let chart = null

const mindMapData = {
  name: '云原生 / Docker / K8s',
  symbolSize: 30,
  itemStyle: { color: '#1f2937' },
  children: [
    {
      name: '🐳 Docker 容器',
      itemStyle: { color: '#0ea5e9' },
      children: [
        { name: 'Docker 是什么', link: '/01-docker/intro' },
        { name: '镜像 image', link: '/01-docker/image' },
        { name: '容器 container', link: '/01-docker/container' },
        { name: 'Docker 网络', link: '/01-docker/network' },
        { name: 'Docker 存储 / 卷', link: '/01-docker/volume' },
        { name: 'Docker Compose', link: '/01-docker/compose' }
      ]
    },
    {
      name: '🏛️ k8s 架构',
      itemStyle: { color: '#326ce5' },
      children: [
        { name: 'k8s 是什么', link: '/02-k8s-arch/overview' },
        { name: '控制面 Control Plane', link: '/02-k8s-arch/control-plane' },
        { name: '工作节点 Node', link: '/02-k8s-arch/node' },
        { name: 'kubectl 命令行', link: '/02-k8s-arch/kubectl' },
        { name: 'etcd 存储', link: '/02-k8s-arch/etcd' }
      ]
    },
    {
      name: '📦 工作负载',
      itemStyle: { color: '#9333ea' },
      children: [
        { name: 'Pod 最小单元', link: '/03-k8s-workload/pod' },
        { name: 'Deployment', link: '/03-k8s-workload/deployment' },
        { name: 'StatefulSet', link: '/03-k8s-workload/statefulset' },
        { name: 'DaemonSet', link: '/03-k8s-workload/daemonset' },
        { name: 'Job / CronJob', link: '/03-k8s-workload/job' }
      ]
    },
    {
      name: '🌐 Service / 网络',
      itemStyle: { color: '#ea580c' },
      children: [
        { name: 'Service 三种类型', link: '/04-k8s-service/service' },
        { name: 'Ingress 入口', link: '/04-k8s-service/ingress' },
        { name: 'NetworkPolicy', link: '/04-k8s-service/network-policy' }
      ]
    },
    {
      name: '💾 存储 / 配置',
      itemStyle: { color: '#16a34a' },
      children: [
        { name: 'PV / PVC', link: '/05-k8s-storage/pv-pvc' },
        { name: 'StorageClass / CSI', link: '/05-k8s-storage/storageclass' },
        { name: 'ConfigMap / Secret', link: '/05-k8s-storage/configmap-secret' }
      ]
    },
    {
      name: '⛵ Helm 包管理',
      itemStyle: { color: '#0f766e' },
      children: [
        { name: 'Chart 结构', link: '/06-helm/chart' },
        { name: 'template / values', link: '/06-helm/template' },
        { name: 'Chart 仓库', link: '/06-helm/repository' }
      ]
    },
    {
      name: '📈 可观测性',
      itemStyle: { color: '#f59e0b' },
      children: [
        { name: 'Prometheus', link: '/07-observability/prometheus' },
        { name: 'Grafana 仪表板', link: '/07-observability/grafana' },
        { name: 'Loki 日志聚合', link: '/07-observability/loki' },
        { name: 'Alertmanager', link: '/07-observability/alertmanager' }
      ]
    },
    {
      name: '🕸️ Service Mesh',
      itemStyle: { color: '#7c3aed' },
      children: [
        { name: 'Istio 核心', link: '/08-service-mesh/istio' },
        { name: 'Sidecar 模式', link: '/08-service-mesh/sidecar' },
        { name: '流量管理', link: '/08-service-mesh/traffic' }
      ]
    },
    {
      name: '🚀 CI/CD & GitOps',
      itemStyle: { color: '#0891b2' },
      children: [
        { name: 'GitOps 思想', link: '/09-cicd/gitops' },
        { name: 'ArgoCD', link: '/09-cicd/argocd' },
        { name: 'Tekton / JenkinsX', link: '/09-cicd/tekton' }
      ]
    },
    {
      name: '🏗️ IaC 基础设施即代码',
      itemStyle: { color: '#84cc16' },
      children: [
        { name: 'Terraform', link: '/10-iac/terraform' },
        { name: 'Pulumi', link: '/10-iac/pulumi' },
        { name: 'Helmfile / Kustomize', link: '/10-iac/helmfile' }
      ]
    },
    {
      name: '🔒 安全',
      itemStyle: { color: '#ef4444' },
      children: [
        { name: 'RBAC 权限', link: '/11-security/rbac' },
        { name: 'Secret 管理', link: '/11-security/secret' },
        { name: 'NetworkPolicy + PodSecurity', link: '/11-security/policy' },
        { name: 'Falco 运行时检测', link: '/11-security/falco' }
      ]
    },
    {
      name: '☁️ Serverless',
      itemStyle: { color: '#6366f1' },
      children: [
        { name: 'Knative Serving', link: '/12-serverless/knative' },
        { name: 'AWS Lambda / GCP Cloud Run', link: '/12-serverless/managed' }
      ]
    },
    {
      name: '🔧 排错',
      itemStyle: { color: '#f97316' },
      children: [
        { name: 'kubectl debug', link: '/13-troubleshooting/debug' },
        { name: 'Pod 卡死 / 排错套路', link: '/13-troubleshooting/pod-trouble' },
        { name: '网络 / DNS 排错', link: '/13-troubleshooting/network' }
      ]
    },
    {
      name: '🎯 CKA / CKS / 面试',
      itemStyle: { color: '#14b8a6' },
      children: [
        { name: 'CKA 考试要点', link: '/14-interview/cka' },
        { name: 'CKS 安全加固', link: '/14-interview/cks' },
        { name: '高频面试题', link: '/14-interview/questions' }
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
      leaves: { label: { position: 'right', verticalAlign: 'middle', align: 'left' } },
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