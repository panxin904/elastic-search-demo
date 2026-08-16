import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

export default withMermaid(defineConfig({
  mermaid: {
    theme: 'default'
  },
  base: '/go/',
  title: 'Go 知识图谱',
  description: '云原生 + 后端微服务深度图谱 - 基础语法 / CSP 并发模型 / goroutine / channel / context · Go 工具链 / 标准库 / 测试 · Docker / Kubernetes / Prometheus / etcd 源码导读 · Gin / gRPC / Kratos 微服务 · runtime GMP / GC / pprof · 6 大类 · 35 节点',
  lang: 'zh-CN',
  lastUpdated: true,
  srcDir: 'docs',
  cleanUrls: true,
  ignoreDeadLinks: true,
  head: [
    ['link', { rel: 'icon', href: '/favicon.ico', type: 'image/x-icon' }],
    ['link', { rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' }],
    ['link', { rel: 'apple-touch-icon', href: '/apple-touch-icon.png', sizes: '180x180' }],
    ['meta', { name: 'theme-color', content: '#00ADD8' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:locale', content: 'zh_CN' }],
  ],
  themeConfig: {
    siteTitle: 'Go',
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
          { text: 'DevOps / CI-CD', link: 'https://java-px.bot.cd/devops/' },
          { text: 'ElasticSearch', link: 'https://java-px.bot.cd/es/' },
          { text: '文件系统与存储', link: 'https://java-px.bot.cd/filesystem/' },
          { text: '前端 & Node', link: 'https://java-px.bot.cd/frontend/' },
          { text: 'Go 语言生态', link: 'https://java-px.bot.cd/go/' },
          { text: 'Java 语言', link: 'https://java-px.bot.cd/java-language/' },
          { text: 'Java Web 开发', link: 'https://java-px.bot.cd/java/' },
          { text: 'Kafka', link: 'https://java-px.bot.cd/kafka/' },
          { text: 'Linux 服务器', link: 'https://java-px.bot.cd/linux/' },
          { text: 'MySQL', link: 'https://java-px.bot.cd/mysql/' },
          { text: '可观测性', link: 'https://java-px.bot.cd/observability/' },
          { text: 'PostgreSQL', link: 'https://java-px.bot.cd/postgresql/' },
          { text: 'Python', link: 'https://java-px.bot.cd/python/' },
          { text: 'Redis', link: 'https://java-px.bot.cd/redis/' },
          { text: 'Rust 系统编程', link: 'https://java-px.bot.cd/rust/' },
          { text: '微服务 / Spring Cloud', link: 'https://java-px.bot.cd/cloud/' },
          { text: '计算机网络', link: 'https://java-px.bot.cd/network/' },
          { text: '安全 / OWASP', link: 'https://java-px.bot.cd/security/' },
          { text: '系统设计', link: 'https://java-px.bot.cd/system-design/' },
          { text: '在线工具', link: 'https://java-px.bot.cd/tools/' },
          { text: '视频处理', link: 'https://java-px.bot.cd/video/' }
        ]
      }
    ],
    sidebar: {
      '/': [
        {
          text: '🐹 Go 基础', collapsed: false, items: [
            { text: 'Go 总览', link: '/01-basics/overview' },
            { text: '语法速览', link: '/01-basics/syntax-fundamentals' },
            { text: '类型与函数', link: '/01-basics/types-and-functions' },
            { text: '错误处理', link: '/01-basics/error-handling' },
            { text: '包与模块管理', link: '/01-basics/package-and-module' },
            { text: 'Hello World 实战', link: '/01-basics/hello-world' }
          ]
        },
        {
          text: '⚡ 并发模型', collapsed: false, items: [
            { text: 'CSP 并发总览', link: '/02-concurrency/overview' },
            { text: 'goroutine', link: '/02-concurrency/goroutine' },
            { text: 'channel', link: '/02-concurrency/channel' },
            { text: 'sync 包', link: '/02-concurrency/sync-package' },
            { text: 'context 上下文', link: '/02-concurrency/context' },
            { text: '并发模式实战', link: '/02-concurrency/patterns' }
          ]
        },
        {
          text: '🔧 生态与工具链', collapsed: false, items: [
            { text: 'Go 生态总览', link: '/03-ecosystem/overview' },
            { text: 'Go 工具链', link: '/03-ecosystem/go-toolchain' },
            { text: '标准库', link: '/03-ecosystem/standard-library' },
            { text: '测试与覆盖率', link: '/03-ecosystem/testing' },
            { text: '性能基准与 pprof', link: '/03-ecosystem/benchmark' }
          ]
        },
        {
          text: '☁️ 云原生生态', collapsed: false, items: [
            { text: '云原生总览', link: '/04-cloud-native/overview' },
            { text: 'Docker 源码导读', link: '/04-cloud-native/docker-internals' },
            { text: 'Kubernetes 源码导读', link: '/04-cloud-native/kubernetes-internals' },
            { text: 'Prometheus 源码导读', link: '/04-cloud-native/prometheus-internals' },
            { text: 'etcd 源码导读', link: '/04-cloud-native/etcd-internals' },
            { text: 'CNCF 项目全景', link: '/04-cloud-native/cncf-ecosystem' }
          ]
        },
        {
          text: '🌐 后端微服务', collapsed: false, items: [
            { text: '微服务总览', link: '/05-microservices/overview' },
            { text: 'Gin 框架', link: '/05-microservices/gin-framework' },
            { text: 'gRPC + Protobuf', link: '/05-microservices/grpc' },
            { text: 'Kratos / go-zero / go-micro', link: '/05-microservices/kratos' },
            { text: '服务治理', link: '/05-microservices/service-governance' },
            { text: '微服务案例研究', link: '/05-microservices/case-study' }
          ]
        },
        {
          text: '🚀 进阶与 runtime', collapsed: false, items: [
            { text: '进阶总览', link: '/06-advanced/overview' },
            { text: 'runtime 调度器 GMP', link: '/06-advanced/runtime' },
            { text: 'GC 三色标记', link: '/06-advanced/gc' },
            { text: 'pprof 与 trace', link: '/06-advanced/pprof' },
            { text: 'cgo 与 FFI', link: '/06-advanced/cgo' },
            { text: '反射 reflect', link: '/06-advanced/reflection' }
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
}))
