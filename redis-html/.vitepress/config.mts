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
  base: '/redis/',
  title: 'Redis 知识图谱',
  description: 'Redis 系统化学习 - 知识图谱、思维导图、底层原理、企业实战',
  lang: 'zh-CN',
  lastUpdated: true,
  srcDir: 'docs',
  head: [
    ['link', { rel: 'apple-touch-icon', href: '/apple-touch-icon.png', sizes: '180x180' }],
    ['link', { rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' }],
    ['link', { rel: 'icon', href: '/favicon.ico', type: 'image/x-icon' }],
    ['meta', { name: 'theme-color', content: '#DC382D' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:locale', content: 'zh_CN' }]  ],
  themeConfig: {
    siteTitle: 'Redis 知识图谱',
    nav: [

      { text: '🏠 门户', link: 'https://java-px.bot.cd/', target: '_blank' },
{ text: '首页', link: '/' },
      { text: '知识图谱', link: '/graph' },
      { text: '思维导图', link: '/mindmap' },
      { text: '命令速查', link: '/cheatsheet' },
      { text: '学习路径', link: '/path' },
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
        {
          text: '🎯 开始',
          items: [
            { text: '📖 学习路径', link: '/path' }
          ]
        },
        {
          text: '🚀 基础入门',
          items: [
            { text: '❓ Redis 是什么', link: '/01-basics/intro' },
            { text: '📥 安装部署', link: '/01-basics/install' },
            { text: '📦 5 大基础类型', link: '/01-basics/datatypes' },
            { text: '🔑 Key 通用操作', link: '/01-basics/keys' },
            { text: '⏱️ 过期策略', link: '/01-basics/expiration' }
          ]
        },
        {
          text: '🧬 数据结构原理',
          items: [
            { text: '🎯 RedisObject', link: '/02-datastruct/object' },
            { text: '📝 SDS 简单动态字符串', link: '/02-datastruct/sds' },
            { text: '🗂️ Dict 哈希表', link: '/02-datastruct/dict' },
            { text: '🦘 SkipList 跳表', link: '/02-datastruct/skiplist' },
            { text: '📋 Listpack 紧凑列表', link: '/02-datastruct/listpack' },
            { text: '🔗 QuickList', link: '/02-datastruct/quicklist' },
            { text: '🌊 Stream 流', link: '/02-datastruct/stream' }
          ]
        },
        {
          text: '💾 持久化机制',
          items: [
            { text: '📚 持久化总览', link: '/03-persistence/overview' },
            { text: '📸 RDB 快照', link: '/03-persistence/rdb' },
            { text: '📜 AOF 日志', link: '/03-persistence/aof' },
            { text: '🔀 混合持久化', link: '/03-persistence/mixed' },
            { text: '🔙 数据恢复策略', link: '/03-persistence/recovery' }
          ]
        },
        {
          text: '🔗 高可用集群',
          items: [
            { text: '🔁 主从复制', link: '/04-cluster/replication' },
            { text: '🛡️ Sentinel 哨兵', link: '/04-cluster/sentinel' },
            { text: '🌐 Cluster 集群', link: '/04-cluster/cluster' },
            { text: '🎰 哈希槽分片', link: '/04-cluster/slots' },
            { text: '💬 Gossip 协议', link: '/04-cluster/gossip' },
            { text: '🚚 数据迁移', link: '/04-cluster/migration' },
            { text: '📈 集群扩容', link: '/04-cluster/scale' }
          ]
        },
        {
          text: '☕ Java SDK',
          items: [
            { text: '🔧 Jedis', link: '/05-jdk/jedis' },
            { text: '🥬 Lettuce', link: '/05-jdk/lettuce' },
            { text: '🔴 Redisson', link: '/05-jdk/redisson' },
            { text: '💧 连接池', link: '/05-jdk/connection-pool' },
            { text: '🌱 Spring Data Redis', link: '/05-jdk/spring-data-redis' },
            { text: '🎁 Spring Cache 集成', link: '/05-jdk/spring-cache' }
          ]
        },
        {
          text: '💼 企业实战',
          items: [
            { text: '🔒 分布式锁', link: '/06-practice/distributed-lock' },
            { text: '👤 分布式 Session', link: '/06-practice/session' },
            { text: '🆔 全局唯一 ID', link: '/06-practice/global-id' },
            { text: '🚦 限流', link: '/06-practice/ratelimit' },
            { text: '🌐 分布式限流', link: '/06-practice/distributed-ratelimit' },
            { text: '📨 Stream 消息队列', link: '/06-practice/stream-mq' },
            { text: '⏰ 延迟队列', link: '/06-practice/delay-queue' },
            { text: '🏆 排行榜', link: '/06-practice/leaderboard' },
            { text: '🔢 计数器', link: '/06-practice/counter' },
            { text: '⚖️ 缓存一致性', link: '/06-practice/cache-consistency' }
          ]
        },
        {
          text: '🛠️ 运维调优',
          items: [
            { text: '🗑️ 内存淘汰策略', link: '/07-ops/eviction' },
            { text: '💾 内存管理优化', link: '/07-ops/memory' },
            { text: '🔑 大 Key 热 Key', link: '/07-ops/bigkey-hotkey' },
            { text: '🐢 慢查询分析', link: '/07-ops/slowlog' },
            { text: '📊 监控告警', link: '/07-ops/monitoring' },
            { text: '🆕 Redis 7 新特性', link: '/07-ops/redis7-features' }
          ]
        },
        {
          text: '🎯 面试手撕题',
          items: [
            { text: '📝 高频面试题（上）', link: '/08-interview/basic' },
            { text: '📝 高频面试题（下）', link: '/08-interview/advanced' },
            { text: '🔒 分布式锁手撕', link: '/08-interview/lock-coding' },
            { text: '📚 LRU 算法手撕', link: '/08-interview/lru' },
            { text: '🦘 跳表手撕', link: '/08-interview/skiplist-coding' },
            { text: '❄️ 缓存三大问题', link: '/08-interview/avalanche' },
            { text: '🎯 一致性 Hash', link: '/08-interview/consistent-hash' },
            { text: '📜 Paxos/Raft 概述', link: '/08-interview/consensus' }
          ]
        }
      ],
      '/graph': [
        {
          text: '🎯 知识图谱',
          items: [
            { text: '🌐 Redis 全局知识图谱', link: '/graph' }
          ]
        }
      ],
      '/mindmap': [
        {
          text: '🎯 思维导图',
          items: [
            { text: '🧭 Redis 思维导图', link: '/mindmap' }
          ]
        }
      ],
      '/cheatsheet': [
        {
          text: '🎯 命令速查',
          items: [
            { text: '📋 Redis 命令速查', link: '/cheatsheet' }
          ]
        }
      ],
      '/path': [
        {
          text: '🎯 学习路径',
          items: [
            { text: '📖 Redis 学习路径', link: '/path' }
          ]
        }
      ]
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com' }
    ],
    footer: {
      message: 'Redis 知识图谱 - 系统化学习 Redis · 🏠 <a href="https://java-px.bot.cd/" target="_blank">门户首页</a>',
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
