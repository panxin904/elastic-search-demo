---
title: 速查表
---

# 📋 Python 速查表

> 50+ 高频 Python 语法速查，支持分类过滤和关键词搜索。

<ClientOnly>
  <Cheatsheet />
</ClientOnly>

## 🧰 常用场景快速索引

| 场景 | 语法 |
|------|------|
| 列表排序 | `sorted(lst)` 或 `lst.sort()` |
| 列表去重 | `list(set(lst))` |
| 列表转字符串 | `','.join(['a', 'b'])` |
| 字符串分割 | `s.split(',')` |
| 字典遍历 | `for k, v in d.items():` |
| 列表推导式 | `[x*2 for x in range(10)]` |
| 读取 JSON | `json.load(open('f.json'))` |
| 写入 JSON | `json.dump(obj, open('f.json', 'w'))` |
| 文件读取 | `with open('f') as f: f.read()` |
| HTTP 请求 | `requests.get(url).json()` |
| 多线程 | `concurrent.futures.ThreadPoolExecutor()` |
| 异步 | `asyncio.run(main())` |

## 📚 跨站参考：🧰 常用场景快速索引

<!-- xlink-dedup:do-not-edit -->

本节在 3 站展开，最权威版本位于 **redis** 站（[https://java-px.bot.cd/redis/](https://java-px.bot.cd/redis/)）。

其他站参考：[kafka](https://java-px.bot.cd/kafka/) / [python](https://java-px.bot.cd/python/)

跨站关联由 `xlink-injector.py` + `crosslink-dedup.py` 自动生成（§8.68）。
