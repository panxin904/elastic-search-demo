import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

// https://vitepress.dev/reference/site-config
export default withMermaid(defineConfig({
  mermaid: {
    theme: 'default'
  },
  base: '/es/',
  title: 'ES Knowledge Atlas',
  description: 'Elasticsearch 7 系统化学习 - 用知识图谱串联概念与使用方式',
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
      { text: '存储层', link: '/01-storage/overview' },
      { text: '查询层', link: '/02-query/overview' },
      { text: '分析层', link: '/03-analysis/overview' },
      { text: '运维层', link: '/04-ops/overview' },
      { text: '调试', link: '/05-tools/curl-client' },
      { text: 'DSL', link: '/05-tools/dsl' },
      { text: 'Java', link: '/05-tools/java' },
      { text: '仪表板', link: '/05-tools/dashboard' },
      { text: '部署', link: '/05-tools/deploy' },
      { text: '7 vs 8', link: '/99-compare/diff' },
      {
        text: '更多站点',
        items: [
        { text: 'AI 工具 / 大模型', link: 'https://java-px.bot.cd/ai/' },
        { text: '企业级架构', link: 'https://java-px.bot.cd/architecture/' },
        { text: '大数据', link: 'https://java-px.bot.cd/bigdata/' },
        { text: '云原生 / Docker / K8s', link: 'https://java-px.bot.cd/cloud-native/' },
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
      '/01-storage/': [
        {
          text: '存储层 Storage',
          items: [
            { text: '总览', link: '/01-storage/overview' },
            { text: '集群 Cluster', link: '/01-storage/cluster' },
            { text: '节点 Node', link: '/01-storage/node' },
            { text: '索引 Index', link: '/01-storage/index' },
            { text: '文档 Document', link: '/01-storage/document' },
            { text: '分片 Shard', link: '/01-storage/shard' },
            { text: '副本 Replica', link: '/01-storage/replica' },
            { text: '段 Segment', link: '/01-storage/segment' },
            { text: '映射 Mapping', link: '/01-storage/mapping' },
            { text: '字段类型', link: '/01-storage/field-types' },
            { text: '_source 元数据', link: '/01-storage/source' },
            { text: 'Translog', link: '/01-storage/translog' },
            { text: 'Refresh 机制', link: '/01-storage/refresh' }
          ]
        }
      ],
      '/02-query/': [
        {
          text: '查询层 Query',
          items: [
            { text: '总览', link: '/02-query/overview' },
            { text: 'Query DSL', link: '/02-query/query-dsl' },
            { text: 'Match Query', link: '/02-query/match' },
            { text: 'Term Query', link: '/02-query/term' },
            { text: 'Bool Query', link: '/02-query/bool' },
            { text: 'Range Query', link: '/02-query/range' },
            { text: 'Boost 相关度', link: '/02-query/boost' },
            { text: '分页', link: '/02-query/pagination' },
            { text: '排序', link: '/02-query/sort' },
            { text: 'Highlight', link: '/02-query/highlight' },
            { text: '聚合 Aggregation', link: '/02-query/aggregation' },
            { text: 'Script Query', link: '/02-query/script' },
            { text: 'Multi Search', link: '/02-query/multi-search' },
            { text: 'Search After', link: '/02-query/search-after' },
            { text: 'Query Rewrite', link: '/02-query/rewrite' },
            { text: 'Query Profile', link: '/02-query/profile' }
          ]
        }
      ],
      '/03-analysis/': [
        {
          text: '分析层 Analysis',
          items: [
            { text: '总览', link: '/03-analysis/overview' },
            { text: 'Analyzer 分析器', link: '/03-analysis/analyzer' },
            { text: 'Tokenizer 分词器', link: '/03-analysis/tokenizer' },
            { text: 'Token Filter', link: '/03-analysis/token-filter' },
            { text: 'Char Filter', link: '/03-analysis/char-filter' },
            { text: '内置分词器', link: '/03-analysis/builtin-analyzers' },
            { text: 'IK 分词器', link: '/03-analysis/ik-analyzer' },
            { text: 'pinyin 分词器', link: '/03-analysis/pinyin-analyzer' },
            { text: '自定义分词', link: '/03-analysis/custom-analyzer' },
            { text: '倒排索引', link: '/03-analysis/inverted-index' },
            { text: 'BM25 相关度', link: '/03-analysis/bm25' },
            { text: 'Explain API', link: '/03-analysis/explain' }
          ]
        }
      ],
      '/04-ops/': [
        {
          text: '运维层 Ops',
          items: [
            { text: '总览', link: '/04-ops/overview' },
            { text: '安装部署', link: '/04-ops/installation' },
            { text: 'JVM 调优', link: '/04-ops/jvm-tuning' },
            { text: '分片分配', link: '/04-ops/shard-allocation' },
            { text: '集群健康', link: '/04-ops/cluster-health' },
            { text: 'Snapshot 备份', link: '/04-ops/snapshot' },
            { text: 'ILM 生命周期', link: '/04-ops/ilm' },
            { text: 'Curator 工具', link: '/04-ops/curator' },
            { text: '监控 Cerebro', link: '/04-ops/monitoring' },
            { text: '慢日志', link: '/04-ops/slow-log' },
            { text: '集群重启', link: '/04-ops/restart' },
            { text: '_cat API', link: '/04-ops/cat-api' },
            { text: '索引模板', link: '/04-ops/index-template' },
            { text: '别名 Alias', link: '/04-ops/alias' }
          ]
        }
      ],
      '/05-tools/': [
        {
          text: '🛠️ 工具 Tools',
          items: [
            { text: '🚀 请求调试器', link: '/05-tools/curl-client' },
            { text: '📚 Query DSL 速查', link: '/05-tools/dsl' },
            { text: '☕ Java SDK 速查', link: '/05-tools/java' },
            { text: '📚 使用场景与最佳实践', link: '/05-tools/scenarios' },
            { text: '📊 集群监控仪表板', link: '/05-tools/dashboard' },
            { text: '⚙️ 部署与生产配置', link: '/05-tools/deploy' }
          ]
        }
      ],
      '/99-compare/': [
        {
          text: '版本对比',
          items: [
            { text: '7 vs 8 差异', link: '/99-compare/diff' }
          ]
        }
      ]
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/elastic/elasticsearch' }
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
      message: '基于 VitePress 构建 · 数据来源 Elasticsearch 7.17 官方文档 · 🏠 <a href="https://java-px.bot.cd/" target="_blank">门户首页</a>',
      copyright: 'ES Knowledge Atlas'
    }
  }
}))
