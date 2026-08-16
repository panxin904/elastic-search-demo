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
  base: '/system-design/',
  title: 'System Design 知识图谱',
  description: '系统化学习分布式系统理论与经典系统设计题 - 10 大类 · 60+ 节点 · 60+ 内容页',
  lang: 'zh-CN', lastUpdated: true, srcDir: 'docs', cleanUrls: true, ignoreDeadLinks: true,
  head: [
    ['link', { rel: 'icon', href: '/favicon.ico', type: 'image/x-icon' }],
    ['link', { rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' }],
    ['link', { rel: 'apple-touch-icon', href: '/apple-touch-icon.png', sizes: '180x180' }],
    ['meta', { name: 'theme-color', content: '#0891b2' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:locale', content: 'zh_CN' }],
  ],
  themeConfig: {
    siteTitle: 'System Design',
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
          { text: '在线工具', link: 'https://java-px.bot.cd/tools/' },
          { text: '视频处理', link: 'https://java-px.bot.cd/video/' }
        ]
      }
    ],
    sidebar: {
      '/': [
        { text: '📖 理论基础', items: [
          { text: '一致性与系统模型', link: '/01-theory/overview' },
          { text: 'CAP 定理', link: '/01-theory/cap' },
          { text: 'PACELC 扩展', link: '/01-theory/pacelc' },
          { text: 'FLP 不可能', link: '/01-theory/consensus-problem' },
          { text: '一致性级别谱', link: '/01-theory/consistency-model' },
          { text: '共识问题', link: '/01-theory/consensus' }
        ]},
        { text: '💾 分布式存储', items: [
          { text: '数据分片策略', link: '/02-storage/sharding' },
          { text: '一致性哈希', link: '/02-storage/consistent-hash' },
          { text: '副本与读写分离', link: '/02-storage/replica' },
          { text: 'Quorum NWR', link: '/02-storage/quorum' }
        ]},
        { text: '🤝 分布式协调', items: [
          { text: 'Paxos 算法', link: '/03-coordination/paxos' },
          { text: 'Raft 共识', link: '/03-coordination/raft' },
          { text: 'ZAB 协议', link: '/03-coordination/zab' },
          { text: '分布式锁', link: '/03-coordination/distributed-lock' },
          { text: 'Leader Election', link: '/03-coordination/leader-election' }
        ]},
        { text: '🔄 分布式事务', items: [
          { text: '2PC 二阶段提交', link: '/04-transaction/2pc' },
          { text: '3PC 三阶段提交', link: '/04-transaction/3pc' },
          { text: 'TCC 补偿事务', link: '/04-transaction/tcc' },
          { text: 'Saga 长事务', link: '/04-transaction/saga' },
          { text: '本地消息表', link: '/04-transaction/local-message-table' },
          { text: '事务消息', link: '/04-transaction/transactional-message' }
        ]},
        { text: '🧩 微服务模式', items: [
          { text: '服务发现', link: '/05-patterns/service-discovery' },
          { text: '配置中心', link: '/05-patterns/config-center' },
          { text: 'API 网关', link: '/05-patterns/api-gateway' },
          { text: '熔断器', link: '/05-patterns/circuit-breaker' },
          { text: '限流', link: '/05-patterns/rate-limiter' },
          { text: '分布式追踪', link: '/05-patterns/distributed-trace' },
          { text: 'gRPC RPC', link: '/05-patterns/rpc' }
        ]},
        { text: '⚡ 缓存体系', items: [
          { text: '多级缓存架构', link: '/06-cache/multi-level' },
          { text: '缓存模式', link: '/06-cache/cache-pattern' },
          { text: '缓存一致性', link: '/06-cache/consistency' },
          { text: '雪崩/穿透/击穿', link: '/06-cache/three-problems' },
          { text: '热点 Key', link: '/06-cache/hotspot' }
        ]},
        { text: '📨 消息可靠性', items: [
          { text: '不丢消息', link: '/07-messaging/not-lost' },
          { text: '幂等去重', link: '/07-messaging/idempotent' },
          { text: '顺序保证', link: '/07-messaging/order' },
          { text: '消息堆积', link: '/07-messaging/backlog' }
        ]},
        { text: '🏢 高可用设计', items: [
          { text: '主备 / 主从', link: '/08-availability/master-slave' },
          { text: '集群模式', link: '/08-availability/cluster' },
          { text: '多活 / 单元化', link: '/08-availability/multi-idc' },
          { text: '容灾演练', link: '/08-availability/disaster-recovery' }
        ]},
        { text: '🆔 分布式 ID', items: [
          { text: 'Snowflake 雪花', link: '/09-id/snowflake' },
          { text: 'Leaf 美团方案', link: '/09-id/leaf' },
          { text: 'UUID vs Snowflake', link: '/09-id/uuid-vs-snowflake' }
        ]},
        { text: '🎯 经典系统设计题', items: [
          { text: '短链系统', link: '/10-cases/short-url' },
          { text: 'Feed 流系统', link: '/10-cases/feed-stream' },
          { text: '秒杀系统', link: '/10-cases/seckill' },
          { text: '抢红包', link: '/10-cases/grab-redpacket' },
          { text: '排行榜', link: '/10-cases/ranking' },
          { text: '搜索 suggestion', link: '/10-cases/search-suggest' },
          { text: '附近的人 LBS', link: '/10-cases/nearby' },
          { text: '消息推送', link: '/10-cases/notification' }
        ]}
      ]
    },
    socialLinks: [{ icon: 'github', link: 'https://github.com' }],
    footer: {
      message: 'System Design - 分布式系统理论 + 经典设计题 · 🏠 <a href="https://java-px.bot.cd/" target="_blank">门户首页</a>',
      copyright: 'MIT License'
    },
    outline: { level: [2, 3], label: '页面大纲' },
    docFooter: { prev: '上一篇', next: '下一篇' },

    search: { provider: 'local' },
  }
}))
