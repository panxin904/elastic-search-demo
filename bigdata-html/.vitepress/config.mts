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
  base: '/bigdata/',
  title: '大数据 / 数据仓库 / 数据湖仓 知识图谱',
  description: '系统化学习大数据 / 数仓 / 数据湖仓 - 14 大类 · 50+ 节点 · 50+ 内容页',
  lang: 'zh-CN', lastUpdated: true, srcDir: 'docs', cleanUrls: true,
    head: [
    ['link', { rel: 'icon', href: '/favicon.ico', type: 'image/x-icon' }],
    ['link', { rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' }],
    ['link', { rel: 'apple-touch-icon', href: '/apple-touch-icon.png', sizes: '180x180' }],
    ['meta', { name: 'theme-color', content: '#0891b2' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:locale', content: 'zh_CN' }],
  ],
  themeConfig: {
    siteTitle: '大数据全栈',
    nav: [      { text: '🏠 门户', link: 'https://java-px.bot.cd/', target: '_blank' },
{text:'首页',link:'/'},{text:'知识图谱',link:'/graph'},{text:'思维导图',link:'/mindmap'},{text:'命令速查',link:'/cheatsheet'},{text:'学习路径',link:'/path'},
      {
        text: '更多站点',
        items: [
        { text: 'AI 工具 / 大模型', link: 'https://java-px.bot.cd/ai/' },
        { text: '企业级架构', link: 'https://java-px.bot.cd/architecture/' },
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
        {text:'🎯 开始',items:[{text:'📖 学习路径',link:'/path'}]},
        {text:'🧠 大数据基础',items:[{text:'4V 特征',link:'/01-basics/4v'},{text:'Hadoop 生态',link:'/01-basics/hadoop-eco'},{text:'批 / 流计算',link:'/01-basics/batch-stream'},{text:'CAP 选型',link:'/01-basics/cap'}]},
        {text:'📦 HDFS',items:[{text:'架构',link:'/02-hdfs/architecture'},{text:'副本机制',link:'/02-hdfs/replication'},{text:'NameNode HA',link:'/02-hdfs/ha'},{text:'HDFS 命令',link:'/02-hdfs/commands'}]},
        {text:'⚙️ MapReduce',items:[{text:'原理',link:'/03-mapreduce/principle'},{text:'Shuffle',link:'/03-mapreduce/shuffle'},{text:'Combiner / Partitioner',link:'/03-mapreduce/optimize'}]},
        {text:'🔥 Spark',items:[{text:'Core / RDD',link:'/04-spark/rdd'},{text:'SQL / DataFrame',link:'/04-spark/dataframe'},{text:'Structured Streaming',link:'/04-spark/streaming'},{text:'Spark 调优',link:'/04-spark/tuning'}]},
        {text:'🌊 Flink',items:[{text:'架构',link:'/05-flink/architecture'},{text:'状态与 Checkpoint',link:'/05-flink/state'},{text:'Exactly-once',link:'/05-flink/exactly-once'},{text:'Flink CDC',link:'/05-flink/cdc'}]},
        {text:'🏛️ Hive',items:[{text:'架构',link:'/06-hive/architecture'},{text:'优化',link:'/06-hive/optimize'},{text:'Hive on Spark/Tez',link:'/06-hive/engine'}]},
        {text:'📨 Kafka 流',items:[{text:'Kafka Streams',link:'/07-kafka-streaming/streams'},{text:'Flink CDC',link:'/07-kafka-streaming/cdc'},{text:'数据血缘',link:'/07-kafka-streaming/lineage'}]},
        {text:'🏛️ 数据建模',items:[{text:'OLAP vs OLTP',link:'/08-modeling/olap-oltp'},{text:'Inmon vs Kimball',link:'/08-modeling/inmon-kimball'},{text:'星型 / 雪花',link:'/08-modeling/star-snowflake'},{text:'Data Vault',link:'/08-modeling/data-vault'}]},
        {text:'🏢 数仓架构',items:[{text:'Snowflake',link:'/09-dw-architecture/snowflake'},{text:'Redshift / BigQuery',link:'/09-dw-architecture/redshift-bigquery'}]},
        {text:'💧 数据湖',items:[{text:'三剑客',link:'/10-data-lake/three-pillars'},{text:'Delta / Iceberg / Hudi',link:'/10-data-lake/delta-iceberg-hudi'},{text:'Lakehouse',link:'/10-data-lake/lakehouse'}]},
        {text:'🔄 ELT',items:[{text:'Airflow / dbt',link:'/11-elt-pipeline/airflow-dbt'},{text:'CDC 同步',link:'/11-elt-pipeline/cdc'},{text:'数据血缘',link:'/11-elt-pipeline/lineage'}]},
        {text:'📊 OLAP 引擎',items:[{text:'ClickHouse',link:'/12-olap-engine/clickhouse'},{text:'Doris / StarRocks',link:'/12-olap-engine/doris-starrocks'},{text:'OLAP 选型',link:'/12-olap-engine/selection'}]},
        {text:'🏢 企业案例',items:[{text:'用户画像',link:'/13-cases/user-profile'},{text:'推荐系统',link:'/13-cases/recommendation'},{text:'风控实时特征',link:'/13-cases/risk-control'},{text:'日志分析平台',link:'/13-cases/log-platform'}]},
        {text:'🎯 面试',items:[{text:'高频题',link:'/14-interview-practice/questions'},{text:'项目案例',link:'/14-interview-practice/cases'}]}
      ]
    },
    socialLinks: [{icon:'github',link:'https://github.com'}],
    footer: { message: '大数据全栈 - 从基础到企业级方案 · 🏠 <a href="https://java-px.bot.cd/" target="_blank">门户首页</a>', copyright: 'MIT License' },
    outline: { level: [2,3], label: '页面大纲' },
    docFooter: { prev: '上一篇', next: '下一篇' },

    search: { provider: 'local' },
  }
}))
