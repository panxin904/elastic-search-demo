import { defineConfig } from 'vitepress'

export default defineConfig({
  base: '/observability/',
  title: 'Observability 知识图谱',
  description: '现代可观测性深度图谱 - Metrics · Logs · Traces · Profiling · OpenTelemetry · Prometheus · Grafana · SRE 三件套 · 11 大类 · 47 节点',
  lang: 'zh-CN',
  lastUpdated: true,
  srcDir: 'docs',
  cleanUrls: true,
  ignoreDeadLinks: true,
  head: [
    ['link', { rel: 'icon', href: '/favicon.ico', type: 'image/x-icon' }],
    ['link', { rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' }],
    ['link', { rel: 'apple-touch-icon', href: '/apple-touch-icon.png', sizes: '180x180' }],
    ['meta', { name: 'theme-color', content: '#14b8a6' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:locale', content: 'zh_CN' }],
  ],
  themeConfig: {
    siteTitle: 'Observability',
    nav: [
      { text: '🏠 门户', link: 'https://java-px.bot.cd/', target: '_blank' },
      { text: '首页', link: '/' },
      {
        text: '更多站点',
        items: [
          { text: 'AI 工具 / 大模型', link: 'https://java-px.bot.cd/ai/' },
          { text: '企业级架构', link: 'https://java-px.bot.cd/architecture/' },
          { text: '大数据', link: 'https://java-px.bot.cd/bigdata/' },
          { text: '云原生 / Docker / K8s', link: 'https://java-px.bot.cd/cloud-native/' },
          { text: 'ElasticSearch', link: 'https://java-px.bot.cd/es/' },
          { text: '文件系统与存储', link: 'https://java-px.bot.cd/filesystem/' },
          { text: '前端 & Node', link: 'https://java-px.bot.cd/frontend/' },
          { text: 'Java 语言', link: 'https://java-px.bot.cd/java-language/' },
          { text: 'Java Web 开发', link: 'https://java-px.bot.cd/java/' },
          { text: 'Kafka', link: 'https://java-px.bot.cd/kafka/' },
          { text: 'Linux 服务器', link: 'https://java-px.bot.cd/linux/' },
          { text: 'MySQL', link: 'https://java-px.bot.cd/mysql/' },
          { text: 'PostgreSQL', link: 'https://java-px.bot.cd/postgresql/' },
          { text: 'Python', link: 'https://java-px.bot.cd/python/' },
          { text: 'Redis', link: 'https://java-px.bot.cd/redis/' },
          { text: '微服务 / Spring Cloud', link: 'https://java-px.bot.cd/cloud/' },
          { text: '计算机网络', link: 'https://java-px.bot.cd/network/' },
          { text: '系统设计', link: 'https://java-px.bot.cd/system-design/' },
          { text: '在线工具', link: 'https://java-px.bot.cd/tools/' },
          { text: '视频处理', link: 'https://java-px.bot.cd/video/' }
        ]
      }
    ],
    sidebar: {
      '/': [
        {
          text: '🏛️ 可观测性基础', collapsed: false, items: [
            { text: '什么是可观测性', link: '/01-foundations/observability-vs-monitoring' },
            { text: '四大支柱', link: '/01-foundations/four-pillars' },
            { text: '信号类型', link: '/01-foundations/signals' },
            { text: 'SLI / SLO / Error Budget', link: '/01-foundations/sli-slo' }
          ]
        },
        {
          text: '🌐 OpenTelemetry', collapsed: false, items: [
            { text: 'OTel 概览', link: '/02-opentelemetry/overview' },
            { text: '各语言 SDK', link: '/02-opentelemetry/sdk' },
            { text: 'OTLP 协议', link: '/02-opentelemetry/otlp' },
            { text: 'OTel Collector', link: '/02-opentelemetry/collector' },
            { text: '自动埋点', link: '/02-opentelemetry/auto-instrumentation' }
          ]
        },
        {
          text: '📈 Prometheus', collapsed: false, items: [
            { text: 'Prometheus 架构', link: '/03-prometheus/overview' },
            { text: '数据模型与 Labels', link: '/03-prometheus/data-model' },
            { text: 'PromQL 详解', link: '/03-prometheus/promql' },
            { text: 'Exporter 生态', link: '/03-prometheus/exporter' },
            { text: '告警规则', link: '/03-prometheus/alert' }
          ]
        },
        {
          text: '📊 Grafana', collapsed: false, items: [
            { text: 'Grafana 安装与数据源', link: '/04-grafana/overview' },
            { text: 'Dashboard 设计', link: '/04-grafana/dashboard' },
            { text: '模板变量', link: '/04-grafana/variables' },
            { text: 'Grafana Alerting', link: '/04-grafana/alerting' },
            { text: 'Annotation 与联动', link: '/04-grafana/annotation' }
          ]
        },
        {
          text: '📜 Loki', collapsed: false, items: [
            { text: 'Loki 架构', link: '/05-loki/overview' },
            { text: 'LogQL 查询', link: '/05-loki/logql' },
            { text: 'Pipeline 配置', link: '/05-loki/pipeline' },
            { text: '最佳实践', link: '/05-loki/best-practice' }
          ]
        },
        {
          text: '🔗 链路追踪', collapsed: false, items: [
            { text: 'Trace / Span 概念', link: '/06-tracing/concepts' },
            { text: 'Jaeger', link: '/06-tracing/jaeger' },
            { text: 'Grafana Tempo', link: '/06-tracing/tempo' },
            { text: 'Zipkin', link: '/06-tracing/zipkin' },
            { text: '协议对比', link: '/06-tracing/protocol-compare' }
          ]
        },
        {
          text: '🌲 ELK / EFK', collapsed: false, items: [
            { text: 'ES 作日志存储', link: '/07-elk-efk/elasticsearch-logs' },
            { text: 'Fluentd 采集', link: '/07-elk-efk/fluentd' },
            { text: 'Filebeat 轻量采集', link: '/07-elk-efk/filebeat' },
            { text: 'Kibana 可视化', link: '/07-elk-efk/kibana' }
          ]
        },
        {
          text: '🚨 告警与值班', collapsed: false, items: [
            { text: 'Alertmanager', link: '/08-alerting/alertmanager' },
            { text: '告警分级 P0/P1/P2', link: '/08-alerting/severity' },
            { text: '静默 / 抑制 / 分组', link: '/08-alerting/silence' },
            { text: 'On-call 与故障复盘', link: '/08-alerting/oncall' }
          ]
        },
        {
          text: '🧪 应用埋点', collapsed: false, items: [
            { text: 'RED 方法', link: '/09-app-instrumentation/red-method' },
            { text: 'USE 方法', link: '/09-app-instrumentation/use-method' },
            { text: 'JVM 埋点 Micrometer', link: '/09-app-instrumentation/jvm-metrics' },
            { text: 'K8s 容器监控', link: '/09-app-instrumentation/k8s-metrics' },
            { text: '业务指标设计', link: '/09-app-instrumentation/business-metrics' }
          ]
        },
        {
          text: '🔥 持续剖析', collapsed: false, items: [
            { text: 'Continuous Profiling', link: '/10-profiling/continuous-profiling' },
            { text: 'Go pprof', link: '/10-profiling/pprof' },
            { text: 'Java async-profiler', link: '/10-profiling/async-profiler' },
            { text: 'Pyroscope 平台', link: '/10-profiling/pyroscope' }
          ]
        },
        {
          text: '🌍 实战场景', collapsed: false, items: [
            { text: 'K8s 全栈监控', link: '/11-scenarios/k8s-monitor' },
            { text: '数据库监控', link: '/11-scenarios/database-monitor' },
            { text: '微服务全链路', link: '/11-scenarios/microservice-trace' },
            { text: '成本优化', link: '/11-scenarios/cost-optimization' }
          ]
        }
      ]
    },
    socialLinks: [],
    footer: {
      message: '本站点基于 VitePress 构建 · CC BY-NC-SA 4.0 · 🏠 <a href="https://java-px.bot.cd/" target="_blank">门户首页</a>',
      copyright: 'Copyright © 2024-2026 Scholar\'s Atlas'
    },
    search: { provider: 'local' }
  }
})