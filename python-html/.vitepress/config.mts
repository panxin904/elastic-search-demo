import { defineConfig } from 'vitepress'

export default defineConfig({
  base: '/python/',
  title: 'Python 知识图谱',
  description: 'Python 系统化学习 - 知识图谱、思维导图、底层原理、AI/爬虫/数据实战',
  lang: 'zh-CN',
  lastUpdated: true,
  // 部分学习路径仍在补充中，构建阶段保留现有页面并允许未完成页面的链接。
  ignoreDeadLinks: true,
  srcDir: 'docs',
  head: [
    ['link', { rel: 'apple-touch-icon', href: '/apple-touch-icon.png', sizes: '180x180' }],
    ['link', { rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' }],
    ['link', { rel: 'icon', href: '/favicon.ico', type: 'image/x-icon' }],
    ['meta', { name: 'theme-color', content: '#3776AB' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:locale', content: 'zh_CN' }]  ],
  themeConfig: {
    siteTitle: 'Python 知识图谱',
    nav: [

      { text: '🏠 门户', link: 'https://java-px.bot.cd/', target: '_blank' },
{ text: '首页', link: '/' },
      { text: '知识图谱', link: '/graph' },
      { text: '思维导图', link: '/mindmap' },
      { text: '速查表', link: '/cheatsheet' },
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
        { text: '🎯 开始', items: [{ text: '📖 学习路径', link: '/path' }] },
        {
          text: '🐍 Python 入门',
          items: [
            { text: '❓ Python 是什么', link: '/01-basics/intro' },
            { text: '📥 安装与环境', link: '/01-basics/install' },
            { text: '🔤 基础语法', link: '/01-basics/syntax' },
            { text: '📦 数据结构', link: '/01-basics/data-structures' },
            { text: '🔁 控制流', link: '/01-basics/control-flow' }
          ]
        },
        {
          text: '🔬 底层原理',
          items: [
            { text: '🏗️ Python 解释器', link: '/02-principles/interpreter' },
            { text: '🧠 字节码与执行', link: '/02-principles/bytecode' },
            { text: '📦 对象模型', link: '/02-principles/object-model' },
            { text: '🗑️ 内存管理', link: '/02-principles/memory' },
            { text: '⏱️ GIL 全局锁', link: '/02-principles/gil' },
            { text: '🔍 垃圾回收', link: '/02-principles/gc' },
            { text: '📊 性能剖析', link: '/02-principles/profiling' }
          ]
        },
        {
          text: '📚 常用库',
          items: [
            { text: '🎯 标准库概览', link: '/03-libraries/stdlib' },
            { text: '🌐 requests HTTP', link: '/03-libraries/requests' },
            { text: '🕷️ BeautifulSoup', link: '/03-libraries/beautifulsoup' },
            { text: '🗄️ SQLAlchemy ORM', link: '/03-libraries/sqlalchemy' },
            { text: '📊 pandas 数据分析', link: '/03-libraries/pandas' },
            { text: '🧪 pytest 测试', link: '/03-libraries/pytest' }
          ]
        },
        {
          text: '⚡ 并发与异步',
          items: [
            { text: '🧵 threading 多线程', link: '/04-concurrency/threading' },
            { text: '🔀 multiprocessing', link: '/04-concurrency/multiprocessing' },
            { text: '⚡ asyncio 协程', link: '/04-concurrency/asyncio' },
            { text: '🔁 同步原语', link: '/04-concurrency/sync-primitives' },
            { text: '🏊 线程池与进程池', link: '/04-concurrency/pool' },
            { text: '🎯 并发模式', link: '/04-concurrency/patterns' }
          ]
        },
        {
          text: '🕷️ Python 爬虫',
          items: [
            { text: '🎯 爬虫基础', link: '/05-scraping/basics' },
            { text: '🌐 requests + BeautifulSoup', link: '/05-scraping/requests-bs4' },
            { text: '⚡ Scrapy 框架', link: '/05-scraping/scrapy' },
            { text: '🌍 动态渲染（Selenium/Playwright）', link: '/05-scraping/dynamic' },
            { text: '🛡️ 反爬对抗', link: '/05-scraping/anti-crawl' }
          ]
        },
        {
          text: '🤖 AI 与机器学习',
          items: [
            { text: '🎯 AI 应用概览', link: '/06-ai-ml/overview' },
            { text: '🧠 机器学习基础', link: '/06-ai-ml/ml-basics' },
            { text: '🤗 Hugging Face', link: '/06-ai-ml/huggingface' },
            { text: '💬 LLM 应用开发', link: '/06-ai-ml/llm-apps' },
            { text: '🖼️ 计算机视觉', link: '/06-ai-ml/cv' },
            { text: '🗣️ 自然语言处理', link: '/06-ai-ml/nlp' }
          ]
        },
        {
          text: '📊 数据处理',
          items: [
            { text: '🐼 pandas 入门', link: '/07-data/pandas' },
            { text: '🔢 NumPy 数值计算', link: '/07-data/numpy' },
            { text: '📈 Matplotlib 可视化', link: '/07-data/matplotlib' },
            { text: '🔍 数据清洗', link: '/07-data/cleaning' },
            { text: '📊 数据分析实战', link: '/07-data/analysis' },
            { text: '💾 大数据处理', link: '/07-data/big-data' }
          ]
        },
        {
          text: '🧮 算法与数据结构',
          items: [
            { text: '📐 复杂度分析', link: '/08-algorithms/complexity' },
            { text: '📚 内置数据结构', link: '/08-algorithms/builtin' },
            { text: '🔍 排序算法', link: '/08-algorithms/sort' },
            { text: '🔎 搜索算法', link: '/08-algorithms/search' },
            { text: '🌳 树与图', link: '/08-algorithms/tree-graph' },
            { text: '🧠 动态规划', link: '/08-algorithms/dp' }
          ]
        },
        {
          text: '💼 企业实战',
          items: [
            { text: '🏗️ 项目结构', link: '/09-enterprise/structure' },
            { text: '📦 依赖管理', link: '/09-enterprise/dependencies' },
            { text: '🧪 单元测试', link: '/09-enterprise/testing' },
            { text: '🚀 性能优化', link: '/09-enterprise/performance' },
            { text: '🌐 FastAPI Web 实战', link: '/09-enterprise/fastapi' },
            { text: '🐳 Docker 部署', link: '/09-enterprise/docker' },
            { text: '🔍 日志与监控', link: '/09-enterprise/logging' },
            { text: '🛡️ 安全最佳实践', link: '/09-enterprise/security' }
          ]
        }
      ],
      '/graph': [{ text: '🎯 知识图谱', items: [{ text: '🌐 Python 全局知识图谱', link: '/graph' }] }],
      '/mindmap': [{ text: '🎯 思维导图', items: [{ text: '🧭 Python 思维导图', link: '/mindmap' }] }],
      '/cheatsheet': [{ text: '🎯 速查表', items: [{ text: '📋 Python 速查表', link: '/cheatsheet' }] }],
      '/path': [{ text: '🎯 学习路径', items: [{ text: '📖 Python 学习路径', link: '/path' }] }]
    },
    socialLinks: [{ icon: 'github', link: 'https://github.com' }],
    footer: {
      message: 'Python 知识图谱 - 系统化学习 Python 全栈 · 🏠 <a href="https://java-px.bot.cd/" target="_blank">门户首页</a>',
      copyright: 'MIT License'
    },
    outline: { level: [2, 3], label: '页面大纲' },
    docFooter: { prev: '上一篇', next: '下一篇' },

    search: { provider: 'local' },
  }
})
