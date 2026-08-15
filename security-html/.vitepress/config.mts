import { defineConfig } from 'vitepress'

export default defineConfig({
  base: '/security/',
  title: 'Security 知识图谱',
  description: 'Web 安全深度图谱 - OWASP Top 10 2025 · OAuth 2.0 / OIDC · JWT · 密码学 · TLS · 容器安全 · 零信任 · 6 大类 · 32 节点',
  lang: 'zh-CN',
  lastUpdated: true,
  srcDir: 'docs',
  cleanUrls: true,
  ignoreDeadLinks: true,
  head: [
    ['link', { rel: 'icon', href: '/favicon.ico', type: 'image/x-icon' }],
    ['link', { rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' }],
    ['link', { rel: 'apple-touch-icon', href: '/apple-touch-icon.png', sizes: '180x180' }],
    ['meta', { name: 'theme-color', content: '#7c3aed' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:locale', content: 'zh_CN' }],
  ],
  themeConfig: {
    siteTitle: 'Security',
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
          { text: '可观测性', link: 'https://java-px.bot.cd/observability/' },
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
          text: '🛡️ OWASP Top 10 2025', collapsed: false, items: [
            { text: 'OWASP 总览', link: '/01-web-top10/overview' },
            { text: 'A01 访问控制失效', link: '/01-web-top10/a01-broken-access' },
            { text: 'A02 加密机制失效', link: '/01-web-top10/a02-crypto-failure' },
            { text: 'A03 注入攻击', link: '/01-web-top10/a03-injection' },
            { text: 'A04 不安全设计', link: '/01-web-top10/a04-insecure-design' },
            { text: 'A05 安全配置错误', link: '/01-web-top10/a05-misconfig' },
            { text: 'A06 易受攻击组件', link: '/01-web-top10/a06-vulnerable-component' },
            { text: 'A07 认证失效', link: '/01-web-top10/a07-auth-failure' },
            { text: 'A08 软件数据完整性', link: '/01-web-top10/a08-software-data-integrity' },
            { text: 'A09 日志与监控失效', link: '/01-web-top10/a09-logging-failure' },
            { text: 'A10 SSRF', link: '/01-web-top10/a10-ssrf' }
          ]
        },
        {
          text: '🔐 认证与授权', collapsed: false, items: [
            { text: '认证协议总览', link: '/02-auth/overview' },
            { text: 'OAuth 2.0', link: '/02-auth/oauth2' },
            { text: 'OpenID Connect', link: '/02-auth/oidc' },
            { text: 'JWT 详解', link: '/02-auth/jwt' },
            { text: 'SAML', link: '/02-auth/saml' },
            { text: 'Session 攻击', link: '/02-auth/session-attack' },
            { text: 'MFA 多因素认证', link: '/02-auth/mfa' }
          ]
        },
        {
          text: '🔏 密码学', collapsed: false, items: [
            { text: '密码学总览', link: '/03-crypto/overview' },
            { text: '对称加密', link: '/03-crypto/symmetric' },
            { text: '非对称加密', link: '/03-crypto/asymmetric' },
            { text: '哈希函数', link: '/03-crypto/hash' },
            { text: '数字签名', link: '/03-crypto/signature' },
            { text: 'TLS 1.3 握手', link: '/03-crypto/tls-deep-dive' }
          ]
        },
        {
          text: '🌐 网络安全', collapsed: false, items: [
            { text: 'TLS PKI 体系', link: '/04-network/tls-pki' },
            { text: 'mTLS 双向认证', link: '/04-network/mtls' },
            { text: 'HSTS / CSP', link: '/04-network/hsts-csp' },
            { text: 'CORS 跨域', link: '/04-network/cors' }
          ]
        },
        {
          text: '📦 容器安全', collapsed: false, items: [
            { text: '容器安全总览', link: '/05-container/overview' },
            { text: '镜像扫描', link: '/05-container/image-scan' },
            { text: '运行时安全', link: '/05-container/runtime-security' },
            { text: '供应链 SBOM', link: '/05-container/supply-chain' }
          ]
        },
        {
          text: '🔒 零信任架构', collapsed: false, items: [
            { text: '零信任总览', link: '/06-zero-trust/overview' },
            { text: 'SPIFFE / SPIRE', link: '/06-zero-trust/spiffe' },
            { text: '落地实践', link: '/06-zero-trust/implementation' }
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
