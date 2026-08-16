import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'
import { fileURLToPath, URL } from 'node:url'

const SHARED_ASSETS = fileURLToPath(new URL('../../shared-assets', import.meta.url))

export default withMermaid(defineConfig({
  mermaid: {
    theme: 'default'
  },
  base: '/tools/',
  title: '在线常用工具',
  description: 'JSON 格式化 / 时间戳转换 / URL 编解码 / UUID 生成 等日常在线工具',
  lang: 'zh-CN',
  srcDir: './docs',
  cleanUrls: true,
  lastUpdated: true,
  ignoreDeadLinks: true,
  head: [
    ['link', { rel: 'icon', href: '/favicon.ico', type: 'image/x-icon' }],
    ['link', { rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' }],
    ['link', { rel: 'apple-touch-icon', href: '/apple-touch-icon.png', sizes: '180x180' }],
    ['meta', { name: 'theme-color', content: '#4F46E5' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:locale', content: 'zh_CN' }],
    ['meta', { name: 'description', content: '在线工具集：JSON 格式化/转换、时间戳、时区、URL、Cron、UUID 等' }]
  ],
  themeConfig: {
    siteTitle: '在线常用工具',
    nav: [

      { text: '🏠 门户', link: 'https://java-px.bot.cd/', target: '_blank' },
{ text: '首页', link: '/' },
      { text: 'JSON 工具', link: '/json' },
      { text: '时间工具', link: '/timestamp' },
      { text: '编码工具', link: '/base64' },
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
        { text: '微服务 / Spring Cloud', link: 'https://java-px.bot.cd/cloud/' },
        { text: '计算机网络', link: 'https://java-px.bot.cd/network/' },
        { text: '文件系统与存储', link: 'https://java-px.bot.cd/filesystem/' },
        { text: '视频处理', link: 'https://java-px.bot.cd/video/' }
      ]
      }
    ],
    sidebar: {
      '/': [
        {
          text: 'JSON 系列',
          items: [
            { text: 'JSON 格式化 / 校验', link: '/json' },
            { text: 'JSON ↔ YAML', link: '/json-yaml' },
            { text: 'JSON ↔ CSV', link: '/json-csv' },
            { text: 'JSON Diff 对比', link: '/json-diff' }
          ]
        },
        {
          text: '时间系列',
          items: [
            { text: '时间戳 ↔ 日期', link: '/timestamp' },
            { text: 'ISO / RFC 格式化', link: '/iso' },
            { text: '时区转换', link: '/timezone' },
            { text: '相对时间', link: '/relative' }
          ]
        },
        {
          text: '编码 / 生成',
          items: [
            { text: 'URL 编解码', link: '/url' },
            { text: 'Base64 编解码', link: '/base64' },
            { text: 'UUID 生成器', link: '/uuid' },
            { text: 'Cron 表达式', link: '/cron' }
          ]
        }
      ]
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com' }
    ],
    footer: {
      message: '本地工具 · 完全在浏览器中运行，数据不会上传 · 🏠 <a href="https://java-px.bot.cd/" target="_blank">门户首页</a>',
      copyright: '常用工具集'
    },
    outline: {
      level: [2, 3],
      label: '本页大纲'
    },
    docFooter: { prev: '上一篇', next: '下一篇' },

    search: { provider: 'local' },
  },
  vite: {
    resolve: {
      alias: [
        { find: '@shared', replacement: SHARED_ASSETS },
      ],
    },
    server: {
      fs: {
        strict: false
      }
    }
  }
}))
