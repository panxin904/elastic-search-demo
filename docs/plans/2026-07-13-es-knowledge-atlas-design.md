# ES Knowledge Atlas (ES 7 学习静态网站 + 知识图谱)

**日期**: 2026-07-13
**目标**: 创建一个面向开发者学习 Elasticsearch 7 的静态知识图谱网站，按 ES 架构四层组织内容，并通过可交互的知识图谱将概念、特性、使用方式串联起来。

---

## 1. 技术栈

| 类别 | 选型 | 理由 |
|---|---|---|
| 静态站点 | **VitePress 1.x** (Vue 3 + Vite) | 现代UI / Vue 生态 / 中文搜索 / 侧边栏自动生成 |
| 图谱渲染 | **ECharts 5.x** (force-layout graph) | 中文文档详细、关系图类型多、性能好、CDN 引入 |
| 图谱数据 | **手写 JSON** (`public/graph.json`) | 节点粒度可控、关系语义清晰 |
| 部署 | 纯静态 | `npm run build` 后 `index.html` 可托管到任意静态服务器 |

---

## 2. 目录结构

```
es-html/
├── .vitepress/
│   ├── config.mts                # VitePress 配置
│   └── theme/
│       ├── index.ts              # 自定义主题入口
│       └── components/
│           └── KnowledgeGraph.vue  # ECharts 知识图谱组件
├── public/
│   └── graph.json                # 知识图谱数据 (52 节点 + ~80 边)
├── docs/
│   ├── index.md                  # 首页（含全图谱视图）
│   ├── 01-storage/               # 存储层 (~12 篇)
│   ├── 02-query/                 # 查询层 (~16 篇)
│   ├── 03-analysis/              # 分析层 (~10 篇)
│   ├── 04-ops/                   # 运维层 (~14 篇)
│   └── 99-compare/               # 7/8 差异
├── package.json
└── README.md
```

---

## 3. 知识图谱数据模型 (graph.json)

```json
{
  "meta": {
    "title": "Elasticsearch 7 知识图谱",
    "version": "7.17.10",
    "lastUpdated": "2026-07-13"
  },
  "categories": [
    { "id": "storage",  "name": "存储层", "color": "#3b82f6" },
    { "id": "query",    "name": "查询层", "color": "#10b981" },
    { "id": "analysis", "name": "分析层", "color": "#f59e0b" },
    { "id": "ops",      "name": "运维层", "color": "#a855f7" }
  ],
  "nodes": [
    {
      "id": "cluster",
      "name": "集群 Cluster",
      "category": "ops",
      "docPath": "/04-ops/cluster",
      "summary": "由一个或多个节点组成的 ES 集群",
      "tags": ["基础概念", "分布式"]
    }
  ],
  "edges": [
    {
      "source": "cluster",
      "target": "node",
      "relation": "包含",
      "label": "包含"
    }
  ]
}
```

### 边关系类型
- `包含` (composes) - 父子组成
- `依赖` (depends-on) - 强依赖
- `切分` (splits-to) - 物理切分
- `使用` (uses) - 操作关系
- `相关` (related-to) - 概念关联
- `作用于` (acts-on) - 应用对象

### 节点规模 (52 总数)
- **存储层** (~12): 集群 / 节点 / 索引 / 文档 / 分片(主/副本) / 段(Segment) / Mapping / 字段类型 / 元数据 / _source / Translog / Refresh
- **查询层** (~16): Query DSL / Match / Term / Bool / Range / Boost / 分页 / 排序 / Highlight / Aggregation / Script Query / Multi Search / Search After
- **分析层** (~10): Analyzer / Tokenizer / Token Filter / Char Filter / 内置分词器 / 自定义分词 / _analyze API / 倒排索引 / BM25 / Explain
- **运维层** (~14): 安装部署 / JVM 调优 / 分片分配 / 集群健康 / Snapshot / ILM / Curator / 监控 / 慢日志 / 集群重启 / _cat API / 索引模板 / 别名 / X-Pack

---

## 4. KnowledgeGraph 组件

**位置**: `.vitepress/theme/components/KnowledgeGraph.vue`

### 两种使用模式
- **全图谱** (首页): `<KnowledgeGraph mode="full" :data="graphData" />`
- **邻居视图** (页面内): `<KnowledgeGraph mode="neighbor" :data="graphData" :focus-node-id="shard" />`

