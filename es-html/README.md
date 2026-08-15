# ES Knowledge Atlas

Elasticsearch 7 系统化学习 - 用知识图谱串联概念与使用方式。

## 🎯 特色

- **📚 51 个核心概念节点** - 按 ES 架构四层组织
- **🗺️ 可交互式知识图谱** - ECharts force-layout，支持节点点击跳转、悬停高亮、邻居视图
- **🔗 与项目源码关联** - 代码示例与 [elastic-search-demo](https://github.com/your-repo) Java 项目中的 `ElasticsearchService.java` 对应
- **🔍 全文搜索** - VitePress 内置中文分词搜索
- **📱 响应式** - 移动端友好

## 🚀 快速开始

```bash
# 安装依赖
npm install

# 开发模式 (localhost:5173)
npm run docs:dev

# 生产构建
npm run docs:build

# 预览构建结果
npm run docs:preview
```

## 📂 目录结构

```
es-html/
├── .vitepress/                # VitePress 配置
│   ├── config.mts            # 主配置（导航/侧边栏）
│   └── theme/                # 自定义主题
│       ├── index.ts
│       ├── style.css
│       ├── components/
│       │   └── KnowledgeGraph.vue  # 知识图谱组件
│       └── composables/
│           └── useGraphData.ts
├── public/
│   └── graph.json            # 知识图谱数据 (51 节点 + 65 边)
├── docs/
│   ├── index.md              # 首页
│   ├── 01-storage/           # 存储层 (12 篇)
│   ├── 02-query/             # 查询层 (16 篇)
│   ├── 03-analysis/          # 分析层 (11 篇)
│   ├── 04-ops/               # 运维层 (12 篇)
│   └── 99-compare/           # 7 vs 8 对比
├── package.json
└── README.md
```

## 🗺️ 知识图谱分类

| 颜色 | 分类 | 节点数 |
|---|---|---|
| 🔵 蓝 | 存储层 Storage | 12 |
| 🟢 绿 | 查询层 Query | 16 |
| 🟠 橙 | 分析层 Analysis | 11 |
| 🟣 紫 | 运维层 Ops | 12 |

## 🛠️ 技术栈

- [VitePress 1.x](https://vitepress.dev/) - 静态站点生成器
- [Vue 3](https://vuejs.org/) - 组件化
- [ECharts 5.x](https://echarts.apache.org/) - 图谱渲染
- 纯静态部署，无后端

## 📜 License

MIT
