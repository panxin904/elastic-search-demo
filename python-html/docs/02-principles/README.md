---
title: Python 底层原理
date: 2026-08-29  # date-auto-injected
description: 解释器、字节码、对象模型、内存管理与 GIL
---

# 🔬 Python 底层原理

> 解释器、字节码、对象模型、内存管理与 GIL

## 📑 本节目录

- [interpreter](./interpreter) — CPython 解释器架构 · 字节码执行流程
- [bytecode](./bytecode) — .pyc · dis 模块 · 字节码指令
- [object-model](./object-model) — 一切皆对象 · type/metaclass · 描述符
- [memory](./memory) — 引用计数 · 内存池 · 小对象缓存
- [gil](./gil) — GIL 全局锁 · 为什么存在 · 影响 · 规避
- [gc](./gc) — 分代垃圾回收 · 循环引用检测
- `perf.md` — cProfile · timeit · 性能剖析工具（待补充）

## 🔗 跨站导航

- [Java 基础](https://java-px.bot.cd/java-language/) — 强类型语言对比
- [Go 入门](https://java-px.bot.cd/go/) — 编译型并发对比
- [系统设计](https://java-px.bot.cd/system-design/) — Python 在分布式系统中的角色
