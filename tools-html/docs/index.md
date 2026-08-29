---
date: 2026-08-15  # date-auto-injected
layout: home

hero:
  name: 常用工具
  text: 把高频日常工具装进口袋
  tagline: JSON 格式化、时间戳转换、URL 编解码、UUID 生成等 12 个静态工具，运行在浏览器里。
  actions:
    - theme: brand
      text: 开始使用
      link: /json
    - theme: alt
      text: 查看全部工具
      link: '#all-tools'

features:
  - icon: 🧰
    title: 12 个工具
    details: JSON 系列、时间系列、编码/生成系列，常用工具一站式。
  - icon: 🔒
    title: 完全本地
    details: 所有计算在浏览器中完成，文件不会上传到任何服务器。
  - icon: ⚡
    title: 即开即用
    details: 不需要登录、不需要安装，直接打开对应页面即可。
---

<div id="all-tools"></div>

<script setup>
// WhyThisGraph 数据：原写在 :prop="..." 里会触发 Vue 编译错误（多行 YAML 数组），
// 改为 script setup 形式。
const painPoints = [
      "日常 JSON 格式化 / 压缩 / 校验每次都开在线工具？",
      "时间戳 / 时区 / ISO 8601 转换容易出错？",
      "URL 编解码 / Base64 / UUID / JWT 解码手算不来？",
      "正则表达式每次都要查语法？",
      "在线工具有数据泄露风险？"
    ]
const goals = [
      "JSON 系列（格式化 / 转 YAML / 转 CSV / Diff）",
      "时间系列（Unix 时间戳 / 时区 / ISO 8601 / Cron）",
      "编码系列（Base64 / URL / JWT / Unicode）",
      "生成系列（UUID / 哈希 / 随机数 / 密码）",
      "正则 / 字符编码 / 相对路径 等"
    ]
const relatedSites = [
      { site: "frontend", path: "/01-basics/json", label: "前端 JSON" },
      { site: "linux", path: "/11-shell/cron", label: "cron 任务" },
      { site: "cloud-native", path: "/04-helm/values", label: "Helm values.yaml" },
      { site: "system-design", path: "/09-id/snowflake", label: "UUID / Snowflake" },
      { site: "python", path: "/01-basics/intro", label: "Python 基础" }
    ]
</script>

<ClientOnly>
  <WhyThisGraph
    :pain-points="painPoints"
    :goals="goals"
    :related-sites="relatedSites"
    title="🎯 为什么写这个图谱？"
  />
</ClientOnly>


## JSON 系列

<div class="tool-grid">
  <a class="card" href="/json">
    <div class="icon">🧹</div>
    <h3>JSON 格式化</h3>
    <p>美化、压缩、校验 JSON，语法错误定位。</p>
  </a>
  <a class="card" href="/json-yaml">
    <div class="icon">🔁</div>
    <h3>JSON ↔ YAML</h3>
    <p>JSON 与 YAML 互转，常用于配置文件改写。</p>
  </a>
  <a class="card" href="/json-csv">
    <div class="icon">📊</div>
    <h3>JSON ↔ CSV</h3>
    <p>把 JSON 数组转成 CSV，或把 CSV 转回 JSON 数组。</p>
  </a>
  <a class="card" href="/json-diff">
    <div class="icon">🆚</div>
    <h3>JSON Diff</h3>
    <p>对比两份 JSON 的差异，高亮新增 / 删除 / 改动。</p>
  </a>
</div>

## 时间系列

<div class="tool-grid">
  <a class="card" href="/timestamp">
    <div class="icon">⏱️</div>
    <h3>时间戳 ↔ 日期</h3>
    <p>Unix 秒 / 毫秒 ↔ 人类可读时间，支持本地时区。</p>
  </a>
  <a class="card" href="/iso">
    <div class="icon">📅</div>
    <h3>ISO / RFC 格式化</h3>
    <p>ISO 8601、RFC 2822、UTC 等多种格式字符串互转。</p>
  </a>
  <a class="card" href="/timezone">
    <div class="icon">🌐</div>
    <h3>时区转换</h3>
    <p>在不同时区之间互转同一时刻，支持自定义时区列表。</p>
  </a>
  <a class="card" href="/relative">
    <div class="icon">🕐</div>
    <h3>相对时间</h3>
    <p>"3 小时前" / "5 天后" 等自然语言时间换算。</p>
  </a>
</div>

## 编码 / 生成

<div class="tool-grid">
  <a class="card" href="/url">
    <div class="icon">🔗</div>
    <h3>URL 编解码</h3>
    <p>encodeURIComponent / decodeURIComponent + URL 参数解析。</p>
  </a>
  <a class="card" href="/base64">
    <div class="icon">🅱️</div>
    <h3>Base64 编解码</h3>
    <p>纯文本与 Base64 字符串互转，支持中文。</p>
  </a>
  <a class="card" href="/uuid">
    <div class="icon">🆔</div>
    <h3>UUID 生成</h3>
    <p>生成 v1 / v4 / v7 UUID，支持批量与大小写。</p>
  </a>
  <a class="card" href="/cron">
    <div class="icon">⏰</div>
    <h3>Cron 表达式</h3>
    <p>解析 Cron 并预览接下来 5 次运行时间。</p>
  </a>
</div>

## 📚 相关阅读（跨站导航）

<!-- xlink-injected:do-not-edit -->

按主题跨站推荐：

- [frontend](https://java-px.bot.cd/frontend/)：前端工具
- [devops](https://java-px.bot.cd/devops/)：运维工具
- [python](https://java-px.bot.cd/python/)：Python 工具


<!-- auto-enrich:do-not-edit -->

## 实战示例

```bash
# TODO: 在此补充本页主题的实战命令
echo "hello"
```

```yaml
# TODO: 配置示例
key: value
```

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料
<!-- auto-enrich:do-not-edit -->

<!-- svg-injected:do-not-edit -->

## 图示：Unix 工具哲学与管道组合

![Unix 工具哲学与管道组合](/tool-pipeline.svg)
