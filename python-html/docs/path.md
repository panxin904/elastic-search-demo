---
title: 学习路径
date: 2026-08-15  # date-auto-injected
---

# 📖 Python 学习路径

> 根据你的角色选择对应路径，每条路径推荐了核心阅读顺序。

## 🛤️ 路径 1：入门（1 周）

适合**刚接触 Python**的初学者。

1. [❓ Python 是什么](/01-basics/intro) - 5 分钟了解 Python
2. [📥 安装与环境](/01-basics/install) - 5 分钟跑起来
3. [🔤 基础语法](/01-basics/syntax) - 变量、运算符、字符串
4. [📦 数据结构](/01-basics/data-structures) - 列表、字典、元组、集合
5. [🔁 控制流](/01-basics/control-flow) - if/else、for、while
6. [📋 速查表](/cheatsheet) - 速查语法

**目标**：能写简单的 Python 脚本，能用标准库处理常见任务。

## 🛤️ 路径 2：进阶（2-3 周）

适合**想深入 Python**的开发者。

- 完成"入门"路径
- [🏗️ Python 解释器](/02-principles/interpreter) - CPython 架构
- [🧠 字节码与执行](/02-principles/bytecode) - 字节码、code object
- [📦 对象模型](/02-principles/object-model) - PyObject 底层结构
- [🗑️ 内存管理](/02-principles/memory) - 引用计数、内存池
- [⏱️ GIL 全局锁](/02-principles/gil) - 为什么 Python 慢
- [🔍 垃圾回收](/02-principles/gc) - GC 机制
- [📊 性能剖析](/02-principles/profiling) - cProfile、cProfile
- [📚 常用库](/03-libraries/stdlib) - 10 个必学标准库
- [🌐 requests HTTP](/03-libraries/requests) - HTTP 请求
- [🐼 pandas 数据分析](/03-libraries/pandas) - 数据分析基础

**目标**：理解 Python 底层原理，能用标准库和常用库完成实际任务。

## 🛤️ 路径 3：并发编程（2 周）

适合**想写出高性能 Python 代码**的开发者。

- 完成"进阶"路径
- [🧵 threading 多线程](/04-concurrency/threading) - GIL 限制
- [🔀 multiprocessing](/04-concurrency/multiprocessing) - 多进程
- [⚡ asyncio 协程](/04-concurrency/asyncio) - 异步 I/O
- [🔁 同步原语](/04-concurrency/sync-primitives) - Lock、Semaphore
- [🏊 线程池与进程池](/04-concurrency/pool) - concurrent.futures
- [🎯 并发模式](/04-concurrency/patterns) - Producer-Consumer 等

**目标**：能选择合适的并发方式（threading/multiprocessing/asyncio）解决实际问题。

## 🛤️ 路径 4：爬虫开发（2 周）

适合**想做数据采集**的开发者。

- 完成"入门"路径
- [🎯 爬虫基础](/05-scraping/basics) - robots.txt、User-Agent
- [🌐 requests + BeautifulSoup](/05-scraping/requests-bs4) - 静态页面
- [⚡ Scrapy 框架](/05-scraping/scrapy) - 工业级爬虫
- [🌍 动态渲染](/05-scraping/dynamic) - Selenium、Playwright
- [🛡️ 反爬对抗](/05-scraping/anti-crawl) - User-Agent、代理、限速

**目标**：能开发中小型爬虫项目，应对常见反爬策略。

## 🛤️ 路径 5：AI 应用开发（3-4 周）

适合**想用 Python 做 AI 应用**的开发者（最热门方向）。

- 完成"入门"路径
- [🎯 AI 应用概览](/06-ai-ml/overview) - 主流应用场景
- [🧠 机器学习基础](/06-ai-ml/ml-basics) - scikit-learn
- [🤗 Hugging Face](/06-ai-ml/huggingface) - 预训练模型
- [💬 LLM 应用开发](/06-ai-ml/llm-apps) - Prompt Engineering、RAG
- [🖼️ 计算机视觉](/06-ai-ml/cv) - OpenCV、YOLO
- [🗣️ 自然语言处理](/06-ai-ml/nlp) - 分词、Embedding
- [🐼 pandas 入门](/07-data/pandas) - 数据预处理

