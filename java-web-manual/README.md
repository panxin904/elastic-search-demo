# Java Web Dev Manual

Java Web 开发手册 - 用知识图谱系统化掌握开发全流程。

## 特色

- **48 个核心概念节点** - 按开发流程/实现思路/重点关注/技术栈四个维度组织
- **可交互式知识图谱** - ECharts force-layout，支持节点点击跳转、悬停高亮
- **全文搜索** - VitePress 内置中文分词搜索
- **响应式** - 移动端友好

## 快速开始

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

## 目录结构

```
java-web-manual/
├── .vitepress/               # VitePress 配置
│   ├── config.mts            # 主配置（导航/侧边栏）
│   └── theme/                # 自定义主题
│       ├── index.ts
│       ├── style.css
│       ├── graph.json        # 知识图谱数据
│       ├── components/
│       │   └── KnowledgeGraph.vue
│       └── composables/
│           └── useGraphData.ts
├── docs/
│   ├── index.md              # 首页
│   ├── 01-process/           # 开发流程 (13 篇)
│   ├── 02-design/            # 实现思路 (13 篇)
│   ├── 03-practice/          # 重点关注 (12 篇)
│   └── 04-tech/              # 技术栈 (12 篇)
├── package.json
└── README.md
```

## 知识图谱分类

| 颜色 | 分类 | 节点数 |
|---|---|---|
| 蓝 | 开发流程 Process | 13 |
| 绿 | 实现思路 Design | 13 |
| 橙 | 重点关注 Practice | 12 |
| 紫 | 技术栈 Tech | 12 |

## 技术栈

- [VitePress 1.x](https://vitepress.dev/) - 静态站点生成器
- [Vue 3](https://vuejs.org/) - 组件化
- [ECharts 5.x](https://echarts.apache.org/) - 图谱渲染
- 纯静态部署，无后端

## License

MIT
