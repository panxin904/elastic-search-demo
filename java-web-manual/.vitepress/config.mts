import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

export default withMermaid(defineConfig({
  mermaid: {
    theme: 'default'
  },
  base: '/java/',
  title: 'Java Web Dev Manual',
  description: 'Java Web 开发手册 - 开发流程 · 实现思路 · 重点关注 · 技术栈',
  head: [
    ['link', { rel: 'icon', href: '/favicon.ico', type: 'image/x-icon' }],
    ['link', { rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' }],
    ['link', { rel: 'apple-touch-icon', href: '/apple-touch-icon.png', sizes: '180x180' }],
    ['meta', { property: 'og:type', content: 'website' }],
  ],
  lang: 'zh-CN',
  srcDir: './docs',
  cleanUrls: true,
  lastUpdated: true,
  ignoreDeadLinks: true,
  themeConfig: {
    nav: [
      { text: '🏠 门户', link: 'https://java-px.bot.cd/', target: '_blank' },
      { text: '首页', link: '/' },
      { text: '开发流程', link: '/01-process/overview' },
      { text: '实现思路', link: '/02-design/overview' },
      { text: '重点关注', link: '/03-practice/overview' },
      { text: '技术栈', link: '/04-tech/overview' },
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
      '/01-process/': [
        {
          text: '开发流程',
          items: [
            { text: '总览', link: '/01-process/overview' },
            { text: '需求分析', link: '/01-process/requirement-analysis' },
            { text: '技术方案', link: '/01-process/tech-solution' },
            { text: '数据库设计', link: '/01-process/database-design' },
            { text: '接口设计', link: '/01-process/api-design' },
            { text: '编码开发', link: '/01-process/coding' },
            { text: '代码评审', link: '/01-process/code-review' },
            { text: '单元测试', link: '/01-process/unit-test' },
            { text: '集成测试', link: '/01-process/integration-test' },
            { text: '部署上线', link: '/01-process/deployment' },
            { text: '监控运维', link: '/01-process/monitoring' },
            { text: '迭代优化', link: '/01-process/iteration' },
            { text: '文档沉淀', link: '/01-process/documentation' }
          ]
        }
      ],
      '/02-design/': [
        {
          text: '实现思路',
          items: [
            { text: '总览', link: '/02-design/overview' },
            { text: '分层架构', link: '/02-design/layered-architecture' },
            { text: 'MVC 模式', link: '/02-design/mvc-pattern' },
            { text: '依赖注入', link: '/02-design/dependency-injection' },
            { text: 'AOP 切面', link: '/02-design/aop' },
            { text: 'RESTful 风格', link: '/02-design/restful-api' },
            { text: '领域驱动 DDD', link: '/02-design/ddd' },
            { text: '微服务架构', link: '/02-design/microservices' },
            { text: '责任链模式', link: '/02-design/chain-of-responsibility' },
            { text: '策略模式', link: '/02-design/strategy-pattern' },
            { text: '模板方法模式', link: '/02-design/template-method' },
            { text: '工厂模式', link: '/02-design/factory-pattern' },
            { text: '代理模式', link: '/02-design/proxy-pattern' }
          ]
        }
      ],
      '/03-practice/': [
        {
          text: '重点关注',
          items: [
            { text: '总览', link: '/03-practice/overview' },
            { text: '异常处理', link: '/03-practice/exception-handling' },
            { text: '日志规范', link: '/03-practice/logging' },
            { text: '参数校验', link: '/03-practice/validation' },
            { text: '事务管理', link: '/03-practice/transaction' },
            { text: '缓存策略', link: '/03-practice/cache-strategy' },
            { text: '安全实践', link: '/03-practice/security' },
            { text: '性能优化', link: '/03-practice/performance' },
            { text: '代码规范', link: '/03-practice/code-style' },
            { text: '接口幂等', link: '/03-practice/idempotency' },
            { text: '数据脱敏', link: '/03-practice/data-masking' },
            { text: '限流熔断', link: '/03-practice/rate-limiting' },
            { text: '并发控制', link: '/03-practice/concurrency' }
          ]
        }
      ],
      '/04-tech/': [
        {
          text: '技术栈',
          items: [
            { text: '总览', link: '/04-tech/overview' },
            { text: 'Spring Boot', link: '/04-tech/spring-boot' },
            { text: 'Spring MVC', link: '/04-tech/spring-mvc' },
            { text: 'Spring Security', link: '/04-tech/spring-security' },
            { text: 'MyBatis / Plus', link: '/04-tech/mybatis' },
            { text: 'MySQL', link: '/04-tech/mysql' },
            { text: 'Redis', link: '/04-tech/redis' },
            { text: '消息队列 MQ', link: '/04-tech/message-queue' },
            { text: 'Maven / Gradle', link: '/04-tech/build-tools' },
            { text: 'Docker', link: '/04-tech/docker' },
            { text: 'Nginx', link: '/04-tech/nginx' },
            { text: '测试框架', link: '/04-tech/testing' },
            { text: '接口文档', link: '/04-tech/api-doc' }
          ]
        }
      ]
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com' }
    ],
    search: {
      provider: 'local',
      options: {
        miniSearch: {
          searchOptions: {
            fuzzy: 0.2,
            prefix: true,
            boost: { title: 4, text: 2 }
          }
        }
      }
    },
    outline: { level: [2, 3], label: '本页目录' },
    docFooter: { prev: '上一篇', next: '下一篇' },
    footer: {
      message: '基于 VitePress 构建 · Java Web 开发系统化手册 · 🏠 <a href="https://java-px.bot.cd/" target="_blank">门户首页</a>',
      copyright: 'Java Web Dev Manual'
    }
  }
}))
