import { defineConfig } from 'vitepress'

export default defineConfig({
  base: '/design-pattern/',
  title: '设计模式知识图谱',
  description: 'GoF 23 模式 + 现代架构模式 + 反模式自查表 - 创建型 / 结构型 / 行为型 · 依赖注入 · CQRS · Event Sourcing · Saga · 6 大类 · 36 节点 · Java + Go + TypeScript 多语言实现',
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
    siteTitle: '设计模式',
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
          { text: '设计模式', link: 'https://java-px.bot.cd/design-pattern/' },
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
          { text: '视频处理', link: 'https://java-px.bot.cd/video/' },
          { text: 'ClickHouse OLAP', link: 'https://java-px.bot.cd/clickhouse/' }
        ]
      }
    ],
    sidebar: {
      '/': [
        {
          text: '🏗️ GoF 创建型模式', collapsed: false, items: [
            { text: '创建型总览', link: '/01-gof-creational/overview' },
            { text: 'Singleton 单例', link: '/01-gof-creational/singleton' },
            { text: 'Factory Method 工厂方法', link: '/01-gof-creational/factory-method' },
            { text: 'Abstract Factory 抽象工厂', link: '/01-gof-creational/abstract-factory' },
            { text: 'Builder 建造者', link: '/01-gof-creational/builder' },
            { text: 'Prototype 原型', link: '/01-gof-creational/prototype' }
          ]
        },
        {
          text: '🧩 GoF 结构型模式', collapsed: false, items: [
            { text: '结构型总览', link: '/02-gof-structural/overview' },
            { text: 'Adapter 适配器', link: '/02-gof-structural/adapter' },
            { text: 'Bridge 桥接', link: '/02-gof-structural/bridge' },
            { text: 'Composite 组合', link: '/02-gof-structural/composite' },
            { text: 'Decorator 装饰器', link: '/02-gof-structural/decorator' },
            { text: 'Facade 外观', link: '/02-gof-structural/facade' },
            { text: 'Flyweight 享元', link: '/02-gof-structural/flyweight' },
            { text: 'Proxy 代理', link: '/02-gof-structural/proxy' }
          ]
        },
        {
          text: '🎭 GoF 行为型模式', collapsed: false, items: [
            { text: '行为型总览', link: '/03-gof-behavioral/overview' },
            { text: 'Chain of Responsibility 责任链', link: '/03-gof-behavioral/chain-of-responsibility' },
            { text: 'Command 命令', link: '/03-gof-behavioral/command' },
            { text: 'Iterator 迭代器', link: '/03-gof-behavioral/iterator' },
            { text: 'Mediator 中介者', link: '/03-gof-behavioral/mediator' },
            { text: 'Memento 备忘录', link: '/03-gof-behavioral/memento' },
            { text: 'Observer 观察者', link: '/03-gof-behavioral/observer' },
            { text: 'State 状态', link: '/03-gof-behavioral/state' },
            { text: 'Strategy 策略', link: '/03-gof-behavioral/strategy' },
            { text: 'Template Method 模板方法', link: '/03-gof-behavioral/template-method' },
            { text: 'Visitor 访问者', link: '/03-gof-behavioral/visitor' },
            { text: 'Interpreter 解释器', link: '/03-gof-behavioral/interpreter' }
          ]
        },
        {
          text: '✨ 现代模式', collapsed: false, items: [
            { text: '现代模式总览', link: '/04-modern-patterns/overview' },
            { text: '依赖注入 DI', link: '/04-modern-patterns/dependency-injection' },
            { text: 'Repository 仓储', link: '/04-modern-patterns/repository' },
            { text: 'Specification 规格', link: '/04-modern-patterns/specification' },
            { text: 'Null Object 空对象', link: '/04-modern-patterns/null-object' }
          ]
        },
        {
          text: '🌐 架构模式', collapsed: false, items: [
            { text: '架构模式总览', link: '/05-architectural-patterns/overview' },
            { text: 'CQRS 命令查询分离', link: '/05-architectural-patterns/cqrs' },
            { text: 'Event Sourcing 事件溯源', link: '/05-architectural-patterns/event-sourcing' },
            { text: 'Saga 分布式事务', link: '/05-architectural-patterns/saga' },
            { text: 'Sidecar 边车', link: '/05-architectural-patterns/sidecar' },
            { text: 'Circuit Breaker 熔断', link: '/05-architectural-patterns/circuit-breaker' },
            { text: 'Bulkhead 舱壁隔离', link: '/05-architectural-patterns/bulkhead' },
            { text: 'Strangler Fig 绞杀者', link: '/05-architectural-patterns/strangler-fig' },
            { text: 'Outbox 事务性发件箱', link: '/05-architectural-patterns/outbox' }
          ]
        },
        {
          text: '🚫 反模式', collapsed: false, items: [
            { text: '反模式总览', link: '/06-anti-patterns/overview' },
            { text: 'God Object 上帝对象', link: '/06-anti-patterns/god-object' },
            { text: 'Anemic Model 贫血模型', link: '/06-anti-patterns/anemic-model' },
            { text: 'Big Ball of Mud 大泥球', link: '/06-anti-patterns/big-ball-of-mud' },
            { text: 'Callback Hell 回调地狱', link: '/06-anti-patterns/callback-hell' },
            { text: 'Circular Dependency 循环依赖', link: '/06-anti-patterns/circular-dependency' },
            { text: 'Magic Number 魔数', link: '/06-anti-patterns/magic-number' },
            { text: 'Premature Optimization 提前优化', link: '/06-anti-patterns/premature-optimization' }
          ]
        }
      ]
    },
    socialLinks: [],
    footer: {
      message: '设计模式是面向对象编程与软件工程的核心抽象武器 · <a href="https://en.wikipedia.org/wiki/Design_Patterns" target="_blank">GoF 1994</a> · 🏠 <a href="https://java-px.bot.cd/" target="_blank">门户首页</a>',
      copyright: 'Copyright © 2026 Scholar\'s Atlas'
    },

    search: { provider: 'local' },
  }
})