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
  base: '/java-language/',
  title: 'Java 语言 知识图谱',
  description: '系统化学习 Java - JVM / 并发 / 集合 / Spring / GC - 14 大类 · 80+ 节点 · 50+ 内容页',
  lang: 'zh-CN', lastUpdated: true, srcDir: 'docs', cleanUrls: true,
    head: [
    ['link', { rel: 'icon', href: '/favicon.ico', type: 'image/x-icon' }],
    ['link', { rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' }],
    ['link', { rel: 'apple-touch-icon', href: '/apple-touch-icon.png', sizes: '180x180' }],
    ['meta', { name: 'theme-color', content: '#dc2626' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:locale', content: 'zh_CN' }],
  ],
  themeConfig: {
    siteTitle: 'Java 语言全栈',
    nav: [      { text: '🏠 门户', link: 'https://java-px.bot.cd/', target: '_blank' },
{text:'首页',link:'/'},{text:'知识图谱',link:'/graph'},{text:'思维导图',link:'/mindmap'},{text:'命令速查',link:'/cheatsheet'},{text:'学习路径',link:'/path'},
      {
        text: '更多站点',
        items: [
        { text: 'AI 工具 / 大模型', link: 'https://java-px.bot.cd/ai/' },
        { text: '企业级架构', link: 'https://java-px.bot.cd/architecture/' },
        { text: '大数据', link: 'https://java-px.bot.cd/bigdata/' },
        { text: '云原生 / Docker / K8s', link: 'https://java-px.bot.cd/cloud-native/' },
        { text: 'ElasticSearch', link: 'https://java-px.bot.cd/es/' },
        { text: '前端 & Node', link: 'https://java-px.bot.cd/frontend/' },
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
        {text:'📐 基础语法',items:[{text:'OOP / 类与对象',link:'/01-basics/oop'},{text:'数据类型 / 包装类',link:'/01-basics/datatypes'},{text:'异常处理',link:'/01-basics/exceptions'},{text:'泛型 / 注解 / 反射',link:'/01-basics/generics'},{text:'JDK 17-21 新特性',link:'/01-basics/new-features'}]},
        {text:'📚 集合框架',items:[{text:'List / ArrayList / LinkedList',link:'/02-collections/list'},{text:'Map / HashMap 原理',link:'/02-collections/map'},{text:'Set / TreeSet',link:'/02-collections/set'},{text:'Stream API',link:'/02-collections/stream'},{text:'并发集合',link:'/02-collections/concurrent'}]},
        {text:'🧵 并发编程',items:[{text:'线程 / 线程池',link:'/03-concurrency/thread-pool'},{text:'锁 / synchronized / AQS',link:'/03-concurrency/locks'},{text:'JUC 工具',link:'/03-concurrency/juc'},{text:'CompletableFuture',link:'/03-concurrency/future'},{text:'虚拟线程 (Loom)',link:'/03-concurrency/virtual-threads'}]},
        {text:'⚙️ JVM 内存模型',items:[{text:'JVM 运行时数据区',link:'/04-jvm/runtime'},{text:'类加载机制',link:'/04-jvm/classloading'},{text:'字节码 / 指令',link:'/04-jvm/bytecode'},{text:'对象创建 / OOM 排查',link:'/04-jvm/oom'}]},
        {text:'🗑️ GC 垃圾回收',items:[{text:'GC 算法',link:'/05-gc/algorithms'},{text:'G1 / ZGC / Shenandoah',link:'/05-gc/collectors'},{text:'GC 日志 / 调优',link:'/05-gc/tuning'}]},
        {text:'🌱 Spring 核心',items:[{text:'IoC / DI / AOP',link:'/06-spring/ioc-aop'},{text:'Spring Boot 自动配置',link:'/06-spring/boot'},{text:'Spring MVC',link:'/06-spring/mvc'},{text:'声明式事务',link:'/06-spring/transaction'}]},
        {text:'☁️ Spring Cloud',items:[{text:'Nacos 注册/配置中心',link:'/07-spring-cloud/nacos'},{text:'Gateway / Sentinel',link:'/07-spring-cloud/gateway'},{text:'Seata 分布式事务',link:'/07-spring-cloud/seata'}]},
        {text:'🗄️ DB / ORM',items:[{text:'JDBC / 连接池 HikariCP',link:'/08-database/jdbc'},{text:'MyBatis / MyBatis-Plus',link:'/08-database/mybatis'},{text:'JPA / Hibernate',link:'/08-database/jpa'}]},
        {text:'📡 IO / NIO',items:[{text:'BIO / NIO / AIO',link:'/09-io/nio'},{text:'Netty 框架',link:'/09-io/netty'},{text:'序列化 / JSON / ProtoBuf',link:'/09-io/serialize'}]},
        {text:'⚡ 性能调优',items:[{text:'JVM 调优参数',link:'/10-performance/jvm-tuning'},{text:'Arthas 诊断',link:'/10-performance/arthas'},{text:'jstack / jmap / jstat',link:'/10-performance/jvm-tools'}]},
        {text:'🏛️ 设计模式',items:[{text:'创建型模式',link:'/11-design/creational'},{text:'结构型模式',link:'/11-design/structural'},{text:'行为型模式',link:'/11-design/behavioral'}]},
        {text:'🛠️ 工具 / 构建',items:[{text:'Maven / Gradle',link:'/12-tools/build'},{text:'Lombok / MapStruct',link:'/12-tools/lombok'},{text:'常用命令速查',link:'/12-tools/commands'}]},
        {text:'🧪 测试',items:[{text:'JUnit5',link:'/13-testing/junit5'},{text:'Mockito',link:'/13-testing/mockito'},{text:'Spring Boot Test',link:'/13-testing/spring-test'}]},
        {text:'🎯 面试 / 进阶',items:[{text:'高频面试题',link:'/14-interview/questions'},{text:'手写代码',link:'/14-interview/coding'},{text:'学习路径',link:'/14-interview/path'}]}
      ]
    },
    socialLinks: [{icon:'github',link:'https://github.com'}],
    footer: { message: 'Java 语言 - JVM / 并发 / Spring 系统化学习 · 🏠 <a href="https://java-px.bot.cd/" target="_blank">门户首页</a>', copyright: 'MIT License' },
    outline: { level: [2,3], label: '页面大纲' },
    docFooter: { prev: '上一篇', next: '下一篇' },

    search: { provider: 'local' },
  }
}))
