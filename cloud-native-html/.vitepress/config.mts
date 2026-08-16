import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'
import { fileURLToPath, URL } from 'node:url'

// P0: VitePress/rollup 默认 fs.allow 限制 cwd 外 import。用 vite alias 解决相对路径。
const SHARED_ASSETS = fileURLToPath(new URL('../../shared-assets', import.meta.url))

export default withMermaid(defineConfig({
  vite: {
    resolve: {
      alias: [
        { find: '@shared', replacement: SHARED_ASSETS },
      ],
    },
  },
    mermaid: {
    theme: 'default'
  },
  base: '/cloud-native/',
  title: '云原生 / Docker / K8s 知识图谱',
  description: '系统化学习云原生 / Docker / Kubernetes - 14 大类 · 80+ 节点 · 60+ 内容页',
  lang: 'zh-CN',
  lastUpdated: true,
  srcDir: 'docs',
  cleanUrls: true,
  head: [
    ['link', { rel: 'apple-touch-icon', href: '/apple-touch-icon.png', sizes: '180x180' }],
    ['link', { rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' }],
    ['link', { rel: 'icon', href: '/favicon.ico', type: 'image/x-icon' }],
    ['meta', { name: 'theme-color', content: '#06b6d4' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:locale', content: 'zh_CN' }]  ],
  themeConfig: {
    siteTitle: '云原生全栈',
    nav: [

      { text: '🏠 门户', link: 'https://java-px.bot.cd/', target: '_blank' },
{ text: '首页', link: '/' },
      { text: '知识图谱', link: '/graph' },
      { text: '思维导图', link: '/mindmap' },
      { text: '命令速查', link: '/cheatsheet' },
      { text: '学习路径', link: '/path' },
      {
        text: '更多站点',
        items: [
        { text: 'AI 工具 / 大模型', link: 'https://java-px.bot.cd/ai/' },
        { text: '企业级架构', link: 'https://java-px.bot.cd/architecture/' },
        { text: '大数据', link: 'https://java-px.bot.cd/bigdata/' },
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
        { text: '在线工具', link: 'https://java-px.bot.cd/tools/' },
        { text: '视频处理', link: 'https://java-px.bot.cd/video/' }
      ]
      }
    ],
    sidebar: {
      '/': [
        { text: '🎯 开始', items: [{ text: '📖 学习路径', link: '/path' }] },
        {
          text: '🐳 Docker 容器',
          items: [
            { text: 'Docker 基础', link: '/01-docker/intro' },
            { text: '镜像 image', link: '/01-docker/image' },
            { text: '容器 container', link: '/01-docker/container' },
            { text: 'Docker 网络', link: '/01-docker/network' },
            { text: '存储 / 卷', link: '/01-docker/volume' },
            { text: 'Docker Compose', link: '/01-docker/compose' }
          ]
        },
        {
          text: '🏛️ k8s 架构',
          items: [
            { text: 'k8s 是什么', link: '/02-k8s-arch/overview' },
            { text: '控制面 Control Plane', link: '/02-k8s-arch/control-plane' },
            { text: '工作节点 Node', link: '/02-k8s-arch/node' },
            { text: 'kubectl 命令行', link: '/02-k8s-arch/kubectl' },
            { text: 'etcd 存储', link: '/02-k8s-arch/etcd' }
          ]
        },
        {
          text: '📦 工作负载',
          items: [
            { text: 'Pod 最小单元', link: '/03-k8s-workload/pod' },
            { text: 'Deployment', link: '/03-k8s-workload/deployment' },
            { text: 'StatefulSet', link: '/03-k8s-workload/statefulset' },
            { text: 'DaemonSet', link: '/03-k8s-workload/daemonset' },
            { text: 'Job / CronJob', link: '/03-k8s-workload/job' }
          ]
        },
        {
          text: '🌐 Service / 网络',
          items: [
            { text: 'Service 三种类型', link: '/04-k8s-service/service' },
            { text: 'Ingress 入口', link: '/04-k8s-service/ingress' },
            { text: 'NetworkPolicy', link: '/04-k8s-service/network-policy' }
          ]
        },
        {
          text: '💾 存储 / 配置',
          items: [
            { text: 'PV / PVC', link: '/05-k8s-storage/pv-pvc' },
            { text: 'StorageClass / CSI', link: '/05-k8s-storage/storageclass' },
            { text: 'ConfigMap / Secret', link: '/05-k8s-storage/configmap-secret' }
          ]
        },
        {
          text: '⛵ Helm 包管理',
          items: [
            { text: 'Chart 结构', link: '/06-helm/chart' },
            { text: 'template / values', link: '/06-helm/template' },
            { text: 'Chart 仓库', link: '/06-helm/repository' }
          ]
        },
        {
          text: '📈 可观测性',
          items: [
            { text: 'Prometheus', link: '/07-observability/prometheus' },
            { text: 'Grafana 仪表板', link: '/07-observability/grafana' },
            { text: 'Loki 日志聚合', link: '/07-observability/loki' },
            { text: 'Alertmanager', link: '/07-observability/alertmanager' }
          ]
        },
        {
          text: '🕸️ Service Mesh',
          items: [
            { text: 'Istio 核心', link: '/08-service-mesh/istio' },
            { text: 'Sidecar 模式', link: '/08-service-mesh/sidecar' },
            { text: '流量管理', link: '/08-service-mesh/traffic' }
          ]
        },
        {
          text: '🚀 CI/CD & GitOps',
          items: [
            { text: 'GitOps 思想', link: '/09-cicd/gitops' },
            { text: 'ArgoCD', link: '/09-cicd/argocd' },
            { text: 'Tekton / JenkinsX', link: '/09-cicd/tekton' }
          ]
        },
        {
          text: '🏗️ IaC 基础设施',
          items: [
            { text: 'Terraform', link: '/10-iac/terraform' },
            { text: 'Pulumi', link: '/10-iac/pulumi' },
            { text: 'Helmfile / Kustomize', link: '/10-iac/helmfile' }
          ]
        },
        {
          text: '🔒 安全',
          items: [
            { text: 'RBAC 权限', link: '/11-security/rbac' },
            { text: 'Secret 管理', link: '/11-security/secret' },
            { text: 'NetworkPolicy + PodSecurity', link: '/11-security/policy' },
            { text: 'Falco 运行时检测', link: '/11-security/falco' }
          ]
        },
        {
          text: '☁️ Serverless',
          items: [
            { text: 'Knative Serving', link: '/12-serverless/knative' },
            { text: 'AWS Lambda / Cloud Run', link: '/12-serverless/managed' }
          ]
        },
        {
          text: '🔧 排错',
          items: [
            { text: 'kubectl debug', link: '/13-troubleshooting/debug' },
            { text: 'Pod 卡死 / 排错套路', link: '/13-troubleshooting/pod-trouble' },
            { text: '网络 / DNS 排错', link: '/13-troubleshooting/network' }
          ]
        },
        {
          text: '🎯 CKA / CKS / 面试',
          items: [
            { text: 'CKA 考试要点', link: '/14-interview/cka' },
            { text: 'CKS 安全加固', link: '/14-interview/cks' },
            { text: '高频面试题', link: '/14-interview/questions' }
          ]
        }
      ],
      '/graph': [{ text: '🌐 知识图谱', items: [{ text: '全局知识图谱', link: '/graph' }] }],
      '/mindmap': [{ text: '🧭 思维导图', items: [{ text: '云原生思维导图', link: '/mindmap' }] }],
      '/cheatsheet': [{ text: '📋 命令速查', items: [{ text: 'Docker / k8s 命令速查', link: '/cheatsheet' }] }],
      '/path': [{ text: '🎯 学习路径', items: [{ text: '云原生学习路径', link: '/path' }] }]
    },
    socialLinks: [{ icon: 'github', link: 'https://github.com' }],
    footer: {
      message: '云原生全栈 - Docker / Kubernetes / Service Mesh / GitOps · 🏠 <a href="https://java-px.bot.cd/" target="_blank">门户首页</a>',
      copyright: 'MIT License'
    },
    outline: { level: [2, 3], label: '页面大纲' },
    docFooter: { prev: '上一篇', next: '下一篇' },

    search: { provider: 'local' },
  }
}))
