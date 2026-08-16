import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

export default withMermaid(defineConfig({
  mermaid: {
    theme: 'default'
  },
  lang: 'zh-CN',
  title: '混沌工程知识图谱',
  description: 'Chaos Engineering：原则、工具（Chaos Mesh / Litmus / Gremlin / ChaosBlade）、韧性模式与游戏日',
  base: '/chaos/',
  srcDir: 'docs',
  cleanUrls: true,
  ignoreDeadLinks: true,

  head: [
    ['link', { rel: 'icon', href: '/favicon.ico', type: 'image/x-icon' }],
    ['link', { rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' }],
    ['link', { rel: 'apple-touch-icon', href: '/apple-touch-icon.png', sizes: '180x180' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { name: 'theme-color', content: '#e11d48' }],
  ],

  themeConfig: {
    logo: { src: '/favicon.svg', alt: 'Chaos Engineering' },
    siteTitle: '混沌工程',

    nav: [
      { text: '🏠 门户', link: 'https://java-px.bot.cd/', target: '_blank' },
      { text: '指南', items: [
        { text: '总览', link: '/' },
        { text: '原则篇', link: '/01-foundations/overview' },
        { text: 'Chaos Mesh', link: '/02-chaos-mesh/overview' },
        { text: 'Litmus', link: '/03-litmus/overview' },
        { text: '工具对比', link: '/04-platform-compare/overview' },
        { text: '韧性模式', link: '/05-resilience-patterns/overview' },
        { text: '游戏日', link: '/06-game-day/overview' },
        { text: '混沌可观测性', link: '/07-observability-for-chaos/overview' },
      ]},
      { text: '🔀 更多站点', items: [
        { text: 'ES', link: 'https://java-px.bot.cd/es/' },
        { text: 'MySQL', link: 'https://java-px.bot.cd/mysql/' },
        { text: 'Redis', link: 'https://java-px.bot.cd/redis/' },
        { text: 'Spring Cloud', link: 'https://java-px.bot.cd/cloud/' },
        { text: 'Python', link: 'https://java-px.bot.cd/python/' },
        { text: 'Kafka', link: 'https://java-px.bot.cd/kafka/' },
        { text: 'Java Web', link: 'https://java-px.bot.cd/java/' },
        { text: '工具', link: 'https://java-px.bot.cd/tools/' },
        { text: 'Frontend', link: 'https://java-px.bot.cd/frontend/' },
        { text: 'Linux', link: 'https://java-px.bot.cd/linux/' },
        { text: 'Cloud Native', link: 'https://java-px.bot.cd/cloud-native/' },
        { text: 'AI', link: 'https://java-px.bot.cd/ai/' },
        { text: 'Java Language', link: 'https://java-px.bot.cd/java-language/' },
        { text: 'BigData', link: 'https://java-px.bot.cd/bigdata/' },
        { text: 'Architecture', link: 'https://java-px.bot.cd/architecture/' },
        { text: 'Network', link: 'https://java-px.bot.cd/network/' },
        { text: 'Video', link: 'https://java-px.bot.cd/video/' },
        { text: 'Filesystem', link: 'https://java-px.bot.cd/filesystem/' },
        { text: 'System Design', link: 'https://java-px.bot.cd/system-design/' },
        { text: 'PostgreSQL', link: 'https://java-px.bot.cd/postgresql/' },
        { text: 'Observability', link: 'https://java-px.bot.cd/observability/' },
        { text: 'Security', link: 'https://java-px.bot.cd/security/' },
        { text: 'DevOps', link: 'https://java-px.bot.cd/devops/' },
        { text: 'Rust', link: 'https://java-px.bot.cd/rust/' },
        { text: 'Go', link: 'https://java-px.bot.cd/go/' },
        { text: 'ClickHouse', link: 'https://java-px.bot.cd/clickhouse/' },
        { text: '🟣 设计模式', link: 'https://java-px.bot.cd/design-pattern/' },
        { text: '🔥 混沌工程', link: 'https://java-px.bot.cd/chaos/' },
      ]},
    ],

    sidebar: {
      '/01-foundations/': [
        { text: '基础篇', items: [
          { text: '概览', link: '/01-foundations/overview' },
          { text: '历史与哲学', link: '/01-foundations/history' },
          { text: '稳态假设', link: '/01-foundations/steady-state' },
          { text: '爆炸半径', link: '/01-foundations/blast-radius' },
        ]},
      ],
      '/02-chaos-mesh/': [
        { text: 'Chaos Mesh', items: [
          { text: '概览', link: '/02-chaos-mesh/overview' },
          { text: '架构与组件', link: '/02-chaos-mesh/architecture' },
          { text: 'PodChaos 实验', link: '/02-chaos-mesh/pod-chaos' },
          { text: 'NetworkChaos 实验', link: '/02-chaos-mesh/network-chaos' },
          { text: '工作流编排', link: '/02-chaos-mesh/workflow' },
        ]},
      ],
      '/03-litmus/': [
        { text: 'Litmus', items: [
          { text: '概览', link: '/03-litmus/overview' },
          { text: 'ChaosExperiment CRD', link: '/03-litmus/chaos-experiment' },
          { text: 'Probe 与 Check', link: '/03-litmus/probe-check' },
          { text: 'Litmus SDK', link: '/03-litmus/sdk' },
        ]},
      ],
      '/04-platform-compare/': [
        { text: '工具对比', items: [
          { text: '概览', link: '/04-platform-compare/overview' },
          { text: 'Chaos Mesh vs Litmus', link: '/04-platform-compare/mesh-vs-litmus' },
          { text: '开源 vs 商业 (Gremlin)', link: '/04-platform-compare/open-vs-commercial' },
          { text: '选型决策树', link: '/04-platform-compare/decision-tree' },
        ]},
      ],
      '/05-resilience-patterns/': [
        { text: '韧性模式', items: [
          { text: '概览', link: '/05-resilience-patterns/overview' },
          { text: '重试与退避', link: '/05-resilience-patterns/retry-backoff' },
          { text: '熔断器', link: '/05-resilience-patterns/circuit-breaker' },
          { text: '限流与降级', link: '/05-resilience-patterns/rate-limit-degrade' },
          { text: '舱壁与隔离', link: '/05-resilience-patterns/bulkhead' },
          { text: '多活与灾备', link: '/05-resilience-patterns/multi-region-dr' },
        ]},
      ],
      '/06-game-day/': [
        { text: '游戏日', items: [
          { text: '概览', link: '/06-game-day/overview' },
          { text: '演练设计', link: '/06-game-day/exercise-design' },
          { text: '角色分工', link: '/06-game-day/roles' },
          { text: '复盘与改进', link: '/06-game-day/retro' },
        ]},
      ],
      '/07-observability-for-chaos/': [
        { text: '混沌可观测性', items: [
          { text: '概览', link: '/07-observability-for-chaos/overview' },
          { text: '稳态假设度量', link: '/07-observability-for-chaos/measure-steady-state' },
          { text: 'SLO 反馈环', link: '/07-observability-for-chaos/slo-feedback-loop' },
          { text: '实战案例', link: '/07-observability-for-chaos/case-study' },
        ]},
      ],
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/chaos-mesh/chaos-mesh' },
    ],

    footer: {
      message: '基于 VitePress 构建 · 混沌工程 28 站知识图谱 · · 🏠 <a href="https://java-px.bot.cd/" target="_blank">门户首页</a>',
      copyright: '© 2026 Chaos Engineering Knowledge Hub',
    },

    search: { provider: 'local' },

    outline: { level: [2, 3], label: '页面导航' },

    docFooter: { prev: '上一篇', next: '下一篇' },

    lastUpdatedText: '最后更新',

    editLink: { text: '在 GitHub 上编辑此页' },
  },
}))
