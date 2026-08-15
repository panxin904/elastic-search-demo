# Scholar's Atlas — VitePress 子站模板（C1）

**目标**：把 28 个子站统一到一套规范模板，消除体验断层，减少维护负担。

## 模板结构

```
shared-assets/vitepress-template/
├── config.mts.tpl              # config.mts 占位符模板
├── theme/
│   ├── style.css               # 统一 CSS 变量 + 卡片/代码块/表格样式
│   └── components/
│       ├── WhyThisGraph.vue    # 「为什么写这个图谱」双栏组件
│       ├── SitePortalLink.vue  # 顶部「返回门户」统一链接
│       └── SiteFooter.vue      # 统一底部
├── scripts/
│   └── render-config.sh        # 占位符替换工具（生成预览，不自动覆盖）
├── docs/                       # 子站 index.md 模板（待补充）
└── README.md                   # 本文件
```

## 各子站如何引用模板

### Step 1：复制 `theme/style.css`

```bash
cp shared-assets/vitepress-template/theme/style.css <your-site>/.vitepress/theme/style.css
```

各站原有的 badge / kg-* 样式保留（样式表用追加而非替换）。

### Step 2：复制共享组件

```bash
cp shared-assets/vitepress-template/theme/components/WhyThisGraph.vue <your-site>/.vitepress/theme/components/
cp shared-assets/vitepress-template/theme/components/SitePortalLink.vue <your-site>/.vitepress/theme/components/
cp shared-assets/vitepress-template/theme/components/SiteFooter.vue <your-site>/.vitepress/theme/components/
```

### Step 3：在 `theme/index.ts` 注册

```ts
import DefaultTheme from 'vitepress/theme'
import KnowledgeGraph from './components/KnowledgeGraph.vue'
import MindMap from './components/MindMap.vue'
import WhyThisGraph from './components/WhyThisGraph.vue'
import SitePortalLink from './components/SitePortalLink.vue'
import SiteFooter from './components/SiteFooter.vue'
import './style.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('KnowledgeGraph', KnowledgeGraph)
    app.component('MindMap', MindMap)
    app.component('WhyThisGraph', WhyThisGraph)
    app.component('SitePortalLink', SitePortalLink)
    app.component('SiteFooter', SiteFooter)
  }
}
```

### Step 4：（可选）用模板重写 config.mts

```bash
bash shared-assets/vitepress-template/scripts/render-config.sh <your-site>
# 生成 .rendered.ts 预览，人工 review 后：
# mv <your-site>/.vitepress/config.mts.rendered <your-site>/.vitepress/config.mts
```

## C1 模板统一了什么

| 项 | 统一前 | 统一后 |
|----|--------|--------|
| 顶部 nav「门户」链接 | 各站手写 | `SitePortalLink` 组件 + 样式统一 |
| theme-color meta | 部分站缺 | 模板强制有 |
| og:site_name | 部分站缺 | 模板强制有 |
| Footer | 各站自定义文案 | `SiteFooter` 统一（可覆盖 message prop） |
| 行距 / 字距 | 各站 CSS 不一 | `style.css` 统一 `--at-line-height: 1.7` |
| 代码块圆角 | 各站不一 | 统一 `--at-radius-md: 8px` |
| 卡片网格 | 仅 ai/bigdata 有 | `.at-features` 通用样式 |

## 各站保留的差异

- `siteTitle`：站名（如"AI 工程全栈"）
- `accent` 颜色：站品牌色
- `nav` 自定义项（如"知识图谱"/"思维导图"）
- `sidebar`：完全站定制（render 脚本不动）
- 站专属组件（如 ai-html 的 `KnowledgeGraph`）

## 迁移 SOP

新站或大改时按上述 4 步操作。现有 28 站**暂不批量迁移**（避免破坏现有 build）：
- 4 站已迁移（ai / architecture / bigdata / cloud-native / java-language，已用 `WhyThisGraph`）
- 24 站待迁（按工作量排序：tools / chaos / devops 等小站先迁）

## 验证 CI（计划中）

未来在 `.github/workflows/sites-hub-ci.yml` 加 job：
- 校验每个子站都有 `SitePortalLink` 注册
- 校验 `style.css` 包含 `--at-line-height: 1.7`
- 校验 `theme-color` meta 存在
