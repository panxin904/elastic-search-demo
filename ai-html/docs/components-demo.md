---
title: §8.82 公共组件演示
date: 2026-09-08
---

# §8.82 公共组件演示（v31）

> 跨 31 站可复用：CrossSiteNav / TipBox / InfoBox / WarnBox
> 
> 全部通过 `@shared/vitepress-template/theme/components/*` 引入，
> 每个站 `.vitepress/theme/index.ts` 已注册全局组件。

## 🧩 1. CrossSiteNav — 跨站推荐

<div class="at-grid-cards at-mt-2">
  <div class="at-card"><strong>385 处硬编码</strong><p>原 markdown 块</p></div>
  <div class="at-card"><strong>→ 组件化</strong><p>v31 一键迁移</p></div>
  <div class="at-card"><strong>样式集中</strong><p>无需在 384 个 md 散落</p></div>
</div>

实际效果：

<CrossSiteNav :items="[
    { site: 'python',   label: 'Python AI / ML',     url: 'https://java-px.bot.cd/python/' },
    { site: 'bigdata',  label: '大数据训练',         url: 'https://java-px.bot.cd/bigdata/' },
    { site: 'system-design', label: 'AI 系统架构',  url: 'https://java-px.bot.cd/system-design/' },
    { site: 'observability', label: '模型监控',     url: 'https://java-px.bot.cd/observability/' },
    { site: 'kafka',    label: 'Kafka 流处理',       url: 'https://java-px.bot.cd/kafka/' },
    { site: 'cloud-native', label: 'GPU 编排',      url: 'https://java-px.bot.cd/cloud-native/' }
  ]" />

## 💡 2. TipBox — 提示框

<div class="at-grid-cards at-mt-2">
  <TipBox icon="💡" title="提示">支持任意 markdown / HTML 内容</TipBox>
  <TipBox icon="🔥" title="重点" variant="danger">高优先级，必须花时间搞懂</TipBox>
  <TipBox icon="✅" title="最佳实践" variant="success">能 filter 就 filter，过滤不需要评分的条件</TipBox>
</div>

## 📘 3. InfoBox — 信息块

<InfoBox icon="📘" title="相关信息">
本页主要讲 AI 7.17（搭配 elastic-search-demo 项目使用 7.17.10）。
如需了解 8.x 新特性请参考 [官方升级指南](https://www.elastic.co/guide/en/elasticsearch/reference/current/migrating-8.0.html)。
</InfoBox>

## ⚠️ 4. WarnBox — 警告块

<WarnBox icon="⚠️" title="Danger">
observe that the XSS attack through the `onerror` attribute is still exploitable
if the user can inject raw HTML.
</WarnBox>

<WarnBox icon="🔥" title="生产警告" variant="danger">
生产环境严禁明文存储密钥，请使用 KMS / Vault 加密。
</WarnBox>

## 🎨 5. at-* 工具类组合

<div class="at-stack at-container at-mt-2">
  <div class="at-card at-link-card">📌 <strong>提示 1</strong>：移动端纵向堆叠</div>
  <div class="at-card at-link-card">📌 <strong>提示 2</strong>：窗口 ≥ 600px 时自动横向排列（容器查询）</div>
  <div class="at-card at-link-card">📌 <strong>提示 3</strong>：使用 <code>.at-container</code> 包裹即可启用</div>
</div>

## 📐 6. at-prose — 受控正文宽度

<div class="at-prose at-content-text">
<p>这是受控宽度的正文（<code>max-width: 75ch</code>），大屏有更好可读性。
段落用 <code>clamp()</code> 流式字号，行高 1.8 适合长篇阅读。</p>
</div>

## 🛠️ 7. 开发者使用指南

### 7.1 在新页面调用 CrossSiteNav

```md
<CrossSiteNav :items="[
  { site: 'python', label: 'Python AI/ML',  url: 'https://java-px.bot.cd/python/' },
  { site: 'kafka',  label: 'Kafka 流处理',  url: 'https://java-px.bot.cd/kafka/' }
]" />
```

### 7.2 替换 emoji 引用块

原：
```md
<TipBox icon="💡" title="提示" variant="tip">
  鼠标拖动节点...
</TipBox>
```

新：
```md
<TipBox icon="💡" title="提示">鼠标拖动节点...</TipBox>
```

### 7.3 添加新组件

1. 在 `shared-assets/vitepress-template/theme/components/` 新建 `.vue` 文件
2. 在每个 `*-html/.vitepress/theme/index.ts` 注册（用脚本批量）
3. 重新 `bash sites-hub/build-release.sh`
