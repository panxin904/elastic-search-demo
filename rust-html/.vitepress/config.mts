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
  base: '/rust/',
  title: 'Rust 知识图谱',
  description: '系统编程与高性能服务深度图谱 - 所有权 / 借用 / 生命周期 · 类型系统 / Trait · Cargo / crates.io · async-await / Tokio · unsafe / FFI / WASM · 6 大类 · 35 节点',
  lang: 'zh-CN',
  lastUpdated: true,
  srcDir: 'docs',
  cleanUrls: true,
  ignoreDeadLinks: true,
  head: [
    ['link', { rel: 'icon', href: '/favicon.ico', type: 'image/x-icon' }],
    ['link', { rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' }],
    ['link', { rel: 'apple-touch-icon', href: '/apple-touch-icon.png', sizes: '180x180' }],
    ['meta', { name: 'theme-color', content: '#ce422b' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:locale', content: 'zh_CN' }],
  ],
  themeConfig: {
    siteTitle: 'Rust',
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
          text: '🦀 Rust 基础', collapsed: false, items: [
            { text: 'Rust 总览', link: '/01-basics/overview' },
            { text: '所有权 Ownership', link: '/01-basics/ownership' },
            { text: '借用 Borrowing', link: '/01-basics/borrowing' },
            { text: '生命周期 Lifetimes', link: '/01-basics/lifetimes' },
            { text: '语法基础', link: '/01-basics/syntax-fundamentals' },
            { text: 'Hello World 实战', link: '/01-basics/hello-world' }
          ]
        },
        {
          text: '🏷️ 类型系统与 Trait', collapsed: false, items: [
            { text: '类型系统总览', link: '/02-types-traits/overview' },
            { text: '枚举与模式匹配', link: '/02-types-traits/enum-and-pattern' },
            { text: '泛型 Generics', link: '/02-types-traits/generics' },
            { text: 'Trait', link: '/02-types-traits/trait' },
            { text: '高级类型', link: '/02-types-traits/advanced-types' },
            { text: 'Trait 对象与动态分发', link: '/02-types-traits/trait-objects' }
          ]
        },
        {
          text: '📦 生态与工具链', collapsed: false, items: [
            { text: '生态总览', link: '/03-ecosystem/overview' },
            { text: 'Cargo', link: '/03-ecosystem/cargo' },
            { text: 'crates.io', link: '/03-ecosystem/crates-io' },
            { text: '标准库', link: '/03-ecosystem/std-lib' },
            { text: '测试与工具链', link: '/03-ecosystem/tooling' }
          ]
        },
        {
          text: '⚡ 并发与异步', collapsed: false, items: [
            { text: '并发总览', link: '/04-concurrency/overview' },
            { text: '线程与 Thread', link: '/04-concurrency/threads' },
            { text: 'async / await', link: '/04-concurrency/async-await' },
            { text: 'Tokio 运行时', link: '/04-concurrency/tokio' },
            { text: 'Channel 与共享状态', link: '/04-concurrency/channels' }
          ]
        },
        {
          text: '⚙️ 系统编程', collapsed: false, items: [
            { text: '系统编程总览', link: '/05-systems/overview' },
            { text: 'unsafe Rust', link: '/05-systems/unsafe' },
            { text: 'FFI 与 C 互操作', link: '/05-systems/ffi' },
            { text: '嵌入式 Rust', link: '/05-systems/embedded' },
            { text: 'WebAssembly', link: '/05-systems/wasm' },
            { text: '性能优化', link: '/05-systems/performance' }
          ]
        },
        {
          text: '🚀 进阶与实战', collapsed: false, items: [
            { text: '宏 Macro', link: '/06-advanced/macro' },
            { text: '闭包与迭代器', link: '/06-advanced/closure-and-iterator' },
            { text: '智能指针', link: '/06-advanced/smart-pointer' },
            { text: '错误处理', link: '/06-advanced/error-handling' },
            { text: '异步生态对比', link: '/06-advanced/async-ecosystem' },
            { text: '案例研究', link: '/06-advanced/case-study' }
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
