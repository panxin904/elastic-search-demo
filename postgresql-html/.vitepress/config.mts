import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'
export default withMermaid(defineConfig({
  mermaid: {
    theme: 'default'
  },
  base: '/postgresql/',
  title: 'PostgreSQL 知识图谱',
  description: '现代关系型数据库深度图谱 - JSONB · PostGIS · pgvector · MVCC · CTE · 11 大类 · 60+ 节点',
  lang: 'zh-CN', lastUpdated: true, srcDir: 'docs', cleanUrls: true, ignoreDeadLinks: true,
  head: [
    ['link', { rel: 'icon', href: '/favicon.ico', type: 'image/x-icon' }],
    ['link', { rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' }],
    ['link', { rel: 'apple-touch-icon', href: '/apple-touch-icon.png', sizes: '180x180' }],
    ['meta', { name: 'theme-color', content: '#336791' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:locale', content: 'zh_CN' }],
  ],
  themeConfig: {
    siteTitle: 'PostgreSQL',
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
        { text: '📖 基础入门', items: [
          { text: 'PostgreSQL 概述', link: '/01-basics/overview' },
          { text: '进程架构', link: '/01-basics/architecture' },
          { text: '关键配置参数', link: '/01-basics/config' }
        ]},
        { text: '🔢 数据类型', items: [
          { text: '内置类型', link: '/02-data-types/built-in' },
          { text: '数组类型', link: '/02-data-types/array' },
          { text: 'JSONB 类型', link: '/02-data-types/jsonb' },
          { text: 'range 类型', link: '/02-data-types/range' },
          { text: '自定义类型', link: '/02-data-types/custom' }
        ]},
        { text: '📊 表与索引', items: [
          { text: '表与分区', link: '/03-tables-and-indexes/table' },
          { text: 'B-Tree 索引', link: '/03-tables-and-indexes/btree' },
          { text: 'Hash 索引', link: '/03-tables-and-indexes/hash' },
          { text: 'GIN 索引', link: '/03-tables-and-indexes/gin' },
          { text: 'GiST 索引', link: '/03-tables-and-indexes/gist' },
          { text: 'BRIN 索引', link: '/03-tables-and-indexes/brin' },
          { text: 'SP-GiST 索引', link: '/03-tables-and-indexes/spgist' }
        ]},
        { text: '🔍 查询优化', items: [
          { text: 'EXPLAIN 详解', link: '/04-query/explain' },
          { text: '查询规划器', link: '/04-query/planner' },
          { text: 'CTE 公用表', link: '/04-query/cte' },
          { text: '窗口函数', link: '/04-query/window' },
          { text: '递归查询', link: '/04-query/recursive' },
          { text: '全文检索', link: '/04-query/fulltext-search' }
        ]},
        { text: '🔄 事务与并发', items: [
          { text: 'MVCC 多版本', link: '/05-transaction/mvcc' },
          { text: '隔离级别', link: '/05-transaction/isolation' },
          { text: '锁机制', link: '/05-transaction/lock' },
          { text: '死锁排查', link: '/05-transaction/deadlock' }
        ]},
        { text: '⚙️ 高级特性', items: [
          { text: '视图与物化视图', link: '/06-advanced/view' },
          { text: '触发器', link: '/06-advanced/trigger' },
          { text: '存储过程', link: '/06-advanced/function' },
          { text: 'UPSERT', link: '/06-advanced/upsert' },
          { text: '生成列', link: '/06-advanced/generated' }
        ]},
        { text: '🛠️ 运维管理', items: [
          { text: 'Vacuum 与 autovacuum', link: '/07-operations/vacuum' },
          { text: 'pg_stat_* 视图', link: '/07-operations/stats' },
          { text: '慢查询分析', link: '/07-operations/slow-query' },
          { text: '备份与恢复', link: '/07-operations/backup' },
          { text: '大版本升级', link: '/07-operations/upgrade' }
        ]},
        { text: '📡 复制与高可用', items: [
          { text: '流复制', link: '/08-replication/streaming' },
          { text: '逻辑复制', link: '/08-replication/logical' },
          { text: '热备读写分离', link: '/08-replication/hot-standby' },
          { text: 'Patroni HA', link: '/08-replication/patroni' }
        ]},
        { text: '🔌 客户端与连接', items: [
          { text: 'PgBouncer 连接池', link: '/09-connection/pgbouncer' },
          { text: 'libpq C 接口', link: '/09-connection/libpq' },
          { text: 'psycopg Python', link: '/09-connection/psycopg' },
          { text: 'JDBC', link: '/09-connection/jdbc' }
        ]},
        { text: '🧩 扩展生态', items: [
          { text: 'PostGIS 空间', link: '/10-extensions/postgis' },
          { text: 'pgvector 向量', link: '/10-extensions/pgvector' },
          { text: 'pg_trgm 模糊', link: '/10-extensions/pg_trgm' },
          { text: 'TimescaleDB 时序', link: '/10-extensions/timescaledb' },
          { text: 'Citus 分布式', link: '/10-extensions/citus' }
        ]},
        { text: '⚖️ 横向对比', items: [
          { text: 'MySQL vs PostgreSQL', link: '/11-compare/mysql-vs-postgresql' }
        ]}
      ]
    },
    footer: {
      message: 'Scholar\'s Atlas · PostgreSQL 知识图谱 · 基于 VitePress 1.6 构建 · 本站部署在 VPS 38.207.171.83 · 🏠 <a href="https://java-px.bot.cd/" target="_blank">门户首页</a>'
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/' }
    ],
    outline: { level: [2, 3], label: '本页大纲' },
    docFooter: { prev: '← 上一篇', next: '下一篇 →' },
    lastUpdatedText: '最后更新',
    darkModeSwitchLabel: '深色模式',
    sidebarMenuLabel: '菜单',
    returnToTopLabel: '回到顶部',

    search: { provider: 'local' },
  }
}))
