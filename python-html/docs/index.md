---
layout: home

hero:
  name: Python 知识图谱
  text: 系统化学习 Python
  tagline: 用知识图谱串联 Python 底层原理、爬虫、AI、数据处理与企业实战
  actions:
    - theme: brand
      text: 🧭 学习路径
      link: /path
    - theme: alt
      text: 🌐 知识图谱
      link: /graph
    - theme: alt
      text: 🧠 思维导图
      link: /mindmap
    - theme: alt
      text: 📋 速查表
      link: /cheatsheet

features:
  - icon: 🐍
    title: Python 入门
    details: Python 是什么 · 安装与环境 · 基础语法 · 数据结构 · 控制流
    link: /01-basics/intro
    linkText: 开始学习 →
  - icon: 🔬
    title: 底层原理
    details: 解释器 · 字节码 · 对象模型 · 内存管理 · GIL 全局锁 · GC · 性能剖析
    link: /02-principles/interpreter
    linkText: 深入原理 →
  - icon: 📚
    title: 常用库
    details: 标准库 · requests · BeautifulSoup · SQLAlchemy · pandas · pytest
    link: /03-libraries/stdlib
    linkText: 常用库 →
  - icon: ⚡
    title: 并发与异步
    details: threading · multiprocessing · asyncio 协程 · 同步原语 · 线程池
    link: /04-concurrency/threading
    linkText: 并发 →
  - icon: 🕷️
    title: Python 爬虫
    details: requests+BS4 · Scrapy 框架 · 动态渲染 · 反爬对抗
    link: /05-scraping/basics
    linkText: 爬虫 →
  - icon: 🤖
    title: AI 与机器学习
    details: 机器学习基础 · Hugging Face · LLM 应用 · 计算机视觉 · NLP
    link: /06-ai-ml/overview
    linkText: AI 实战 →
  - icon: 📊
    title: 数据处理
    details: pandas · NumPy · Matplotlib · 数据清洗 · 大数据处理
    link: /07-data/pandas
    linkText: 数据 →
  - icon: 🧮
    title: 算法与数据结构
    details: 复杂度分析 · 内置数据结构 · 排序搜索 · 动态规划 · 树与图
    link: /08-algorithms/complexity
    linkText: 算法 →
  - icon: 💼
    title: 企业实战
    details: 项目结构 · 依赖管理 · 单元测试 · 性能优化 · FastAPI · Docker · 安全
    link: /09-enterprise/structure
    linkText: 实战 →
---

## 🎯 为什么写这个知识图谱？

```
Python 是最流行的编程语言之一，但绝大多数人：
  ❌ 只懂基础语法，不了解底层原理
  ❌ 用过 requests / pandas 但不知道内部实现
  ❌ 写 GIL 多线程却不知道为什么慢
  ❌ 爬虫写完就封 IP，不知道反爬怎么破
  ❌ LLM 应用只会调 API，不知道 prompt 怎么写

本图谱的目标：
  ✅ 系统化讲解 Python 底层原理（解释器、字节码、对象模型、GIL、GC）
  ✅ 覆盖常用库：requests、BeautifulSoup、pandas、SQLAlchemy、pytest
  ✅ 深入并发编程：threading、asyncio、multiprocessing
  ✅ 爬虫实战：requests、Scrapy、Playwright、反爬
  ✅ AI/ML 应用：scikit-learn、PyTorch、Hugging Face、LLM 开发
  ✅ 数据处理：pandas、NumPy、Matplotlib
  ✅ 算法与数据结构实战
  ✅ 企业级项目：FastAPI、Docker、性能优化
```

## 🎯 学习路径

```
🆕 入门     →  🐍 Python 入门 →  🔬 底层原理
📚 进阶     →  📚 常用库 →  ⚡ 并发与异步
🌐 实战     →  🕷️ Python 爬虫 →  📊 数据处理
🤖 AI 时代  →  🤖 AI 与机器学习
🧮 进阶     →  🧮 算法与数据结构
💼 工程化   →  💼 企业实战
```

完整路径请看 [📖 学习路径](/path)。

## 🆕 推荐先看

- [🐍 Python 是什么](/01-basics/intro) - 5 分钟了解 Python
- [🌐 全局知识图谱](/graph) - 看完整节点关系
- [🧭 思维导图](/mindmap) - 树形结构总览
- [📋 速查表](/cheatsheet) - Python 常用语法速查

## 🛠️ 技术栈

- [VitePress 1.x](https://vitepress.dev/) - 静态站点生成器
- [Vue 3](https://vuejs.org/) - 组件化
- [ECharts 5.x](https://echarts.apache.org/) - 图谱、思维导图、排序可视化
- 7 个自研交互组件（Playground / Scrapy 流程 / 排序可视化 / API 速查 / 知识图谱 / 思维导图 / Cheatsheet）
