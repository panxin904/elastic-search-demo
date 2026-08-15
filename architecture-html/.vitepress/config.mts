import { defineConfig } from 'vitepress'
export default defineConfig({
  base: '/architecture/',
  title: '企业级架构 知识图谱',
  description: '系统化学习高可用 / 高并发 / 微服务 / DDD - 14 大类 · 50+ 节点 · 50+ 内容页',
  lang: 'zh-CN', lastUpdated: true, srcDir: 'docs', cleanUrls: true, ignoreDeadLinks: true,
    head: [
    ['link', { rel: 'icon', href: '/favicon.ico', type: 'image/x-icon' }],
    ['link', { rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' }],
    ['link', { rel: 'apple-touch-icon', href: '/apple-touch-icon.png', sizes: '180x180' }],
    ['meta', { name: 'theme-color', content: '#7c3aed' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:locale', content: 'zh_CN' }],
  ],
  themeConfig: {
    siteTitle: '企业级架构',
    nav: [      { text: '🏠 门户', link: 'https://java-px.bot.cd/', target: '_blank' },
{text:'首页',link:'/'},{text:'知识图谱',link:'/graph'},{text:'思维导图',link:'/mindmap'},{text:'命令速查',link:'/cheatsheet'},{text:'学习路径',link:'/path'},
      {
        text: '更多站点',
        items: [
        { text: 'AI 工具 / 大模型', link: 'https://java-px.bot.cd/ai/' },
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
        { text: '在线工具', link: 'https://java-px.bot.cd/tools/' },
        { text: '视频处理', link: 'https://java-px.bot.cd/video/' }
      ]
      }
    ],
    sidebar: {
      '/': [
        {text:'🎯 开始',items:[{text:'📖 学习路径',link:'/path'}]},
        {text:'🧠 并发理论',items:[{text:'JMM 内存模型',link:'/01-concurrency-theory/jmm'},{text:'happens-before',link:'/01-concurrency-theory/happens-before'},{text:'CAS / Lock-Free',link:'/01-concurrency-theory/cas'},{text:'volatile / final',link:'/01-concurrency-theory/volatile'}]},
        {text:'🧵 线程池',items:[{text:'ThreadPoolExecutor',link:'/02-thread-pool/executor'},{text:'ForkJoinPool',link:'/02-thread-pool/forkjoin'},{text:'JDK 21 虚拟线程',link:'/02-thread-pool/virtual'}]},
        {text:'🏛️ 高可用理论',items:[{text:'CAP 定理',link:'/03-ha-theory/cap'},{text:'BASE / 最终一致性',link:'/03-ha-theory/base'},{text:'Raft 共识',link:'/03-ha-theory/raft'},{text:'Quorum 多数派',link:'/03-ha-theory/quorum'},{text:'幂等性设计',link:'/03-ha-theory/idempotency'}]},
        {text:'🚦 限流',items:[{text:'令牌桶算法',link:'/04-rate-limit/token-bucket'},{text:'漏桶 / 滑动窗口',link:'/04-rate-limit/leaky-bucket'},{text:'分布式限流',link:'/04-rate-limit/distributed'}]},
        {text:'⚡ 熔断降级',items:[{text:'熔断器三态',link:'/05-circuit-breaker/states'},{text:'Sentinel / Hystrix',link:'/05-circuit-breaker/impl'},{text:'Fallback 设计',link:'/05-circuit-breaker/fallback'}]},
        {text:'🧩 微服务',items:[{text:'服务拆分原则',link:'/06-microservice/split'},{text:'服务发现',link:'/06-microservice/discovery'},{text:'API 网关',link:'/06-microservice/gateway'},{text:'配置中心',link:'/06-microservice/config'}]},
        {text:'🔄 分布式事务',items:[{text:'2PC / 3PC',link:'/07-distributed-tx/2pc'},{text:'TCC 模式',link:'/07-distributed-tx/tcc'},{text:'Saga 模式',link:'/07-distributed-tx/saga'},{text:'本地消息表',link:'/07-distributed-tx/local-table'}]},
        {text:'📨 消息队列',items:[{text:'Kafka vs RabbitMQ',link:'/08-message-queue/compare'},{text:'顺序 / 幂等',link:'/08-message-queue/idempotency'},{text:'死信 / 重试',link:'/08-message-queue/dlq'}]},
        {text:'💾 缓存',items:[{text:'多级缓存架构',link:'/09-cache/architecture'},{text:'缓存三大问题',link:'/09-cache/breakdown'},{text:'一致性策略',link:'/09-cache/consistency'}]},
        {text:'🗄️ 分库分表',items:[{text:'水平 / 垂直拆分',link:'/10-database-sharding/strategy'},{text:'路由 / 扩容',link:'/10-database-sharding/routing'},{text:'分布式 ID',link:'/10-database-sharding/id'}]},
        {text:'🧠 DDD',items:[{text:'聚合 / 实体 / 值对象',link:'/11-ddd/basics'},{text:'限界上下文',link:'/11-ddd/bounded-context'},{text:'事件风暴',link:'/11-ddd/event-storming'}]},
        {text:'🧱 微服务模式',items:[{text:'Service Mesh',link:'/12-microservice-patterns/service-mesh'},{text:'Sidecar',link:'/12-microservice-patterns/sidecar'},{text:'Saga / Bulkhead',link:'/12-microservice-patterns/saga'}]},
        {text:'🔭 可观测',items:[{text:'Metrics / Tracing / Logging',link:'/13-observability/three-pillars'},{text:'OpenTelemetry',link:'/13-observability/otel'}]},
        {text:'🏢 企业案例',items:[{text:'秒杀系统',link:'/14-enterprise-cases/flash-sale'},{text:'短链系统',link:'/14-enterprise-cases/short-url'},{text:'异地多活',link:'/14-enterprise-cases/multi-region'}]}
      ]
    },
    socialLinks: [{icon:'github',link:'https://github.com'}],
    footer: { message: '企业级架构 - 高可用 / 高并发 / 微服务 / DDD · 🏠 <a href="https://java-px.bot.cd/" target="_blank">门户首页</a>', copyright: 'MIT License' },
    outline: { level: [2,3], label: '页面大纲' },
    docFooter: { prev: '上一篇', next: '下一篇' },

    search: { provider: 'local' },
  }
})