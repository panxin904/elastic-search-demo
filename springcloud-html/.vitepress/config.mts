import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

export default withMermaid(defineConfig({
  mermaid: {
    theme: 'default'
  },
  base: '/cloud/',
  title: 'Spring Cloud Alibaba 知识图谱',
  description: 'Spring Boot + Spring Cloud Alibaba 系统化学习 - 用知识图谱串联微服务组件',
  lang: 'zh-CN',
  lastUpdated: true,
  ignoreDeadLinks: true,
  srcDir: 'docs',
  head: [
    ['link', { rel: 'apple-touch-icon', href: '/apple-touch-icon.png', sizes: '180x180' }],
    ['link', { rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' }],
    ['link', { rel: 'icon', href: '/favicon.ico', type: 'image/x-icon' }],
    ['meta', { name: 'theme-color', content: '#6DB33F' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:locale', content: 'zh_CN' }]  ],
  themeConfig: {
    siteTitle: 'Spring Cloud Alibaba 知识图谱',
    nav: [

      { text: '🏠 门户', link: 'https://java-px.bot.cd/', target: '_blank' },
{ text: '首页', link: '/' },
      { text: '知识图谱', link: '/graph' },
      { text: '思维导图', link: '/mindmap' },
      { text: '组件速查', link: '/cheatsheet' },
      { text: '学习路径', link: '/path' },
      { text: '分布式理论', link: '/07-distributed/cap-base' },
      {
        text: '更多站点',
        items: [
        { text: 'AI 工具 / 大模型', link: 'https://java-px.bot.cd/ai/' },
        { text: '企业级架构', link: 'https://java-px.bot.cd/architecture/' },
        { text: '大数据', link: 'https://java-px.bot.cd/bigdata/' },
        { text: '云原生 / Docker / K8s', link: 'https://java-px.bot.cd/cloud-native/' },
        { text: 'ElasticSearch', link: 'https://java-px.bot.cd/es/' },
        { text: '前端 & Node', link: 'https://java-px.bot.cd/frontend/' },
        { text: 'Java 语言', link: 'https://java-px.bot.cd/java-language/' },
        { text: 'Java Web 开发', link: 'https://java-px.bot.cd/java/' },
        { text: 'Kafka', link: 'https://java-px.bot.cd/kafka/' },
        { text: 'Linux 服务器', link: 'https://java-px.bot.cd/linux/' },
        { text: 'MySQL', link: 'https://java-px.bot.cd/mysql/' },
        { text: 'Python', link: 'https://java-px.bot.cd/python/' },
        { text: 'Redis', link: 'https://java-px.bot.cd/redis/' },
        { text: '计算机网络', link: 'https://java-px.bot.cd/network/' },
        { text: '文件系统与存储', link: 'https://java-px.bot.cd/filesystem/' },
        { text: '在线工具', link: 'https://java-px.bot.cd/tools/' },
        { text: '视频处理', link: 'https://java-px.bot.cd/video/' }
      ]
      }
    ],
    sidebar: {
      '/': [
        {
          text: '🎯 开始',
          items: [
            { text: '📖 学习路径', link: '/path' }
          ]
        },
        {
          text: '🍃 Spring Boot 基础',
          items: [
            { text: '🚀 快速开始', link: '/01-springboot/quickstart' },
            { text: '⚙️ 自动配置原理', link: '/01-springboot/auto-config' },
            { text: '🌐 Web 开发', link: '/01-springboot/web' },
            { text: '💾 数据访问', link: '/01-springboot/data' },
            { text: '🔄 事务管理', link: '/01-springboot/transaction' }
          ]
        },
        {
          text: '☁️ Spring Cloud Alibaba 核心',
          items: [
            { text: '📚 Spring Cloud Alibaba 总览', link: '/02-overview/intro' },
            { text: '🌐 Nacos 服务发现', link: '/02-overview/nacos-discovery' },
            { text: '⚙️ Nacos 配置中心', link: '/02-overview/nacos-config' },
            { text: '⚡ Nacos 底层原理', link: '/02-overview/nacos-principle' }
          ]
        },
        {
          text: '🚪 微服务网关',
          items: [
            { text: '🌊 Gateway 基础', link: '/03-gateway/basic' },
            { text: '🛣️ 路由与断言', link: '/03-gateway/route' },
            { text: '🔧 过滤器', link: '/03-gateway/filter' }
          ]
        },
        {
          text: '⚖️ 负载均衡',
          items: [
            { text: '🔄 Spring Cloud LoadBalancer', link: '/04-loadbalancer/basic' },
            { text: '🎯 负载均衡策略', link: '/04-loadbalancer/strategy' }
          ]
        },
        {
          text: '🔐 认证授权',
          items: [
            { text: '🛡️ Spring Security 基础', link: '/05-security/basic' },
            { text: '🔑 OAuth2 + JWT 实战', link: '/05-security/oauth2' },
            { text: '🏛️ 统一认证中心', link: '/05-security/auth-center' }
          ]
        },
        {
          text: '🛠️ 实战与面试',
          items: [
            { text: '💼 综合实战项目', link: '/06-practice/comprehensive' },
            { text: '⚠️ 常见坑与最佳实践', link: '/06-practice/pitfalls' },
            { text: '🎯 高频面试题', link: '/06-practice/interview' }
          ]
        },
        {
          text: '🌐 分布式理论',
          items: [
            { text: '⚖️ CAP 与 BASE 理论', link: '/07-distributed/cap-base' },
            { text: '🏗️ 分布式架构模式', link: '/07-distributed/architecture' },
            { text: '🔐 分布式锁', link: '/07-distributed/distributed-lock' },
            { text: '💰 分布式事务', link: '/07-distributed/distributed-transaction' },
            { text: '🆔 分布式 ID', link: '/07-distributed/distributed-id' },
            { text: '💬 分布式消息队列', link: '/07-distributed/distributed-mq' },
            { text: '📊 分布式存储', link: '/07-distributed/distributed-storage' },
            { text: '🔄 分布式协调', link: '/07-distributed/distributed-coordination' },
            { text: '🔍 分布式追踪', link: '/07-distributed/distributed-tracing' },
            { text: '🛡️ 高可用与限流熔断', link: '/07-distributed/high-availability' }
          ]
        }
      ],
      '/graph': [
        {
          text: '🎯 知识图谱',
          items: [
            { text: '🌐 Spring Cloud 知识图谱', link: '/graph' }
          ]
        }
      ],
      '/mindmap': [
        {
          text: '🎯 思维导图',
          items: [
            { text: '🧭 Spring Cloud 思维导图', link: '/mindmap' }
          ]
        }
      ],
      '/cheatsheet': [
        {
          text: '🎯 组件速查',
          items: [
            { text: '📋 常用配置速查', link: '/cheatsheet' }
          ]
        }
      ],
      '/path': [
        {
          text: '🎯 学习路径',
          items: [
            { text: '📖 Spring Cloud 学习路径', link: '/path' }
          ]
        }
      ]
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com' }
    ],
    footer: {
      message: 'Spring Cloud Alibaba 知识图谱 - 系统化学习微服务 · 🏠 <a href="https://java-px.bot.cd/" target="_blank">门户首页</a>',
      copyright: 'MIT License'
    },
    outline: {
      level: [2, 3],
      label: '页面大纲'
    },
    docFooter: { prev: '上一篇', next: '下一篇' },

    search: { provider: 'local' },
  }
}))