### 交互特性
- 拖拽节点、滚轮缩放
- 点击节点: 跳转到 `node.docPath`
- 鼠标悬停: 高亮节点 + tooltip 显示 summary
- 双击空白: 重置视图
- 全图谱模式: 顶部图例点击切换层级显隐
- 邻居模式: 中心节点固定在中央, 大小 1.5x, 同心圆布局

### ECharts 配置核心
```js
{
  type: 'graph',
  layout: 'force',
  roam: true,
  force: {
    repulsion: 300,
    edgeLength: [60, 120],
    gravity: 0.05
  },
  edgeSymbol: ['none', 'arrow'],
  emphasis: { focus: 'adjacency', lineStyle: { width: 3 } }
}
```

### 性能
- 52 节点规模无需特殊优化
- 邻居视图 < 10 节点，性能极佳
- 主题切换时 dispose + recreate 实例
- SSR 兼容: `onMounted` 后初始化图表

---

## 5. 内容页面结构

### Frontmatter 规范
```yaml
---
title: 分片 Shard
category: storage
graphNodeId: shard
related: [cluster, index, replica, segment]
---
```

### 正文通用结构
1. **📌 一句话定义** - 极简定义
2. **🎯 为什么需要它？** - 解决的问题
3. **🔧 核心配置** - DSL/JSON 示例
4. **🔗 在图谱中的位置** - 邻居视图
5. **📚 延伸阅读** - 链接到其他节点
6. **🔗 对应源码** (可选) - 链接到本项目 Java 源码

### 代码示例规范
- DSL 示例: ` ```json `
- Java API 示例: ` ```java `
- 标注 ES 版本 (7.x)

---

## 6. VitePress 配置要点

```ts
// .vitepress/config.mts
export default {
  title: 'ES Knowledge Atlas',
  description: 'Elasticsearch 7 系统化学习 - 用知识图谱串联概念与使用方式',
  themeConfig: {
    nav: [
      { text: '存储层', link: '/01-storage/overview' },
      { text: '查询层', link: '/02-query/overview' },
      { text: '分析层', link: '/03-analysis/overview' },
      { text: '运维层', link: '/04-ops/overview' },
      { text: '7 vs 8', link: '/99-compare/diff' }
    ],
    sidebar: {
      '/01-storage/': [...],
      '/02-query/': [...],
      '/03-analysis/': [...],
      '/04-ops/': [...],
      '/99-compare/': [...]
    },
    search: { provider: 'local' }
  }
}
```

---

## 7. 首页设计 (docs/index.md)

- **Hero 区**: "Elasticsearch 7 知识图谱 - 用图谱方式系统化学习 ES"
- **三大统计**: 节点数 / 文档数 / 分类数
- **完整大图谱** (全屏 ECharts force-layout)
- **四层快速入口卡片**
- **最近更新列表**

---

## 8. 实施计划

| 阶段 | 任务 | 产物 |
|---|---|---|
| 1 | 项目初始化 | `package.json` / `config.mts` / 基础目录 |
| 2 | 知识图谱数据 | `public/graph.json` (52 节点 + ~80 边) |
| 3 | KnowledgeGraph 组件 | `KnowledgeGraph.vue` (full + neighbor 双模式) |
| 4 | 内容页面 (4 层并行) | 52 篇 markdown |
| 5 | 集成与样式 | 侧边栏、主题色、移动端 |
| 6 | 验证 | dev server + build + 链接检查 |

---

## 9. 验证清单

- [ ] 首页加载 1 秒内图谱渲染完成
- [ ] 节点点击准确跳转
- [ ] 邻居模式正确显示一度关系
- [ ] 52 节点全部可达
- [ ] 全文搜索可用 (VitePress local search)
- [ ] `npm run build` 退出码 0
- [ ] 所有外部链接 (ES 官方文档) 可访问

---

## 10. YAGNI (本期不做)

- ❌ 多语言 (i18n)
- ❌ 暗色/亮色主题切换 (VitePress 默认)
- ❌ 用户账号、评论、收藏
- ❌ 实时 ES 集群连接演示
- ❌ 代码运行沙箱