**目标**：能使用 Hugging Face、LLM API 开发 AI 应用。

## 🛤️ 路径 6：数据处理（2-3 周）

适合**想做数据分析**的开发者。

- 完成"入门"路径
- [🐼 pandas 入门](/07-data/pandas) - DataFrame
- [🔢 NumPy 数值计算](/07-data/numpy) - 数组运算
- [📈 Matplotlib 可视化](/07-data/matplotlib) - 数据可视化
- [🔍 数据清洗](/07-data/cleaning) - 缺失值、异常值
- [📊 数据分析实战](/07-data/analysis) - 真实案例
- [💾 大数据处理](/07-data/big-data) - Dask、Spark

**目标**：能使用 Python 进行完整的数据分析流程。

## 🛤️ 路径 7：算法与面试（4 周）

适合**准备算法面试**的开发者。

- 完成"入门"路径
- [📐 复杂度分析](/08-algorithms/complexity) - O 记号
- [📚 内置数据结构](/08-algorithms/builtin) - list/dict/set
- [🔍 排序算法](/08-algorithms/sort) - 快排、归并、堆排
- [🔎 搜索算法](/08-algorithms/search) - 二分、DFS、BFS
- [🌳 树与图](/08-algorithms/tree-graph) - 二叉树、图论
- [🧠 动态规划](/08-algorithms/dp) - 背包、最长子序列

**目标**：能解 LeetCode 中等难度问题。

## 🛤️ 路径 8：企业级工程（3-4 周）

适合**想成为 Python 工程师**的开发者。

- 完成所有前置路径
- [🏗️ 项目结构](/09-enterprise/structure) - 良好项目组织
- [📦 依赖管理](/09-enterprise/dependencies) - poetry、pipenv
- [🧪 单元测试](/09-enterprise/testing) - pytest
- [🚀 性能优化](/09-enterprise/performance) - 性能调优
- [🌐 FastAPI Web 实战](/09-enterprise/fastapi) - 现代 Web 框架
- [🐳 Docker 部署](/09-enterprise/docker) - 容器化
- [🔍 日志与监控](/09-enterprise/logging) - 可观测性
- [🛡️ 安全最佳实践](/09-enterprise/security) - Web 安全

**目标**：能独立开发生产级 Python 项目。

## 🎯 速查卡片

| 我想 | 推荐先看 |
|------|---------|
| 学基础 | [🔤 基础语法](/01-basics/syntax) → [📋 速查表](/cheatsheet) |
| 写爬虫 | [🌐 requests + BS4](/05-scraping/requests-bs4) → [⚡ Scrapy](/05-scraping/scrapy) |
| 做 AI 应用 | [🤗 Hugging Face](/06-ai-ml/huggingface) → [💬 LLM 应用开发](/06-ai-ml/llm-apps) |
| 数据分析 | [🐼 pandas](/07-data/pandas) → [📊 分析实战](/07-data/analysis) |
| 解算法题 | [📐 复杂度](/08-algorithms/complexity) → [🔍 排序](/08-algorithms/sort) → [🧠 动态规划](/08-algorithms/dp) |
| 写 Web 后端 | [🌐 FastAPI](/09-enterprise/fastapi) → [🐳 Docker](/09-enterprise/docker) |
| 优化性能 | [📊 性能剖析](/02-principles/profiling) → [🚀 性能优化](/09-enterprise/performance) |
| 面试 | [🧮 算法](./08-algorithms/) → [💼 企业实战](./09-enterprise/) |


## 📱 手机扫码继续阅读

<ClientOnly>
  <QrShare />
</ClientOnly>
