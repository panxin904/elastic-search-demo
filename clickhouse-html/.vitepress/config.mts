import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

export default withMermaid(defineConfig({
  mermaid: {
    theme: 'default'
  },
  base: '/clickhouse/',
  title: 'ClickHouse 知识图谱',
  description: 'OLAP 列式数据库深度图谱 - MergeTree / 主键索引 / 数据分区 / 向量化执行 / 实时数仓 · Kafka 引擎 / Grafana / Prometheus · vs Doris / StarRocks / TiDB / Snowflake · 6 大类 · 35 节点',
  lang: 'zh-CN',
  lastUpdated: true,
  srcDir: 'docs',
  cleanUrls: true,
  ignoreDeadLinks: true,
  head: [
    ['link', { rel: 'icon', href: '/favicon.ico', type: 'image/x-icon' }],
    ['link', { rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' }],
    ['link', { rel: 'apple-touch-icon', href: '/apple-touch-icon.png', sizes: '180x180' }],
    ['meta', { name: 'theme-color', content: '#FFCC01' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:locale', content: 'zh_CN' }],
  ],
  themeConfig: {
    siteTitle: 'ClickHouse',
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
          text: '🟡 ClickHouse 基础', collapsed: false, items: [
            { text: 'ClickHouse 总览', link: '/01-basics/overview' },
            { text: '历史与特点', link: '/01-basics/history' },
            { text: '安装部署', link: '/01-basics/installation' },
            { text: '客户端与连接', link: '/01-basics/client' },
            { text: '数据类型', link: '/01-basics/data-types' }
          ]
        },
        {
          text: '🔍 SQL 实战', collapsed: false, items: [
            { text: 'SQL 总览', link: '/02-sql/overview' },
            { text: 'SELECT 与聚合', link: '/02-sql/select-aggregate' },
            { text: 'JOIN 用法', link: '/02-sql/join' },
            { text: '常用函数', link: '/02-sql/functions' },
            { text: '窗口函数', link: '/02-sql/window-functions' },
            { text: '字典 Dictionary', link: '/02-sql/dictionary' }
          ]
        },
        {
          text: '⚙️ 表引擎', collapsed: false, items: [
            { text: '表引擎总览', link: '/03-table-engine/overview' },
            { text: 'MergeTree 家族', link: '/03-table-engine/mergetree-family' },
            { text: 'Log 引擎', link: '/03-table-engine/log-engine' },
            { text: 'Kafka 引擎', link: '/03-table-engine/kafka-engine' },
            { text: 'Distributed 表', link: '/03-table-engine/distributed' },
            { text: 'MaterializedView', link: '/03-table-engine/materialized-view' }
          ]
        },
        {
          text: '📊 OLAP 实战场景', collapsed: false, items: [
            { text: 'OLAP 场景总览', link: '/04-olap-scenarios/overview' },
            { text: '用户行为埋点', link: '/04-olap-scenarios/user-tracking' },
            { text: '日志分析', link: '/04-olap-scenarios/log-analysis' },
            { text: '指标存储', link: '/04-olap-scenarios/metrics-storage' },
            { text: '实时数仓', link: '/04-olap-scenarios/realtime-warehouse' },
            { text: 'Bitmap 去重', link: '/04-olap-scenarios/bitmap' }
          ]
        },
        {
          text: '🔌 生态工具链', collapsed: false, items: [
            { text: '生态总览', link: '/05-ecosystem/overview' },
            { text: 'Kafka 实时集成', link: '/05-ecosystem/kafka-integration' },
            { text: 'Grafana 可视化', link: '/05-ecosystem/grafana' },
            { text: 'Prometheus remote_write', link: '/05-ecosystem/prometheus' },
            { text: 'Go 客户端 ch-go', link: '/05-ecosystem/go-client' },
            { text: 'dbt + Airbyte 集成', link: '/05-ecosystem/dbt-airbyte' }
          ]
        },
        {
          text: '🆚 对比与选型', collapsed: false, items: [
            { text: '选型总览', link: '/06-compare/overview' },
            { text: 'vs MySQL / PostgreSQL', link: '/06-compare/vs-mysql-pg' },
            { text: 'vs Doris', link: '/06-compare/vs-doris' },
            { text: 'vs StarRocks', link: '/06-compare/vs-starrocks' },
            { text: 'vs TiDB', link: '/06-compare/vs-tidb' }
          ]
        },
        {
          text: '📖 大厂实战案例', collapsed: false, items: [
            { text: '12 个真实案例', link: '/case-study' }
          ]
        }
      ]
    },
    socialLinks: [],
    footer: {
      message: 'ClickHouse 是 Yandex 开源的高性能列式 OLAP 数据库 · <a href="https://clickhouse.com/" target="_blank">clickhouse.com</a> · 🏠 <a href="https://java-px.bot.cd/" target="_blank">门户首页</a>',
      copyright: 'Copyright © 2026 Scholar\'s Atlas'
    },

    search: { provider: 'local' },
  }
}))
