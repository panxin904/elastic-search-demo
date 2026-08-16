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
  base: '/devops/',
  title: 'DevOps 知识图谱',
  description: '软件交付链深度图谱 - CI/CD Pipeline · IaC · GitOps · 蓝绿 / 灰度 / 金丝雀 · DORA Metrics · 6 大类 · 29 节点',
  lang: 'zh-CN',
  lastUpdated: true,
  srcDir: 'docs',
  cleanUrls: true,
  ignoreDeadLinks: true,
  head: [
    ['link', { rel: 'icon', href: '/favicon.ico', type: 'image/x-icon' }],
    ['link', { rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' }],
    ['link', { rel: 'apple-touch-icon', href: '/apple-touch-icon.png', sizes: '180x180' }],
    ['meta', { name: 'theme-color', content: '#06b6d4' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:locale', content: 'zh_CN' }],
  ],
  themeConfig: {
    siteTitle: 'DevOps',
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
          { text: 'Java 语言', link: 'https://java-px.bot.cd/java-language/' },
          { text: 'Java Web 开发', link: 'https://java-px.bot.cd/java/' },
          { text: 'Kafka', link: 'https://java-px.bot.cd/kafka/' },
          { text: 'Linux 服务器', link: 'https://java-px.bot.cd/linux/' },
          { text: 'MySQL', link: 'https://java-px.bot.cd/mysql/' },
          { text: '可观测性', link: 'https://java-px.bot.cd/observability/' },
          { text: 'PostgreSQL', link: 'https://java-px.bot.cd/postgresql/' },
          { text: 'Python', link: 'https://java-px.bot.cd/python/' },
          { text: 'Redis', link: 'https://java-px.bot.cd/redis/' },
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
          text: '⚙️ CI/CD Pipeline', collapsed: false, items: [
            { text: 'Pipeline 总览', link: '/01-pipeline/overview' },
            { text: 'GitHub Actions', link: '/01-pipeline/github-actions' },
            { text: 'GitLab CI', link: '/01-pipeline/gitlab-ci' },
            { text: 'Jenkins', link: '/01-pipeline/jenkins' },
            { text: 'Tekton', link: '/01-pipeline/tekton' },
            { text: 'Pipeline 最佳实践', link: '/01-pipeline/best-practices' }
          ]
        },
        {
          text: '🏗️ IaC 基础设施即代码', collapsed: false, items: [
            { text: 'IaC 总览', link: '/02-iac/overview' },
            { text: 'Terraform', link: '/02-iac/terraform' },
            { text: 'Pulumi', link: '/02-iac/pulumi' },
            { text: 'Ansible', link: '/02-iac/ansible' },
            { text: 'Terraform vs Pulumi', link: '/02-iac/terraform-vs-pulumi' }
          ]
        },
        {
          text: '🔄 GitOps', collapsed: false, items: [
            { text: 'GitOps 总览', link: '/03-gitops/overview' },
            { text: 'ArgoCD', link: '/03-gitops/argocd' },
            { text: 'Flux', link: '/03-gitops/flux' },
            { text: 'Progressive Delivery', link: '/03-gitops/progressive-delivery' }
          ]
        },
        {
          text: '🚀 发布策略', collapsed: false, items: [
            { text: '发布策略总览', link: '/04-release/overview' },
            { text: '蓝绿部署', link: '/04-release/blue-green' },
            { text: '金丝雀发布', link: '/04-release/canary' },
            { text: 'Feature Flag', link: '/04-release/feature-flag' },
            { text: '回滚机制', link: '/04-release/rollback' }
          ]
        },
        {
          text: '📊 CI/CD 可观测性', collapsed: false, items: [
            { text: '流水线可观测性', link: '/05-cicd-observability/overview' },
            { text: 'DORA Metrics', link: '/05-cicd-observability/dora-metrics' },
            { text: 'Flaky Test', link: '/05-cicd-observability/flaky-test' },
            { text: 'Pipeline 监控', link: '/05-cicd-observability/pipeline-monitoring' }
          ]
        },
        {
          text: '⭐ 最佳实践', collapsed: false, items: [
            { text: '构建缓存', link: '/06-best-practices/caching' },
            { text: '安全流水线', link: '/06-best-practices/secure-pipeline' },
            { text: 'Secrets 管理', link: '/06-best-practices/secrets-management' },
            { text: 'OIDC 联邦', link: '/06-best-practices/oidc-federation' },
            { text: '案例研究', link: '/06-best-practices/case-study' }
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
